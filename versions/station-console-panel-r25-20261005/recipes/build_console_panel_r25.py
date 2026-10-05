from pathlib import Path
import json,hashlib,subprocess,os,shutil
C=Path(__file__).resolve().parent;W=Path(r'E:\ESTUDO APK\work\station-console-panel-r25-20261005');B=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005');N=W/'native'
os.environ['TMP']=os.environ['TEMP']=str(W/'temp')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(name,cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence'/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-2500:];return r.stdout
shutil.copy2(C/'test_console_panel_r25.cpp',W/'tests/test_console_panel_r25.cpp')
cc=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
run('host-build',[cc,'-std=c++17','-O2','-I',N,W/'tests/test_console_panel_r25.cpp','-o',W/'tests/test_console_panel_r25.exe'])
tests=run('host-tests',[W/'tests/test_console_panel_r25.exe']);print(tests,flush=True)
previous=json.loads((B/'evidence/native-build.json').read_text('utf8'))
base={p.name:sha(p) for p in (B/'native').iterdir() if p.is_file()};assert base==previous['overlaySources']
cmd=[x.replace(str(B/'native'),str(N)).replace(str(B/'libturbo_carousel.so'),str(W/'libturbo_carousel.so')) for x in previous['command']]
run('android-build',cmd)
final={p.name:sha(p) for p in N.iterdir() if p.is_file()}
changed=[n for n in base if base[n]!=final[n]];assert set(changed)=={'native_info.h','native_console.h','station_game_panel_layout.h'}
result={'baseAPK':str(B/'TurboStations-NeoGeo-Laser-R24-20261005.apk'),'baseSHA256':'d35516420934aeda7cee96af6185a17506146ae7fa2c28f867d6e7c44e721a0b','baseNative':str(B/'native'),'baseSources':base,'overlaySources':final,'command':cmd,'changedSources':changed,'addedSources':sorted(set(final)-set(base)),'soSHA256':sha(W/'libturbo_carousel.so'),'soBytes':(W/'libturbo_carousel.so').stat().st_size,'androidCompile':True,'hostTests':tests,'r24LedSourcesUnchanged':True}
(W/'evidence/native-build.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({'built':True,'sha256':result['soSHA256']}),flush=True)
