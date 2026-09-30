from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-xbox-pce-refresh'
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
sys.path.insert(0,str(P/'system-videos/tools'));import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
folder=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=[]
for key,file,slug in [('Super Nintendo - BR','snesBR.mp4','snesbr'),('MegaDrive - BR','megadriveBR.mp4','megadrivebr'),('xbox360','xbox360.mp4','xbox360'),('xbox','xbox.mp4','xbox')]:
 src=folder/file;dst=R/'media'/('720-'+slug+'.mp4')
 subprocess.run([ff,'-hide_banner','-loglevel','error','-nostdin','-y','-i',str(src),'-vf','scale=720:720:force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','19','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',str(dst)],check=True)
 a=imageio_ffmpeg.read_frames(str(src));before=next(a);a.close();a=imageio_ffmpeg.read_frames(str(dst));after=next(a);a.close()
 assert tuple(after['size'])==(720,720) and abs(after['fps']-30)<.01 and abs(before['duration']-after['duration'])<.08
 manifest.append({'key':key,'source':str(src),'source_sha256':sha(src),'asset':'assets/turbo-system-videos/'+dst.name,'sha256':sha(dst),'source_duration':before['duration'],'duration':after['duration'],'fps':30,'size':[720,720],'speed':1,'loop':True,'focus_only':True})
 print('Prepared',file,flush=True)
(R/'media-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
shutil.copy2(__file__,R/'refresh_platform_media.py')
