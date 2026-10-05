from pathlib import Path
import shutil, subprocess, json, hashlib, os

root = Path(__file__).resolve().parent
source = root/'work/neogeo-access-20261005/java'
work = Path(r'E:\ESTUDO APK\work\station-neogeo-access-20261005')
java = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
sdk = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
bt = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP'] = os.environ['TMP'] = str(work)
def run(args, name):
    result = subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace')
    (work/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
if (work/'classes').exists() or (work/'dex').exists(): raise RuntimeError('Do not overwrite compiled revision')
assert len(list(source.rglob('*.java'))) == 2
shutil.copytree(source,work/'java')
(work/'classes').mkdir(); (work/'dex').mkdir()
run([java/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-cp',sdk,'-d',work/'classes',*(work/'java').rglob('*.java')],'compile')
run([java/'java.exe','-Djava.io.tmpdir='+str(work),'-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',sdk,'--output',work/'dex',*(work/'classes').rglob('*.class')],'dex')
result={'compiled':True,'installed':False,'dexSHA256':hashlib.sha256((work/'dex/classes.dex').read_bytes()).hexdigest(),'sourceHashes':{str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (work/'java').rglob('*.java')}}
(work/'bridge-build.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
