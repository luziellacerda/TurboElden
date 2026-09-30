from pathlib import Path
import json,zipfile,hashlib,shutil,sys,subprocess,os,struct
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'focus-video-30';R.mkdir(exist_ok=True)
for name in ['before','source-media','media','tmp','classes','dex']:(R/name).mkdir(exist_ok=True)
B=R/'before';APK=P/'TurboramaStation-Plataformas-Organizadas.apk'
sha=lambda data:hashlib.sha256(data).hexdigest()
assert sha(APK.read_bytes())=='af9d76ba686a1e279b215ffd564946c1198d4258cd376f7f91505792f6c38053'
for f in [P/'native_system_video720.h',P/'system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java',P/'libturbo_carousel.so']:
 if not (B/f.name).exists():shutil.copy2(f,B/f.name)
for name in ['build-result.json','installed.json']:shutil.copy2(P/'gbc-video-fix'/name,B/name)
with zipfile.ZipFile(APK) as z:
 hashes={n:sha(z.read(n)) for n in z.namelist() if not n.startswith('META-INF/')}
 (B/'entry-hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
 (B/'classes9.dex').write_bytes(z.read('classes9.dex'))
 videos=[]
 for name in z.namelist():
  if name.startswith('assets/turbo-system-videos/') and name.endswith('.mp4'):
   source=R/'source-media'/Path(name).name;source.write_bytes(z.read(name));videos.append((name,source))

f=P/'native_system_video720.h';s=f.read_text(encoding='utf-8')
s=s.replace('// One 720p stream per clip. Retained GPU frames bridge decoder restarts with no green card.', '// One focused 720p30 loop; side cards draw retained frames from their own videos.')
s=s.replace(' int wantedCount=0,cursor=at<int>(p,0xf0),firstVisible=cursor,lastVisible=cursor;', ' int wantedCount=0,cursor=at<int>(p,0xf0),firstVisible=cursor,lastVisible=cursor;\n const char*focusedAsset=video720Asset(p,cursor);')
old='if((int)absolute((float)(painted[j].index-cursor))==distance)addWanted(video720Asset(p,painted[j].index),true);'
new='if((int)absolute((float)(painted[j].index-cursor))==distance)addWanted(video720Asset(p,painted[j].index),painted[j].index==cursor);'
assert old in s;s=s.replace(old,new)
anchor=' // Use remaining decoder slots for recently visited clips instead of tearing'
insert=''' // Pause the old focus before queuing a new start/resume on the Java worker.
 // A duplicate platform alias may share a decoder, but only its focused cell draws live.
 for(int i=0;i<video720SlotCount;i++){
  auto&v=video720Slots[i];
  if(v.visible&&(!focusedAsset||!v.asset||strcmp(v.asset,focusedAsset)!=0)){
   retainVideo720Frame(v);v.visible=false;
   if(v.texture){env->CallStaticVoidMethod(video720Class,video720Visibility,i,(jboolean)false);videoJniException(env);}
  }
 }
 static const char*loggedFocus;
 if(loggedFocus!=focusedAsset){loggedFocus=focusedAsset;__android_log_print(4,"TurboCarousel","VIDEO focus-only 720p30: %s",focusedAsset?focusedAsset:"none");}
'''
assert anchor in s;s=s.replace(anchor,insert+anchor)
old='for(int i=0;i<video720SlotCount;i++)if(result[i]>0&&video720Slots[i].asset&&strcmp(video720Slots[i].asset,asset)==0){live=i;break;}'
new='for(int i=0;i<video720SlotCount;i++)if(r.index==cursor&&result[i]>0&&video720Slots[i].asset&&strcmp(video720Slots[i].asset,asset)==0){live=i;break;}'
assert old in s;s=s.replace(old,new)
s=s.replace('// Visible cells always have priority.', '// Focused and visible preview cells always have priority.')
f.write_text(s,encoding='utf-8')
java=P/'system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java';s=java.read_text(encoding='utf-8')
s=s.replace('One 720p source per clip; neighbouring offscreen clips stay prepared and paused.', 'One focused 720p30 loop; all other clips prepare a video frame and remain paused.')
s=s.replace('areSizeAndRateSupported(720,720,60)', 'areSizeAndRateSupported(720,720,30)')
s=s.replace('Single-source 720p60 capacity=', 'Focus-only 720p30 capacity=')
s=s.replace('720p loop ready at retained position: ', '720p30 focused/preview video ready: ')
java.write_text(s,encoding='utf-8')

sys.path.insert(0,str(P/'system-videos/tools'));import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();manifest=[]
for index,(name,src) in enumerate(videos,1):
 dest=R/'media'/src.name
 subprocess.run([ff,'-hide_banner','-loglevel','error','-nostdin','-y','-threads','1','-i',str(src),'-vf','fps=30','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','19','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',str(dest)],check=True)
 reader=imageio_ffmpeg.read_frames(str(src));before=next(reader);reader.close()
 reader=imageio_ffmpeg.read_frames(str(dest));after=next(reader);reader.close()
 assert tuple(after['size'])==(720,720) and abs(after['fps']-30)<0.01
 assert abs(before['duration']-after['duration'])<=0.07,(name,before['duration'],after['duration'])
 manifest.append({'asset':name,'source_sha256':sha(src.read_bytes()),'sha256':sha(dest.read_bytes()),'source_duration':before['duration'],'duration':after['duration'],'width':720,'height':720,'fps':30,'speed':1.0})
 print(f'Converted {index}/{len(videos)}: {src.name}',flush=True)
(R/'media-manifest.json').write_text(json.dumps({'scope':'only focused cell loops; side cells retain decoded video frames','fps':30,'speed':1.0,'resolution':[720,720],'videos':manifest},indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(__file__),R/'prepare.py')
print('Prepared focus-only sources and all 720p30 videos',flush=True)
