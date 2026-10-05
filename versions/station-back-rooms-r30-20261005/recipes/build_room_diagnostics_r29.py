from pathlib import Path
import subprocess,os,zipfile,json,hashlib,sys,datetime
W=Path(r'E:\ESTUDO APK\work\station-room-diagnostics-r29-20261005')
label=sys.argv[1] if len(sys.argv)>1 else 'final'
assert label in ('baseline','final')
O=W/'build'/label;O.mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(W)
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');A=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
station=Path(r'E:\ESTUDO APK\work\station-library-r10-build-20261004\station-client.jar')
classes=O/'classes';classes.mkdir(exist_ok=True);dex=O/'dex';dex.mkdir(exist_ok=True)
sources=sorted((W/'netplay-src').rglob('*.java'))+sorted((W/'dependency-src').rglob('*.java'))
args=['-encoding','UTF-8','--release','8','-cp',str(A)+';'+str(station),'-d',str(classes)]+[str(p) for p in sources]
argfile=O/'javac.args';argfile.write_text('\n'.join('"'+a.replace('\\','/')+'"' for a in args),'utf8')
def run(args,name):
 r=subprocess.run([str(v) for v in args],capture_output=True,text=True,encoding='utf8',errors='replace');(O/name).write_text(r.stdout+r.stderr,'utf8');print((r.stdout+r.stderr)[-2200:]);r.check_returncode()
run([J/'javac.exe','@'+str(argfile)],'javac.log')
jar=O/'netplay.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(classes.rglob('*.class')):z.write(p,p.relative_to(classes).as_posix())
run([J/'java.exe','-cp',r'G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',A,'--classpath',station,'--output',dex,jar],'d8.log')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':label,'sourceFiles':len(sources),'files':{str(p.relative_to(W)):sha(p) for p in sources},'dex':str(dex/'classes.dex'),'dexSHA256':sha(dex/'classes.dex'),'dexBytes':(dex/'classes.dex').stat().st_size,'java8API34':True,'minAPI':26}
(O/'result.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({k:result[k] for k in ['sourceFiles','dex','dexSHA256','dexBytes']}))
