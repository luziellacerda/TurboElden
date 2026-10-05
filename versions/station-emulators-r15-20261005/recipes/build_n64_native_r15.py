import os
from pathlib import Path
import shutil,subprocess,json,hashlib
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=Path(os.environ['STATION_N64_WORK']);N=W/'frontend-native'
assert not N.exists(),'Native snapshot already exists; do not overwrite'
shutil.copytree(Path(os.environ['STATION_BASE_NATIVE']),N)
shutil.copy2('native_n64.h',N/'native_n64.h')
p=N/'native_carousel.cpp';s=p.read_text('utf8');before=hashlib.sha256(p.read_bytes()).hexdigest()
needle='#include "native_mega.h"';assert s.count(needle)==1
s=s.replace(needle,needle+'\n#include "native_n64.h"')
hook_names=['Command','Run','Fresh','Bundled','Installed','Assets','Pack','Definitions','Settings']
for name in hook_names:
 a='(void*)mega'+name+'Hook';b='(void*)n64'+name+'Hook';assert s.count(a)==1,name;s=s.replace(a,b)
p.write_text(s,'utf8')
args=[r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',N/'native_carousel.cpp',N/'video720_posters.o','-L',N,'-lc','-ldl','-llog','-o',N/'libturbo_carousel.so']
r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/'native-build.log').write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,r.stdout+r.stderr
preserved=[]
for name in ('native_menu_power.h','native_folders.h','native_formation.h','native_game_actions.h','native_netplay.h','native_system_video720.h','video720_posters.o'):
 assert (N/name).read_bytes()==(Path(os.environ['STATION_BASE_NATIVE'])/name).read_bytes(),name;preserved.append(name)
(W/'native-build.json').write_text(json.dumps({'baseSourceSHA256':before,'patchedSourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'soSHA256':hashlib.sha256((N/'libturbo_carousel.so').read_bytes()).hexdigest(),'preservedR14BFiles':preserved},indent=2),'utf8')
print('N64 native compiled; R14B navigation, video, buttons, power, netplay preserved')
