from pathlib import Path
import os,subprocess,json,hashlib
r=Path(__file__).resolve().parent
out=r/'build/native/arm64-v8a';out.mkdir(parents=True,exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(r/'temp')
ndk=Path(os.environ.get('STATION_NDK',r'E:\TurboEdenEngine\android-ndk-r28c'))
cc=ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/clang++.exe'
lib=out/'libstation_frontend.so'
subprocess.run([str(cc),'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-fvisibility=hidden','-Wall','-Wextra','-Werror','-Wno-return-type-c-linkage','-static-libstdc++','-Wl,--exclude-libs,ALL','-Wl,--no-undefined','-Wl,-z,max-page-size=16384',str(r/'src/native/station_frontend.cpp'),'-ldl','-llog','-o',str(lib)],check=True)
report={'library':str(lib),'sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),'size':lib.stat().st_size,'apkIntegrated':False}
(r/'build/frontend-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
