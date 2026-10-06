from pathlib import Path
import subprocess,json,hashlib,os
W=Path(__file__).resolve().parent;N=W/'native'
os.environ['TEMP']=os.environ['TMP']=str(W/'temp')
def run(name,cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace')
 (W/'evidence'/(name+'.log')).write_text(r.stdout+r.stderr,'utf8')
 assert r.returncode==0,(r.stdout+r.stderr)[-6000:]
 return r.stdout
print(run('host-compile',[r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-include','initializer_list','-I',N,W/'tests/test_ui_r37.cpp','-o',W/'tests/test_ui_r37.exe']))
tests=run('host-tests',[W/'tests/test_ui_r37.exe']);print(tests,flush=True)
r=json.loads((W/'evidence/native-build-input.json').read_text('utf8'))
canonical=Path(r['command'][-1]).parent
r['command']=[part.replace(str(canonical),str(W)) for part in r['command']]
print(run('android-build',r['command']),flush=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r['overlaySources']={p.name:sha(p) for p in N.iterdir() if p.is_file()}
r['changedSources']=[n for n in r['baseSources'] if n not in r['overlaySources'] or r['baseSources'][n]!=r['overlaySources'][n]]
r['addedSources']=[n for n in r['overlaySources'] if n not in r['baseSources']]
r.update(soSHA256=sha(W/'libturbo_carousel.so'),soBytes=(W/'libturbo_carousel.so').stat().st_size,androidCompile=True,hostTests=tests)
(W/'evidence/native-build.json').write_text(json.dumps(r,indent=2),'utf8');print(r['soSHA256'])
