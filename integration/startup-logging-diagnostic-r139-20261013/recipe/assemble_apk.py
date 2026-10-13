"""Assemble an unpromoted diagnostic: five replacements, one logger library addition."""
from pathlib import Path
import argparse
import copy
import json
import shutil
import struct
import sys
import zipfile

sys.dont_write_bytecode = True
from common import BASE, BASE_BYTES, DEX, RETRO, PARTITION, WRAPPERS, SIDE, REPLACED, ROOT, need, sha, digest, read, entry_sha, verify_commit, isolated, temporary_fields


def elf(raw):
    need(raw[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", raw, 18)[0] == 183, "AArch64 sidecar required")
    phoff = struct.unpack_from("<Q", raw, 32)[0]
    size, count = struct.unpack_from("<HH", raw, 54)
    alignments = [struct.unpack_from("<Q", raw, phoff + i * size + 48)[0]
                  for i in range(count) if struct.unpack_from("<I", raw, phoff + i * size)[0] == 1]
    need(alignments and min(alignments) >= 16384, "16 KiB sidecar LOAD alignment required")
    need(b"Java_org_emulationstation_frontend_netplay_StationStartupLogging_enable\0" in raw, "Logger JNI symbol missing")
    return min(alignments)


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R139 donor required")
    pins = verify_commit(a.source_commit)
    identity = read(a.identity / "runtime-identity.json")
    need(identity.get("passed") is True and identity.get("compiled") is True and identity.get("diagnosticTemporary") is True and
         identity.get("sourceCommit") == a.source_commit and identity.get("sourceFiles") == pins and
         identity.get("baselineApkSha256") == BASE and identity.get("dexSha256") == sha(a.dex) and
         identity.get("sidecarSha256") == sha(a.sidecar) and identity.get("preservedRetroArchSha256") == RETRO and
         identity.get("finalPayloadCount") == 346, "Frozen diagnostic identity receipt required")
    dex = read(a.dex_receipt)
    side = read(a.sidecar_receipt)
    need(sha(a.dex_receipt) == identity["dexBuildReceiptSha256"] and sha(a.sidecar_receipt) == identity["sidecarBuildReceiptSha256"] and
         dex.get("inversePassed") is True and dex.get("unchangedClasses") == 606 and
         side.get("compiled") is True and side.get("diagnosticOnly") is True and side.get("sourceCommit") == a.source_commit and
         side.get("sidecarSha256") == sha(a.sidecar), "Diagnostic DEX/native build receipt differs")
    files = {PARTITION: a.dex, "assets/station-online/engines.json": a.identity / "engines.json", SIDE: a.sidecar}
    for kind, (name, _) in WRAPPERS.items():
        path = a.identity / "native" / name if kind == "psx" else a.identity / name
        need(sha(path) == identity["markers"][kind]["runtimeSha256"], "Renewed wrapper differs: " + kind)
        files["lib/arm64-v8a/" + name] = path
    need(set(files) == REPLACED | {SIDE} and sha(files["assets/station-online/engines.json"]) == identity["enginesAssetSha256"], "Only five replacements plus logger allowed")
    alignment = elf(a.sidecar.read_bytes())
    out = isolated(a.out)
    with zipfile.ZipFile(a.base) as original:
        names = original.namelist()
        need(len(names) == len(set(names)) == 13860 and SIDE not in names and REPLACED <= set(names), "Exact donor entries required")
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
        unsigned = out / "TurboStations-R139-DIAG-startup-unsigned.apk"
        with zipfile.ZipFile(unsigned, "w", allowZip64=True) as destination:
            for item in original.infolist():
                with destination.open(copy.copy(item), "w", force_zip64=True) as target:
                    if item.filename in files:
                        with files[item.filename].open("rb") as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
                    else:
                        with original.open(item.filename) as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
            item = zipfile.ZipInfo(SIDE)
            item.compress_type = zipfile.ZIP_STORED
            item.external_attr = 0o100644 << 16
            with destination.open(item, "w", force_zip64=True) as target, a.sidecar.open("rb") as source:
                shutil.copyfileobj(source, target, 1024 * 1024)
    need(verify_commit(a.source_commit) == pins, "Sources changed during package assembly")
    receipt = dict(schema="station.r139.startup-logging.package.v1", passed=True, sourceCommit=a.source_commit, sourceFiles=pins,
        baselineApkSha256=BASE, baselineApkBytes=BASE_BYTES, unsignedApkSha256=sha(unsigned), unsignedApkBytes=unsigned.stat().st_size,
        replacedEntries=sorted(REPLACED), addedEntries=[SIDE], removedEntries=[], preservedEntryCount=13855,
        baselineEntryCount=13860, finalEntryCount=13861, expectedEntrySha256=expected,
        nativeRuntimeSha256=RETRO, sidecarSha256=sha(a.sidecar), sidecarMinimumLoadAlignment=alignment,
        runtimeIdentityReceiptSha256=sha(a.identity / "runtime-identity.json"), **temporary_fields())
    (out / "unsigned-package.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("base", "dex", "dex-receipt", "identity", "sidecar", "sidecar-receipt", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    result = build(p.parse_args())
    print(json.dumps({"passed": True, "unsignedApkSha256": result["unsignedApkSha256"], "diagnosticTemporary": True}))
