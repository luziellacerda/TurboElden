"""Prepare private, pinned Sony assets; never build, sign, install, or publish an APK."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import zipfile

OFFICIAL = {
    "ps3": {
        "sha256": "c5a58fb056ae333b8bd6ed69e6bfacdd1e5bf7e0ac2134456a0622bd94a3e466",
        "bytes": 40122859, "versionName": "2.43", "versionCode": 43, "minSdk": 28,
        "certificateSha256": "7acaebec9e121cf269d2654a40423463456dd3bde8219a4d1359bf38138690ca",
        "requiredAssets": ("config/config.yml", "licenses.html", "patch.yml"),
        "assetPrefixes": ("Icons/ui/",), "expectedNativeCount": 7,
        "glibc": frozenset(),
    },
    "ps4": {
        "sha256": "4077b0d0b80e354c71eff1ce2c003f122449ac266eb27a6ac26744d3f9809a08",
        "bytes": 207779222, "versionName": "0.2.4", "versionCode": 26100114, "minSdk": 31,
        "certificateSha256": "a1d6e9aa7b3ff5ae3354f082b133b4d37b156be8aeaf704b0bfaaaee625761ee",
        "requiredAssets": ("runtime/runtime.zip", "runtime/manifest.json", "runtime/native-runtime.json"),
        "assetPrefixes": ("licenses/", "patches/repository/"), "expectedNativeCount": 16,
        "glibc": frozenset({"libXss.so", "libbachata_host_loader.so", "libxkbcommon.so"}),
    },
}
SYSTEM_LIBRARIES = frozenset({
    "libandroid.so", "libc.so", "libdl.so", "libm.so", "liblog.so", "libz.so", "libvulkan.so",
    "libOpenSLES.so", "libEGL.so", "libGLESv1_CM.so", "libGLESv2.so", "libGLESv3.so", "libjnigraphics.so",
})
PS4_DERIVED_PATHS = frozenset({"upstream/derived/owner.dex", "upstream/derived/pkg-rsa.bin"})
PS3_FIRMWARE_SHA256 = "158471fd834f8ea8036136b6aab43cd86c7ba73d79ca30e0af3c0fe0001cf365"
PS3_FIRMWARE_BYTES = 206197916


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")


def safe_relative(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 512 or "\\" in value or ":" in value or "\0" in value:
        raise ValueError("Unsafe Sony asset path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("Unsafe Sony asset path segment")
    return value


def ordinary(path: Path) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Input must be an ordinary file: {path.name}")
    resolved = path.resolve(strict=True)
    # Windows reparse points must not be accepted as a substitute for the pinned input.
    for current in [path, *path.parents]:
        if current.exists() and (current.is_symlink() or
                getattr(current.stat(follow_symlinks=False), "st_file_attributes", 0) & 0x400):
            raise ValueError("Input contains a symlink/reparse point")
    return resolved


def stamp(path: Path) -> tuple[int, int, int, int]:
    info = path.stat()
    return info.st_size, info.st_mtime_ns, info.st_dev, info.st_ino


def elf_contract(raw: bytes) -> dict:
    if len(raw) < 64 or raw[:7] != b"\x7fELF\x02\x01\x01":
        raise ValueError("Expected a little-endian ELF64 native artifact")
    header = struct.unpack_from("<16sHHIQQQIHHHHHH", raw)
    if header[2] != 183 or header[9] != 56:
        raise ValueError("Sony native artifact is not the audited AArch64 ELF format")
    phoff, phnum = header[5], header[10]
    if phnum == 0 or phnum > 1000 or phoff + phnum * 56 > len(raw):
        raise ValueError("Invalid ELF program header table")
    loads, dynamic = [], None
    for index in range(phnum):
        row = struct.unpack_from("<IIQQQQQQ", raw, phoff + 56 * index)
        if row[2] + row[5] > len(raw) or row[5] > row[6]:
            raise ValueError("Invalid ELF file segment")
        if row[0] == 1:
            loads.append({"offset": row[2], "vaddr": row[3], "bytes": row[5], "alignment": row[7]})
        elif row[0] == 2:
            if dynamic is not None:
                raise ValueError("Multiple ELF dynamic segments")
            dynamic = (row[2], row[5])
    if not loads or dynamic is None or dynamic[1] % 16:
        raise ValueError("Missing ELF load/dynamic segments")
    tags: dict[int, list[int]] = {}
    terminated = False
    for offset in range(dynamic[0], dynamic[0] + dynamic[1], 16):
        tag, value = struct.unpack_from("<qQ", raw, offset)
        if tag == 0:
            terminated = True
            break
        tags.setdefault(tag, []).append(value)
    if not terminated or len(tags.get(5, [])) != 1 or len(tags.get(10, [])) != 1 or len(tags.get(14, [])) != 1:
        raise ValueError("Missing/ambiguous ELF dynamic string table or SONAME")
    address, length = tags[5][0], tags[10][0]
    containing = [row for row in loads if row["vaddr"] <= address and
        address + length <= row["vaddr"] + row["bytes"]]
    if len(containing) != 1:
        raise ValueError("ELF string table does not map to one file-backed segment")
    offset = containing[0]["offset"] + address - containing[0]["vaddr"]
    strings = raw[offset:offset + length]

    def string(index: int) -> str:
        if index >= len(strings) or (end := strings.find(b"\0", index)) < 0:
            raise ValueError("Invalid ELF dynamic string")
        value = strings[index:end].decode("ascii", "strict")
        if not re.fullmatch(r"[A-Za-z0-9_+.-]+", value):
            raise ValueError("Unsafe native dependency/SONAME")
        return value

    alignments = [row["alignment"] for row in loads]
    page_16k = all(row["alignment"] >= 16384 and row["offset"] % 16384 == row["vaddr"] % 16384 for row in loads)
    return {"elfMachine": 183, "soname": string(tags[14][0]),
        "needed": [string(index) for index in tags.get(1, [])], "loadAlignment": min(alignments),
        "ptLoad": loads, "elf16KiBCompatible": page_16k}


def write_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def copy_entry(archive: zipfile.ZipFile, entry: zipfile.ZipInfo, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest, count = hashlib.sha256(), 0
    with archive.open(entry) as source, destination.open("xb") as output:
        for data in iter(lambda: source.read(128 * 1024), b""):
            count += len(data)
            digest.update(data)
            output.write(data)
    if count != entry.file_size:
        raise ValueError("Pinned ZIP entry length changed")
    return {"bytes": count, "sha256": digest.hexdigest()}


def derived_files(input_json: Path | None, output: Path) -> tuple[list[dict], dict | None]:
    if input_json is None:
        return [], None
    source = ordinary(input_json)
    raw = source.read_bytes()
    receipt = json.loads(raw)
    if receipt.get("schema") != "station.sony.ps4.derived.v1" or receipt.get("sourceApkSha256") != OFFICIAL["ps4"]["sha256"]:
        raise ValueError("PS4 derived receipt does not bind the audited official source APK")
    rows = receipt.get("files")
    if not isinstance(rows, list) or {row.get("path") for row in rows} != PS4_DERIVED_PATHS or len(rows) != 2:
        raise ValueError("PS4 derived artifacts require exactly owner.dex and the explicitly authorized local PKG material")
    # Descriptor bytes must reproduce in a different private build directory. Physical input paths
    # remain in the private receipt, but do not participate in the immutable module identity.
    provenance = {"schema": receipt["schema"], "sourceApkSha256": receipt["sourceApkSha256"],
        "files": [{key: row[key] for key in ("path", "bytes", "sha256")}
            for row in sorted(rows, key=lambda value: value["path"])]}
    provenance_sha = hashlib.sha256(canonical(provenance)).hexdigest()
    result = []
    for row in sorted(rows, key=lambda value: value["path"]):
        relative = safe_relative(row["path"])
        original = ordinary(Path(row["file"]))
        before = stamp(original)
        if before[0] != row["bytes"] or sha256(original) != row["sha256"]:
            raise ValueError("PS4 derived artifact differs from its receipt")
        if relative.endswith("owner.dex"):
            with original.open("rb") as stream:
                magic = stream.read(8)
            if not re.fullmatch(b"dex\n0[3-4][0-9]\x00", magic):
                raise ValueError("PS4 child owner is not a DEX artifact")
        elif not 0 < before[0] <= 1024 * 1024:
            raise ValueError("Authorized PS4 local material exceeds its size bound")
        asset = "sony/ps4/" + relative
        target = output / "assets" / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        with original.open("rb") as stream, target.open("xb") as destination:
            shutil.copyfileobj(stream, destination, 128 * 1024)
        if stamp(original) != before or sha256(target) != row["sha256"]:
            raise ValueError("PS4 derived artifact changed during copying")
        result.append({"path": relative, "asset": asset, "kind": "asset",
            "bytes": before[0], "sha256": row["sha256"],
            "derivationReceiptSha256": provenance_sha})
    return result, {"inputReceiptSha256": hashlib.sha256(raw).hexdigest(),
        "stableProvenanceSha256": provenance_sha,
        "schema": receipt["schema"], "sourceApkSha256": receipt["sourceApkSha256"]}


def firmware_file(firmware: Path, output: Path) -> dict:
    firmware = ordinary(firmware)
    before = stamp(firmware)
    if before[0] != PS3_FIRMWARE_BYTES or sha256(firmware) != PS3_FIRMWARE_SHA256:
        raise ValueError("PS3 firmware is not the exact authorized private Sony 4.93 artifact")
    relative = "upstream/PS3UPDAT.PUP"
    asset = "sony/ps3/" + relative
    target = output / "assets" / asset
    target.parent.mkdir(parents=True, exist_ok=True)
    with firmware.open("rb") as stream, target.open("xb") as destination:
        shutil.copyfileobj(stream, destination, 128 * 1024)
    if stamp(firmware) != before or sha256(target) != PS3_FIRMWARE_SHA256:
        raise ValueError("PS3 firmware changed during its private copying")
    return {"path": relative, "asset": asset, "kind": "asset", "bytes": PS3_FIRMWARE_BYTES,
        "sha256": PS3_FIRMWARE_SHA256, "source": "authorized-private-Sony-4.93-firmware"}


def prepare_module(system: str, apk: Path, output: Path, derived: Path | None = None,
        ps3_firmware: Path | None = None) -> dict:
    spec = OFFICIAL[system]
    apk = ordinary(apk)
    before = stamp(apk)
    if before[0] != spec["bytes"] or sha256(apk) != spec["sha256"]:
        raise ValueError(f"{system} input is not the audited official APK")
    files, native = [], []
    with zipfile.ZipFile(apk) as archive:
        entries: dict[str, zipfile.ZipInfo] = {}
        for entry in archive.infolist():
            name = entry.filename.rstrip("/")
            safe_relative(name)
            if name in entries:
                raise ValueError("Duplicate source APK entry")
            entries[name] = entry
        selected_assets = ["assets/" + path for path in spec["requiredAssets"]]
        selected_assets.extend(name for name, entry in entries.items() if not entry.is_dir() and
            any(name.startswith("assets/" + prefix) for prefix in spec["assetPrefixes"]))
        selected_native = [name for name, entry in entries.items() if not entry.is_dir() and
            name.startswith("lib/arm64-v8a/")]
        if len(selected_native) != spec["expectedNativeCount"] or len(selected_assets) != len(set(selected_assets)):
            raise ValueError("Source APK native/asset selection does not match the audited set")
        for name in sorted(selected_native + selected_assets):
            entry = entries.get(name)
            if entry is None or entry.is_dir() or stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError("Required source APK artifact is missing or linked")
            is_native = name.startswith("lib/")
            relative = "native/" + PurePosixPath(name).name if is_native else "upstream/" + name.removeprefix("assets/")
            asset = f"sony/{system}/{relative}"
            destination = output / "assets" / asset
            row = {"path": relative, "asset": asset, "sourceEntry": name,
                "kind": "asset", **copy_entry(archive, entry, destination)}
            if is_native:
                details = elf_contract(destination.read_bytes())
                row.update(details)
                row["kind"] = "glibc" if PurePosixPath(name).name in spec["glibc"] else "bionic"
                if row["kind"] == "bionic" and not row["elf16KiBCompatible"]:
                    raise ValueError("Audited Bionic ELF no longer has 16 KiB-compatible PT_LOAD alignment")
                native.append(row)
            files.append(row)
    if stamp(apk) != before or sha256(apk) != spec["sha256"]:
        raise ValueError("Official source APK changed while preparing its private artifacts")
    if system == "ps4":
        extra, derived_receipt = derived_files(derived, output)
        files.extend(extra)
    else:
        derived_receipt = None
        if ps3_firmware is not None:
            files.append(firmware_file(ps3_firmware, output))
    bionic = {row["soname"]: row for row in native if row["kind"] == "bionic"}
    if len(bionic) != sum(row["kind"] == "bionic" for row in native):
        raise ValueError("Duplicate private Bionic SONAME")
    for row in bionic.values():
        if row["soname"] != PurePosixPath(row["path"]).name:
            raise ValueError("Bionic native basename/SONAME mismatch; no blind renames allowed")
        unknown = set(row["needed"]) - bionic.keys() - SYSTEM_LIBRARIES
        if unknown:
            raise ValueError(f"Unclosed Bionic dependency set: {sorted(unknown)}")
    files.sort(key=lambda row: row["path"])
    descriptor = {"schemaVersion": 1, "system": system, "abi": "arm64-v8a", "minSdk": spec["minSdk"],
        "sourceApkSha256": spec["sha256"], "sourceApkBytes": spec["bytes"],
        "sourceVersionName": spec["versionName"], "sourceVersionCode": spec["versionCode"], "files": files}
    module_digest = hashlib.sha256(canonical(descriptor)).hexdigest()
    descriptor["moduleId"] = f"{system}-{module_digest[:24]}"
    raw = canonical(descriptor)
    manifest_asset = f"assets/sony/{system}/module.json"
    write_new(output / manifest_asset, raw)
    payloads = {"assets/" + row["asset"]: {"path": str(output / "assets" / row["asset"]),
        "bytes": row["bytes"], "sha256": row["sha256"]} for row in files}
    payloads[manifest_asset] = {"path": str(output / manifest_asset), "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest()}
    return {"system": system, "moduleId": descriptor["moduleId"],
        "manifestSha256": hashlib.sha256(raw).hexdigest(), "sourceApkSha256": spec["sha256"],
        "sourceApkBytes": spec["bytes"], "previouslyAuditedCertificateSha256": spec["certificateSha256"],
        "certificateVerificationExecutedByThisRecipe": False,
        "nativeFiles": native, "derivedReceipt": derived_receipt,
        "selectedUpstreamAssets": [row["sourceEntry"] for row in files if row.get("sourceEntry", "").startswith("assets/")],
        "payloads": payloads, "sourceNativeBytesUnmodified": True,
        "foreignDexOrResourcesMerged": False, "glibcLibrariesIncludedButNotBionicLoadTargets": sorted(spec["glibc"])}


def prepare(ps3_apk: Path, ps4_apk: Path, out: Path, ps4_derived: Path | None = None,
        ps3_firmware: Path | None = None) -> dict:
    if ps4_derived is None:
        raise ValueError("The final PS4 child-owner DEX receipt is required before freezing pins")
    if ps3_firmware is None:
        raise ValueError("The explicitly authorized private PS3 firmware is required before freezing pins")
    out = out.absolute()
    if out.is_symlink() or (out.exists() and any(out.iterdir())):
        raise ValueError("Output must be a new or empty private directory")
    out.mkdir(parents=True, exist_ok=True)
    if out.resolve() != out:
        raise ValueError("Output path may not traverse symlinks/reparse points")
    modules = {system: prepare_module(system, apk, out, ps4_derived if system == "ps4" else None,
        ps3_firmware if system == "ps3" else None)
        for system, apk in (("ps3", ps3_apk), ("ps4", ps4_apk))}
    constants = """package org.emulationstation.frontend.sony;

/** Generated from the private, audited assets of this exact release. */
public final class StationSonyAssetPins {
    private StationSonyAssetPins() { }
    public static final String PS3_MANIFEST_SHA256 = "%s";
    public static final String PS4_MANIFEST_SHA256 = "%s";
}
""" % (modules["ps3"]["manifestSha256"], modules["ps4"]["manifestSha256"])
    generated = out / "generated-java/org/emulationstation/frontend/sony/StationSonyAssetPins.java"
    write_new(generated, constants.encode("utf-8"))
    receipt = {"schema": "station.sony.internal.assets.v1", "passed": True,
        "assetsOnly": True, "packageBuilt": False, "androidLoadOrGameplayValidated": False,
        "preparedOfficialAssetsDoNotMeanFirmwareOrGamesInstalled": True,
        "firmwareBundledPrivatelyByExplicitHumanAuthorization": True,
        "pkgMaterialBundledPrivatelyByExplicitHumanAuthorization": True,
        "sourceRecipeSha256": sha256(Path(__file__)), "modules": modules,
        "generatedSource": {"path": str(generated), "sha256": sha256(generated), "bytes": generated.stat().st_size},
        "payloads": {name: row for module in modules.values() for name, row in module["payloads"].items()}}
    write_new(out / "sony-assets.json", canonical(receipt))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ps3-apk", type=Path, required=True)
    parser.add_argument("--ps4-apk", type=Path, required=True)
    parser.add_argument("--ps4-derived", type=Path, required=True)
    parser.add_argument("--ps3-firmware", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = prepare(args.ps3_apk, args.ps4_apk, args.out, args.ps4_derived, args.ps3_firmware)
    print(json.dumps({"passed": True, "assetCount": len(receipt["payloads"]),
        "receipt": str(args.out / "sony-assets.json")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
