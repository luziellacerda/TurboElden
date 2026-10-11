"""Read-only verification of the exact existing normal source/libraries."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT.parents[1]/'audits/station-online-system-engines-20261011/snes-megadrive'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', type=Path, default=Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003'))
    p.add_argument('--apk', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    pins = json.loads((AUDIT/'source-pins.json').read_text(encoding='utf-8'))
    for rel, expected in pins['sourceFiles'].items():
        path = a.base/'source'/rel
        if not path.is_file() or sha(path) != expected['sha256']:
            raise SystemExit('Source mismatch: '+rel)
    for rel, expected in pins['buildInputs'].items():
        path = a.base/rel
        if not path.is_file() or sha(path) != expected['sha256']:
            raise SystemExit('Build input mismatch: '+rel)
    for item in pins['anchors']:
        lines = (a.base/'source'/item['file']).read_text(encoding='utf-8').splitlines()
        hits = [i+1 for i, line in enumerate(lines) if item['anchor'] in line]
        if hits != item['lines']: raise SystemExit('Source anchor changed: '+item['file'])
    for rel in ('Snes9x/CMakeLists.txt', 'Snes9x/src/CMakeLists.txt'):
        text = (a.base/'source'/rel).read_text(encoding='utf-8')
        if any(n in text for n in ('NETPLAY_SUPPORT','netplay.cpp','server.cpp')):
            raise SystemExit('Historical SNES networking build changed: '+rel)
    entries = {}
    if a.apk:
        with zipfile.ZipFile(a.apk) as z:
            for name, expected in pins['offlineLibraries'].items():
                entry = 'lib/arm64-v8a/'+name
                observed = hashlib.sha256(z.read(entry)).hexdigest()
                if observed != expected['sha256']: raise SystemExit('Offline library mismatch: '+entry)
                entries[entry] = {'sha256': observed, 'bytes': z.getinfo(entry).file_size}
            manifest = json.loads(z.read('assets/station-online/engines.json'))
            array = manifest if isinstance(manifest, list) else manifest.get('engines', [])
            wanted = pins['currentOnlineEngineIds']
            found = [x for x in array if x.get('id', x.get('engineId')) in wanted]
            if len(found) != 2: raise SystemExit('Current SNES/MD online manifest identity changed')
            entries['onlineEngineIds'] = wanted
    receipt = {'schema': 1, 'generatedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'readOnly': True, 'productiveChanges': False,
        'sourcePinsSha256': sha(AUDIT/'source-pins.json'),
        'sourceFilesChecked': len(pins['sourceFiles']), 'buildInputsChecked': len(pins['buildInputs']),
        'anchorsChecked': len(pins['anchors']), 'locations': pins['anchors'], 'apkEntriesChecked': entries,
        'limits': ['Source guards/read-only hashes, not emulator compilation or gameplay',
                   'No server registration/current response checked',
                   'Snapshot defects belong to normal EX+ source, not current bsnes/clown online route']}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: receipt[key] for key in
        ('readOnly','sourceFilesChecked','buildInputsChecked','anchorsChecked','apkEntriesChecked')}, indent=2))

if __name__ == '__main__': main()
