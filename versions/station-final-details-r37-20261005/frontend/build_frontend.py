from pathlib import Path
import hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parent
BUILD=ROOT/'build';EVIDENCE=ROOT/'evidence';TEMP=BUILD/'temp';TEMP.mkdir(exist_ok=True)
env=dict(os.environ,TEMP=str(TEMP),TMP=str(TEMP))
NDK=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin')
HOST=Path(r'C:\Program Files\LLVM\bin')
commands=[];outputs=[]
def run(args):
 args=list(map(str,args));commands.append(args)
 result=subprocess.run(args,cwd=ROOT,env=env,text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 outputs.append(result.stdout)
 print(result.stdout,end='',flush=True)
 if result.returncode:raise RuntimeError('Build command failed: '+str(result.returncode))
 return result.stdout
run([HOST/'clang.exe','-x','c','-std=c11','-Wall','-Wextra','-Werror','-fsyntax-only',ROOT/'tests'/'bridge_header_c_test.c'])
run([HOST/'clang++.exe','-std=c++17','-O2','-Wall','-Wextra','-Werror',ROOT/'tests'/'profile_name_test.cpp','-o',BUILD/'profile_name_test.exe'])
testOutput=run([BUILD/'profile_name_test.exe'])
base=Path(r'C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\station-native-rate-phase-20261005\client\src\native\station_frontend.cpp').read_text(encoding='utf-8')
current=(ROOT/'station_frontend.cpp').read_text(encoding='utf-8')
expected=base.replace('#include "station_transfer_rate.hpp"','#include "station_transfer_rate.hpp"\n#include "station_profile_bridge.h"\n#include "station_profile_state.hpp"',1).replace('std::atomic<bool> coversForeground{true};','std::atomic<bool> coversForeground{true};\nstation::ProfileName profileName;',1).replace('std::string error,name;','std::string error;').replace('inbox.name=std::move(display);','profileName.publish(std::move(display));')
expected=expected.replace('API jint JNI_OnLoad(JavaVM* machine,void*){','// The authenticated Java publication is the sole producer. The renderer copies\n// a bounded snapshot; it never receives a borrowed std::string or private path.\nAPI uint64_t StationProfile_nameRevision(){return profileName.revision();}\nAPI bool StationProfile_copyName(char* destination,size_t capacity,uint64_t* revision){\n return profileName.copyName(destination,capacity,revision);\n}\n'+'API jint JNI_OnLoad(JavaVM* machine,void*){')
assert expected==current,'Unexpected edits outside name bridge'
baseEvidence=json.loads((EVIDENCE/'base-sources.json').read_text())
for filename,sha in baseEvidence['headers'].items():assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==sha
run([NDK/'clang++.exe','--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-fvisibility=hidden','-Wall','-Wextra','-Werror','-Wno-return-type-c-linkage','-static-libstdc++','-Wl,--exclude-libs,ALL','-I',ROOT,ROOT/'station_frontend.cpp','-ldl','-llog','-o',BUILD/'libstation_frontend.so'])
symbols=run([NDK/'llvm-nm.exe','--defined-only','--dynamic',BUILD/'libstation_frontend.so'])
for symbol in ['StationProfile_nameRevision','StationProfile_copyName','Java_org_emulationstation_frontend_station_StationFrontend_publishCatalog','StationCatalog_update','StationDownload_networkRate']:
 assert symbol in symbols,'Missing export '+symbol
original=run([NDK/'llvm-nm.exe','--defined-only','--dynamic',Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\native-build\libstation_frontend.so')])
names=lambda text:{line.split()[-1] for line in text.splitlines() if line.split()}
assert names(original).issubset(names(symbols)),'Existing exports lost'
assert names(symbols)-names(original)=={'StationProfile_nameRevision','StationProfile_copyName'},'Unexpected new exports'
elf=run([NDK/'llvm-readelf.exe','-lW',BUILD/'libstation_frontend.so'])
loads=[line.split() for line in elf.splitlines() if line.strip().startswith('LOAD')]
assert loads and all(row[-1]=='0x4000' for row in loads),'16KiB LOAD alignment'
files={str(path.relative_to(ROOT)).replace('\\','/'):{'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in list(ROOT.glob('*.h'))+list(ROOT.glob('*.hpp'))+[ROOT/'station_frontend.cpp',ROOT/'tests'/'profile_name_test.cpp',ROOT/'tests'/'bridge_header_c_test.c',ROOT/'build_frontend.py',BUILD/'libstation_frontend.so']}
receipt={'testOutput':testOutput.strip(),'sourceDeltaExact':True,'existingExportsPreserved':True,'newExports':['StationProfile_nameRevision','StationProfile_copyName'],'maximumPageSize':16384,'target':'aarch64-linux-android26','baseFrontendSO':baseEvidence['baseFrontendSO'],'files':files,'commands':commands,'apkPackaged':False,'installed':False,'serverChanged':False}
(EVIDENCE/'compiled-profile-bridge.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
(EVIDENCE/'build.log').write_text(''.join(outputs),encoding='utf-8')
print('PASS exact source delta, all existing exports preserved, two profile exports added, 16KiB alignment')
print(json.dumps(files['build/libstation_frontend.so']))
