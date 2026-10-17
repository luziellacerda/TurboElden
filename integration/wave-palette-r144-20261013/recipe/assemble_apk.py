"""Assemble R144 visual changes: six replacements, no entry additions or removals."""
from pathlib import Path
import argparse
import copy
import json
import re
import shutil
import sys
import zipfile

sys.dont_write_bytecode = True
zipfile.ZIP64_LIMIT = (1 << 32) - 1
from common import (BASE, BASE_BYTES, DEX, RETRO, ROOT, PARTITION, CAROUSEL, CAROUSEL_SHA,
                    PRESERVED_DEX35, WRAPPERS, REPLACED, need, sha, read, fingerprints,
                    entry_sha, verify_commit, isolated, state_fields, elf_contract)
from build_identity import (ROOT_DEX, DEPENDENCIES, validate_dex_receipt, validate_native_receipt,
                            expected_payload, validate_marker_bindings)


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed stable R143 donor required")
    pins = verify_commit(a.source_commit)
    dex = validate_dex_receipt(read(a.dex_receipt), a.dex, a.source_commit, pins)
    native = validate_native_receipt(read(a.native_receipt), a.native, a.source_commit, pins)
    identity = read(a.identity / "runtime-identity.json")
    need(identity.get("schema") == "station.r144.wave-palette.identity.v1" and identity.get("passed") is True and
         identity.get("compiled") is True and all(identity.get(key) == value for key, value in state_fields().items()) and
         identity.get("sourceCommit") == a.source_commit and identity.get("sourceFiles") == pins and
         identity.get("retainedIdentityDependencies") == DEPENDENCIES and identity.get("baselineApkSha256") == BASE and
         identity.get("dexSha256") == sha(a.dex) and identity.get("carouselSha256") == sha(a.native) and
         identity.get("dexBuildReceiptSha256") == sha(a.dex_receipt) and identity.get("nativeBuildReceiptSha256") == sha(a.native_receipt) and
         identity.get("preservedRetroArchSha256") == RETRO and identity.get("preservedDex35Sha256") == PRESERVED_DEX35 and
         identity.get("inheritedPayloadCount") == identity.get("finalPayloadCount") == 345 and
         identity.get("changedPayloadEntries") == sorted({PARTITION, CAROUSEL}),
         "Exact qualified candidate identity and both frozen visual receipts required")
    files = {PARTITION: a.dex, CAROUSEL: a.native, "assets/station-online/engines.json": a.identity / "engines.json"}
    for kind, (library, _) in WRAPPERS.items():
        path = a.identity / "native" / library if kind == "psx" else a.identity / library
        need(sha(path) == identity["markers"][kind]["runtimeSha256"], "Qualified wrapper binary differs: " + kind)
        files["lib/arm64-v8a/" + library] = path
    need(set(files) == REPLACED and len(files) == 6 and
         sha(files["assets/station-online/engines.json"]) == identity["enginesAssetSha256"],
         "Exactly six replacements with no additions allowed")
    out = isolated(a.out)
    with zipfile.ZipFile(a.base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and REPLACED <= set(names) and
             {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)} == ROOT_DEX,
             "Exact stable donor entry and 40-DEX inventory required")
        previous = fingerprints(original)
        payload = expected_payload(previous, a.dex, a.native)
        expected_registry, selected = validate_marker_bindings(original, previous, payload, pins, identity["markers"], files)
        old_registry = json.loads(original.read("assets/station-online/engines.json"))
        registry = read(files["assets/station-online/engines.json"])
        retro = [row for row in old_registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
        need(registry == expected_registry and identity["engines"] == selected and len(old_registry["engines"]) == 13 and
             len(registry["engines"]) == 13 and len(retro) == 9 and identity["preservedRetroArchDescriptors"] == retro and
             [row for row in registry["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
             "Original nine RetroArch descriptors and four independent owner policies must stay exact")
        before = {name: entry_sha(original, name) for name in names}
        need(before[PARTITION] == DEX and before[CAROUSEL] == CAROUSEL_SHA and before["classes35.dex"] == PRESERVED_DEX35 and
             before["lib/arm64-v8a/libstation_retroarch.so"] == RETRO and
             {name: before[name] for name in ROOT_DEX - {PARTITION}} == dex["preservedDexSha256"] and
             all(before[name] == checksum for name, checksum in previous["psx"]["payloadSha256"].items()),
             "Exact donor DEX, runtime and complete inherited marker payload required")
        need(payload == identity["payloadSha256"], "Qualified complete visual payload binding differs")
        old_contract, new_contract = elf_contract(original.read(CAROUSEL)), elf_contract(a.native.read_bytes())
        need(old_contract["exports"] == new_contract["exports"] and old_contract["needed"] == new_contract["needed"] and
             old_contract["soname"] == new_contract["soname"] == ["libturbo_carousel.so"],
             "Native carousel API/dependencies/SONAME changed")
        expected = {**before, **{name: sha(path) for name, path in files.items()}}
        need({name for name in before if before[name] != expected[name]} == REPLACED and
             all(expected[name] == checksum for name, checksum in payload.items()),
             "Exact six changed entries and all 345 bound payloads required")
        out.mkdir(parents=True)
        unsigned = out / "TurboStations-Premium-R144-ondas-unsigned.apk"
        with zipfile.ZipFile(unsigned, "w", allowZip64=False) as destination:
            for item in original.infolist():
                with destination.open(copy.copy(item), "w", force_zip64=False) as target:
                    if item.filename in files:
                        with files[item.filename].open("rb") as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
                    else:
                        with original.open(item.filename) as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
    with zipfile.ZipFile(unsigned) as archive:
        need(len(archive.namelist()) == len(set(archive.namelist())) == 13860 and
             {name: entry_sha(archive, name) for name in archive.namelist()} == expected,
             "Independent full assembled entry readback failed")
    need(verify_commit(a.source_commit) == pins and read(a.dex_receipt) == dex and read(a.native_receipt) == native,
         "Frozen sources or qualified receipts changed during assembly")
    receipt = dict(schema="station.r144.wave-palette.package.v1", passed=True, sourceCommit=a.source_commit, sourceFiles=pins,
        baselineApkSha256=BASE, baselineApkBytes=BASE_BYTES, unsignedApkSha256=sha(unsigned), unsignedApkBytes=unsigned.stat().st_size,
        replacedEntries=sorted(REPLACED), addedEntries=[], removedEntries=[], preservedEntryCount=13854,
        baselineEntryCount=13860, finalEntryCount=13860, expectedEntrySha256=expected,
        preservedDexSha256=dex["preservedDexSha256"], preservedDex35Sha256=PRESERVED_DEX35,
        nativeRuntimeSha256=RETRO, carouselSha256=sha(a.native), carouselContract=new_contract,
        preservedRetroArchDescriptors=retro, renewedIndependentEngines=selected, renewedRuntimeMarkers=identity["markers"],
        payloadSha256=payload, runtimeIdentityReceiptSha256=sha(a.identity / "runtime-identity.json"),
        dexBuildReceiptSha256=sha(a.dex_receipt), nativeBuildReceiptSha256=sha(a.native_receipt),
        retainedIdentityDependencies=DEPENDENCIES, **state_fields())
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "dex", "dex-receipt", "native", "native-receipt", "identity", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    result = build(parser.parse_args())
    print(json.dumps({"passed": True, "unsignedApkSha256": result["unsignedApkSha256"], "revision": "R144"}))
