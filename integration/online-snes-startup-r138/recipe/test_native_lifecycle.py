"""Host regression tests use extracted production functions and Windows threads."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from patch_native_lifecycle import BASELINE_SHA256, function_span, patch_bytes

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ['station_activity_release', 'android_app_request_quit', 'android_app_free',
             'onDestroy', 'free_saved_state', 'android_app_destroy', 'android_app_entry']
SCENARIOS = ['normal', 'double', 'early', 'race', 'join']
EXPECTED_BASELINE_FAILURES = {'double', 'early', 'race'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def assemble(source, template):
    text = source.decode('utf-8')
    pieces = []
    for name in FUNCTIONS:
        start, end = function_span(text, name)
        pieces.append(text[start:end])
    return template.replace('/* @PRODUCTION_FUNCTIONS@ */', '\n\n'.join(pieces))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    baseline = args.baseline.read_bytes()
    if digest(baseline) != BASELINE_SHA256:
        raise ValueError('Wrong installed baseline source')
    candidate_path = ROOT / 'native/source/frontend/drivers/platform_unix.c'
    candidate = candidate_path.read_bytes()
    if candidate != patch_bytes(baseline):
        raise ValueError('Candidate source differs from exact reviewed patch')
    template_path = ROOT / 'native/tests/lifecycle_harness.c.in'
    template = template_path.read_text(encoding='utf-8')
    compiler = Path(r'C:\Program Files\LLVM\bin\clang.exe')
    args.work.mkdir(parents=True, exist_ok=True)
    results = {}
    for label, source in [('baseline', baseline), ('candidate', candidate)]:
        generated = args.work / (label + '.c')
        binary = args.work / (label + '.exe')
        generated.write_text(assemble(source, template), encoding='utf-8')
        command = [str(compiler), '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                   '-Wno-unused-function', str(generated), '-o', str(binary)]
        compiled = subprocess.run(command, capture_output=True, text=True)
        if compiled.returncode:
            raise ValueError('Host compile failed: ' + compiled.stderr)
        results[label] = {}
        for scenario in SCENARIOS:
            run = subprocess.run([str(binary), scenario], capture_output=True, text=True, timeout=30)
            passed = run.returncode == 0
            expected = label == 'candidate' or scenario not in EXPECTED_BASELINE_FAILURES
            if passed != expected:
                raise ValueError(f'Unexpected {label}/{scenario}: {run.returncode}\n{run.stdout}{run.stderr}')
            results[label][scenario] = {
                'passed': passed, 'expectedResultConfirmed': True,
                'exitCode': run.returncode, 'output': (run.stdout + run.stderr).strip(),
            }
    report = {
        'schemaVersion': 1,
        'baselinePlatformUnixSHA256': digest(baseline),
        'candidatePlatformUnixSHA256': digest(candidate),
        'harnessTemplateSHA256': digest(template_path.read_bytes()),
        'extractedProductionFunctions': FUNCTIONS,
        'realHostMutexesConditionsAndThreads': True,
        'raceIterations': 300,
        'quitAttemptsPerRace': 2128,
        'scenarios': results,
        'allExpectedResultsConfirmed': True,
        'fullNativeCompiled': False,
        'androidExecuted': False,
        'gameplayValidated': False,
        'scope': 'Native lifecycle only; Android/JNI/looper/config operations are fixtures.',
    }
    (ROOT / 'native/lifecycle-tests.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
