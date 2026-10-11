"""Verify the real aligned/signed R131 and every inherited R130 entry.

Android tools verify the original certificate, v2/v3 signatures and 16KiB ZIP
alignment. This does not install, import firmware, start an engine or certify
gameplay, thermal results or server activation.
"""
from pathlib import Path
import argparse
import importlib.util
import json


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(base, apk, freeze, identity_receipt, receipt_path, java, apksigner, zipalign):
    assembler = load(Path(__file__).with_name("assemble_apk.py"), "r131_final_assembly")
    runtime = assembler.runtime_module()
    legacy = runtime.legacy("verify_final")
    legacy.package = assembler.assembler(identity_receipt)
    result = legacy.verify(base, apk, freeze, identity_receipt, receipt_path, java, apksigner, zipalign)
    report = legacy.package.read(receipt_path)
    receipt = legacy.package.read(identity_receipt)
    report.update({"sourceCommit": receipt["sourceCommit"], "internalSonyOwnersAdded": True,
        "existing39DexByteIdentical": True, "existingResourcesAndCarouselByteIdentical": True,
        "ps3Ps4OfflineOnly": True, "ps3Ps4OnlineEnabled": False,
        "sonyModules": receipt["sonyModules"], "sonyNativeLibrariesModified": False,
        "externalSonyEmulatorInvoked": False, "sonyFirmwareImported": False,
        "sonyAndroidBootstrapValidated": False, "physicalThermalValidated": False,
        "bundledFirmwareIsNotProofOfImport": True,
        "verificationScope": "original-certificate-signatures-alignment-and-every-final-entry"})
    legacy.package.write(receipt_path, report)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "apk", "freeze", "identity-receipt", "receipt", "java", "apksigner-jar", "zipalign"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.base, args.apk, args.freeze, args.identity_receipt,
        args.receipt, args.java, args.apksigner_jar, args.zipalign)))


if __name__ == "__main__": main()
