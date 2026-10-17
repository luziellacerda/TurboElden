"""Assemble one unsigned R167 candidate from the exact signed R166 APK.

The only permitted entries are carousel, engines.json and three runtime
markers. Check mode creates no APK. Signing, installation and server registration
remain separate; no secret or APK belongs in the source repo.
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
REPO = Path(__file__).resolve().parents[3]
BASE_SHA = "4872f6dd0fef24930568c00c535a63afb66253f20a9c6a636627cadc52e71d6d"
BASE_BYTES = 2_715_466_850
ENTRY_COUNT = 13_861
DEX_NAME = "classes35.dex"
DEX_SHA = "5eccedadc2d5fe22a4d9aac9f23620ce9c5e3749d101831e0d42fd1972c13580"
DEX36_SHA = "a1c12b34c5eba4060707235c86dea3bbdfa59ef52264afc7ebaaa5d73231287c"
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_SHA = "3f20f862bed0d73668fdbc0fa06e7009011cbf8ea32c2cfff96029c2b8f23fc8"
NATIVE_RECEIPT_SHA = "3dd4cca1f17d0f7a6a438b2250f9b186b19548a2177362efd1315c1b75637c3b"
NATIVE_SCHEMA = "station.r167.selection-neighbor-native.v1"
FRONTEND = "lib/arm64-v8a/libstation_frontend.so"
FRONTEND_SHA = "438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d"
ONLINE_BRIDGE = "lib/arm64-v8a/libstation_ae_bridge.so"
ONLINE_BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
OFFLINE_BRIDGE = "lib/arm64-v8a/libae-bridge.so"
OFFLINE_BRIDGE_SHA = "ba5a7582295215f159e197f805dbfe85851aa912462996870f61ccd752ecb360"
ENGINES = "assets/station-online/engines.json"
ENGINES_SHA = "f058d338c1269e267135d5dd27854cf6abb40314c94dacecdd7db8e05ec50f0b"
WRAPPERS = {"psx": "libstation_psx_online.so",
            "n64": "libstation_mupen64plus_runtime.so",
            "dolphin": "libstation_dolphin_runtime.so"}
WRAPPER_SHA = {"psx": "3794feb8bb10dec2319bf9c367242fc2bdcf482b4d5eee1e7e6cfba8688699aa",
               "n64": "803a0bee5c5deb7314696d2a63424cf6c3de995befece526ab774eb6fdbf830d",
               "dolphin": "bf11f4e2851c5186d0318fa11130af6079a22ea1c660d34a07e0b346ded00df8"}
REPLACED = {CAROUSEL, ENGINES,
            *("lib/arm64-v8a/" + name for name in WRAPPERS.values())}
NATIVE_SOURCES = (
    "integration/game-selection-neighbor-width-r167/recipe/patch_neighbors.py",
    "integration/game-selection-neighbor-width-r167/recipe/build_native.py",
)
SOURCES = (
    "integration/game-selection-neighbor-width-r167/recipe/package_candidate.py",
    "integration/game-selection-neighbor-width-r167/recipe/sign_private.py",
)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def load(path: Path, name: str, imports: Path | None = None):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Pinned helper unavailable")
    module = importlib.util.module_from_spec(spec)
    previous = list(sys.path)
    try:
        if imports is not None:
            sys.path.insert(0, str(imports))
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = previous
    return module


def source_commit(revision: str, native_sources: dict[str, str] | None = None) -> dict[str, str]:
    need(bool(re.fullmatch(r"[0-9a-f]{40}", revision)), "Frozen source commit required")
    result = {}
    for name in (*SOURCES, *(native_sources or {})):
        relative = Path(name)
        need(not relative.is_absolute() and ".." not in relative.parts and
             relative.parts[0] == "integration" and "/" in name and
             name not in result, "Unsafe or duplicate productive source path")
        value = sha(REPO / name)
        raw = subprocess.check_output(["git", "-C", str(REPO), "show", revision + ":" + name])
        need(digest(raw) == value, "Source changed from frozen commit: " + name)
        if native_sources is not None and name in native_sources:
            need(native_sources[name] == value, "Native receipt source differs: " + name)
        result[name] = value
    return result


def verify_native(native: Path) -> dict:
    receipt_path = native.parent / "native-receipt.json"
    receipt = json.loads(receipt_path.read_text("utf-8"))
    need(receipt.get("schema") == NATIVE_SCHEMA and receipt.get("passed") is True and
         receipt.get("sourceLibrarySha256") == CAROUSEL_SHA and
         receipt.get("sourceReceiptSha256") == NATIVE_RECEIPT_SHA and
         receipt.get("outputSha256") == sha(native) and
         receipt.get("outputSha256") != CAROUSEL_SHA and
         receipt.get("abiPreserved") is True and
         receipt.get("compilerWarningsUnchanged") is True and
         receipt.get("extraPerFrameDrawCalls") == 0 and
         receipt.get("newTimersThreadsHeapAllocations") == 0 and
         receipt.get("newTimersThreadsWorkersOrPerFrameDraws") == 0 and
         receipt.get("effectRoutingPreserved") is True and
         receipt.get("changedHeaders") == ["native_formation.h"] and
         receipt.get("neighborPatchSourceSha256") == sha(REPO / NATIVE_SOURCES[0]) and
         receipt.get("neighborPatch", {}).get("selectedCoverAndNeighborHeightUnchanged") is True and
         receipt.get("neighborPatch", {}).get("newTimersThreadsWorkersAllocationsOrDraws") == 0 and
         isinstance(receipt.get("sourceFilesSha256"), dict) and
         set(receipt["sourceFilesSha256"]) == set(NATIVE_SOURCES),
         "Scoped R167 neighbor-width native receipt required")
    return receipt


def input_proof(base: Path, native: Path | None, ndk: Path | None,
                revision: str, full: bool):
    need(base.is_file() and base.stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
         "Exact signed R166 donor required")
    r149 = load(REPO / "integration/dolphin-onpause-r149/recipe/build_candidate.py", "r165_r149")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r165_elf")
    native_proof = verify_native(native) if native is not None else None
    need(not full or native_proof is not None, "Combined APK needs reviewed native library")
    source_files = source_commit(revision, native_proof["sourceFilesSha256"] if native_proof else None)
    identity_dir = REPO / "integration/online-lifecycle-review-r135/recipe"
    identity = load(identity_dir / "build_runtime_identity.py", "r165_identity", identity_dir)
    primitive = load(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py",
                     "r165_marker")
    identity.verify_dependencies()
    tools = identity.native_tools(ndk) if full else None
    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == ENTRY_COUNT and REPLACED <= set(names) and
             {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} ==
             {"classes.dex", *(f"classes{i}.dex" for i in range(2, 41))},
             "R166 archive shape differs")
        locked = {DEX_NAME: DEX_SHA, "classes36.dex": DEX36_SHA, CAROUSEL: CAROUSEL_SHA,
                  FRONTEND: FRONTEND_SHA, ONLINE_BRIDGE: ONLINE_BRIDGE_SHA,
                  OFFLINE_BRIDGE: OFFLINE_BRIDGE_SHA, ENGINES: ENGINES_SHA,
                  **{"lib/arm64-v8a/" + name: WRAPPER_SHA[kind]
                     for kind, name in WRAPPERS.items()}}
        need(all(entry_sha(original, name) == value for name, value in locked.items()),
             "R166 protected binary differs")
        if native is not None:
            old_abi = elf.elf_contract(original.read(CAROUSEL))
            new_abi = elf.elf_contract(native.read_bytes())
            need(old_abi["exports"] == new_abi["exports"] and
                 old_abi["needed"] == new_abi["needed"] and
                 old_abi["soname"] == new_abi["soname"] == ["libturbo_carousel.so"] and
                 new_abi["minimumLoadAlignment"] >= 16384,
                 "Carousel ABI or 16 KiB ELF alignment changed")
        previous = {kind: r149.fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        payload = previous["psx"]["payloadSha256"]
        need(len(payload) == 346 and payload[DEX_NAME] == DEX_SHA and
             payload["classes36.dex"] == DEX36_SHA and payload[CAROUSEL] == CAROUSEL_SHA and
             payload[ONLINE_BRIDGE] == ONLINE_BRIDGE_SHA and payload[FRONTEND] == FRONTEND_SHA and
             all(value["payloadSha256"] == payload and
                 value["productiveTransforms"] == previous["psx"]["productiveTransforms"]
                        for value in previous.values()), "Shared R166 payload bindings differ")
        registry = json.loads(original.read(ENGINES))
        old_selected = {row["platform"]: row for row in registry["engines"]
                        if row["platform"] in {"psx", "n64", "gamecube", "wii"}}
        need(len(registry["engines"]) == 13 and len(old_selected) == 4 and
             old_selected["n64"]["dependencySha256"].get("libstation_ae_bridge.so") == ONLINE_BRIDGE_SHA and
             old_selected["n64"]["options"].count("cpu=dynarec\n") == 1 and
             old_selected["n64"]["options"].count("video=glide64mk2\n") == 1 and
             old_selected["n64"]["options"].count("inputDelay=2\n") == 1,
             "N64 approved online options differ")
        need(all(payload.get(name) == entry_sha(original, name) for name in payload),
             "R166 marker payload map differs from APK")
        before = {name: entry_sha(original, name) for name in names} if full else None
    return dict(sourceFiles=source_files, previous=previous,
                payload=payload, registry=registry, before=before, names=names,
                 r149=r149, elf=elf, identity=identity, primitive=primitive, tools=tools,
                 nativeProof=native_proof,
                 nativeReceiptSha=sha(native.parent / "native-receipt.json") if native else None)


def build(base: Path, native: Path | None, ndk: Path | None,
          out: Path | None, revision: str, check_only: bool) -> dict:
    need(check_only or out is not None and not out.exists(),
         "New isolated output directory required")
    proof = input_proof(base, native, ndk, revision, not check_only)
    if check_only:
        return {"passed": True, "assembled": False, "donorApkSha256": BASE_SHA,
                "preservedClasses35Sha256": DEX_SHA,
                 "nativeSha256": sha(native) if native is not None else None,
                 "nativePending": native is None,
                "plannedEntries": sorted(REPLACED), "preservedEntryCount": 13_856,
                "sourceCommit": revision}
    need(out is not None and native is not None and ndk is not None,
         "Fresh output, native library and pinned NDK required")
    source_files = proof["sourceFiles"]
    previous = proof["previous"]
    payload = {**proof["payload"], CAROUSEL: sha(native)}
    transforms = {**previous["psx"]["productiveTransforms"],
                  **{"station-selection-neighbor-r167/" + name: checksum
                     for name, checksum in source_files.items()}}
    need(len(transforms) == len(previous["psx"]["productiveTransforms"]) + len(source_files),
         "R167 source history collides with previous transforms")
    out.mkdir(parents=True)
    temp = out / "temp"
    temp.mkdir()
    env = {**os.environ, "TEMP": str(temp), "TMP": str(temp), "PYTHONDONTWRITEBYTECODE": "1"}
    identity = proof["identity"]
    primitive = proof["primitive"]
    markers, identities = {}, {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE_SHA, payloadSha256=payload, productiveTransforms=transforms)
    need(identity.policy(psx) == identity.policy(previous["psx"]), "PSX policy changed")
    raw = canonical(psx)
    source = out / "StationPsxIdentity.cpp"
    source.write_text(
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n',
        encoding="ascii")
    psx_out = out / "native"
    compile_psx = [sys.executable, "-B", str(REPO / "integration/psx-online/recipe/build_entry.py"),
                   "--ndk", str(ndk), "--owner", str(identity.PSX / "native"),
                   "--protocol", str(identity.PSX / "native"),
                   "--pinned-options", str(identity.PSX / "native"),
                   "--identity-source", str(source), "--out", str(psx_out)]
    result = subprocess.run(compile_psx, capture_output=True, text=True, timeout=1800, env=env)
    (out / "psx-marker.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    need(result.returncode == 0, "Pinned PSX marker build failed")
    psx_binary = psx_out / WRAPPERS["psx"]
    need(raw in psx_binary.read_bytes(), "PSX marker lacks exact R167 fingerprint")
    markers["psx"] = {"runtimeLibrary": psx_binary.name, "runtimeSha256": sha(psx_binary),
                      "runtimeBytes": psx_binary.stat().st_size, "fingerprintSha256": digest(raw)}
    identities["psx"] = psx
    prior_temp = {key: os.environ.get(key) for key in ("TEMP", "TMP", "TMPDIR")}
    os.environ.update(TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    try:
        for kind, api in (("n64", "StationMupenRuntime"), ("dolphin", "StationDolphinRuntime")):
            value = copy.deepcopy(previous[kind])
            name = WRAPPERS[kind]
            value.update(baseApkSha256=BASE_SHA, payloadSha256=payload,
                         productiveTransforms=transforms,
                         parentFingerprintSha256=digest(canonical(previous[kind])),
                         parentRuntimeSha256=proof["before"]["lib/arm64-v8a/" + name],
                         psxRuntimeSha256=markers["psx"]["runtimeSha256"])
            need(identity.policy(value) == identity.policy(previous[kind]),
                 "Unrequested owner policy changed: " + kind)
            markers[kind] = primitive.marker(value, name, api, ndk, out)
            identities[kind] = value
    finally:
        for key, value in prior_temp.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    registry, selected = identity.expected_engines(proof["registry"], markers)
    old_selected = {row["platform"]: row for row in proof["registry"]["engines"]
                    if row["platform"] in {"psx", "n64", "gamecube", "wii"}}
    new_selected = {row["platform"]: row for row in selected}
    need(len(registry["engines"]) == 13 and len(selected) == 4 and
         all({k: v for k, v in old_selected[name].items() if k not in {"engineId", "runtimeSha256"}} ==
             {k: v for k, v in new_selected[name].items() if k not in {"engineId", "runtimeSha256"}}
             for name in old_selected) and
         [row for row in registry["engines"] if row["platform"] not in old_selected] ==
         [row for row in proof["registry"]["engines"] if row["platform"] not in old_selected],
         "Engine policies or retro descriptors changed")
    engine_path = out / "engines.json"
    engine_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(engine_path.stat().st_size <= 32768, "Engine registry exceeds reader limit")
    replacements = {CAROUSEL: native, ENGINES: engine_path,
                    **{"lib/arm64-v8a/" + name: psx_binary if kind == "psx" else out / name
                       for kind, name in WRAPPERS.items()}}
    need(set(replacements) == REPLACED and
         all(proof["r149"].fingerprint(replacements["lib/arm64-v8a/" + name].read_bytes()) == identities[kind]
             for kind, name in WRAPPERS.items()), "Marker fingerprint differs")
    with zipfile.ZipFile(base) as original:
        for kind, name in WRAPPERS.items():
            path = "lib/arm64-v8a/" + name
            old_abi = proof["elf"].elf_contract(original.read(path))
            new_abi = proof["elf"].elf_contract(replacements[path].read_bytes())
            need(old_abi["exports"] == new_abi["exports"] and
                 old_abi["needed"] == new_abi["needed"] and
                 old_abi["soname"] == new_abi["soname"] == [name] and
                 new_abi["minimumLoadAlignment"] >= 16384,
                 "Runtime marker ABI changed: " + kind)
        expected = {**proof["before"], **{name: sha(path) for name, path in replacements.items()}}
        need({name for name in proof["before"] if proof["before"][name] != expected[name]} == REPLACED and
             len(expected) - len(REPLACED) == 13_856 and
             all(expected[name] == proof["before"][name] for name in
                 (DEX_NAME, "classes36.dex", FRONTEND, ONLINE_BRIDGE, OFFLINE_BRIDGE)),
             "Exactly five R167 APK entries must change")
        unsigned = out / "TurboStations-Premium-R167-combined-unsigned.apk"
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
        need(candidate.namelist() == proof["names"] and
             {name: entry_sha(candidate, name) for name in proof["names"]} == expected,
             "Full R167 APK entry readback differs")
    receipt = {"schema": "station.selection.neighbor-width.package.r167.v1", "passed": True,
               "revision": "R167", "sourceCommit": revision,
               "baselineApkSha256": BASE_SHA, "baselineApkBytes": BASE_BYTES,
               "nativeReceiptSha256": proof["nativeReceiptSha"],
               "nativeLibrarySha256": sha(native),
               "sourceFilesSha256": source_files,
               "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
               "entryCount": ENTRY_COUNT, "replacedEntries": sorted(REPLACED),
               "preservedEntryCount": 13_856, "expectedEntrySha256": expected,
               "changedDexPartitions": [], "preservedDexPartitions": 40,
               "classes35Sha256Preserved": DEX_SHA,
               "classes36Sha256Preserved": DEX36_SHA,
               "onlineAeBridgeSha256Preserved": ONLINE_BRIDGE_SHA,
               "offlineAeBridgeSha256Preserved": OFFLINE_BRIDGE_SHA,
               "carouselSha256ChangedFrom": CAROUSEL_SHA,
               "frontendSha256Preserved": FRONTEND_SHA,
               "runtimeMarkers": markers,
               "onlineEngineIds": {row["platform"]: row["engineId"] for row in selected},
               "retainedOwnerPolicies": True, "retainedRetroDescriptors": 9,
               "newThreadsTimersOrPolling": False,
               "extraPerFrameDrawCalls": 0,
               "effectRoutingAudited": True,
               "nativeToolFiles": proof["tools"],
               "signed": False, "installed": False, "serverRegistered": False,
               "physicalGameplayValidated": False}
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    need(source_commit(revision, proof["nativeProof"]["sourceFilesSha256"]) == source_files and
         sha(base) == BASE_SHA and sha(native) == proof["nativeProof"]["outputSha256"] and
         sha(native.parent / "native-receipt.json") == proof["nativeReceiptSha"],
         "Source or payload changed during package assembly")
    return {"passed": True, "unsignedApkSha256": receipt["unsignedApkSha256"],
            "changedEntries": sorted(REPLACED), "signed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--ndk", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--check-inputs-only", action="store_true")
    args = parser.parse_args()
    if not args.check_inputs_only and (args.ndk is None or args.native is None or args.out is None):
        parser.error("--native, --ndk and --out are required for full marker/package build")
    print(json.dumps(build(args.base, args.native, args.ndk, args.out,
                           args.source_commit, args.check_inputs_only), sort_keys=True))
