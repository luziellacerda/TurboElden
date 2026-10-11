#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Verify an aligned/signed R127 using real Android tools and entry hashes.

This performs read-only verification, then writes an aggregate receipt. It
never signs, installs, restarts a service or declares physical gameplay valid.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import re
import subprocess
import zipfile

spec = importlib.util.spec_from_file_location("psx_assemble", Path(__file__).with_name("assemble_apk.py"))
package = importlib.util.module_from_spec(spec); spec.loader.exec_module(package)


def verify(base, apk, freeze, identity_receipt, receipt_path, java, apksigner, zipalign):
    if package.fs(receipt_path).exists(): raise FileExistsError("Never overwrite a verification receipt")
    if apk.resolve() == base.resolve(): raise ValueError("Final candidate cannot be the base APK")
    _, runtime, _, expected, manifest = package.inputs(base, freeze, identity_receipt)
    freeze_sha, identity_sha = package.sha(freeze), package.sha(identity_receipt)
    # These are tools, not booleans taken from a previous receipt.
    signature = subprocess.run([str(java), "-jar", str(apksigner), "verify", "--verbose", "--print-certs", str(apk)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    certificate = re.search(r"^Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]{64})\s*$", signature.stdout, re.M)
    if not certificate or certificate.group(1).lower() != package.CERT:
        raise ValueError("Original signing identity was not preserved")
    if re.search(r"^Signer #[2-9]\d* certificate", signature.stdout, re.M):
        raise ValueError("Unexpected additional signer")
    for scheme in ("v2", "v3"):
        if not re.search(r"^Verified using " + scheme + r" scheme.*: true\s*$", signature.stdout, re.M):
            raise ValueError("Missing verified signature scheme: " + scheme)
    subprocess.run([str(zipalign), "-P", "16", "-c", "4", str(apk)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    preserved, replacements, additions = {}, {}, {}
    with zipfile.ZipFile(package.fs(base)) as original, zipfile.ZipFile(package.fs(apk)) as result:
        original_names = package.classic_entries(original)
        output_names = package.classic_entries(result)
        original_data = {n for n in original_names if not package.signature_metadata(n)}
        output_data = {n for n in output_names if not package.signature_metadata(n)}
        if output_data != original_data | package.ADDED:
            raise ValueError("Final data entry set differs")
        if result.comment != original.comment: raise ValueError("Base ZIP comment changed")
        for name in sorted(original_data):
            old, new = package.entry_sha(original, name), package.entry_sha(result, name)
            if name in package.REPLACED:
                if new != expected[name]: raise ValueError("Replacement differs from frozen bytes: " + name)
                replacements[name] = new
            else:
                if old != new: raise ValueError("Preserved entry changed: " + name)
                preserved[name] = new
        for name in sorted(package.ADDED):
            additions[name] = package.entry_sha(result, name)
            if additions[name] != expected[name]: raise ValueError("Added native bytes differ: " + name)
        if json.loads(result.read("assets/station-online/engines.json")) != manifest:
            raise ValueError("Final engine asset differs")
        for engine in runtime["engines"]:
            pins = {engine["library"]: engine["coreSha256"], engine["runtimeLibrary"]: engine["runtimeSha256"],
                    **engine.get("dependencySha256", {})}
            for library, checksum in pins.items():
                if package.entry_sha(result, package.PREFIX + library) != checksum:
                    raise ValueError("Pinned dependency differs: " + library)
        package.classic_zip(apk, result.comment)
    if package.sha(freeze) != freeze_sha or package.sha(identity_receipt) != identity_sha:
        raise ValueError("Freeze/identity changed during verification")
    package.inputs(base, freeze, identity_receipt)
    report = {"schemaVersion": 1, "revision": "R127", "baseApkSha256": package.BASE_SHA,
        "apkSha256": package.sha(apk), "apkBytes": package.fs(apk).stat().st_size,
        "freezeSha256": freeze_sha, "identityReceiptSha256": identity_sha,
        "replacedEntrySha256": replacements, "addedEntrySha256": additions,
        "preservedEntryCount": len(preserved),
        "preservedEntryManifestSha256": package.digest(package.canonical(preserved)),
        "signingCertificateSha256": package.CERT, "signatureSchemesVerified": ["v2", "v3"],
        "zipAlignmentVerifiedBytes": 16384, "classicZip": True, "zip64": False,
        "verificationTools": {"java": {"path": str(java.resolve()), "sha256": package.sha(java)},
            "apksignerJar": {"path": str(apksigner.resolve()), "sha256": package.sha(apksigner)},
            "zipalign": {"path": str(zipalign.resolve()), "sha256": package.sha(zipalign)}},
        "engineIds": [e["engineId"] for e in runtime["engines"]],
        "offlineEmulatorEntriesChanged": False, "n64DolphinCoresAndOptionsPreserved": True,
        "snesMegadriveEntriesPreserved": True, "installed": False,
        "serverActivationConfirmed": False, "physicalGameplayValidated": False}
    package.write(receipt_path, report)
    return {k: report[k] for k in ("revision", "apkSha256", "apkBytes", "preservedEntryCount", "installed")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "apk", "freeze", "identity-receipt", "receipt", "java", "apksigner-jar", "zipalign"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.base, args.apk, args.freeze, args.identity_receipt,
                           args.receipt, args.java, args.apksigner_jar, args.zipalign)))


if __name__ == "__main__": main()
