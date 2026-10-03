from pathlib import Path
import subprocess,os,zipfile,json,hashlib
r=Path(__file__).resolve().parent;out=r/'build/device-frontend';out.mkdir(parents=True,exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(r/'temp')
cc=r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe'
lib=out/'libstation_frontend.so'
subprocess.run([cc,'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-fvisibility=hidden','-Wall','-Wextra','-Werror','-Wno-return-type-c-linkage','-static-libstdc++','-Wl,--exclude-libs,ALL','-Wl,--no-undefined','-Wl,-z,max-page-size=16384',str(r/'tests/station_frontend_test.cpp'),'-ldl','-o',str(lib)],check=True)
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');android=r'G:\Android\Sdk\platforms\android-34\android.jar'
classes=out/'classes';classes.mkdir(exist_ok=True)
subprocess.run([str(jdk/'javac.exe'),'-encoding','UTF-8','--release','8','-cp',android+os.pathsep+str(r/'build/android-classes'),'-d',str(classes),str(r/'tests/StationFrontendDeviceTest.java')],check=True)
jar=out/'test.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 for base in [r/'build/android-classes',classes]:
  for p in base.rglob('*.class'):z.write(p,p.relative_to(base).as_posix())
dex=out/'dex';dex.mkdir(exist_ok=True)
subprocess.run([str(jdk/'java.exe'),'-cp',r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',str(dex),str(jar)],check=True)
with zipfile.ZipFile(out/'frontend-test.jar','w') as z:z.write(dex/'classes.dex','classes.dex')
print('Native frontend device fixture ready: '+str(out))
