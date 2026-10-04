from pathlib import Path
import os,subprocess,sys,json,hashlib
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');B=R/'folders/build';B.mkdir(parents=True,exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(B);os.environ['STATION_BUILD_DIR']=str(B)
def run(args,name):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(B/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,p.stdout+p.stderr;print(name+': PASS',flush=True)
run([sys.executable,R/'station/run_tests.py'],'station-tests')
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
run([J/'java.exe','-cp',str(B/'host-classes')+';E:\\ESTUDO APK\\work\\turbostations-reconstruction-20261002\\tools\\json-20250517.jar','org.emulationstation.frontend.station.StationFoldersTest'],'folder-java-tests')
run([sys.executable,R/'station/build_module.py'],'station-dex')
out=B/'native/arm64-v8a';out.mkdir(parents=True,exist_ok=True)
cc=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe')
run([cc,'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-fvisibility=hidden','-Wall','-Wextra','-Werror','-Wno-return-type-c-linkage','-static-libstdc++','-Wl,--exclude-libs,ALL','-Wl,--no-undefined','-Wl,-z,max-page-size=16384',R/'station/src/native/station_frontend.cpp','-ldl','-llog','-o',out/'libstation_frontend.so'],'frontend')
print('Station folder catalog Java + native built.')
