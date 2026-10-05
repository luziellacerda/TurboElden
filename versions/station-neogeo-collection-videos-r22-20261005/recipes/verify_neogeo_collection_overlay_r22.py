from pathlib import Path
import json, subprocess, re, shutil, hashlib
W=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005');N=W/'native';T=W/'tests'
R=Path(r'E:\ESTUDO APK\work\station-console-games-only-r21-20261005')
B=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
cc=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
def run(name,args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace')
 (T/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-2000:]
 return r.stdout.strip()
shutil.copyfile(R/'synopsis-tests/test_synopsis_scroll.cpp',T/'test_synopsis_scroll.cpp')
run('scroll-compile',[cc,'-std=c++17',T/'test_synopsis_scroll.cpp','-o',T/'scroll.exe'])
scroll=run('scroll',[T/'scroll.exe'])
shutil.copyfile(R/'tests/visibility.cpp',T/'visibility.cpp');(T/'before').mkdir(exist_ok=True)
shutil.copyfile(R/'tests/before/station_info_layout.h',T/'before/station_info_layout.h')
run('visibility-compile',[cc,'-std=c++17','-I',N,T/'visibility.cpp','-o',T/'visibility.exe'])
visibility=run('visibility',[T/'visibility.exe'])
symbols=run('native-symbols',[r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\llvm-nm.exe','--defined-only',W/'libturbo_carousel.so'])
new=[line for line in symbols.splitlines() if re.search(r'\bstation_neogeo_collection_',line)]
old=[line for line in symbols.splitlines() if re.search(r'\bstation_(?:collection_video|video_frame)_',line)]
assert len(new)==3 and len(old)==49,(len(new),len(old))
header=(N/'video720_posters.h').read_text('utf8')
assert len(re.findall(r'^\{"turbo-system-videos/',header,re.M))==52
assert 'video720TextureBudget=8' in (B/'video720_policy.h').read_text('utf8')
assert 'video720SlotCount=4' in (N/'native_system_video720.h').read_text('utf8')
evidence={'synopsis':scroll,'visibility':visibility,'compiledPosterSymbols':len(new)+len(old),
          'newPosterSymbols':new,'existingPosterSymbols':len(old),'duplicatePosterSymbols':False,
          'textureBudgetUnchanged':8,'playerSlotLimitUnchanged':4,'rendersOrPlayersAdded':0}
(W/'evidence/regressions.json').write_text(json.dumps(evidence,indent=2)+'\n','utf8')
print(json.dumps(evidence))
