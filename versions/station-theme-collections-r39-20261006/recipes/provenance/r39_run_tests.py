from pathlib import Path
import subprocess,shutil,json
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native';T=W/'tests'
R=Path('work/TurboElden-git');compiler=r'C:\Program Files\LLVM\bin\clang++.exe'
for name in ['r39_tests.cpp','r39_jni_tests.cpp']:shutil.copy2(name,T/name)
nav=(R/'versions/station-single-folder-r17-20261005/tests/navigation.cpp').read_text('utf8')
nav=nav.replace('char synopsis[2048]','char synopsis[6144]').replace('"biblioteca completa"','"Toda a biblioteca"').replace('"Coleção RPG."','"RPG —"')
nav=nav.replace('filterFolderGames(p);}', 'at<int>(p,0xf0)=(int)n+50;at<float>(p,0xf4)=(float)n+50;filterFolderGames(p);}')
nav=nav.replace('openSelectedFolder(ui);','openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}')
nav=nav.replace('#include "native_folders.h"','static void clearSearchForNavigation(void*p){strAssign((B*)p+0x650,"");}\n#include "native_folders.h"')
(T/'navigation.cpp').write_text(nav,'utf8')
frontend=R/'versions/station-final-details-r37-20261005/frontend'
shutil.copy2(frontend/'station_collections.hpp',T/'station_collections.hpp')
report={}
for name in ['r39_tests','r39_jni_tests','navigation','test_ui_r37']:
 cmd=[compiler,'-std=c++17','-O2','-include','initializer_list','-I',str(N),'-I',str(T),str(T/(name+'.cpp')),'-o',str(T/(name+'.exe'))]
 r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence'/(name+'-compile.log')).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-2000:]
 r=subprocess.run([str(T/(name+'.exe'))],capture_output=True,text=True,encoding='utf8',errors='replace');report[name]=dict(returncode=r.returncode,output=r.stdout+r.stderr);print(name,r.stdout+r.stderr,flush=True);assert r.returncode==0
(W/'evidence/local-tests.json').write_text(json.dumps(report,indent=2),'utf8')
