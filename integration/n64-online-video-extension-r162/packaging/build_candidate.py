"""Package the isolated N64 online video-extension candidate from exact signed R161.

The scoped DEX proof supplies classes35 and classes36. One new bridge ELF is
added; the three bound runtime identities and engine registry are renewed.
Every other APK entry, including the offline bridge and native cores, stays
byte-identical. Signing, server registration and installation are separate.
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
import struct
import subprocess
import sys
import zipfile


sys.dont_write_bytecode = True
zipfile.ZIP64_LIMIT = (1 << 32) - 1
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE_SHA = "66f429d47af725a6767064c3623ee10c505171a85fbc8c0a50dc9e5bc4f80081"
BASE_BYTES = 2_715_122_703
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_BASE_SHA = "7d2f2be22083c3fb2a27df9fd43c3b92cf63bc74f87e1f64955753910b00c025"
FRONTEND = "lib/arm64-v8a/libstation_frontend.so"
FRONTEND_SHA = "438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d"
DEXES = {
    "classes35.dex": "59db81435a197d9e33ce20822a6bf86f2a6746e98998cdf721dff9eeafcd97bf",
    "classes36.dex": "6e0f7116d156518fad1e65e72f4c204cfacfd9904c4ee2c3110395d56842d707",
}
ENGINES = "assets/station-online/engines.json"
ENGINES_SHA = "f90353af952c25cef27a2a7003e043f8234f51dee322f522401e53f3d2d7cf66"
BRIDGE = "lib/arm64-v8a/libstation_ae_bridge.so"
BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
BRIDGE_BYTES = 331_520
OFFLINE_BRIDGE = "lib/arm64-v8a/libae-bridge.so"
OFFLINE_BRIDGE_SHA = "ba5a7582295215f159e197f805dbfe85851aa912462996870f61ccd752ecb360"
WRAPPERS = {"psx": "libstation_psx_online.so", "n64": "libstation_mupen64plus_runtime.so",
            "dolphin": "libstation_dolphin_runtime.so"}
WRAPPER_SHA = {
    "psx": "3c5f696fa30ee9a7760b3925acf49693456a5a988f6362062658a3604e4a1939",
    "n64": "656d6d7c017f17b55c3da06a5ee5ed11a60072f1b159790c78c4a8ab4606c9e3",
    "dolphin": "8b181081428b9012eb8bcb291010018d1b0c0d3217e5e555f6db306b582b5256",
}
REPLACED = {*DEXES, ENGINES, *("lib/arm64-v8a/" + name for name in WRAPPERS.values()), BRIDGE}
REPLACED_EXISTING = REPLACED - {BRIDGE}
SOURCE_FILES = (
    "versions/station-mupen-online-r162-20261015/recipes/build_station_ae_bridge.py",
    "integration/n64-online-video-extension-r162/recipe/build_dex.py",
    "integration/n64-online-video-extension-r162/recipe/patch_bridge.py",
    "integration/n64-online-video-extension-r162/recipe/StationN64Bridge.java",
    "integration/n64-online-video-extension-r162/packaging/build_candidate.py",
    "integration/n64-online-video-extension-r162/packaging/sign_private.py",
    "integration/n64-online-video-extension-r162/packaging/package_private_kit.py",
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


def bridge_abi(raw: bytes) -> dict:
    """Read AE bridge ABI; the pinned offline donor itself has 4 KiB LOAD alignment."""
    need(raw[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", raw, 18)[0] == 183,
         "ARM64 AE bridge ELF required")
    phoff = struct.unpack_from("<Q", raw, 32)[0]
    phsize, phnum = struct.unpack_from("<HH", raw, 54)
    loads = [struct.unpack_from("<IIQQQQQQ", raw, phoff + i * phsize)
             for i in range(phnum)]
    aligns = [row[-1] for row in loads if row[0] == 1]
    need(bool(aligns), "AE bridge ELF LOAD segments missing")
    shoff = struct.unpack_from("<Q", raw, 40)[0]
    shsize, shnum = struct.unpack_from("<HH", raw, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", raw, shoff + i * shsize)
                for i in range(shnum)]

    def string(table: bytes, index: int) -> str:
        end = table.find(b"\0", index)
        need(0 <= index < len(table) and end >= index, "Invalid AE bridge ELF string")
        return table[index:end].decode("ascii")

    exports, needed, sonames = [], [], []
    for row in sections:
        if row[1] not in (6, 11):
            continue
        table = sections[row[6]]
        strings = raw[table[4]:table[4] + table[5]]
        data = raw[row[4]:row[4] + row[5]]
        need(row[9] > 0 and len(data) % row[9] == 0, "Invalid AE bridge ELF table")
        for offset in range(0, len(data), row[9]):
            if row[1] == 11:
                name, info, other, index, _, _ = struct.unpack_from("<IBBHQQ", data, offset)
                if name and index and info >> 4 in (1, 2):
                    exports.append((string(strings, name), info, other))
            else:
                tag, value = struct.unpack_from("<qQ", data, offset)
                if tag == 1:
                    needed.append(string(strings, value))
                elif tag == 14:
                    sonames.append(string(strings, value))
    return {"exports": sorted(exports), "needed": sorted(needed),
            "soname": sonames, "minimumLoadAlignment": min(aligns)}


def verify_dex_proof(dex_dir: Path) -> tuple[dict[str, Path], dict[str, str], str]:
    receipt_path = dex_dir / "dex-receipt.json"
    need(receipt_path.is_file(), "Scoped R162 VideoExt DEX receipt required")
    proof = json.loads(receipt_path.read_text("utf-8"))
    partitions = proof.get("partitions")
    need(proof.get("schema") == "station.n64.online-video-extension.r162.v1" and
         proof.get("passed") is True and proof.get("donorApkSha256") == BASE_SHA and
         isinstance(partitions, dict) and set(partitions) == set(DEXES),
         "Scoped N64 VideoExt proof differs")
    owners = {
        "classes35.dex": {"Lorg/emulationstation/frontend/netplay/StationN64Bridge;"},
        "classes36.dex": {"Lpaulscode/android/mupen64plusae/jni/CoreInterface;"},
    }
    paths: dict[str, Path] = {}
    candidate_hashes: dict[str, str] = {}
    for name, donor_hash in DEXES.items():
        row = partitions[name]
        path = dex_dir / ("candidate-" + name)
        count = row.get("classCount")
        candidate_hash = row.get("candidateDexSha256")
        need(path.is_file() and row.get("donorDexSha256") == donor_hash and
             set(row.get("owners", [])) == owners[name] and isinstance(count, int) and count > 1 and
             row.get("unrelatedClassesUnchanged") == count - 1 and
             isinstance(candidate_hash, str) and len(candidate_hash) == 64 and
             sha(path) == candidate_hash and candidate_hash != donor_hash,
             "Scoped R162 VideoExt DEX differs: " + name)
        paths[name], candidate_hashes[name] = path, candidate_hash
    return paths, candidate_hashes, sha(receipt_path)


def build(base: Path, dex_dir: Path, bridge: Path, ndk: Path, out: Path) -> dict:
    if out.exists():
        raise FileExistsError(out)
    need(base.stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
         "Exact signed R161 donor required")
    source_files = {name: sha(REPO / name) for name in SOURCE_FILES}
    dex_paths, candidate_hashes, dex_receipt_sha = verify_dex_proof(dex_dir)
    need(bridge.is_file() and bridge.name == "libstation_ae_bridge.so" and
         bridge.stat().st_size == BRIDGE_BYTES and sha(bridge) == BRIDGE_SHA,
         "Scoped R162 bridge ELF required")
    bridge_receipt_path = bridge.with_name("build-station-ae-bridge.json")
    bridge_receipt = json.loads(bridge_receipt_path.read_text("utf-8"))
    need(bridge_receipt.get("schema") == "station-ae-bridge-build-v1" and
         bridge_receipt.get("sha256") == BRIDGE_SHA and
         bridge_receipt.get("bytes") == BRIDGE_BYTES and
         bridge_receipt.get("originalBridgeSha256") == OFFLINE_BRIDGE_SHA and
         bridge_receipt.get("offlineBridgeUnchanged") is True and
         bridge_receipt.get("physicalGameplayValidated") is False,
         "Scoped native bridge proof differs")
    r149 = load(REPO / "integration/dolphin-onpause-r149/recipe/build_candidate.py", "r161_r149")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r161_elf")
    inherited_dir = REPO / "integration/online-lifecycle-review-r135/recipe"
    inherited = load(inherited_dir / "build_runtime_identity.py", "r161_identity", inherited_dir)
    primitive = load(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r161_marker")
    inherited.verify_dependencies()
    native_tools = inherited.native_tools(ndk)
    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and
             REPLACED_EXISTING <= set(names) and BRIDGE not in names and
             {name for name in names if name.endswith(".dex") and name.startswith("classes")} ==
             {"classes.dex", *(f"classes{i}.dex" for i in range(2, 41))},
             "R161 archive entry list changed")
        before = {name: entry_sha(original, name) for name in names}
        need(before[CAROUSEL] == CAROUSEL_BASE_SHA and before[FRONTEND] == FRONTEND_SHA and
             before[OFFLINE_BRIDGE] == OFFLINE_BRIDGE_SHA and
             all(before[name] == checksum for name, checksum in DEXES.items()) and
             before[ENGINES] == ENGINES_SHA and
             all(before["lib/arm64-v8a/" + name] == WRAPPER_SHA[kind]
                 for kind, name in WRAPPERS.items()),
             "R161 visual, room or runtime payload differs")
        previous = {kind: r149.fingerprint(original.read("lib/arm64-v8a/" + name))
                    for kind, name in WRAPPERS.items()}
        old_payload = previous["psx"]["payloadSha256"]
        need(len(old_payload) == 345 and old_payload[CAROUSEL] == CAROUSEL_BASE_SHA and
             old_payload[FRONTEND] == FRONTEND_SHA and
             old_payload["classes36.dex"] == DEXES["classes36.dex"] and
             all(old_payload[name] == checksum for name, checksum in DEXES.items()) and
             all(old_payload == value["payloadSha256"] and
                 previous["psx"]["productiveTransforms"] == value["productiveTransforms"]
                 for value in previous.values()) and
             all(before.get(name) == checksum for name, checksum in old_payload.items()),
             "R161 independent runtime identity bindings differ")
        old_registry = json.loads(original.read(ENGINES))
    original_n64 = next(row for row in old_registry["engines"] if row["platform"] == "n64")
    need(previous["n64"]["options"] == original_n64["options"],
         "R161 N64 registry and runtime options disagree")
    need(original_n64["options"].count("cpu=dynarec\n") == 1 and
         original_n64["options"].count("inputDelay=2\n") == 1,
         "Pinned R161 online CPU or input-delay profile differs")
    offline_abi = bridge_abi(bridge.read_bytes())
    with zipfile.ZipFile(base) as original:
        original_abi = bridge_abi(original.read(OFFLINE_BRIDGE))
    # The older offline build also exports six weak C++ exception RTTI names.
    # Preserve its 428 strong API symbols; the new status symbol is the only
    # additional strong export. Weak RTTI from the old toolchain is not ABI.
    original_exports = {item for item in original_abi["exports"] if item[1] >> 4 == 1}
    candidate_exports = {item for item in offline_abi["exports"] if item[1] >> 4 == 1}
    added_exports = candidate_exports - original_exports
    need(len(original_exports) == 428 and original_exports <= candidate_exports and
         len(added_exports) == 1 and
         next(iter(added_exports))[0] == "stationVideoOverrideReady" and
         offline_abi["needed"] == original_abi["needed"] and
         original_abi["minimumLoadAlignment"] >= 4096 and
         offline_abi["soname"] == ["libstation_ae_bridge.so"] and
         offline_abi["minimumLoadAlignment"] >= 16384,
         "R162 bridge ABI differs from pinned offline AE bridge")
    payload = {**old_payload, **candidate_hashes, BRIDGE: sha(bridge)}
    transforms = {**previous["psx"]["productiveTransforms"],
                  **{"n64-online-video-extension-r162/" + name: checksum for name, checksum in source_files.items()}}
    need(len(transforms) == len(previous["psx"]["productiveTransforms"]) + len(source_files),
         "R162 source history collides with an earlier transform")
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
    need(raw in psx_binary.read_bytes(), "PSX marker lacks the R162 fingerprint")
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
            need(BRIDGE.removeprefix("lib/arm64-v8a/") not in value["dependencySha256"],
                 "R161 N64 dependencies unexpectedly contain online AE bridge")
            value["dependencySha256"] = {
                **value["dependencySha256"], BRIDGE.removeprefix("lib/arm64-v8a/"): BRIDGE_SHA}
            expected_policy["dependencySha256"] = value["dependencySha256"]
        need(inherited.policy(value) == expected_policy,
             "Unrequested owner policy changed: " + kind)
        markers[kind] = primitive.marker(value, name, api, ndk, out)
        identities[kind] = value
    target_registry = copy.deepcopy(old_registry)
    target_n64 = next(row for row in target_registry["engines"] if row["platform"] == "n64")
    need(BRIDGE.removeprefix("lib/arm64-v8a/") not in target_n64["dependencySha256"],
         "R161 N64 registry unexpectedly contains online AE bridge")
    target_n64["dependencySha256"][BRIDGE.removeprefix("lib/arm64-v8a/")] = BRIDGE_SHA
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
         len({name for row in new_selected.values() for name in row["dependencySha256"]}) == 21 and
         new_selected["n64"]["dependencySha256"] ==
         {**old_selected["n64"]["dependencySha256"], BRIDGE.removeprefix("lib/arm64-v8a/"): BRIDGE_SHA} and
         all({key: value for key, value in old_selected[platform].items()
              if key not in {"engineId", "runtimeSha256", "dependencySha256"}} ==
             {key: value for key, value in new_selected[platform].items()
              if key not in {"engineId", "runtimeSha256", "dependencySha256"}}
             for platform in old_selected) and
         all(old_selected[platform]["dependencySha256"] == new_selected[platform]["dependencySha256"]
             for platform in old_selected if platform != "n64"),
         "Core, dependency, player, profile or owner policies changed")
    engine_path = out / "engines.json"
    engine_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(engine_path.stat().st_size <= 32768, "Engine registry exceeds reader limit")
    replacements = {**dex_paths, ENGINES: engine_path, BRIDGE: bridge,
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
        need({name for name in before if before[name] != expected[name]} == REPLACED_EXISTING and
             set(expected) - set(before) == {BRIDGE},
             "Exactly six R161 entries and one new R162 bridge must change")
        unsigned = out / "TurboStations-Premium-R162-n64-online-video-unsigned.apk"
        with zipfile.ZipFile(unsigned, "w", allowZip64=False) as destination:
            for item in original.infolist():
                with destination.open(copy.copy(item), "w", force_zip64=False) as target:
                    if item.filename in replacements:
                        with replacements[item.filename].open("rb") as stream:
                            shutil.copyfileobj(stream, target, 1024 * 1024)
                    else:
                        with original.open(item.filename) as stream:
                            shutil.copyfileobj(stream, target, 1024 * 1024)
            reference = original.getinfo(OFFLINE_BRIDGE)
            addition = zipfile.ZipInfo(BRIDGE, date_time=reference.date_time)
            addition.compress_type = zipfile.ZIP_STORED
            addition.external_attr = reference.external_attr
            addition.create_system = reference.create_system
            with destination.open(addition, "w", force_zip64=False) as target:
                with bridge.open("rb") as stream:
                    shutil.copyfileobj(stream, target, 1024 * 1024)
    with zipfile.ZipFile(unsigned) as candidate:
        need(candidate.namelist() == names + [BRIDGE] and
             {name: entry_sha(candidate, name) for name in candidate.namelist()} == expected,
             "Full 13,861-entry unsigned readback failed")
    receipt = {"schema": "station.r162.n64-online-video-extension.package.v1", "revision": "R162",
               "passed": True, "baselineApkSha256": BASE_SHA,
               "unsignedApkSha256": sha(unsigned), "unsignedApkBytes": unsigned.stat().st_size,
               "sourceFilesSha256": source_files, "replacedEntries": sorted(REPLACED),
               "preservedEntryCount": 13854, "entryCount": 13861,
               "expectedEntrySha256": expected, "preservedDexPartitions": 38,
               "changedDexPartitions": sorted(DEXES), "dexReceiptSha256": dex_receipt_sha,
               "dexSha256": candidate_hashes, "donorDexSha256": DEXES,
               "carouselSha256Preserved": CAROUSEL_BASE_SHA,
               "offlineAeBridgeSha256Preserved": OFFLINE_BRIDGE_SHA,
               "addedOnlineAeBridgeSha256": sha(bridge),
               "retainedOwnerPolicies": True, "preservedRetroArchDescriptors": 9,
               "preservedIndependentDependencies": 20,
               "addedN64Dependency": {BRIDGE.removeprefix("lib/arm64-v8a/"): BRIDGE_SHA},
               "visualCarouselAndOtherEmulatorsPreserved": True,
               "nativeToolFiles": native_tools,
               "n64OnlineOptions": original_n64["options"],
               "offlineProfileChanged": False, "inputDelayChanged": False,
               "taskRemovalChanged": False,
               "serverRegistered": False, "signed": False, "installed": False}
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return {"revision": "R162", "passed": True, "preservedEntryCount": 13854,
            "unsignedApkSha256": receipt["unsignedApkSha256"]}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "dex-dir", "bridge", "ndk", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.base.resolve(), args.dex_dir.resolve(),
                           args.bridge.resolve(), args.ndk.resolve(), args.out.resolve()), ensure_ascii=False))
