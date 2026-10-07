"""Run seven tests against exact compiled Java classes in the restored E: workspace."""
from pathlib import Path
import subprocess,json,datetime
W=Path(__file__).resolve().parent
J=Path('C:/Program Files/Eclipse Adoptium/jdk-17.0.20.101-hotspot/bin')
JSON=Path('E:/ESTUDO APK/work/turbostations-reconstruction-20261002/tools/json-20250517.jar')
T=W/'tests';out=T/'run';out.mkdir();classes=out/'classes';classes.mkdir()
cp=str(JSON)+';'+str(W/'build/final/classes');files=sorted(T.glob('*.java'))
def execute(args,name):
    r=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=90)
    (out/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');r.check_returncode();return r.stdout.strip()
execute([J/'javac.exe','--release','8','-encoding','UTF-8','-cp',cp,'-d',classes,*files],'compile')
results={f.stem:execute([J/'java.exe','-cp',str(classes)+';'+cp,'org.emulationstation.frontend.netplay.'+f.stem],f.stem) for f in files}
(out/'result.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'androidExecuted':False,'productionModified':False},indent=2),'utf8')
print(json.dumps(results,indent=2))
