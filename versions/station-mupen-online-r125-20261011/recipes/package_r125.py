"""Assemble an unsigned R125 APK from exact R124 and frozen final payloads.

Only four existing entries and two new Station N64 libraries may differ. This
does not sign, align or install an APK. Original offline cores/plugins, media,
data formats and all other entries are preserved and hash-checked on disk.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import zipfile

# APK signing/install tools require classic ZIP. Python otherwise emits ZIP64
# at 2 GiB, despite unsigned 32-bit ZIP offsets supporting up to 4 GiB. R124
# is already above 2 GiB and below this actual ZIP limit.
zipfile.ZIP64_LIMIT = (1 << 32) - 1

SPEC = importlib.util.spec_from_file_location("runtime_identity", Path(__file__).with_name("build_runtime_identity.py"))
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)

def signature_metadata(name: str) -> bool:
    return bool(re.fullmatch(r"META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))", name, re.IGNORECASE))

def stream_copy(source, target) -> str:
    checksum = hashlib.sha256()
    for raw in iter(lambda: source.read(1024 * 1024), b""):
        target.write(raw)
        checksum.update(raw)
    return checksum.hexdigest()

def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    checksum = hashlib.sha256()
    with archive.open(name) as source:
        for raw in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(raw)
    return checksum.hexdigest()

def package(base: Path, frozen_path: Path, runtime_dir: Path, out: Path) -> dict:
    out = identity.checked_output(out)
    if out.exists():
        raise FileExistsError("Never overwrite an existing APK candidate")
    if identity.sha(base) != identity.BASE_SHA256:
        raise ValueError("Base APK is not exact R124")
    frozen = json.loads(identity.fs(frozen_path).read_text(encoding="utf-8"))
    receipt = json.loads(identity.fs(runtime_dir / "runtime-identity.json").read_text(encoding="utf-8"))
    if receipt["fingerprintSha256"] != identity.digest(identity.canonical(identity.fingerprint(frozen))):
        raise ValueError("Runtime was not built from these frozen inputs")
    if identity.source_files() != frozen["sources"]:
        raise ValueError("Source changed after runtime freeze")
    if frozen["baseApkSha256"] != identity.BASE_SHA256 or receipt["baseApkSha256"] != identity.BASE_SHA256:
        raise ValueError("Frozen/runtime base differs")
    payloads = {name: Path(info["path"]) for name, info in frozen["payloads"].items()}
    if set(payloads) != identity.PAYLOAD_NAMES:
        raise ValueError("Final DEX/manifest payload set differs")
    for name, path in payloads.items():
        if identity.sha(path) != frozen["payloads"][name]["sha256"]:
            raise ValueError("Final payload changed: " + name)
    engines_path = runtime_dir / "engines.json"
    if identity.sha(engines_path) != receipt["enginesAssetSha256"]:
        raise ValueError("Generated engine asset changed")
    payloads["assets/station-online/engines.json"] = engines_path
    additions = {
        identity.PREFIX + identity.CORE_NAME: runtime_dir / identity.CORE_NAME,
        identity.PREFIX + identity.RUNTIME_NAME: runtime_dir / identity.RUNTIME_NAME,
    }
    for name, path in additions.items():
        expected = receipt["coreSha256"] if name.endswith(identity.CORE_NAME) else receipt["runtimeSha256"]
        if identity.sha(path) != expected:
            raise ValueError("Generated native library changed: " + name)
    original_hashes, written_hashes, removed_signatures = {}, {}, []
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(base) as original, zipfile.ZipFile(out, "w", allowZip64=False) as result:
        names = original.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate base ZIP entry")
        if not set(payloads).issubset(names) or set(additions).intersection(names):
            raise ValueError("Replacement/addition entry set differs from exact base")
        result.comment = original.comment
        for source_info in original.infolist():
            name = source_info.filename
            if signature_metadata(name):
                removed_signatures.append(name)
                continue
            target_info = copy.copy(source_info)
            if name in payloads:
                target_info.file_size = identity.fs(payloads[name]).stat().st_size
                with identity.fs(payloads[name]).open("rb") as source, result.open(target_info, "w", force_zip64=target_info.file_size >= zipfile.ZIP64_LIMIT) as target:
                    written_hashes[name] = stream_copy(source, target)
            else:
                with original.open(source_info) as source, result.open(target_info, "w", force_zip64=target_info.file_size >= zipfile.ZIP64_LIMIT) as target:
                    written_hashes[name] = stream_copy(source, target)
                original_hashes[name] = written_hashes[name]
        for name, path in additions.items():
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            info.file_size = path.stat().st_size
            with path.open("rb") as source, result.open(info, "w") as target:
                written_hashes[name] = stream_copy(source, target)
    with zipfile.ZipFile(out) as result:
        if set(result.namelist()) != set(written_hashes):
            raise ValueError("Output entry set differs")
        for name, expected in written_hashes.items():
            if entry_sha(result, name) != expected:
                raise ValueError("Output entry hash differs: " + name)
        engines = json.loads(result.read("assets/station-online/engines.json"))
        matching = [e for e in engines["engines"] if e.get("platform") == "n64"]
        if len(matching) != 1 or matching[0] != receipt["engine"]:
            raise ValueError("N64 engine identity not packaged exactly")
        for name, sha256 in matching[0]["dependencySha256"].items():
            if original_hashes.get(identity.PREFIX + name) != sha256:
                raise ValueError("Pinned normal emulator dependency not preserved: " + name)
        eocd_position = out.stat().st_size - 22 - len(result.comment)
    with out.open("rb") as stream:
        stream.seek(eocd_position - 20)
        if stream.read(4) == b"PK\x06\x07":
            raise ValueError("APK unexpectedly contains a ZIP64 locator")
    result = {
        "schemaVersion": 1, "baseApkSha256": identity.BASE_SHA256,
        "unsignedApkSha256": identity.sha(out), "unsignedApkBytes": out.stat().st_size,
        "replacedEntrySha256": {name: written_hashes[name] for name in payloads},
        "addedEntrySha256": {name: written_hashes[name] for name in additions},
        "preservedEntryCount": len(original_hashes), "preservedEntrySha256": original_hashes,
        "removedSignatureMetadata": removed_signatures, "engineId": receipt["engine"]["engineId"],
        "signingPerformed": False, "zipalignPerformed": False, "installed": False,
        "androidPeerGameplayValidated": False, "offlineEmulatorEntriesChanged": False,
        "classicZip": True, "zip64": False,
    }
    out.with_suffix(".package.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return {key: result[key] for key in ("unsignedApkSha256", "unsignedApkBytes", "preservedEntryCount", "engineId")}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.base, args.freeze, args.runtime_dir, args.out)))

if __name__ == "__main__":
    main()
