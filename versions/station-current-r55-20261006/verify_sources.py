"""Read-only verification of the published source snapshot; does not compile/install."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
manifest = json.loads((root / "SOURCE-MANIFEST.json").read_text("utf-8"))
for relative, expected in manifest["files"].items():
    path = root / relative
    assert path.resolve().is_relative_to(root.resolve()), relative
    assert path.stat().st_size == expected["bytes"], relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected["sha256"], relative
print("Source snapshot verified:", len(manifest["files"]), "files")
