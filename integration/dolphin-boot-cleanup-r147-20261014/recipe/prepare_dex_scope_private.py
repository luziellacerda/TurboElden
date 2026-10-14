"""Private read-only donor preparation; no DEX/APK assembly or source edits."""
from pathlib import Path
import hashlib
import json
import os
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
import audit_ownership as a
import prepare_ownership as p
import verify_projection as v

BASE = '04930201ad2f1c016f3385b3f08248ed4fa112d482a98761d00494b7a937468a'
BYTES = 2715073551
SOURCE = 'bfea454d04ef297e9dfd1b397e0bf25df3937e93'
APK = Path('F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R146-relay-direto-online-20261014.apk')
DONOR = ROOT.parent / 'r147-dex10-baseline-private'


def sha(path):
    with long_path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def long_path(path):
    value = str(Path(path).resolve())
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        value = '\\\\?\\' + value
    return Path(value)


def main():
    assert APK.stat().st_size == BYTES and sha(APK) == BASE
    maps = {}
    long_donor = long_path(DONOR)
    for path in sorted(long_donor.rglob('*.smali')):
        assert not path.is_symlink()
        kind = 'L' + path.relative_to(long_donor).as_posix()[:-6] + ';'
        assert kind not in maps
        maps[kind] = sha(path)
    assert len(maps) == 4991 and maps[p.TYPE] == a.DONOR_SHA
    baseline = (ROOT / 'evidence/baseline-NetplaySession.smali.txt').read_bytes()
    actual = (DONOR / 'org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali').read_bytes()
    assert baseline == actual
    raw_path = ROOT / 'smali/org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali'
    raw = raw_path.read_bytes()
    canonical = (ROOT / 'evidence/canonical-proposed-NetplaySession.smali.txt').read_bytes()
    projection = v.verify(canonical)
    fields = re.findall(rb'^\.field[^\r\n]+', baseline, re.M)
    assert fields == re.findall(rb'^\.field[^\r\n]+', raw, re.M) and len(fields) == 40
    preserved = {}
    with zipfile.ZipFile(APK) as archive:
        names = {name for name in archive.namelist() if name == 'classes.dex' or
                 (name.startswith('classes') and name.endswith('.dex') and '/' not in name)}
        assert names == {'classes.dex', *[f'classes{i}.dex' for i in range(2, 41)]}
        assert a.sha(archive.read('classes10.dex')) == a.DEX_SHA
        for name in sorted(names - {'classes10.dex'}):
            with archive.open(name) as stream:
                preserved[name] = hashlib.file_digest(stream, 'sha256').hexdigest()
    source_checks = {}
    for name in ['ownership-scope.json', 'baseline-race-proof.json', 'patched-ownership-proof.json',
                 'field-scan-proof.json', 'canonical-source-proof.json']:
        source_checks[name] = sha(ROOT / 'evidence' / name)
    sites = sum(a.method(raw.decode(), sig).count('    monitor-enter ') for sig in p.SIGNATURES)
    assert sites == 3
    callbacks = []
    pattern = re.compile(r'NetplaySession;->(isLaunching|consumeBootSessionData)\(')
    for path in sorted(long_donor.rglob('*.smali')):
        for index, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            match = pattern.search(line)
            if match:
                callbacks.append({'classPath': path.relative_to(long_donor).as_posix(), 'line': index, 'method': match[1]})
    assert len(callbacks) == 3 and all(row['classPath'].endswith('EmulationFragment$$ExternalSyntheticLambda0.smali') for row in callbacks)
    value = {'schema': 'station.r147.dolphin.boot-ownership.dex.scope.v1',
             'baselineApkSha256': BASE, 'baselineApkBytes': BYTES, 'baselineSourceCommit': SOURCE,
             'partition': 'classes10.dex', 'baselineDexSha256': a.DEX_SHA,
             'classCount': 4991, 'unchangedClassCount': 4990, 'modifiedClasses': [p.TYPE],
             'modifiedMethods': {p.TYPE: p.SIGNATURES}, 'newMethods': [], 'newFields': [], 'newClasses': [],
             'baselineClassSha256': maps, 'proposedRawClassSha256': {p.TYPE: a.sha(raw)},
             'proposedCanonicalClassSha256': {p.TYPE: a.sha(canonical)},
             'baselineMethodSha256': {p.TYPE: p.methods(baseline.decode())},
             'rawMethodSha256': {p.TYPE: p.methods(raw.decode())},
             'canonicalMethodSha256': {p.TYPE: p.methods(canonical.decode())},
             'baselineFieldDeclarations': [field.decode() for field in fields],
             'originalMethodCount': 63, 'finalMethodCount': 63, 'unchangedMethods': 59,
             'fieldCount': 40, 'preservedDexSha256': preserved, 'sourceProofSha256': source_checks,
             'productionMethodStrategy': 'donor-smali-only', 'sourceWholeClassInversePassed': True,
             'rawToCanonicalInstructionBranchAndTryProofPassed': True,
             'postassemblyActualDecodeAndInverseRequired': True,
             'ownershipClassMonitorSitesAdded': sites, 'ownershipMonitorContainsNativeOrCallback': False,
             'newPerFrameJniCalls': 0, 'newSchedulersOrThreads': 0,
             'existingBootGetterConsumeCallsites': callbacks,
             'performanceLimit': 'Three short boot-lifecycle monitor sites; no per-frame call, JNI, thread, timer or throughput measurement added.',
             'sourcePrepared': True, 'dexCompiled': False, 'apkCompiled': False,
             'nativeCoreCompiled': False, 'phoneAccessed': False, 'serverAccessed': False}
    destination = ROOT / 'evidence/dex10-scope.json'
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'scope': str(destination), 'scopeSha256': sha(destination), 'classes': 4991,
                      'preservedClasses': 4990, 'preservedDex': 39, 'newMonitorSites': 3, 'dexCompiled': False}))


if __name__ == '__main__':
    main()
