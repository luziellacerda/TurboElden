from pathlib import Path
import subprocess,json
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=R/'native';W=R/'navigation-r14b';T=W/'tests';T.mkdir(exist_ok=True)
def run(args,name,expected=0):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert (p.returncode==0)==(expected==0),(name,p.returncode,p.stdout+p.stderr);print(name,('PASS' if p.returncode==0 else 'old implementation rejected'),(p.stdout+p.stderr)[-500:],flush=True);return p.stdout+p.stderr
nav=(R/'visual-r14/tests/navigation.cpp').read_text('utf8')
insertion=r'''
 // Return remembers stable path AND row kind, not a positional index.
 auto selectedName=[&](){int i=at<int>(ui,0xf0);check(i>=0&&i<folderCount);check(at<float>(ui,0xf4)==(float)i);return strData(folderItems+visible[i]*0xe8+0x18);};
 check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG2"));
 // Server inserts a folder before the selected entry: the visible index shifts.
 int previous=at<int>(ui,0xf0);paths["id_root"]="AAA";revision++;refreshFolderNavigation(ui);
 check(!strcmp(selectedName(),"RPG2"));check(at<int>(ui,0xf0)==previous+1);
 select("RPG");openSelectedFolder(ui);check(folderMode&&!strcmp(folderPath,"RPG"));
 select("Traduções");openSelectedFolder(ui);check(!systemsMode);check(backFromFolder(ui));
 check(!strcmp(selectedName(),"Traduções"));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==0);
 check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG"));
 // Same parent-path direct-games row must not be confused with its child row.
 openSelectedFolder(ui);select("RPG");openSelectedFolder(ui);check(!systemsMode);check(backFromFolder(ui));
 check(!strcmp(selectedName(),"RPG"));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==1);
 check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG"));
 select("Todos os jogos");openSelectedFolder(ui);check(backFromFolder(ui));
 check(!strcmp(selectedName(),"Todos os jogos"));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==2);
 select("RPG2");paths.erase("id_rpg2");revision++;refreshFolderNavigation(ui);
 check(!strcmp(selectedName(),"Todos os jogos")); // Removed selection: explicit safe first row.
 // Restore a leaf then repeat return/refresh with exact selection 200 times.
 paths["id_rpg2"]="RPG2";revision++;refreshFolderNavigation(ui);
 for(int i=0;i<200;i++){select("RPG2");openSelectedFolder(ui);check(!systemsMode);check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG2"));revision++;refreshFolderNavigation(ui);check(!strcmp(selectedName(),"RPG2"));}
'''
needle=' showSystems(ui);for(size_t i=0;i<realItems.size();i++)';assert needle in nav;nav=nav.replace(needle,insertion+needle);(T/'navigation.cpp').write_text(nav,'utf8')
cc=r'C:\Program Files\LLVM\bin\clang++.exe'
run([cc,'-std=c++17','-I'+str(N),'-I'+str(R/'station/src/native'),T/'navigation.cpp','-o',T/'navigation.exe'],'navigation-compile');navigation=run([T/'navigation.exe'],'navigation')
run([cc,'-std=c++17','-I'+str(W/'before'),'-I'+str(N),'-I'+str(R/'station/src/native'),T/'navigation.cpp','-o',T/'navigation-before.exe'],'navigation-before-compile');run([T/'navigation-before.exe'],'navigation-before',1)
cpp=r'''#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <vector>
using U=uint64_t;using B=unsigned char;
static U micros=1000000;static bool dialog,video,systemsMode;static int target;static unsigned slept,calls;
static U count(){return micros;}static U freq(){return 1000000;}
static void delay(unsigned ms){assert(ms>0&&ms<=67);micros+=ms*1000;slept+=ms;calls++;}
static unsigned tick(){return (unsigned)(micros/1000);}
template<class T>static T fn(U addr){assert(addr==0x39e240);return (T)tick;}
template<class T>static T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
static void*dlopen(const char*,int){return (void*)1;}
static void*dlsym(void*,const char*n){if(!strcmp(n,"SDL_GetPerformanceCounter"))return (void*)count;if(!strcmp(n,"SDL_GetPerformanceFrequency"))return (void*)freq;if(!strcmp(n,"SDL_Delay"))return (void*)delay;return nullptr;}
static bool modal(void*){return dialog;}
static const char*video720Asset(void*,int){return video?"video":nullptr;}
static int __android_log_print(int,const char*,const char*,int fps,const char*){target=fps;return 0;}
#include "native_menu_power.h"
int main(){alignas(8) B ui[0x1000]={};int checks=0;
 for(bool d:{false,true})for(bool v:{false,true})for(bool sys:{false,true})for(bool load:{false,true})for(unsigned elapsed:{0u,649u,650u,5000u,60000u}){
  dialog=d;video=v;systemsMode=sys;at<int>(ui,0x370)=load?2:3;micros+=1000000;noteStoreInteraction();micros+=elapsed*1000;
  paceStoreMenu(ui);int expected=!d||elapsed<650||load?60:15;
  if(target!=expected){fprintf(stderr,"target=%d expected=%d dialog=%d elapsed=%u\n",target,expected,d,elapsed);return 2;}checks++;
 }
 dialog=false;systemsMode=true;video=true;at<int>(ui,0x370)=3;micros+=1000000;paceStoreMenu(ui);U start=micros;unsigned beginCalls=calls;
 for(int i=0;i<600;i++){micros+=2000;paceStoreMenu(ui);assert(target==60);}
 U duration=micros-start;assert(duration>=9990000&&duration<=10010000);assert(calls-beginCalls==600);
 micros+=500000;paceStoreMenu(ui);micros+=80000;paceStoreMenu(ui);assert(target==60);
 printf("PASS %d policy cases; 600 frames in %llu us with sleeping, stable foreground target and idle modal15; suspension/overrun recovery\n",checks,(unsigned long long)duration);
}'''
(T/'pacing.cpp').write_text(cpp,'utf8')
run([cc,'-std=c++17','-I'+str(N),T/'pacing.cpp','-o',T/'pacing.exe'],'pacing-compile');pacing=run([T/'pacing.exe'],'pacing')
run([cc,'-std=c++17','-I'+str(W/'before'),T/'pacing.cpp','-o',T/'pacing-before.exe'],'pacing-before-compile');run([T/'pacing-before.exe'],'pacing-before',1)
run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',N/'native_carousel.cpp',N/'video720_posters.o','-L',N,'-lc','-ldl','-llog','-o',W/'libturbo_carousel.so'],'native-build')
(W/'tests.json').write_text(json.dumps({'passed':True,'navigation':navigation,'pacing':pacing,'bothRegressionTestsFailBeforeFix':True,'compiledAndroid26':True,'deviceFrameRateMeasured':False,'deviceReturnVerified':False},indent=2)+'\n','utf8')
