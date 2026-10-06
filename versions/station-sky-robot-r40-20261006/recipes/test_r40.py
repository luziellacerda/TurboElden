from pathlib import Path
import subprocess,json,os
W=Path(__file__).resolve().parent;os.environ['TEMP']=os.environ['TMP']=str(W/'temp');report={}
for name in ('r40_tests','r39_search_tests','r39_jni_tests','navigation','test_ribbons','test_ui_r37'):
 c=[r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-include','initializer_list','-I',str(W/'native'),'-I',str(W/'tests'),str(W/'tests'/(name+'.cpp')),'-o',str(W/'tests'/(name+'.exe'))]
 p=subprocess.run(c,capture_output=True,text=True,encoding='utf8',errors='replace');assert p.returncode==0,p.stderr
 p=subprocess.run([str(W/'tests'/(name+'.exe'))],capture_output=True,text=True,encoding='utf8',errors='replace');assert p.returncode==0,p.stdout+p.stderr
 report[name]=p.stdout;print(p.stdout,flush=True)
(W/'evidence/local-tests.json').write_text(json.dumps(report,indent=2),'utf8')
