"""Resolve the exact R66 Java inputs, then apply the reviewed R67 security delta."""
from pathlib import Path
import hashlib, json

SNAPSHOT = Path(__file__).resolve().parent.parent
VERSIONS = SNAPSHOT.parent
PREFIXES = ('client/src/java/', 'netplay-src/', 'dependency-src/')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def composition():
    base = VERSIONS / 'station-current-r55-20261006'
    result = {}
    # DEX28 did not change between the published R55 snapshot and R66.
    frozen = json.loads((base / 'SOURCE-MANIFEST.json').read_text('utf8'))
    for name, entry in frozen['files'].items():
        if name.startswith('client/src/java/') and name.endswith('.java'):
            source = base / name
            assert sha(source) == entry['sha256'], name
            result[name] = source
    r64 = VERSIONS / 'station-online-controls-r64-20261007'
    current = json.loads((r64 / 'JAVA-BUILD-RECEIPT.json').read_text('utf8'))['files']
    roots = [r64, VERSIONS / 'station-auto-access-r63-20261006',
             VERSIONS / 'station-online-integrated-r62-20261006',
             VERSIONS / 'station-layout-r57-20261006', base]
    assert len(current) == 161
    for raw, expected in current.items():
        name = raw.replace('\\', '/')
        assert name.endswith('.java') and name.startswith(('netplay-src/', 'dependency-src/'))
        source = next((root / name for root in roots if (root / name).is_file()), None)
        assert source and sha(source) == expected, 'R66 input mismatch: ' + name
        result[name] = source
    baseline = {name: sha(source) for name, source in result.items()}
    for prefix in PREFIXES:
        for source in (SNAPSHOT / prefix).rglob('*.java'):
            result[source.relative_to(SNAPSHOT).as_posix()] = source
    return result, baseline

def verified_composition():
    files, baseline = composition()
    receipt = json.loads((SNAPSHOT / 'JAVA-SOURCE-MANIFEST.json').read_text('utf8'))
    assert receipt['baseline'] == baseline, 'Original compiler inputs changed'
    assert receipt['files'] == {name: sha(source) for name, source in files.items()}, 'R67 source manifest differs'
    return files
