"""Closed R131 assembly: add internal Sony owners and renew four shared IDs.

The exact installed R130 donor remains authoritative for all 39 existing DEX,
resources, offline cores, UI, videos, LEDs, cache and controls. Signing,
installation and server activation are outside this recipe.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import re
import struct
import zipfile


def runtime_module():
    path = Path(__file__).with_name("build_runtime_identity.py")
    spec = importlib.util.spec_from_file_location("r131_runtime_contract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assembler(identity_path):
    identity = runtime_module()
    module = identity.legacy("assemble_apk")
    module.BASE_SHA = identity.BASE_SHA
    module.REPLACED = frozenset({"AndroidManifest.xml", "assets/station-online/engines.json",
        *[identity.PREFIX + name for name in identity.MARKERS.values()]})
    runtime = module.read(identity_path)
    shared_names = set(runtime.get("newSharedPayloadSha256", {}))
    module.ADDED = frozenset(shared_names - {"AndroidManifest.xml"})
    if (len(module.ADDED) != 300 or "classes40.dex" not in module.ADDED or
            any(not name.startswith(("assets/sony/ps3/", "assets/sony/ps4/"))
                for name in module.ADDED - {"classes40.dex"})):
        raise ValueError("Only DEX40 and the exact 299 prepared Sony assets may be added")
    module.PAYLOADS = module.REPLACED | module.ADDED
    module.SHARED = frozenset(shared_names)

    def current_sources():
        java, inherited = identity.parent_sources()
        return java, identity.productive_transforms(inherited)
    module.current_sources = current_sources

    original_engine_guard = module.engine_manifest
    def engine_manifest(original, updated, receipt):
        original_engine_guard(original, updated, receipt)
        strip = lambda row: {key: value for key, value in row.items()
            if key not in {"engineId", "runtimeSha256"}}
        for before, after in zip(original["engines"], updated["engines"]):
            if strip(before) != strip(after):
                raise ValueError("Engine core/options/profile/capacity/transport changed: " + before["platform"])
            if before["platform"] in {"psx", "n64", "gamecube", "wii"}:
                if before["engineId"] == after["engineId"] or before["runtimeSha256"] == after["runtimeSha256"]:
                    raise ValueError("Shared identity was not renewed")
        return updated
    module.engine_manifest = engine_manifest

    def inputs(base, freeze_path, identity_path, prepared_freeze=None):
        if module.fs(base).stat().st_size != identity.BASE_BYTES or module.sha(base) != identity.BASE_SHA:
            raise ValueError("Exact installed R130 donor required")
        frozen = module.read(freeze_path) if prepared_freeze is None else prepared_freeze
        receipt = module.read(identity_path)
        if (frozen.get("schemaVersion") != 1 or frozen.get("revision") != "R131" or
                frozen.get("sourceFrozen") is not True or frozen.get("baseApkSha256") != identity.BASE_SHA or
                receipt.get("revision") != "R131" or receipt.get("baseApkSha256") != identity.BASE_SHA or
                receipt.get("schemaVersion") != 3 or frozen.get("identityReceiptSha256") != module.sha(identity_path)):
            raise ValueError("Exact final R131 source freeze and identity required")
        if (not re.fullmatch(r"[0-9a-f]{40}", receipt.get("sourceCommit", "")) or
                receipt.get("sourceSha256") != identity.source_map() or receipt.get("ps3Ps4OfflineOnly") is not True or
                receipt.get("dependencySourceSha256") != identity.dependency_source_map() or
                receipt.get("ps3Ps4OnlineEnabled") is not False or receipt.get("existing39DexByteIdentical") is not True or
                receipt.get("newHostCompilerProducedExistingDex") is not False):
            raise ValueError("Productive sources or isolated internal-Sony scope differ")
        if set(frozen.get("payloads", {})) != module.PAYLOADS:
            raise ValueError("Exactly five replacements and 300 additions required")
        paths, expected = {}, {}
        for name, record in frozen["payloads"].items():
            paths[name] = identity.check_file(record, name)
            expected[name] = record["sha256"]
        names = ("assets-receipt", "host-receipt", "manifest-receipt", "derived-receipt", "child-receipt")
        if (set(receipt.get("compilationReceiptPaths", {})) != set(names) or
                set(receipt.get("compilationReceiptSha256", {})) != set(names)):
            raise ValueError("Five exact private compilation receipts required")
        compilation_paths = [Path(receipt["compilationReceiptPaths"][name]) for name in names]
        for name, path in zip(names, compilation_paths):
            if module.sha(path) != receipt["compilationReceiptSha256"][name]:
                raise ValueError("Compilation receipt changed after identity: " + name)
        shared, inherited, compiled = identity.compilation(base, *compilation_paths)
        if receipt.get("preservedR130PayloadSha256") != inherited:
            raise ValueError("Inherited actual R130 payload pins differ")
        shared_pins = {name: module.sha(path) for name, path in shared.items()}
        if (receipt.get("newSharedPayloadSha256") != shared_pins or set(shared) != module.SHARED or
                any(expected[name] != shared_pins[name] or paths[name] != shared[name] for name in shared)):
            raise ValueError("Actual host/manifest/assets differ from frozen shared bundle")
        bundle = {**inherited, **shared_pins}
        if receipt.get("payloadSha256") != bundle:
            raise ValueError("Fingerprint bundle differs from actual donor plus compiled additions")
        parent_dir = Path(receipt["r130ParentIdentityDirectory"])
        parent, parent_values, inherited_sources = identity.parents(base, parent_dir)
        if (module.sha(parent_dir / "runtime-identity.json") != receipt["r130ParentIdentityReceiptSha256"] or
                module.sha(parent_dir / "java-effective-receipt.json") != receipt["r130JavaEffectiveReceiptSha256"] or
                receipt.get("r130JavaReceiptUnmodified") is not True):
            raise ValueError("Inherited effective R130 Java/identity receipt changed")
        parent_java = module.read(parent_dir / "java-effective-receipt.json")
        if (parent_java.get("classes35Sha256") != inherited["classes35.dex"] or
                parent_java.get("receiptKind") != "base-java-compilation-plus-scoped-dex35-overlay" or
                parent_java.get("compileOnlyStubsPackaged") is not False or
                parent_java.get("composition", {}).get("baseCompilerProducedOverlayDex") is not False):
            raise ValueError("Existing DEX35 requires its original effective R130 compilation attribution")
        if set(receipt.get("markers", {})) != set(identity.MARKERS):
            raise ValueError("Only the existing three identity ELF libraries may be renewed")
        sources = current_sources()
        for kind, library in identity.MARKERS.items():
            marker = receipt["markers"][kind]
            if marker["runtimeLibrary"] != library or expected[identity.PREFIX + library] != marker["runtimeSha256"]:
                raise ValueError("Actual identity ELF differs: " + kind)
            filename = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
            raw = module.fs(identity_path.parent / filename).read_bytes().rstrip(b"\r\n")
            value = json.loads(raw)
            binary = module.fs(paths[identity.PREFIX + library]).read_bytes()
            if (raw != module.canonical(value) or module.digest(raw) != marker["fingerprintSha256"] or
                    raw not in binary or marker["fingerprintSha256"].encode("ascii") not in binary or
                    value["baseApkSha256"] != identity.BASE_SHA or value["payloadSha256"] != bundle or
                    (value["javaSources"], value["productiveTransforms"]) != sources):
                raise ValueError("Runtime does not bind exact frozen shared bytes and productive sources")
            if binary[:6] != b"\x7fELF\x02\x01" or len(binary) < 64 or struct.unpack_from("<H", binary, 18)[0] != 183:
                raise ValueError("Identity runtime must be an AArch64 ELF")
            phoff = struct.unpack_from("<Q", binary, 32)[0]
            stride, count = struct.unpack_from("<HH", binary, 54)
            if not count or stride < 56 or phoff + stride * count > len(binary):
                raise ValueError("Truncated identity ELF program headers")
            loads = []
            for index in range(count):
                at = phoff + stride * index
                if struct.unpack_from("<I", binary, at)[0] == 1:
                    offset, vaddr = struct.unpack_from("<QQ", binary, at + 8)
                    align = struct.unpack_from("<Q", binary, at + 48)[0]
                    loads.append(align)
                    if align < 16384 or align & (align - 1) or (vaddr-offset) % align:
                        raise ValueError("Identity ELF PT_LOAD is not 16KiB compatible")
            if not loads: raise ValueError("Identity runtime has no PT_LOAD")
            if kind != "psx":
                if (value["parentRuntimeSha256"] != identity.PARENT_MARKER_SHA[kind] or
                        value["parentFingerprintSha256"] != identity.PARENT_FINGERPRINT_SHA[kind] or
                        value["psxRuntimeSha256"] != receipt["markers"]["psx"]["runtimeSha256"]):
                    raise ValueError("Renewed identity does not bind the exact R130 parent/PSX runtime")
                changed_keys = {"schemaVersion", "baseApkSha256", "payloadSha256", "preservedPayloadSha256",
                    "javaSources", "productiveTransforms", "parentRuntimeSha256", "parentFingerprintSha256",
                    "psxRuntimeSha256"}
                strip = lambda row: {key: val for key, val in row.items() if key not in changed_keys}
                if strip(value) != strip(parent_values[kind]):
                    raise ValueError("Renewed identity changed an existing owner/core/options contract")
        engines_name = "assets/station-online/engines.json"
        if expected[engines_name] != receipt["enginesAssetSha256"] or paths[engines_name].stat().st_size > 32768:
            raise ValueError("Actual engine asset differs from bound identity or existing size limit")
        policy = module.read(module.ROOT / "profile.json")
        psx = module.read(identity_path.parent / "psx.fingerprint.json")
        if (psx["backend"] != policy["backend"] or psx["options"] != policy["options"] or
                psx["optionsSha256"] != policy["optionsSha256"] or psx["inputDelayFrames"] != 4 or
                receipt["normalPsxLibrariesPreserved"] != module.NORMAL_PINS):
            raise ValueError("Normal PSX owner/core/options/profile changed")
        with zipfile.ZipFile(module.fs(base)) as original:
            entries = module.classic_entries(original)
            module.classic_zip(base, original.comment)
            if not module.REPLACED.issubset(entries) or module.ADDED & entries:
                raise ValueError("Donor entry set escaped the declared R131 scope")
            for name, checksum in module.NORMAL_PINS.items():
                if module.entry_sha(original, identity.PREFIX + name) != checksum:
                    raise ValueError("Normal PSX library changed: " + name)
            manifest = engine_manifest(json.loads(original.read(engines_name)), module.read(paths[engines_name]), receipt)
            for engine in receipt["engines"]:
                pins = {engine["library"]: engine["coreSha256"], engine["runtimeLibrary"]: engine["runtimeSha256"],
                    **engine.get("dependencySha256", {})}
                for library, checksum in pins.items():
                    if "/" in library or "\\" in library: raise ValueError("Native dependency must be a basename")
                    name = identity.PREFIX + library
                    actual = expected[name] if name in expected else module.entry_sha(original, name)
                    if actual != checksum: raise ValueError("Existing online core/dependency changed: " + library)
        return frozen, receipt, paths, expected, manifest
    module.inputs = inputs
    original_package = module.package
    def package(base, freeze_path, identity_path, out):
        result = original_package(base, freeze_path, identity_path, out)
        path = out.resolve().with_suffix(".package.json")
        report = module.read(path)
        report.update({"sourceCommit": module.read(identity_path)["sourceCommit"],
            "internalSonyOwnersAdded": True, "existing39DexByteIdentical": True,
            "existingResourcesAndCarouselByteIdentical": True, "ps3Ps4OfflineOnly": True,
            "externalSonyEmulatorInvoked": False, "sonyFirmwareImported": False,
            "sonyAndroidBootstrapValidated": False, "physicalThermalValidated": False})
        module.write(path, report)
        return result
    module.package = package
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "freeze", "identity-receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--out", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check-inputs", action="store_true")
    group.add_argument("--write-freeze", action="store_true")
    parser.add_argument("--payload", action="append", default=[])
    args = parser.parse_args()
    package = assembler(args.identity_receipt)
    if args.write_freeze:
        if args.out: parser.error("Freeze writes no APK")
        result = package.freeze_inputs(args.base, args.identity_receipt, args.payload, args.freeze)
    elif args.check_inputs:
        if args.payload or args.out: parser.error("Input verification writes no APK")
        _, receipt, _, _, _ = package.inputs(args.base, args.freeze, args.identity_receipt)
        result = {"inputsVerified": True, "engineIds": [row["engineId"] for row in receipt["engines"]], "apkWritten": False}
    else:
        if args.out is None or args.payload: parser.error("Assembly requires only --out")
        result = package.package(args.base, args.freeze, args.identity_receipt, args.out)
    print(json.dumps(result))


if __name__ == "__main__": main()
