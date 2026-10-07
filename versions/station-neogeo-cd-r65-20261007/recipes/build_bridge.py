"""Reproduce R65 classes30.dex from exact sources. All generated files stay on E:."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess

p=argparse.ArgumentParser()
p.add_argument('--work',type=Path,required=True)
p.add_argument('--jdk-bin',type=Path,default=Path('C:/Program Files/Eclipse Adoptium/jdk-17.0.20.101-hotspot/bin'))
p.add_argument('--android-jar',type=Path,default=Path('G:/Android/Sdk/platforms/android-34/android.jar'))
p.add_argument('--d8-jar',type=Path,default=Path('G:/Android/Sdk/build-tools/34.0.0/lib/d8.jar'))
a=p.parse_args();root=Path(__file__).resolve().parents[1];w=a.work.resolve()
assert w.drive.lower()=='e:' and not w.exists(), 'Use a fresh output folder on E:'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
expected=json.loads((root/'evidence/build.json').read_text('utf8'))
sources=sorted((root/'java').rglob('*.java'))
actual={s.relative_to(root).as_posix():sha(s) for s in sources}
assert actual==expected['sourceFiles'], 'Source mismatch'
w.mkdir(parents=True);(w/'classes').mkdir();(w/'dex').mkdir();(w/'evidence').mkdir()
os.environ['TEMP']=os.environ['TMP']=str(w)
def run(cmd,name):
    r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace')
    (w/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');r.check_returncode()
run([a.jdk_bin/'javac.exe','-J-Djava.io.tmpdir='+str(w),'-encoding','UTF-8','--release','8','-classpath',a.android_jar,'-d',w/'classes',*sources],'javac')
run([a.jdk_bin/'jar.exe','--create','--file',w/'bridge.jar','-C',w/'classes','.'],'jar')
run([a.jdk_bin/'java.exe','-Djava.io.tmpdir='+str(w),'-cp',a.d8_jar,'com.android.tools.r8.D8','--min-api','26','--lib',a.android_jar,'--output',w/'dex',w/'bridge.jar'],'d8')
assert sorted(f.name for f in (w/'dex').glob('*.dex'))==['classes.dex']
got=sha(w/'dex/classes.dex');assert got==expected['dexSHA256'],(got,expected['dexSHA256'])
(w/'evidence/build.json').write_text(json.dumps(expected,indent=2)+'\n','utf8')
receipt={'passed':True,'dexSHA256':got,'sourceFiles':actual,'reproducedIdenticalDEX':True,'androidJarSHA256':sha(a.android_jar),'d8JarSHA256':sha(a.d8_jar),'apkInstalled':False}
(w/'reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8');print(json.dumps(receipt))
