"""Compile actual R79/R81 profile classes; require the reproduced baseline bug and corrected suite."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
WORK = Path(r'E:\ESTUDO APK\work\station-online-readiness-r81-20261008\profile-classification-tests')
SOURCE = HERE.parent / 'java/netplay-src/org/emulationstation/frontend/netplay'
BASELINE = HERE / 'baseline-r79'
JDK = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
JSON = Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
PRODUCTION = ('StationMultiplayerProfile.java', 'StationGamePlayerInfo.java')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(label, source, work):
    src = work / label / 'src'
    classes = work / label / 'classes'
    src.mkdir(parents=True, exist_ok=True)
    classes.mkdir(parents=True, exist_ok=True)
    for name in PRODUCTION:
        shutil.copyfile(source / name, src / name)
    template = HERE / 'StationProfileClassificationTest.java.in'
    shutil.copyfile(template, src / template.name[:-3])
    compiled = subprocess.run([str(JDK / 'javac.exe'), '-J-Dfile.encoding=UTF-8', '--release', '17', '-encoding', 'UTF-8', '-cp', str(JSON), '-d', str(classes), *map(str, src.glob('*.java'))], capture_output=True, text=True, encoding='utf8')
    (work / label / 'compile.log').write_text(compiled.stdout + compiled.stderr, encoding='utf8')
    if compiled.returncode:
        raise RuntimeError(compiled.stdout + compiled.stderr)
    tested = subprocess.run([str(JDK / 'java.exe'), '-Dfile.encoding=UTF-8', '-ea', '-cp', str(classes) + ';' + str(JSON), 'org.emulationstation.frontend.netplay.StationProfileClassificationTest'], capture_output=True, text=True, encoding='utf8', timeout=30)
    (work / label / 'test.log').write_text(tested.stdout + tested.stderr, encoding='utf8')
    return tested

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, default=WORK)
    args = parser.parse_args()
    if args.work.resolve().drive.upper() != 'E:':
        raise ValueError('Build and temporary output must remain on E:')
    baseline = run('baseline-r79', BASELINE, args.work)
    reproduced = baseline.returncode != 0 and 'REGRESSION: valid solo classification aborts multiplayer choices' in baseline.stderr
    if not reproduced:
        raise AssertionError('Expected baseline bug was not reproduced: ' + baseline.stdout + baseline.stderr)
    corrected = run('corrected-r81', SOURCE, args.work)
    if corrected.returncode:
        raise RuntimeError(corrected.stdout + corrected.stderr)
    metrics = json.loads(corrected.stdout.strip().splitlines()[-1])
    receipt = {'utc': datetime.now(timezone.utc).isoformat(), 'passed': True, 'baselineBugReproduced': reproduced, 'metrics': metrics, 'baselineSources': {name: digest(BASELINE / name) for name in PRODUCTION}, 'correctedSources': {name: digest(SOURCE / name) for name in PRODUCTION}, 'testSHA256': digest(HERE / 'StationProfileClassificationTest.java.in'), 'recipeSHA256': digest(__file__), 'jsonJarSHA256': digest(JSON), 'limits': ['Synthetic contract fixtures do not qualify any real game', 'No Android, gameplay, network, server or phone touched']}
    (args.work / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'baselineBugReproduced': reproduced, **metrics}))
    print('receipt=' + str(args.work / 'receipt.json'))

if __name__ == '__main__':
    main()
