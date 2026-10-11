"""Isolated checks of the real R126 identity/registry transformation.

Fake marker hashes deliberately exercise JSON structure only. This does not
emit a runtime, APK, authenticated profile or server registration.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import zipfile

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r126_identity", HERE / "recipe/build_runtime_identity.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
checks = 0

def check(value, message):
    global checks
    checks += 1
    if not value: raise AssertionError(message)

def reject(call, message):
    caught = False
    try: call()
    except (ValueError, AssertionError): caught = True
    check(caught, message)

def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--base", type=Path, required=True); p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    with zipfile.ZipFile(a.base) as archive:
        original = json.loads(archive.read("assets/station-online/engines.json"))
    old = copy.deepcopy(original)
    backend, n64_options = m.literals(m.R125 / "java/org/emulationstation/frontend/netplay/StationN64Launch.java")
    dpl_backend, dpl_options = m.literals(HERE / "java/org/emulationstation/frontend/netplay/StationDolphinLaunch.java")
    core = "1" * 64; runtime = "2" * 64
    fixtures = {"n64": {"backend": backend, "options": n64_options, "coreSha256": core, "dependencies": {}},
                "dolphin": {"backend": dpl_backend, "options": dpl_options, "libraries": {m.DOLPHIN_NAMES[0]: {"sha256": core}}, "dependencies": {}}}
    markers = {"n64": {"runtimeLibrary": m.N64_MARKER, "runtimeSha256": runtime},
               "dolphin": {"runtimeLibrary": m.DOLPHIN_MARKER, "runtimeSha256": "3" * 64}}
    manifest, entries = m.engines(original, fixtures, markers)
    check(original == old, "input manifest was mutated")
    check(len(entries) == 3, "must create three identities")
    check(len(manifest["engines"]) == len(original["engines"]) + 2, "N64 replace plus two native Dolphin entries")
    check(not any(e["engineId"] == m.N64_OLD_ID for e in manifest["engines"]), "old N64 cannot remain selected")
    check(len({e["engineId"] for e in manifest["engines"]}) == len(manifest["engines"]), "engine IDs unique")
    for engine in entries:
        platform = engine["platform"]
        check(engine["maximumPlayers"] == 4, "physical controller ceiling")
        check(engine["controllerProfiles"] == [m.PROFILES[platform]], "exact system controller profile")
        check(engine["recoveryProtocol"] == "station-stream.v3", "exact transport version")
        check(engine["status"] == "implemented-candidate-peer-gameplay-pending", "no gameplay claim")
        check(engine["runtimeSha256"] == markers["n64" if platform == "n64" else "dolphin"]["runtimeSha256"], "exact marker identity")
        check(engine["contentIdentityByExtension"] == {"default": "launch-file-v1"}, "content identity remains launch bytes")
    gc = next(e for e in entries if e["platform"] == "gamecube")
    wii = next(e for e in entries if e["platform"] == "wii")
    check(gc["coreSha256"] == wii["coreSha256"] and gc["runtimeSha256"] == wii["runtimeSha256"], "shared real binary, distinct platform entries")
    check(gc["engineId"] != wii["engineId"], "no cross-platform engine alias")
    check("gcm" in gc["extensions"] and "wbfs" not in gc["extensions"], "GC format scope")
    check("wbfs" in wii["extensions"] and "gcm" not in wii["extensions"], "Wii format scope")
    for forbidden in ("elf", "dol", "wad", "zip", "nsp", "xci"):
        check(forbidden not in gc["extensions"] and forbidden not in wii["extensions"], "reject unrelated executable/container format")
    for before, after in zip(original["engines"], manifest["engines"]):
        if before["platform"] != "n64": check(before == after, "unrelated engine must remain unchanged")
    for before, after in zip(original.get("platformPolicies", []), manifest.get("platformPolicies", [])):
        if before["platform"] in ("gamecube", "wii"):
            check(after["automaticRoomIntegrationReady"] == before["automaticRoomIntegrationReady"], "no fabricated service readiness")
            check({k:v for k,v in before.items() if k != "reason"} == {k:v for k,v in after.items() if k != "reason"}, "only GC/Wii reason changed")
        else: check(before == after, "unrelated policy unchanged")
    gc_profile = m.profile_bytes(m.PROFILES["gamecube"], dpl_options)
    wii_profile = m.profile_bytes(m.PROFILES["wii"], dpl_options)
    check(gc_profile != wii_profile and m.digest(gc_profile) != m.digest(wii_profile), "GC and Wii profiles never interchangeable")
    check(m.digest(m.profile_bytes(m.PROFILES["n64"], n64_options)) == "2966309729f8a19c03b564f0178f263170e1843172f6719002f35fb54e313f9c", "N64 exact profile preserved")
    check(gc_profile.startswith(b'{"schemaVersion":1,"controllerProfile":'), "Java canonical order")
    check(gc_profile.endswith(b'"}'), "LF escaped in exact JSON string")
    invalid = copy.deepcopy(original); invalid["engines"].append(copy.deepcopy(next(e for e in original["engines"] if e["platform"] == "n64")))
    reject(lambda:m.engines(invalid, fixtures, markers), "duplicate N64 not silently selected")
    for platform in ("gamecube", "wii"):
        invalid = copy.deepcopy(original); invalid["engines"].append({"platform": platform, "engineId": "other-live-backend"})
        reject(lambda:m.engines(invalid, fixtures, markers), "never append behind live Dolphin engine")
    reject(lambda:m.payload_mapping(["classes35.dex=fixture"]), "missing final payloads refused")
    reject(lambda:m.payload_mapping(["classes37.dex=fixture"]), "unknown DEX refused")
    reject(lambda:m.checked_output(Path(r"G:\Unrelated\identity")), "output confinement")
    receipt = {"checks": checks, "failures": 0, "scope": "isolated-json-and-canonical-profile-transformation",
               "actualRuntimeEmitted": False, "apkChanged": False, "serverRegistrationConfirmed": False,
               "physicalGameplayValidated": False, "recipeSha256": m.sha(HERE / "recipe/build_runtime_identity.py")}
    m.fs(a.out).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": checks, "failures": 0, "physicalGameplayValidated": False}))

if __name__ == "__main__": main()
