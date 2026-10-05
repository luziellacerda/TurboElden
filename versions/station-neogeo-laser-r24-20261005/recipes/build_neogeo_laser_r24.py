"""Merge four tested LED files onto the released, verified R23 successor."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,zipfile,datetime
p=argparse.ArgumentParser();p.add_argument('--base-receipt',required=True);p.add_argument('--base-native',required=True);p.add_argument('--base-apk',required=True);p.add_argument('--expected-base-sha',required=True);p.add_argument('--base-apk-so-sha',help='Explicit APK SO when released source successor is compiled but not packaged');a=p.parse_args()
W=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005');N=W/'native';T=W/'temp'
B=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
V=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005')
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
receipt=json.loads(Path(a.base_receipt).read_text('utf8'));source=Path(a.base_native);apk=Path(a.base_apk)
assert receipt['allPackageEntriesVerified'] and receipt['sha256']==a.expected_base_sha==sha(apk)
assert not (W/'evidence/native-build.json').exists(), 'Already built; do not overwrite'
original=json.loads((source.parent/'evidence/native-build.json').read_text('utf8'))
originals={p.name:sha(p) for p in source.iterdir() if p.is_file()}
assert originals==original['overlaySources']
with zipfile.ZipFile(apk) as z,z.open('lib/arm64-v8a/libturbo_carousel.so') as f:
    apkSo=hashlib.file_digest(f,'sha256').hexdigest()
    assert apkSo==(a.base_apk_so_sha or original['soSHA256'])
led=json.loads((W/'evidence/led-tests.json').read_text('utf8'));assert led['passed']
changed={'magazine_shader.h','premium-magazine-led-android.glsl','native_neogeocd_square.h','neogeocd-square.glsl'}
for name in changed:assert sha(N/name)==led['sourceSHA256'][name]
for name in originals:
    if name not in changed:shutil.copy2(source/name,N/name)
assert (N/'station_game_details.h').exists() and (N/'station_game_panel_layout.h').exists()
assert sha(N/'collection_video_policy.h')==sha(V/'native/collection_video_policy.h')
assert sha(N/'video720_posters.h')==sha(V/'native/video720_posters.h')
os.environ['TEMP']=os.environ['TMP']=str(T)
cc=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe')
cmd=[cc,'--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so','-I',B,N/'native_carousel.cpp',B/'video720_posters.o',V/'neogeo_previews.o','-L',B,'-lc','-ldl','-llog','-o',W/'libturbo_carousel.so']
r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace')
(W/'evidence/android-build.log').write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-3000:]
final={p.name:sha(p) for p in N.iterdir() if p.is_file()}
assert {name for name in originals if originals[name]!=final[name]}==changed
record={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseReceipt':a.base_receipt,'baseAPK':str(apk),'baseSHA256':sha(apk),'baseNative':str(source),'baseSources':originals,'command':list(map(str,cmd)),
 'baseAPKNativeSHA256':apkSo,'baseSourceCompiledNativeSHA256':original['soSHA256'],'sourceSuccessorNotPackaged':apkSo!=original['soSHA256'],
 'changedSources':sorted(changed),'overlaySources':final,'soSHA256':sha(W/'libturbo_carousel.so'),'soBytes':(W/'libturbo_carousel.so').stat().st_size,'androidCompile':True,'r23LayoutPreserved':True,'r22VideosPreserved':True,'posterObjects':[{'path':str(x),'sha256':sha(x)} for x in (B/'video720_posters.o',V/'neogeo_previews.o')]}
(W/'evidence/native-build.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
print(json.dumps({'built':True,'soSHA256':record['soSHA256'],'base':record['baseSHA256']}),flush=True)
