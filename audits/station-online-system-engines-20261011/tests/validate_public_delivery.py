"""Validate the source-only audit and isolated candidate; no APK is modified."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

AUDIT = "audits/station-online-system-engines-20261011"
CANDIDATE = "candidates/station-explus-frame-gate-20261011"
ALLOWED = {".md", ".json", ".py", ".ps1", ".java", ".cpp", ".hpp", ".h", ".txt"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())


def validate_manifest(root: Path, filename: str) -> int:
    manifest = json.loads((root / filename).read_text(encoding="utf-8-sig"))
    expected = manifest["files"]
    count = 0
    actual = {p.relative_to(root).as_posix() for p in files(root) if p != root / filename}
    assert actual == set(expected), (filename, "Manifest file set changed", actual ^ set(expected))
    for name, entry in expected.items():
        path = root / name
        assert path.stat().st_size == entry["bytes"], (name, "Size mismatch")
        assert digest(path) == entry["sha256"], (name, "Hash mismatch")
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    roots = [repo / AUDIT, repo / CANDIDATE]
    counts = {"textFiles": 0, "jsonFiles": 0, "pythonSources": 0, "relativeLinks": 0}
    for root in roots:
        for path in files(root):
            assert path.name == ".gitattributes" or path.suffix in ALLOWED, (path, "Nonpublic artifact type")
            text = path.read_text(encoding="utf-8-sig")
            assert "\x00" not in text, (path, "Binary content")
            counts["textFiles"] += 1
            if path.suffix == ".json":
                json.loads(text)
                counts["jsonFiles"] += 1
            elif path.suffix == ".py":
                ast.parse(text, filename=path.name)
                counts["pythonSources"] += 1
            elif path.suffix == ".md":
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                    if "://" in target or target.startswith("#"):
                        continue
                    target = target.split("#", 1)[0]
                    assert (path.parent / target).resolve().exists(), (path, target, "Broken relative link")
                    counts["relativeLinks"] += 1
    audit = roots[0]
    if args.write_manifest:
        entries = {
            path.relative_to(audit).as_posix(): {"bytes": path.stat().st_size, "sha256": digest(path)}
            for path in files(audit) if path.name != "AUDIT-MANIFEST.json" or path.parent != audit
        }
        manifest = {
            "schemaVersion": 1,
            "role": "read-only-audit-and-reproducible-probes",
            "executableChanged": False,
            "binariesIncluded": False,
            "files": entries,
        }
        (audit / "AUDIT-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    counts["rootManifestFiles"] = validate_manifest(audit, "AUDIT-MANIFEST.json")
    counts["candidateManifestFiles"] = validate_manifest(roots[1], "CANDIDATE-MANIFEST.json")
    counts["snesAuditManifestFiles"] = validate_manifest(audit / "snes-megadrive", "AUDIT-MANIFEST.json")
    print(json.dumps({"passed": True, **counts, "apkModified": False, "gameplayValidated": False}))


if __name__ == "__main__":
    main()
