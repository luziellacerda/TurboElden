"""Windows wrapper around the unchanged recovery builder and explicit R71 stall fix."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, subprocess, sys, zipfile

SNAPSHOT = Path(__file__).resolve().parent.parent
NATIVE = SNAPSHOT / 'native-recovery'
UPSTREAM = '69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
ARCHIVE = 'cecf1e3f5446724f748124d097bb9c5169c6f599404d33a8447d88fd197d17fe'
BUILDER = '7d594d76e21cabda3375eb0f9f1295e903765d1a3d2ee798afb4e95d931e964a'
ORIGINAL_MANIFEST = '6a4c528ab4e270fffb29a8ff78f1735bc5c9b5d9ab010e1f21c08700161b3f55'
OLD = 'netplay->stall!=NETPLAY_STALL_NONE)station_recovery_mark_stalled();'
NEW = 'netplay->stall==NETPLAY_STALL_RUNNING_FAST)station_recovery_mark_stalled();'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_inputs():
    origin = json.loads((NATIVE / 'ORIGIN.json').read_text('utf8'))
    manifest = json.loads((NATIVE / 'native/RECOVERY-SOURCE-MANIFEST.json').read_text('utf8'))
    assert origin['sourceManifestSHA256'] == ORIGINAL_MANIFEST
    assert sha(NATIVE / 'recipes/build_native_runtime.py') == BUILDER
    assert origin['sourceCommit'] == '4d30401a80658dd56666ef10f48d9556b3fdd9e9'
    modified = {'recipes/patch_native.py', 'engine-patches/retroarch-station-recovery.patch'}
    assert set(origin['modifiedFiles']) == modified
    for name, expected in manifest['files'].items():
        assert sha(NATIVE / name) == expected, name
    for name, expected in origin['originalFiles'].items():
        data = (NATIVE / name).read_bytes()
        if name in modified:
            assert data.count(NEW.encode()) == 1
            data = data.replace(NEW.encode(), OLD.encode())
        assert hashlib.sha256(data).hexdigest() == expected, name
    return origin, manifest

def run_tests(work, source_zip, origin):
    tests = work / 'host-tests'
    tests.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(source_zip) as archive:
        data = archive.read('RetroArch-' + UPSTREAM + '/network/netplay/netplay_private.h')
    enum = re.search(r'enum rarch_netplay_stall_reason\s*\{.*?\};', data.decode(), re.S).group()
    (tests / 'upstream_stall_enum.h').write_text(enum + '\n', encoding='utf8')
    # Only the host harness maps POSIX mutexes to Windows' real exclusive SRW lock.
    # The production header and all 13 original assertions are unchanged.
    (tests / 'pthread.h').write_text('''#include <windows.h>
typedef SRWLOCK pthread_mutex_t;
#define PTHREAD_MUTEX_INITIALIZER SRWLOCK_INIT
static int pthread_mutex_lock(pthread_mutex_t *m) { AcquireSRWLockExclusive(m); return 0; }
static int pthread_mutex_unlock(pthread_mutex_t *m) { ReleaseSRWLockExclusive(m); return 0; }
''', encoding='utf8')
    compiler = Path(r'C:\Program Files\LLVM\bin\clang.exe')
    assert compiler.is_file()
    common = [str(compiler), '-std=c11', '-Wall', '-Wextra', '-Wno-unused-function',
              '-I', str(tests), '-I', str(NATIVE / 'native')]
    outputs = {}
    def invoke(command, label, expected=0):
        result = subprocess.run(command, capture_output=True, text=True)
        (tests / (label + '.log')).write_text(result.stdout + result.stderr, encoding='utf8')
        assert result.returncode == expected, label + ': ' + result.stderr[-1000:]
        return result.stdout.strip()
    binary = tests / 'control.exe'
    invoke(common + [str(NATIVE / 'tests/native_recovery_test.c'), '-o', str(binary)], 'control-compile')
    outputs['originalStateChecks'] = invoke([str(binary)], 'control-test')
    assert outputs['originalStateChecks'].startswith('PASS 13 ')
    patch = (NATIVE / 'engine-patches/retroarch-station-recovery.patch').read_text('utf8')
    hook = re.search(r'if\(station_recovery_active\(\) && netplay->stall[^\n]+', patch).group()
    assert NEW in hook
    for label, clause, expected in [('baseline', hook.replace(NEW, OLD), 1), ('candidate', hook, 0)]:
        generated = ('static void candidate_sample_stall(enum rarch_netplay_stall_reason reason) {\n'
                     'struct { enum rarch_netplay_stall_reason stall; } value = {reason};\n'
                     'void *unused = 0; (void)unused;\n'
                     'struct { enum rarch_netplay_stall_reason stall; } *netplay = (void*)&value;\n' + clause + '\n}\n')
        (tests / 'candidate_stall_hook.h').write_text(generated, encoding='utf8')
        binary = tests / (label + '.exe')
        invoke(common + [str(NATIVE / 'tests/recovery_stall_policy.c'), '-o', str(binary)], label + '-compile')
        outputs[label] = invoke([str(binary)], label + '-test', expected)
    assert 'enum=3 enabled=1' in outputs['baseline']
    assert outputs['candidate'].startswith('PASS 112 ')
    return {'passed': True, 'originalStateChecks': 13, 'stallPolicyChecks': 112,
            'baselineFails': True, 'baselineFailure': outputs['baseline'],
            'outputs': outputs, 'upstreamEnumFileSHA256': hashlib.sha256(data).hexdigest(),
            'testSourceSHA256': sha(NATIVE / 'tests/recovery_stall_policy.c'),
            'originalTestSourceSHA256': origin['originalFiles']['tests/native_recovery_test.c'],
            'mutexBackend': 'Windows SRWLOCK compatibility header, host test only',
            'compiler': str(compiler), 'compilerSHA256': sha(compiler),
            'androidExecuted': False, 'twoDeviceGameplayVerified': False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-zip', required=True)
    parser.add_argument('--ndk', default=r'E:\TurboEdenEngine\android-ndk-r28c')
    parser.add_argument('--output', required=True)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--tests-only', action='store_true')
    args = parser.parse_args()
    work = Path(args.output).resolve()
    assert work.drive.upper() == 'E:' and ' ' not in str(work) and not work.exists()
    assert sha(args.source_zip) == ARCHIVE
    origin, manifest = verify_inputs()
    before = {str(p.relative_to(NATIVE)): sha(p) for p in NATIVE.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_COUNT='2',
               GIT_CONFIG_KEY_0='core.autocrlf', GIT_CONFIG_VALUE_0='false',
               GIT_CONFIG_KEY_1='core.eol', GIT_CONFIG_VALUE_1='lf')
    if args.tests_only:
        work.mkdir(parents=True)
    else:
        command = [sys.executable, str(NATIVE / 'recipes/build_native_runtime.py'),
                   '--source-zip', str(Path(args.source_zip).resolve()), '--ndk', args.ndk,
                   '--output', str(work), '--jobs', str(args.jobs)]
        subprocess.run(command, env=env, check=True)
        result = json.loads((work / 'result.json').read_text())
        assert result['recoveryInputs'] == manifest['files'] and result['buildRecipeSHA256'] == BUILDER
    tests = run_tests(work, args.source_zip, origin)
    assert before == {str(p.relative_to(NATIVE)): sha(p) for p in NATIVE.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    receipt = {'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'work': str(work), 'nativeOverlayManifestSHA256': sha(NATIVE / 'native/RECOVERY-SOURCE-MANIFEST.json'),
               'originalManifestSHA256': ORIGINAL_MANIFEST, 'originSHA256': sha(NATIVE / 'ORIGIN.json'),
               'wrapperSHA256': sha(__file__), 'originalBuilderSHA256': BUILDER,
               'gitConfiguration': {'core.autocrlf': False, 'core.eol': 'lf', 'scope': 'child process only'},
               'sourceArchiveSHA256': ARCHIVE, 'nativeInputs': before, 'tests': tests,
               'runtimeSHA256': None if args.tests_only else sha(work / 'libstation_retroarch.so')}
    (work / 'r71-build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    evidence = SNAPSHOT / 'evidence'
    evidence.mkdir(exist_ok=True)
    (evidence / ('native-tests-prebuild.json' if args.tests_only else 'native-build-r71.json')).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print('PASS 13 native control assertions and 112 stall policy checks; original predicate fails enum=3')

if __name__ == '__main__':
    main()
