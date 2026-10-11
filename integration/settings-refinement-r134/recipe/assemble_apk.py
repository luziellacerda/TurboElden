"""Seven closed R134 substitutions over the exact signed R133; zero additions."""
from pathlib import Path
import argparse
import json
import types
from common import *

PREFIX = "lib/arm64-v8a/"
REPLACED = frozenset({"classes28.dex", "classes40.dex", "assets/station-online/engines.json", *[PREFIX + name for name in (
    "libturbo_carousel.so", "libstation_psx_online.so", "libstation_mupen64plus_runtime.so", "libstation_dolphin_runtime.so")]})
LEGACY_SHA = "1d8c07e825fd28da68381a5e3b41cc9e6191cb6669ece1ff8f9a98624855f7a1"


def runtime():
    return module(ROOT / "recipe/build_runtime_identity.py", "r134_identity")


def assembler():
    primitive = REPO / "integration/psx-online/recipe/assemble_apk.py"
    require(sha(primitive) == LEGACY_SHA, "Pinned streaming ZIP primitive changed")
    result = types.ModuleType("r134_streaming_zip")
    result.__file__ = str(primitive)
    exec(compile(primitive.read_text(encoding="utf-8").replace('"R127"', '"R134"'), str(primitive), "exec"), result.__dict__)
    result.BASE_SHA = BASE_SHA
    result.REPLACED = REPLACED
    result.ADDED = frozenset()
    result.PAYLOADS = REPLACED
    result.inputs = inputs
    return result


def paths_for(receipt, identity):
    native = read(receipt["nativeReceiptPath"])
    paths = {name: Path(record["path"]) for name, record in native["payloads"].items()}
    directory = Path(identity).parent
    paths["assets/station-online/engines.json"] = directory / "engines.json"
    for kind, marker in receipt["markers"].items():
        library = marker["runtimeLibrary"]
        paths[PREFIX + library] = directory / "native" / library if kind == "psx" else directory / library
    require(set(paths) == REPLACED, "Seven exact conventional replacements required")
    return paths


def inputs(base, freeze_path, identity_path, prepared_freeze=None):
    receipt, manifest = runtime().validate_inputs(base, identity_path)
    frozen = read(freeze_path) if prepared_freeze is None else prepared_freeze
    require(frozen.get("schemaVersion") == 1 and frozen.get("revision") == "R134" and frozen.get("sourceFrozen") is True and
            frozen.get("baseApkSha256") == BASE_SHA and frozen.get("identityReceiptSha256") == sha(identity_path) and
            frozen.get("sourceCommit") == receipt["sourceCommit"] and frozen.get("sourceSha256") == receipt["sourceSha256"] and
            frozen.get("nativeReceiptSha256") == receipt["nativeReceiptSha256"] and
            frozen.get("payloadReceiptSha256") == receipt["payloadReceiptSha256"] and
            frozen.get("compilationReceiptSchema") == receipt["compilationReceiptSchema"] and
            frozen.get("nativeInputSha256") == receipt["nativeInputSha256"] and
            frozen.get("nativeTransforms") == receipt["nativeTransforms"] and frozen.get("dexScopes") == receipt["dexScopes"],
            "Closed R134 productive/scoped compilation freeze differs")
    paths = paths_for(receipt, identity_path)
    expected = {name: manifest[name] for name in REPLACED}
    require(set(frozen.get("payloads", {})) == REPLACED, "Freeze replacement scope differs")
    for name, path in paths.items():
        record = {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha(path)}
        checked_file(record, name)
        require(frozen["payloads"][name] == record and record["sha256"] == expected[name], "Frozen payload changed: " + name)
    return frozen, receipt, paths, expected, read(paths["assets/station-online/engines.json"])


def freeze_inputs(base, identity, out):
    receipt, _ = runtime().validate_inputs(base, identity)
    paths = paths_for(receipt, identity)
    frozen = {"schemaVersion": 1, "revision": "R134", "sourceFrozen": True, "baseApkSha256": BASE_SHA,
              "identityReceiptSha256": sha(identity), "sourceCommit": receipt["sourceCommit"],
              "sourceSha256": receipt["sourceSha256"], "nativeReceiptSha256": receipt["nativeReceiptSha256"],
              "payloadReceiptSha256": receipt["payloadReceiptSha256"], "compilationReceiptSchema": receipt["compilationReceiptSchema"],
              "nativeInputSha256": receipt["nativeInputSha256"], "nativeTransforms": receipt["nativeTransforms"],
              "dexScopes": receipt["dexScopes"],
              "payloads": {name: {"path": str(path.resolve()), "bytes": path.stat().st_size,
                                  "sha256": sha(path)} for name, path in paths.items()}}
    inputs(base, out, identity, frozen)
    write(out, frozen)
    return {"sourceFrozen": True, "payloadCount": 7, "freezeSha256": sha(out)}


def package(base, freeze, identity, out):
    result = assembler().package(base, freeze, identity, out)
    report_path = Path(out).with_suffix(".package.json")
    report = read(report_path)
    receipt = read(identity)
    require(set(report["replacedEntrySha256"]) == REPLACED and report["addedEntrySha256"] == {},
            "Unsigned composition is not seven replacements and zero additions")
    require(set(report["preservedEntrySha256"]) & runtime().DEX == runtime().PRESERVED_DEX and
            {name: report["preservedEntrySha256"][name] for name in runtime().PRESERVED_DEX} ==
            {name: receipt["payloadSha256"][name] for name in runtime().PRESERVED_DEX},
            "Exactly 38 unrelated original DEX must remain byte-identical")
    require(report["preservedEntrySha256"].get(PREFIX + "libstation_frontend.so") == FRONTEND_SHA,
            "Frontend library must remain byte-identical")
    report.update(sourceCommit=receipt["sourceCommit"], replacementCount=7, additionCount=0,
                  existing38DexByteIdentical=True, dexScopedClassesVerified=True, dexScopes=receipt["dexScopes"],
                  menuDexClassDeltaRestrictedToAllowedFamilies=True, menuDexUnrelatedClassesByteIdentical=True,
                  nativeSettingsLabelsExactInversePassed=True, nativeOtherBytesByteIdentical=True,
                  frontendLibraryByteIdentical=True, nativeEmulatorEntriesPreserved=True,
                  offlineEmulatorUiEntriesChanged=True, offlineEmulatorEntriesChanged=True, offlineEmulatorLibraryEntriesChanged=False,
                  manifestByteIdentical=True, resourcesAndSonyAssetsByteIdentical=True,
                  approvedScopes=receipt["approvedScopes"], nativeReceiptSha256=receipt["nativeReceiptSha256"],
                  payloadReceiptSha256=receipt["payloadReceiptSha256"], compilationReceiptSchema=receipt["compilationReceiptSchema"])
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result.update(revision="R134", replacementCount=7, additionCount=0, existing38DexByteIdentical=True,
                  dexScopedClassesVerified=True, frontendLibraryByteIdentical=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "freeze", "identity-receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--out", type=Path)
    flags = parser.add_mutually_exclusive_group()
    flags.add_argument("--write-freeze", action="store_true")
    flags.add_argument("--check-inputs", action="store_true")
    args = parser.parse_args()
    if args.write_freeze:
        result = freeze_inputs(args.base, args.identity_receipt, args.freeze)
    elif args.check_inputs:
        inputs(args.base, args.freeze, args.identity_receipt)
        result = {"inputsVerified": True, "apkWritten": False}
    else:
        require(args.out is not None, "Explicit output APK required")
        result = package(args.base, args.freeze, args.identity_receipt, args.out)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
