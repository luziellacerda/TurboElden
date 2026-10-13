"""Assemble R141 direct downloads only: five replacements and zero additions/removals."""
from pathlib import Path
import argparse
import copy
import json
import shutil
import sys
import zipfile

sys.dont_write_bytecode = True
zipfile.ZIP64_LIMIT = (1 << 32) - 1
from common import *
from build_identity import module


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R140 donor required")
    pins = verify_commit(a.source_commit)
    identity = read(a.identity / "runtime-identity.json")
    dex = validate_dex_receipt(read(a.dex_receipt), a.dex, a.source_commit, pins)
    need(identity.get("schema") == "station.r141.direct-downloads.identity.v1" and identity.get("passed") is True and
         identity.get("compiled") is True and identity.get("revision") == "R141" and
         identity.get("diagnosticLoggerIncluded") is False and identity.get("serverRegistered") is False and
         identity.get("sourceCommit") == a.source_commit and identity.get("sourceFiles") == pins and
         identity.get("baselineApkSha256") == BASE and identity.get("dexSha256") == sha(a.dex) and
         identity.get("dexBuildReceiptSha256") == sha(a.dex_receipt) and identity.get("preservedRetroArchSha256") == RETRO and
         identity.get("preservedDex35Sha256") == PRESERVED_DEX35 and identity.get("finalPayloadCount") == 345,
         "Frozen R141 identity and exact scoped DEX receipts required")
    files = {PARTITION: a.dex, "assets/station-online/engines.json": a.identity / "engines.json"}
    for kind, (name, _) in WRAPPERS.items():
        path = a.identity / "native" / name if kind == "psx" else a.identity / name
        need(sha(path) == identity["markers"][kind]["runtimeSha256"], "Renewed wrapper differs: " + kind)
        files["lib/arm64-v8a/" + name] = path
    need(set(files) == REPLACED and sha(files["assets/station-online/engines.json"]) == identity["enginesAssetSha256"],
         "Only five replacements and no additions allowed")
    inherited = module(REPO / "integration/online-lifecycle-review-r135/recipe/build_runtime_identity.py", "r141_package_policy")
    out = isolated(a.out)
    with zipfile.ZipFile(a.base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and REPLACED <= set(names), "Exact donor entry inventory required")
        previous = fingerprints(original)
        old_registry = json.loads(original.read("assets/station-online/engines.json"))
        registry = read(files["assets/station-online/engines.json"])
        expected_registry, selected = inherited.expected_engines(old_registry, identity["markers"])
        need(registry == expected_registry and identity["engines"] == selected, "Only four inherited independent IDs/hashes may change")
        retro = [row for row in old_registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
        need(len(old_registry["engines"]) == len(registry["engines"]) == 13 and len(retro) == 9 and
             identity["preservedRetroArchDescriptors"] == retro and
             [row for row in registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
             "All nine RetroArch descriptors, controls and options must stay exact")
        before = {name: entry_sha(original, name) for name in names}
        need(before[PARTITION] == DEX and before["classes35.dex"] == PRESERVED_DEX35 and
             before["lib/arm64-v8a/libstation_retroarch.so"] == RETRO and
             {n: before[n] for n in ROOT_DEX - {PARTITION}} == dex["preservedDexSha256"], "R140 DEX/runtime donor identity differs")
        inherited_payload = previous["psx"]["payloadSha256"]
        need(all(before[name] == checksum for name, checksum in inherited_payload.items()), "Inherited actual payload differs")
        expected_payload = {**inherited_payload, PARTITION: sha(a.dex)}
        need(len(expected_payload) == 345 and expected_payload == identity["payloadSha256"] and
             expected_payload["classes35.dex"] == PRESERVED_DEX35, "Both DEX28 and corrected R140 DEX35 must remain bound")
        transforms = {**previous["psx"]["productiveTransforms"], **{ROOT.name + "/" + name: checksum for name, checksum in pins.items()}}
        need(len(transforms) == len(previous["psx"]["productiveTransforms"]) + len(pins), "R141 source chain must append without overwrite")
        for kind, (library, parent_hash) in WRAPPERS.items():
            raw = files["lib/arm64-v8a/" + library].read_bytes()
            actual = extract_fingerprint(raw)
            wanted = copy.deepcopy(previous[kind])
            wanted.update(baseApkSha256=BASE, payloadSha256=expected_payload, productiveTransforms=transforms)
            if kind != "psx":
                wanted.update(parentFingerprintSha256=PARENT_FINGERPRINTS[kind], parentRuntimeSha256=parent_hash,
                              psxRuntimeSha256=identity["markers"]["psx"]["runtimeSha256"])
            need(actual == wanted and inherited.policy(actual) == inherited.policy(previous[kind]) and
                 digest(canonical(actual)) == identity["markers"][kind]["fingerprintSha256"],
                 "Original owner/core/controllers/options policy or fingerprint changed: " + kind)
            wrapper_contract(original.read("lib/arm64-v8a/" + library), raw, kind)
        expected = {**before, **{name: sha(path) for name, path in files.items()}}
        need({n for n in before if before[n] != expected[n]} == REPLACED and
             all(expected[n] == checksum for n, checksum in expected_payload.items()), "Exact five replacements and canonical payload required")
        out.mkdir(parents=True)
        unsigned = out / "TurboStations-Premium-R141-downloads-diretos-unsigned.apk"
        with zipfile.ZipFile(unsigned, "w", allowZip64=False) as destination:
            for item in original.infolist():
                # ZipFile.open mutates header_offset; never reuse the donor ZipInfo object.
                with destination.open(copy.copy(item), "w", force_zip64=False) as target:
                    if item.filename in files:
                        with files[item.filename].open("rb") as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
                    else:
                        with original.open(item.filename) as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
    with zipfile.ZipFile(unsigned) as archive:
        need(len(archive.namelist()) == len(set(archive.namelist())) == 13860 and
             {n: entry_sha(archive, n) for n in archive.namelist()} == expected, "Independent assembled entry readback failed")
    need(verify_commit(a.source_commit) == pins, "Sources changed during package assembly")
    receipt = dict(schema="station.r141.direct-downloads.package.v1", passed=True, sourceCommit=a.source_commit, sourceFiles=pins,
        baselineApkSha256=BASE, baselineApkBytes=BASE_BYTES, retainedBaseSourceCommit=BASE_SOURCE,
        unsignedApkSha256=sha(unsigned), unsignedApkBytes=unsigned.stat().st_size,
        replacedEntries=sorted(REPLACED), addedEntries=[], removedEntries=[], preservedEntryCount=13855,
        baselineEntryCount=13860, finalEntryCount=13860, expectedEntrySha256=expected,
        preservedDexSha256=dex["preservedDexSha256"], preservedDex35Sha256=PRESERVED_DEX35,
        nativeRuntimeSha256=RETRO, preservedRetroArchDescriptors=retro, renewedIndependentEngines=selected,
        runtimeIdentityReceiptSha256=sha(a.identity / "runtime-identity.json"), **state_fields())
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("base", "dex", "dex-receipt", "identity", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    result = build(p.parse_args())
    print(json.dumps({"passed": True, "unsignedApkSha256": result["unsignedApkSha256"], "revision": "R141"}))
