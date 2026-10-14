"""Package the scoped N64 owner propagation fix from exact signed R158 v8.

Only classes35.dex, three bound runtime identities and the engine registry
may change. The carousel, other DEX partitions, native cores and media are
preserved byte for byte. Signing and installation are separate.
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
BASE_SHA = "fc1d2d983deb5179979a4aebac7fa64b1740da1c62ae46bfc0d1f4c11eb46cf0"
BASE_BYTES = 2_715_106_319
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_BASE_SHA = "7d2f2be22083c3fb2a27df9fd43c3b92cf63bc74f87e1f64955753910b00c025"
FRONTEND = "lib/arm64-v8a/libstation_frontend.so"
FRONTEND_SHA = "438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d"
DEX = "classes35.dex"
DEX35_SHA = "e2cbccdb9af8dbeb1485c7119312875aece8660956833d22ee042b5b5306b513"
ENGINES = "assets/station-online/engines.json"
ENGINES_SHA = "77de9ff0a09ff87a5763b0b924229aefac75512fb173f2b398ba4cd31d22f887"
WRAPPERS = {"psx": "libstation_psx_online.so", "n64": "libstation_mupen64plus_runtime.so",
            "dolphin": "libstation_dolphin_runtime.so"}
WRAPPER_SHA = {
    "psx": "25f26a587ea3a84eb336d26a33fe71eff02508ff964c6268c2e902bf1c8ed94b",
    "n64": "0702412628d22ffa7c4c02c1f0708aa7b4d6f827a854ec2b2f9b1592d51f9f61",
    "dolphin": "91be6a0d00e213996bde57eb11fdcef3626735ce1af4c5f27e97a710ed4ef7c0",
}
DEX_CANDIDATE_SHA = "59367f469277ef94b7b31cc2e2e7d0ab3b5ab0f102b41a8c2a95a05a6eb50e05"
DEX_RECEIPT_SHA = "8a0ab78ac4ba0cb3461d9a45e8042589a9c0ed296b8f3615644db65f7aa924aa"
REPLACED = {DEX, ENGINES, *("lib/arm64-v8a/" + name for name in WRAPPERS.values())}
SOURCE_FILES = (
    "integration/n64-owner-application-context-r159/recipe/StationN64Bridge.java",
    "integration/n64-owner-application-context-r159/recipe/patch_smali.py",
    "integration/n64-owner-application-context-r159/recipe/build_dex.py",
    "integration/n64-owner-application-context-r159/packaging/build_candidate.py",
    "integration/n64-owner-application-context-r159/packaging/sign_private.py",
)


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


def verify_dex_proof(dex: Path, receipt_path: Path) -> dict:
    need(dex.name == "candidate-classes35.dex" and receipt_path.name == "dex-receipt.json" and
         dex.parent == receipt_path.parent and sha(dex) == DEX_CANDIDATE_SHA and
         sha(receipt_path) == DEX_RECEIPT_SHA, "Exact reviewed R159 DEX and receipt required")
    proof = json.loads(receipt_path.read_text("utf-8"))
    need(proof.get("schema") == "station.n64.owner-application-context.r159.v2" and
         proof.get("passed") is True and proof.get("donorApkSha256") == BASE_SHA and
         proof.get("partition") == DEX and proof.get("donorDexSha256") == DEX35_SHA and
         proof.get("candidateDexSha256") == DEX_CANDIDATE_SHA and
         proof.get("owner") == "Lorg/emulationstation/frontend/netplay/StationN64Bridge;" and
         proof.get("classCount") == 608 and proof.get("unrelatedClassesUnchanged") == 607 and
         all(proof.get(key) is False for key in ("newThreadsOrPolling", "offlineGateBroadened",
                 "serviceOwnerValidationRelaxed", "apkBuilt", "phoneInstalled", "gameplayValidated")),
         "Scoped N64 owner proof differs")
    return proof


def build(base: Path, dex: Path, dex_receipt: Path, ndk: Path, out: Path) -> dict:
    if out.exists():
        raise FileExistsError(out)
    need(base.stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
         "Exact signed R158 v8 donor required")
    source_files = {name: sha(REPO / name) for name in SOURCE_FILES}
    verify_dex_proof(dex, dex_receipt)
    r149 = load(REPO / "integration/dolphin-onpause-r149/recipe/build_candidate.py", "r159_r149")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r159_elf")
    inherited_dir = REPO / "integration/online-lifecycle-review-r135/recipe"
    inherited = load(inherited_dir / "build_runtime_identity.py", "r159_identity", inherited_dir)
    primitive = load(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r159_marker")
    inherited.verify_dependencies()
    native_tools = inherited.native_tools(ndk)
    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and REPLACED <= set(names) and
             {name for name in names if name.endswith(".dex") and name.startswith("classes")} ==
             {"classes.dex", *(f"classes{i}.dex" for i in range(2, 41))},
             "R158 v8 archive entry list changed")
        before = {name: entry_sha(original, name) for name in names}
        need(before[CAROUSEL] == CAROUSEL_BASE_SHA and before[FRONTEND] == FRONTEND_SHA and
             before[DEX] == DEX35_SHA and before[ENGINES] == ENGINES_SHA and
             all(before["lib/arm64-v8a/" + name] == WRAPPER_SHA[kind]
                 for kind, name in WRAPPERS.items()),
             "R158 v8 visual, room or runtime payload differs")
        previous = {kind: r149.fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        old_payload = previous["psx"]["payloadSha256"]
        need(len(old_payload) == 345 and old_payload[CAROUSEL] == CAROUSEL_BASE_SHA and
             old_payload[FRONTEND] == FRONTEND_SHA and old_payload[DEX] == DEX35_SHA and
             all(old_payload == value["payloadSha256"] and
                 previous["psx"]["productiveTransforms"] == value["productiveTransforms"]
                 for value in previous.values()) and
             all(before.get(name) == checksum for name, checksum in old_payload.items()),
             "R158 v8 independent runtime identity bindings differ")
        old_registry = json.loads(original.read(ENGINES))
    payload = {**old_payload, DEX: DEX_CANDIDATE_SHA}
    transforms = {**previous["psx"]["productiveTransforms"],
                  **{"n64-owner-application-context-r159/" + name: checksum for name, checksum in source_files.items()}}
    need(len(transforms) == len(previous["psx"]["productiveTransforms"]) + len(source_files),
         "R159 source history collides with an earlier transform")
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
    need(raw in psx_binary.read_bytes(), "PSX marker lacks the R159 fingerprint")
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
        need(inherited.policy(value) == inherited.policy(previous[kind]),
             "Retained owner policy changed: " + kind)
        markers[kind] = primitive.marker(value, name, api, ndk, out)
        identities[kind] = value
    registry, selected = inherited.expected_engines(old_registry, markers)
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
              if key not in {"engineId", "runtimeSha256"}} ==
             {key: value for key, value in new_selected[platform].items()
              if key not in {"engineId", "runtimeSha256"}}
             for platform in old_selected),
         "Core, dependency, player, profile or owner policies changed")
    engine_path = out / "engines.json"
    engine_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(engine_path.stat().st_size <= 32768, "Engine registry exceeds reader limit")
    replacements = {DEX: dex, ENGINES: engine_path,
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
             "Exactly five R159 entries must change")
        unsigned = out / "TurboStations-Premium-R159-n64-owner-unsigned.apk"
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
    receipt = {"schema": "station.r159.n64-owner.package.v1", "revision": "R159",
               "passed": True, "baselineApkSha256": BASE_SHA,
               "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
               "sourceFilesSha256": source_files, "replacedEntries": sorted(REPLACED),
               "preservedEntryCount": 13855, "entryCount": 13860,
               "expectedEntrySha256": expected, "preservedDexPartitions": 39,
               "changedDexPartitions": [DEX], "dexReceiptSha256": DEX_RECEIPT_SHA,
               "dexSha256": DEX_CANDIDATE_SHA, "donorDexSha256": DEX35_SHA,
               "carouselSha256Preserved": CAROUSEL_BASE_SHA,
               "retainedOwnerPolicies": True, "preservedRetroArchDescriptors": 9,
               "preservedIndependentDependencies": 20,
               "visualCarouselAndOtherEmulatorsPreserved": True,
               "nativeToolFiles": native_tools,
               "serverRegistered": False, "installed": False}
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return {"revision": "R159", "passed": True, "preservedEntryCount": 13855,
            "unsignedApkSha256": receipt["unsignedApkSha256"]}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "dex", "dex-receipt", "ndk", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.base.resolve(), args.dex.resolve(), args.dex_receipt.resolve(),
                           args.ndk.resolve(), args.out.resolve()), ensure_ascii=False))
