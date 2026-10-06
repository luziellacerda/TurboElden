from pathlib import Path
import json,hashlib,subprocess
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
p=N/'native_theme_preferences.h';s=p.read_text('utf8');s=s.replace('jstring name=env->NewStringUTF("station_appearance"),key=env->NewStringUTF("theme");if(!name||!key)break;','jstring name=env->NewStringUTF("station_appearance");if(!name)break;\n  jstring key=env->NewStringUTF("theme");if(!key)break;');p.write_text(s,'utf8')
# Confirm regression detects the old behavior using the same native-folder test harness.
t=W/'tests';old=(N/'native_folders.h').read_text('utf8')
old=old.replace('firstFolderGame(p);refreshHook(p);folderRevision=foldersRevision();','refreshHook(p);')
old=old.replace('at<int>(p,0xf0)=0;at<float>(p,0xf4)=0;\n if(selectedKind>=0){','if(selectedKind>=0){')
(t/'old_folder_behavior.h').write_text(old,'utf8');test=(t/'navigation.cpp').read_text('utf8').replace('#include "native_folders.h"','#include "old_folder_behavior.h"');(t/'navigation_before.cpp').write_text(test,'utf8')
r=subprocess.run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-I',str(N),'-I',str(t),str(t/'navigation_before.cpp'),'-o',str(t/'navigation_before.exe')],capture_output=True,text=True);assert r.returncode==0,r.stderr
r=subprocess.run([str(t/'navigation_before.exe')],capture_output=True,text=True);assert r.returncode!=0,'Regression did not catch old behavior'
(W/'evidence/navigation-before.json').write_text(json.dumps({'passed':False,'expectedFailure':True,'returncode':r.returncode,'output':r.stdout+r.stderr,'method':'Same real native folder code with pre-R39 entry-selection placement, simulated native rebuild restores an out-of-range cursor; post-fix harness passes.'},indent=2),'utf8')
print('Regression fails before the selection fix as expected:',r.stderr.strip())
