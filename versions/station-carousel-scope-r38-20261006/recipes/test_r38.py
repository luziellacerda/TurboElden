from pathlib import Path
import subprocess,os
W=Path(__file__).resolve().parent;os.environ['TEMP']=os.environ['TMP']=str(W/'temp')
compiler=r'C:\Program Files\LLVM\bin\clang++.exe'
for name in ('test_ribbons','test_ui_r37'):
 subprocess.run([compiler,'-std=c++17','-O2','-include','initializer_list','-I',str(W/'native'),str(W/'tests'/(name+'.cpp')),'-o',str(W/'tests'/(name+'.exe'))],check=True)
 subprocess.run([str(W/'tests'/(name+'.exe'))],check=True)
