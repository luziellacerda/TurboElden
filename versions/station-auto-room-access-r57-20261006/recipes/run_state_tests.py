"""Run the current R55 room/guest policy tests on the JVM, without Android data."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess

p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
p.add_argument('--json-jar', required=True)
p.add_argument('--java', default='java')
p.add_argument('--javac', default='javac')
a = p.parse_args()
snapshot = Path(__file__).resolve().parent.parent
base = snapshot.parent / 'station-current-r55-20261006'
out = Path(a.output).resolve()
if out.exists():
    raise SystemExit('Use a new output directory')
os.umask(0o077)
out.mkdir(parents=True)
classes = out / 'classes'
classes.mkdir()
src = base / 'netplay-src/org/emulationstation/frontend/netplay'
names = ['StationLaunchPolicy', 'StationRoomStartState', 'StationPlayerModel',
         'StationInvitationCode', 'StationSocial', 'StationRoomState']
tests = ['StationCompactLobbyTest', 'StationJoinPlayerTest',
         'StationLaunchPolicyTest', 'StationSocialTest', 'StationShortInvitationTest']
files = []
for n in names:
    overlay = snapshot / 'netplay-src/org/emulationstation/frontend/netplay' / (n + '.java')
    files.append(overlay if overlay.exists() else src / (n + '.java'))
for n in tests:
    overlay = snapshot / 'tests' / (n + '.java')
    files.append(overlay if overlay.exists() else base / 'tests/java' / (n + '.java'))

def run(args, name):
    r = subprocess.run(list(map(str, args)), capture_output=True, text=True,
                       encoding='utf8', errors='replace', timeout=60)
    (out / (name + '.log')).write_text(r.stdout + r.stderr, encoding='utf8')
    print((r.stdout + r.stderr)[-1500:], flush=True)
    r.check_returncode()
    return r.stdout.strip()

run([a.javac, '--release', '8', '-encoding', 'UTF-8', '-cp', a.json_jar,
     '-d', classes, *files], 'javac')
results = {n: run([a.java, '-cp', str(classes) + os.pathsep + a.json_jar,
                  'org.emulationstation.frontend.netplay.' + n], n) for n in tests}
report = {'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'passed': True, 'sourceBase': 'R55 + R57 + automatic room access', 'results': results,
          'jsonJarSHA256': hashlib.sha256(Path(a.json_jar).read_bytes()).hexdigest(),
          'sourceFiles': {str(f.relative_to(base.parent)): hashlib.sha256(f.read_bytes()).hexdigest()
                          for f in files},
          'androidExecuted': False, 'productionModified': False}
(out / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
