from pathlib import Path
import shutil,subprocess,json,hashlib
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native';T=W/'tests'
shutil.copy2('r39_search_actions.h',N/'station_search_actions.h')
shutil.copy2('r39_search_tests.cpp',T/'r39_search_tests.cpp')
cmd=[r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-I',str(N),str(T/'r39_search_tests.cpp'),'-o',str(T/'r39_search_tests.exe')]
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace');assert r.returncode==0,r.stderr
r=subprocess.run([str(T/'r39_search_tests.exe')],capture_output=True,text=True,encoding='utf8',errors='replace');print(r.stdout,r.stderr,flush=True);assert r.returncode==0
sources=['native_search_state.h','station_search_actions.h','native_search_download.h','native_carousel.cpp','native_folders.h','station_root_label.h']
report={'test':'shared production functions with simulated original GuiStore, no Android claim','command':cmd,'returncode':r.returncode,'output':r.stdout,'sources':{s:hashlib.sha256((N/s).read_bytes()).hexdigest() for s in sources}}
(W/'evidence/search-tests.json').write_text(json.dumps(report,indent=2),'utf8')
