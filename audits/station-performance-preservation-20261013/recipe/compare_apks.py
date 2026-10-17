"""Compare every uncompressed APK entry using SHA256, without changing inputs."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile


def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(path, expected):
    digest = file_hash(path)
    if digest != expected:
        raise ValueError('APK does not match its reviewed SHA256: ' + path.name)
    entries = {}
    with zipfile.ZipFile(path) as archive:
        for entry in archive.infolist():
            if entry.filename in entries:
                raise ValueError('Duplicate archive entry')
            with archive.open(entry) as stream:
                checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
            entries[entry.filename] = {'bytes': entry.file_size, 'sha256': checksum}
    return {'apkBasename': path.name, 'bytes': path.stat().st_size, 'sha256': digest,
            'entryCount': len(entries)}, entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('baseline', 'candidate'):
        parser.add_argument('--' + name, type=Path, required=True)
        parser.add_argument('--' + name + '-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    destination = args.out.resolve()
    repo = Path(__file__).resolve().parents[3]
    if destination.exists() or destination == repo or repo in destination.parents:
        raise ValueError('Choose a fresh output outside the repository')
    for path in (args.baseline.resolve(), args.candidate.resolve()):
        if destination == path or destination in path.parents:
            raise ValueError('Output cannot contain the input APKs')
    baseline, old = inventory(args.baseline, args.baseline_sha256.lower())
    candidate, new = inventory(args.candidate, args.candidate_sha256.lower())
    common = old.keys() & new.keys()
    changed = [{'entry': name, 'before': old[name], 'after': new[name]}
               for name in sorted(common) if old[name] != new[name]]
    report = {'method': 'SHA256 of whole APK and every uncompressed entry; no CRC-only shortcut',
              'baseline': baseline, 'candidate': candidate,
              'added': sorted(new.keys() - old.keys()), 'removed': sorted(old.keys() - new.keys()),
              'changed': changed, 'preservedEntryCount': len(common) - len(changed),
              'inputsChanged': False, 'physicalPerformanceMeasured': False}
    destination.mkdir(parents=True)
    for name, value in (('comparison.json', report), ('baseline-entries.json', old), ('candidate-entries.json', new)):
        (destination / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'changed': len(changed), 'added': len(report['added']), 'removed': len(report['removed']),
                      'preserved': report['preservedEntryCount'], 'inputsChanged': False}))


if __name__ == '__main__':
    main()
