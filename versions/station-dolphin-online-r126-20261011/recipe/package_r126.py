"""Build and hash-check an unsigned classic-ZIP R126 APK from exact R125.

Six replacements and six additions are permitted. All offline cores, N64 core,
plugins, DEX36, media and other entries remain byte-identical. This does not
align, sign, install, authenticate a room or activate a server engine.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import re
import zipfile

zipfile.ZIP64_LIMIT = (1 << 32) - 1
spec = importlib.util.spec_from_file_location("r126_identity", Path(__file__).with_name("build_runtime_identity.py"))
identity = importlib.util.module_from_spec(spec); spec.loader.exec_module(identity)
REPLACED = frozenset((*identity.PAYLOADS, "assets/station-online/engines.json", identity.PREFIX + identity.N64_MARKER))
ADDED = frozenset(identity.PREFIX + name for name in (*identity.DOLPHIN_NAMES, identity.DOLPHIN_MARKER))

def signature_metadata(name):
    return bool(re.fullmatch(r"META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))", name, re.I))

def stream_copy(source, target):
    checksum = hashlib.sha256()
    for raw in iter(lambda:source.read(1048576), b""):
        target.write(raw); checksum.update(raw)
    return checksum.hexdigest()

def entry_sha(archive, name):
    checksum = hashlib.sha256()
    with archive.open(name) as source:
        for raw in iter(lambda:source.read(1048576), b""): checksum.update(raw)
    return checksum.hexdigest()

def classic_zip(path, comment):
    position = identity.fs(path).stat().st_size - 22 - len(comment)
    with identity.fs(path).open("rb") as source:
        source.seek(position - 20)
        if source.read(4) == b"PK\x06\x07": raise ValueError("APK must not have a ZIP64 locator")
        source.seek(position)
        if source.read(4) != b"PK\x05\x06": raise ValueError("Invalid classic ZIP end record")

def inputs(base, freeze_path, runtime_dir):
    if identity.sha(base) != identity.BASE_SHA: raise ValueError("Not exact signed R125 base")
    frozen = identity.read_json(freeze_path); receipt = identity.read_json(runtime_dir / "runtime-identity.json")
    if frozen.get("schemaVersion") != 2 or frozen.get("sourceFrozen") is not True:
        raise ValueError("Final source freeze required")
    if frozen["baseApkSha256"] != identity.BASE_SHA or receipt["baseApkSha256"] != identity.BASE_SHA:
        raise ValueError("Frozen/marker base differs")
    java, transforms = identity.productive_sources()
    if (java, transforms) != (frozen["javaSources"], frozen["productiveTransforms"]): raise ValueError("Source changed after marker freeze")
    if identity.validate_n64(base, frozen["n64"]["r125FreezePath"]) != frozen["n64"]: raise ValueError("N64 proof changed")
    if identity.validate_dolphin(base, frozen["dolphin"]["directory"], frozen["dolphin"]["stage"]) != frozen["dolphin"]: raise ValueError("Dolphin proof changed")
    if set(frozen["payloads"]) != identity.PAYLOADS: raise ValueError("Payload set differs")
    replacements = {name:Path(record["path"]) for name, record in frozen["payloads"].items()}
    expected = {name:record["sha256"] for name, record in frozen["payloads"].items()}
    replacements["assets/station-online/engines.json"] = runtime_dir / "engines.json"
    expected["assets/station-online/engines.json"] = receipt["enginesAssetSha256"]
    additions = {identity.PREFIX + name:Path(frozen["dolphin"]["libraries"][name]["path"]) for name in identity.DOLPHIN_NAMES}
    expected.update({identity.PREFIX + name:record["sha256"] for name, record in frozen["dolphin"]["libraries"].items()})
    for kind in ("n64", "dolphin"):
        marker = receipt["markers"][kind]; path = runtime_dir / marker["runtimeLibrary"]
        fingerprint = identity.canonical(identity.fingerprint(frozen, kind))
        if marker["fingerprintSha256"] != identity.digest(fingerprint): raise ValueError("Marker fingerprint differs")
        raw = identity.fs(path).read_bytes()
        if fingerprint not in raw or marker["fingerprintSha256"].encode() not in raw:
            raise ValueError("Marker does not embed the frozen canonical identity")
        name = identity.PREFIX + marker["runtimeLibrary"]
        (replacements if kind == "n64" else additions)[name] = path
        expected[name] = marker["runtimeSha256"]
    if set(replacements) != REPLACED or set(additions) != ADDED: raise ValueError("Only six replacements/six additions allowed")
    for name, path in {**replacements, **additions}.items():
        if identity.sha(path) != expected[name]: raise ValueError("Final input bytes changed: " + name)
    with zipfile.ZipFile(base) as archive: original = json.loads(archive.read("assets/station-online/engines.json"))
    manifest, engines = identity.engines(original, frozen, receipt["markers"])
    if identity.read_json(runtime_dir / "engines.json") != manifest or engines != receipt["engines"]:
        raise ValueError("Actual engines differ from frozen source/binaries")
    return frozen, receipt, replacements, additions, expected

def package(base, freeze_path, runtime_dir, out):
    out = identity.checked_output(out)
    if identity.fs(out).exists(): raise FileExistsError("Never overwrite an APK candidate")
    frozen, receipt, replacements, additions, expected = inputs(base, freeze_path, runtime_dir)
    original_hashes, written_hashes, removed = {}, {}, []
    identity.fs(out.parent).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(base) as original, zipfile.ZipFile(out, "w", allowZip64=False) as result:
        names = original.namelist()
        if len(names) != len(set(names)): raise ValueError("Duplicate base ZIP entry")
        if not REPLACED.issubset(names) or ADDED.intersection(names): raise ValueError("Unexpected base entry set")
        result.comment = original.comment
        for info in original.infolist():
            name = info.filename
            if signature_metadata(name): removed.append(name); continue
            target_info = copy.copy(info)
            if name in replacements:
                path = replacements[name]; target_info.file_size = identity.fs(path).stat().st_size
                with identity.fs(path).open("rb") as source, result.open(target_info, "w") as target:
                    written_hashes[name] = stream_copy(source, target)
            else:
                with original.open(info) as source, result.open(target_info, "w") as target:
                    written_hashes[name] = stream_copy(source, target)
                original_hashes[name] = written_hashes[name]
        for name, path in additions.items():
            info = zipfile.ZipInfo(name, (1980,1,1,0,0,0)); info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16; info.file_size = identity.fs(path).stat().st_size
            with identity.fs(path).open("rb") as source, result.open(info, "w") as target:
                written_hashes[name] = stream_copy(source, target)
    with zipfile.ZipFile(out) as result:
        if len(result.namelist()) != len(set(result.namelist())) or set(result.namelist()) != set(written_hashes):
            raise ValueError("Output ZIP entry set differs")
        for name, checksum in written_hashes.items():
            if entry_sha(result, name) != checksum: raise ValueError("Read-back output bytes differ: " + name)
        for name, checksum in expected.items():
            if written_hashes[name] != checksum: raise ValueError("Final payload hash differs: " + name)
        if original_hashes[identity.PREFIX + identity.N64_CORE] != identity.N64_CORE_SHA or original_hashes["classes36.dex"] != identity.DEX36_SHA:
            raise ValueError("Normal/N64 preserved core or hooks changed")
        for engine in receipt["engines"]:
            for name, checksum in engine["dependencySha256"].items():
                if written_hashes[identity.PREFIX + name] != checksum: raise ValueError("Pinned emulator dependency not packaged exactly: " + name)
        classic_zip(out, result.comment)
    report = {"schemaVersion":2, "revision":"R126", "baseApkSha256":identity.BASE_SHA,
              "unsignedApkSha256":identity.sha(out), "unsignedApkBytes":identity.fs(out).stat().st_size,
              "replacedEntrySha256":{name:written_hashes[name] for name in replacements},
              "addedEntrySha256":{name:written_hashes[name] for name in additions},
              "preservedEntryCount":len(original_hashes), "preservedEntrySha256":original_hashes,
              "removedSignatureMetadata":removed, "engineIds":[e["engineId"] for e in receipt["engines"]],
              "classicZip":True,"zip64":False,"signingPerformed":False,"zipalignPerformed":False,
              "installed":False,"offlineEmulatorEntriesChanged":False,"physicalGameplayValidated":False}
    identity.write_json(out.with_suffix(".package.json"), report)
    return {key:report[key] for key in ("unsignedApkSha256","unsignedApkBytes","preservedEntryCount","engineIds")}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("base","freeze","runtime-dir","out"): p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args(); print(json.dumps(package(a.base,a.freeze,a.runtime_dir,a.out)))

if __name__ == "__main__": main()
