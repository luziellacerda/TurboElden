"""Compile the real R117 lobby merge and bounded query recovery against R116 dependencies."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess

ROOT = Path(__file__).resolve().parents[1]
JSON_SHA = '3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('work', 'dependency-build', 'jdk', 'json-jar', 'android-jar'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if sha(args.json_jar) != JSON_SHA:
        raise ValueError('Use the pinned org.json jar')
    args.work.mkdir(parents=True, exist_ok=False)
    fixture = args.work/'StationLobbyRecoveryTest.java'
    fixture.write_bytes((ROOT/'tests/StationLobbyRecoveryR117Test.java.in').read_bytes())
    sources = [ROOT/'java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineClient.java',
               ROOT/'java/netplay-src/org/emulationstation/frontend/netplay/StationOnlinePlatformPolicy.java',
               ROOT/'java/client/src/java/org/emulationstation/frontend/station/StationPlatforms.java']
    dependencies = [args.json_jar, args.dependency_build/'rooms.jar', args.dependency_build/'client.jar', args.android_jar]
    cp = os.pathsep.join(map(str, [args.work, *dependencies]))
    suffix = '.exe' if os.name == 'nt' else ''
    def run(command, label):
        result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
        (args.work/(label+'.log')).write_text(result.stdout+result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(label+' failed; inspect private log')
        return result.stdout
    run([args.jdk/('javac'+suffix), '-encoding', 'UTF-8', '--release', '8', '-proc:none',
         '-cp', cp, '-d', args.work, *sources, fixture], 'javac')
    result = json.loads(run([args.jdk/('java'+suffix), '-cp', cp,
                           'org.emulationstation.frontend.netplay.StationLobbyRecoveryTest'], 'lobby'))
    if not result.get('passed') or result.get('checks') != 54:
        raise RuntimeError('Complete expected lobby suite did not pass')
    result.update(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  recipeSHA256=sha(__file__), fixtureSHA256=sha(fixture),
                  sourceHashes={str(p.relative_to(ROOT)):sha(p) for p in sources},
                  dependencyHashes={p.name:sha(p) for p in dependencies},
                  scope='actual patched Java compiled on host; Android UI, WAN and gameplay are not tested',
                  physicalAndroidGameplayVerified=False)
    text = json.dumps(result, indent=2)+'\n'
    (args.work/'receipt.json').write_text(text, encoding='utf-8')
    (ROOT/'evidence/lobby-recovery-r117-tests.json').write_text(text, encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('sourceHashes', 'dependencyHashes')}))

if __name__ == '__main__':
    main()
