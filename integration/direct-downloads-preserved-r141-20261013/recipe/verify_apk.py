"""Check every final R141 APK entry, both bound DEXes, original certificate and alignment."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
from common import *

SIGNER_SHA = "00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7"
ZIPALIGN_SHA = "aa2475ce201962b871fb8daec020da03fd6292c9c1f422cd0fe2e39b20d4f673"


def verify(a):
    receipt = read(a.receipt)
    pins = verify_commit(receipt.get("sourceCommit"))
    need(receipt.get("schema") == "station.r141.direct-downloads.package.v1" and receipt.get("passed") is True and
         receipt.get("revision") == "R141" and receipt.get("sourceFiles") == pins and
         receipt.get("diagnosticLoggerIncluded") is False and receipt.get("baselineApkSha256") == BASE and
         receipt.get("replacedEntries") == sorted(REPLACED) and receipt.get("addedEntries") == receipt.get("removedEntries") == [] and
         receipt.get("preservedEntryCount") == 13855 and receipt.get("baselineEntryCount") == receipt.get("finalEntryCount") == 13860 and
         receipt.get("preservedDex35Sha256") == PRESERVED_DEX35 and receipt.get("nativeRuntimeSha256") == RETRO and
         set(receipt.get("preservedDexSha256", {})) == ROOT_DEX - {PARTITION}, "Exact R141 five-replacement package receipt required")
    with zipfile.ZipFile(a.apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13860 and set(names) == set(receipt["expectedEntrySha256"]), "Exact final R141 entry set required")
        actual = {name: entry_sha(archive, name) for name in names}
        need(actual == receipt["expectedEntrySha256"] and actual["classes35.dex"] == PRESERVED_DEX35 and
             actual["lib/arm64-v8a/libstation_retroarch.so"] == RETRO and
             {n: actual[n] for n in ROOT_DEX - {PARTITION}} == receipt["preservedDexSha256"], "Final entry/39 DEX content differs")
        need({n for n in names if re.fullmatch(r"classes(?:\d+)?\.dex", n)} == ROOT_DEX and
             "lib/arm64-v8a/libstation_startup_logging.so" not in actual, "Original root DEX inventory required; diagnostic sidecar forbidden")
        registry = json.loads(archive.read("assets/station-online/engines.json"))
        retro = [e for e in registry["engines"] if e["platform"] not in {"psx", "n64", "gamecube", "wii"}]
        selected = [e for e in registry["engines"] if e["platform"] in {"psx", "n64", "gamecube", "wii"}]
        need(len(registry["engines"]) == 13 and len(retro) == 9 and retro == receipt["preservedRetroArchDescriptors"] and
             selected == receipt["renewedIndependentEngines"] and len(selected) == 4, "RetroArch descriptors and four independent identities differ")
        identities = []
        common_payload = None
        for library, _ in WRAPPERS.values():
            raw = archive.read("lib/arm64-v8a/" + library)
            elf_contract(raw)
            value = extract_fingerprint(raw)
            payload = value["payloadSha256"]
            need(value["baseApkSha256"] == BASE and len(payload) == 345 and payload.get(PARTITION) == actual[PARTITION] and
                 payload.get("classes35.dex") == PRESERVED_DEX35 and all(actual.get(n) == checksum for n, checksum in payload.items()),
                 "Wrapper must bind new HTTP DEX28 and exact R140 DEX35, with all 345 real payloads")
            need(common_payload is None or common_payload == payload, "Wrapper payload maps differ")
            common_payload = payload
            identities.append(digest(canonical(value)))
        for row in selected:
            need(actual["lib/arm64-v8a/" + row["runtimeLibrary"]] == row["runtimeSha256"] and
                 row["engineId"].endswith("-" + row["runtimeSha256"][:12]), "Registry runtime suffix/hash differs")
    need(a.apksigner.suffix.lower() == ".jar" and a.java is not None and sha(a.java) == TOOLS["java"] and
         sha(a.apksigner) == SIGNER_SHA and sha(a.zipalign) == ZIPALIGN_SHA, "Pinned Java/apksigner JAR/zipalign required")
    signature = subprocess.run([str(a.java), "-jar", str(a.apksigner), "verify", "--verbose", "--print-certs", str(a.apk)],
                               capture_output=True, text=True, timeout=300)
    need(signature.returncode == 0 and CERT in signature.stdout.lower().replace(":", "") and
         "Verified using v2 scheme (APK Signature Scheme v2): true" in signature.stdout and
         "Verified using v3 scheme (APK Signature Scheme v3): true" in signature.stdout, "Original certificate and v2/v3 required")
    alignment = subprocess.run([str(a.zipalign), "-c", "-P", "16", "4", str(a.apk)], capture_output=True, text=True, timeout=300)
    need(alignment.returncode == 0, "Final APK 16 KiB alignment required")
    proof = dict(schema="station.r141.direct-downloads.final.v1", passed=True, apkSha256=sha(a.apk), apkBytes=a.apk.stat().st_size,
        signatureCertificateSha256=CERT, v2=True, v3=True, zipAlignment16KiB=True, sourceCommit=receipt["sourceCommit"],
        checkedEntries=13860, preservedEntryCount=13855, replacedEntries=sorted(REPLACED), addedEntries=[], removedEntries=[],
        preservedDex35Sha256=PRESERVED_DEX35, preservedRetroArchSha256=RETRO, preservedDexPartitions=39,
        preservedRetroArchDescriptors=9, wrapperFingerprints=identities, **state_fields())
    need(not a.out.exists(), "New final proof file required")
    with a.out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(proof, stream, indent=2)
        stream.write("\n")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("apk", "receipt", "apksigner", "zipalign", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--java", type=Path, required=True)
    result = verify(p.parse_args())
    print(json.dumps({"passed": True, "apkSha256": result["apkSha256"], "revision": "R141"}))
