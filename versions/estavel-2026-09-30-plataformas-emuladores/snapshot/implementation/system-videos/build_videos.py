from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,zipfile
R=Path(__file__).resolve().parent;P=R.parent
ap=argparse.ArgumentParser()
ap.add_argument('--base-apk',type=Path,default=Path(r'E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira\TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk'))
ap.add_argument('--base-sha256',default='54681d24d4ae912c0d081b276064264f95ad5e1d41e4e2851d2daa87169c4257')
ap.add_argument('--output',type=Path,default=P/'TurboramaStation-playlist-retro.apk')
a=ap.parse_args();BASE=a.base_apk;APK=a.output
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
SDK=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())==a.base_sha256,'Unexpected base APK'
for folder in ['tmp','classes','dex']:(R/folder).mkdir(exist_ok=True)
def run(*args):subprocess.run(list(map(str,args)),check=True)
# Only generated Java classes in this build directory.
for stale in (R/'classes').rglob('*.class'):stale.unlink()
run(JAVA.with_name('javac.exe'),'-encoding','UTF-8','-source','8','-target','8','-cp',SDK,'-d',R/'classes',R/'java/org/emulationstation/frontend/SystemCardVideo720.java',R/'java/org/emulationstation/frontend/MenuRetroMusic.java')
classes=sorted((R/'classes').rglob('*.class'));assert classes
run(JAVA,'-Djava.io.tmpdir='+str(R/'tmp'),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',SDK,'--output',R/'dex',*classes)
module='lib/arm64-v8a/libturbo_carousel.so'
unsigned=R/'videos-unsigned.apk';aligned=R/'videos-aligned.apk'
manifest=json.loads((R/'videos-manifest.json').read_text(encoding='utf-8'))
assert all(x['slug'].startswith('720-') for x in manifest['assets']), 'Only 720p videos are allowed'
assert all(Path(x['source']).resolve().parent==Path(manifest['source_directory']).resolve() and not x.get('generated_from_art') for x in manifest['assets']), 'Only the requested source folder is permitted'
expected_assets={'assets/turbo-system-videos/'+x['slug']+'.mp4':R/'assets'/(x['slug']+'.mp4') for x in manifest['assets']}
expected_assets['assets/turbo-system-videos/manifest.json']=R/'videos-manifest.json'
music_root=P/'retro-playlist'
music=json.loads((music_root/'playlist-manifest.json').read_text(encoding='utf-8'))
for track in music['tracks']:
 assert track['asset'].startswith('turbo-retro-music/') and '..' not in track['asset']
 expected_assets['assets/'+track['asset']]=music_root/'assets'/Path(track['asset']).name
expected_assets['assets/turbo-retro-music/playlist.json']=music_root/'assets/playlist.json'
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
 dex_numbers=[int(m.group(1) or 1) for n in z.namelist() if (m:=re.fullmatch(r'classes(\d*)\.dex',n))]
 helper_dex='classes'+str(max(dex_numbers)+1)+'.dex'
 for info in z.infolist():
  if info.filename.startswith('META-INF/'):continue
  out.writestr(info,(P/'libturbo_carousel.so').read_bytes() if info.filename==module else z.read(info.filename))
 out.write(R/'dex/classes.dex',helper_dex,compress_type=zipfile.ZIP_STORED)
 for name,path in expected_assets.items():out.write(path,name,compress_type=zipfile.ZIP_STORED)
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink() # Our exact generated intermediate; keep peak E: usage below two APKs.
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',APK,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',APK)
with zipfile.ZipFile(BASE) as before,zipfile.ZipFile(APK) as after:
 old={n for n in before.namelist() if not n.startswith('META-INF/')};new={n for n in after.namelist() if not n.startswith('META-INF/')}
 changed=sorted(n for n in old&new if before.read(n)!=after.read(n))
 added=sorted(new-old);removed=sorted(old-new)
 assert not removed and added==sorted([helper_dex,*expected_assets]),(added,removed)
 assert all(n==module for n in changed),changed
 assert all(after.getinfo(n).compress_type==zipfile.ZIP_STORED for n in expected_assets),'openFd requires stored video assets'
 for x in manifest['assets']:assert sha(after.read('assets/turbo-system-videos/'+x['slug']+'.mp4'))==x['sha256']
 for track in music['tracks']:assert sha(after.read('assets/'+track['asset']))==track['sha256']
report=dict(music=dict(track_count=len(music['tracks']),bytes=sum(t['bytes'] for t in music['tracks']),mode='one streaming player; interleaved sequential repeat; pauses/releases for emulation and Activity pause; respects audio focus',control='original StoreMusic toggle; media volume buttons; enabled once on feature installation',source='owner-provided local MP3s, unchanged',track_titles=[t['game']+' - '+t['title'] for t in music['tracks']]),video_preload=manifest['preload'],led='brighter focused native LED: base rim opacity 0.72, stronger colored halo and hot head, longer fading tail; immediate focus visibility; 3.8s cycle; exact palette; one ring draw',apk=str(APK),sha256=sha(APK.read_bytes()),bytes=APK.stat().st_size,base=str(BASE),base_sha256=a.base_sha256,stable_tag='estavel-2026-09-29-camera-traseira',stable_git_commit='95d244bcea95647236bea335c41b46afe15674bf',historical_engine_commit='6727ab7',changed=changed,added=added,removed=removed,original_dex_identical=True,all_emulator_engines_identical=True,login_and_icon_identical=True,native_module_sha256=sha((P/'libturbo_carousel.so').read_bytes()),mapped_platforms=len(manifest['mapping']),unique_videos=len(manifest['clips']),atlas_files=0,high_resolution_videos=len(manifest['clips']),missing_videos=manifest['missing'],playback_speed=1.0,requested_video_quality=manifest['requested_quality'],generated_platforms=manifest['generated_platforms'],video_mode='one 720p60 stream; visible/previous-neighbour priority; retain GPU video frames across player eviction; resume prior position; no green flash, no photo assets, no atlas',aircraft='shared 28.65 degree diagonal rear-view frame and vanishing point with clouds/stars; corrected screen-right yaw sign; reduced camera-depth excursion; coherent constant forward travel, softer advected volume exhaust',video_bytes=sum(x['bytes'] for x in manifest['assets']),installed=False,visual_check_performed=False,performance_measurement_performed=False)
(R/'build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
