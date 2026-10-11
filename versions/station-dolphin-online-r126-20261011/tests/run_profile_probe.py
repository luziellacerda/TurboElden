"""Run the production profile parser with isolated JSON fixtures, not gameplay."""
from pathlib import Path
import argparse,hashlib,json,subprocess

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    for flag in ('jdk','json-jar','android-jar','rooms-jar','out','receipt'):
        parser.add_argument('--'+flag,type=Path,required=True)
    a=parser.parse_args();root=Path(__file__).resolve().parent
    assert not a.out.exists(),'Use a fresh probe directory';a.out.mkdir(parents=True)
    cp=';'.join(str(p) for p in (a.json_jar,a.rooms_jar,a.android_jar))
    source=root/'StationDolphinProfileProbe.java'
    subprocess.run([str(a.jdk/'javac.exe'),'-encoding','UTF-8','--release','8','-cp',cp,'-d',str(a.out),str(source)],check=True,capture_output=True)
    result=subprocess.run([str(a.jdk/'java.exe'),'-cp',str(a.out)+';'+cp,'org.emulationstation.frontend.netplay.StationDolphinProfileProbe'],check=True,capture_output=True,text=True)
    receipt=json.loads(result.stdout)
    receipt.update({'kind':'isolated-jvm-production-profile-parser','probeSourceSha256':sha(source),'roomsJarSha256':sha(a.rooms_jar),'jsonDependencySha256':sha(a.json_jar),'androidGameplayValidated':False})
    a.receipt.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(result.stdout.strip())
if __name__=='__main__':main()
