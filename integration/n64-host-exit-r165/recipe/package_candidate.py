"""Assemble an unsigned R165 APK with exactly five changed R164 ZIP entries.

Call only after the scoped DEX proof passes. Signing, installation and server
registration remain separate; no secret or APK belongs in the source repo.
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
BASE_SHA = "903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210"
BASE_BYTES = 2_715_466_850
ENTRY_COUNT = 13_861
DEX_NAME = "classes35.dex"
DEX_SHA = "0489cd99a51d43d001cab4ef5374e03aea694b58f6cc72648e7217f363d79b52"
DEX36_SHA = "a1c12b34c5eba4060707235c86dea3bbdfa59ef52264afc7ebaaa5d73231287c"
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_SHA = "bd3222558a43f8998d51b0b72010ecb8a94c7ae62a14d34b39863d13737a10d0"
FRONTEND = "lib/arm64-v8a/libstation_frontend.so"
FRONTEND_SHA = "438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d"
ONLINE_BRIDGE = "lib/arm64-v8a/libstation_ae_bridge.so"
ONLINE_BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
OFFLINE_BRIDGE = "lib/arm64-v8a/libae-bridge.so"
OFFLINE_BRIDGE_SHA = "ba5a7582295215f159e197f805dbfe85851aa912462996870f61ccd752ecb360"
ENGINES = "assets/station-online/engines.json"
ENGINES_SHA = "ca778de0c7a83c193cb4abb164b0e5b2e77d4403016fe01c08b6cca0c16d1c42"
WRAPPERS = {"psx": "libstation_psx_online.so",
            "n64": "libstation_mupen64plus_runtime.so",
            "dolphin": "libstation_dolphin_runtime.so"}
WRAPPER_SHA = {"psx": "1b315b86b4a789247a355f09eb04bf41027e1cb8e5941019da6ade486835dd36",
               "n64": "bba0ea0d7ff730fe9548b5b4a32921ea892dbce131cb92d430dbf009f1c58f42",
               "dolphin": "c3d59714834540b65961678c9736790f7c4041853bb680c1ebcd7b2f943134fb"}
REPLACED = {DEX_NAME, ENGINES, *("lib/arm64-v8a/" + name for name in WRAPPERS.values())}
SOURCES = (
    "integration/n64-host-exit-r165/java/org/emulationstation/frontend/netplay/StationHumanDeparture.java",
    "integration/n64-host-exit-r165/recipe/build_dex.py",
    "integration/n64-host-exit-r165/recipe/package_candidate.py",
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


def source_commit(revision: str) -> dict[str, str]:
    need(bool(re.fullmatch(r"[0-9a-f]{40}", revision)), "Frozen source commit required")
    result = {}
    for name in SOURCES:
        value = sha(REPO / name)
        raw = subprocess.check_output(["git", "-C", str(REPO), "show", revision + ":" + name])
        need(digest(raw) == value, "Source changed from frozen commit: " + name)
        result[name] = value
    return result


def verify_dex(path: Path, revision: str) -> tuple[Path, dict]:
    receipt = json.loads((path / "dex-receipt.json").read_text("utf-8"))
    dex = path / DEX_NAME
    need(receipt.get("schema") == "station.n64.host-exit.dex.r165.v1" and
         receipt.get("passed") is True and receipt.get("sourceCommit") == revision and
         receipt.get("donorApkSha256") == BASE_SHA and receipt.get("donorDexSha256") == DEX_SHA and
         receipt.get("partition") == DEX_NAME and receipt.get("modifiedTypes") ==
         ["Lorg/emulationstation/frontend/netplay/StationHumanDeparture;"] and
         receipt.get("addedTypes") == receipt.get("removedTypes") == [] and
         receipt.get("classCount", 0) - receipt.get("unrelatedClassesUnchanged", -1) == 1 and
         receipt.get("event4CallerPreserved") is True and
         receipt.get("event4HelperCallCount") == 1 and
         receipt.get("changedDexPartitions") == [DEX_NAME] and
         receipt.get("apkAssembled") is False and receipt.get("signed") is False and
         receipt.get("installed") is False and dex.is_file() and
         sha(dex) == receipt.get("candidateDexSha256") and sha(dex) != DEX_SHA,
         "Exact R165 single-class DEX proof required")
    return dex, receipt


def input_proof(base: Path, dex_dir: Path, ndk: Path | None, revision: str, full: bool):
    need(base.is_file() and base.stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
         "Exact signed R164 donor required")
    source_files = source_commit(revision)
    dex, dex_proof = verify_dex(dex_dir, revision)
    r149 = load(REPO / "integration/dolphin-onpause-r149/recipe/build_candidate.py", "r165_r149")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r165_elf")
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
             "R164 archive shape differs")
        locked = {DEX_NAME: DEX_SHA, "classes36.dex": DEX36_SHA, CAROUSEL: CAROUSEL_SHA,
                  FRONTEND: FRONTEND_SHA, ONLINE_BRIDGE: ONLINE_BRIDGE_SHA,
                  OFFLINE_BRIDGE: OFFLINE_BRIDGE_SHA, ENGINES: ENGINES_SHA,
                  **{"lib/arm64-v8a/" + name: WRAPPER_SHA[kind]
                     for kind, name in WRAPPERS.items()}}
        need(all(entry_sha(original, name) == value for name, value in locked.items()),
             "R164 protected binary differs")
        previous = {kind: r149.fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        payload = previous["psx"]["payloadSha256"]
        need(len(payload) == 346 and payload[DEX_NAME] == DEX_SHA and
             payload["classes36.dex"] == DEX36_SHA and payload[CAROUSEL] == CAROUSEL_SHA and
             payload[ONLINE_BRIDGE] == ONLINE_BRIDGE_SHA and payload[FRONTEND] == FRONTEND_SHA and
             all(value["payloadSha256"] == payload and
                 value["productiveTransforms"] == previous["psx"]["productiveTransforms"]
                 for value in previous.values()), "Shared R164 payload bindings differ")
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
             "R164 marker payload map differs from APK")
        before = {name: entry_sha(original, name) for name in names} if full else None
    return dict(dex=dex, dexProof=dex_proof, sourceFiles=source_files, previous=previous,
                payload=payload, registry=registry, before=before, names=names,
                r149=r149, elf=elf, identity=identity, primitive=primitive, tools=tools)


def build(base: Path, dex_dir: Path, ndk: Path | None, out: Path,
          revision: str, check_only: bool) -> dict:
    need(not out.exists(), "New isolated output directory required")
    proof = input_proof(base, dex_dir, ndk, revision, not check_only)
    if check_only:
        return {"passed": True, "assembled": False, "donorApkSha256": BASE_SHA,
                "dexSha256": proof["dexProof"]["candidateDexSha256"],
                "plannedEntries": sorted(REPLACED), "sourceCommit": revision}
    source_files = proof["sourceFiles"]
    previous = proof["previous"]
    payload = {**proof["payload"], DEX_NAME: sha(proof["dex"])}
    transforms = {**previous["psx"]["productiveTransforms"],
                  **{"n64-host-exit-r165/" + name: checksum for name, checksum in source_files.items()}}
    need(len(transforms) == len(previous["psx"]["productiveTransforms"]) + len(source_files),
         "R165 source history collides with previous transforms")
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
    need(raw in psx_binary.read_bytes(), "PSX marker lacks exact R165 fingerprint")
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
    replacements = {DEX_NAME: proof["dex"], ENGINES: engine_path,
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
                 ("classes36.dex", CAROUSEL, FRONTEND, ONLINE_BRIDGE, OFFLINE_BRIDGE)),
             "Exactly five R165 APK entries must change")
        unsigned = out / "TurboStations-Premium-R165-host-exit-unsigned.apk"
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
             "Full R165 APK entry readback differs")
    receipt = {"schema": "station.n64.host-exit.package.r165.v1", "passed": True,
               "revision": "R165", "sourceCommit": revision,
               "baselineApkSha256": BASE_SHA, "baselineApkBytes": BASE_BYTES,
               "dexReceiptSha256": sha(dex_dir / "dex-receipt.json"),
               "sourceFilesSha256": source_files,
               "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
               "entryCount": ENTRY_COUNT, "replacedEntries": sorted(REPLACED),
               "preservedEntryCount": 13_856, "expectedEntrySha256": expected,
               "changedDexPartitions": [DEX_NAME], "preservedDexPartitions": 39,
               "classes36Sha256Preserved": DEX36_SHA,
               "onlineAeBridgeSha256Preserved": ONLINE_BRIDGE_SHA,
               "offlineAeBridgeSha256Preserved": OFFLINE_BRIDGE_SHA,
               "carouselSha256Preserved": CAROUSEL_SHA,
               "frontendSha256Preserved": FRONTEND_SHA,
               "runtimeMarkers": markers,
               "onlineEngineIds": {row["platform"]: row["engineId"] for row in selected},
               "retainedOwnerPolicies": True, "retainedRetroDescriptors": 9,
               "newThreadsTimersOrPolling": False,
               "nativeToolFiles": proof["tools"],
               "signed": False, "installed": False, "serverRegistered": False,
               "physicalGameplayValidated": False}
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    need(source_commit(revision) == source_files and sha(base) == BASE_SHA and
         sha(proof["dex"]) == proof["dexProof"]["candidateDexSha256"],
         "Source or payload changed during package assembly")
    return {"passed": True, "unsignedApkSha256": receipt["unsignedApkSha256"],
            "changedEntries": sorted(REPLACED), "signed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--dex-dir", type=Path, required=True)
    parser.add_argument("--ndk", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--check-inputs-only", action="store_true")
    args = parser.parse_args()
    if not args.check_inputs_only and args.ndk is None:
        parser.error("--ndk is required for full marker/package build")
    print(json.dumps(build(args.base, args.dex_dir, args.ndk, args.out,
                           args.source_commit, args.check_inputs_only), sort_keys=True))
