"""Renew four online identities for a closed R132 UI/Switch overlay on R131.

Consumes real native and scoped Switch DEX compilation receipts. The 39 other
DEX, Manifest, Sony assets, cores, profiles, options and protocols are inherited.
Only carousel/frontend, one Switch config class in DEX8, runtime identities and
the engines asset change. The Switch repair moves or deletes no user files.
This command builds identity libraries; it never signs, installs or registers.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PSX = ROOT.parent / "psx-online"
PREFIX = "lib/arm64-v8a/"
BASE_SHA = "0273ab9ae1b7ef5a061fdcc76c49558db4180bedd10a8100e6d5f764ac2ab175"
BASE_BYTES = 2711825423
BASE_SOURCE = "8503c2e32d7487d3bb31397ba9533dc7e1bfe981"
PARENT_RECEIPT_SHA = "7df6fe4ad140ff8e5cb21146e07a77345c02878500c69a1d8167f5aeccc52cc0"
PARENT_ENGINES_SHA = "0d5c548472a2878dfda801a69a87e5523b4a48bce4bde329ac2e825e0779d282"
MARKERS = {
    "psx": ("libstation_psx_online.so", "7c182b3928147af569e642d4b1951eedf60358018d8e03908e15169afbd563d9", "59070e99af1a277230119356fb76d999cba53c9392f664fcfb9f9dfc0285137c"),
    "n64": ("libstation_mupen64plus_runtime.so", "cf3c21e161fac06c094fabfbf7e349280b5e86eed89258296f85baca576602eb", "1b38302907ebb1465d4a75bb261bde4dc66b80d3f339cf144d3a5a1fd8fa2cb8"),
    "dolphin": ("libstation_dolphin_runtime.so", "cdfd3b17ee2b6c2108c47394e1a5c94a716b481ad594830b4593c618902088c5", "0e82ff640d61be586d3c8d4395216f3edfe0f6101e513ad879e6202f3d24fd90"),
}
PAYLOADS = frozenset(PREFIX + name for name in ("libturbo_carousel.so", "libstation_frontend.so"))
DEX = frozenset(["classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]])
BASE_DEX8_SHA = "1f099e70e5d5220e46fa92d6ac8743f26bd70c63f2ebc99f4316db970cad90a5"
SWITCH_TYPES = ["Lorg/emulationstation/frontend/switchengine/SwitchConfigPatcher;"]
NATIVE_SCOPES = ["shader-prewarm-loading-barrier", "sony-platform-synopses"]
SCOPES = [*NATIVE_SCOPES, "switch-empty-legacy-path-migration"]
SHARED_REPLACEMENTS = PAYLOADS | {"classes8.dex"}
DEPENDENCY_SOURCES = {
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
    "versions/station-mupen-online-r125-20261011/recipes/build_runtime_identity.py": "fdb79db3e354f3359d00980a1a00e7dec9d5fcbfed27892d4c42fbd4af1b2a16",
}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw): return hashlib.sha256(raw).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
def write(path, value): Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_map():
    """Only productive R132 sources; no evidence, receipts, tests or outputs."""
    result = {}
    suffixes = {".java", ".py", ".cpp", ".c", ".h", ".hpp", ".glsl"}
    excluded = {"tests", "evidence", "receipts", "out", "outputs", "build", "temp", "__pycache__"}
    for directory in ("java", "native", "recipe"):
        for path in sorted((ROOT / directory).rglob("*")):
            relative = path.relative_to(ROOT)
            if (path.is_file() and path.suffix in suffixes and not excluded.intersection(relative.parts)):
                if path.is_symlink(): raise ValueError("Productive source cannot be symbolic: " + relative.as_posix())
                result[relative.as_posix()] = sha(path)
    if not result or "recipe/build_runtime_identity.py" not in result:
        raise ValueError("Complete productive R132 source map required")
    return result


def verify_source_commit(commit, pins):
    if not re.fullmatch(r"[0-9a-f]{40}", commit): raise ValueError("Explicit full source commit required")
    command = ["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO)]
    relative_root = ROOT.relative_to(REPO).as_posix()
    for name, expected in pins.items():
        raw = subprocess.check_output(command + ["show", commit + ":" + relative_root + "/" + name], stderr=subprocess.PIPE)
        if digest(raw) != expected: raise ValueError("R132 source commit differs: " + name)


def checked_file(record, label):
    if (not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"} or
            not isinstance(record["bytes"], int) or record["bytes"] <= 0 or
            not re.fullmatch(r"[0-9a-f]{64}", record["sha256"])):
        raise ValueError("Exact artifact record required: " + label)
    original = Path(record["path"])
    path = original.resolve(strict=True)
    if original.is_symlink() or not path.is_file() or path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
        raise ValueError("Actual compiled artifact changed: " + label)
    return path


def archive_sha(archive, name):
    value = hashlib.sha256()
    with archive.open(name) as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""): value.update(part)
    return value.hexdigest()


def verify_dependencies():
    for name, expected in DEPENDENCY_SOURCES.items():
        if sha(REPO / name) != expected: raise ValueError("Pinned identity primitive changed: " + name)


def native_inputs(path, commit, pins):
    receipt = read(path)
    if (receipt.get("schema") != "station.startup.cleanup.native.v1" or
            receipt.get("revision") != "R132" or receipt.get("baseApkSha256") != BASE_SHA or
            receipt.get("sourceCommit") != commit or receipt.get("sourceSha256") != pins or
            receipt.get("baselineReproduced") != {"carousel": True, "frontend": True} or
            receipt.get("approvedScopes") != NATIVE_SCOPES or receipt.get("dexChanged") is not False or
            set(receipt.get("payloads", {})) != PAYLOADS or
            set(receipt.get("transforms", {})) != {"loading", "synopsis"} or
            not all(isinstance(receipt["transforms"][key], dict) and receipt["transforms"][key] for key in ("loading", "synopsis")) or
            not isinstance(receipt.get("inputSha256"), dict) or not receipt["inputSha256"] or
            not isinstance(receipt.get("frontendInputSha256"), dict) or not receipt["frontendInputSha256"]):
        raise ValueError("Closed native-only R132 compilation receipt required")
    for field in ("inputSha256", "frontendInputSha256"):
        if any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in receipt[field].values()):
            raise ValueError("Exact retained native input hashes required")
    return receipt, {name: checked_file(record, name) for name, record in receipt["payloads"].items()}


def switch_inputs(path, commit, pins):
    """Accept only the independently checked config-patcher DEX8 overlay."""
    receipt = read(path)
    if (receipt.get("schema") != "station.startup.cleanup.switch.v1" or
            receipt.get("revision") != "R132" or receipt.get("baseApkSha256") != BASE_SHA or
            receipt.get("sourceCommit") != commit or receipt.get("sourceSha256") != pins or
            set(receipt.get("payloads", {})) != {"classes8.dex"} or
            receipt.get("baselineDexSha256") != BASE_DEX8_SHA or receipt.get("allowedTypes") != SWITCH_TYPES or
            receipt.get("newSwitchRoot") != "roms/switch" or
            receipt.get("migrationLegacyRoot") != "SAMBOX-Vfull/sistema/roms/switch"):
        raise ValueError("Exact R132 Switch configuration DEX8 receipt required")
    for flag in ("classSetExactlyPreserved", "unrelatedClassesByteIdentical",
            "originalEngineCommandsPreserved", "noFilesMovedOrDeleted", "onlyExactEmptyLegacyPathMigrated"):
        if receipt.get(flag) is not True: raise ValueError("Switch scope assertion differs: " + flag)
    payload = checked_file(receipt["payloads"]["classes8.dex"], "classes8.dex")
    with payload.open("rb") as stream: magic = stream.read(8)
    if not re.fullmatch(rb"dex\n0[0-9]{2}\x00", magic) or sha(payload) == BASE_DEX8_SHA:
        raise ValueError("A changed actual Android DEX8 artifact is required")
    return receipt, {"classes8.dex": payload}


def parent_inputs(base, directory):
    """Check parent receipts, all 344 payloads and fingerprints against real APK."""
    if Path(base).stat().st_size != BASE_BYTES or sha(base) != BASE_SHA:
        raise ValueError("Exact corrected, signed R131 donor required")
    receipt_path = directory / "runtime-identity.json"
    parent = read(receipt_path)
    if (sha(receipt_path) != PARENT_RECEIPT_SHA or parent.get("revision") != "R131" or
            parent.get("sourceCommit") != BASE_SOURCE or set(parent.get("markers", {})) != set(MARKERS) or
            len(parent.get("payloadSha256", {})) != 344 or parent.get("ps3Ps4OfflineOnly") is not True or
            parent.get("ps3Ps4OnlineEnabled") is not False):
        raise ValueError("Exact corrected R131 identity receipt required")
    fingerprints = {}
    with zipfile.ZipFile(base) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} != DEX:
            raise ValueError("Unique exact 40-DEX R131 archive required")
        for name, expected in parent["payloadSha256"].items():
            if archive_sha(archive, name) != expected: raise ValueError("Actual parent payload differs: " + name)
        raw_engines = archive.read("assets/station-online/engines.json")
        if digest(raw_engines) != PARENT_ENGINES_SHA or sha(directory / "engines.json") != PARENT_ENGINES_SHA:
            raise ValueError("Parent engine asset differs from actual R131")
        engines = json.loads(raw_engines)
        current = [row for row in engines["engines"] if row["platform"] in {"psx", "n64", "gamecube", "wii"}]
        if current != parent["engines"]: raise ValueError("Parent engine receipt differs from actual APK asset")
        for kind, (library, runtime_hash, fingerprint_hash) in MARKERS.items():
            filename = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
            raw = (directory / filename).read_bytes().rstrip(b"\r\n")
            value = json.loads(raw)
            binary = archive.read(PREFIX + library)
            if (raw != canonical(value) or digest(raw) != fingerprint_hash or raw not in binary or
                    digest(binary) != runtime_hash or parent["markers"][kind]["runtimeSha256"] != runtime_hash or
                    parent["markers"][kind]["fingerprintSha256"] != fingerprint_hash or
                    value.get("payloadSha256") != parent["payloadSha256"]):
                raise ValueError("Actual R131 runtime/fingerprint/payload binding differs: " + kind)
            for name, expected in value["dependencySha256"].items():
                if archive_sha(archive, PREFIX + name) != expected: raise ValueError("Parent dependency differs: " + name)
            fingerprints[kind] = value
        for entry in current:
            if archive_sha(archive, PREFIX + entry["library"]) != entry["coreSha256"]:
                raise ValueError("Actual parent core differs: " + entry["platform"])
            for name, expected in entry["dependencySha256"].items():
                if archive_sha(archive, PREFIX + name) != expected: raise ValueError("Actual engine dependency differs: " + name)
        profile = (directory / "psx-controller-profile.json").read_bytes().rstrip(b"\r\n")
        if digest(profile) != parent["psxControllerProfileSha256"]:
            raise ValueError("Exact parent PSX controller profile required")
        inherited = dict(parent["payloadSha256"])
        inherited[PREFIX + "libstation_frontend.so"] = archive_sha(archive, PREFIX + "libstation_frontend.so")
    first = fingerprints["psx"]
    if any(value["javaSources"] != first["javaSources"] or value["productiveTransforms"] != first["productiveTransforms"] for value in fingerprints.values()):
        raise ValueError("Parent effective source maps disagree")
    # Rebuild only the unchanged PSX SDL/protocol entry with a new manifest literal.
    for name in ("StationPsxEntry.cpp", "StationPsxOwner.cpp", "StationPsxOwner.hpp", "StationPsxProtocol.cpp", "StationPsxProtocol.hpp", "StationPsxSha256.cpp", "PsxPinnedOptions.h"):
        if sha(PSX / "native" / name) != first["productiveTransforms"].get("native/" + name):
            raise ValueError("Pinned PSX native source changed: " + name)
    bridge = PSX / "java/org/emulationstation/frontend/netplay/StationPsxBridge.java"
    bridge_key = "netplay-src/org/emulationstation/frontend/netplay/StationPsxBridge.java"
    if sha(bridge) != first["javaSources"].get(bridge_key):
        raise ValueError("Pinned PSX JNI declaration source changed")
    return parent, fingerprints, engines, profile, inherited


def import_markers():
    path = REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py"
    spec = importlib.util.spec_from_file_location("r132_retained_identity_primitives", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def policy(row, kind):
    result = copy.deepcopy(row)
    for key in ("baseApkSha256", "payloadSha256", "productiveTransforms", "parentFingerprintSha256", "parentRuntimeSha256", "psxRuntimeSha256"):
        result.pop(key, None)
    if kind == "psx": result["dependencySha256"].pop("libstation_frontend.so")
    return result


def validate_inputs(base, identity_path):
    """Recheck closed inputs/output bytes; return receipt and ZIP-entry SHA map.

    No native compilation, Android operation or mutation occurs here. The
    assembler must preserve donor entries not listed as replacements and use
    the conventional marker paths, not substitute libraries found elsewhere.
    """
    identity_path = Path(identity_path)
    directory = identity_path.parent
    receipt = read(identity_path)
    pins = source_map()
    if (receipt.get("schemaVersion") != 3 or receipt.get("revision") != "R132" or
            receipt.get("baseApkSha256") != BASE_SHA or receipt.get("sourceSha256") != pins or
            receipt.get("retainedBaseSourceCommit") != BASE_SOURCE or
            receipt.get("registeredOnServer") is not False or receipt.get("installed") is not False or
            receipt.get("physicalGameplayValidated") is not False or
            receipt.get("approvedScopes") != SCOPES or
            receipt.get("parentIdentityReceiptSha256") != PARENT_RECEIPT_SHA or
            receipt.get("dependencySourceSha256") != DEPENDENCY_SOURCES):
        raise ValueError("Exact uninstalled R132 UI/Switch identity receipt required")
    verify_source_commit(receipt["sourceCommit"], pins)
    verify_dependencies()
    native_path = Path(receipt["nativeReceiptPath"])
    if sha(native_path) != receipt["nativeReceiptSha256"]:
        raise ValueError("Native compilation receipt changed after fingerprinting")
    _, native_payloads = native_inputs(native_path, receipt["sourceCommit"], pins)
    switch_path = Path(receipt["switchReceiptPath"])
    if sha(switch_path) != receipt["switchReceiptSha256"]:
        raise ValueError("Switch DEX compilation receipt changed after fingerprinting")
    switch, switch_payloads = switch_inputs(switch_path, receipt["sourceCommit"], pins)
    parent_path = Path(receipt["parentIdentityReceiptPath"])
    if parent_path.name != "runtime-identity.json" or sha(parent_path) != PARENT_RECEIPT_SHA:
        raise ValueError("Exact corrected R131 parent receipt path required")
    parent, previous, original, profile, inherited = parent_inputs(base, parent_path.parent)
    if inherited.get("classes8.dex") != BASE_DEX8_SHA:
        raise ValueError("Parent DEX8 baseline differs")
    actual = {**inherited, **{name: sha(path) for name, path in {**native_payloads, **switch_payloads}.items()}}
    if actual != receipt["payloadSha256"] or receipt["newSharedPayloadSha256"] != {name: actual[name] for name in SHARED_REPLACEMENTS}:
        raise ValueError("Final native/preserved payload map changed")
    expected_preserved = {name: checksum for name, checksum in inherited.items() if name not in SHARED_REPLACEMENTS}
    if receipt["preservedR131PayloadSha256"] != expected_preserved:
        raise ValueError("Preserved exact 39 other DEX/Manifest/Sony asset map changed")
    if (receipt.get("switchBaselineDexSha256") != BASE_DEX8_SHA or
            receipt.get("switchAllowedTypes") != SWITCH_TYPES or
            receipt.get("compilationReceiptSha256") != {"native-receipt": sha(native_path), "switch-receipt": sha(switch_path)} or
            receipt.get("compilationReceiptPaths") != {"native-receipt": str(native_path.resolve()), "switch-receipt": str(switch_path.resolve())}):
        raise ValueError("Exact compilation references or DEX8 scope changed")
    if receipt.get("parentRuntimeMarkers") != parent["markers"] or set(receipt.get("markers", {})) != set(MARKERS):
        raise ValueError("Parent/new marker sets differ")
    transforms = {**previous["psx"]["productiveTransforms"],
        **{"startup-cleanup-r132/" + name: value for name, value in pins.items()}}
    manifest = dict(actual)
    for kind, (library, _, _) in MARKERS.items():
        filename = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
        raw = (directory / filename).read_bytes().rstrip(b"\r\n")
        value = json.loads(raw)
        expected = copy.deepcopy(previous[kind])
        expected.update(baseApkSha256=BASE_SHA, payloadSha256=actual, productiveTransforms=transforms)
        if kind == "psx": expected["dependencySha256"]["libstation_frontend.so"] = actual[PREFIX + "libstation_frontend.so"]
        else:
            expected.update(parentFingerprintSha256=MARKERS[kind][2], parentRuntimeSha256=MARKERS[kind][1],
                psxRuntimeSha256=receipt["markers"]["psx"]["runtimeSha256"])
        binary = directory / "native" / library if kind == "psx" else directory / library
        marker = receipt["markers"][kind]
        if (raw != canonical(expected) or value != expected or raw not in binary.read_bytes() or
                marker["runtimeLibrary"] != library or sha(binary) != marker["runtimeSha256"] or
                binary.stat().st_size != marker["runtimeBytes"] or digest(raw) != marker["fingerprintSha256"]):
            raise ValueError("Actual new marker/fingerprint differs: " + kind)
        manifest[PREFIX + library] = marker["runtimeSha256"]
    updated = copy.deepcopy(original)
    selected = []
    for entry in updated["engines"]:
        platform = entry["platform"]
        if platform not in {"psx", "n64", "gamecube", "wii"}: continue
        kind = "dolphin" if platform in {"gamecube", "wii"} else platform
        marker = receipt["markers"][kind]
        prefix = "pcsx-rearmed-ff81ed17-player-v3-" if kind == "psx" else "mupen64plus-ae-33bf7021-n64-v3-" if kind == "n64" else "dolphin-5102a033-" + platform + "-v3-"
        entry.update(engineId=prefix + marker["runtimeSha256"][:12], runtimeSha256=marker["runtimeSha256"])
        if kind == "psx": entry["dependencySha256"]["libstation_frontend.so"] = actual[PREFIX + "libstation_frontend.so"]
        selected.append(entry)
    engines = directory / "engines.json"
    if (read(engines) != updated or receipt["engines"] != selected or len(selected) != 4 or
            sha(engines) != receipt["enginesAssetSha256"] or engines.stat().st_size > 32768 or
            (directory / "psx-controller-profile.json").read_bytes() != profile + b"\n" or
            receipt["psxControllerProfileSha256"] != parent["psxControllerProfileSha256"] or
            receipt["psxOptionsSha256"] != parent["psxOptionsSha256"]):
        raise ValueError("Actual engine IDs/dependencies or retained controller profile changed")
    for flag in ("existing39OtherDexByteIdentical", "dexClassSetsPreserved", "unrelatedDex8ClassesByteIdentical",
            "switchNoFilesMovedOrDeleted", "switchOnlyExactEmptyLegacyPathMigrated",
            "manifestByteIdentical", "resourcesAndSonyAssetsByteIdentical",
            "n64DolphinCoreAndOptionsUnchanged", "snesMegadriveEntriesUnchanged", "controllerProfilesUnchanged",
            "protocolAndTransportUnchanged", "ps3Ps4OfflineOnly"):
        if receipt.get(flag) is not True: raise ValueError("Retained contract flag differs: " + flag)
    if receipt.get("ps3Ps4OnlineEnabled") is not False: raise ValueError("Sony must remain offline")
    if "existing40DexByteIdentical" in receipt:
        raise ValueError("DEX8 changed; an unchanged-40-DEX assertion would be false")
    manifest["assets/station-online/engines.json"] = receipt["enginesAssetSha256"]
    return receipt, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base-apk", "parent-identity", "native-receipt", "switch-receipt", "ndk", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if args.out.exists(): raise ValueError("Never overwrite a runtime identity output tree")
    pins = source_map()
    verify_source_commit(args.source_commit, pins)
    verify_dependencies()
    native, payloads = native_inputs(args.native_receipt, args.source_commit, pins)
    switch, switch_payloads = switch_inputs(args.switch_receipt, args.source_commit, pins)
    parent, previous, original_engines, profile, inherited = parent_inputs(args.base_apk, args.parent_identity)
    if inherited.get("classes8.dex") != BASE_DEX8_SHA:
        raise ValueError("Parent DEX8 baseline differs")
    native_receipt_hash = sha(args.native_receipt)
    switch_receipt_hash = sha(args.switch_receipt)
    actual_payloads = {**inherited, **{name: sha(path) for name, path in {**payloads, **switch_payloads}.items()}}
    if any(actual_payloads[name] == inherited[name] for name in SHARED_REPLACEMENTS):
        raise ValueError("All three scoped UI/Switch payloads must actually differ from R131")
    transforms = {**previous["psx"]["productiveTransforms"],
        **{"startup-cleanup-r132/" + name: value for name, value in pins.items()}}
    args.out.mkdir(parents=True)
    fingerprints = {}
    markers = {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE_SHA, payloadSha256=actual_payloads, productiveTransforms=transforms)
    psx["dependencySha256"]["libstation_frontend.so"] = actual_payloads[PREFIX + "libstation_frontend.so"]
    raw = canonical(psx)
    (args.out / "psx.fingerprint.json").write_bytes(raw + b"\n")
    identity_source = args.out / "StationPsxIdentity.cpp"
    identity_source.write_text('extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n', encoding="ascii")
    native_out = args.out / "native"
    subprocess.run([sys.executable, str(PSX / "recipe/build_entry.py"), "--ndk", str(args.ndk),
        "--owner", str(PSX / "native"), "--protocol", str(PSX / "native"), "--pinned-options", str(PSX / "native"),
        "--identity-source", str(identity_source), "--out", str(native_out)], check=True)
    runtime = native_out / "libstation_psx_online.so"
    if raw not in runtime.read_bytes(): raise ValueError("New PSX entry lacks the exact canonical fingerprint")
    markers["psx"] = {"runtimeLibrary": runtime.name, "runtimeSha256": sha(runtime), "runtimeBytes": runtime.stat().st_size,
        "fingerprintSha256": digest(raw)}
    fingerprints["psx"] = psx
    primitive = import_markers()
    for kind in ("n64", "dolphin"):
        value = copy.deepcopy(previous[kind])
        value.update(baseApkSha256=BASE_SHA, payloadSha256=actual_payloads, productiveTransforms=transforms,
            parentFingerprintSha256=MARKERS[kind][2], parentRuntimeSha256=MARKERS[kind][1],
            psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        library = MARKERS[kind][0]
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, args.ndk, args.out)
        fingerprints[kind] = value
    for kind, value in fingerprints.items():
        if policy(previous[kind], kind) != policy(value, kind): raise ValueError("Retained runtime policy changed: " + kind)
    updated = copy.deepcopy(original_engines)
    selected = []
    for before, after in zip(original_engines["engines"], updated["engines"]):
        platform = after["platform"]
        if platform not in {"psx", "n64", "gamecube", "wii"}: continue
        kind = "dolphin" if platform in {"gamecube", "wii"} else platform
        after["runtimeSha256"] = markers[kind]["runtimeSha256"]
        prefix = "pcsx-rearmed-ff81ed17-player-v3-" if kind == "psx" else "mupen64plus-ae-33bf7021-n64-v3-" if kind == "n64" else "dolphin-5102a033-" + platform + "-v3-"
        after["engineId"] = prefix + markers[kind]["runtimeSha256"][:12]
        if kind == "psx": after["dependencySha256"]["libstation_frontend.so"] = actual_payloads[PREFIX + "libstation_frontend.so"]
        strip = lambda row: {key: val for key, val in row.items() if key not in {"engineId", "runtimeSha256"}}
        left, right = copy.deepcopy(strip(before)), copy.deepcopy(strip(after))
        if kind == "psx":
            left["dependencySha256"].pop("libstation_frontend.so")
            right["dependencySha256"].pop("libstation_frontend.so")
        if left != right or before["engineId"] == after["engineId"]: raise ValueError("Existing engine contract changed: " + platform)
        selected.append(after)
    if {entry["platform"] for entry in selected} != {"psx", "n64", "gamecube", "wii"} or len(selected) != 4:
        raise ValueError("Exactly four existing online identities required")
    engines = args.out / "engines.json"
    write(engines, updated)
    if engines.stat().st_size > 32768: raise ValueError("Engine asset size exceeds client contract")
    (args.out / "psx-controller-profile.json").write_bytes(profile + b"\n")
    verify_dependencies()
    if (source_map() != pins or sha(args.native_receipt) != native_receipt_hash or
            sha(args.switch_receipt) != switch_receipt_hash):
        raise ValueError("Productive R132 inputs changed during identity compilation")
    native_again, paths_again = native_inputs(args.native_receipt, args.source_commit, pins)
    if native_again != native or paths_again != payloads: raise ValueError("Compiled native artifacts changed")
    switch_again, switch_paths_again = switch_inputs(args.switch_receipt, args.source_commit, pins)
    if switch_again != switch or switch_paths_again != switch_payloads:
        raise ValueError("Compiled Switch DEX artifact changed")
    result = {"schemaVersion": 3, "revision": "R132", "sourceCommit": args.source_commit,
        "baseApkSha256": BASE_SHA, "retainedBaseSourceCommit": BASE_SOURCE,
        "r131ParentIdentityReceiptSha256": PARENT_RECEIPT_SHA, "parentRuntimeMarkers": parent["markers"],
        "parentIdentityReceiptPath": str((args.parent_identity / "runtime-identity.json").resolve()),
        "parentIdentityReceiptSha256": PARENT_RECEIPT_SHA,
        "nativeReceiptPath": str(args.native_receipt.resolve()), "nativeReceiptSha256": native_receipt_hash,
        "switchReceiptPath": str(args.switch_receipt.resolve()), "switchReceiptSha256": switch_receipt_hash,
        "switchBaselineDexSha256": BASE_DEX8_SHA, "switchAllowedTypes": SWITCH_TYPES,
        "markers": markers, "engines": selected, "enginesAssetSha256": sha(engines),
        "payloadSha256": actual_payloads, "preservedR131PayloadSha256": {name: checksum for name, checksum in inherited.items() if name not in SHARED_REPLACEMENTS},
        "newSharedPayloadSha256": {name: sha(path) for name, path in {**payloads, **switch_payloads}.items()},
        "sourceSha256": pins, "dependencySourceSha256": dict(DEPENDENCY_SOURCES),
        "compilationReceiptSha256": {"native-receipt": native_receipt_hash, "switch-receipt": switch_receipt_hash},
        "compilationReceiptPaths": {"native-receipt": str(args.native_receipt.resolve()), "switch-receipt": str(args.switch_receipt.resolve())},
        "psxControllerProfileSha256": digest(profile), "psxOptionsSha256": parent["psxOptionsSha256"],
        "normalPsxLibrariesPreserved": {name: checksum for name, checksum in previous["psx"]["dependencySha256"].items() if name != "libstation_frontend.so"},
        "updatedPsxFrontendDependencySha256": actual_payloads[PREFIX + "libstation_frontend.so"],
        "existing39OtherDexByteIdentical": True, "dexClassSetsPreserved": True, "unrelatedDex8ClassesByteIdentical": True,
        "switchNoFilesMovedOrDeleted": True, "switchOnlyExactEmptyLegacyPathMigrated": True,
        "manifestByteIdentical": True, "resourcesAndSonyAssetsByteIdentical": True,
        "n64DolphinCoreAndOptionsUnchanged": True, "snesMegadriveEntriesUnchanged": True,
        "controllerProfilesUnchanged": True, "protocolAndTransportUnchanged": True,
        "ps3Ps4OfflineOnly": True, "ps3Ps4OnlineEnabled": False,
        "registeredOnServer": False, "installed": False, "physicalGameplayValidated": False,
        "approvedScopes": SCOPES}
    write(args.out / "runtime-identity.json", result)
    print(json.dumps({"revision": "R132", "engineIds": [row["engineId"] for row in selected], "registeredOnServer": False}))


if __name__ == "__main__": main()
