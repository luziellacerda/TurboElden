"""Apply only four reviewed native files after checking all original and staged hashes."""
from pathlib import Path
import argparse
import hashlib
import json

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--target', type=Path, required=True)
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
target = args.target.resolve()
manifest = json.loads((root / 'tools/source-manifest.json').read_text(encoding='utf-8'))
pending = []
for entry in manifest['files']:
    rel = Path(entry['path'])
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('Invalid relative path')
    source = root / rel
    destination = target / rel
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != entry['sha256']:
        raise ValueError(f'Staged source changed: {rel}')
    actual = hashlib.sha256(destination.read_bytes()).hexdigest() if destination.exists() else None
    if actual == entry['sha256']:
        continue
    if actual != entry['originalSha256']:
        raise ValueError(f'Base changed; reconcile instead of overwriting: {rel}')
    pending.append((source, destination))
if args.apply:
    for source, destination in pending:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
print(json.dumps({'applied': args.apply, 'target': str(target), 'changedFiles': len(pending),
                  'paths': [str(destination.relative_to(target)) for _, destination in pending]}, indent=2))
