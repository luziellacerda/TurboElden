"""Renew only the shared identity for the scoped R135 DEX35 lifecycle overlay.

The signed R134 donor, its original receipt and every inherited payload are
checked. The retained PSX entry and N64/Dolphin marker builders keep their
sources, flags, policies, cores and dependencies. No signing or device action.
"""
from __future__ import annotations
import argparse
import copy
import os
import re
import struct
import subprocess
import sys
import zipfile
from release_common import *

PSX = REPO / "integration/psx-online"
PARENT_RECEIPT_SHA = "2d6fc1c1933b4dc88aa09192138b8564b5f0b743461faa7580896b8339b2067f"
PARENT_ENGINES_SHA = "40e55b795eae0d2a0f1a439f271bab692eb84e38907043c537b69da403fa354e"
PARENT_PAYLOAD_COUNT = 345
MARKERS = {
    "psx": ("libstation_psx_online.so", "69ac2b703f03826c8f7203b296665c6f2cc34cb944af7c3f758d9033116cade3", "20b94de2c844a18439a7f5acd447e0ac2d1bd09c986aa00cd58392848a257a39"),
    "n64": ("libstation_mupen64plus_runtime.so", "5f56099c433f29514c864d1eeea2995e3f52b0d15d76eaf125c4f4346a9d6e87", "53d7c041285c27cd2a8d847b15ba9b9df11ca294f44513de6b5d995d51a6df9e"),
    "dolphin": ("libstation_dolphin_runtime.so", "9c87e2ec4c798ab1f42130326855d0171617501ee513dfefa74241b3665e38ad", "074970a845b44e40d62a8b3b86869ff7a7d85db5fc33dd7cb0a3837ee408044c"),
}
DEPENDENCY_SOURCES = {
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
    "versions/station-mupen-online-r125-20261011/recipes/build_runtime_identity.py": "fdb79db3e354f3359d00980a1a00e7dec9d5fcbfed27892d4c42fbd4af1b2a16",
}
NDK_BIN = "toolchains/llvm/prebuilt/windows-x86_64/bin/"
NATIVE_TOOL_PINS = {
    "source.properties": "c00aa236fdb205e9be9edd9e2169763e48aca52735efff4e16f34205d49783b5",
    NDK_BIN + "clang.exe": "7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579",
    NDK_BIN + "clang++.exe": "1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3",
    NDK_BIN + "aarch64-linux-android28-clang++.cmd": "2e39a6973566b53f303797c4985d7f52d8b25e461797ce7bad3eaa680c8b756d",
    NDK_BIN + "llvm-strip.exe": "2d411db64e0b45508775e9e8fd436fb6e0af814a9dfbf8aea8fc37ce436c435c",
    NDK_BIN + "llvm-nm.exe": "90236526ebb24c232e59ec573675e32a92190b3346cf3a342c8b0eb5ad0f8203",
    NDK_BIN + "llvm-readobj.exe": "68f67a9285a798a470fba5b9ab8ecab80031d5a606d941e1f3310a1f7a268bec",
    NDK_BIN + "llvm-readelf.exe": "2646e382d8b2559b5c4ae91e9a98e187ed9bd59f23936054d424049ef795ba5e",
}
SCOPE_FIELDS = (
    "partition", "baselineDexSha256", "allowedFamilies", "originalClassCount", "finalClassCount",
    "unchangedClasses", "originalAllowedTypes", "finalAllowedTypes", "addedTypes", "removedTypes",
    "modifiedTypes", "baselineClassSha256", "outputClassSha256", "unchangedClassSha256",
    "unrelatedClassesByteIdentical", "classProjectionFormat", "unrelatedProjectionCanonicalSha256",
    "classDeltaRestrictedToAllowedFamilies", "staticInitializersPreserved", "restoredInitializerArrays",
    "d8SyntheticTypes", "d8OverlayDexSha256", "scopeDeclarationSha256",
)


def archive_sha(archive, name):
    import hashlib
    value = hashlib.sha256()
    with archive.open(name) as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(part)
    return value.hexdigest()


def artifact(path):
    path = Path(path).resolve(strict=True)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}


def verify_dependencies():
    for name, expected in DEPENDENCY_SOURCES.items():
        require(sha(REPO / name) == expected, "Retained identity primitive changed: " + name)


def native_tools(ndk):
    records = {name: artifact(Path(ndk) / name) for name in NATIVE_TOOL_PINS}
    check_native_tools(records)
    return records


def check_native_tools(records):
    require(isinstance(records, dict) and set(records) == set(NATIVE_TOOL_PINS), "Exact retained NDK r28c tools required")
    roots = set()
    for name, expected in NATIVE_TOOL_PINS.items():
        path = checked_file(records[name], name)
        require(records[name]["sha256"] == expected, "Pinned native tool differs: " + name)
        root = path
        for _ in Path(name).parts:
            root = root.parent
        roots.add(root)
    require(len(roots) == 1, "Native tools must belong to one pinned NDK installation")


def check_marker_elf(binary, kind):
    require(len(binary) >= 64 and binary[:6] == b"\x7fELF\x02\x01" and
            struct.unpack_from("<H", binary, 18)[0] == 183, "Runtime marker must remain an AArch64 ELF: " + kind)
    offset = struct.unpack_from("<Q", binary, 32)[0]
    stride, count = struct.unpack_from("<HH", binary, 54)
    require(count > 0 and stride >= 56 and offset + stride * count <= len(binary), "Runtime marker program headers differ: " + kind)
    loads = [struct.unpack_from("<Q", binary, offset + index * stride + 48)[0] for index in range(count)
             if struct.unpack_from("<I", binary, offset + index * stride)[0] == 1]
    require(loads and all(value >= 16384 and value & (value - 1) == 0 for value in loads),
            "Runtime marker LOAD alignment must remain 16KiB: " + kind)


def dex_scope(receipt, compiler):
    require(receipt.get("partition") == "classes35.dex" and receipt.get("baselineDexSha256") == BASELINE_DEX_SHA and
            receipt.get("allowedFamilies") == FAMILIES, "Exact three-family R135 DEX35 scope required")
    before, after, outside = (receipt.get(k) for k in ("baselineClassSha256", "outputClassSha256", "unchangedClassSha256"))
    require(all(isinstance(m, dict) and m for m in (before, after, outside)) and
            all(isinstance(t, str) and t.startswith("L") and t.endswith(";") and
                isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h)
                for m in (before, after, outside) for t, h in m.items()), "Complete class projection hashes required")
    old_allowed = {t for t in before if compiler.belongs(t)}
    new_allowed = {t for t in after if compiler.belongs(t)}
    require(old_allowed == compiler.ORIGINAL_TYPES and set(FAMILIES) <= new_allowed and
            receipt.get("originalAllowedTypes") == sorted(old_allowed) and receipt.get("finalAllowedTypes") == sorted(new_allowed) and
            set(before) - old_allowed == set(after) - new_allowed == set(outside) and
            {t: before[t] for t in outside} == {t: after[t] for t in outside} == outside,
            "Foreign classes changed or exact owner-family set differs")
    require(len(before) == receipt.get("originalClassCount") == 606 and len(outside) == receipt.get("unchangedClasses") == 582 and
            len(after) == receipt.get("finalClassCount") and
            receipt.get("addedTypes") == sorted(new_allowed - old_allowed) and
            receipt.get("removedTypes") == sorted(old_allowed - new_allowed) and
            receipt.get("modifiedTypes") == sorted(t for t in old_allowed & new_allowed if before[t] != after[t]) and
            receipt.get("unrelatedProjectionCanonicalSha256") == digest(canonical(outside)), "Complete scoped class delta differs")
    require(all(receipt.get(flag) is True for flag in ("unrelatedClassesByteIdentical", "classDeltaRestrictedToAllowedFamilies",
                                                     "staticInitializersPreserved")) and
            type(receipt.get("restoredInitializerArrays")) is int and 0 <= receipt["restoredInitializerArrays"] <= 582 and
            receipt.get("classProjectionFormat") == "apktool-3.0.3-baksmali-locals-sequential-labels-debug-info" and
            all(isinstance(receipt.get(k), str) and re.fullmatch(r"[0-9a-f]{64}", receipt[k])
                for k in ("scopeDeclarationSha256", "d8OverlayDexSha256")) and
            receipt.get("d8SyntheticTypes") == sorted(t for t in new_allowed if "$$ExternalSynthetic" in t),
            "Static initializer, scope declaration or D8 synthetic guard missing")
    return {key: copy.deepcopy(receipt[key]) for key in SCOPE_FIELDS}


def payload_inputs(path, commit, pins):
    path = Path(path).resolve(strict=True)
    receipt = read(path)
    compiler = module(ROOT / "recipe/build_dex.py", "r135_scoped_dex_contract")
    require(receipt.get("schema") == "station.online-lifecycle.dex.r135.v1" and
            receipt.get("status") == "compiled-dex-payload-only" and receipt.get("passed") is True and
            receipt.get("sourceCommitVerified") is True and receipt.get("sourceCommit") == commit and
            receipt.get("baseAppCommit") == BASE_SOURCE and receipt.get("baselineApkSha256") == BASE_SHA and
            receipt.get("baselineApkBytes") == BASE_BYTES and receipt.get("sourceSha256") == pins and
            receipt.get("sourceCanonicalSha256") == digest(canonical(pins)) and
            receipt.get("sourcePinsSha256") == compiler.SOURCE_PINS_SHA == sha(ROOT / "SOURCE-PINS.json") and
            receipt.get("changedDexPartitions") == ["classes35.dex"] and
            set(receipt.get("preservedDexSha256", {})) == PRESERVED_DEX and
            receipt.get("inputSha256") == compiler.INPUT_PINS, "Exact committed R135 DEX-only compilation receipt required")
    require(receipt.get("productiveJavaTarget") == 8 and receipt.get("classMajorVersion") == 52 and
            receipt.get("androidCompileApi") == 34 and receipt.get("dexMinimumApi") == 28 and
            all(receipt.get(flag) is False for flag in ("compileOnlyClassesPackaged", "sdkOrDependenciesPackaged",
                "testsOrFixturesPackaged", "productiveSourcesChanged", "runtimeIdentityBuilt", "apkAssembled",
                "signed", "installed", "physicalGameplayValidated", "productionAccess")), "DEX build scope or Android API policy differs")
    require(set(receipt.get("inputFiles", {})) == set(compiler.INPUT_PINS), "Complete pinned external DEX inputs required")
    for name, record in receipt["inputFiles"].items():
        checked_file(record, name)
        require(record["sha256"] == compiler.INPUT_PINS[name], "DEX input record differs: " + name)
    scope = dex_scope(receipt, compiler)
    payload = receipt.get("payload")
    require(isinstance(payload, dict) and set(payload) == {"name", "bytes", "sha256"} and
            payload["name"] == "classes35.dex" and payload["sha256"] != BASELINE_DEX_SHA, "Only changed DEX35 payload allowed")
    output = checked_file({"path": str(path.parent / "classes35.dex"), "bytes": payload["bytes"], "sha256": payload["sha256"]}, "classes35.dex")
    require(len(compiler.dex_types(output.read_bytes())) == scope["finalClassCount"] and
            compiler.dex_types(output.read_bytes()) == set(scope["outputClassSha256"]), "Actual DEX payload class set differs")
    return receipt, {"classes35.dex": output}, {"classes35.dex": scope}


def parent_inputs(base, directory):
    require(Path(base).stat().st_size == BASE_BYTES and sha(base) == BASE_SHA, "Exact signed R134 donor required")
    directory = Path(directory).resolve(strict=True)
    receipt_path = directory / "runtime-identity.json"
    parent = read(receipt_path)
    require(sha(receipt_path) == PARENT_RECEIPT_SHA and parent.get("revision") == "R134" and
            parent.get("sourceCommit") == BASE_SOURCE and set(parent.get("markers", {})) == set(MARKERS) and
            len(parent.get("payloadSha256", {})) == PARENT_PAYLOAD_COUNT and
            parent.get("ps3Ps4OfflineOnly") is True and parent.get("ps3Ps4OnlineEnabled") is False,
            "Original private R134 identity receipt required")
    previous = {}
    with zipfile.ZipFile(base) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) == 13860 and
                {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} == DEX and
                REPLACED <= set(names), "Unique exact 40-DEX R134 archive required")
        for name, expected in parent["payloadSha256"].items():
            require(archive_sha(archive, name) == expected, "Actual inherited payload differs: " + name)
        require(parent["payloadSha256"].get("classes35.dex") == BASELINE_DEX_SHA and
                parent["payloadSha256"].get(PREFIX + "libstation_frontend.so") == FRONTEND_SHA,
                "Actual R134 DEX35/frontend differs")
        raw_engines = archive.read("assets/station-online/engines.json")
        require(digest(raw_engines) == sha(directory / "engines.json") == PARENT_ENGINES_SHA, "Original R134 engines asset differs")
        engines = json.loads(raw_engines)
        selected = [row for row in engines["engines"] if row["platform"] in {"psx", "n64", "gamecube", "wii"}]
        require(selected == parent["engines"] and len(selected) == 4 and
                {row["platform"] for row in selected} == {"psx", "n64", "gamecube", "wii"}, "Exact four existing online identities required")
        for kind, (library, runtime_hash, fingerprint_hash) in MARKERS.items():
            filename = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
            raw = (directory / filename).read_bytes().rstrip(b"\r\n")
            value = json.loads(raw)
            binary = archive.read(PREFIX + library)
            require(raw == canonical(value) and digest(raw) == fingerprint_hash and raw in binary and
                    fingerprint_hash.encode("ascii") in binary and digest(binary) == runtime_hash and
                    parent["markers"][kind]["runtimeSha256"] == runtime_hash and
                    parent["markers"][kind]["fingerprintSha256"] == fingerprint_hash and
                    value.get("payloadSha256") == parent["payloadSha256"], "R134 marker/fingerprint binding differs: " + kind)
            for field in ("dependencySha256", "compiledBackendSha256"):
                for name, expected in value.get(field, {}).items():
                    require(archive_sha(archive, PREFIX + name) == expected, "Actual inherited dependency/core differs: " + name)
            previous[kind] = value
        for entry in selected:
            require(archive_sha(archive, PREFIX + entry["library"]) == entry["coreSha256"], "Actual inherited core differs: " + entry["platform"])
            for name, expected in entry["dependencySha256"].items():
                require(archive_sha(archive, PREFIX + name) == expected, "Actual engine dependency differs: " + name)
        profile = (directory / "psx-controller-profile.json").read_bytes().rstrip(b"\r\n")
        require(digest(profile) == parent["psxControllerProfileSha256"], "Original PSX controller profile required")
    first = previous["psx"]
    require(all(value["javaSources"] == first["javaSources"] and value["productiveTransforms"] == first["productiveTransforms"]
                for value in previous.values()), "Inherited source-chain maps disagree")
    for name in ("StationPsxEntry.cpp", "StationPsxOwner.cpp", "StationPsxOwner.hpp", "StationPsxProtocol.cpp",
                 "StationPsxProtocol.hpp", "StationPsxSha256.cpp", "PsxPinnedOptions.h"):
        require(sha(PSX / "native" / name) == first["productiveTransforms"].get("native/" + name), "Retained PSX source changed: " + name)
    require(sha(PSX / "java/org/emulationstation/frontend/netplay/StationPsxBridge.java") ==
            first["javaSources"].get("netplay-src/org/emulationstation/frontend/netplay/StationPsxBridge.java"), "Retained PSX JNI declaration changed")
    return parent, previous, engines, profile, dict(parent["payloadSha256"])


def policy(value):
    result = copy.deepcopy(value)
    for key in ("baseApkSha256", "payloadSha256", "productiveTransforms", "parentFingerprintSha256", "parentRuntimeSha256", "psxRuntimeSha256"):
        result.pop(key, None)
    return result


def transforms_for(previous, pins):
    extra = {"online-lifecycle-review-r135/" + name: value for name, value in pins.items()}
    inherited = previous["psx"]["productiveTransforms"]
    require(not set(extra).intersection(inherited), "R135 source overlay must append without changing frozen source-chain maps")
    return {**inherited, **extra}


def expected_engines(original, markers):
    updated = copy.deepcopy(original)
    selected = []
    for before, after in zip(original["engines"], updated["engines"]):
        platform = after["platform"]
        if platform not in {"psx", "n64", "gamecube", "wii"}:
            continue
        kind = "dolphin" if platform in {"gamecube", "wii"} else platform
        runtime_hash = markers[kind]["runtimeSha256"]
        prefix = ("pcsx-rearmed-ff81ed17-player-v3-" if kind == "psx" else
                  "mupen64plus-ae-33bf7021-n64-v3-" if kind == "n64" else "dolphin-5102a033-" + platform + "-v3-")
        after.update(engineId=prefix + runtime_hash[:12], runtimeSha256=runtime_hash)
        strip = lambda row: {key: value for key, value in row.items() if key not in {"engineId", "runtimeSha256"}}
        require(strip(before) == strip(after) and before["engineId"] != after["engineId"], "Only engine ID/runtime hash may change: " + platform)
        selected.append(after)
    require(len(selected) == 4 and {row["platform"] for row in selected} == {"psx", "n64", "gamecube", "wii"} and
            len({row["engineId"] for row in updated["engines"]}) == len(updated["engines"]), "Four renewed identities and unique existing engine set required")
    return updated, selected


def validate_inputs(base, identity_path):
    """Read-only validation of the original donor, scoped DEX and derived identity."""
    identity_path = Path(identity_path).resolve(strict=True)
    directory = identity_path.parent
    receipt = read(identity_path)
    pins = source_map()
    require(receipt.get("schemaVersion") == 3 and receipt.get("revision") == "R135" and
            receipt.get("baseApkSha256") == BASE_SHA and receipt.get("retainedBaseSourceCommit") == BASE_SOURCE and
            receipt.get("sourceSha256") == pins and receipt.get("parentIdentityReceiptSha256") == PARENT_RECEIPT_SHA and
            receipt.get("dependencySourceSha256") == DEPENDENCY_SOURCES and receipt.get("approvedScopes") == SCOPES and
            all(receipt.get(flag) is False for flag in ("registeredOnServer", "installed", "physicalGameplayValidated", "ps3Ps4OnlineEnabled")),
            "Exact uninstalled R135 lifecycle identity receipt required")
    verify_source_commit(receipt["sourceCommit"], pins)
    verify_dependencies()
    check_native_tools(receipt.get("nativeToolFiles"))
    payload_path = Path(receipt["payloadReceiptPath"])
    require(sha(payload_path) == receipt.get("payloadReceiptSha256") and
            receipt.get("compilationReceiptSchema") == "station.online-lifecycle.dex.r135.v1", "Scoped DEX receipt changed after fingerprinting")
    compiled, payloads, scopes = payload_inputs(payload_path, receipt["sourceCommit"], pins)
    parent_path = Path(receipt["parentIdentityReceiptPath"])
    require(parent_path.name == "runtime-identity.json" and sha(parent_path) == PARENT_RECEIPT_SHA, "Original R134 parent receipt path required")
    parent, previous, original, profile, inherited = parent_inputs(base, parent_path.parent)
    actual = {**inherited, "classes35.dex": sha(payloads["classes35.dex"])}
    require(actual != inherited and actual == receipt.get("payloadSha256") and
            receipt.get("newSharedPayloadSha256") == {"classes35.dex": actual["classes35.dex"]} and
            receipt.get("preservedR134PayloadSha256") == {name: value for name, value in inherited.items() if name != "classes35.dex"} and
            compiled["preservedDexSha256"] == {name: inherited[name] for name in PRESERVED_DEX} and
            receipt.get("payloadInputSha256") == compiled["inputSha256"] and receipt.get("payloadInputFiles") == compiled["inputFiles"] and
            receipt.get("dexScopes") == scopes and receipt.get("parentRuntimeMarkers") == parent["markers"], "Only scoped DEX35 may change in the complete common payload map")
    require(set(receipt.get("markers", {})) == set(MARKERS), "Exact three renewed runtime markers required")
    transforms = transforms_for(previous, pins)
    manifest = dict(actual)
    for kind, (library, old_runtime, old_fingerprint) in MARKERS.items():
        expected = copy.deepcopy(previous[kind])
        expected.update(baseApkSha256=BASE_SHA, payloadSha256=actual, productiveTransforms=transforms)
        if kind != "psx":
            expected.update(parentFingerprintSha256=old_fingerprint, parentRuntimeSha256=old_runtime,
                            psxRuntimeSha256=receipt["markers"]["psx"]["runtimeSha256"])
        filename = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
        raw = (directory / filename).read_bytes().rstrip(b"\r\n")
        marker = receipt["markers"][kind]
        path = directory / "native" / library if kind == "psx" else directory / library
        binary = checked_file({"path": str(path), "bytes": marker["runtimeBytes"], "sha256": marker["runtimeSha256"]}, library).read_bytes()
        check_marker_elf(binary, kind)
        require(raw == canonical(expected) and raw in binary and digest(raw).encode("ascii") in binary and
                marker["runtimeLibrary"] == library and marker["fingerprintSha256"] == digest(raw) and
                marker["runtimeSha256"] != old_runtime and policy(previous[kind]) == policy(expected), "Derived marker or retained runtime policy differs: " + kind)
        manifest[PREFIX + library] = marker["runtimeSha256"]
    updated, selected = expected_engines(original, receipt["markers"])
    require(read(directory / "engines.json") == updated and receipt.get("engines") == selected and
            sha(directory / "engines.json") == receipt.get("enginesAssetSha256") and (directory / "engines.json").stat().st_size <= 32768 and
            (directory / "psx-controller-profile.json").read_bytes() == profile + b"\n" and
            receipt.get("psxControllerProfileSha256") == parent["psxControllerProfileSha256"] and
            receipt.get("psxOptionsSha256") == parent["psxOptionsSha256"] and
            receipt.get("normalPsxLibrariesPreserved") == previous["psx"]["dependencySha256"], "New identity or preserved controller/options/dependency contract differs")
    for flag in ("existing39DexByteIdentical", "dexScopedClassesVerified", "classDeltaRestrictedToAllowedFamilies", "unrelatedClassesByteIdentical",
                 "staticInitializersPreserved", "frontendLibraryByteIdentical", "manifestByteIdentical", "resourcesAndSonyAssetsByteIdentical",
                 "nativeEmulatorEntriesPreserved", "n64DolphinCoreAndOptionsUnchanged", "snesMegadriveEntriesUnchanged",
                 "controllerProfilesUnchanged", "nativeRebuildsIdentityOnly", "coreAndControllerPoliciesUnchanged", "ps3Ps4OfflineOnly"):
        require(receipt.get(flag) is True, "Retained R135 contract flag differs: " + flag)
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
    tool_files = native_tools(args.ndk)
    compiled, payloads, scopes = payload_inputs(args.payload_receipt, args.source_commit, pins)
    parent, previous, original, profile, inherited = parent_inputs(args.base_apk, args.parent_identity)
    payload_hash = sha(args.payload_receipt)
    actual = {**inherited, "classes35.dex": sha(payloads["classes35.dex"])}
    require(actual["classes35.dex"] != inherited["classes35.dex"] and
            compiled["preservedDexSha256"] == {name: inherited[name] for name in PRESERVED_DEX}, "Only DEX35 may change with the other 39 DEX retained")
    transforms = transforms_for(previous, pins)
    args.out.mkdir(parents=True)
    markers, fingerprints = {}, {}
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
    require(raw in binary.read_bytes(), "Retained PSX entry lacks the exact canonical identity")
    markers["psx"] = {"runtimeLibrary": binary.name, "runtimeSha256": sha(binary), "runtimeBytes": binary.stat().st_size, "fingerprintSha256": digest(raw)}
    fingerprints["psx"] = psx
    primitive = module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r135_retained_marker_primitives")
    for kind in ("n64", "dolphin"):
        value = copy.deepcopy(previous[kind])
        library, old_runtime, old_fingerprint = MARKERS[kind]
        value.update(baseApkSha256=BASE_SHA, payloadSha256=actual, productiveTransforms=transforms,
                     parentFingerprintSha256=old_fingerprint, parentRuntimeSha256=old_runtime, psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, args.ndk, args.out)
        fingerprints[kind] = value
    require(all(policy(previous[kind]) == policy(value) for kind, value in fingerprints.items()), "Retained runtime policy changed")
    updated, selected = expected_engines(original, markers)
    write(args.out / "engines.json", updated)
    require((args.out / "engines.json").stat().st_size <= 32768, "Engine asset exceeds the unchanged client limit")
    (args.out / "psx-controller-profile.json").write_bytes(profile + b"\n")
    verify_dependencies()
    check_native_tools(tool_files)
    require(source_map() == pins and sha(args.payload_receipt) == payload_hash, "Committed R135 source or DEX receipt changed during marker compilation")
    again, paths_again, scopes_again = payload_inputs(args.payload_receipt, args.source_commit, pins)
    require(again == compiled and paths_again == payloads and scopes_again == scopes, "Compiled DEX input changed")
    result = {
        "schemaVersion": 3, "revision": "R135", "sourceCommit": args.source_commit,
        "baseApkSha256": BASE_SHA, "retainedBaseSourceCommit": BASE_SOURCE,
        "parentRuntimeMarkers": parent["markers"], "parentIdentityReceiptPath": str((args.parent_identity / "runtime-identity.json").resolve()),
        "parentIdentityReceiptSha256": PARENT_RECEIPT_SHA, "payloadReceiptPath": str(args.payload_receipt.resolve()),
        "payloadReceiptSha256": payload_hash, "compilationReceiptSchema": "station.online-lifecycle.dex.r135.v1",
        "payloadInputSha256": compiled["inputSha256"], "payloadInputFiles": compiled["inputFiles"], "dexScopes": scopes,
        "markers": markers, "engines": selected, "enginesAssetSha256": sha(args.out / "engines.json"), "payloadSha256": actual,
        "preservedR134PayloadSha256": {name: value for name, value in inherited.items() if name != "classes35.dex"},
        "newSharedPayloadSha256": {"classes35.dex": actual["classes35.dex"]}, "sourceSha256": pins,
        "dependencySourceSha256": dict(DEPENDENCY_SOURCES), "nativeToolFiles": tool_files,
        "psxControllerProfileSha256": digest(profile), "psxOptionsSha256": parent["psxOptionsSha256"],
        "normalPsxLibrariesPreserved": previous["psx"]["dependencySha256"],
        "existing39DexByteIdentical": True, "dexScopedClassesVerified": True, "classDeltaRestrictedToAllowedFamilies": True,
        "unrelatedClassesByteIdentical": True, "staticInitializersPreserved": True,
        "frontendLibraryByteIdentical": True, "manifestByteIdentical": True, "resourcesAndSonyAssetsByteIdentical": True,
        "nativeEmulatorEntriesPreserved": True, "n64DolphinCoreAndOptionsUnchanged": True,
        "snesMegadriveEntriesUnchanged": True, "controllerProfilesUnchanged": True,
        "nativeRebuildsIdentityOnly": True, "coreAndControllerPoliciesUnchanged": True,
        "ps3Ps4OfflineOnly": True, "ps3Ps4OnlineEnabled": False, "registeredOnServer": False, "installed": False,
        "physicalGameplayValidated": False, "approvedScopes": SCOPES,
    }
    write(args.out / "runtime-identity.json", result)
    validate_inputs(args.base_apk, args.out / "runtime-identity.json")
    print(json.dumps({"revision": "R135", "engineIds": [row["engineId"] for row in selected],
                      "registeredOnServer": False, "existing39DexByteIdentical": True, "dexScopedClassesVerified": True}))


if __name__ == "__main__":
    main()
