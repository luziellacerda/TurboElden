"""Assemble R143 binding only: five replacements and zero additions/removals."""
from pathlib import Path
import argparse
import copy
import json
import shutil
import sys
import zipfile

sys.dont_write_bytecode = True
# Android's APK tooling requires classic ZIP headers below the 4 GiB boundary.
zipfile.ZIP64_LIMIT = (1 << 32) - 1
from common import BASE, BASE_BYTES, DEX, RETRO, PARTITION, WRAPPERS, CLINICAL_SHA, REPLACED, ROOT, need, sha, digest, read, entry_sha, verify_commit, isolated, state_fields


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R139 donor required")
    pins = verify_commit(a.source_commit)
    identity = read(a.identity / "runtime-identity.json")
    need(identity.get("passed") is True and identity.get("compiled") is True and identity.get("revision") == "R143" and identity.get("diagnosticLoggerIncluded") is False and
         identity.get("sourceCommit") == a.source_commit and identity.get("sourceFiles") == pins and
         identity.get("baselineApkSha256") == BASE and identity.get("dexSha256") == sha(a.dex) and
         identity.get("preservedRetroArchSha256") == RETRO and identity.get("clinicalQualificationSha256") == CLINICAL_SHA and
         identity.get("finalPayloadCount") == 345, "Frozen R143 identity receipt required")
    dex = read(a.dex_receipt)
    need(sha(a.dex_receipt) == identity["dexBuildReceiptSha256"] and dex.get("inversePassed") is True and
         dex.get("unchangedClasses") == 607 and dex.get("finalClassCount") == 608 and dex.get("addedClasses") == [] and
         dex.get("removedClasses") == [] and dex.get("sourceCommit") == a.source_commit and dex.get("sourceFiles") == pins and
         dex.get("clinicalQualificationSha256") == CLINICAL_SHA, "Exact R143 DEX build proof required")
    files = {PARTITION: a.dex, "assets/station-online/engines.json": a.identity / "engines.json"}
    for kind, (name, _) in WRAPPERS.items():
        path = a.identity / "native" / name if kind == "psx" else a.identity / name
        need(sha(path) == identity["markers"][kind]["runtimeSha256"], "Renewed wrapper differs: " + kind)
        files["lib/arm64-v8a/" + name] = path
    need(set(files) == REPLACED and sha(files["assets/station-online/engines.json"]) == identity["enginesAssetSha256"], "Only five replacements and no additions allowed")
    out = isolated(a.out)
    with zipfile.ZipFile(a.base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and REPLACED <= set(names), "Exact donor entries required")
        old_registry = json.loads(original.read("assets/station-online/engines.json"))
        registry = read(files["assets/station-online/engines.json"])
        changed = []
        for before, after in zip(old_registry["engines"], registry["engines"]):
            if before != after:
                strip = lambda row: {k: v for k, v in row.items() if k not in {"engineId", "runtimeSha256"}}
                need(before["platform"] in {"psx", "n64", "gamecube", "wii"} and strip(before) == strip(after), "Only four independent engine IDs/hash may change")
                changed.append(before["platform"])
        need(len(registry["engines"]) == len(old_registry["engines"]) == 13 and set(changed) == {"psx", "n64", "gamecube", "wii"} and
             {k: v for k, v in old_registry.items() if k != "engines"} == {k: v for k, v in registry.items() if k != "engines"}, "Registry descriptors/metadata expanded")
        need(entry_sha(original, "lib/arm64-v8a/libstation_retroarch.so") == RETRO and entry_sha(original, PARTITION) == DEX, "Native/DEX donor identity differs")
        before = {name: entry_sha(original, name) for name in names}
        expected = {**before, **{name: sha(path) for name, path in files.items()}}
        need({n for n in before if before[n] != expected[n]} == REPLACED, "Exact five replacements required")
        need(all(expected[n] == checksum for n, checksum in identity["payloadSha256"].items()), "Marker common payload differs from package")
        out.mkdir(parents=True)
        unsigned = out / "TurboStations-Premium-R143-core-options-unsigned.apk"
        with zipfile.ZipFile(unsigned, "w", allowZip64=False) as destination:
            for item in original.infolist():
                with destination.open(copy.copy(item), "w", force_zip64=False) as target:
                    if item.filename in files:
                        with files[item.filename].open("rb") as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
                    else:
                        with original.open(item.filename) as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
    need(verify_commit(a.source_commit) == pins, "Sources changed during package assembly")
    receipt = dict(schema="station.r143.snes-multitap-unique-flag.package.v1", passed=True, sourceCommit=a.source_commit, sourceFiles=pins,
        baselineApkSha256=BASE, baselineApkBytes=BASE_BYTES, unsignedApkSha256=sha(unsigned), unsignedApkBytes=unsigned.stat().st_size,
        replacedEntries=sorted(REPLACED), addedEntries=[], removedEntries=[], preservedEntryCount=13855,
        baselineEntryCount=13860, finalEntryCount=13860, expectedEntrySha256=expected,
        nativeRuntimeSha256=RETRO, clinicalQualificationSha256=CLINICAL_SHA,
        runtimeIdentityReceiptSha256=sha(a.identity / "runtime-identity.json"), **state_fields())
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("base", "dex", "dex-receipt", "identity", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    result = build(p.parse_args())
    print(json.dumps({"passed": True, "unsignedApkSha256": result["unsignedApkSha256"], "revision": "R143"}))
