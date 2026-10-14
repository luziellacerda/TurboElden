"""Build only the reviewed direct-v3 DEX35 overlay, after new R146 source freeze.

Actual R145 donor smali is authoritative. No historical Activity/Session Java is
compiled or restored. Final decode must recover both entire donor classes by
inversion, and every one of the other 606 classes must remain byte-identical.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import zipfile
from route_scope import *

TOOLS = {'java': '1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406',
         'javac': '9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549',
         'apktool': 'dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423'}
REPO = ROOT.parents[1] if ROOT.parent.name == 'integration' else ROOT.parent / 'publication-app'


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, 'Scoped tool rejected operation: ' + result.stderr[-1800:])
    return result.stdout.strip()


def source_map():
    result = {}
    for folder in ('recipe', 'java', 'tests', 'evidence'):
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and path.suffix in {'.py', '.java', '.smali', '.txt', '.json'}:
                need(not path.is_symlink(), 'Symbolic source refused')
                result[path.relative_to(ROOT).as_posix()] = sha(path)
    required = {'recipe/build_dex.py', 'recipe/route_scope.py', 'recipe/AssembleScopedPartition.java',
                'recipe/VerifyScopedPartition.java', 'recipe/DecodeDolphinPartition.java',
                'evidence/route-scope.json', 'tests/run_tests.py',
                'tests/StationRelayTlsRouteProbe.java'}
    need(required <= result.keys(), 'Closed route source/test set required')
    return result


def verify_commit(commit):
    need(ROOT == REPO / 'integration' / SCOPE_NAME, 'Private preparation cannot build production; stage fresh scope first')
    need(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit) and commit != BASE_SOURCE,
         'Full distinct frozen R146 source commit required')
    pins = source_map()
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, expected in pins.items():
        result = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                                 'show', commit + ':' + prefix + '/' + name], capture_output=True, timeout=90)
        need(result.returncode == 0 and digest(result.stdout) == expected, 'Frozen R146 source differs: ' + name)
    return pins


def require_base(path, plan):
    need(path.stat().st_size == BASE_BYTES and sha(path) == BASE_APK, 'Exact signed final R145 APK required')
    with zipfile.ZipFile(path) as archive:
        names = {name for name in archive.namelist() if name == 'classes.dex' or
                 (name.startswith('classes') and name.endswith('.dex') and '/' not in name)}
        need(names == {'classes.dex', *[f'classes{i}.dex' for i in range(2, 41)]}, 'Exact 40 DEX set required')
        pins = {}
        for name in sorted(names):
            with archive.open(name) as stream:
                import hashlib
                pins[name] = hashlib.file_digest(stream, 'sha256').hexdigest()
        need(pins[PARTITION] == BASE_DEX and {k: v for k, v in pins.items() if k != PARTITION} == plan['preservedDexSha256'],
             'Pinned R145 DEX set differs')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--jdk-bin', type=Path, required=True)
    parser.add_argument('--apktool', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    pins = verify_commit(args.source_commit)
    plan = reviewed_plan()
    host_tests = read(ROOT / 'evidence/host-test-receipt.json')
    need(host_tests.get('schema') == 'station.r146.direct-v3-route.host-tests.v1' and
         host_tests.get('passed') is True and host_tests.get('scopeDeclarationSha256') == sha(ROOT / 'evidence/route-scope.json') and
         host_tests.get('javaTlsSourceSha256') == sha(ROOT / 'java/org/emulationstation/frontend/netplay/StationRelayTls.java') and
         host_tests.get('hostProbeSourceSha256') == sha(ROOT / 'tests/StationRelayTlsRouteProbe.java') and
         host_tests.get('actualWebSocketHttpsHostnameIdentificationPreserved') is True and
         len(host_tests.get('negativeGuards', [])) == 5 and host_tests.get('hostProbe', {}).get('checks', 0) >= 20,
         'Matching meaningful host TLS and inverse test receipt required')
    require_base(args.base, plan)
    output = args.out.resolve()
    need(not output.exists() and BUILD_NAMESPACE.resolve() in output.parents and REPO.resolve() not in output.parents,
         'Fresh isolated output under fixed R146 build namespace required')
    java, javac = args.jdk_bin / 'java.exe', args.jdk_bin / 'javac.exe'
    for name, path in [('java', java), ('javac', javac), ('apktool', args.apktool)]:
        need(sha(path) == TOOLS[name], 'Pinned tool required: ' + name)
    output.mkdir(parents=True)
    utilities = output / 'tools'
    utilities.mkdir()
    helpers = ['DecodeDolphinPartition.java', 'VerifyScopedPartition.java', 'AssembleScopedPartition.java']
    compile_log = run([javac, '-encoding', 'UTF-8', '-cp', args.apktool, '-d', utilities,
                       *[ROOT / 'recipe' / name for name in helpers]])
    classpath = str(utilities) + ';' + str(args.apktool)
    donor, patched, final = output / 'donor-smali', output / 'patched-smali', output / 'final-smali'
    decode_log = run([java, '-cp', classpath, 'DecodeDolphinPartition', args.base, PARTITION, BASE_DEX, donor])
    original = class_maps(donor)
    need(original == plan['baselineClassSha256'], 'Actual donor decode does not match frozen R145 baseline')
    shutil.copytree(donor, patched)
    for kind in sorted(CHANGED):
        path = class_path(patched, kind)
        rewritten = proposed_class(kind, path.read_bytes())
        need(rewritten == class_path(ROOT / 'evidence/proposed-smali', kind).read_bytes(),
             'Prepared route projection differs from frozen proposed class')
        path.write_bytes(rewritten)
    verify_projection(patched, plan)
    scope = output / 'scope.properties'
    allowed = '|'.join(sorted(CHANGED))
    scope.write_text('\n'.join(['schema=station.direct-v3.scoped-types.r146.v1', 'partition=' + PARTITION,
                               'donorSha256=' + BASE_DEX, 'families=' + allowed,
                               'originalAllowed=' + allowed, 'finalAllowed=' + allowed]) + '\n', encoding='utf-8')
    verifier_log = run([java, '-cp', classpath, 'VerifyScopedPartition', args.base, PARTITION, BASE_DEX, patched, scope])
    compiled = output / PARTITION
    assembler_log = run([java, '-cp', classpath, 'AssembleScopedPartition', args.base, PARTITION, BASE_DEX, patched, compiled, scope])
    compiled_sha = sha(compiled)
    need(compiled_sha != BASE_DEX, 'Compiled route must differ from donor')
    # Decoder takes a tiny container holding the compiled DEX only. No APK is
    # assembled, signed or installed by this recipe.
    container = output / 'final-container.apk'
    with zipfile.ZipFile(container, 'x', compression=zipfile.ZIP_STORED) as archive:
        archive.write(compiled, PARTITION)
    final_decode_log = run([java, '-cp', classpath, 'DecodeDolphinPartition', container, PARTITION, compiled_sha, final])
    actual, inverse, inverse_methods = verify_projection(final, plan)
    final_verifier_log = run([java, '-cp', classpath, 'VerifyScopedPartition', args.base, PARTITION, BASE_DEX, final, scope])
    unchanged = {kind: checksum for kind, checksum in original.items() if kind not in CHANGED}
    need(len(unchanged) == 606 and all(actual[kind] == checksum for kind, checksum in unchanged.items()),
         'All 606 unrelated classes must survive assembly')
    record = {'baselineDexSha256': BASE_DEX, 'outputDexSha256': compiled_sha,
              'originalClassCount': 608, 'finalClassCount': 608, 'unchangedClasses': 606,
              'modifiedClasses': sorted(CHANGED), 'modifiedMethods': plan['modifiedMethods'],
              'newMethods': plan['newMethods'], 'newFields': [], 'newClasses': [],
              'removedClasses': [], 'removedMethods': [], 'addedClasses': [],
              'baselineClassSha256': original, 'outputClassSha256': actual,
              'unchangedClassSha256': unchanged, 'inverseClassSha256': inverse,
              'methodBaselineSha256': plan['baselineMethodSha256'], 'methodInverseSha256': inverse_methods,
              'methodOutputSha256': plan['proposedMethodSha256'],
              'inverseWholeClassPassed': True, 'postassemblyInversePassed': True,
              'unrelatedClassesByteIdentical': True, 'unrelatedMethodsPreserved': True,
              'staticInitializersPreserved': True, 'onlyReviewedRouteMethodsChanged': True}
    receipt = {'schema': 'station.r146.direct-v3-relay.dex.v1', 'passed': True,
               'sourceCommit': args.source_commit, 'sourceFiles': pins,
               'baselineSourceCommit': BASE_SOURCE, 'baselineApkSha256': BASE_APK,
               'baselineApkBytes': BASE_BYTES, 'scopeDeclarationSha256': sha(ROOT / 'evidence/route-scope.json'),
               'productionMethodStrategy': 'actual-donor-smali-with-exact-route-method-overlay',
               'payloads': {PARTITION: {'path': str(compiled), 'bytes': compiled.stat().st_size, 'sha256': compiled_sha}},
               'scopes': {PARTITION: record}, 'preservedDexSha256': plan['preservedDexSha256'],
               'inversePassed': True, 'inverseWholeClassPassed': True, 'postAssemblyInversePassed': True,
               'unrelatedMethodsPreserved': True, 'legacyRelayAndApiAuthPreserved': True,
               'ticketProofPathProtocolReadyAckAndExitPreserved': True,
               'nativeEnginesProfilesHleMultitapAndGameplayPreserved': True,
               'newMethods': plan['newMethods'], 'newFields': [], 'newClasses': [],
               'tools': TOOLS, 'utilityCompileLog': compile_log,
               'hostTestReceiptSha256': sha(ROOT / 'evidence/host-test-receipt.json'),
               'donorDecodeLog': decode_log, 'preassemblyVerifierLog': verifier_log,
               'assemblerLog': assembler_log, 'postassemblyDecodeLog': final_decode_log,
               'postassemblyVerifierLog': final_verifier_log,
               'apkAssembledOrSigned': False, 'phoneAccessed': False, 'liveServerCalled': False,
               'physicalGameplayValidated': False}
    destination = output / 'dex-compilation.json'
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    need(source_map() == pins, 'Frozen source changed during DEX build')
    print(json.dumps({'receipt': str(destination), 'dexSha256': compiled_sha,
                      'classes': 608, 'changedClasses': 2, 'preservedClasses': 606,
                      'postassemblyInversePassed': True, 'apkAssembledOrSigned': False}))


if __name__ == '__main__':
    main()
