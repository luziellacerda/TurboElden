"""Shared guards for the isolated R139 diagnostic, never a current release."""
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
PARTITION = "classes35.dex"
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
WRAPPERS = {
    "psx": ("libstation_psx_online.so", "c26d8836df255ad4cc10d19d328b6fc8dcbc6a429725794c88acd4de5ca3dc50"),
    "n64": ("libstation_mupen64plus_runtime.so", "2f248cfcdc9e6d0e20795b1dab84f581b8fe9ea59eb0994ae96036aed2abeb77"),
    "dolphin": ("libstation_dolphin_runtime.so", "2e0b362220979226c4996fce6691b9f8330fb9193e4d16c67b5f4c06e46bec82"),
}
SIDE = "lib/arm64-v8a/libstation_startup_logging.so"
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
    files = {p.relative_to(ROOT).as_posix(): sha(p)
            for folder in ("java", "recipe", "native")
            for p in sorted((ROOT / folder).rglob("*"))
            if p.is_file() and p.suffix in {".py", ".java", ".c", ".h"}}
    for name in ("native/COPYING", "native/base-receipt.json"):
        need((ROOT / name).is_file(), "Diagnostic native provenance/license missing: " + name)
        files[name] = sha(ROOT / name)
    return files


def verify_commit(commit):
    need(re.fullmatch("[0-9a-f]{40}", commit or ""), "Full frozen diagnostic source commit required")
    pins = source_map()
    need(pins and any(n.endswith(".c") for n in pins), "Frozen sidecar and Java sources required")
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, expected in pins.items():
        raw = subprocess.check_output(["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO), "show", commit + ":" + prefix + "/" + name], stderr=subprocess.PIPE)
        need(digest(raw) == expected, "Frozen source mismatch: " + name)
    return pins


def isolated(path):
    output = Path(path).resolve()
    need(not output.exists(), "New isolated output directory required")
    need(REPO != output and REPO not in output.parents and ".git" not in output.parts, "Build output outside repository required")
    return output


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, "Diagnostic build stage failed: " + result.stderr[-1600:])
    return result.stdout.strip()


def fingerprints(archive):
    result = {}
    for kind, (name, old_hash) in WRAPPERS.items():
        raw = archive.read("lib/arm64-v8a/" + name)
        need(digest(raw) == old_hash, "Exact R139 wrapper required: " + kind)
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
        need(len(docs) == 1, "Exactly one wrapper fingerprint required")
        value = docs[0]
        need(canonical(value) in raw and digest(canonical(value)).encode("ascii") in raw, "Original canonical fingerprint required")
        need(len(value["payloadSha256"]) == 345 and value["payloadSha256"].get(PARTITION) == DEX, "R139 wrapper DEX binding differs")
        result[kind] = value
    need(all(v["payloadSha256"] == result["psx"]["payloadSha256"] and v["productiveTransforms"] == result["psx"]["productiveTransforms"] for v in result.values()), "Wrapper common payload/source chain differs")
    return result


def entry_sha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def temporary_fields():
    return dict(diagnosticTemporary=True, permanentRelease=False, promoted=False,
                installed=False, serverRegistered=False, physicalGameplayValidated=False)
