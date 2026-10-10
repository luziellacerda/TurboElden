"""Exercise the compiled production lobby merge and read-only retry policy."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[1]
JSON_SHA='3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ('work','build','jdk','json-jar','android-jar'):parser.add_argument('--'+n,type=Path,required=True)
    a=parser.parse_args();build=json.loads((a.build/'receipt.json').read_bytes())
    if not build['compiled'] or sha(a.json_jar)!=JSON_SHA or sha(a.android_jar)!=build['inputs']['androidJar']:raise ValueError('Pinned complete build inputs required')
    for name,digest in build['sourceHashes'].items():
        if sha(ROOT/'java'/name)!=digest:raise ValueError('Source changed after complete build')
    a.work.mkdir(parents=True,exist_ok=False);fixture=a.work/'StationLobbyRecoveryTest.java';fixture.write_bytes((ROOT/'tests/StationLobbyRecoveryTest.java.in').read_bytes())
    cp=os.pathsep.join(map(str,[a.work,a.json_jar,a.build/'rooms.jar',a.build/'client.jar',a.android_jar]));suffix='.exe' if os.name=='nt' else ''
    def run(command,label):
        r=subprocess.run(list(map(str,command)),capture_output=True,text=True);(a.work/(label+'.log')).write_text(r.stdout+r.stderr)
        if r.returncode:raise RuntimeError(label+' failed; inspect private log')
        return r.stdout
    run([a.jdk/('javac'+suffix),'-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',a.work,fixture],'javac')
    result=json.loads(run([a.jdk/('java'+suffix),'-cp',cp,'org.emulationstation.frontend.netplay.StationLobbyRecoveryTest'],'lobby'))
    if not result['passed'] or result['checks']!=36:raise RuntimeError('Complete expected lobby suite did not pass')
    result.update(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),jsonJarSHA256=JSON_SHA,recipeSHA256=sha(__file__),fixtureSHA256=sha(fixture),roomsJarSHA256=sha(a.build/'rooms.jar'),sourceHashes=build['sourceHashes'],physicalAndroidGameplayVerified=False)
    text=json.dumps(result,indent=2)+'\n';(a.work/'receipt.json').write_text(text);(ROOT/'evidence/lobby-recovery-tests.json').write_text(text);print(json.dumps({k:v for k,v in result.items() if k!='sourceHashes'}))
if __name__=='__main__':main()
