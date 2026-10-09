"""Run the actual profile parser/presentation against bounded synthetic fixtures.

No Android installation, service mutation or gameplay qualification occurs.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess

ROOT = Path(__file__).resolve().parents[1]
JSON_SHA = '3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796'

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('jdk', 'json-jar', 'work'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if sha(args.json_jar) != JSON_SHA:
        raise ValueError('Use the pinned org.json 20250517 jar')
    args.work.mkdir(parents=True, exist_ok=False)
    test = args.work/'StationProfileClassificationTest.java'
    test.write_bytes((ROOT/'tests/StationProfileClassificationTest.java.in').read_bytes())
    source_dir = ROOT/'java/netplay-src/org/emulationstation/frontend/netplay'
    sources = [source_dir/'StationMultiplayerProfile.java', source_dir/'StationGamePlayerInfo.java', source_dir/'StationOnlinePlatformPolicy.java', ROOT/'java/client/src/java/org/emulationstation/frontend/station/StationPlatforms.java']
    suffix = '.exe' if os.name == 'nt' else ''
    def run(command, label):
        result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
        (args.work/(label+'.log')).write_text(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError(label+' failed; inspect the private log')
        return result.stdout
    run([args.jdk/('javac'+suffix), '-encoding', 'UTF-8', '--release', '8',
         '-proc:none', '-cp', args.json_jar, '-d', args.work, *sources, test], 'javac')
    result = json.loads(run([args.jdk/('java'+suffix), '-cp', str(args.work)+os.pathsep+str(args.json_jar),
        'org.emulationstation.frontend.netplay.StationProfileClassificationTest'], 'profiles'))
    if not result.get('passed') or result.get('checks') != 200:
        raise RuntimeError('The complete expected suite did not pass')
    result.update(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        jsonJarSHA256=JSON_SHA, recipeSHA256=sha(__file__),
        sourceSHA256={p.name:sha(p) for p in sources}, fixtureSHA256=sha(test),
        physicalAndroidGameplayVerified=False)
    text = json.dumps(result, indent=2)+'\n'
    (args.work/'receipt.json').write_text(text)
    (ROOT/'evidence/profile-tests.json').write_text(text)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
