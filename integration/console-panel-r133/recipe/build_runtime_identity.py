"""Renew four identities for one closed console-panel carousel overlay on R132.

No DEX, frontend, engine core, options, controllers, transport or security
changes. The PSX entry is rebuilt from its exact retained native sources with
only the new canonical identity literal; N64/Dolphin use pinned marker builders.
No signing, installation, server registration or gameplay occurs here.
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
PARENT_RECEIPT_SHA = "0278f06066b2853784a66201f289dde21859dd3c647a2832a46159bfd3684b72"
PARENT_ENGINES_SHA = "b57780604b4d750b90a339bf3155ca3ac6e1670b3015da45804f569de6758e9f"
PARENT_PAYLOAD_COUNT = 345
MARKERS = {
    "psx": ("libstation_psx_online.so", "6976f8ff22820520540b3e5c13fbb1234c21294e3e8c2fd6aaf3a6b0a7e32e2c", "fc20705b3b9b4036f2ce4490394abbc800e3c817e760d8c81b30a5034d2e2ffb"),
    "n64": ("libstation_mupen64plus_runtime.so", "6b41b91a4914976ec2c5326a7081675d1a7bbf4cd7268dd1a3da8132e580d222", "a1066924c0feb87d232e21aebcb624c362ff87f7a4db07f3f6f2050d19682542"),
    "dolphin": ("libstation_dolphin_runtime.so", "f32c0c2f87aa5ec5c8fb4edd3a8c4ee8b269807d084f7f85bb65fe511335fc2b", "b446bbcf3211686c6352fc7d5b7e1265535be76eb190f886c62b5d548b960cc2"),
}
PAYLOADS = frozenset({PREFIX + "libturbo_carousel.so"})
DEX = frozenset(["classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]])
SCOPES = ["console-hardware-panel-psp-ps3-ps4"]
DEPENDENCY_SOURCES = {
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
    "versions/station-mupen-online-r125-20261011/recipes/build_runtime_identity.py": "fdb79db3e354f3359d00980a1a00e7dec9d5fcbfed27892d4c42fbd4af1b2a16",
    "integration/startup-cleanup-r132/recipe/common.py": "268230041e5560c8de4e549a7b55d3e0ab63cb23c069bab46ec9eaec97e4e460",
    "integration/startup-cleanup-r132/recipe/build_runtime_identity.py": "21fd2ea981c30c44c99511b9fa86cee8a04dcf3a0537b167325cd73b7efce15b",
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


def native_inputs(path, commit, pins):
    receipt = read(path)
    require(receipt.get("schema") == "station.console.panel.native.v1" and
            receipt.get("revision") == "R133" and receipt.get("baseApkSha256") == BASE_SHA and
            receipt.get("sourceCommit") == commit and receipt.get("sourceSha256") == pins and
            receipt.get("baselineReproduced") == {"carousel": True} and
            receipt.get("approvedScopes") == SCOPES and receipt.get("dexChanged") is False and
            set(receipt.get("payloads", {})) == PAYLOADS and
            set(receipt.get("transforms", {})) == {"consolePanel"} and
            isinstance(receipt["transforms"]["consolePanel"], dict) and receipt["transforms"]["consolePanel"] and
            isinstance(receipt.get("inputSha256"), dict) and receipt["inputSha256"],
            "Closed carousel-only R133 compilation receipt required")
    require(all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                for value in receipt["inputSha256"].values()), "Complete exact private/public native input hashes required")
    payloads = {name: checked_file(record, name) for name, record in receipt["payloads"].items()}
    require(payloads[PREFIX + "libturbo_carousel.so"].name == "libturbo_carousel.so",
            "Conventional carousel payload path required")
    return receipt, payloads


def parent_inputs(base, directory):
    """Check all 345 parent payloads, embedded fingerprints and real cores/deps."""
    require(Path(base).stat().st_size == BASE_BYTES and sha(base) == BASE_SHA,
            "Exact signed R132 donor required")
    directory = Path(directory).resolve(strict=True)
    receipt_path = directory / "runtime-identity.json"
    parent = read(receipt_path)
    require(sha(receipt_path) == PARENT_RECEIPT_SHA and parent.get("revision") == "R132" and
            parent.get("sourceCommit") == BASE_SOURCE and set(parent.get("markers", {})) == set(MARKERS) and
            len(parent.get("payloadSha256", {})) == PARENT_PAYLOAD_COUNT and
            parent.get("ps3Ps4OfflineOnly") is True and parent.get("ps3Ps4OnlineEnabled") is False,
            "Exact original R132 identity receipt required")
    fingerprints = {}
    with zipfile.ZipFile(base) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and
                {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} == DEX,
                "Unique exact 40-DEX R132 archive required")
        for name, expected in parent["payloadSha256"].items():
            require(archive_sha(archive, name) == expected, "Actual parent payload differs: " + name)
        require(parent["payloadSha256"].get(PREFIX + "libturbo_carousel.so") == CAROUSEL_SHA and
                parent["payloadSha256"].get(PREFIX + "libstation_frontend.so") == FRONTEND_SHA,
                "Actual parent carousel/frontend payload differs")
        raw_engines = archive.read("assets/station-online/engines.json")
        require(digest(raw_engines) == PARENT_ENGINES_SHA and sha(directory / "engines.json") == PARENT_ENGINES_SHA,
                "Parent engine asset differs from actual R132")
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
                    "Actual R132 marker/fingerprint/payload binding differs: " + kind)
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
                  "r133_retained_identity_primitives")


def policy(row):
    result = copy.deepcopy(row)
    for key in ("baseApkSha256", "payloadSha256", "productiveTransforms", "parentFingerprintSha256",
                "parentRuntimeSha256", "psxRuntimeSha256"):
        result.pop(key, None)
    return result


def transforms_for(previous, pins):
    additional = {"console-panel-r133/" + name: value for name, value in pins.items()}
    require(not set(additional).intersection(previous["psx"]["productiveTransforms"]),
            "R133 productive transforms must only append to original parent maps")
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
    require(receipt.get("schemaVersion") == 3 and receipt.get("revision") == "R133" and
            receipt.get("baseApkSha256") == BASE_SHA and receipt.get("retainedBaseSourceCommit") == BASE_SOURCE and
            receipt.get("sourceSha256") == pins and receipt.get("parentIdentityReceiptSha256") == PARENT_RECEIPT_SHA and
            receipt.get("dependencySourceSha256") == DEPENDENCY_SOURCES and receipt.get("approvedScopes") == SCOPES and
            receipt.get("registeredOnServer") is False and receipt.get("installed") is False and
            receipt.get("physicalGameplayValidated") is False, "Exact uninstalled R133 console-only identity receipt required")
    verify_source_commit(receipt["sourceCommit"], pins)
    verify_dependencies()
    native_path = Path(receipt["nativeReceiptPath"])
    require(sha(native_path) == receipt["nativeReceiptSha256"], "Native receipt changed after fingerprinting")
    native, payloads = native_inputs(native_path, receipt["sourceCommit"], pins)
    parent_path = Path(receipt["parentIdentityReceiptPath"])
    require(parent_path.name == "runtime-identity.json" and sha(parent_path) == PARENT_RECEIPT_SHA,
            "Exact original R132 parent receipt path required")
    parent, previous, original, profile, inherited = parent_inputs(base, parent_path.parent)
    actual = {**inherited, **{name: sha(path) for name, path in payloads.items()}}
    require(actual != inherited and actual == receipt["payloadSha256"] and
            receipt["newSharedPayloadSha256"] == {name: actual[name] for name in PAYLOADS} and
            receipt["preservedR132PayloadSha256"] == {name: value for name, value in inherited.items() if name not in PAYLOADS},
            "Final carousel or preserved full parent payload map changed")
    require(receipt.get("nativeInputSha256") == native["inputSha256"] and
            receipt.get("nativeTransforms") == native["transforms"] and
            receipt.get("compilationReceiptSha256") == {"native-receipt": sha(native_path)} and
            receipt.get("compilationReceiptPaths") == {"native-receipt": str(native_path.resolve())},
            "Private native inputs/transforms or compilation references changed")
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
    for flag in ("existing40DexByteIdentical", "dexClassSetsPreserved", "frontendLibraryByteIdentical",
                 "manifestByteIdentical", "resourcesAndSonyAssetsByteIdentical", "shaderCodeAndEffectsPreserved",
                 "videoBytesAndLoopPolicyPreserved", "n64DolphinCoreAndOptionsUnchanged", "snesMegadriveEntriesUnchanged",
                 "controllerProfilesUnchanged", "protocolAndTransportUnchanged", "ps3Ps4OfflineOnly"):
        require(receipt.get(flag) is True, "Retained contract flag differs: " + flag)
    require(receipt.get("ps3Ps4OnlineEnabled") is False, "Sony must remain offline")
    require(receipt.get("normalPsxLibrariesPreserved") == previous["psx"]["dependencySha256"],
            "PSX owner/core/frontend library dependencies must stay exact")
    require(not any(key in receipt for key in ("switchReceiptPath", "switchAllowedTypes", "updatedPsxFrontendDependencySha256")),
            "R133 must not introduce Switch/frontend compilation")
    manifest["assets/station-online/engines.json"] = receipt["enginesAssetSha256"]
    return receipt, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base-apk", "parent-identity", "native-receipt", "ndk", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Never overwrite a runtime identity output tree")
    pins = source_map()
    verify_source_commit(args.source_commit, pins)
    verify_dependencies()
    native, payloads = native_inputs(args.native_receipt, args.source_commit, pins)
    parent, previous, original, profile, inherited = parent_inputs(args.base_apk, args.parent_identity)
    native_hash = sha(args.native_receipt)
    actual = {**inherited, **{name: sha(path) for name, path in payloads.items()}}
    require(all(actual[name] != inherited[name] for name in PAYLOADS), "Only the scoped carousel must actually change")
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
    require(source_map() == pins and sha(args.native_receipt) == native_hash,
            "Productive R133/native inputs changed during compilation")
    native_again, payloads_again = native_inputs(args.native_receipt, args.source_commit, pins)
    require(native_again == native and payloads_again == payloads, "Compiled native artifacts changed")
    result = {
        "schemaVersion": 3, "revision": "R133", "sourceCommit": args.source_commit,
        "baseApkSha256": BASE_SHA, "retainedBaseSourceCommit": BASE_SOURCE,
        "parentRuntimeMarkers": parent["markers"],
        "parentIdentityReceiptPath": str((args.parent_identity / "runtime-identity.json").resolve()),
        "parentIdentityReceiptSha256": PARENT_RECEIPT_SHA,
        "nativeReceiptPath": str(args.native_receipt.resolve()), "nativeReceiptSha256": native_hash,
        "nativeInputSha256": native["inputSha256"], "nativeTransforms": native["transforms"],
        "compilationReceiptSha256": {"native-receipt": native_hash},
        "compilationReceiptPaths": {"native-receipt": str(args.native_receipt.resolve())},
        "markers": markers, "engines": selected, "enginesAssetSha256": sha(engines),
        "payloadSha256": actual,
        "preservedR132PayloadSha256": {name: value for name, value in inherited.items() if name not in PAYLOADS},
        "newSharedPayloadSha256": {name: sha(path) for name, path in payloads.items()},
        "sourceSha256": pins, "dependencySourceSha256": dict(DEPENDENCY_SOURCES),
        "psxControllerProfileSha256": digest(profile), "psxOptionsSha256": parent["psxOptionsSha256"],
        "normalPsxLibrariesPreserved": previous["psx"]["dependencySha256"],
        "existing40DexByteIdentical": True, "dexClassSetsPreserved": True,
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
    print(json.dumps({"revision": "R133", "engineIds": [row["engineId"] for row in selected],
                      "registeredOnServer": False, "existing40DexByteIdentical": True}))


if __name__ == "__main__":
    main()
