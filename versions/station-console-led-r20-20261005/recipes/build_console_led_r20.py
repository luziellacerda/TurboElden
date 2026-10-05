from pathlib import Path
import subprocess, json, hashlib, os
W=Path(r'E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005');N=W/'native';T=W/'tests'
B=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
os.environ['TEMP']=os.environ['TMP']=str(W/'temp')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf-8',errors='replace')
 (T/(name+'.log')).write_text(r.stdout+r.stderr,'utf-8');assert r.returncode==0,(name,(r.stdout+r.stderr)[-3000:])
 print(name+': '+(r.stdout+r.stderr)[-350:],flush=True);return r.stdout.strip()
test=r'''
#include <cstring>
#include <cstdio>
#include <cstdlib>
static bool presentationKeyEqual(const char*a,const char*b){if(!a||!b)return false;while(*a&&*b){char x=*a++,y=*b++;if(x>='A'&&x<='Z')x+=32;if(y>='A'&&y<='Z')y+=32;if(x!=y)return false;}while(*a==' ')a++;while(*b==' ')b++;return *a==*b;}
#include "station_console_keys.h"
#include "neogeo_led_profile.h"
static int n;static void check(bool x){++n;if(!x){printf("FAIL %d\n",n);exit(2);}}
int main(){
 for(const auto&r:stationConsoleAliases)check(stationConsoleKey(r.alias)&&strcmp(stationConsoleKey(r.alias),r.key)==0);
 for(const char*s:{"Neo Geo","Neo Geo CD","neo-geo","neo-geo-cd","neogeo","neogeocd","NEO GEO CD"})check(neoMagazineKey(s));
 for(const char*s:{"Neo Geo Extra","neo-geo-cd-wrong","Nintendo 64","Super Nintendo","MegaDrive",""})check(!neoMagazineKey(s));
 check(!neoMagazineKey(nullptr));check(!stationConsoleKey(nullptr));check(!stationConsoleKey("unknown"));
 check(neoSquareVideoAsset("turbo-system-videos/720-neogeocd.mp4"));
 for(const char*s:{"turbo-system-videos/720-neogeo.mp4","720-neogeocd.mp4","turbo-system-videos/720-neogeocd.mp4.old",""})check(!neoSquareVideoAsset(s));
 check(!neoSquareVideoAsset(nullptr));printf("PASS %d console and LED routing checks\n",n);
}
'''
test='#include <initializer_list>\n'+test
(T/'routing.cpp').write_text(test,'utf-8')
cc=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
run('routes-compile',[cc,'-std=c++17','-Wall','-Wextra','-I'+str(N),T/'routing.cpp','-o',T/'routing.exe'])
routes=run('routes',[T/'routing.exe'])
nav=Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005\tests\navigation.cpp')
run('navigation-compile',[cc,'-std=c++17','-I'+str(N),'-I'+str(B),'-I'+str(B.parent/'client/src/native'),nav,'-o',T/'navigation.exe'])
navigation=run('navigation',[T/'navigation.exe'])
clang=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe')
cmd=[clang,'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so','-I',B,N/'native_carousel.cpp',B/'video720_posters.o','-L',B,'-lc','-ldl','-llog','-o',W/'libturbo_carousel.so']
run('android-build',cmd)
record={'routes':routes,'navigation':navigation,'androidCompile':True,'command':list(map(str,cmd)),'soSHA256':sha(W/'libturbo_carousel.so'),'soBytes':(W/'libturbo_carousel.so').stat().st_size,'overlaySources':{p.name:sha(p) for p in N.iterdir() if p.is_file()}}
(W/'evidence/native-build.json').write_text(json.dumps(record,indent=2),'utf-8')
print(json.dumps({'native':record['soSHA256'],'bytes':record['soBytes']}),flush=True)
