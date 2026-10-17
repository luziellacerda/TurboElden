"""Package an isolated N64 online Dynarec candidate from exact signed R159.

Only classes35.dex, three bound runtime identities and the engine registry
may change. DEX36, carousel, native cores and media stay byte-identical.
Signing, server registration and installation are separate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


sys.dont_write_bytecode = True
zipfile.ZIP64_LIMIT = (1 << 32) - 1
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE_SHA = "4837be706f9ac1f913b4844353741f70c539674e125ae185239611cf5faac2b3"
BASE_BYTES = 2_715_106_319
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_BASE_SHA = "7d2f2be22083c3fb2a27df9fd43c3b92cf63bc74f87e1f64955753910b00c025"
FRONTEND = "lib/arm64-v8a/libstation_frontend.so"
FRONTEND_SHA = "438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d"
DEXES = {
    "classes35.dex": "59367f469277ef94b7b31cc2e2e7d0ab3b5ab0f102b41a8c2a95a05a6eb50e05",
}
DEX36_SHA = "6e0f7116d156518fad1e65e72f4c204cfacfd9904c4ee2c3110395d56842d707"
ENGINES = "assets/station-online/engines.json"
ENGINES_SHA = "ba1b5306842559a4fe741eab16055c1f438d3a470b2bb04474a0e15d8d4260fe"
WRAPPERS = {"psx": "libstation_psx_online.so", "n64": "libstation_mupen64plus_runtime.so",
            "dolphin": "libstation_dolphin_runtime.so"}
WRAPPER_SHA = {
    "psx": "7d5350589348901976ba7e524295555d18830b323a1b2f22e718982e71b9aaa4",
    "n64": "7d50f27b470278726f2b1f0744838f068e8fcbba67b4f6606bd5334fb7bbd524",
    "dolphin": "008698beba99089faacc232322c2edaa541961e5d8f85cb37e7a5bc99254bd4a",
}
REPLACED = {*DEXES, ENGINES, *("lib/arm64-v8a/" + name for name in WRAPPERS.values())}
SOURCE_FILES = (
    "integration/n64-online-dynarec-r161/recipe/patch_profile.py",
    "integration/n64-online-dynarec-r161/recipe/build_dex.py",
    "integration/n64-online-dynarec-r161/packaging/build_candidate.py",
    "integration/n64-online-dynarec-r161/packaging/sign_private.py",
)
CPU_OLD = "cpu=cached-interpreter\n"
CPU_NEW = "cpu=dynarec\n"


def dynarec_options(options: str) -> str:
    need(options.count(CPU_OLD) == 1 and CPU_NEW not in options,
         "Pinned R159 N64 CPU option differs")
    return options.replace(CPU_OLD, CPU_NEW, 1)


def need(condition: bool, message: str) -> None:
    if not condition:
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


def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_dex_proof(dex_dir: Path) -> tuple[dict[str, Path], dict[str, str], str]:
    receipt_path = dex_dir / "dex-receipt.json"
    need(receipt_path.is_file(), "Scoped R161 Dynarec DEX receipt required")
    proof = json.loads(receipt_path.read_text("utf-8"))
    partitions = proof.get("partitions")
    need(proof.get("schema") == "station.n64.online-dynarec.r161.v1" and
         proof.get("passed") is True and proof.get("donorApkSha256") == BASE_SHA and
         isinstance(partitions, dict) and set(partitions) == set(DEXES) and
         all(proof.get(key) is False for key in ("newThreadsOrPolling", "offlineGateBroadened",
                 "serviceOwnerValidationRelaxed", "taskRemovalChanged", "inputDelayChanged",
                 "apkBuilt", "phoneInstalled", "gameplayValidated")),
         "Scoped N64 Dynarec proof differs")
    owners = {"Lorg/emulationstation/frontend/netplay/StationN64Bridge$Session;",
              "Lorg/emulationstation/frontend/netplay/StationN64Launch;",
              "Lorg/emulationstation/frontend/netplay/StationN64Server;"}
    paths: dict[str, Path] = {}
    candidate_hashes: dict[str, str] = {}
    for name, donor_hash in DEXES.items():
        row = partitions[name]
        path = dex_dir / ("candidate-" + name)
        count = row.get("classCount")
        candidate_hash = row.get("candidateDexSha256")
        need(path.is_file() and row.get("donorDexSha256") == donor_hash and
             set(row.get("owners", [])) == owners and isinstance(count, int) and count > 3 and
             row.get("unrelatedClassesUnchanged") == count - 3 and
             isinstance(candidate_hash, str) and len(candidate_hash) == 64 and
             sha(path) == candidate_hash and candidate_hash != donor_hash,
             "Scoped R161 Dynarec DEX differs: " + name)
        paths[name], candidate_hashes[name] = path, candidate_hash
    return paths, candidate_hashes, sha(receipt_path)


def build(base: Path, dex_dir: Path, ndk: Path, out: Path) -> dict:
    if out.exists():
        raise FileExistsError(out)
    need(base.stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
         "Exact signed R159 donor required")
    source_files = {name: sha(REPO / name) for name in SOURCE_FILES}
    dex_paths, candidate_hashes, dex_receipt_sha = verify_dex_proof(dex_dir)
    r149 = load(REPO / "integration/dolphin-onpause-r149/recipe/build_candidate.py", "r161_r149")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r161_elf")
    inherited_dir = REPO / "integration/online-lifecycle-review-r135/recipe"
    inherited = load(inherited_dir / "build_runtime_identity.py", "r161_identity", inherited_dir)
    primitive = load(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r161_marker")
    inherited.verify_dependencies()
    native_tools = inherited.native_tools(ndk)
    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and REPLACED <= set(names) and
             {name for name in names if name.endswith(".dex") and name.startswith("classes")} ==
             {"classes.dex", *(f"classes{i}.dex" for i in range(2, 41))},
             "R159 archive entry list changed")
        before = {name: entry_sha(original, name) for name in names}
        need(before[CAROUSEL] == CAROUSEL_BASE_SHA and before[FRONTEND] == FRONTEND_SHA and
             before["classes36.dex"] == DEX36_SHA and
             all(before[name] == checksum for name, checksum in DEXES.items()) and
             before[ENGINES] == ENGINES_SHA and
             all(before["lib/arm64-v8a/" + name] == WRAPPER_SHA[kind]
                 for kind, name in WRAPPERS.items()),
             "R159 visual, room or runtime payload differs")
        previous = {kind: r149.fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        old_payload = previous["psx"]["payloadSha256"]
        need(len(old_payload) == 345 and old_payload[CAROUSEL] == CAROUSEL_BASE_SHA and
             old_payload[FRONTEND] == FRONTEND_SHA and
             old_payload["classes36.dex"] == DEX36_SHA and
             all(old_payload[name] == checksum for name, checksum in DEXES.items()) and
             all(old_payload == value["payloadSha256"] and
                 previous["psx"]["productiveTransforms"] == value["productiveTransforms"]
                 for value in previous.values()) and
             all(before.get(name) == checksum for name, checksum in old_payload.items()),
             "R159 independent runtime identity bindings differ")
        old_registry = json.loads(original.read(ENGINES))
    original_n64 = next(row for row in old_registry["engines"] if row["platform"] == "n64")
    need(previous["n64"]["options"] == original_n64["options"],
         "R159 N64 registry and runtime options disagree")
    n64_options = dynarec_options(original_n64["options"])
    payload = {**old_payload, **candidate_hashes}
    transforms = {**previous["psx"]["productiveTransforms"],
                  **{"n64-online-dynarec-r161/" + name: checksum for name, checksum in source_files.items()}}
    need(len(transforms) == len(previous["psx"]["productiveTransforms"]) + len(source_files),
         "R161 source history collides with an earlier transform")
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
               "--ndk", str(ndk), "--owner", str(inherited.PSX / "native"),
               "--protocol", str(inherited.PSX / "native"),
               "--pinned-options", str(inherited.PSX / "native"),
               "--identity-source", str(source), "--out", str(psx_out)]
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=1800, env=env)
    (out / "psx-marker.log").write_text(compiled.stdout + compiled.stderr, encoding="utf-8")
    need(compiled.returncode == 0, "Pinned PSX marker build failed")
    psx_binary = psx_out / WRAPPERS["psx"]
    need(raw in psx_binary.read_bytes(), "PSX marker lacks the R161 fingerprint")
    markers["psx"] = {"runtimeLibrary": psx_binary.name, "runtimeSha256": sha(psx_binary),
                      "runtimeBytes": psx_binary.stat().st_size, "fingerprintSha256": digest(raw)}
    identities["psx"] = psx
    for kind, api in (("n64", "StationMupenRuntime"), ("dolphin", "StationDolphinRuntime")):
        value = copy.deepcopy(previous[kind])
        name = WRAPPERS[kind]
        value.update(baseApkSha256=BASE_SHA, payloadSha256=payload, productiveTransforms=transforms,
                     parentFingerprintSha256=digest(canonical(previous[kind])),
                     parentRuntimeSha256=before["lib/arm64-v8a/" + name],
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        expected_policy = inherited.policy(previous[kind])
        if kind == "n64":
            value["options"] = n64_options
            expected_policy["options"] = n64_options
        need(inherited.policy(value) == expected_policy,
             "Unrequested owner policy changed: " + kind)
        markers[kind] = primitive.marker(value, name, api, ndk, out)
        identities[kind] = value
    target_registry = copy.deepcopy(old_registry)
    next(row for row in target_registry["engines"] if row["platform"] == "n64")["options"] = n64_options
    registry, selected = inherited.expected_engines(target_registry, markers)
    retro = [row for row in old_registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(old_registry["engines"]) == len(registry["engines"]) == 13 and len(retro) == 9 and
         [row for row in registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
         "Unrelated engine descriptors changed")
    old_selected = {row["platform"]: row for row in old_registry["engines"]
                    if row["platform"] in {"psx", "n64", "gamecube", "wii"}}
    new_selected = {row["platform"]: row for row in selected}
    need(len(old_selected) == len(new_selected) == 4 and set(old_selected) == set(new_selected) and
         len({name for row in old_selected.values() for name in row["dependencySha256"]}) == 20 and
         all({key: value for key, value in old_selected[platform].items()
              if key not in {"engineId", "runtimeSha256", "options"}} ==
             {key: value for key, value in new_selected[platform].items()
              if key not in {"engineId", "runtimeSha256", "options"}}
             for platform in old_selected) and
         all(old_selected[platform]["options"] == new_selected[platform]["options"]
             for platform in old_selected if platform != "n64") and
         new_selected["n64"]["options"] == n64_options,
         "Core, dependency, player, profile or owner policies changed")
    engine_path = out / "engines.json"
    engine_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(engine_path.stat().st_size <= 32768, "Engine registry exceeds reader limit")
    replacements = {**dex_paths, ENGINES: engine_path,
                    **{"lib/arm64-v8a/" + name: psx_out / name if kind == "psx" else out / name
                       for kind, name in WRAPPERS.items()}}
    need(set(replacements) == REPLACED and
         all(r149.fingerprint(replacements["lib/arm64-v8a/" + name].read_bytes()) == identities[kind]
             for kind, name in WRAPPERS.items()), "Rebuilt marker fingerprint differs")
    with zipfile.ZipFile(base) as original:
        for kind, name in WRAPPERS.items():
            path = "lib/arm64-v8a/" + name
            old_abi = elf.elf_contract(original.read(path))
            new_abi = elf.elf_contract(replacements[path].read_bytes())
            need(old_abi["exports"] == new_abi["exports"] and
                 old_abi["needed"] == new_abi["needed"] and
                 old_abi["soname"] == new_abi["soname"] == [name] and
                 new_abi["minimumLoadAlignment"] >= 16384,
                 "Marker ABI changed: " + kind)
        expected = {**before, **{name: sha(path) for name, path in replacements.items()}}
        need({name for name in before if before[name] != expected[name]} == REPLACED,
             "Exactly five R161 entries must change")
        unsigned = out / "TurboStations-Premium-R161-n64-online-dynarec-unsigned.apk"
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
    receipt = {"schema": "station.r161.n64-online-dynarec.package.v1", "revision": "R161",
               "passed": True, "baselineApkSha256": BASE_SHA,
               "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
               "sourceFilesSha256": source_files, "replacedEntries": sorted(REPLACED),
               "preservedEntryCount": 13855, "entryCount": 13860,
               "expectedEntrySha256": expected, "preservedDexPartitions": 39,
               "changedDexPartitions": sorted(DEXES), "dexReceiptSha256": dex_receipt_sha,
               "dexSha256": candidate_hashes, "donorDexSha256": DEXES,
               "carouselSha256Preserved": CAROUSEL_BASE_SHA,
               "retainedOwnerPolicies": True, "preservedRetroArchDescriptors": 9,
               "preservedIndependentDependencies": 20,
               "visualCarouselAndOtherEmulatorsPreserved": True,
               "nativeToolFiles": native_tools,
               "n64OnlineOptions": n64_options,
               "offlineProfileChanged": False, "inputDelayChanged": False,
               "taskRemovalChanged": False,
               "serverRegistered": False, "signed": False, "installed": False}
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return {"revision": "R161", "passed": True, "preservedEntryCount": 13855,
            "unsignedApkSha256": receipt["unsignedApkSha256"]}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "dex-dir", "ndk", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.base.resolve(), args.dex_dir.resolve(),
                           args.ndk.resolve(), args.out.resolve()), ensure_ascii=False))
