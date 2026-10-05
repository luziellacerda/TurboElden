from pathlib import Path
import subprocess,json
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=R/'native';W=R/'collection-video-r13';T=W/'tests';T.mkdir(exist_ok=True)
def run(args,name):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,p.stdout+p.stderr;print((p.stdout+p.stderr)[-2000:],flush=True)
s=(R/'collections-r11/tests/station_collection_navigation_test.cpp').read_text('utf8')
s=s.replace('check(!enterFolderRoot(ui,"Absent platform",3));check(!foldersEnabled);','check(enterFolderRoot(ui,"Absent platform",3));check(folderMode&&folderCount==1);check(folderMeta[select("Todos os jogos")].count==0);check(backFromFolder(ui));check(!foldersEnabled);')
(T/'navigation.cpp').write_text(s,'utf8')
s=r'''#include <cassert>
#include <cstdio>
#include <cstring>
#include "collection_video_policy.h"
int main(){int n=0;auto check=[&](bool x){assert(x);++n;};
 const char*platforms[]={"Super Nintendo","Super Nintendo - BR","snes","snesbr"};
 const char*paths[]={"## BOMBER MAN ##","## DONKEY KONG ##","## SUPER MARIO ##","## TOP GEAR ##","## 1 -PT-BR ##"};
 for(auto platform:platforms)for(int i=0;i<5;i++){
  auto*v=collectionVideoFor(platform,paths[i],false);check(v!=nullptr);check(v==&collectionVideoDefinitions[i]);check(v->aspect==(i==2?1.f:16.f/9.f));
  check(collectionVideoFor(platform,paths[i],true)==nullptr);
 }
 for(auto platform:{"MegaDrive","Nintendo 64","Neo Geo","Unknown"})for(auto path:paths)check(collectionVideoFor(platform,path,false)==nullptr);
 check(collectionVideoFor("snes","## MEGA MAN ##",false)==nullptr);check(collectionVideoFor("snes","## FINAL FIGHT ##",false)==nullptr);
 check(collectionVideoFor("snes","nested/## TOP GEAR ##",false)==&collectionVideoDefinitions[3]);
 check(collectionVideoFor("snes","## TOP GEAR ## sequel",false)==nullptr);check(collectionVideoFor(nullptr,"",false)==nullptr);
 printf("PASS %d exact collection video and source aspect checks\n",n);
}'''.replace('#include <cstdio>','#include <cstdio>\n#include <initializer_list>')
(T/'policy.cpp').write_text(s,'utf8')
for name in ['navigation','policy']:
 run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-I'+str(N),'-I'+str(R/'station/src/native'),T/(name+'.cpp'),'-o',T/(name+'.exe')],name+'-compile');run([T/(name+'.exe')],name)
assert 'drawFolderLabels' not in (N/'native_info.h').read_text('utf8')
assert 'drawFolderLabels' not in (N/'native_formation.h').read_text('utf8')
run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',N/'native_carousel.cpp',W/'before/video720_posters.o',W/'collection_previews.o','-L',N,'-lc','-ldl','-llog','-o',W/'libturbo_carousel.so'],'native-build')
(W/'tests.json').write_text(json.dumps({'passed':True,'navigation':(W/'navigation.log').read_text('utf8'),'videoMapping':(W/'policy.log').read_text('utf8'),'noCellLabelRenderer':True,'nativeAndroid26Compiled':True,'deviceVisualVerified':False},indent=2)+'\n','utf8')
