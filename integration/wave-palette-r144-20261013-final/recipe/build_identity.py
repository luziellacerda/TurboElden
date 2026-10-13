"""Bind the two R144 visual payloads to the original independent owner policies."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
from common import (BASE, BASE_BYTES, DEX, RETRO, ROOT, REPO, PARTITION, CAROUSEL,
                    CAROUSEL_SHA, PRESERVED_DEX35, WRAPPERS, need, sha, digest,
                    canonical, read, fingerprints, entry_sha, verify_commit,
                    isolated, state_fields, wrapper_contract, elf_contract)

ROOT_DEX = {"classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]}
WAVE_TYPE = "Lorg/emulationstation/frontend/station/StationWaveBackground;"
DEPENDENCIES = {
    "integration/online-lifecycle-review-r135/recipe/build_runtime_identity.py": "f1a1d8e3bd161bb6751801efc5a314e61b403f670822085dc92127dc63fe98da",
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    previous_path = list(sys.path)
    try:
        sys.path.insert(0, str(path.parent))
        spec.loader.exec_module(result)
    finally:
        sys.path[:] = previous_path
    return result


def retained_builder():
    for name, expected in DEPENDENCIES.items():
        need(sha(REPO / name) == expected, "Retained identity implementation changed: " + name)
    result = module(REPO / next(iter(DEPENDENCIES)), "r144_visual_inherited")
    result.verify_dependencies()
    return result


def extract_fingerprint(raw):
    docs = []
    for match in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw):
        end = raw.find(b"\0", match.start())
        if end < 0:
            continue
        try:
            value = json.loads(raw[match.start():end].decode("ascii"))
        except (ValueError, UnicodeError):
            continue
        if isinstance(value, dict) and "baseApkSha256" in value and "payloadSha256" in value:
            docs.append(value)
    need(len(docs) == 1, "Exactly one embedded wrapper identity required")
    value = docs[0]
    need(canonical(value) in raw and digest(canonical(value)).encode("ascii") in raw,
         "Canonical wrapper manifest and fingerprint differ")
    return value


def validate_dex_receipt(receipt, path, commit, pins):
    need(receipt.get("schema") == "station.r144.wave-palette.dex.v1" and
         receipt.get("passed") is True and receipt.get("compiled") is True and
         receipt.get("sourceCommit") == commit and receipt.get("sourceFiles") == pins and
         receipt.get("baselineApkSha256") == BASE and receipt.get("baselineDexSha256") == DEX and
         receipt.get("outputDexSha256") == sha(path) and receipt.get("inversePassed") is True and
         receipt.get("originalClassCount") == receipt.get("finalClassCount") == 272 and
         receipt.get("unchangedClasses") == 271 and receipt.get("addedClasses") == receipt.get("removedClasses") == [] and
         receipt.get("modifiedMethods") == ["updatePalette"] and
         receipt.get("unrelatedClassesByteIdentical") is True and
         receipt.get("preservedDex35Sha256") == PRESERVED_DEX35 and
         set(receipt.get("preservedDexSha256", {})) == ROOT_DEX - {PARTITION} and
         receipt["preservedDexSha256"].get("classes35.dex") == PRESERVED_DEX35,
         "Exact one-method visual DEX receipt and all 39 preserved DEX proofs required")
    before, after, retained = (receipt.get(key, {}) for key in
                              ("baselineClassSha256", "outputClassSha256", "unchangedClassSha256"))
    need(len(before) == len(after) == 272 and len(retained) == 271 and
         set(before) == set(after) and set(before) - {WAVE_TYPE} == set(retained) and
         {kind: before[kind] for kind in retained} == {kind: after[kind] for kind in retained} == retained and
         before[WAVE_TYPE] != after[WAVE_TYPE] and sha(path) != DEX,
         "Only StationWaveBackground may differ in canonical class projections")
    return receipt


def validate_native_receipt(receipt, path, commit, pins):
    source = module(ROOT / "recipe/build_native.py", "r144_visual_native_contract")
    native_pins = source.source_map()
    need(set(native_pins) == {"native/native_space.h", "native/station_wave_palette.h", "recipe/build_native.py"} and
         all(pins.get(name) == checksum for name, checksum in native_pins.items()),
         "Native receipt must use the same three frozen R144 source inputs")
    payload = receipt.get("payloads", {}).get(CAROUSEL, {})
    waves = receipt.get("transforms", {}).get("waves", {})
    need(receipt.get("schema") == "station.wave.palette.native.v1" and receipt.get("revision") == "R144" and
         receipt.get("passed") is True and receipt.get("compiled") is True and
         receipt.get("sourceCommit") == commit and receipt.get("sourceSha256") == native_pins and
         receipt.get("baseApkSha256") == BASE and receipt.get("baselineNativeSha256") == CAROUSEL_SHA and
         receipt.get("baselineReproduced") == {"r133Carousel": True, "r143Carousel": True} and
         receipt.get("approvedScopes") == ["waves-platform-rgb-and-opacity-only"] and
         receipt.get("dexChanged") is False and receipt.get("frontendChanged") is False and
         receipt.get("exportsExactlyPreserved") is True and receipt.get("dependenciesExactlyPreserved") is True and
         receipt.get("sonameExactlyPreserved") is True and receipt.get("nativeLoadAlignment") == "0x4000" and
         set(receipt.get("payloads", {})) == {CAROUSEL} and payload.get("sha256") == sha(path) and
         payload.get("bytes") == Path(path).stat().st_size and
         Path(payload.get("path", "")).resolve() == Path(path).resolve() and
         receipt.get("outputNativeSha256") == sha(path) and sha(path) != CAROUSEL_SHA and
         set(waves) == {"wholeHeaderInversePassed", "drawNativeWavesByteIdentical", "drawNativeSpaceByteIdentical",
                        "diagonalBackdropByteIdentical", "onlyColorSelectorBlockReplaced"} and
         all(value is True for value in waves.values()),
         "Byte-exact reproduced donor and closed native color-selector qualification required")
    elf_contract(Path(path).read_bytes())
    return receipt


def transforms_for(previous, pins):
    old = previous["psx"]["productiveTransforms"]
    extra = {ROOT.name + "/" + name: checksum for name, checksum in pins.items()}
    need(not set(old).intersection(extra), "R144 source chain must append without overwriting history")
    return {**old, **extra}


def expected_payload(previous, dex_path, native_path):
    old = previous["psx"]["payloadSha256"]
    need(len(old) == 345 and old.get(PARTITION) == DEX and old.get(CAROUSEL) == CAROUSEL_SHA and
         old.get("classes35.dex") == PRESERVED_DEX35,
         "Exact R143 345-entry payload, including stable multiplayer DEX35, required")
    result = {**old, PARTITION: sha(dex_path), CAROUSEL: sha(native_path)}
    need(len(result) == 345 and {name for name in old if old[name] != result[name]} == {PARTITION, CAROUSEL},
         "Only visual DEX28 and carousel hashes may change in the complete payload")
    return result


def validate_marker_bindings(original, previous, payload, pins, markers, files):
    inherited = retained_builder()
    transforms = transforms_for(previous, pins)
    need(set(markers) == set(WRAPPERS), "Exactly three renewed identity wrappers required")
    for kind, (library, parent_hash) in WRAPPERS.items():
        raw = Path(files["lib/arm64-v8a/" + library]).read_bytes()
        actual = extract_fingerprint(raw)
        wanted = copy.deepcopy(previous[kind])
        wanted.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
        if kind != "psx":
            wanted.update(parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_hash,
                          psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        marker = markers[kind]
        need(marker.get("runtimeLibrary") == library and marker.get("runtimeSha256") == digest(raw) != parent_hash and
             marker.get("runtimeBytes") == len(raw) and marker.get("fingerprintSha256") == digest(canonical(actual)) and
             actual == wanted and inherited.policy(actual) == inherited.policy(previous[kind]),
             "Owner implementation, dependencies, controllers, options or canonical binding differs: " + kind)
        wrapper_contract(original.read("lib/arm64-v8a/" + library), raw, kind)
    return inherited.expected_engines(json.loads(original.read("assets/station-online/engines.json")), markers)


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed stable R143 donor required")
    pins = verify_commit(a.source_commit)
    dex = validate_dex_receipt(read(a.dex_receipt), a.dex, a.source_commit, pins)
    native_receipt = validate_native_receipt(read(a.native_receipt), a.native, a.source_commit, pins)
    with zipfile.ZipFile(a.base) as archive:
        previous = fingerprints(archive)
        need(entry_sha(archive, "lib/arm64-v8a/libstation_retroarch.so") == RETRO and
             entry_sha(archive, "classes35.dex") == PRESERVED_DEX35 and entry_sha(archive, CAROUSEL) == CAROUSEL_SHA,
             "Stable R143 runtime, multiplayer repair and carousel donor must stay exact")
        original = json.loads(archive.read("assets/station-online/engines.json"))
        for name, checksum in previous["psx"]["payloadSha256"].items():
            need(entry_sha(archive, name) == checksum, "Inherited real payload differs: " + name)
        need({name: entry_sha(archive, name) for name in ROOT_DEX - {PARTITION}} == dex["preservedDexSha256"],
             "Exact 39 retained donor DEX partitions required")
        old_contract, new_contract = elf_contract(archive.read(CAROUSEL)), elf_contract(a.native.read_bytes())
        need(old_contract["exports"] == new_contract["exports"] and old_contract["needed"] == new_contract["needed"] and
             old_contract["soname"] == new_contract["soname"] == ["libturbo_carousel.so"],
             "Carousel native API, dependencies and SONAME must remain exact")
    payload = expected_payload(previous, a.dex, a.native)
    transforms = transforms_for(previous, pins)
    inherited = retained_builder()
    for name in ("StationPsxEntry.cpp", "StationPsxOwner.cpp", "StationPsxOwner.hpp", "StationPsxProtocol.cpp",
                 "StationPsxProtocol.hpp", "StationPsxSha256.cpp", "PsxPinnedOptions.h"):
        need(sha(inherited.PSX / "native" / name) == previous["psx"]["productiveTransforms"].get("native/" + name),
             "Retained PSX productive source changed: " + name)
    native_tools = inherited.native_tools(a.ndk)
    out = isolated(a.out)
    out.mkdir(parents=True)
    markers = {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
    need(inherited.policy(psx) == inherited.policy(previous["psx"]), "Original PSX owner policy changed")
    raw = canonical(psx)
    (out / "psx.fingerprint.json").write_bytes(raw + b"\n")
    identity_source = out / "StationPsxIdentity.cpp"
    identity_source.write_text(
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n',
        encoding="ascii")
    native_out = out / "native"
    subprocess.run([sys.executable, "-B", str(inherited.PSX / "recipe/build_entry.py"), "--ndk", str(a.ndk),
                    "--owner", str(inherited.PSX / "native"), "--protocol", str(inherited.PSX / "native"),
                    "--pinned-options", str(inherited.PSX / "native"), "--identity-source", str(identity_source), "--out", str(native_out)],
                   check=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    psx_binary = native_out / WRAPPERS["psx"][0]
    need(raw in psx_binary.read_bytes(), "Canonical PSX identity embedding failed")
    markers["psx"] = dict(runtimeLibrary=psx_binary.name, runtimeSha256=sha(psx_binary),
                          runtimeBytes=psx_binary.stat().st_size, fingerprintSha256=digest(raw))
    primitive = module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r144_visual_marker")
    for kind in ("n64", "dolphin"):
        value = copy.deepcopy(previous[kind])
        library, parent_runtime = WRAPPERS[kind]
        value.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms,
                     parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_runtime,
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        need(inherited.policy(value) == inherited.policy(previous[kind]), "Independent owner policy changed: " + kind)
        (out / (library + ".fingerprint.json")).write_bytes(canonical(value) + b"\n")
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, a.ndk, out)
    files = {"lib/arm64-v8a/" + library: (out / "native" / library if kind == "psx" else out / library)
             for kind, (library, _) in WRAPPERS.items()}
    with zipfile.ZipFile(a.base) as archive:
        updated, selected = validate_marker_bindings(archive, previous, payload, pins, markers, files)
    retro = [row for row in original["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(original["engines"]) == len(updated["engines"]) == 13 and len(retro) == 9 and
         [row for row in updated["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
         "All nine RetroArch descriptors and their eight active IDs must stay exact")
    (out / "engines.json").write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(inherited.native_tools(a.ndk) == native_tools and verify_commit(a.source_commit) == pins and
         read(a.dex_receipt) == dex and read(a.native_receipt) == native_receipt and
         sha(a.dex) == payload[PARTITION] and sha(a.native) == payload[CAROUSEL],
         "Frozen R144 source, qualified payload receipts or native tools changed during marker build")
    receipt = dict(schema="station.r144.wave-palette.identity.v1", passed=True, compiled=True, sourceCommit=a.source_commit,
        sourceFiles=pins, nativeToolFiles=native_tools, retainedIdentityDependencies=DEPENDENCIES,
        baselineApkSha256=BASE, dexSha256=sha(a.dex), carouselSha256=sha(a.native), payloadSha256=payload,
        markers=markers, engines=selected, enginesAssetSha256=sha(out / "engines.json"),
        preservedRetroArchSha256=RETRO, preservedRetroArchDescriptors=retro, preservedDex35Sha256=PRESERVED_DEX35,
        dexBuildReceiptSha256=sha(a.dex_receipt), nativeBuildReceiptSha256=sha(a.native_receipt),
        inheritedPayloadCount=345, finalPayloadCount=345, changedPayloadEntries=sorted({PARTITION, CAROUSEL}), **state_fields())
    (out / "runtime-identity.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "dex", "dex-receipt", "native", "native-receipt", "ndk", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    result = build(parser.parse_args())
    print(json.dumps({"revision": "R144", "renewedIndependentIds": len(result["engines"]), "preservedRetroArchDescriptors": 9}))
