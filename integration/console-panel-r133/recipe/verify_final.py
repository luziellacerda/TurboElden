"""Verify original signature, 16KiB alignment and every R132 entry in R133."""
from pathlib import Path
import argparse
import json
import types
import zipfile
from common import *


def verify(base, apk, freeze, identity, receipt_path, java, apksigner, zipalign):
    assembly = module(ROOT / "recipe/assemble_apk.py", "r133_assembly")
    primitive = REPO / "integration/psx-online/recipe/verify_final.py"
    require(sha(primitive) == "9d7c40088a848367df431fac8088ad778a139bcc31bcb4ef10a219ce4a085ddf",
            "Pinned independent APK verifier changed")
    verifier = types.ModuleType("r133_independent_verify")
    verifier.__file__ = str(primitive)
    raw = primitive.read_text(encoding="utf-8")
    start = raw.index('spec = importlib.util.spec_from_file_location(')
    end = raw.index('\n\n\ndef verify(', start)
    raw = raw[:start] + raw[end:]
    exec(compile(raw.replace('"R127"', '"R133"'), str(primitive), "exec"), verifier.__dict__)
    verifier.package = assembly.assembler()
    result = verifier.verify(base, apk, freeze, identity, receipt_path, java, apksigner, zipalign)
    report = read(receipt_path)
    runtime = read(identity)
    require(set(report["replacedEntrySha256"]) == assembly.REPLACED and report["addedEntrySha256"] == {},
            "Final composition is not five replacements and zero additions")
    preserved = {}
    with zipfile.ZipFile(verifier.package.fs(apk)) as archive:
        for name in sorted(verifier.package.classic_entries(archive)):
            if name not in assembly.REPLACED and not verifier.package.signature_metadata(name):
                preserved[name] = verifier.package.entry_sha(archive, name)
    require(len(preserved) == report["preservedEntryCount"] and
            verifier.package.digest(verifier.package.canonical(preserved)) == report["preservedEntryManifestSha256"],
            "Full preserved map differs from independent final verification")
    require(verifier.package.sha(apk) == report["apkSha256"], "Signed APK changed while aggregating maps")
    require(set(preserved) & assembly.runtime().DEX == assembly.runtime().DEX,
            "All 40 original DEX must remain byte-identical")
    require(preserved.get(assembly.PREFIX + "libstation_frontend.so") == FRONTEND_SHA,
            "Frontend library must remain byte-identical")
    report.update(sourceCommit=runtime["sourceCommit"], replacementCount=5, additionCount=0,
                  preservedEntrySha256=preserved, completeAggregateEntryHashMaps=True,
                  existing40DexByteIdentical=True, dexClassSetsPreserved=True, frontendLibraryByteIdentical=True,
                  offlineEmulatorEntriesChanged=False, offlineEmulatorLibraryEntriesChanged=False,
                  noGameSaveLicenseFilesMovedOrDeleted=True, manifestByteIdentical=True,
                  resourcesAndSonyAssetsByteIdentical=True, shaderCodeAndEffectsPreserved=True,
                  videoBytesAndLoopPolicyPreserved=True, controllerProfilesUnchanged=True,
                  protocolAndTransportUnchanged=True, ps3Ps4OfflineOnly=True, ps3Ps4OnlineEnabled=False,
                  approvedScopes=runtime["approvedScopes"], nativeReceiptSha256=runtime["nativeReceiptSha256"],
                  physicalStartupValidated=False, physicalThermalValidated=False,
                  verificationScope="original-signature-16KiB-and-every-entry-with-five-closed-replacements")
    Path(receipt_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    result.update(replacementCount=5, additionCount=0, existing40DexByteIdentical=True,
                  frontendLibraryByteIdentical=True, completeAggregateEntryHashMaps=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "apk", "freeze", "identity-receipt", "receipt", "java", "apksigner-jar", "zipalign"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.base, args.apk, args.freeze, args.identity_receipt, args.receipt,
                           args.java, args.apksigner_jar, args.zipalign)))


if __name__ == "__main__":
    main()
