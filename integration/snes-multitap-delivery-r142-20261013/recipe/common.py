"""Closed R142 binding scope over the exact original R139, with clinical host gate."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = "b5a76023860bceb2aa11c946c8003fa2d92951e700dbde3a498f8316857670d4"
BASE_BYTES = 2715008015
DEX = "49f381dc3ef375797d2db56b25a8a6c86a8150c2515ce115f4639b7bb243478e"
RETRO = "ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378"
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
PARTITION = "classes35.dex"
CLINICAL_RELATIVE = "integration/snes-multitap-delivery-r142-20261013/evidence/host-control-reader.json"
CLINICAL_SHA = "bd931f8cb1093d61524b95ce959d2b6859affd50c25d6e2e34594308691ac633"
RUNLOOP_SHA = "13179287191fe00a76c6d35ddc75374388543b2c05607b14dc8c6efef135a012"
WRAPPERS = {
    "psx": ("libstation_psx_online.so", "e990120d57cc8fac22a5f9809d6289e2f630c732a2341371c50afafb496bff20"),
    "n64": ("libstation_mupen64plus_runtime.so", "6638adec6f02917243f5a84c0d0a88d966254440fee369c700020fd9a4587b56"),
    "dolphin": ("libstation_dolphin_runtime.so", "0f8cb2115a397895b3f201da64d79e1897eca16440d0687eddb4792f32164639"),
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
             if p.is_file() and p.suffix in {".py", ".java", ".smali"}}
    files["PROPOSED-SCOPE.json"] = sha(ROOT / "PROPOSED-SCOPE.json")
    need(not (ROOT / "native").exists() and not (ROOT / "java").exists(), "No added productive Java/native code allowed")
    return files


def verify_clinical(path):
    need(Path(path).resolve() == (REPO / CLINICAL_RELATIVE).resolve() and sha(path) == CLINICAL_SHA, "Exact qualified host control-reader receipt required")
    value = read(path)
    need(value.get("passed") is True and value.get("executedCases") == 1 and value.get("unchangedRuntimeSha256") == RETRO and value.get("productionRemapLoaderExecuted") is True and value.get("productionControllerInitExecuted") is True and value.get("globalConfigDeviceKeyNotRead") is True and value.get("extractedBodiesByteExact") is True and value.get("actualAndroidVariablesMeasured") is False, "Host qualification scope differs")
    return value


def verify_commit(commit):
    need(re.fullmatch("[0-9a-f]{40}", commit or ""), "Full frozen R142 source commit required before build")
    pins = source_map()
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, expected in {**{prefix + "/" + n: h for n, h in pins.items()}, CLINICAL_RELATIVE: CLINICAL_SHA}.items():
        raw = subprocess.check_output(["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO), "show", commit + ":" + name], stderr=subprocess.PIPE)
        need(digest(raw) == expected, "Frozen R142 source/provenance mismatch: " + name)
    verify_clinical(REPO / CLINICAL_RELATIVE)
    return pins


def isolated(path):
    output = Path(path).resolve()
    need(not output.exists(), "New isolated output directory required")
    need(REPO != output and REPO not in output.parents and ".git" not in output.parts, "Output outside source repository required")
    return output


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, "R142 build stage failed: " + result.stderr[-1600:])
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
    return dict(revision="R142", candidateOnly=True, diagnosticLoggerIncluded=False, nativeRuntimeRebuilt=False,
                promoted=False, installed=False, serverRegistered=False, physicalGameplayValidated=False)
