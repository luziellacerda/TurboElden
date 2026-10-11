#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Stream an unsigned R127 classic-ZIP APK from the exact signed R126 base.

Only seven replacements and one addition are accepted. The source freeze and
identity receipt are checked before and after writing. Every other entry is
hashed while copying and read back independently. This never aligns, signs,
installs, deletes a backup or changes an emulator or server.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import re
import struct
import types
import zipfile

# Python defaults to ZIP64 at 2GiB; this APK is larger but remains below 4GiB.
zipfile.ZIP64_LIMIT = (1 << 32) - 1
BASE_SHA = "f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d"
PREFIX = "lib/arm64-v8a/"
SHARED = frozenset(("AndroidManifest.xml", "classes6.dex", "classes28.dex", "classes35.dex"))
REPLACED = SHARED | frozenset(("assets/station-online/engines.json",
    PREFIX + "libstation_mupen64plus_runtime.so", PREFIX + "libstation_dolphin_runtime.so"))
ADDED = frozenset((PREFIX + "libstation_psx_online.so",))
PAYLOADS = REPLACED | ADDED
MARKERS = {"n64": "libstation_mupen64plus_runtime.so",
           "dolphin": "libstation_dolphin_runtime.so", "psx": "libstation_psx_online.so"}
NORMAL_PINS = {"libmain.so": "62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6",
    "libSDL2.so": "a282b35554eb006773349430e117bfeeff32a84e246a058c8fb7c7027c2e4dee",
    "libpcsx_rearmed_libretro_android.so": "e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9",
    "libc++_shared.so": "b5d97c38a728afe28d341cda3369f512d35eaf9c680c1b0563cd6a63e395230f",
    "libstation_frontend.so": "de092671462a0960665d06d1b463cd48108e65c599c5125c733d7205dd463468"}
ROOT = Path(__file__).resolve().parents[1]
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"


def fs(path):
    """Use Windows extended paths for the long productive Java source tree."""
    resolved = Path(path).resolve()
    if os.name != "nt": return resolved
    value = str(resolved)
    if value.startswith("\\\\?\\"): return resolved
    return Path("\\\\?\\UNC\\" + value[2:] if value.startswith("\\\\") else "\\\\?\\" + value)


def sha(path):
    value = hashlib.sha256()
    with fs(path).open("rb") as source:
        for part in iter(lambda: source.read(1048576), b""): value.update(part)
    return value.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def read(path): return json.loads(fs(path).read_text(encoding="utf-8"))


def write(path, value):
    fs(path.parent).mkdir(parents=True, exist_ok=True)
    fs(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(value): return hashlib.sha256(value).hexdigest()


def signature_metadata(name):
    return bool(re.fullmatch(r"META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))", name, re.I))


def stream_copy(source, target):
    checksum = hashlib.sha256()
    for part in iter(lambda: source.read(1048576), b""):
        target.write(part); checksum.update(part)
    return checksum.hexdigest()


def entry_sha(archive, name):
    checksum = hashlib.sha256()
    with archive.open(name) as source:
        for part in iter(lambda: source.read(1048576), b""): checksum.update(part)
    return checksum.hexdigest()


def classic_zip(path, comment):
    """Verify the actual EOCD/count/offset fields and absence of ZIP64 records."""
    size = fs(path).stat().st_size
    position = size - 22 - len(comment)
    if position < 0 or size >= 0xffffffff: raise ValueError("APK exceeds classic ZIP bounds")
    with fs(path).open("rb") as source:
        if position >= 20:
            source.seek(position - 20)
            if source.read(4) == b"PK\x06\x07": raise ValueError("ZIP64 locator is forbidden")
        source.seek(position)
        raw = source.read(22)
        if len(raw) != 22: raise ValueError("Incomplete ZIP end record")
        magic, disk, central_disk, disk_count, count, length, offset, comment_size = struct.unpack("<4s4H2IH", raw)
        if magic != b"PK\x05\x06" or disk or central_disk or disk_count != count:
            raise ValueError("Invalid single-disk classic ZIP end record")
        if count == 0xffff or length == 0xffffffff or offset == 0xffffffff:
            raise ValueError("ZIP64 sentinel is forbidden")
        if comment_size != len(comment) or offset + length != position:
            raise ValueError("ZIP end offsets/comment differ")
        if source.read() != comment: raise ValueError("ZIP comment bytes differ")


def classic_entries(archive):
    names = archive.namelist()
    if len(names) != len(set(names)) or len(names) >= 0xffff:
        raise ValueError("Duplicate or excessive ZIP entry count")
    for item in archive.infolist():
        if item.flag_bits & 1: raise ValueError("Encrypted APK entry is unsupported")
        if item.file_size >= 0xffffffff or item.compress_size >= 0xffffffff:
            raise ValueError("Entry exceeds classic ZIP bounds")
        if item.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raise ValueError("Unexpected APK compression method: " + item.filename)
        offset = 0
        while offset < len(item.extra):
            if offset + 4 > len(item.extra): raise ValueError("Malformed ZIP extra field")
            kind, size = struct.unpack_from("<HH", item.extra, offset); offset += 4
            if offset + size > len(item.extra): raise ValueError("Truncated ZIP extra field")
            if kind == 1: raise ValueError("ZIP64 extra fields are forbidden")
            offset += size
    return set(names)


def current_sources():
    # This is the same complete effective source overlay used by the compiler.
    # Keep __file__ unprefixed: the compiler's own long-path helper prepends it.
    source = ROOT / "recipe/compile_java.py"
    module = types.ModuleType("psx_package_compile"); module.__file__ = str(source)
    exec(compile(fs(source).read_text(encoding="utf-8"), str(source), "exec"), module.__dict__)
    java = {name: sha(path) for name, path in sorted(module.sources().items())}
    transforms = {}
    for directory, suffixes in (("native", {".cpp", ".hpp", ".h"}), ("recipe", {".py"})):
        for path in sorted(fs(ROOT / directory).rglob("*")):
            if path.is_file() and path.suffix in suffixes and path.name != "build_runtime_identity.py":
                transforms[Path(str(path).removeprefix("\\\\?\\")).relative_to(ROOT).as_posix()] = sha(path)
    transforms["profile.json"] = sha(ROOT / "profile.json")
    return java, transforms


def engine_manifest(original, updated, receipt):
    """Check actual client engine selection and every unrelated engine/policy."""
    if {k: v for k, v in original.items() if k != "engines"} != {k: v for k, v in updated.items() if k != "engines"}:
        raise ValueError("Unrelated engine asset settings/policies changed")
    old, new = original["engines"], updated["engines"]
    if len(old) != len(new): raise ValueError("Engine count changed")
    targets = {"psx", "n64", "gamecube", "wii"}
    selected = []
    for before, after in zip(old, new):
        platform = before["platform"]
        if after["platform"] != platform: raise ValueError("Engine ordering/platform changed")
        if platform not in targets:
            if before != after: raise ValueError("Unrelated engine changed: " + platform)
            continue
        selected.append(after)
        if platform != "psx":
            strip = lambda item: {k: v for k, v in item.items() if k not in ("runtimeSha256", "engineId")}
            if strip(before) != strip(after): raise ValueError("Existing emulator core/options changed: " + platform)
        kind = "psx" if platform == "psx" else ("n64" if platform == "n64" else "dolphin")
        marker = receipt["markers"][kind]
        if after["runtimeSha256"] != marker["runtimeSha256"] or after["runtimeLibrary"] != MARKERS[kind]:
            raise ValueError("Engine runtime differs from identity: " + platform)
        if after["recoveryProtocol"] != "station-stream.v3": raise ValueError("Recovery protocol differs")
        prefix = ("pcsx-rearmed-ff81ed17-player-v3-" if platform == "psx" else
                  "mupen64plus-ae-33bf7021-n64-v3-" if platform == "n64" else
                  "dolphin-5102a033-" + platform + "-v3-")
        if after["engineId"] != prefix + marker["runtimeSha256"][:12]: raise ValueError("Stale engine identity")
        if platform == "psx":
            if after["coreSha256"] != NORMAL_PINS["libpcsx_rearmed_libretro_android.so"] or after["library"] != "libpcsx_rearmed_libretro_android.so":
                raise ValueError("PSX does not use the exact normal core")
            if after["maximumPlayers"] != 2 or after["controllerProfiles"] != ["standard-2p-v1"]:
                raise ValueError("PSX two-standard-port profile differs")
    if sorted(e["platform"] for e in selected) != sorted(targets) or selected != receipt["engines"]:
        raise ValueError("Four exact engine records required")
    ids = [e["engineId"] for e in new]
    if len(ids) != len(set(ids)): raise ValueError("Duplicate engine identity")
    return updated


def inputs(base, freeze_path, identity_path, prepared_freeze=None):
    if sha(base) != BASE_SHA: raise ValueError("Not the exact signed R126 base")
    frozen = read(freeze_path) if prepared_freeze is None else prepared_freeze
    receipt = read(identity_path)
    if frozen.get("schemaVersion") != 1 or frozen.get("revision") != "R127" or frozen.get("sourceFrozen") is not True:
        raise ValueError("Final R127 source freeze required")
    if frozen.get("baseApkSha256") != BASE_SHA or receipt.get("baseApkSha256") != BASE_SHA or receipt.get("schemaVersion") != 3:
        raise ValueError("Freeze/runtime base or schema differs")
    if frozen.get("identityReceiptSha256") != sha(identity_path): raise ValueError("Runtime receipt changed after freeze")
    if set(frozen.get("payloads", {})) != PAYLOADS: raise ValueError("Only seven replacements and one addition allowed")
    paths, expected = {}, {}
    for name, record in frozen["payloads"].items():
        path = Path(record["path"]).resolve()
        if not re.fullmatch("[0-9a-f]{64}", record["sha256"]): raise ValueError("Invalid SHA256 pin")
        if not fs(path).is_file() or fs(path).stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
            raise ValueError("Frozen payload changed: " + name)
        paths[name], expected[name] = path, record["sha256"]
    if set(receipt.get("payloadSha256", {})) != SHARED:
        raise ValueError("Exact DEX/manifest identity pins required")
    if any(expected[n] != receipt["payloadSha256"][n] for n in SHARED): raise ValueError("DEX/manifest differs from identity")
    if expected["assets/station-online/engines.json"] != receipt["enginesAssetSha256"]:
        raise ValueError("Actual engine asset differs from identity")
    if fs(paths["assets/station-online/engines.json"]).stat().st_size > 32768:
        raise ValueError("Engine asset exceeds the existing client limit")
    if set(receipt.get("markers", {})) != set(MARKERS): raise ValueError("Three final markers required")
    source_sets = None
    for kind, library in MARKERS.items():
        marker = receipt["markers"][kind]
        if marker["runtimeLibrary"] != library or expected[PREFIX + library] != marker["runtimeSha256"]:
            raise ValueError("Runtime ELF differs: " + kind)
        fingerprint_path = identity_path.parent / ("psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json")
        raw = fs(fingerprint_path).read_bytes().rstrip(b"\r\n")
        value = json.loads(raw)
        if raw != canonical(value) or digest(raw) != marker["fingerprintSha256"]:
            raise ValueError("Runtime fingerprint is not the frozen canonical identity")
        binary = fs(paths[PREFIX + library]).read_bytes()
        if binary[:6] != b"\x7fELF\x02\x01" or len(binary) < 20 or struct.unpack_from("<H", binary, 18)[0] != 183:
            raise ValueError("Runtime must be an AArch64 ELF")
        if len(binary) < 64: raise ValueError("Truncated ELF header")
        phoff = struct.unpack_from("<Q", binary, 32)[0]
        stride, count = struct.unpack_from("<HH", binary, 54)
        if not count or stride < 56 or phoff + stride * count > len(binary): raise ValueError("Invalid ELF program headers")
        loads = []
        for index in range(count):
            offset = phoff + stride * index
            if struct.unpack_from("<I", binary, offset)[0] == 1:
                loads.append(struct.unpack_from("<Q", binary, offset + 48)[0])
        if not loads or any(n < 16384 or n & (n - 1) for n in loads): raise ValueError("Runtime LOAD alignment is not 16KiB")
        if raw not in binary or marker["fingerprintSha256"].encode("ascii") not in binary:
            raise ValueError("Runtime does not embed the exact identity")
        if value["baseApkSha256"] != BASE_SHA or value["payloadSha256"] != receipt["payloadSha256"]:
            raise ValueError("Runtime shared payload binding differs")
        candidate_sources = (value["javaSources"], value["productiveTransforms"])
        if source_sets is not None and source_sets != candidate_sources: raise ValueError("Markers bind different sources")
        source_sets = candidate_sources
        if kind != "psx" and value["psxRuntimeSha256"] != receipt["markers"]["psx"]["runtimeSha256"]:
            raise ValueError("Existing marker lacks the final PSX runtime binding")
    if source_sets != current_sources(): raise ValueError("Productive sources changed after fingerprinting")
    policy = read(ROOT / "profile.json")
    psx_manifest = read(identity_path.parent / "psx.fingerprint.json")
    if (psx_manifest["backend"] != policy["backend"] or psx_manifest["options"] != policy["options"] or
            psx_manifest["optionsSha256"] != policy["optionsSha256"] or psx_manifest["inputDelayFrames"] != 4 or
            receipt["normalPsxLibrariesPreserved"] != NORMAL_PINS):
        raise ValueError("PSX runtime does not bind the current normal owner/profile/options")
    with zipfile.ZipFile(fs(base)) as original:
        names = classic_entries(original); classic_zip(base, original.comment)
        if not REPLACED.issubset(names) or ADDED & names: raise ValueError("Unexpected base entry set")
        for name, checksum in NORMAL_PINS.items():
            if entry_sha(original, PREFIX + name) != checksum: raise ValueError("Normal PSX library differs: " + name)
        manifest = engine_manifest(json.loads(original.read("assets/station-online/engines.json")),
                                   read(paths["assets/station-online/engines.json"]), receipt)
        psx_engine = next(e for e in receipt["engines"] if e["platform"] == "psx")
        if psx_engine["backend"] != policy["backend"] or psx_engine["options"] != policy["options"]:
            raise ValueError("PSX engine asset does not bind the current backend/options")
        for engine in receipt["engines"]:
            pins = {engine["library"]: engine["coreSha256"], engine["runtimeLibrary"]: engine["runtimeSha256"], **engine.get("dependencySha256", {})}
            for library, checksum in pins.items():
                if "/" in library or "\\" in library: raise ValueError("Native dependency must be a basename")
                name = PREFIX + library
                actual = expected.get(name) if name in paths else entry_sha(original, name)
                if actual != checksum: raise ValueError("Engine native dependency differs: " + library)
    return frozen, receipt, paths, expected, manifest


def freeze_inputs(base, identity_path, values, freeze_path):
    if fs(freeze_path).exists(): raise FileExistsError("Never overwrite a source freeze")
    records = {}
    for value in values:
        name, separator, raw = value.partition("=")
        if not separator or name not in PAYLOADS or name in records: raise ValueError("Exact payload=path mapping required")
        path = Path(raw).resolve()
        records[name] = {"path": str(path), "sha256": sha(path), "bytes": fs(path).stat().st_size}
    if set(records) != PAYLOADS: raise ValueError("All eight payloads must be supplied")
    value = {"schemaVersion": 1, "revision": "R127", "sourceFrozen": True, "baseApkSha256": BASE_SHA,
             "identityReceiptSha256": sha(identity_path), "payloads": records}
    inputs(base, freeze_path, identity_path, value)
    fs(freeze_path.parent).mkdir(parents=True, exist_ok=True)
    with fs(freeze_path).open("x", encoding="utf-8") as output:
        output.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return {"freeze": str(freeze_path), "freezeSha256": sha(freeze_path), "payloadCount": len(records)}


def package(base, freeze_path, identity_path, out):
    out = out.resolve()
    receipt_path = out.with_suffix(".package.json")
    if out == base.resolve() or fs(out).exists() or fs(receipt_path).exists():
        raise FileExistsError("Never overwrite a base, APK candidate or package receipt")
    frozen, receipt, paths, expected, manifest = inputs(base, freeze_path, identity_path)
    freeze_sha, identity_sha = sha(freeze_path), sha(identity_path)
    preserved, written, removed = {}, {}, []
    fs(out.parent).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(fs(base)) as original, zipfile.ZipFile(fs(out), "w", allowZip64=False) as result:
        result.comment = original.comment
        for info in original.infolist():
            name = info.filename
            if signature_metadata(name): removed.append(name); continue
            target_info = copy.copy(info)
            if name in paths:
                target_info.file_size = fs(paths[name]).stat().st_size
                with fs(paths[name]).open("rb") as source, result.open(target_info, "w", force_zip64=False) as target:
                    written[name] = stream_copy(source, target)
            else:
                with original.open(info) as source, result.open(target_info, "w", force_zip64=False) as target:
                    written[name] = stream_copy(source, target)
                preserved[name] = written[name]
        for name in sorted(ADDED):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED; info.external_attr = 0o100644 << 16
            info.file_size = fs(paths[name]).stat().st_size
            with fs(paths[name]).open("rb") as source, result.open(info, "w", force_zip64=False) as target:
                written[name] = stream_copy(source, target)
    with zipfile.ZipFile(fs(out)) as result:
        if classic_entries(result) != set(written): raise ValueError("Output entry set differs")
        if any(signature_metadata(n) for n in result.namelist()): raise ValueError("Original signature metadata survived")
        for name, checksum in written.items():
            if entry_sha(result, name) != checksum: raise ValueError("Independent read-back differs: " + name)
        for name, checksum in expected.items():
            if written[name] != checksum: raise ValueError("Final payload changed while copying: " + name)
        if json.loads(result.read("assets/station-online/engines.json")) != manifest: raise ValueError("Written engine asset differs")
        classic_zip(out, result.comment)
    if sha(freeze_path) != freeze_sha or sha(identity_path) != identity_sha:
        raise ValueError("Freeze/identity receipt changed during packaging")
    # Revalidate productive source pins and binaries after the complete read-back.
    inputs(base, freeze_path, identity_path)
    report = {"schemaVersion": 1, "revision": "R127", "baseApkSha256": BASE_SHA,
        "freezeSha256": freeze_sha, "identityReceiptSha256": identity_sha,
        "unsignedApkSha256": sha(out), "unsignedApkBytes": fs(out).stat().st_size,
        "replacedEntrySha256": {n: written[n] for n in sorted(REPLACED)},
        "addedEntrySha256": {n: written[n] for n in sorted(ADDED)},
        "preservedEntryCount": len(preserved), "preservedEntrySha256": preserved,
        "preservedEntryManifestSha256": digest(canonical(preserved)),
        "removedSignatureMetadata": removed, "engineIds": [e["engineId"] for e in receipt["engines"]],
        "classicZip": True, "zip64": False, "signingPerformed": False, "zipalignPerformed": False,
        "offlineEmulatorEntriesChanged": False, "installed": False, "serverActivationConfirmed": False,
        "physicalGameplayValidated": False}
    write(receipt_path, report)
    return {k: report[k] for k in ("unsignedApkSha256", "unsignedApkBytes", "preservedEntryCount", "engineIds")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "freeze", "identity-receipt"): parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--out", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check-inputs", action="store_true")
    group.add_argument("--write-freeze", action="store_true")
    parser.add_argument("--payload", action="append", default=[])
    args = parser.parse_args()
    if args.write_freeze:
        result = freeze_inputs(args.base, args.identity_receipt, args.payload, args.freeze)
    elif args.check_inputs:
        if args.payload or args.out: parser.error("--check-inputs writes nothing and accepts no --payload/--out")
        _, receipt, _, _, _ = inputs(args.base, args.freeze, args.identity_receipt)
        result = {"inputsVerified": True, "engineIds": [e["engineId"] for e in receipt["engines"]], "apkWritten": False}
    else:
        if args.out is None or args.payload: parser.error("Assembly needs --out and accepts no --payload")
        result = package(args.base, args.freeze, args.identity_receipt, args.out)
    print(json.dumps(result))


if __name__ == "__main__": main()
