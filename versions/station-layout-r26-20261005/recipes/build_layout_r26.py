from pathlib import Path
import json,hashlib,subprocess,os,shutil
C=Path(__file__).resolve().parent;W=Path(r'E:\ESTUDO APK\work\station-layout-r26-20261005');B=Path(r'E:\ESTUDO APK\work\station-console-panel-r25-20261005');N=W/'native'
os.environ['TMP']=os.environ['TEMP']=str(W/'temp')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(name,cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence'/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-5000:];return r.stdout
shutil.copy2(C/'test_layout_r26.cpp',W/'tests/test_layout_r26.cpp')
run('host-build',[r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-I',N,W/'tests/test_layout_r26.cpp','-o',W/'tests/test_layout_r26.exe'])
tests=run('host-tests',[W/'tests/test_layout_r26.exe']);print(tests,flush=True)
previous=json.loads((B/'evidence/native-build.json').read_text('utf8'))
base={p.name:sha(p) for p in (B/'native').iterdir() if p.is_file()};assert base==previous['overlaySources']
cmd=[x.replace(str(B/'native'),str(N)).replace(str(B/'libturbo_carousel.so'),str(W/'libturbo_carousel.so')) for x in previous['command']]
run('android-build',cmd)
final={p.name:sha(p) for p in N.iterdir() if p.is_file()}
changed=[n for n in base if base[n]!=final[n]];assert set(changed)=={'native_info.h','native_carousel.cpp','station_game_panel_layout.h'}
result={'baseAPK':str(B/'TurboStations-Console-Players-R25-20261005.apk'),'baseSHA256':'0d62d806fb0fd7ef45cf0167dd6908794e180e81171c8f7fa0b3e701aa78baad','baseNative':str(B/'native'),'baseSources':base,'overlaySources':final,'command':cmd,'changedSources':changed,'addedSources':sorted(set(final)-set(base)),'soSHA256':sha(W/'libturbo_carousel.so'),'soBytes':(W/'libturbo_carousel.so').stat().st_size,'androidCompile':True,'hostTests':tests,'r24LedSourcesUnchanged':True,'r25ConsoleFitUnchanged':True}
(W/'evidence/native-build.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({'built':True,'sha256':result['soSHA256']}),flush=True)
