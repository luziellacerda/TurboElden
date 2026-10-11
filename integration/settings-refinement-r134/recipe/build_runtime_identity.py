"""Renew four identities for scoped settings DEX28/40 and two native labels.

Every other DEX, frontend, core, option, controller, transport, media and
renderer byte remains pinned to R133. PSX uses the retained entry builder;
N64/Dolphin use the retained marker builders. No signing or device operation.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
import subprocess
import zipfile
from common import *

PSX = ROOT.parent / "psx-online"
PREFIX = "lib/arm64-v8a/"
PARENT_RECEIPT_SHA = "d1eb9bfe78be4c513daedde1ff1f624f653b5353db5a64b8a07d9df213dfb34e"
PARENT_ENGINES_SHA = "9d76d080439fed3f9aa36ff59b7e5f15c2761cb4e426779c9b5fa85215e98b6f"
PARENT_PAYLOAD_COUNT = 345
MARKERS = {
    "psx": ("libstation_psx_online.so", "42e4ca5f2acc86f7b9c15584bb0f583b9fe07d24c88f955eebd0bcbde30f03d4", "fe69918e5b3fd3f7b4c6dd7e86f677c1a502a3dc918ef2507ded4b0899a49b58"),
    "n64": ("libstation_mupen64plus_runtime.so", "6dd47d4e00923f27e71523cdfa6c9d3d37d45f0d5ab9cb00225acbfeed45987b", "8008a3e872504c535ad9daf4c2513c73cd6d0c49564f035196e7ef8766f67499"),
    "dolphin": ("libstation_dolphin_runtime.so", "5912af1feeef31abd75095b169b919a6737637c6d070a6b7f69cdfccf5f74737", "ffd551fe70b6e70d94ae9f0842e8514d20d13d1e7201be004e30b84aad90d888"),
}
PAYLOADS = frozenset({"classes28.dex", "classes40.dex", PREFIX + "libturbo_carousel.so"})
DEX = frozenset(["classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]])
PRESERVED_DEX = DEX - PAYLOADS
SCOPES = ["graphics-settings-grouped-pages", "sony-emulator-settings-and-return", "native-sony-settings-action-labels"]
BASELINE_PAYLOADS = {
    "classes28.dex": "62d74741c096e0280133b4cb7b37f4b9c4b25bade682be44dae734f2554140e0",
    "classes40.dex": "f3dddbea9c8fcb80e3ecc6f6a255fe5b77a2f3572d4fdf657e31a4ebd6576a10",
    PREFIX + "libturbo_carousel.so": CAROUSEL_SHA,
}
FAMILIES = {
    "classes28.dex": ["Lorg/emulationstation/frontend/station/StationGraphicsPanel;"],
    "classes40.dex": ["Lorg/emulationstation/frontend/sony/Ps3Activity;", "Lorg/emulationstation/frontend/sony/Ps4Activity;"],
}
DEPENDENCY_SOURCES = {
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
    "versions/station-mupen-online-r125-20261011/recipes/build_runtime_identity.py": "fdb79db3e354f3359d00980a1a00e7dec9d5fcbfed27892d4c42fbd4af1b2a16",
    "integration/console-panel-r133/recipe/common.py": "c680a8e148b00e1dd3f0d2f690a6f0c3868e18c3659005b63debd6ba133cd5f7",
    "integration/console-panel-r133/recipe/build_runtime_identity.py": "a1e79bd9dd1498c1ad2dae95b48ccaf307495b2f51e9017c7624f0dd75bd37d9",
}


def archive_sha(archive, name):
    import hashlib
    value = hashlib.sha256()
    with archive.open(name) as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(part)
    return value.hexdigest()


def verify_dependencies():
    for name, expected in DEPENDENCY_SOURCES.items():
        require(sha(REPO / name) == expected, "Pinned identity primitive changed: " + name)


def belongs(value, families):
    return any(value == family or value.startswith(family[:-1] + "$") for family in families)


def dex_scope(name, scope):
    """Validate the complete before/after projection, not just class counts."""
    families = FAMILIES[name]
    require(scope.get("partition") == name and scope.get("baselineDexSha256") == BASELINE_PAYLOADS[name] and
            scope.get("allowedFamilyRoots") == families and scope.get("allowedFamilies") == families,
            "Exact owner-family scope required: " + name)
    before, after, outside = (scope.get(k) for k in ("baselineClassSha256", "outputClassSha256", "unchangedClassSha256"))
    require(all(isinstance(m, dict) and m for m in (before, after, outside)) and
            all(isinstance(t, str) and t.startswith("L") and t.endswith(";") and
                isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h)
                for m in (before, after, outside) for t, h in m.items()), "Complete class hashes required")
    original_allowed = {t for t in before if belongs(t, families)}
    final_allowed = {t for t in after if belongs(t, families)}
    require(set(families) <= original_allowed and set(families) <= final_allowed and
            scope.get("originalAllowedTypes") == sorted(original_allowed) and
            scope.get("finalAllowedTypes") == sorted(final_allowed) and
            set(before) - original_allowed == set(after) - final_allowed == set(outside) and
            {t: before[t] for t in outside} == {t: after[t] for t in outside} == outside,
            "Unrelated classes changed or family declaration incomplete: " + name)
    require(scope.get("addedTypes") == sorted(final_allowed - original_allowed) and
            scope.get("removedTypes") == sorted(original_allowed - final_allowed) and
            scope.get("modifiedTypes") == sorted(t for t in original_allowed & final_allowed if before[t] != after[t]) and
            scope.get("originalClassCount") == len(before) and scope.get("finalClassCount") == len(after) and
            scope.get("unchangedClasses") == len(outside) and
            scope.get("unrelatedClassProjectionSha256") == outside and
            scope.get("unrelatedProjectionCanonicalSha256") == digest(canonical(outside)),
            "Exact scoped class delta differs: " + name)
    require(all(scope.get(flag) is True for flag in ("unrelatedClassesByteIdentical", "classDeltaRestrictedToAllowedFamilies",
                                                  "staticInitializersPreserved")) and
            type(scope.get("restoredInitializerArrays")) is int and scope["restoredInitializerArrays"] >= 0 and
            isinstance(scope.get("scopeDeclarationSha256"), str) and re.fullmatch(r"[0-9a-f]{64}", scope["scopeDeclarationSha256"]),
            "Assembler/static initializer guards missing: " + name)


def payload_inputs(path, commit, pins):
    receipt = read(path)
    require(receipt.get("schema") == "station.settings.refinement.payloads.v1" and receipt.get("passed") is True and
            receipt.get("revision") == "R134" and receipt.get("baseApkSha256") == BASE_SHA and
            receipt.get("baseApkBytes") == BASE_BYTES and receipt.get("baselinePayloadSha256") == BASELINE_PAYLOADS and
            receipt.get("sourceCommit") == commit and receipt.get("sourceSha256") == pins and
            receipt.get("sourceCanonicalSha256") == digest(canonical(pins)) and receipt.get("approvedScopes") == SCOPES and
            set(receipt.get("payloads", {})) == PAYLOADS and set(receipt.get("dexScopes", {})) == set(FAMILIES) and
            set(receipt.get("preservedDexSha256", {})) == PRESERVED_DEX and
            all(receipt.get(flag) is True for flag in ("classDeltaRestrictedToAllowedFamilies", "unrelatedClassesByteIdentical",
                "labelPatchInversePassed", "allOtherNativeBytesIdentical", "original16KiBAlignmentPreserved")) and
            receipt.get("javaApiPolicy") == "android-sdk-bootclasspath-only" and
            all(receipt.get(flag) is False for flag in ("compileOnlyClassesPackaged", "compilerLambdaStubsPackaged",
                                                      "apkAssembled", "signed", "installed", "physicalGameplayValidated")),
            "Exact reviewed R134 three-payload compilation receipt required")
    java = module(ROOT / "recipe/build_java_payloads.py", "r134_scoped_java_contract")
    labels = module(ROOT / "recipe/patch_settings_labels.py", "r134_native_label_contract")
    require(receipt.get("inputSha256") == {**java.PINS, **java.JDK_PINS} and
            set(receipt.get("inputFiles", {})) == set(receipt["inputSha256"]), "Complete pinned Android compile inputs required")
    for name, record in receipt["inputFiles"].items():
        checked_file(record, name)
        require(record["sha256"] == receipt["inputSha256"][name], "Compile input path/hash seal differs: " + name)
    compiled_path = checked_file(receipt["javaReceipt"], "Java receipt")
    labels_path = checked_file(receipt["labelsReceipt"], "Label receipt")
    compiled, patched = read(compiled_path), read(labels_path)
    require(compiled.get("schema") == "station.settings.refinement.java.r134.v1" and compiled.get("revision") == "R134" and
            compiled.get("passed") is True and compiled.get("baselineApkSha256") == BASE_SHA and
            compiled.get("baselineApkBytes") == BASE_BYTES and
            compiled.get("sourceCommit") == commit and compiled.get("sourceSha256") == pins and
            compiled.get("sourceCanonicalSha256") == digest(canonical(pins)) and
            compiled.get("preservedDexSha256") == receipt["preservedDexSha256"] and
            compiled.get("inputSha256") == receipt["inputSha256"] and compiled.get("inputFiles") == receipt["inputFiles"] and
            compiled.get("changedDexPartitions") == list(FAMILIES) and
            compiled.get("javaApiPolicy") == "android-sdk-bootclasspath-only" and
            compiled.get("classDeltaRestrictedToAllowedFamilies") is True and compiled.get("unrelatedClassesByteIdentical") is True and
            compiled.get("compileOnlyClassesPackaged") is False and compiled.get("compilerLambdaStubsPackaged") is False,
            "Java compilation binding differs")
    compiled_scopes = {row["partition"]: {k: v for k, v in row.items() if k != "payload"} for row in compiled["partitions"]}
    require(len(compiled["partitions"]) == len(FAMILIES) and compiled_scopes == receipt["dexScopes"],
            "Original Java scope receipt differs from aggregate")
    payloads = {name: checked_file(record, name) for name, record in receipt["payloads"].items()}
    for name, scope in receipt["dexScopes"].items():
        dex_scope(name, scope)
        require(payloads[name].name == name, "Conventional DEX payload path required")
        require(java.class_count(payloads[name].read_bytes()) == scope["finalClassCount"], "Actual DEX class count differs")
        original = next(row for row in compiled["partitions"] if row["partition"] == name)
        require({k: original["payload"][k] for k in ("path", "bytes", "sha256")} == receipt["payloads"][name],
                "Compiled DEX artifact differs from aggregate")
    native_name = PREFIX + "libturbo_carousel.so"
    native = payloads[native_name].read_bytes()
    require(patched.get("schema") == "station.settings.labels.r134.v1" and patched.get("passed") is True and
            patched.get("baselineCarouselSha256") == CAROUSEL_SHA and patched.get("payloadSha256") == digest(native) and
            patched.get("payloadBytes") == len(native) and len(patched.get("changedLabels", [])) == 2 and
            all(patched.get(flag) is True for flag in ("exactInversePassed", "allOtherBytesIdentical", "equalSizeReplacements",
                "elfHeaderPreserved", "original16KiBAlignmentPreserved", "artAndShadersByteIdentical")) and
            {k: patched["payload"][k] for k in ("path", "bytes", "sha256")} == receipt["payloads"][native_name],
            "Exact two-label native receipt differs")
    inverse = bytearray(native)
    for row, (old, new) in zip(patched["changedLabels"], labels.LABELS):
        at = row["offset"]
        require(type(at) is int and at >= 0 and row["bytes"] == 22 and row["fromText"] == old and row["toText"] == new and
                row.get("fromSha256") == digest(old.encode("utf-8")) and row.get("toSha256") == digest(new.encode("utf-8")) and
                native[at:at + 22] == new.encode("utf-8"), "Actual native label offset differs")
        inverse[at:at + 22] = old.encode("utf-8")
    require(digest(inverse) == CAROUSEL_SHA, "Exact whole-native inverse differs from R133")
    replay, _ = labels.patch(bytes(inverse))
    require(replay == native, "Independent native two-label replay differs")
    return receipt, payloads


# Compatibility name for tooling; this receipt explicitly covers Java and labels.
native_inputs = payload_inputs


def parent_inputs(base, directory):
    """Check all 345 parent payloads, embedded fingerprints and real cores/deps."""
    require(Path(base).stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
            "Exact signed R133 donor required")
    directory = Path(directory).resolve(strict=True)
    receipt_path = directory / "runtime-identity.json"
    parent = read(receipt_path)
    require(sha(receipt_path) == PARENT_RECEIPT_SHA and parent.get("revision") == "R133" and
            parent.get("sourceCommit") == BASE_SOURCE and set(parent.get("markers", {})) == set(MARKERS) and
            len(parent.get("payloadSha256", {})) == PARENT_PAYLOAD_COUNT and
            parent.get("ps3Ps4OfflineOnly") is True and parent.get("ps3Ps4OnlineEnabled") is False,
            "Exact original R133 identity receipt required")
    fingerprints = {}
    with zipfile.ZipFile(base) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and
                {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} == DEX,
                "Unique exact 40-DEX R133 archive required")
        for name, expected in parent["payloadSha256"].items():
            require(archive_sha(archive, name) == expected, "Actual parent payload differs: " + name)
        require(all(parent["payloadSha256"].get(name) == expected for name, expected in BASELINE_PAYLOADS.items()) and
                parent["payloadSha256"].get(PREFIX + "libstation_frontend.so") == FRONTEND_SHA,
                "Actual parent scoped DEX/carousel/frontend payload differs")
        raw_engines = archive.read("assets/station-online/engines.json")
        require(digest(raw_engines) == PARENT_ENGINES_SHA and sha(directory / "engines.json") == PARENT_ENGINES_SHA,
                "Parent engine asset differs from actual R133")
        engines = json.loads(raw_engines)
        current = [row for row in engines["engines"] if row["platform"] in {"psx", "n64", "gamecube", "wii"}]
        require(current == parent["engines"] and len(current) == 4 and
                {row["platform"] for row in current} == {"psx", "n64", "gamecube", "wii"},
                "Exact four parent engines required")
        for kind, (library, runtime_hash, fingerprint_hash) in MARKERS.items():
            filename = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
            raw = (directory / filename).read_bytes().rstrip(b"\r\n")
            value = json.loads(raw)
            binary = archive.read(PREFIX + library)
            require(raw == canonical(value) and digest(raw) == fingerprint_hash and raw in binary and
                    digest(binary) == runtime_hash and parent["markers"][kind]["runtimeSha256"] == runtime_hash and
                    parent["markers"][kind]["fingerprintSha256"] == fingerprint_hash and
                    value.get("payloadSha256") == parent["payloadSha256"],
                    "Actual R133 marker/fingerprint/payload binding differs: " + kind)
            for field in ("dependencySha256", "compiledBackendSha256"):
                for name, expected in value.get(field, {}).items():
                    require(archive_sha(archive, PREFIX + name) == expected,
                            "Actual parent dependency/core differs: " + name)
            fingerprints[kind] = value
        for entry in current:
            require(archive_sha(archive, PREFIX + entry["library"]) == entry["coreSha256"],
                    "Actual parent core differs: " + entry["platform"])
            for name, expected in entry["dependencySha256"].items():
                require(archive_sha(archive, PREFIX + name) == expected, "Actual engine dependency differs: " + name)
        profile = (directory / "psx-controller-profile.json").read_bytes().rstrip(b"\r\n")
        require(digest(profile) == parent["psxControllerProfileSha256"], "Exact parent PSX controller profile required")
    first = fingerprints["psx"]
    require(all(value["javaSources"] == first["javaSources"] and
                value["productiveTransforms"] == first["productiveTransforms"] for value in fingerprints.values()),
            "Parent effective source maps disagree")
    for name in ("StationPsxEntry.cpp", "StationPsxOwner.cpp", "StationPsxOwner.hpp", "StationPsxProtocol.cpp",
                 "StationPsxProtocol.hpp", "StationPsxSha256.cpp", "PsxPinnedOptions.h"):
        require(sha(PSX / "native" / name) == first["productiveTransforms"].get("native/" + name),
                "Pinned PSX native source changed: " + name)
    bridge = PSX / "java/org/emulationstation/frontend/netplay/StationPsxBridge.java"
    require(sha(bridge) == first["javaSources"].get("netplay-src/org/emulationstation/frontend/netplay/StationPsxBridge.java"),
            "Pinned PSX JNI declaration source changed")
    return parent, fingerprints, engines, profile, dict(parent["payloadSha256"])


def import_markers():
    return module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py",
                  "r134_retained_identity_primitives")


def policy(row):
    result = copy.deepcopy(row)
    for key in ("baseApkSha256", "payloadSha256", "productiveTransforms", "parentFingerprintSha256",
                "parentRuntimeSha256", "psxRuntimeSha256"):
        result.pop(key, None)
    return result


def transforms_for(previous, pins):
    additional = {"settings-refinement-r134/" + name: value for name, value in pins.items()}
    require(not set(additional).intersection(previous["psx"]["productiveTransforms"]),
            "R134 productive transforms must only append to original parent maps")
    return {**previous["psx"]["productiveTransforms"], **additional}


def expected_engines(original, markers):
    updated = copy.deepcopy(original)
    selected = []
    for before, after in zip(original["engines"], updated["engines"]):
        platform = after["platform"]
        if platform not in {"psx", "n64", "gamecube", "wii"}:
            continue
        kind = "dolphin" if platform in {"gamecube", "wii"} else platform
        marker = markers[kind]
        prefix = ("pcsx-rearmed-ff81ed17-player-v3-" if kind == "psx" else
                  "mupen64plus-ae-33bf7021-n64-v3-" if kind == "n64" else
                  "dolphin-5102a033-" + platform + "-v3-")
        after.update(engineId=prefix + marker["runtimeSha256"][:12], runtimeSha256=marker["runtimeSha256"])
        strip = lambda row: {key: value for key, value in row.items() if key not in {"engineId", "runtimeSha256"}}
        require(strip(before) == strip(after) and before["engineId"] != after["engineId"],
                "Only four existing identity IDs/hashes may change: " + platform)
        selected.append(after)
    require(len(selected) == 4 and {row["platform"] for row in selected} == {"psx", "n64", "gamecube", "wii"},
            "Exactly four existing online identities required")
    return updated, selected


def validate_inputs(base, identity_path):
    """Read-only preflight; conventional paths and every donor binding rechecked."""
    identity_path = Path(identity_path)
    directory = identity_path.parent
    receipt = read(identity_path)
    pins = source_map()
    require(receipt.get("schemaVersion") == 3 and receipt.get("revision") == "R134" and
            receipt.get("baseApkSha256") == BASE_SHA and receipt.get("retainedBaseSourceCommit") == BASE_SOURCE and
            receipt.get("sourceSha256") == pins and receipt.get("parentIdentityReceiptSha256") == PARENT_RECEIPT_SHA and
            receipt.get("dependencySourceSha256") == DEPENDENCY_SOURCES and receipt.get("approvedScopes") == SCOPES and
            receipt.get("registeredOnServer") is False and receipt.get("installed") is False and
            receipt.get("physicalGameplayValidated") is False, "Exact uninstalled R134 settings-only identity receipt required")
    verify_source_commit(receipt["sourceCommit"], pins)
    verify_dependencies()
    native_path = Path(receipt["nativeReceiptPath"])
    require(receipt.get("payloadReceiptPath") == receipt["nativeReceiptPath"] and
            receipt.get("payloadReceiptSha256") == receipt["nativeReceiptSha256"] and
            receipt.get("compilationReceiptSchema") == "station.settings.refinement.payloads.v1" and
            sha(native_path) == receipt["nativeReceiptSha256"], "Combined payload receipt changed after fingerprinting")
    native, payloads = native_inputs(native_path, receipt["sourceCommit"], pins)
    parent_path = Path(receipt["parentIdentityReceiptPath"])
    require(parent_path.name == "runtime-identity.json" and sha(parent_path) == PARENT_RECEIPT_SHA,
            "Exact original R133 parent receipt path required")
    parent, previous, original, profile, inherited = parent_inputs(base, parent_path.parent)
    actual = {**inherited, **{name: sha(path) for name, path in payloads.items()}}
    require(actual != inherited and actual == receipt["payloadSha256"] and
            receipt["newSharedPayloadSha256"] == {name: actual[name] for name in PAYLOADS} and
            receipt["preservedR133PayloadSha256"] == {name: value for name, value in inherited.items() if name not in PAYLOADS} and
            native["preservedDexSha256"] == {name: inherited[name] for name in PRESERVED_DEX},
            "Final scoped payloads or preserved full parent payload map changed")
    transforms = {"dexScopes": native["dexScopes"], "nativeLabels": read(native["labelsReceipt"]["path"])["changedLabels"]}
    compilation_paths = {"payload-receipt": str(native_path.resolve()),
                         "java-receipt": native["javaReceipt"]["path"], "labels-receipt": native["labelsReceipt"]["path"]}
    compilation_hashes = {"payload-receipt": sha(native_path), "java-receipt": native["javaReceipt"]["sha256"],
                          "labels-receipt": native["labelsReceipt"]["sha256"]}
    require(receipt.get("nativeInputSha256") == native["inputSha256"] and
            receipt.get("payloadInputSha256") == native["inputSha256"] and
            receipt.get("nativeTransforms") == transforms and receipt.get("payloadTransforms") == transforms and
            receipt.get("dexScopes") == native["dexScopes"] and
            receipt.get("compilationReceiptSha256") == compilation_hashes and
            receipt.get("compilationReceiptPaths") == compilation_paths,
            "Private scoped inputs/transforms or compilation references changed")
    require(receipt.get("parentRuntimeMarkers") == parent["markers"] and set(receipt.get("markers", {})) == set(MARKERS),
            "Parent/new marker sets differ")
    transforms = transforms_for(previous, pins)
    manifest = dict(actual)
    for kind, (library, old_runtime, old_fingerprint) in MARKERS.items():
        filename = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
        raw = (directory / filename).read_bytes().rstrip(b"\r\n")
        value = json.loads(raw)
        expected = copy.deepcopy(previous[kind])
        expected.update(baseApkSha256=BASE_SHA, payloadSha256=actual, productiveTransforms=transforms)
        if kind != "psx":
            expected.update(parentFingerprintSha256=old_fingerprint, parentRuntimeSha256=old_runtime,
                            psxRuntimeSha256=receipt["markers"]["psx"]["runtimeSha256"])
        binary = directory / "native" / library if kind == "psx" else directory / library
        marker = receipt["markers"][kind]
        actual_binary = checked_file({"path": str(binary), "bytes": marker["runtimeBytes"],
                                      "sha256": marker["runtimeSha256"]}, library)
        require(raw == canonical(expected) and value == expected and raw in actual_binary.read_bytes() and
                marker["runtimeLibrary"] == library and digest(raw) == marker["fingerprintSha256"] and
                marker["runtimeSha256"] != old_runtime and policy(previous[kind]) == policy(value),
                "New exact marker/fingerprint or retained policy differs: " + kind)
        manifest[PREFIX + library] = marker["runtimeSha256"]
    updated, selected = expected_engines(original, receipt["markers"])
    engines = directory / "engines.json"
    require(read(engines) == updated and receipt["engines"] == selected and
            sha(engines) == receipt["enginesAssetSha256"] and engines.stat().st_size <= 32768 and
            (directory / "psx-controller-profile.json").read_bytes() == profile + b"\n" and
            receipt["psxControllerProfileSha256"] == parent["psxControllerProfileSha256"] and
            receipt["psxOptionsSha256"] == parent["psxOptionsSha256"],
            "Exact new engines/unchanged options or controller profile differs")
    for flag in ("existing38DexByteIdentical", "dexScopedClassesVerified", "frontendLibraryByteIdentical",
                 "manifestByteIdentical", "resourcesAndSonyAssetsByteIdentical", "shaderCodeAndEffectsPreserved",
                 "videoBytesAndLoopPolicyPreserved", "n64DolphinCoreAndOptionsUnchanged", "snesMegadriveEntriesUnchanged",
                 "controllerProfilesUnchanged", "protocolAndTransportUnchanged", "ps3Ps4OfflineOnly",
                 "nativeEmulatorEntriesPreserved", "menuDexClassDeltaRestrictedToAllowedFamilies",
                 "menuDexUnrelatedClassesByteIdentical", "nativeSettingsLabelsExactInversePassed", "nativeOtherBytesByteIdentical",
                 "offlineEmulatorUiEntriesChanged"):
        require(receipt.get(flag) is True, "Retained contract flag differs: " + flag)
    require(receipt.get("ps3Ps4OnlineEnabled") is False, "Sony must remain offline")
    require(receipt.get("normalPsxLibrariesPreserved") == previous["psx"]["dependencySha256"],
            "PSX owner/core/frontend library dependencies must stay exact")
    require(not any(key in receipt for key in ("switchReceiptPath", "switchAllowedTypes", "updatedPsxFrontendDependencySha256",
                                              "existing40DexByteIdentical", "dexClassSetsPreserved")),
            "R134 must not introduce Switch/frontend changes or claim identical scoped DEX")
    manifest["assets/station-online/engines.json"] = receipt["enginesAssetSha256"]
    return receipt, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base-apk", "parent-identity", "payload-receipt", "ndk", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Never overwrite a runtime identity output tree")
    pins = source_map()
    verify_source_commit(args.source_commit, pins)
    verify_dependencies()
    native, payloads = payload_inputs(args.payload_receipt, args.source_commit, pins)
    parent, previous, original, profile, inherited = parent_inputs(args.base_apk, args.parent_identity)
    native_hash = sha(args.payload_receipt)
    actual = {**inherited, **{name: sha(path) for name, path in payloads.items()}}
    require(all(actual[name] != inherited[name] for name in PAYLOADS) and
            native["preservedDexSha256"] == {name: inherited[name] for name in PRESERVED_DEX},
            "All three scoped payloads must change, with exactly 38 retained DEX")
    transforms = transforms_for(previous, pins)
    args.out.mkdir(parents=True)
    fingerprints, markers = {}, {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE_SHA, payloadSha256=actual, productiveTransforms=transforms)
    raw = canonical(psx)
    (args.out / "psx.fingerprint.json").write_bytes(raw + b"\n")
    identity_source = args.out / "StationPsxIdentity.cpp"
    identity_source.write_text('extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
                               'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n', encoding="ascii")
    native_out = args.out / "native"
    subprocess.run([sys.executable, "-B", str(PSX / "recipe/build_entry.py"), "--ndk", str(args.ndk),
                    "--owner", str(PSX / "native"), "--protocol", str(PSX / "native"), "--pinned-options", str(PSX / "native"),
                    "--identity-source", str(identity_source), "--out", str(native_out)], check=True,
                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    binary = native_out / "libstation_psx_online.so"
    require(raw in binary.read_bytes(), "PSX entry lacks exact canonical identity literal")
    markers["psx"] = {"runtimeLibrary": binary.name, "runtimeSha256": sha(binary), "runtimeBytes": binary.stat().st_size,
                      "fingerprintSha256": digest(raw)}
    fingerprints["psx"] = psx
    primitive = import_markers()
    for kind in ("n64", "dolphin"):
        value = copy.deepcopy(previous[kind])
        library, old_runtime, old_fingerprint = MARKERS[kind]
        value.update(baseApkSha256=BASE_SHA, payloadSha256=actual, productiveTransforms=transforms,
                     parentFingerprintSha256=old_fingerprint, parentRuntimeSha256=old_runtime,
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, args.ndk, args.out)
        fingerprints[kind] = value
    for kind, value in fingerprints.items():
        require(policy(previous[kind]) == policy(value), "Retained runtime policy changed: " + kind)
    updated, selected = expected_engines(original, markers)
    engines = args.out / "engines.json"
    write(engines, updated)
    require(engines.stat().st_size <= 32768, "Engine asset exceeds client contract")
    (args.out / "psx-controller-profile.json").write_bytes(profile + b"\n")
    verify_dependencies()
    require(source_map() == pins and sha(args.payload_receipt) == native_hash,
            "Productive R134/scoped inputs changed during compilation")
    native_again, payloads_again = payload_inputs(args.payload_receipt, args.source_commit, pins)
    require(native_again == native and payloads_again == payloads, "Compiled native artifacts changed")
    native_transforms = {"dexScopes": native["dexScopes"], "nativeLabels": read(native["labelsReceipt"]["path"])["changedLabels"]}
    result = {
        "schemaVersion": 3, "revision": "R134", "sourceCommit": args.source_commit,
        "baseApkSha256": BASE_SHA, "retainedBaseSourceCommit": BASE_SOURCE,
        "parentRuntimeMarkers": parent["markers"],
        "parentIdentityReceiptPath": str((args.parent_identity / "runtime-identity.json").resolve()),
        "parentIdentityReceiptSha256": PARENT_RECEIPT_SHA,
        "payloadReceiptPath": str(args.payload_receipt.resolve()), "payloadReceiptSha256": native_hash,
        "nativeReceiptPath": str(args.payload_receipt.resolve()), "nativeReceiptSha256": native_hash,
        "compilationReceiptSchema": "station.settings.refinement.payloads.v1",
        "payloadInputSha256": native["inputSha256"], "payloadTransforms": native_transforms,
        "nativeInputSha256": native["inputSha256"], "nativeTransforms": native_transforms, "dexScopes": native["dexScopes"],
        "compilationReceiptSha256": {"payload-receipt": native_hash, "java-receipt": native["javaReceipt"]["sha256"],
                                     "labels-receipt": native["labelsReceipt"]["sha256"]},
        "compilationReceiptPaths": {"payload-receipt": str(args.payload_receipt.resolve()),
                                    "java-receipt": native["javaReceipt"]["path"], "labels-receipt": native["labelsReceipt"]["path"]},
        "markers": markers, "engines": selected, "enginesAssetSha256": sha(engines),
        "payloadSha256": actual,
        "preservedR133PayloadSha256": {name: value for name, value in inherited.items() if name not in PAYLOADS},
        "newSharedPayloadSha256": {name: sha(path) for name, path in payloads.items()},
        "sourceSha256": pins, "dependencySourceSha256": dict(DEPENDENCY_SOURCES),
        "psxControllerProfileSha256": digest(profile), "psxOptionsSha256": parent["psxOptionsSha256"],
        "normalPsxLibrariesPreserved": previous["psx"]["dependencySha256"],
        "existing38DexByteIdentical": True, "dexScopedClassesVerified": True,
        "menuDexClassDeltaRestrictedToAllowedFamilies": True, "menuDexUnrelatedClassesByteIdentical": True,
        "nativeSettingsLabelsExactInversePassed": True, "nativeOtherBytesByteIdentical": True,
        "nativeEmulatorEntriesPreserved": True, "offlineEmulatorUiEntriesChanged": True,
        "frontendLibraryByteIdentical": True, "manifestByteIdentical": True,
        "resourcesAndSonyAssetsByteIdentical": True, "shaderCodeAndEffectsPreserved": True,
        "videoBytesAndLoopPolicyPreserved": True, "n64DolphinCoreAndOptionsUnchanged": True,
        "snesMegadriveEntriesUnchanged": True, "controllerProfilesUnchanged": True,
        "protocolAndTransportUnchanged": True, "ps3Ps4OfflineOnly": True,
        "ps3Ps4OnlineEnabled": False, "registeredOnServer": False,
        "installed": False, "physicalGameplayValidated": False, "approvedScopes": SCOPES,
    }
    write(args.out / "runtime-identity.json", result)
    validate_inputs(args.base_apk, args.out / "runtime-identity.json")
    print(json.dumps({"revision": "R134", "engineIds": [row["engineId"] for row in selected],
                      "registeredOnServer": False, "existing38DexByteIdentical": True, "dexScopedClassesVerified": True}))


if __name__ == "__main__":
    main()
