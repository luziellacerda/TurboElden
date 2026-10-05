from pathlib import Path
import subprocess,os,zipfile,json,hashlib
W=Path(r'E:\ESTUDO APK\work\station-netplay-20261004\internet-r12');O=W/'app-build';O.mkdir(exist_ok=True)
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');A=Path(r'G:\Android\Sdk\platforms\android-34\android.jar');station=Path(r'E:\ESTUDO APK\work\station-library-r10-build-20261004\station-client.jar')
classes=O/'classes';classes.mkdir(exist_ok=True);dex=O/'dex';dex.mkdir(exist_ok=True)
sources=sorted((W/'netplay-src').rglob('*.java'))+sorted((W/'dependency-src').rglob('*.java'))
args=['-encoding','UTF-8','--release','8','-cp',str(A)+';'+str(station),'-d',str(classes)]+[str(p) for p in sources]
argfile=O/'javac.args';argfile.write_text('\n'.join('"'+a.replace('\\','/')+'"' for a in args),'utf8')
subprocess.run([str(J/'javac.exe'),'@'+str(argfile)],check=True)
jar=O/'netplay-internet.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 for p in classes.rglob('*.class'):z.write(p,p.relative_to(classes).as_posix())
subprocess.run([str(J/'java.exe'),'-cp',r'G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',str(A),'--classpath',str(station),'--output',str(dex),str(jar)],check=True)
report={'sourceFiles':len(sources),'java8Api34':True,'dexApi26':True,'files':{str(p.relative_to(O)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [jar,dex/'classes.dex']},'installed':False}
(O/'build-result.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report,indent=2))
