"""Closed R140 binding scope over the exact original R139, with clinical host gate."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = "19acdeceef86bc66c2475300cbd142da783850c02f5a9e2068d8652ef8523164"
BASE_BYTES = 2714991631
DEX = "dd6ea401376aafcba86518038fa2589c3d626c076cdcfc21252efca1a93ab6a9"
RETRO = "ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378"
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
PARTITION = "classes35.dex"
CLINICAL_RELATIVE = "audits/station-r139-core-options-binding-20261013/evidence/host-resolver-qualification.json"
CLINICAL_SHA = "42db9aa7537486f15b555987ac05d0d4850de7b34af9ffa5063a014438bfc821"
RUNLOOP_SHA = "13179287191fe00a76c6d35ddc75374388543b2c05607b14dc8c6efef135a012"
WRAPPERS = {
    "psx": ("libstation_psx_online.so", "c26d8836df255ad4cc10d19d328b6fc8dcbc6a429725794c88acd4de5ca3dc50"),
    "n64": ("libstation_mupen64plus_runtime.so", "2f248cfcdc9e6d0e20795b1dab84f581b8fe9ea59eb0994ae96036aed2abeb77"),
    "dolphin": ("libstation_dolphin_runtime.so", "2e0b362220979226c4996fce6691b9f8330fb9193e4d16c67b5f4c06e46bec82"),
}
REPLACED = {PARTITION, "assets/station-online/engines.json", *["lib/arm64-v8a/" + v[0] for v in WRAPPERS.values()]}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def read(path):
    return json.loads(Path(path).read_text("utf-8"))


def source_map():
    files = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "recipe").rglob("*"))
             if p.is_file() and p.suffix in {".py", ".java"}}
    files["PROPOSED-SCOPE.json"] = sha(ROOT / "PROPOSED-SCOPE.json")
    need(not (ROOT / "native").exists() and not (ROOT / "java").exists(), "No added productive Java/native code allowed")
    return files


def verify_clinical(path):
    need(Path(path).resolve() == (REPO / CLINICAL_RELATIVE).resolve() and sha(path) == CLINICAL_SHA, "Exact qualified host resolver receipt required")
    value = read(path)
    need(value.get("passed") is True and value.get("executedCases") == 20 and value.get("unchangedRuntimeSha256") == RETRO and
         value.get("runloopSourceSha256") == RUNLOOP_SHA and value.get("extractedBodiesByteExact") is True and
         value.get("productionResolverAndWrapperExecuted") is True and value.get("productionSetVariablesCallExecuted") is True and
         value.get("productSourceModified") is False and value.get("currentDeviceLegacyFileRead") is False and
         value.get("actualBsnesVariablesMeasured") is False, "Qualified path-selection scope differs")
    cases = value["cases"]
    states = {"none", "per-core", "game", "folder", "all"}
    settings = {"current-defaults", "global-only", "specific-off-only", "two-key-binding"}
    need(len(cases) == 20 and {(c["legacyFiles"], c["settings"]) for c in cases} == {(state, flag) for state in states for flag in settings}, "Complete twenty-case grid required")
    bound = [c for c in cases if c["settings"] == "two-key-binding"]
    need(len(bound) == 5 and all(c["globalCoreOptions"] is True and c["gameSpecificOptions"] is False and
         c["selected"] == "room" and c["canonicalPassedDirectlyToManager"] is True and c["inputClass"] == "canonical-HLE" and
         c["discoveryCalls"] == {"game": 0, "folder": 0, "core": 0} for c in bound), "Both flags must bind the canonical room directly in every state")
    need(all(c["sourceFilesUnchanged"] is True and c["settingsInputsUnchanged"] is True and c["unrelatedFlagsUnchanged"] is True for c in cases), "Clinical unrelated inputs changed")
    return value


def verify_commit(commit):
    need(re.fullmatch("[0-9a-f]{40}", commit or ""), "Full frozen R140 source commit required before build")
    pins = source_map()
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, expected in {**{prefix + "/" + n: h for n, h in pins.items()}, CLINICAL_RELATIVE: CLINICAL_SHA}.items():
        raw = subprocess.check_output(["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO), "show", commit + ":" + name], stderr=subprocess.PIPE)
        need(digest(raw) == expected, "Frozen R140 source/provenance mismatch: " + name)
    verify_clinical(REPO / CLINICAL_RELATIVE)
    return pins


def isolated(path):
    output = Path(path).resolve()
    need(not output.exists(), "New isolated output directory required")
    need(REPO != output and REPO not in output.parents and ".git" not in output.parts, "Output outside source repository required")
    return output


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, "R140 build stage failed: " + result.stderr[-1600:])
    return result.stdout.strip()


def extract_fingerprint(raw):
    docs = []
    for match in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw):
        end = raw.find(b"\0", match.start())
        if end < 0:
            continue
        try:
            value = json.loads(raw[match.start():end].decode("ascii"))
        except (ValueError, UnicodeError):
            continue
        if isinstance(value, dict) and "baseApkSha256" in value and "payloadSha256" in value:
            docs.append(value)
    need(len(docs) == 1, "Exactly one canonical wrapper identity required")
    value = docs[0]
    need(canonical(value) in raw and digest(canonical(value)).encode("ascii") in raw, "Embedded wrapper fingerprint differs")
    return value


def fingerprints(archive):
    result = {}
    for kind, (name, old_hash) in WRAPPERS.items():
        raw = archive.read("lib/arm64-v8a/" + name)
        need(digest(raw) == old_hash, "Exact original R139 wrapper required")
        value = extract_fingerprint(raw)
        need(len(value["payloadSha256"]) == 345 and value["payloadSha256"].get(PARTITION) == DEX, "Exact R139 wrapper payload required")
        result[kind] = value
    need(all(v["payloadSha256"] == result["psx"]["payloadSha256"] and v["productiveTransforms"] == result["psx"]["productiveTransforms"] for v in result.values()), "Inherited common payload/source chains differ")
    return result


def entry_sha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def state_fields():
    return dict(revision="R140", candidateOnly=True, diagnosticLoggerIncluded=False, nativeRuntimeRebuilt=False,
                promoted=False, installed=False, serverRegistered=False, physicalGameplayValidated=False)
