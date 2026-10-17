"""Renew only three R139 DEX-bound wrappers for the one-method R140 binding."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import os
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
from common import BASE, DEX, RETRO, ROOT, REPO, PARTITION, WRAPPERS, CLINICAL_SHA, need, sha, digest, canonical, read, fingerprints, entry_sha, verify_commit, isolated, state_fields


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    previous_path = list(sys.path)
    try:
        sys.path.insert(0, str(path.parent))
        spec.loader.exec_module(result)
    finally:
        sys.path[:] = previous_path
    return result


def build(a):
    need(sha(a.base) == BASE, "Exact R139 signed donor required")
    pins = verify_commit(a.source_commit)
    dex = read(a.dex_receipt)
    need(dex.get("passed") is True and dex.get("compiled") is True and dex.get("diagnosticLoggerIncluded") is False and
         dex.get("sourceCommit") == a.source_commit and dex.get("sourceFiles") == pins and
         dex.get("baselineApkSha256") == BASE and dex.get("baselineDexSha256") == DEX and
         dex.get("outputDexSha256") == sha(a.dex) and dex.get("inversePassed") is True and
         dex.get("unchangedClasses") == 607 and dex.get("finalClassCount") == 608 and
         dex.get("clinicalQualificationSha256") == CLINICAL_SHA and
         dex.get("addedClasses") == [] and dex.get("removedClasses") == [], "Reviewed scoped R140 DEX required")
    with zipfile.ZipFile(a.base) as archive:
        previous = fingerprints(archive)
        need(entry_sha(archive, "lib/arm64-v8a/libstation_retroarch.so") == RETRO, "R139 RetroArch must stay exact")
        original = json.loads(archive.read("assets/station-online/engines.json"))
        inherited_payload = previous["psx"]["payloadSha256"]
        for name, expected in inherited_payload.items():
            need(entry_sha(archive, name) == expected, "Inherited wrapper payload changed: " + name)
    need(sha(a.dex) != DEX, "Only changed DEX binding required")
    expected = {**inherited_payload, PARTITION: sha(a.dex)}
    need(len(expected) == 345 and {n for n in inherited_payload if inherited_payload[n] != expected[n]} == {PARTITION},
         "Exactly 345 payload entries; only the DEX hash may change")
    transforms = dict(previous["psx"]["productiveTransforms"])
    for name, checksum in pins.items():
        key = ROOT.name + "/" + name
        need(key not in transforms, "R140 transform already in source chain")
        transforms[key] = checksum
    inherited = module(REPO / "integration/online-lifecycle-review-r135/recipe/build_runtime_identity.py", "r140_binding_inherited")
    # Validate the real retained native implementation, not a permissive fixture.
    for name in ("StationPsxEntry.cpp", "StationPsxOwner.cpp", "StationPsxOwner.hpp", "StationPsxProtocol.cpp", "StationPsxProtocol.hpp", "StationPsxSha256.cpp", "PsxPinnedOptions.h"):
        need(sha(inherited.PSX / "native" / name) == previous["psx"]["productiveTransforms"].get("native/" + name), "Original PSX source changed: " + name)
    inherited.native_tools(a.ndk)
    out = isolated(a.out)
    out.mkdir(parents=True)
    markers = {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE, payloadSha256=expected, productiveTransforms=transforms)
    need(inherited.policy(psx) == inherited.policy(previous["psx"]), "PSX behavior/policy changed")
    raw = canonical(psx)
    (out / "psx.fingerprint.json").write_bytes(raw + b"\n")
    identity_source = out / "StationPsxIdentity.cpp"
    identity_source.write_text(
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n', encoding="ascii")
    native = out / "native"
    subprocess.run([sys.executable, "-B", str(inherited.PSX / "recipe/build_entry.py"), "--ndk", str(a.ndk),
                    "--owner", str(inherited.PSX / "native"), "--protocol", str(inherited.PSX / "native"),
                    "--pinned-options", str(inherited.PSX / "native"), "--identity-source", str(identity_source), "--out", str(native)],
                   check=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    psx_binary = native / WRAPPERS["psx"][0]
    need(raw in psx_binary.read_bytes(), "PSX canonical identity embedding failed")
    markers["psx"] = dict(runtimeLibrary=psx_binary.name, runtimeSha256=sha(psx_binary), runtimeBytes=psx_binary.stat().st_size, fingerprintSha256=digest(raw))
    primitive = module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r140_binding_marker")
    for kind in ("n64", "dolphin"):
        value = copy.deepcopy(previous[kind])
        library, parent_runtime = WRAPPERS[kind]
        value.update(baseApkSha256=BASE, payloadSha256=expected, productiveTransforms=transforms,
                     parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_runtime,
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        need(inherited.policy(value) == inherited.policy(previous[kind]), "Independent owner behavior/policy changed: " + kind)
        (out / (library + ".fingerprint.json")).write_bytes(canonical(value) + b"\n")
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, a.ndk, out)
    updated, selected = inherited.expected_engines(original, markers)
    retro_before = [e for e in original["engines"] if e["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    retro_after = [e for e in updated["engines"] if e["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(retro_before) == 9 and retro_before == retro_after, "All nine RetroArch descriptors must stay exact")
    (out / "engines.json").write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(verify_commit(a.source_commit) == pins, "R140 source changed during wrapper build")
    receipt = dict(schema="station.r140.core-options-binding.identity.v1", passed=True, compiled=True, sourceCommit=a.source_commit,
        sourceFiles=pins, baselineApkSha256=BASE, dexSha256=sha(a.dex), payloadSha256=expected, markers=markers,
        engines=selected, enginesAssetSha256=sha(out / "engines.json"), preservedRetroArchSha256=RETRO,
        preservedRetroArchDescriptors=retro_after, clinicalQualificationSha256=CLINICAL_SHA,
        dexBuildReceiptSha256=sha(a.dex_receipt), inheritedPayloadCount=345, finalPayloadCount=345, **state_fields())
    (out / "runtime-identity.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("base", "dex", "dex-receipt", "ndk", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    result = build(p.parse_args())
    print(json.dumps({"revision": "R140", "renewedIndependentIds": len(result["engines"]), "preservedRetroArchDescriptors": 9}))
