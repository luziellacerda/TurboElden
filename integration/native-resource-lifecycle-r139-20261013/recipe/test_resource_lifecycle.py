"""Qualify exact R138/R139 resource paths with controlled JNI and real host TLS/threads."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
from patch_resource_lifecycle import BASELINE_SHA256, patch_bytes, function_span, digest

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ['jni_thread_getenv', 'jni_thread_destruct', 'android_app_create', 'ANativeActivity_onCreate']
SCENARIOS = ['fault-'+str(i) for i in range(8)] + [
    'launches', 'key-retry', 'native-clear', 'java-owned', 'tls-concurrent',
    'attach-failure', 'setspecific-failure', 'query-failure', 'no-context',
    'ensure-concurrent', 'vm-mismatch', 'vm-null',
    'state-null-zero', 'state-null-size', 'state-data-zero', 'state-data-size']


def assemble(text, template, candidate):
    pieces = []
    for name in FUNCTIONS:
        a, b = function_span(text, name)
        pieces.append(text[a:b])
    if candidate:
        from patch_resource_lifecycle import TLS_GLOBALS
        a, b = function_span(text, 'station_jni_key_ensure')
        ensure = 'static void jni_thread_destruct(void *value);\n'+text[a:b]
        declarations = TLS_GLOBALS
        reenter = 'if(!station_jni_key_ensure(vm))InterlockedIncrement(&env_errors);'
        thread = 'if(!station_jni_key_ensure(&process_vm))InterlockedIncrement(&env_errors);'
        mismatch = 'if(station_jni_key_ensure(&other_vm))InterlockedIncrement(&env_errors);'
    else:
        declarations = 'static pthread_key_t thread_key;'
        ensure = ''
        reenter = '(void)vm;'
        thread = '(void)process_vm;'
        mismatch = 'puts("BASELINE_VM_MISMATCH_GUARD_ABSENT");'
    return (template.replace('/* @TLS_GLOBALS@ */', declarations)
            .replace('/* @ENSURE@ */', ensure)
            .replace('/* @PRODUCTION@ */', '\n\n'.join(pieces))
            .replace('/* @REENTER@ */', reenter)
            .replace('/* @ENSURE_THREAD@ */', thread)
            .replace('/* @VM_MISMATCH@ */', mismatch))


def counts(stdout):
    lines = [s for s in stdout.splitlines() if s.startswith('scenario=')]
    if not lines: return {}
    return {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', lines[-1])}


def validate(label, scenario, stdout):
    c = counts(stdout)
    if label == 'candidate':
        if c.get('allocations') != 0 or c.get('fds') != 0:
            raise ValueError('Candidate leaked fixture resources: '+stdout)
        if c.get('wrongDetach') != 0 or c.get('javaDetach') != 0 or c.get('envErrors') != 0:
            raise ValueError('Candidate JNI ownership failed: '+stdout)
        if scenario.startswith('fault-'):
            n = int(scenario[6:])
            if n and (c['finish'] != 1 or c['release'] != 1 or c['worker'] != (1 if n == 6 else 0)):
                raise ValueError('Candidate unsafe startup failure: '+stdout)
            if n == 7 and c['resets'] != 0:
                raise ValueError('TLS failure entered core setup')
            if n == 0 and (c['worker'] != 1 or c['finish'] or c['release']):
                raise ValueError('Normal startup changed')
        elif scenario == 'launches':
            if c['keys'] != 1 or c['worker'] != 100 or c['finish']:
                raise ValueError('Key leaked across repeated launches')
        elif scenario == 'key-retry':
            if c['keyAttempts'] != 2 or c['keys'] != 1 or c['finish'] != 1 or c['worker'] != 1:
                raise ValueError('Failed key allocation was not safely retriable')
        elif scenario == 'vm-null':
            if c['keys'] or c['keyAttempts'] or c['worker'] or c['resets'] or c['finish'] != 1 or c['release'] != 1:
                raise ValueError('Null VM entered worker/core initialization')
        elif scenario.startswith('state-'):
            if c['worker'] != 1 or c['finish'] or c['release']:
                raise ValueError('Valid saved-state shape changed startup')
        elif scenario == 'ensure-concurrent':
            if c['keys'] != 1 or c['keyAttempts'] != 1:
                raise ValueError('Concurrent key creation raced')
        elif scenario == 'native-clear':
            if c['attach'] != 1 or c['detach'] != 1 or c['calls'] != 20:
                raise ValueError('Native TLS cleanup failed after app cleared')
        elif scenario == 'java-owned':
            if c['attach'] or c['detach'] or c['calls'] != 20:
                raise ValueError('Already-attached Java thread was detached')
        elif scenario == 'tls-concurrent':
            if c['attach'] != 16 or c['detach'] != 16 or c['calls'] != 640 or c['keys'] != 1:
                raise ValueError('Concurrent TLS ownership failed')
        elif scenario == 'setspecific-failure':
            if c['attach'] != 1 or c['detach'] != 1:
                raise ValueError('Newly-attached thread was not rolled back')
        elif scenario in ['attach-failure', 'query-failure', 'no-context']:
            if c['attach'] or c['detach']:
                raise ValueError('Failure/context created an attachment')
    else:
        expected = {
            'fault-2': 'NULL_MUTEX_ACCEPTED',
            'fault-3': 'NULL_CONDITION_ACCEPTED',
            'fault-4': 'NULL_SAVED_STATE_DESTINATION',
            'fault-6': 'WAIT_WITHOUT_WORKER',
        }
        if scenario in expected and expected[scenario] not in stdout:
            raise ValueError('Baseline unsafe path not reproduced: '+stdout)
        if scenario == 'fault-5' and c.get('allocations') != 2:
            raise ValueError('Baseline pipe resource leak not reproduced')
        if scenario == 'launches' and c.get('keys') != 100:
            raise ValueError('Baseline repeated key creation not reproduced')
        if scenario == 'native-clear' and c.get('detach') != 0:
            raise ValueError('Baseline absent-app missed detach not reproduced')
        if scenario == 'java-owned' and c.get('javaDetach') != 1:
            raise ValueError('Baseline detach of Java-owned thread not reproduced')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    if not args.work.is_absolute():
        raise ValueError('Work directory must be an explicit absolute path')
    args.work = args.work.resolve()
    args.receipt = args.receipt.resolve()
    args.baseline = args.baseline.resolve()
    args.compiler = args.compiler.resolve()
    repository = ROOT.parents[1].resolve()
    if args.work.exists() or args.work.is_relative_to(repository):
        raise ValueError('Work must be a fresh directory outside the repository')
    if args.receipt.exists() or args.receipt.suffix.lower() != '.json':
        raise ValueError('Receipt must be a new JSON file')
    if args.receipt.is_relative_to(repository) and not args.receipt.is_relative_to(ROOT/'evidence'):
        raise ValueError('Repository receipt must stay in this new overlay evidence directory')
    baseline = args.baseline.read_bytes()
    if digest(baseline) != BASELINE_SHA256:
        raise ValueError('Wrong R138 baseline')
    source = ROOT/'native/source/frontend/drivers/platform_unix.c'
    candidate = source.read_bytes()
    if candidate != patch_bytes(baseline):
        raise ValueError('Candidate differs from exact scoped recipe')
    template_path = ROOT/'tests/resource_tls_harness.c.in'
    template = template_path.read_text(encoding='utf-8')
    args.work.mkdir(parents=True, exist_ok=False)
    results = {}
    for label, data in [('baseline', baseline), ('candidate', candidate)]:
        generated = args.work/(label+'.c')
        generated.write_text(assemble(data.decode('utf-8'), template, label == 'candidate'), encoding='utf-8')
        binary = args.work/(label+'.exe')
        compiled = subprocess.run([str(args.compiler), '-std=c11', '-O2', '-Wall', '-Wextra',
                                   '-Wno-unused-function', '-Wno-unused-variable',
                                   str(generated), '-o', str(binary)], capture_output=True, text=True)
        if compiled.returncode:
            raise ValueError('Host compile failed: '+compiled.stderr)
        runs = {}
        for scenario in SCENARIOS:
            if label == 'baseline' and scenario == 'ensure-concurrent': continue
            run = subprocess.run([str(binary), '1' if label == 'candidate' else '0', scenario],
                                 capture_output=True, text=True, timeout=15)
            if run.returncode:
                raise ValueError(label+'/'+scenario+' failed: '+run.stdout+run.stderr)
            validate(label, scenario, run.stdout)
            runs[scenario] = dict(exitCode=run.returncode, expectedResultConfirmed=True,
                                  stdout=run.stdout.strip(), stderr=run.stderr.strip(), counters=counts(run.stdout))
        results[label] = dict(generatedFixtureSha256=digest(generated.read_bytes()), scenarios=runs)
    report = dict(schemaVersion=1, baselineSourceSha256=digest(baseline),
                  candidateSourceSha256=digest(candidate),
                  harnessSha256=digest(template_path.read_bytes()),
                  compilerSha256=digest(args.compiler.read_bytes()),
                  extractedProductionFunctions=FUNCTIONS+['station_jni_key_ensure (candidate only)'],
                  inverseSourcePreservationVerified=True,
                  realHostThreadsMutexAndTlsDestructors=True,
                  concurrentThreads=32, callsPerThread=20, repeatedLaunches=100,
                  androidActivityWorkerHandshakeMocked=True,
                  noHotLoopOrTimingChange=True, fullNativeCompiled=False, androidExecuted=False,
                  cpuPerformanceMeasured=False, results=results,
                  scope='Exact production functions; JNI/VM/Activity/allocation/FD/worker edges are fixtures. Windows FLS/thread exit and concurrent key creation are real host events. Unsafe baseline null/indefinite-wait edges are reported without actually crashing/hanging the host.')
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(candidateSha256=digest(candidate), allExpectedResultsConfirmed=True,
                         candidateScenarios=len(results['candidate']['scenarios']),
                         receipt=str(args.receipt)), indent=2))


if __name__ == '__main__':
    main()
