from pathlib import Path
import subprocess, json, hashlib, os
W=Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
N=W/'native'; T=W/'tests'
BASE=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
os.environ['TEMP']=os.environ['TMP']=str(T)
prefix=r'''
#include <string>
#include <cstring>
#include <cstdio>
#include <cstdlib>
struct UiString { std::string value; };
static int checks=0, opened=0, delegated=0, closed=0;
static bool setting=false, allowed=true;
static std::string path;
static void check(bool ok){checks++;if(!ok){fprintf(stderr,"Failed N64 route check %d\n",checks);exit(2);}}
static const char* strData(const void* p){return ((const UiString*)p)->value.c_str();}
static void strAssign(void* p,const char* s){((UiString*)p)->value=s;}
static bool presentationKeyEqual(const char* key,const char* alias){
 while(*key&&*alias){char a=*key++,b=*alias++;if(a>='A'&&a<='Z')a+=32;if(b>='A'&&b<='Z')b+=32;if(a!=b)return false;}
 return *key==*alias;
}
static bool openN64(const char* p,bool s){opened++;setting=s;path=p;return allowed;}
static void requestSettingsClose(void*){closed++;}
static UiString megaRunHook(const void*,const void*){delegated++;return {};}
static bool megaDefinitionsHook(const void*,void*,void*){delegated++;return false;}
static void megaSettingsHook(void*,const void*){delegated++;}
static UiString megaCommandHook(const void*){delegated++;return {};}
static bool megaFreshHook(const void*){delegated++;return true;}
static bool megaBundledHook(const void*){delegated++;return false;}
static bool megaInstalledHook(void*,const void*){delegated++;return false;}
static bool megaAssetsHook(void*,const void*){delegated++;return false;}
static bool megaPackHook(const void*,void*,void*){delegated++;return true;}
'''
suffix=r'''
int main(){
 // Real bundled resolver prepends lib at 0x2a8e2c..0x2a8e3c.
 // Exercise the result passed to run, not only an unresolved command alias.
 for(const char* name:{"mupen64plus_ae_android.so","mupen64plus_next_gles3_libretro_android.so"}){
  UiString core{std::string("lib")+name},game{"/storage/emulated/0/EmulationStation/roms/.station-v2/nintendo-64/id/content/game.z64"};
  int d=delegated,o=opened;check(n64Core(&core));check(n64RunHook(&core,&game).value.empty());
  check(opened==o+1&&delegated==d&&!setting&&path==game.value);
 }
 for(const char* name:{"Nintendo 64","Nintendo 64 - BR","n64","n64br","nintendo-64","nintendo-64--br","NINTENDO-64","NINTENDO 64"}){
  UiString key{name};check(n64CommandHook(&key).value=="libretro: core=mupen64plus_ae_android.so");
  int c=closed,o=opened;n64SettingsHook(nullptr,&key);check(opened==o+1&&closed==c+1&&setting&&path.empty());
 }
 for(const char* name:{"mupen64plus_ae_android.so","mupen64plus_next_gles3_libretro_android.so","mupen64plus_next_gles3"}){
  for(const char* root:{"","lib","/data/app/pkg/lib/arm64/lib","/data/user/0/pkg/files/cores/","C:\\cores\\lib"}){
   UiString core{std::string(root)+name},game{"/some path/Corrida.z64"},title,u,p;
   int d=delegated;check(n64Core(&core));check(n64RunHook(&core,&game).value.empty());check(!setting&&path==game.value);
   n64SettingsHook(nullptr,&core);check(setting&&path.empty());
   check(!n64FreshHook(&core));check(n64BundledHook(&core));check(n64InstalledHook(nullptr,&core));check(n64AssetsHook(nullptr,&core));
   check(!n64DefinitionsHook(&core,&title,nullptr));check(title.value.find("Mupen64Plus AE")!=std::string::npos);
   check(!n64PackHook(&core,&u,&p));check(delegated==d);
  }
 }
 for(const char* name:{"","l","li","lib","/n64/pcsx_rearmed.so","/Nintendo 64/fceumm.so","mupen64plus_ae_android.so.old","xmupen64plus_next_gles3","Super Nintendo","snes9x_libretro_android.so","MegaDrive","mdemu_station.so","MAME","Neo Geo","Nintendo DS","GameCube","PSP","Flycast"}){
  UiString key{name},title,u,p;int d=delegated,o=opened;
  check(!n64Core(&key));n64RunHook(&key,&key);n64CommandHook(&key);n64SettingsHook(nullptr,&key);
  n64DefinitionsHook(&key,&title,nullptr);n64FreshHook(&key);n64BundledHook(&key);n64InstalledHook(nullptr,&key);n64AssetsHook(nullptr,&key);n64PackHook(&key,&u,&p);
  check(delegated==d+9&&opened==o);
 }
 allowed=false;UiString key{"libmupen64plus_ae_android.so"},game{"/missing.z64"};int d=delegated,c=closed;
 check(!n64RunHook(&key,&game).value.empty());n64SettingsHook(nullptr,&key);check(delegated==d&&closed==c);
 printf("PASS %d N64 routing checks: bundled prefix, paths, catalog slugs, own settings, no legacy fallback on launch failure\n",checks);
}
'''
def host_source(path):
 s=path.read_text('utf8')
 a=s.index('static jclass n64Bridge;');b=s.index('static UiString n64RunHook')
 return prefix+s[:a]+s[b:]+suffix
def run(args,name,ok=True):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace')
 (W/(name+'.log')).write_text(p.stdout+p.stderr,'utf8')
 assert (p.returncode==0)==ok,(name,p.stdout+p.stderr)
 print(name,(p.stdout+p.stderr)[-400:],flush=True)
 return p.stdout+p.stderr
cc=r'C:\Program Files\LLVM\bin\clang++.exe'
for label,header in [('routes',N/'native_n64.h'),('old-routes',W/'before/native_n64.h')]:
 (T/(label+'.cpp')).write_text(host_source(header),'utf8')
 run([cc,'-std=c++17',T/(label+'.cpp'),'-o',T/(label+'.exe')],label+'-compile')
 result=run([T/(label+'.exe')],label,label=='routes')
 if label=='routes':good=result.strip()
# Run the R17 navigation checks against the new overlay, preserving single-folder Back behavior.
nav=Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005\tests\navigation.cpp')
run([cc,'-std=c++17','-I'+str(N),'-I'+str(BASE),'-I'+str(BASE.parent/'client/src/native'),nav,'-o',T/'navigation.exe'],'navigation-compile')
navresult=run([T/'navigation.exe'],'navigation').strip()
clang=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe')
cmd=[clang,'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so','-I',BASE,N/'native_carousel.cpp',BASE/'video720_posters.o','-L',BASE,'-lc','-ldl','-llog','-o',W/'libturbo_carousel.so']
run(cmd,'android-build')
(W/'tests.json').write_text(json.dumps({'routes':good,'oldRejected':True,'navigation':navresult,'androidCompiled':True,'command':list(map(str,cmd)),'soSHA256':hashlib.sha256((W/'libturbo_carousel.so').read_bytes()).hexdigest()},indent=2),'utf8')
