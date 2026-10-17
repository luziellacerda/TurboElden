"""Check every signed R143 APK entry, DEX-bound markers, certificate and alignment."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
from common import BASE, CERT, RETRO, PARTITION, REPLACED, WRAPPERS, CLINICAL_SHA, need, sha, digest, canonical, read, entry_sha, extract_fingerprint, state_fields


def verify(a):
    receipt = read(a.receipt)
    need(receipt.get("schema") == "station.r143.snes-multitap-unique-flag.package.v1" and receipt.get("passed") is True and
         receipt.get("revision") == "R143" and receipt.get("diagnosticLoggerIncluded") is False and
         receipt.get("baselineApkSha256") == BASE and receipt.get("clinicalQualificationSha256") == CLINICAL_SHA and
         receipt.get("replacedEntries") == sorted(REPLACED) and receipt.get("addedEntries") == [] and receipt.get("removedEntries") == [] and
         receipt.get("preservedEntryCount") == 13855 and receipt.get("baselineEntryCount") == receipt.get("finalEntryCount") == 13860,
         "Exact R143 five-replacement assembly receipt required")
    with zipfile.ZipFile(a.apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13860 and set(names) == set(receipt["expectedEntrySha256"]), "Exact signed R143 entry set required")
        actual = {name: entry_sha(archive, name) for name in names}
        need(actual == receipt["expectedEntrySha256"], "Signed R143 entry content differs")
        need(actual["lib/arm64-v8a/libstation_retroarch.so"] == RETRO, "Original R139 runtime changed")
        need("lib/arm64-v8a/libstation_startup_logging.so" not in actual, "Diagnostic sidecar forbidden")
        need({n for n in names if re.fullmatch(r"classes(?:[2-9]|[1-9][0-9])?\.dex", n)} == {"classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]}, "Root DEX set changed")
        identities = []
        for library, _ in WRAPPERS.values():
            value = extract_fingerprint(archive.read("lib/arm64-v8a/" + library))
            need(value["baseApkSha256"] == BASE and len(value["payloadSha256"]) == 345 and
                 value["payloadSha256"].get(PARTITION) == actual[PARTITION] and
                 all(actual.get(name) == checksum for name, checksum in value["payloadSha256"].items()), "Renewed wrapper payload differs from signed APK")
            identities.append(digest(canonical(value)))
    signer = [str(a.apksigner)]
    if a.apksigner.suffix.lower() == ".jar":
        need(a.java is not None and a.java.is_file(), "Explicit Java executable required for apksigner JAR")
        signer = [str(a.java), "-jar", str(a.apksigner)]
    signature = subprocess.run([*signer, "verify", "--verbose", "--print-certs", str(a.apk)], capture_output=True, text=True, timeout=300)
    need(signature.returncode == 0 and CERT in signature.stdout.lower().replace(":", "") and
         "Verified using v2 scheme (APK Signature Scheme v2): true" in signature.stdout and
         "Verified using v3 scheme (APK Signature Scheme v3): true" in signature.stdout, "Original certificate and v2/v3 required")
    alignment = subprocess.run([str(a.zipalign), "-c", "-P", "16", "4", str(a.apk)], capture_output=True, text=True, timeout=300)
    need(alignment.returncode == 0, "Signed APK 16 KiB alignment required")
    proof = dict(schema="station.r143.snes-multitap-unique-flag.final.v1", passed=True, apkSha256=sha(a.apk), apkBytes=a.apk.stat().st_size,
        signatureCertificateSha256=CERT, v2=True, v3=True, zipAlignment16KiB=True, sourceCommit=receipt["sourceCommit"],
        clinicalQualificationSha256=CLINICAL_SHA, checkedEntries=13860, preservedEntryCount=13855,
        replacedEntries=sorted(REPLACED), addedEntries=[], removedEntries=[], preservedRetroArchSha256=RETRO,
        wrapperFingerprints=identities, **state_fields())
    need(not a.out.exists(), "New final proof file required")
    with a.out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(proof, stream, indent=2)
        stream.write("\n")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("apk", "receipt", "apksigner", "zipalign", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--java", type=Path)
    result = verify(p.parse_args())
    print(json.dumps({"passed": True, "apkSha256": result["apkSha256"], "revision": "R143"}))
