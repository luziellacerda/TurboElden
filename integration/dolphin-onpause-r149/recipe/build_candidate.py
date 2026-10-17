"""Build an unsigned R149 candidate from the exact signed R148 APK.

Only the two onPause flags in DEX10 and four owner identity entries may differ.
Signing, installation, and server registration are separate private steps.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
zipfile.ZIP64_LIMIT = (1 << 32) - 1

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
BASE_SHA = "c8b8c30cac7d36ec2a8ca8d470542096919435c749dede535cd0d58648e00dc1"
BASE_SIZE = 2_715_089_935
OLD_DEX_SHA = "4d200405747b4d42108fe6bd8afdccc290db3fa1a72a9aa28c779f8772a53a78"
NEW_DEX_SHA = "1f1b285af161fbf85573c081bee3bc6e4c95f90485d8d405ae064b86feb9144e"
CAROUSEL_SHA = "313de078f8c300b6c7944de2ce03292de697532bc1a493b7406fdbb8260fbd28"
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
DEX_PARTITION = "classes10.dex"
ENGINES = "assets/station-online/engines.json"
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
WRAPPERS = {
    "psx": "libstation_psx_online.so",
    "n64": "libstation_mupen64plus_runtime.so",
    "dolphin": "libstation_dolphin_runtime.so",
}
REPLACED = {DEX_PARTITION, ENGINES, *("lib/arm64-v8a/" + name for name in WRAPPERS.values())}
DEX = {"classes.dex", *(f"classes{index}.dex" for index in range(2, 41))}
SOURCE_FILES = (
    "integration/dolphin-onpause-r149/recipe/patch_dex.py",
    "integration/dolphin-onpause-r149/recipe/build_candidate.py",
)
IDENTITY_SOURCE_PINS = {
    "integration/online-lifecycle-review-r135/recipe/build_runtime_identity.py": "f1a1d8e3bd161bb6751801efc5a314e61b403f670822085dc92127dc63fe98da",
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
}


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str, imports: Path | None = None):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Identity primitive missing: " + str(path))
    module = importlib.util.module_from_spec(spec)
    before = list(sys.path)
    try:
        if imports is not None:
            sys.path.insert(0, str(imports))
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = before
    return module


def frozen_source(commit: str) -> dict[str, str]:
    need(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "Complete frozen source commit required")
    result = {}
    for name in SOURCE_FILES:
        local = REPO / name
        need(local.is_file(), "Missing source: " + name)
        checksum = sha(local)
        read = subprocess.run(
            ["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO), "show", commit + ":" + name],
            capture_output=True, timeout=90,
        )
        need(read.returncode == 0 and digest(read.stdout) == checksum,
             "Productive source is not the frozen commit: " + name)
        result[name] = checksum
    return result


def fingerprint(raw: bytes) -> dict:
    matches = []
    for token in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw):
        end = raw.find(b"\0", token.start())
        if end < 0:
            continue
        try:
            value = json.loads(raw[token.start():end].decode("ascii"))
        except (UnicodeError, ValueError):
            continue
        if isinstance(value, dict) and "baseApkSha256" in value and "payloadSha256" in value:
            matches.append(value)
    need(len(matches) == 1, "Exactly one embedded runtime fingerprint required")
    value = matches[0]
    need(canonical(value) in raw and digest(canonical(value)).encode("ascii") in raw,
         "Embedded canonical fingerprint or hash changed")
    return value


def verify_dex_receipt(dex: Path, receipt_path: Path, original_dex: bytes) -> dict:
    proof = json.loads(receipt_path.read_text("utf-8"))
    patcher = load(HERE / "patch_dex.py", "r149_dex_patch")
    reproduced, expected = patcher.patch(original_dex)
    need(proof.get("schema") == "station.r149.dolphin-onpause-dex.v1" and
         proof.get("revision") == "R149" and proof.get("passed") is True and
         proof.get("sourceApkSha256") == BASE_SHA and
         proof.get("sourceDexSha256") == OLD_DEX_SHA and
         proof.get("outputDexSha256") == NEW_DEX_SHA == sha(dex) and
         proof.get("inverseExact") is True and
         proof.get("codeAndOtherDexBytesPreserved") is True and
         proof.get("changedByteOffsets") == expected["changedByteOffsets"] and
         proof.get("methodsBefore") == expected["methodsBefore"] and
         proof.get("methodsAfter") == expected["methodsAfter"] and
         proof.get("dispatchChainChildToParent") == expected["dispatchChainChildToParent"] and
         proof.get("intermediateDeclaresOnPause") is False and
         dex.read_bytes() == reproduced,
         "Exact two-flag DEX10 patch and independent replay required")
    return proof


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def build(args: argparse.Namespace) -> dict:
    base = args.base.resolve(strict=True)
    dex = args.dex.resolve(strict=True)
    need(base.stat().st_size == BASE_SIZE and sha(base) == BASE_SHA, "Exact signed R148 parent APK required")
    need(args.out.resolve().parent == args.build_root.resolve(strict=True) and not args.out.exists(),
         "Fresh R149 output directly under the chosen isolated build root required")
    source_files = frozen_source(args.source_commit)
    for name, checksum in IDENTITY_SOURCE_PINS.items():
        need(sha(REPO / name) == checksum, "Retained identity compiler changed: " + name)

    old_elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r149_elf")
    inherited_path = REPO / "integration/online-lifecycle-review-r135/recipe"
    inherited = load(inherited_path / "build_runtime_identity.py", "r149_identity", inherited_path)
    primitive = load(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r149_marker")
    inherited.verify_dependencies()
    tools = inherited.native_tools(args.ndk)

    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and REPLACED <= set(names) and
             {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} == DEX,
             "R148 entry inventory or 40 DEX partitions differ")
        before = {name: entry_sha(original, name) for name in names}
        need(before[CAROUSEL] == CAROUSEL_SHA and before[DEX_PARTITION] == OLD_DEX_SHA,
             "R148 carousel or DEX10 differs")
        carousel_contract = old_elf.elf_contract(original.read(CAROUSEL))
        need(carousel_contract["soname"] == ["libturbo_carousel.so"] and
             carousel_contract["minimumLoadAlignment"] >= 16384,
             "Preserved carousel ELF contract invalid")
        dex_receipt = verify_dex_receipt(dex, args.dex_receipt, original.read(DEX_PARTITION))
        previous = {kind: fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        old_payload = previous["psx"]["payloadSha256"]
        need(len(old_payload) == 345 and old_payload[CAROUSEL] == CAROUSEL_SHA and
             old_payload[DEX_PARTITION] == OLD_DEX_SHA and
             all(value["payloadSha256"] == old_payload and
                 value["productiveTransforms"] == previous["psx"]["productiveTransforms"]
                 for value in previous.values()), "Inherited 345 payload bindings differ")
        need(all(before.get(name) == checksum for name, checksum in old_payload.items()),
             "R148 payload does not match the bound owner fingerprints")
        updated_payload = {**old_payload, DEX_PARTITION: sha(dex)}
        transform = {"dolphin-onpause-r149/" + name: checksum for name, checksum in source_files.items()}
        need(not set(transform).intersection(previous["psx"]["productiveTransforms"]),
             "Source provenance would overwrite an inherited transform")
        transforms = {**previous["psx"]["productiveTransforms"], **transform}
        old_registry = json.loads(original.read(ENGINES))

    args.out.mkdir(parents=True)
    temp = args.out / "temp"
    temp.mkdir()
    env = {**os.environ, "TEMP": str(temp), "TMP": str(temp), "PYTHONDONTWRITEBYTECODE": "1"}
    markers = {}
    identities = {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE_SHA, payloadSha256=updated_payload, productiveTransforms=transforms)
    need(inherited.policy(psx) == inherited.policy(previous["psx"]), "PSX owner policy changed")
    raw = canonical(psx)
    source = args.out / "StationPsxIdentity.cpp"
    source.write_text(
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n',
        encoding="ascii",
    )
    psx_out = args.out / "native"
    command = [sys.executable, "-B", str(REPO / "integration/psx-online/recipe/build_entry.py"),
               "--ndk", str(args.ndk), "--owner", str(inherited.PSX / "native"),
               "--protocol", str(inherited.PSX / "native"),
               "--pinned-options", str(inherited.PSX / "native"),
               "--identity-source", str(source), "--out", str(psx_out)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=1800, env=env)
    (args.out / "psx-marker.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    need(result.returncode == 0, "Pinned PSX marker build failed")
    psx_binary = psx_out / WRAPPERS["psx"]
    need(raw in psx_binary.read_bytes(), "PSX wrapper lacks canonical fingerprint")
    markers["psx"] = {"runtimeLibrary": psx_binary.name, "runtimeSha256": sha(psx_binary),
                      "runtimeBytes": psx_binary.stat().st_size, "fingerprintSha256": digest(raw)}
    identities["psx"] = psx
    for kind, api in (("n64", "StationMupenRuntime"), ("dolphin", "StationDolphinRuntime")):
        value = copy.deepcopy(previous[kind])
        parent_binary = WRAPPERS[kind]
        value.update(baseApkSha256=BASE_SHA, payloadSha256=updated_payload,
                     productiveTransforms=transforms,
                     parentFingerprintSha256=digest(canonical(previous[kind])),
                     parentRuntimeSha256=before["lib/arm64-v8a/" + parent_binary],
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        need(inherited.policy(value) == inherited.policy(previous[kind]),
             "Retained " + kind + " owner policy changed")
        markers[kind] = primitive.marker(value, parent_binary, api, args.ndk, args.out)
        identities[kind] = value

    registry, selected = inherited.expected_engines(old_registry, markers)
    retro = [row for row in old_registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(old_registry["engines"]) == len(registry["engines"]) == 13 and len(retro) == 9 and
         [row for row in registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
         "RetroArch descriptors or unrelated platforms changed")
    engine_path = args.out / "engines.json"
    engine_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(engine_path.stat().st_size <= 32768, "Engine asset exceeds existing reader limit")
    replacements = {DEX_PARTITION: dex, ENGINES: engine_path,
                    **{"lib/arm64-v8a/" + name: psx_out / name if kind == "psx" else args.out / name
                       for kind, name in WRAPPERS.items()}}
    need(set(replacements) == REPLACED and
         all(fingerprint(path.read_bytes()) == identities[kind]
             for kind, name in WRAPPERS.items()
             for path in [replacements["lib/arm64-v8a/" + name]]),
         "Rebuilt wrapper fingerprint differs")
    with zipfile.ZipFile(base) as original:
        for kind, name in WRAPPERS.items():
            before_contract = old_elf.elf_contract(original.read("lib/arm64-v8a/" + name))
            after_contract = old_elf.elf_contract(replacements["lib/arm64-v8a/" + name].read_bytes())
            need(before_contract["exports"] == after_contract["exports"] and
                 before_contract["needed"] == after_contract["needed"] and
                 before_contract["soname"] == after_contract["soname"] == [name] and
                 after_contract["minimumLoadAlignment"] >= 16384,
                 "Rebuilt wrapper ABI changed: " + kind)
        expected = {**before, **{name: sha(path) for name, path in replacements.items()}}
        need({name for name in before if before[name] != expected[name]} == REPLACED,
             "Exactly five DEX/identity/registry entries must change")
        unsigned = args.out / "TurboStations-Premium-R149-dolphin-onpause-unsigned.apk"
        with zipfile.ZipFile(unsigned, "w", allowZip64=False) as destination:
            for item in original.infolist():
                with destination.open(copy.copy(item), "w", force_zip64=False) as target:
                    if item.filename in replacements:
                        with replacements[item.filename].open("rb") as stream:
                            shutil.copyfileobj(stream, target, 1024 * 1024)
                    else:
                        with original.open(item.filename) as stream:
                            shutil.copyfileobj(stream, target, 1024 * 1024)
    with zipfile.ZipFile(unsigned) as candidate:
        need(candidate.namelist() == names and
             {name: entry_sha(candidate, name) for name in names} == expected,
             "Full 13,860-entry unsigned readback failed")
    receipt = {
        "schema": "station.r149.dolphin-onpause.package.v1", "revision": "R149", "passed": True,
        "sourceCommit": args.source_commit, "sourceFilesSha256": source_files,
        "baselineApkSha256": BASE_SHA, "baselineApkBytes": BASE_SIZE,
        "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
        "dex10Sha256": sha(dex), "dexPatchReceiptSha256": sha(args.dex_receipt),
        "carouselSha256": CAROUSEL_SHA, "carouselContract": carousel_contract,
        "nativeToolFiles": tools,
        "replacedEntries": sorted(REPLACED), "preservedEntryCount": 13855,
        "entryCount": 13860, "expectedEntrySha256": expected,
        "changedDex": [DEX_PARTITION], "preservedDexPartitions": 39,
        "retainedOwnerPolicies": True, "preservedRetroArchDescriptors": 9,
        "dexPatchInverseExact": dex_receipt["inverseExact"],
        "preservedOtherDexCodeAndNativePayloads": True, "serverRegistered": False,
        "installed": False, "physicalGameplayValidated": False,
        "independentEngineIds": [row["engineId"] for row in selected],
        "runtimeMarkerSha256": {kind: row["runtimeSha256"] for kind, row in markers.items()},
        "payloadSha256": updated_payload,
    }
    write_json(args.out / "unsigned-package.json", receipt)
    return {"revision": "R149", "passed": True, "unsignedApkSha256": receipt["unsignedApkSha256"],
            "preservedEntryCount": 13855, "changedDex": 1}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "dex", "dex-receipt", "ndk", "out", "build-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    print(json.dumps(build(parser.parse_args()), ensure_ascii=False))


if __name__ == "__main__":
    main()
