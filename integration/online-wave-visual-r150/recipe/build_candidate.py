"""Assemble the R150 visual candidate from the exact signed R149 APK.

Only the carousel, three color DEX partitions, three bound runtime markers and
their registry may change. Signing and installation are separate operations.
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
REPO = HERE.parents[2]
BASE_SHA = "698e8a7914cc7be2facc00e6701ff1f3533fa13f763358b51578a35d25c2741e"
BASE_BYTES = 2_715_089_935
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_BASE_SHA = "313de078f8c300b6c7944de2ce03292de697532bc1a493b7406fdbb8260fbd28"
DEX_BASE = {"classes28.dex": "0f4e73bf6389d9d594c96f2e478d2c55fade7ea09ecccef124eba59ea2b91a3a",
            "classes35.dex": "dd9713ddace46aa902fe607a59ea13952afe374fed64f4200ab819537b9f8d2f",
            "classes40.dex": "216196f6c24095e4c51512a08782e56f6c3bc0444ce4f728308502c908489c4b"}
DEX_OUTPUT = {"classes28.dex": "a93a7257257cdd36841c6b8990b957a756ee3635f39a47881ba09c5b08d080bf",
              "classes35.dex": "ede5309d31dd44910d4e5b841604ab5fe3e1129ba693d7ee490ad0974047efbc",
              "classes40.dex": "e5f74abfb3ec7e182dacbf16db56a968c6fc62af8a098f16a729ffe2fe7bc282"}
ENGINES = "assets/station-online/engines.json"
WRAPPERS = {"psx": "libstation_psx_online.so", "n64": "libstation_mupen64plus_runtime.so",
            "dolphin": "libstation_dolphin_runtime.so"}
REPLACED = {CAROUSEL, ENGINES, *DEX_BASE,
            *("lib/arm64-v8a/" + name for name in WRAPPERS.values())}
SOURCE_FILES = (
    "integration/online-wave-visual-r150/recipe/build_candidate.py",
    "integration/online-wave-visual-r150/recipe/build_native.py",
    "integration/online-wave-visual-r150/recipe/prepare_snes_cover_overlay.py",
    "integration/online-wave-visual-r150/recipe/prepare_native_overlay.py",
    "integration/online-wave-visual-r150/recipe/patch_dex_binary.py",
)
PINNED_HELPERS = {
    "integration/dolphin-onpause-r149/recipe/build_candidate.py": "1c664a4bf28aaf2ac4582a05612bd52827a4795c9779af3224b3babe00e7f44d",
    "integration/online-lifecycle-review-r135/recipe/build_runtime_identity.py": "f1a1d8e3bd161bb6751801efc5a314e61b403f670822085dc92127dc63fe98da",
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
}


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def load(path: Path, name: str, imports: Path | None = None):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Pinned helper missing: " + str(path))
    module = importlib.util.module_from_spec(spec)
    previous = list(sys.path)
    try:
        if imports is not None:
            sys.path.insert(0, str(imports))
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = previous
    return module


def frozen_source(commit: str) -> dict[str, str]:
    need(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "Full committed R150 source required")
    result = {}
    for name in SOURCE_FILES:
        path = REPO / name
        checksum = sha(path)
        read = subprocess.run(["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO),
                               "show", commit + ":" + name], capture_output=True, timeout=90)
        need(read.returncode == 0 and digest(read.stdout) == checksum,
             "R150 source differs from frozen commit: " + name)
        result[name] = checksum
    return result


def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def build(args: argparse.Namespace) -> dict:
    base = args.base.resolve(strict=True)
    native = args.native.resolve(strict=True)
    dex_dir = args.dex_dir.resolve(strict=True)
    out = args.out.resolve()
    need(out.parent == args.build_root.resolve(strict=True) and not out.exists(),
         "Fresh R150 candidate output under the chosen build root required")
    need(base.stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
         "Exact signed R149 donor required")
    source_files = frozen_source(args.source_commit)
    for name, checksum in PINNED_HELPERS.items():
        need(sha(REPO / name) == checksum, "Identity helper changed: " + name)
    r149 = load(REPO / "integration/dolphin-onpause-r149/recipe/build_candidate.py", "r150_parent")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r150_elf")
    inherited_dir = REPO / "integration/online-lifecycle-review-r135/recipe"
    inherited = load(inherited_dir / "build_runtime_identity.py", "r150_identity", inherited_dir)
    primitive = load(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py",
                     "r150_marker")
    inherited.verify_dependencies()
    native_tools = inherited.native_tools(args.ndk)

    native_proof = json.loads((native.parent / "native-receipt.json").read_text("utf-8"))
    dex_proof = json.loads((dex_dir / "binary-dex-proof.json").read_text("utf-8"))
    need(native_proof.get("schema") == "station.r150.native.single-pass.v1" and
         native_proof.get("passed") is True and native_proof.get("r149Reproduced") is True and
         native_proof.get("snesLegacyAndMegaClassifiersSkipped") is True and
         native_proof.get("coverDrawCallsAddedPerFrame") == 0 and
         native_proof.get("outputNativeSha256") == sha(native) != CAROUSEL_BASE_SHA,
         "Exact single-pass R150 native result required")
    need(dex_proof.get("schema") == "station.r150.visual.binary-dex.v1" and
         dex_proof.get("passed") is True and dex_proof.get("baseApkSha256") == BASE_SHA and
         dex_proof.get("inverseByteExact") is True and
         dex_proof.get("dexlib2InstructionBoundariesVerified") is True and
         dex_proof.get("changedDex") == sorted(DEX_BASE) and
         all(dex_proof["partitionProofs"][name]["sourceSha256"] == DEX_BASE[name] and
             dex_proof["partitionProofs"][name]["outputSha256"] == DEX_OUTPUT[name] == sha(dex_dir / name)
             for name in DEX_BASE), "Exact scoped R150 DEX proof required")

    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and REPLACED <= set(names) and
             {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} ==
             {"classes.dex", *(f"classes{i}.dex" for i in range(2, 41))},
             "R149 entry inventory differs")
        before = {name: entry_sha(original, name) for name in names}
        need(before[CAROUSEL] == CAROUSEL_BASE_SHA and
             all(before[name] == checksum for name, checksum in DEX_BASE.items()) and
             before["classes10.dex"] == "1f1b285af161fbf85573c081bee3bc6e4c95f90485d8d405ae064b86feb9144e",
             "R149 visual or gameplay payload differs")
        old_abi, new_abi = elf.elf_contract(original.read(CAROUSEL)), elf.elf_contract(native.read_bytes())
        need(old_abi["exports"] == new_abi["exports"] and
             old_abi["needed"] == new_abi["needed"] and
             old_abi["soname"] == new_abi["soname"] == ["libturbo_carousel.so"] and
             new_abi["minimumLoadAlignment"] >= 16384, "R150 carousel ABI changed")
        previous = {kind: r149.fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        old_payload = previous["psx"]["payloadSha256"]
        need(len(old_payload) == 345 and old_payload[CAROUSEL] == CAROUSEL_BASE_SHA and
             all(old_payload[name] == checksum for name, checksum in DEX_BASE.items()) and
             all(value["payloadSha256"] == old_payload and
                 value["productiveTransforms"] == previous["psx"]["productiveTransforms"]
                 for value in previous.values()) and
             all(before.get(name) == checksum for name, checksum in old_payload.items()),
             "R149 independent runtime bindings differ")
        payload = {**old_payload, CAROUSEL: sha(native),
                   **{name: sha(dex_dir / name) for name in DEX_BASE}}
        transform = {"online-wave-visual-r150/" + name: checksum for name, checksum in source_files.items()}
        need(not set(transform).intersection(previous["psx"]["productiveTransforms"]),
             "R150 transform would overwrite history")
        transforms = {**previous["psx"]["productiveTransforms"], **transform}
        old_registry = json.loads(original.read(ENGINES))

    out.mkdir(parents=True)
    temp = out / "temp"
    temp.mkdir()
    env = {**os.environ, "TEMP": str(temp), "TMP": str(temp), "PYTHONDONTWRITEBYTECODE": "1"}
    markers, identities = {}, {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE_SHA, payloadSha256=payload, productiveTransforms=transforms)
    need(inherited.policy(psx) == inherited.policy(previous["psx"]), "PSX owner policy changed")
    raw = canonical(psx)
    source = out / "StationPsxIdentity.cpp"
    source.write_text(
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n',
        encoding="ascii")
    psx_out = out / "native"
    command = [sys.executable, "-B", str(REPO / "integration/psx-online/recipe/build_entry.py"),
               "--ndk", str(args.ndk), "--owner", str(inherited.PSX / "native"),
               "--protocol", str(inherited.PSX / "native"), "--pinned-options", str(inherited.PSX / "native"),
               "--identity-source", str(source), "--out", str(psx_out)]
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=1800, env=env)
    (out / "psx-marker.log").write_text(compiled.stdout + compiled.stderr, encoding="utf-8")
    need(compiled.returncode == 0, "Pinned PSX marker build failed")
    psx_binary = psx_out / WRAPPERS["psx"]
    need(raw in psx_binary.read_bytes(), "PSX marker lacks the R150 fingerprint")
    markers["psx"] = {"runtimeLibrary": psx_binary.name, "runtimeSha256": sha(psx_binary),
                      "runtimeBytes": psx_binary.stat().st_size, "fingerprintSha256": digest(raw)}
    identities["psx"] = psx
    for kind, api in (("n64", "StationMupenRuntime"), ("dolphin", "StationDolphinRuntime")):
        value = copy.deepcopy(previous[kind])
        parent_binary = WRAPPERS[kind]
        value.update(baseApkSha256=BASE_SHA, payloadSha256=payload, productiveTransforms=transforms,
                     parentFingerprintSha256=digest(canonical(previous[kind])),
                     parentRuntimeSha256=before["lib/arm64-v8a/" + parent_binary],
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        need(inherited.policy(value) == inherited.policy(previous[kind]),
             "Retained owner policy changed: " + kind)
        markers[kind] = primitive.marker(value, parent_binary, api, args.ndk, out)
        identities[kind] = value
    registry, selected = inherited.expected_engines(old_registry, markers)
    retro = [row for row in old_registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(old_registry["engines"]) == len(registry["engines"]) == 13 and len(retro) == 9 and
         [row for row in registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
         "Unrelated engine descriptors changed")
    engine_path = out / "engines.json"
    engine_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(engine_path.stat().st_size <= 32768, "Engine asset exceeds existing reader limit")
    replacements = {CAROUSEL: native, ENGINES: engine_path,
                    **{name: dex_dir / name for name in DEX_BASE},
                    **{"lib/arm64-v8a/" + name:
                       psx_out / name if kind == "psx" else out / name
                       for kind, name in WRAPPERS.items()}}
    need(set(replacements) == REPLACED and
         all(r149.fingerprint(replacements["lib/arm64-v8a/" + name].read_bytes()) == identities[kind]
             for kind, name in WRAPPERS.items()), "Rebuilt marker fingerprint differs")
    with zipfile.ZipFile(base) as original:
        for kind, name in WRAPPERS.items():
            path = "lib/arm64-v8a/" + name
            old_contract = elf.elf_contract(original.read(path))
            new_contract = elf.elf_contract(replacements[path].read_bytes())
            need(old_contract["exports"] == new_contract["exports"] and
                 old_contract["needed"] == new_contract["needed"] and
                 old_contract["soname"] == new_contract["soname"] == [name] and
                 new_contract["minimumLoadAlignment"] >= 16384,
                 "Marker ABI changed: " + kind)
        expected = {**before, **{name: sha(path) for name, path in replacements.items()}}
        need({name for name in before if before[name] != expected[name]} == REPLACED,
             "Exactly eight R150 visual/identity entries must change")
        unsigned = out / "TurboStations-Premium-R150-visual-unsigned.apk"
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
    receipt = {"schema": "station.r150.visual.package.v1", "revision": "R150", "passed": True,
               "sourceCommit": args.source_commit, "sourceFilesSha256": source_files,
               "baselineApkSha256": BASE_SHA, "baselineApkBytes": BASE_BYTES,
               "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
               "nativeReceiptSha256": sha(native.parent / "native-receipt.json"),
               "dexReceiptSha256": sha(dex_dir / "binary-dex-proof.json"),
               "replacedEntries": sorted(REPLACED), "preservedEntryCount": 13852,
               "entryCount": 13860, "expectedEntrySha256": expected,
               "changedDex": sorted(DEX_BASE), "preservedDexPartitions": 37,
               "retainedOwnerPolicies": True, "preservedRetroArchDescriptors": 9,
               "snesCoverSinglePass": True, "coverDrawCallsAddedPerFrame": 0,
               "newTimersThreadsHeapAllocations": 0, "serverRegistered": False,
               "installed": False, "physicalGameplayValidated": False,
               "independentEngineIds": [row["engineId"] for row in selected],
               "runtimeMarkerSha256": {kind: row["runtimeSha256"] for kind, row in markers.items()},
               "payloadSha256": payload, "nativeToolFiles": native_tools}
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return {"revision": "R150", "passed": True, "preservedEntryCount": 13852,
            "unsignedApkSha256": receipt["unsignedApkSha256"]}


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "native", "dex-dir", "ndk", "out", "build-root"):
        cli.add_argument("--" + name, type=Path, required=True)
    cli.add_argument("--source-commit", required=True)
    print(json.dumps(build(cli.parse_args()), ensure_ascii=False))


if __name__ == "__main__":
    main()
