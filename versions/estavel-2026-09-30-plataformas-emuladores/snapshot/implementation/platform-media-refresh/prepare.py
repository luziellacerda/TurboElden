from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,zipfile

P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
R=P/'platform-media-refresh'; R.mkdir(exist_ok=True)
for d in ['before','media','previews','tmp']:(R/d).mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert digest(BASE)=='2f93a8ad604f6060d3b26adde507698dacf8ea999e0b507700417599410b58c7'
for name in ['native_carousel.cpp','system_video720_assets.h','libturbo_carousel.so']:
    dest=R/'before'/name
    assert not dest.exists(), 'Preparation already started; inspect the existing revision instead of overwriting its backup.'
    shutil.copy2(P/name,dest)
for name in ['installed.json','build-result.json']:shutil.copy2(P/'focus-video-30'/name,R/'before'/name)
shutil.copy2(P/'stable-design/active-profile.json',R/'before/active-profile.json')
with zipfile.ZipFile(BASE) as z:
    hashes={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.startswith('META-INF/')}
    (R/'before/entry-hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    (R/'before/720-xbox360.mp4').write_bytes(z.read('assets/turbo-system-videos/720-xbox360.mp4'))
sys.path.insert(0,str(P/'system-videos/tools'));import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
folder=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas')
manifest=[]
for key,filename,slug in [('xbox360','xbox360.mp4','xbox360'),('Pc Engine','pc egine.mp4','pcengine'),('Pc Engine cd','pc egine cd.mp4','pcenginecd')]:
    src=folder/filename; dest=R/'media'/('720-'+slug+'.mp4')
    subprocess.run([ff,'-hide_banner','-loglevel','error','-nostdin','-y','-i',str(src),'-vf','scale=720:720:force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','19','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',str(dest)],check=True)
    reader=imageio_ffmpeg.read_frames(str(src));before=next(reader);reader.close()
    reader=imageio_ffmpeg.read_frames(str(dest));after=next(reader);reader.close()
    if tuple(after['size'])!=(720,720) or abs(after['fps']-30)>0.01 or abs(before['duration']-after['duration'])>0.08:raise RuntimeError('Unexpected media conversion metadata')
    subprocess.run([ff,'-hide_banner','-loglevel','error','-nostdin','-y','-ss','1','-i',str(dest),'-frames:v','1',str(R/'previews'/(slug+'.png'))],check=True)
    manifest.append({'key':key,'source':str(src),'source_sha256':digest(src),'source_size':before['size'],'source_fps':before['fps'],'source_duration':before['duration'],'duration':after['duration'],'asset':'assets/turbo-system-videos/'+dest.name,'sha256':digest(dest),'width':720,'height':720,'fps':30,'speed':1.0})
    print('Converted '+filename,flush=True)
(R/'media-manifest.json').write_text(json.dumps({'removed_platforms':['atari7800','supergrafx'],'focus_only':True,'loop':True,'videos':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(__file__),R/'prepare.py')
print('Media ready for visual inspection; sources not modified yet.',flush=True)
