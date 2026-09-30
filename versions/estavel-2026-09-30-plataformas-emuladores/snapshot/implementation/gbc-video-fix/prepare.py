from pathlib import Path
import sys,subprocess,shutil,hashlib,json,zipfile
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'gbc-video-fix';R.mkdir(exist_ok=True);B=R/'before';B.mkdir(exist_ok=True);(R/'tmp').mkdir(exist_ok=True)
SRC=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas\gc.mp4')
sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(P/'system-videos/tools'));import imageio_ffmpeg
dest=R/'720-gbc.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-nostdin','-y','-threads','1','-i',str(SRC),'-vf','scale=720:720:force_original_aspect_ratio=decrease:flags=lanczos,pad=720:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.2','-pix_fmt','yuv420p','-preset','fast','-crf','21','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','120','-bf','0','-movflags','+faststart',str(dest)],check=True)
header=P/'system_video720_assets.h'
if not (B/header.name).exists():shutil.copy2(header,B/header.name)
s=header.read_text(encoding='utf-8');line='{"Gameboy Color","turbo-system-videos/720-gbc.mp4"},'
if line not in s:
 assert s.count('\n};')==1;s=s.replace('\n};','\n'+line+'\n};');header.write_text(s,encoding='utf-8')
apk=P/'TurboramaStation-Plataformas-Organizadas.apk'
with zipfile.ZipFile(apk) as z:
 entries={n:sha(z.read(n)) for n in z.namelist() if not n.startswith('META-INF/')}
(B/'installed-apk-entry-hashes.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
for name in ['build-result.json','installed.json']:shutil.copy2(P/'video-stream-fix'/name,B/name)
shutil.copy2(Path(__file__),R/'prepare.py')
provenance={'platform_key':'Gameboy Color','source':str(SRC),'source_sha256':sha(SRC.read_bytes()),'asset':'turbo-system-videos/720-gbc.mp4','sha256':sha(dest.read_bytes()),'width':720,'height':720,'fps':60,'speed':1.0,'loop':True,'source_visually_confirmed':'GAME BOY COLOR','gamecube_asset_preserved':'turbo-system-videos/720-gc.mp4','note':'Current source gc.mp4 is Game Boy Color, as specified by owner; existing GameCube encoded clip is a different video. Do not regenerate GameCube from the current source gc.mp4.'}
(R/'media-manifest.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=(P/'video-stream-fix/package.py').read_text(encoding='utf-8').replace("R=P/'video-stream-fix'","R=P/'gbc-video-fix'")
s=s.replace("removed=set()", "replacements['assets/turbo-system-videos/720-gbc.mp4']=(R/'720-gbc.mp4').read_bytes()\nreplacements['assets/gbc-video-fix/media-manifest.json']=(R/'media-manifest.json').read_bytes()\nreplacements['assets/gbc-video-fix/source/prepare.py']=(R/'prepare.py').read_bytes()\nremoved=set()")
s=s.replace("if name=='assets/platform-layout-update/source/package.py':continue", "if name in ['assets/platform-layout-update/source/package.py','assets/platform-layout-update/source/system_video720_assets.h','lib/arm64-v8a/libturbo_carousel.so']:continue")
s=s.replace("'update':'", "'update':'Add Game Boy Color from owner gc.mp4; preserve distinct cached GameCube clip. ")
(R/'package.py').write_text(s,encoding='utf-8')
print(json.dumps(provenance,ensure_ascii=False,indent=2))
