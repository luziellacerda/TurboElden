from pathlib import Path
import json,subprocess
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=R/'library-r10/tests'
repo=Path('work/TurboElden-git');cc=r'C:\Program Files\LLVM\bin\clang++.exe'
src=(repo/'versions/station-online-20261004/station/tests/station_synopsis_pages_test.cpp').read_text('utf8')
src=src.replace('../src/native/station_synopsis_pages.hpp','station_synopsis_pages.hpp')
(W/'station_synopsis_pages_test.cpp').write_text(src,'utf8')
results=[]
for name,source in [('station_collection_test',Path('ui-r8/station_collection_test.cpp')),('station_folder_navigation_test',Path('ui-r8/station_folder_navigation_test.cpp')),('station_synopsis_pages_test',W/'station_synopsis_pages_test.cpp')]:
 out=W/(name+'.exe')
 subprocess.run([cc,'-std=c++17','-I'+str(R/'native'),'-I'+str(R/'station/src/native'),str(source),'-o',str(out)],check=True)
 run=subprocess.run([str(out)],capture_output=True,text=True,check=True);print(run.stdout.strip());results.append({'test':name,'output':run.stdout.strip()})
(W/'native-results.json').write_text(json.dumps(results,indent=2)+'\n','utf8')
