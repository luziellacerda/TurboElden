"""Shared closed-input helpers for the R132 composition; no external IO."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE_SHA = "0273ab9ae1b7ef5a061fdcc76c49558db4180bedd10a8100e6d5f764ac2ab175"
BASE_BYTES = 2711825423
CAROUSEL_SHA = "45e8131c0fc59f5c4627950c3aaed7b05dee1b519704d173698d5f56644fb806"
FRONTEND_SHA = "de092671462a0960665d06d1b463cd48108e65c599c5125c733d7205dd463468"

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write(path, value):
    path = Path(path)
    require(not path.exists(), "Refusing to overwrite a receipt: " + path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def source_map():
    """Same productive-source scope as build_runtime_identity.source_map."""
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
            "Complete productive R132 source map required")
    return result

def verify_source_commit(commit):
    require(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "Explicit source commit required")
    git = ["git", "-c", "safe.directory="+REPO.as_posix(), "-C", str(REPO)]
    # Later receipt/document commits may advance HEAD. Every productive file
    # must still equal the explicitly selected executable-source commit.
    for name, checksum in source_map().items():
        tracked = subprocess.check_output(git+["show", commit+":integration/startup-cleanup-r132/"+name])
        require(hashlib.sha256(tracked).hexdigest() == checksum, "Source differs from committed bytes: "+name)
    return source_map()

def run(command, work, label):
    work = Path(work)
    temp = work / "temp"
    temp.mkdir(exist_ok=True)
    env = {**os.environ, "TEMP": str(temp), "TMP": str(temp), "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(list(map(str, command)), cwd=work, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=1800)
    (work/(label+".log")).write_text(result.stdout+result.stderr, encoding="utf-8")
    require(result.returncode == 0, "Tool failed: "+label+"; inspect its local log")
    return result.stdout
