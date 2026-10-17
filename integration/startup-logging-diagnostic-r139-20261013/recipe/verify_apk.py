"""Verify every final diagnostic APK entry and the original v2/v3 certificate."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
from common import BASE, CERT, RETRO, PARTITION, SIDE, REPLACED, WRAPPERS, need, sha, digest, canonical, read, entry_sha, temporary_fields
from assemble_apk import elf


def verify(a):
    receipt = read(a.receipt)
    need(receipt.get("schema") == "station.r139.startup-logging.package.v1" and receipt.get("passed") is True and
         receipt.get("baselineApkSha256") == BASE and receipt.get("diagnosticTemporary") is True and
         receipt.get("replacedEntries") == sorted(REPLACED) and receipt.get("addedEntries") == [SIDE] and
         receipt.get("removedEntries") == [] and receipt.get("preservedEntryCount") == 13855, "Exact temporary diagnostic assembly receipt required")
    with zipfile.ZipFile(a.apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13861 and set(names) == set(receipt["expectedEntrySha256"]), "Exact signed entry set required")
        actual = {name: entry_sha(archive, name) for name in names}
        need(actual == receipt["expectedEntrySha256"], "Signed diagnostic entry content differs")
        need(actual["lib/arm64-v8a/libstation_retroarch.so"] == RETRO, "R139 RetroArch changed")
        need(elf(archive.read(SIDE)) >= 16384, "Logger ELF shape differs")
        need({n for n in names if re.fullmatch(r"classes(?:[2-9]|[1-9][0-9])?\.dex", n)} == {"classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]}, "Root DEX partition set changed")
        identities = []
        for library, _ in WRAPPERS.values():
            raw = archive.read("lib/arm64-v8a/" + library)
            documents = []
            for match in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw):
                end = raw.find(b"\0", match.start())
                if end < 0:
                    continue
                try:
                    value = json.loads(raw[match.start():end].decode("ascii"))
                except (ValueError, UnicodeError):
                    continue
                if isinstance(value, dict) and "baseApkSha256" in value and "payloadSha256" in value:
                    documents.append(value)
            need(len(documents) == 1, "Exactly one renewed wrapper identity required")
            value = documents[0]
            encoded = canonical(value)
            need(encoded in raw and digest(encoded).encode("ascii") in raw and value["baseApkSha256"] == BASE and
                 len(value["payloadSha256"]) == 346 and value["payloadSha256"].get(PARTITION) == actual[PARTITION] and
                 value["payloadSha256"].get(SIDE) == actual[SIDE] and
                 all(actual.get(name) == h for name, h in value["payloadSha256"].items()), "Renewed identity payload does not match final APK")
            identities.append(digest(encoded))
    result = subprocess.run([str(a.apksigner), "verify", "--verbose", "--print-certs", str(a.apk)], capture_output=True, text=True, timeout=300)
    need(result.returncode == 0 and CERT in result.stdout.lower() and
         "Verified using v2 scheme (APK Signature Scheme v2): true" in result.stdout and
         "Verified using v3 scheme (APK Signature Scheme v3): true" in result.stdout, "Original certificate/v2/v3 required")
    alignment = subprocess.run([str(a.zipalign), "-c", "-P", "16", "4", str(a.apk)], capture_output=True, text=True, timeout=300)
    need(alignment.returncode == 0, "Final 16 KiB APK/native library alignment required")
    proof = dict(schema="station.r139.startup-logging.final.v1", passed=True, diagnosticApkSha256=sha(a.apk),
                 diagnosticApkBytes=a.apk.stat().st_size, signatureCertificateSha256=CERT, v2=True, v3=True, zipAlignment16KiB=True,
                 sourceCommit=receipt["sourceCommit"], checkedEntries=13861, preservedEntryCount=13855,
                 preservedRetroArchSha256=RETRO, wrapperFingerprints=identities, **temporary_fields())
    need(not a.out.exists(), "New final proof path required")
    a.out.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("apk", "receipt", "apksigner", "zipalign", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    result = verify(p.parse_args())
    print(json.dumps({"passed": True, "diagnosticApkSha256": result["diagnosticApkSha256"], "diagnosticTemporary": True}))
