"""Bind the four R145 visual payloads to the original independent owner policies."""
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
from common import *
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
    result = module(REPO / next(iter(DEPENDENCIES)), "r145_visual_inherited")
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



def validate_dex_receipt(receipt, directory, commit, pins):
    plan = read(ROOT / "evidence/java-background-scope.json")
    need(plan.get("schema") == "station.r145.sky-blue.background.scope.v1" and
         plan.get("baselineApkSha256") == BASE and plan.get("onlyLiteralReplacement") is True and
         plan.get("wholeClassSmaliSourceInversePassed") is True and plan.get("postassemblyMustRecoverExactDonor") is True and
         plan.get("noNewFields") is plan.get("noNewMethods") is plan.get("noNewClasses") is True and
         plan.get("networkAndGameplayChanges") is False and plan.get("changedConstantCount") == 10 and
         set(plan.get("partitions", {})) == PARTITIONS,
         "Closed reviewed ten-constant R145 visual plan required")
    need(receipt.get("schema") == "station.r145.sky-blue-waves.dex.v1" and
         receipt.get("passed") is True and receipt.get("compiled") is True and
         receipt.get("sourceCommit") == commit and receipt.get("sourceFiles") == pins and
         receipt.get("baselineApkSha256") == BASE and
         receipt.get("scopeDeclarationSha256") == sha(ROOT / "evidence/java-background-scope.json") and
         receipt.get("productionMethodStrategy") == "donor-smali-literals-only" and
         set(receipt.get("payloads", {})) == set(receipt.get("scopes", {})) == PARTITIONS and
         set(receipt.get("preservedDexSha256", {})) == ROOT_DEX - PARTITIONS and
         receipt.get("inversePassed") is True and receipt.get("unrelatedMethodsPreserved") is True and
         receipt.get("gameplayAndNetworkLogicPreserved") is True and receipt.get("newFields") == receipt.get("newMethods") == receipt.get("newClasses") == [],
         "Qualified three-partition literal-only assembly and exact 37 retained DEX proofs required")
    paths = {}
    total_classes = 0
    for partition in sorted(PARTITIONS):
        wanted, scope, artifact = plan["partitions"][partition], receipt["scopes"][partition], receipt["payloads"][partition]
        path = Path(directory) / partition
        need(path.is_file() and not path.is_symlink() and Path(artifact.get("path", "")).resolve() == path.resolve() and
             artifact.get("sha256") == sha(path) != DEX_BASE[partition] and artifact.get("bytes") == path.stat().st_size,
             "Exact assembled scoped DEX payload required: " + partition)
        count = {"classes28.dex": 272, "classes35.dex": 608, "classes40.dex": 129}[partition]
        changed = set(wanted["modifiedClasses"])
        need(wanted["classCount"] == count and wanted["donorDexSha256"] == DEX_BASE[partition] and
             len(changed) == {"classes28.dex": 3, "classes35.dex": 2, "classes40.dex": 2}[partition] and
             scope.get("baselineDexSha256") == DEX_BASE[partition] and scope.get("outputDexSha256") == sha(path) and
             scope.get("originalClassCount") == scope.get("finalClassCount") == count and
             scope.get("modifiedClasses") == wanted["modifiedClasses"] and scope.get("modifiedMethods") == wanted["modifiedMethods"] and
             scope.get("constantChanges") == wanted["constantChanges"] and scope.get("unchangedClasses") == count - len(changed) and
             scope.get("methodBaselineSha256") == wanted["methodBaselineSha256"] and
             scope.get("methodInverseSha256") == wanted["methodBaselineSha256"] and
             scope.get("inverseClassSha256") == wanted["baselineClassSha256"] and
             scope.get("onlyLiteralReplacement") is True and scope.get("inverseWholeClassPassed") is True and
             scope.get("postassemblyInversePassed") is True and scope.get("unrelatedClassesByteIdentical") is True and
             scope.get("unrelatedMethodsPreserved") is True and scope.get("staticInitializersPreserved") is True and
             scope.get("addedClasses") == scope.get("removedClasses") == scope.get("addedMethods") == scope.get("removedMethods") == [],
             "Actual complete-class and method/literal inverse proof required: " + partition)
        before, after, retained = (scope.get(name, {}) for name in
                                  ("baselineClassSha256", "outputClassSha256", "unchangedClassSha256"))
        need(before == wanted["originalClassSha256"] and len(before) == len(after) == count and
             set(before) == set(after) and set(retained) == set(before) - changed and
             {kind: before[kind] for kind in retained} == {kind: after[kind] for kind in retained} == retained and
             {kind: after[kind] for kind in changed} == wanted["plannedOutputClassSha256"] and
             {kind for kind in before if before[kind] != after[kind]} == changed,
             "Frozen seven-class canonical projections must contain no other difference: " + partition)
        paths[partition] = path
        total_classes += count
    need(total_classes == 1009, "All 1,009 classes in changed partitions must be accounted for")
    return receipt, paths


def validate_native_receipt(receipt, path, commit, pins):
    source = module(ROOT / "recipe/build_native.py", "r145_native_contract")
    native_pins = source.source_map()
    need(set(native_pins) == {"native/native_space.h", "native/station_wave_palette.h", "native/station_theme_palette.h", "recipe/build_native.py"} and
         all(pins.get(name) == checksum for name, checksum in native_pins.items()),
         "Three frozen visual headers and native recipe must share the R145 source commit")
    payload = receipt.get("payloads", {}).get(CAROUSEL, {})
    proof = receipt.get("transforms", {}).get("native", {})
    input_map = receipt.get("retainedInputSha256", {})
    need(receipt.get("schema") == "station.r145.native.sky-blue-bands.v1" and receipt.get("revision") == "R145" and
         receipt.get("passed") is True and receipt.get("compiled") is True and receipt.get("sourceCommit") == commit and
         receipt.get("sourceSha256") == native_pins and receipt.get("baseApkSha256") == BASE and
         receipt.get("baselineNativeSha256") == CAROUSEL_SHA and receipt.get("baselineReproduced") == {"r144Carousel": True} and
         receipt.get("retainedParentNativeReceiptSha256") == PARENT_NATIVE_RECEIPT_SHA and
         receipt.get("retainedParentFinalProofSha256") == PARENT_FINAL_PROOF_SHA and
         len(input_map) == 158 and digest(canonical(input_map)) == PARENT_NATIVE_INPUT_MAP_SHA and
         receipt.get("scopeDeclarationSha256") == sha(ROOT / "evidence/native-visual-scope.json") and
         receipt.get("paletteSpecSha256") == sha(ROOT / "evidence/native-palette-spec.json") and
         receipt.get("dexChanged") is False and receipt.get("frontendChanged") is False and
         receipt.get("exportsExactlyPreserved") is True and receipt.get("dependenciesExactlyPreserved") is True and
         receipt.get("sonameExactlyPreserved") is True and receipt.get("nativeLoadAlignment") == "0x4000" and
         set(receipt.get("payloads", {})) == {CAROUSEL} and payload.get("sha256") == sha(path) != CAROUSEL_SHA and
         payload.get("bytes") == Path(path).stat().st_size and Path(payload.get("path", "")).resolve() == Path(path).resolve() and
         receipt.get("outputNativeSha256") == sha(path) and
         set(proof) == {"wholeHeaderInversePassed", "drawNativeSpaceByteIdentical", "diagonalBackdropByteIdentical",
                        "waveCurveTimingEquationByteIdentical", "unrequestedPalettesCountsWidthsPreserved",
                        "requestedPaletteSpecVerified", "onlyApprovedNativeVisualBlocksChanged"} and
         all(value is True for value in proof.values()),
         "Exact reproduced R144 and its 158 retained inputs plus closed authorized native visual inverse required")
    elf_contract(Path(path).read_bytes())
    return receipt


def expected_payload(previous, dex_paths, native_path):
    old = previous["psx"]["payloadSha256"]
    need(len(old) == 345 and old.get(CAROUSEL) == CAROUSEL_SHA and
         all(old.get(name) == checksum for name, checksum in DEX_BASE.items()), "Exact complete R144 inherited payload required")
    result = {**old, **{name: sha(path) for name, path in dex_paths.items()}, CAROUSEL: sha(native_path)}
    need(set(dex_paths) == PARTITIONS and len(result) == 345 and
         {name for name in old if old[name] != result[name]} == CHANGED_PAYLOAD,
         "Only three literal-scoped DEXes and native carousel may change in the complete marker payload")
    return result

def transforms_for(previous, pins):
    old = previous["psx"]["productiveTransforms"]
    extra = {ROOT.name + "/" + name: checksum for name, checksum in pins.items()}
    need(not set(old).intersection(extra), "R145 source chain must append without overwriting history")
    return {**old, **extra}


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
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R144 donor required")
    pins = verify_commit(a.source_commit)
    dex, dex_paths = validate_dex_receipt(read(a.dex_receipt), a.dex_dir, a.source_commit, pins)
    native_receipt = validate_native_receipt(read(a.native_receipt), a.native, a.source_commit, pins)
    with zipfile.ZipFile(a.base) as archive:
        previous = fingerprints(archive)
        need(entry_sha(archive, "lib/arm64-v8a/libstation_retroarch.so") == RETRO and
             all(entry_sha(archive, name) == checksum for name, checksum in DEX_BASE.items()) and
             entry_sha(archive, CAROUSEL) == CAROUSEL_SHA, "Actual R144 runtime and visual donor identity required")
        original = json.loads(archive.read("assets/station-online/engines.json"))
        for name, checksum in previous["psx"]["payloadSha256"].items():
            need(entry_sha(archive, name) == checksum, "Inherited payload differs: " + name)
        need({name: entry_sha(archive, name) for name in ROOT_DEX - PARTITIONS} == dex["preservedDexSha256"],
             "All 37 unrelated DEX partitions must remain exact")
        old_contract, new_contract = elf_contract(archive.read(CAROUSEL)), elf_contract(a.native.read_bytes())
        need(old_contract["exports"] == new_contract["exports"] and old_contract["needed"] == new_contract["needed"] and
             old_contract["soname"] == new_contract["soname"] == ["libturbo_carousel.so"],
             "Carousel native API, dependencies or SONAME changed")
    payload = expected_payload(previous, dex_paths, a.native)
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
    primitive = module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r145_visual_marker")
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
         all(sha(path) == payload[name] for name, path in dex_paths.items()) and sha(a.native) == payload[CAROUSEL],
         "Frozen visual sources, receipts, payloads or native tools changed during marker build")
    receipt = dict(schema="station.r145.sky-blue-waves.identity.v1", passed=True, compiled=True, sourceCommit=a.source_commit,
        sourceFiles=pins, nativeToolFiles=native_tools, retainedIdentityDependencies=DEPENDENCIES, baselineApkSha256=BASE,
        changedDexSha256={name: sha(path) for name, path in dex_paths.items()}, carouselSha256=sha(a.native), payloadSha256=payload,
        markers=markers, engines=selected, enginesAssetSha256=sha(out / "engines.json"),
        preservedRetroArchSha256=RETRO, preservedRetroArchDescriptors=retro, preservedDexSha256=dex["preservedDexSha256"],
        dexBuildReceiptSha256=sha(a.dex_receipt), nativeBuildReceiptSha256=sha(a.native_receipt),
        javaScopeDeclarationSha256=sha(ROOT / "evidence/java-background-scope.json"),
        nativeScopeDeclarationSha256=sha(ROOT / "evidence/native-visual-scope.json"),
        inheritedPayloadCount=345, finalPayloadCount=345, changedPayloadEntries=sorted(CHANGED_PAYLOAD), **state_fields())
    (out / "runtime-identity.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "dex-dir", "dex-receipt", "native", "native-receipt", "ndk", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    result = build(parser.parse_args())
    print(json.dumps({"revision": "R145", "renewedIndependentIds": len(result["engines"]), "preservedRetroArchDescriptors": 9}))
