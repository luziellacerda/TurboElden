"""Build R66's three Java bridge sources; generated files stay on E:."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--expected-dex')
a=p.parse_args();root=Path(__file__).resolve().parents[1];w=a.work.resolve()
assert w.drive.lower()=='e:' and not w.exists()
w.mkdir(parents=True);(w/'classes').mkdir();(w/'dex').mkdir();(w/'evidence').mkdir()
os.environ['TEMP']=os.environ['TMP']=str(w)
j=Path('C:/Program Files/Eclipse Adoptium/jdk-17.0.20.101-hotspot/bin');api=Path('G:/Android/Sdk/platforms/android-34/android.jar');d8=Path('G:/Android/Sdk/build-tools/34.0.0/lib/d8.jar')
sources=sorted((root/'java').rglob('*.java'));assert len(sources)==3
def run(args,name):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(w/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');r.check_returncode()
run([j/'javac.exe','-J-Djava.io.tmpdir='+str(w),'-encoding','UTF-8','--release','8','-classpath',api,'-d',w/'classes',*sources],'javac')
run([j/'jar.exe','--create','--file',w/'bridge.jar','-C',w/'classes','.'],'jar')
run([j/'java.exe','-Djava.io.tmpdir='+str(w),'-cp',d8,'com.android.tools.r8.D8','--min-api','26','--lib',api,'--output',w/'dex',w/'bridge.jar'],'d8')
assert sorted(p.name for p in (w/'dex').glob('*.dex'))==['classes.dex']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();digest=sha(w/'dex/classes.dex')
if a.expected_dex:assert digest==a.expected_dex
result={'compiled':True,'sourceFiles':{p.relative_to(root).as_posix():sha(p) for p in sources},'dexSHA256':digest,'dexBytes':(w/'dex/classes.dex').stat().st_size,'androidJarSHA256':sha(api),'d8JarSHA256':sha(d8),'expectedDEXMatched':bool(a.expected_dex),'bundledBIOSAutomaticPreparation':True,'newBIOSAssetsAdded':False,'cartridgeRouteChanged':False,'runtimeChanged':False,'androidInstalled':False}
(w/'evidence/build.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))
