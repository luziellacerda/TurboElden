"""Closed inputs for the R133 carousel-only overlay over the verified R132."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE_SHA = "47a619a194c095e70738a4d191fb8491ee410d868e4c11742530ffcaaf844f20"
BASE_BYTES = 2711825423
BASE_SOURCE = "56ba83b7fcc5c243ae50052fec9b6f4141e1b5f1"
CAROUSEL_SHA = "0dc370523a448f2966a53563d90a73b3dc1555648c2ab87c02ea1a17470053cb"
FRONTEND_SHA = "4e7ad58e1e8f8a284654120c27280eed8c124ad5301a9e87d769e41f100d8d0d"


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    require(not path.exists(), "Refusing to overwrite a receipt: " + path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def source_map():
    """Public productive code only; private atlas inputs are receipt-pinned."""
    result = {}
    suffixes = {".java", ".py", ".cpp", ".c", ".h", ".hpp", ".glsl"}
    excluded = {"tests", "evidence", "receipts", "out", "outputs", "build", "temp", "__pycache__"}
    for directory in ("java", "native", "recipe"):
        for path in sorted((ROOT / directory).rglob("*")):
            relative = path.relative_to(ROOT)
            if path.is_file() and path.suffix in suffixes and not excluded.intersection(relative.parts):
                require(not path.is_symlink(), "Productive source cannot be symbolic: " + relative.as_posix())
                result[relative.as_posix()] = sha(path)
    require(result and "recipe/build_runtime_identity.py" in result,
            "Complete productive R133 source map required")
    return result


def verify_source_commit(commit, pins=None):
    require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit),
            "Explicit full executable-source commit required")
    pins = source_map() if pins is None else pins
    git = ["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO)]
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, checksum in pins.items():
        raw = subprocess.check_output(git + ["show", commit + ":" + prefix + "/" + name], stderr=subprocess.PIPE)
        require(digest(raw) == checksum, "Source differs from selected committed bytes: " + name)
    return pins


def checked_file(record, label):
    require(isinstance(record, dict) and set(record) == {"path", "bytes", "sha256"} and
            isinstance(record["bytes"], int) and not isinstance(record["bytes"], bool) and record["bytes"] > 0 and
            isinstance(record["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", record["sha256"]),
            "Exact artifact record required: " + label)
    original = Path(record["path"])
    actual = original.resolve(strict=True)
    require(not original.is_symlink() and actual.is_file() and actual.stat().st_size == record["bytes"] and
            sha(actual) == record["sha256"], "Compiled artifact changed: " + label)
    return actual
