from pathlib import Path
import subprocess,json,os,hashlib,shutil
C=Path(__file__).resolve().parent;W=Path(r'E:\ESTUDO APK\work\station-back-button-r30-20261005');N=W/'native'
os.environ['TEMP']=os.environ['TMP']=str(W/'temp')
def run(name,cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence'/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-3000:];return r.stdout
for name in ['test_layout_r26','test_back_button_r30']:
 if name.endswith('r30'):shutil.copy2(C/(name+'.cpp'),W/'tests'/(name+'.cpp'))
 run(name+'-build',[r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-I',N,W/'tests'/(name+'.cpp'),'-o',W/'tests'/(name+'.exe')])
 print(run(name,[W/'tests'/(name+'.exe')]),flush=True)
r=json.loads((W/'evidence/native-build-input.json').read_text())
run('android-build',r['command'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r['overlaySources']={p.name:sha(p) for p in N.iterdir() if p.is_file()}
r['changedSources']=[n for n in r['baseSources'] if r['baseSources'][n]!=r['overlaySources'][n]]
assert set(r['changedSources'])=={'native_skin.h','station_bottom_action_layout.h'}
r.update(soSHA256=sha(W/'libturbo_carousel.so'),soBytes=(W/'libturbo_carousel.so').stat().st_size,androidCompile=True)
(W/'evidence/native-build.json').write_text(json.dumps(r,indent=2),'utf8');print(r['soSHA256'])
