"""Package only the reviewed R163 carousel and its bound engine identities.

The donor is the exact signed R162 APK.  The online VideoExt DEX partitions,
the AE bridge, every emulator core and all other APK entries are copied without
changing their contents.  Signing and installation are separate steps.
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
BASE_SHA = "7ec742c4cae7b663f2198e347253986b4c4c5d0d0461052dd75df56ca6335dd7"
BASE_BYTES = 2_715_466_850
ENTRY_COUNT = 13_861
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_BASE_SHA = "7d2f2be22083c3fb2a27df9fd43c3b92cf63bc74f87e1f64955753910b00c025"
FRONTEND = "lib/arm64-v8a/libstation_frontend.so"
FRONTEND_SHA = "438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d"
DEX = {
    "classes35.dex": "0489cd99a51d43d001cab4ef5374e03aea694b58f6cc72648e7217f363d79b52",
    "classes36.dex": "a1c12b34c5eba4060707235c86dea3bbdfa59ef52264afc7ebaaa5d73231287c",
}
ONLINE_BRIDGE = "lib/arm64-v8a/libstation_ae_bridge.so"
ONLINE_BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
OFFLINE_BRIDGE = "lib/arm64-v8a/libae-bridge.so"
OFFLINE_BRIDGE_SHA = "ba5a7582295215f159e197f805dbfe85851aa912462996870f61ccd752ecb360"
ENGINES = "assets/station-online/engines.json"
ENGINES_SHA = "d4bdb3350512dd80e72a1e027196bc502392b09bc3ea8449dd7fce230283f8fe"
WRAPPERS = {
    "psx": "libstation_psx_online.so",
    "n64": "libstation_mupen64plus_runtime.so",
    "dolphin": "libstation_dolphin_runtime.so",
}
WRAPPER_SHA = {
    "psx": "bf682d6798e74cb46cd221ecceb10475e4f7fb2d11e1da45a84e2f25ac7ad4ab",
    "n64": "57155617f470e39144ba050169bdf5801f0392f62995a95d0116a4497ce0fd1e",
    "dolphin": "3bfbe6be43a7c507a381b4d5ef9a0f7571737031453eb7254835687199972796",
}
REPLACED = {CAROUSEL, ENGINES, *("lib/arm64-v8a/" + name for name in WRAPPERS.values())}
SOURCE_FILES = (
    "integration/game-selection-n64-cover-r163/recipe/patch_layout.py",
    "integration/game-selection-n64-cover-r163/recipe/patch_n64_cover.py",
    "integration/game-selection-n64-cover-r163/recipe/build_native.py",
    "integration/game-selection-n64-cover-r163/recipe/package_candidate.py",
    "integration/game-selection-n64-cover-r163/recipe/sign_private.py",
)


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
    need(spec is not None and spec.loader is not None, "Pinned identity helper missing: " + str(path))
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


def verify_native(native: Path) -> dict:
    proof = json.loads((native.parent / "native-receipt.json").read_text("utf-8"))
    need(proof.get("schema") == "station.r163.selection-n64-cover.native.v1" and
         proof.get("passed") is True and
         proof.get("sourceLibrarySha256") == CAROUSEL_BASE_SHA and
         proof.get("outputSha256") == sha(native) and
         proof.get("outputSha256") != CAROUSEL_BASE_SHA and
         proof.get("abiPreserved") is True and
         proof.get("compilerWarningsUnchanged") is True and
         proof.get("extraPerFrameDrawCalls") == 0 and
         proof.get("newTimersThreadsHeapAllocations") == 0 and
         isinstance(proof.get("layout"), dict) and
         proof["layout"].get("actionsPreserved") == [0, 1, 2, 3, 4, 5] and
         proof["layout"].get("newTimersThreadsWorkers") == 0 and
         isinstance(proof.get("cover"), dict) and
         proof["cover"].get("referenceDimensions") == [1024, 1536] and
         proof["cover"].get("newThreadsTimersPerFrameDraws") == 0 and
         proof["cover"].get("oldN64ArtworkProfilePreserved") is True,
         "Reviewed R163 native receipt required")
    return proof


def build(base: Path, native: Path, ndk: Path, out: Path) -> dict:
    if out.exists():
        raise FileExistsError(out)
    need(base.stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
         "Exact signed R162 donor required")
    native_proof = verify_native(native)
    source_files = {name: sha(REPO / name) for name in SOURCE_FILES}
    r149 = load(REPO / "integration/dolphin-onpause-r149/recipe/build_candidate.py", "r163_r149")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r163_elf")
    inherited_dir = REPO / "integration/online-lifecycle-review-r135/recipe"
    inherited = load(inherited_dir / "build_runtime_identity.py", "r163_identity", inherited_dir)
    primitive = load(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py",
                     "r163_marker")
    inherited.verify_dependencies()
    native_tools = inherited.native_tools(ndk)
    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == ENTRY_COUNT and REPLACED <= set(names) and
             {name for name in names if name.endswith(".dex") and name.startswith("classes")} ==
             {"classes.dex", *(f"classes{i}.dex" for i in range(2, 41))},
             "R162 archive entry set changed")
        before = {name: entry_sha(original, name) for name in names}
        need(before[CAROUSEL] == CAROUSEL_BASE_SHA and
             before[FRONTEND] == FRONTEND_SHA and
             before[ONLINE_BRIDGE] == ONLINE_BRIDGE_SHA and
             before[OFFLINE_BRIDGE] == OFFLINE_BRIDGE_SHA and
             all(before[name] == checksum for name, checksum in DEX.items()) and
             before[ENGINES] == ENGINES_SHA and
             all(before["lib/arm64-v8a/" + name] == WRAPPER_SHA[kind]
                 for kind, name in WRAPPERS.items()),
             "R162 online bridge, DEX, frontend or visual base differs")
        previous = {kind: r149.fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        old_payload = previous["psx"]["payloadSha256"]
        need(len(old_payload) == 346 and old_payload[CAROUSEL] == CAROUSEL_BASE_SHA and
             old_payload[FRONTEND] == FRONTEND_SHA and
             old_payload[ONLINE_BRIDGE] == ONLINE_BRIDGE_SHA and
             all(old_payload.get(name) == checksum for name, checksum in DEX.items()) and
             all(old_payload == value["payloadSha256"] and
                 previous["psx"]["productiveTransforms"] == value["productiveTransforms"]
                 for value in previous.values()) and
             all(before.get(name) == checksum for name, checksum in old_payload.items()),
             "R162 independent runtime bindings differ")
        old_registry = json.loads(original.read(ENGINES))
        old_contract = elf.elf_contract(original.read(CAROUSEL))
    new_contract = elf.elf_contract(native.read_bytes())
    need(old_contract["exports"] == new_contract["exports"] and
         old_contract["needed"] == new_contract["needed"] and
         old_contract["soname"] == new_contract["soname"] == ["libturbo_carousel.so"] and
         new_contract["minimumLoadAlignment"] >= 16384,
         "Carousel ABI or 16 KiB alignment changed")
    payload = {**old_payload, CAROUSEL: sha(native)}
    transforms = {**previous["psx"]["productiveTransforms"],
                  **{"game-selection-n64-cover-r163/" + name: checksum
                     for name, checksum in source_files.items()}}
    need(len(transforms) == len(previous["psx"]["productiveTransforms"]) + len(source_files),
         "R163 source history collides with previous transformations")
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
    need(raw in psx_binary.read_bytes(), "PSX marker lacks the R163 fingerprint")
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
             "Unrequested owner policy changed: " + kind)
        markers[kind] = primitive.marker(value, name, api, ndk, out)
        identities[kind] = value
    need(identities["n64"]["dependencySha256"].get("libstation_ae_bridge.so") == ONLINE_BRIDGE_SHA and
         identities["n64"]["options"].count("cpu=dynarec\n") == 1 and
         identities["n64"]["options"].count("video=glide64mk2\n") == 1 and
         identities["n64"]["options"].count("inputDelay=2\n") == 1,
         "N64 online bridge or approved options changed")
    registry, selected = inherited.expected_engines(old_registry, markers)
    retro = [row for row in old_registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(old_registry["engines"]) == len(registry["engines"]) == 13 and len(retro) == 9 and
         [row for row in registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
         "Unrelated engine descriptors changed")
    old_selected = {row["platform"]: row for row in old_registry["engines"] if row["platform"] in {"psx", "n64", "gamecube", "wii"}}
    new_selected = {row["platform"]: row for row in selected}
    need(set(old_selected) == set(new_selected) == {"psx", "n64", "gamecube", "wii"} and
         all({key: value for key, value in old_selected[platform].items()
              if key not in {"engineId", "runtimeSha256"}} ==
             {key: value for key, value in new_selected[platform].items()
              if key not in {"engineId", "runtimeSha256"}}
             for platform in old_selected) and
         new_selected["n64"]["dependencySha256"].get("libstation_ae_bridge.so") == ONLINE_BRIDGE_SHA,
         "Core, dependency, players, profile or online policy changed")
    engine_path = out / "engines.json"
    engine_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(engine_path.stat().st_size <= 32768, "Engine registry exceeds reader limit")
    replacements = {CAROUSEL: native, ENGINES: engine_path,
                    **{"lib/arm64-v8a/" + name: psx_binary if kind == "psx" else out / name
                       for kind, name in WRAPPERS.items()}}
    need(set(replacements) == REPLACED and
         all(r149.fingerprint(replacements["lib/arm64-v8a/" + name].read_bytes()) == identities[kind]
             for kind, name in WRAPPERS.items()),
         "Rebuilt marker fingerprint differs")
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
        need({name for name in before if before[name] != expected[name]} == REPLACED and
             len(expected) - len(REPLACED) == 13_856 and
             all(expected[name] == before[name] for name in (*DEX, ONLINE_BRIDGE, OFFLINE_BRIDGE, FRONTEND)),
             "Exactly five visual/identity APK entries must change")
        unsigned = out / "TurboStations-Premium-R163-selection-n64-cover-unsigned.apk"
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
             "Full R163 unsigned archive readback differs")
    receipt = {
        "schema": "station.r163.selection-n64-cover.package.v1", "revision": "R163", "passed": True,
        "baselineApkSha256": BASE_SHA, "baselineApkBytes": BASE_BYTES,
        "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
        "nativeReceiptSha256": sha(native.parent / "native-receipt.json"),
        "nativeLibrarySha256": native_proof["outputSha256"],
        "sourceFilesSha256": source_files, "replacedEntries": sorted(REPLACED),
        "preservedEntryCount": 13_856, "entryCount": ENTRY_COUNT,
        "expectedEntrySha256": expected, "preservedDexPartitions": 40,
        "classes35Sha256Preserved": DEX["classes35.dex"],
        "classes36Sha256Preserved": DEX["classes36.dex"],
        "onlineAeBridgeSha256Preserved": ONLINE_BRIDGE_SHA,
        "offlineAeBridgeSha256Preserved": OFFLINE_BRIDGE_SHA,
        "retainedOwnerPolicies": True, "preservedRetroArchDescriptors": 9,
        "visualAndLayoutOnly": True, "newTimersThreadsHeapAllocations": 0,
        "nativeToolFiles": native_tools, "signed": False, "installed": False,
        "serverRegistered": False,
    }
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return {"revision": "R163", "passed": True, "preservedEntryCount": 13_856,
            "unsignedApkSha256": receipt["unsignedApkSha256"]}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "native", "ndk", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.base.resolve(), args.native.resolve(), args.ndk.resolve(),
                           args.out.resolve()), ensure_ascii=False))
