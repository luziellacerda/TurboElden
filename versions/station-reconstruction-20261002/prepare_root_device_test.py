from pathlib import Path
import subprocess,zipfile
r=Path(__file__).resolve().parent
out=r/'build/root-device-test';out.mkdir(parents=True,exist_ok=True)
classes=out/'classes';classes.mkdir(exist_ok=True)
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
subprocess.run([str(jdk/'javac.exe'),'--release','8','-cp',str(r/'build/station-client.jar'),'-d',str(classes),str(r/'tests/device/StationRootDeviceTest.java')],check=True)
jar=out/'fixture.jar'
with zipfile.ZipFile(jar,'w') as z:
 for f in classes.rglob('*.class'):z.write(f,f.relative_to(classes).as_posix())
subprocess.run([str(jdk/'java.exe'),'-cp',r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',str(out),str(jar),str(r/'build/station-client.jar')],check=True)
with zipfile.ZipFile(out/'root-test.jar','w') as z:z.write(out/'classes.dex','classes.dex')
print('Root device fixture ready: '+str(out/'root-test.jar'))
