"""Exact R146 DEX10 donor, one ownership class/four methods, no Java rollback.

Production runs only after distinct R147 source freeze. Canonical actual output
must recover the complete original class and preserve all 4,990 other classes.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
import common as c

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
import audit_ownership as a
import prepare_ownership as p
import verify_projection as v

BASE = '04930201ad2f1c016f3385b3f08248ed4fa112d482a98761d00494b7a937468a'
BASE_BYTES = 2715073551
BASE_SOURCE = 'bfea454d04ef297e9dfd1b397e0bf25df3937e93'
PARTITION = 'classes10.dex'
BASE_DEX = '09ed47c40c4a6f5194bcb9ace23f85392b99c19c84cd654e61716de37b32e01c'
TYPE = 'Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;'
CLASS_SHA = '7dcbc2c67298d18e7ffe5b4839e73ca6967a0318e4628269598bef9a45ec2315'
RAW_SHA = '00869b191ffc794d32aaad2f787be11c80188395953ebd7f8a5c95bec69dd1de'
CANONICAL_SHA = 'ed45e5272b1d554d26e702b6d168b1e49ce1f14144b25451858e8cc78c542690'
SCOPE_NAME = 'dolphin-boot-cleanup-r147-20261014-final'
BUILD_NAMESPACE = Path('E:/StationDolphinBootCleanupR147Final-20261014')
TOOLS = {'java': '1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406',
         'javac': '9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549',
         'apktool': 'dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423'}
METHODS = ['.method public final consumeBootSessionData()J',
           '.method public final releaseNativeResources()V',
           '.method public final isLaunching()Z',
           '.method public final onBootGame(Ljava/lang/String;J)V']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def long_path(path):
    value = str(Path(path).resolve())
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        value = '\\\\?\\' + value
    return Path(value)


def sha(path):
    with long_path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(long_path(path).read_text(encoding='utf-8-sig'))


def class_path(directory, kind):
    return long_path(directory) / (kind[1:-1] + '.smali')


def class_maps(directory):
    root = long_path(directory)
    result = {}
    for path in sorted(root.rglob('*.smali')):
        need(not path.is_symlink(), 'Symbolic smali refused')
        kind = 'L' + path.relative_to(root).as_posix()[:-6] + ';'
        need(kind not in result, 'Duplicate donor class')
        result[kind] = sha(path)
    return result


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, 'Scoped tool rejected operation: ' + result.stderr[-1800:])
    return result.stdout.strip()


def reviewed_plan():
    need(sys.flags.optimize == 0, 'Ownership assertion guards must remain enabled')
    plan = read(ROOT / 'evidence/dex10-scope.json')
    need(plan['schema'] == 'station.r147.dolphin.boot-ownership.dex.scope.v1' and
         plan['baselineApkSha256'] == BASE and plan['baselineApkBytes'] == BASE_BYTES and
         plan['baselineSourceCommit'] == BASE_SOURCE and plan['baselineDexSha256'] == BASE_DEX and
         plan['partition'] == PARTITION and plan['classCount'] == 4991 and plan['unchangedClassCount'] == 4990 and
         plan['modifiedClasses'] == [TYPE] and plan['modifiedMethods'] == {TYPE: METHODS} and
         plan['newMethods'] == plan['newFields'] == plan['newClasses'] == [] and
         plan['productionMethodStrategy'] == 'donor-smali-only', 'Closed ownership DEX10 scope required')
    need(len(plan['baselineClassSha256']) == 4991 and plan['baselineClassSha256'][TYPE] == CLASS_SHA and
         plan['proposedRawClassSha256'] == {TYPE: RAW_SHA} and
         plan['proposedCanonicalClassSha256'] == {TYPE: CANONICAL_SHA} and len(plan['preservedDexSha256']) == 39,
         'Exact donor/proposed/full class and DEX sets required')
    source_ready = read(ROOT / 'SOURCE-READY.json')
    for name, expected in source_ready['filesSha256'].items():
        need(sha(ROOT / name) == expected, 'Accepted immutable ownership audit source changed: ' + name)
    for name, expected in plan['sourceProofSha256'].items():
        need(sha(ROOT / 'evidence' / name) == expected, 'Accepted ownership proof changed: ' + name)
    scope = read(ROOT / 'evidence/ownership-scope.json')
    patched = read(ROOT / 'evidence/patched-ownership-proof.json')
    canonical = read(ROOT / 'evidence/canonical-source-proof.json')
    fields = read(ROOT / 'evidence/field-scan-proof.json')
    need(scope['wholeClassSourceInversePassed'] is True and scope['modifiedMethods'] == METHODS and
         patched['passed'] is True and all(patched['results'].values()) and len(patched['results']) == 11 and
         canonical['passed'] is True and canonical['baselineParseEmitByteIdentical'] is True and
         all(row['instructionsAndTryRangesEquivalent'] for row in canonical['methods'].values()) and
         fields['closedFieldVolatileVerified'] is True and fields['fieldMapIdentical'] is True and
         fields['closedFieldSingleBytecodeWriter'] == 'NetplaySession.closeBlocking',
         'Race, semantic, field-visibility and class-lock proofs required')
    baseline = (ROOT / 'evidence/baseline-NetplaySession.smali.txt').read_bytes()
    raw = (ROOT / 'smali/org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali').read_bytes()
    expected = (ROOT / 'evidence/canonical-proposed-NetplaySession.smali.txt').read_bytes()
    need(a.sha(baseline) == CLASS_SHA and a.sha(raw) == RAW_SHA and a.sha(expected) == CANONICAL_SHA,
         'Pinned whole ownership class projections required')
    need(p.methods(baseline.decode()) == plan['baselineMethodSha256'][TYPE] and
         p.methods(raw.decode()) == plan['rawMethodSha256'][TYPE] and
         p.methods(expected.decode()) == plan['canonicalMethodSha256'][TYPE] and
         len(plan['baselineMethodSha256'][TYPE]) == len(plan['canonicalMethodSha256'][TYPE]) == 63,
         'All 63 ownership class methods must remain pinned')
    v.verify(expected)
    return plan


def rewrite_donor(raw):
    need(a.sha(raw) == CLASS_SHA, 'Actual pinned donor class required')
    text = raw.decode('utf-8')
    before = {signature: a.method(text, signature) for signature in METHODS}
    changed = {METHODS[0]: p.wrapped(before[METHODS[0]], 'long'),
               METHODS[1]: p.release_changed(before[METHODS[1]]),
               METHODS[2]: p.wrapped(before[METHODS[2]], 'boolean'),
               METHODS[3]: p.boot_changed(before[METHODS[3]])}
    for signature in METHODS:
        need(text.count(before[signature]) == 1, 'Unique actual ownership method required')
        text = text.replace(before[signature], changed[signature], 1)
    result = text.encode('utf-8')
    need(a.sha(result) == RAW_SHA and result == (ROOT / 'smali/org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali').read_bytes(),
         'Actual donor overlay differs from accepted raw projection')
    inverse = text
    for signature in reversed(METHODS):
        need(inverse.count(changed[signature]) == 1, 'Unique inverse ownership method required')
        inverse = inverse.replace(changed[signature], before[signature], 1)
    need(inverse.encode('utf-8') == raw, 'Raw whole class inverse must recover donor')
    return result


def require_base(path, plan):
    need(path.stat().st_size == BASE_BYTES and sha(path) == BASE, 'Exact signed final R146 donor APK required')
    with zipfile.ZipFile(path) as archive:
        names = {name for name in archive.namelist() if name == 'classes.dex' or
                 (name.startswith('classes') and name.endswith('.dex') and '/' not in name)}
        need(names == {'classes.dex', *[f'classes{i}.dex' for i in range(2, 41)]}, 'Exact 40 donor DEX set required')
        actual = {}
        for name in sorted(names):
            with archive.open(name) as stream:
                actual[name] = hashlib.file_digest(stream, 'sha256').hexdigest()
        need(actual[PARTITION] == BASE_DEX and {name: checksum for name, checksum in actual.items() if name != PARTITION} == plan['preservedDexSha256'],
             'All donor DEX identities must match accepted R146')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--jdk-bin', type=Path, required=True)
    parser.add_argument('--apktool', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    need(ROOT.parent.name == 'integration' and ROOT.name == SCOPE_NAME, 'Private preparation cannot build production')
    pins = c.verify_commit(args.source_commit)
    plan = reviewed_plan()
    require_base(args.base, plan)
    output = args.out.resolve()
    need(not output.exists() and BUILD_NAMESPACE.resolve() in output.parents and '.git' not in output.parts,
         'Fresh isolated output under fixed R147 namespace required')
    java, javac = args.jdk_bin / 'java.exe', args.jdk_bin / 'javac.exe'
    for name, path in [('java', java), ('javac', javac), ('apktool', args.apktool)]:
        need(sha(path) == TOOLS[name], 'Pinned tool required: ' + name)
    output.mkdir(parents=True)
    utilities = output / 'tools'; utilities.mkdir()
    tools = ['DecodeDolphinPartition.java', 'VerifyScopedPartition.java', 'AssembleScopedPartition.java']
    compile_log = run([javac, '-encoding', 'UTF-8', '-cp', args.apktool, '-d', utilities,
                       *[ROOT / 'recipe' / name for name in tools]])
    classpath = str(utilities) + ';' + str(args.apktool)
    donor, patched, final = output / 'donor-smali', output / 'patched-smali', output / 'final-smali'
    decode_log = run([java, '-cp', classpath, 'DecodeDolphinPartition', args.base, PARTITION, BASE_DEX, donor])
    baseline_map = class_maps(donor)
    need(baseline_map == plan['baselineClassSha256'], 'Actual decoded R146 DEX10 differs from full frozen baseline')
    shutil.copytree(long_path(donor), long_path(patched))
    path = class_path(patched, TYPE)
    path.write_bytes(rewrite_donor(path.read_bytes()))
    pre_map = class_maps(patched)
    pre_expected = dict(baseline_map); pre_expected[TYPE] = RAW_SHA
    need(pre_map == pre_expected, 'Preassembly overlay changed outside exact class')
    properties = output / 'scope.properties'
    properties.write_text('\n'.join(['schema=station.dolphin-boot.scoped-types.r147.v1', 'partition=' + PARTITION,
                                    'donorSha256=' + BASE_DEX, 'families=' + TYPE,
                                    'originalAllowed=' + TYPE, 'finalAllowed=' + TYPE]) + '\n', encoding='utf-8')
    before_log = run([java, '-cp', classpath, 'VerifyScopedPartition', args.base, PARTITION, BASE_DEX, patched, properties])
    compiled = output / PARTITION
    assemble_log = run([java, '-cp', classpath, 'AssembleScopedPartition', args.base, PARTITION, BASE_DEX, patched, compiled, properties])
    compiled_sha = sha(compiled)
    need(compiled_sha != BASE_DEX, 'Compiled ownership DEX must differ from donor')
    container = output / 'final-container.apk'
    with zipfile.ZipFile(container, 'x', compression=zipfile.ZIP_STORED) as archive:
        archive.write(compiled, PARTITION)
    final_decode_log = run([java, '-cp', classpath, 'DecodeDolphinPartition', container, PARTITION, compiled_sha, final])
    final_map = class_maps(final)
    expected = dict(baseline_map); expected[TYPE] = CANONICAL_SHA
    need(final_map == expected, 'Actual compiled projection must preserve all 4990 other classes')
    inverse = v.verify(class_path(final, TYPE).read_bytes())
    final_log = run([java, '-cp', classpath, 'VerifyScopedPartition', args.base, PARTITION, BASE_DEX, final, properties])
    unchanged = {kind: checksum for kind, checksum in baseline_map.items() if kind != TYPE}
    need(len(unchanged) == 4990 and all(final_map[kind] == checksum for kind, checksum in unchanged.items()),
         'All 4990 unrelated classes must survive assembly')
    scope = {'baselineDexSha256': BASE_DEX, 'outputDexSha256': compiled_sha,
             'originalClassCount': 4991, 'finalClassCount': 4991, 'unchangedClasses': 4990,
             'modifiedClasses': [TYPE], 'modifiedMethods': {TYPE: METHODS},
             'baselineClassSha256': baseline_map, 'outputClassSha256': final_map,
             'unchangedClassSha256': unchanged, 'inverseClassSha256': {TYPE: CLASS_SHA},
             'methodBaselineSha256': plan['baselineMethodSha256'],
             'methodInverseSha256': plan['baselineMethodSha256'],
             'methodOutputSha256': plan['canonicalMethodSha256'],
             'originalModifiedClassMethodCount': 63, 'finalModifiedClassMethodCount': 63,
             'unchangedModifiedClassMethods': 59, 'unchangedModifiedClassFields': 40,
             'inverseWholeClassPassed': True, 'postassemblyInversePassed': True,
             'unrelatedClassesByteIdentical': True, 'unrelatedMethodsPreserved': True,
             'staticInitializersPreserved': True, 'onlyReviewedOwnershipMethodsChanged': True,
             'canonicalInstructionBranchAndTryProofPassed': True,
             'newMethods': [], 'newFields': [], 'newClasses': [], 'removedClasses': [], 'removedMethods': [], 'addedClasses': []}
    receipt = {'schema': 'station.r147.dolphin.boot-ownership.dex.v1', 'passed': True,
               'sourceCommit': args.source_commit, 'sourceFiles': pins,
               'baselineApkSha256': BASE, 'baselineApkBytes': BASE_BYTES, 'baselineSourceCommit': BASE_SOURCE,
               'scopeDeclarationSha256': sha(ROOT / 'evidence/dex10-scope.json'),
               'productionMethodStrategy': 'donor-smali-only',
               'payloads': {PARTITION: {'path': str(compiled), 'bytes': compiled.stat().st_size, 'sha256': compiled_sha}},
               'scopes': {PARTITION: scope}, 'preservedDexSha256': plan['preservedDexSha256'],
               'inversePassed': True, 'inverseWholeClassPassed': True, 'postAssemblyInversePassed': True,
               'unrelatedMethodsPreserved': True, 'newMethods': [], 'newFields': [], 'newClasses': [],
               'r146RouteVisualControlsInputsProfilesAndReadinessPreserved': True,
               'ownershipClassMonitorSitesAdded': 3, 'newPerFrameJniCalls': 0, 'newSchedulersOrThreads': 0,
               'nativeOrCallbackInsideOwnershipMonitor': False, 'sourceProofSha256': plan['sourceProofSha256'],
               'tools': TOOLS, 'utilityCompileLog': compile_log, 'donorDecodeLog': decode_log,
               'preassemblyVerifierLog': before_log, 'assemblerLog': assemble_log,
               'postassemblyDecodeLog': final_decode_log, 'postassemblyVerifierLog': final_log,
               'apkAssembledOrSigned': False, 'nativeCoreCompiledByThisRecipe': False,
               'phoneAccessed': False, 'serverAccessed': False, 'physicalGameplayValidated': False}
    destination = output / 'dex-compilation.json'
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write('\n')
    need(c.source_map() == pins, 'Frozen global source changed during DEX build')
    print(json.dumps({'receipt': str(destination), 'classes': 4991, 'unchangedClasses': 4990,
                      'changedClass': 1, 'changedMethods': 4, 'dexSha256': compiled_sha,
                      'postassemblyWholeClassInversePassed': True, 'apkAssembledOrSigned': False}))


if __name__ == '__main__':
    main()
