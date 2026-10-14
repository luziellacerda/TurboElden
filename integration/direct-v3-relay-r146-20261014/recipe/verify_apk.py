"""Verify signed R146 against every R145 entry, policy, certificate and alignment."""
from pathlib import Path
import argparse
import copy
import json
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
from common import *
from build_identity import (DEPENDENCIES, retained_builder, extract_fingerprint, transforms_for,
                            validate_dex_receipt)

JAVA_SHA = "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406"
SIGNER_SHA = "00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7"
ZIPALIGN_SHA = "aa2475ce201962b871fb8daec020da03fd6292c9c1f422cd0fe2e39b20d4f673"


def verify(a):
    isolated(a.out)
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R145 comparison donor required")
    receipt = read(a.receipt)
    pins = verify_commit(receipt.get("sourceCommit"))
    dex, dex_paths = validate_dex_receipt(read(a.dex_receipt), a.dex_dir, receipt["sourceCommit"], pins)
    parent_proof = verify_parent_proof(a.parent_proof)
    need(receipt.get("schema") == "station.r146.direct-v3-relay.package.v1" and receipt.get("passed") is True and
         receipt.get("sourceFiles") == pins and all(receipt.get(key) == value for key, value in state_fields().items()) and
         receipt.get("baselineApkSha256") == BASE and receipt.get("baselineApkBytes") == BASE_BYTES and
         receipt.get("replacedEntries") == sorted(REPLACED) and len(REPLACED) == 5 and
         receipt.get("addedEntries") == receipt.get("removedEntries") == [] and receipt.get("preservedEntryCount") == 13855 and
         receipt.get("baselineEntryCount") == receipt.get("finalEntryCount") == 13860 and
         receipt.get("nativeRuntimeSha256") == RETRO and receipt.get("gameplayMethodsPreserved") is True and
         receipt.get("legacyRelayAndApiAuthPreserved") is True and
         receipt.get("v3TicketProofPathProtocolReadyAckAndExitPreserved") is True and
         receipt.get("dexBuildReceiptSha256") == sha(a.dex_receipt) and receipt.get("parentFinalProofSha256") == sha(a.parent_proof) and
         receipt.get("scopeDeclarationSha256") == sha(ROOT / "evidence/route-scope.json") and
         receipt.get("dexScopes") == dex["scopes"] and
         receipt.get("changedDexSha256") == {name: sha(path) for name, path in dex_paths.items()} and
         receipt.get("retainedIdentityDependencies") == DEPENDENCIES and
         set(receipt.get("preservedDexSha256", {})) == ROOT_DEX - PARTITIONS,
         "Exact R146 five-replacement candidate assembly receipt required")
    inherited = retained_builder()
    with zipfile.ZipFile(a.base) as original, zipfile.ZipFile(a.apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == len(original.namelist()) == 13860 and
             set(names) == set(original.namelist()) == set(receipt["expectedEntrySha256"]),
             "Exact final and donor entry inventory required")
        before = {name: entry_sha(original, name) for name in names}
        actual = {name: entry_sha(archive, name) for name in names}
        need(actual == receipt["expectedEntrySha256"] and {name for name in names if before[name] != actual[name]} == REPLACED and
             all(before[name] == checksum for name, checksum in DEX_BASE.items()) and before[CAROUSEL] == CAROUSEL_SHA and
             all(actual[name] == sha(path) for name, path in dex_paths.items()) and actual[CAROUSEL] == CAROUSEL_SHA and
             actual["lib/arm64-v8a/libstation_retroarch.so"] == before["lib/arm64-v8a/libstation_retroarch.so"] == RETRO and
             {name: actual[name] for name in ROOT_DEX - PARTITIONS} == receipt["preservedDexSha256"],
             "All 13,855 retained entries and 39 complete DEX partitions must stay byte exact")
        need({name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} == ROOT_DEX and
             "lib/arm64-v8a/libstation_startup_logging.so" not in actual,
             "Original 40-DEX inventory required; diagnostic sidecar forbidden")
        previous = fingerprints(original)
        old_payload = previous["psx"]["payloadSha256"]
        payload = {**old_payload, **{name: actual[name] for name in PARTITIONS}, CAROUSEL: actual[CAROUSEL]}
        need(len(payload) == 345 and {name for name in old_payload if old_payload[name] != payload[name]} == CHANGED_PAYLOAD and
             payload == receipt["payloadSha256"] and all(actual[name] == checksum for name, checksum in payload.items()),
             "Complete 345-entry marker binding may change only the one approved route DEX payload hash")
        transforms = transforms_for(previous, pins)
        markers = receipt["renewedRuntimeMarkers"]
        need(set(markers) == set(WRAPPERS), "Exactly three marker libraries required")
        identities = []
        for kind, (library, parent_hash) in WRAPPERS.items():
            raw = archive.read("lib/arm64-v8a/" + library)
            value = extract_fingerprint(raw)
            expected = copy.deepcopy(previous[kind])
            expected.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
            if kind != "psx":
                expected.update(parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_hash,
                                psxRuntimeSha256=markers["psx"]["runtimeSha256"])
            marker = markers[kind]
            need(value == expected and inherited.policy(value) == inherited.policy(previous[kind]) and
                 marker.get("runtimeLibrary") == library and marker.get("runtimeSha256") == digest(raw) != parent_hash and
                 marker.get("runtimeBytes") == len(raw) and marker.get("fingerprintSha256") == digest(canonical(value)),
                 "Canonical independent owner policy or marker identity changed: " + kind)
            wrapper_contract(original.read("lib/arm64-v8a/" + library), raw, kind)
            identities.append(digest(canonical(value)))
        old_registry = json.loads(original.read("assets/station-online/engines.json"))
        registry = json.loads(archive.read("assets/station-online/engines.json"))
        expected_registry, selected = inherited.expected_engines(old_registry, markers)
        retro = [row for row in registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
        need(registry == expected_registry and selected == receipt["renewedIndependentEngines"] and
             len(registry["engines"]) == 13 and len(retro) == 9 and retro == receipt["preservedRetroArchDescriptors"],
             "Nine original RetroArch descriptors and four renewed independent IDs required")
        old_contract, new_contract = elf_contract(original.read(CAROUSEL)), elf_contract(archive.read(CAROUSEL))
        need(original.read(CAROUSEL) == archive.read(CAROUSEL) and
             old_contract["exports"] == new_contract["exports"] and old_contract["needed"] == new_contract["needed"] and
             old_contract["soname"] == new_contract["soname"] == ["libturbo_carousel.so"] and
             canonical(new_contract) == canonical(receipt["carouselContract"]) and actual[CAROUSEL] == receipt["carouselSha256"],
             "Carousel native API, dependencies, SONAME or qualified alignment changed")
    need(a.apksigner.suffix.lower() == ".jar" and sha(a.java) == JAVA_SHA and
         sha(a.apksigner) == SIGNER_SHA and sha(a.zipalign) == ZIPALIGN_SHA,
         "Pinned Java, apksigner JAR and zipalign required")
    signature = subprocess.run([str(a.java), "-jar", str(a.apksigner), "verify", "--verbose", "--print-certs", str(a.apk)],
                               capture_output=True, text=True, timeout=300)
    certificates = [value.lower().replace(":", "") for value in
                    re.findall(r"Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F:]+)", signature.stdout)]
    need(signature.returncode == 0 and certificates == [CERT] and
         "Verified using v2 scheme (APK Signature Scheme v2): true" in signature.stdout and
         "Verified using v3 scheme (APK Signature Scheme v3): true" in signature.stdout,
         "Original certificate and v2/v3 signature schemes required")
    alignment = subprocess.run([str(a.zipalign), "-c", "-P", "16", "4", str(a.apk)], capture_output=True, text=True, timeout=300)
    need(alignment.returncode == 0, "Final signed APK 16 KiB alignment required")
    need(verify_commit(receipt["sourceCommit"]) == pins and
         sha(a.dex_receipt) == receipt["dexBuildReceiptSha256"] and
         sha(a.parent_proof) == receipt["parentFinalProofSha256"] and
         read(a.dex_receipt) == dex and verify_parent_proof(a.parent_proof) == parent_proof,
         "Frozen route sources or qualified input receipts changed during final verification")
    proof = dict(schema="station.r146.direct-v3-relay.final.v1", passed=True, apkSha256=sha(a.apk), apkBytes=a.apk.stat().st_size,
        signatureCertificateSha256=CERT, v2=True, v3=True, zipAlignment16KiB=True, sourceCommit=receipt["sourceCommit"],
        sourceFiles=pins, assemblyReceiptSha256=sha(a.receipt), baselineApkSha256=BASE,
        checkedEntries=13860, preservedEntryCount=13855, replacedEntries=sorted(REPLACED), addedEntries=[], removedEntries=[],
        changedDexSha256={name: actual[name] for name in PARTITIONS}, preservedRetroArchSha256=RETRO,
        checkedChangedClasses=2, checkedChangedExistingMethods=2, checkedAddedMethods=1,
        gameplayMethodsPreserved=True, legacyRelayAndApiAuthPreserved=True,
        v3TicketProofPathProtocolReadyAckAndExitPreserved=True, preservedDexPartitions=39,
        parentFinalProofSha256=sha(a.parent_proof), parentSourceCommit=BASE_SOURCE,
        scopeDeclarationSha256=sha(ROOT / "evidence/route-scope.json"), preservedCarouselSha256=CAROUSEL_SHA,
        preservedRetroArchDescriptors=9, changedPayloadEntries=sorted(CHANGED_PAYLOAD),
        wrapperFingerprints=identities, **state_fields())
    need(not a.out.exists(), "New final proof file required")
    with a.out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(proof, stream, indent=2)
        stream.write("\n")
    return proof


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "apk", "receipt", "dex-dir", "dex-receipt", "apksigner", "zipalign", "java", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--parent-proof", type=Path, default=PARENT_PROOF_PATH)
    result = verify(parser.parse_args())
    print(json.dumps({"passed": True, "apkSha256": result["apkSha256"], "revision": "R146"}))
