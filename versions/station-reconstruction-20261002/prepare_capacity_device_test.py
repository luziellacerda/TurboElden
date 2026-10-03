from pathlib import Path
import os, subprocess, zipfile, shutil
from datetime import datetime
r=Path(__file__).resolve().parent
out=r/'build/device-capacity';out.mkdir(parents=True,exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(r/'temp')
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
jsonjar=r/'tools/json-20250517.jar'
host=r/'build/host-classes'
subprocess.run([str(jdk/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',str(host)+os.pathsep+str(jsonjar),'-d',str(host),str(r/'tests/StationCapacityTest.java')],check=True)
fixture=out/datetime.now().strftime('fixture-%Y%m%d-%H%M%S')
subprocess.run([str(jdk/'java.exe'),'-Xmx512m','-cp',str(host)+os.pathsep+str(jsonjar),'org.emulationstation.frontend.station.StationCapacityTest',str(fixture)],check=True)
for name in ['catalog-envelope.json','authority.der','device-public.der','capacity-results.json']:
 shutil.copy2(fixture/name,out/name)
android=r'G:\Android\Sdk\platforms\android-34\android.jar'
classes=out/'classes';classes.mkdir(exist_ok=True)
subprocess.run([str(jdk/'javac.exe'),'--release','8','-encoding','UTF-8','-cp',android+os.pathsep+str(r/'build/android-classes'),'-d',str(classes),str(r/'tests/device/StationCapacityAndroidTest.java')],check=True)
jar=out/'test.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 for root in [r/'build/android-classes',classes]:
  for p in root.rglob('*.class'):z.write(p,p.relative_to(root).as_posix())
dex=out/'dex';dex.mkdir(exist_ok=True)
subprocess.run([str(jdk/'java.exe'),'-cp',r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',str(dex),str(jar)],check=True)
with zipfile.ZipFile(out/'capacity-test.jar','w') as z:z.write(dex/'classes.dex','classes.dex')
print('Isolated Android capacity fixture ready: '+str(out))
