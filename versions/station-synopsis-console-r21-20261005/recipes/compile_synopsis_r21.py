from pathlib import Path
import json, subprocess, hashlib, datetime, os
W=Path(r'E:\ESTUDO APK\work\station-console-games-only-r21-20261005')
R=Path(r'E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005\native')
N=W/'native'; E=W/'evidence'
os.environ['TEMP']=os.environ['TMP']=str(W)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(cmd,name):
    r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace')
    (E/(name+'.log')).write_text(r.stdout+r.stderr,'utf8')
    assert r.returncode==0,(r.stdout+r.stderr)[-5000:]
    return r.stdout.strip()
record=json.loads((E/'native-build.json').read_text('utf8'))
if not (E/'intermediate-console-only-build.json').exists():
    (E/'intermediate-console-only-build.json').write_text(json.dumps(record,indent=2),'utf8')
changed=[p.name for p in R.iterdir() if p.is_file() and sha(p)!=sha(N/p.name)]
assert set(changed)=={'native_carousel.cpp','native_info.h','station_info_layout.h'},changed
added=[p.name for p in N.iterdir() if not (R/p.name).exists()]
assert added==['station_synopsis_scroll.h'],added
run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-Wall','-Wextra','-Wno-unused-parameter','-I',N,W/'tests/visibility.cpp','-o',W/'tests/visibility.exe'],'visibility-compile-final')
visibility=run([W/'tests/visibility.exe'],'visibility-final')
scroll_record=json.loads((W/'synopsis-tests/result.json').read_text('utf8'))
run(scroll_record['compile_command'],'scroll-compile-final')
scroll=run([W/'synopsis-tests/test_synopsis_scroll.exe'],'scroll-final')
print(visibility,flush=True);print(scroll,flush=True)
print('Compiling final console + synopsis native library',flush=True)
run(record['command'],'android-compile-final')
record.update(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    changedSources=changed,addedSources=added,tests={'visibility':visibility,'scroll':scroll},
    androidCompile=True,soSHA256=sha(W/'libturbo_carousel.so'),soBytes=(W/'libturbo_carousel.so').stat().st_size,
    preservedR20Sources=[p.name for p in R.iterdir() if p.name not in changed],
    overlaySources={p.name:sha(p) for p in N.iterdir() if p.is_file()},
    synopsis={'nativeMeasuredHeight':True,'clippedViewport':True,'fullText':True,
    'manualDragTextAndScrollbar':True,'autoPageTimerRemoved':True,'modes':['platforms','collections','games']})
(E/'native-build.json').write_text(json.dumps(record,indent=2),'utf8')
print(json.dumps({k:record[k] for k in ['changedSources','addedSources','soSHA256','soBytes','tests']},indent=2),flush=True)
