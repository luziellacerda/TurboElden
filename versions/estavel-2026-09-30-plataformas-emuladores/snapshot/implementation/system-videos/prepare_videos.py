from pathlib import Path
import sys,json,subprocess,hashlib
R=Path(__file__).resolve().parent;P=R.parent
sys.path.insert(0,str(R/'tools'))
import imageio_ffmpeg
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
SOURCE=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas')
removed={'colecovision','fds','gameandwatch','Gameboy','Odyssey 2'}
rows=json.loads((P/'theme-infos-mapping.json').read_text(encoding='utf-8'))
mapping=[];missing=[]
for row in rows:
 if row['key'] in removed:continue
 slug={'arcade':'mame'}.get(row['folder'],row['folder'])
 if (SOURCE/(slug+'.mp4')).is_file():mapping.append({'key':row['key'],'slug':slug,'asset':'turbo-system-videos/'+slug+'.mp4'})
 else:missing.append({'key':row['key'],'expected':str(SOURCE/(slug+'.mp4')),'behavior':'preserve static system cover'})
assets=[]
for slug in sorted({x['slug'] for x in mapping}):
 src=SOURCE/(slug+'.mp4');dest=R/'assets'/(slug+'.mp4')
 args=[ffmpeg,'-hide_banner','-loglevel','error','-nostdin','-y','-i',str(src),'-map','0:v:0','-an','-sn','-dn','-vf','scale=480:480:force_original_aspect_ratio=decrease,pad=480:480:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24','-c:v','libx264','-profile:v','baseline','-level:v','3.0','-pix_fmt','yuv420p','-preset','medium','-crf','24','-maxrate','650k','-bufsize','1300k','-g','48','-bf','0','-threads','2','-movflags','+faststart',str(dest)]
 subprocess.run(args,check=True)
 assets.append({'slug':slug,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'format':'H.264 baseline, 480x480, 24 fps, video only'})
 print('Prepared '+slug,flush=True)
manifest={'source_directory':str(SOURCE),'source_video_count':len(list(SOURCE.glob('*.mp4'))),'mapping':mapping,'missing':missing,'assets':assets,'playback':'selected platform only; static covers on neighbours and missing/failed videos'}
(R/'videos-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
header='struct SystemVideoDef { const char* key; const char* asset; };\nstatic const SystemVideoDef systemVideos[]={\n'
header+=''.join('{'+json.dumps(x['key'])+','+json.dumps(x['asset'])+'},\n' for x in mapping)+'};\n'
(P/'system_videos.h').write_text(header,encoding='utf-8')
print(json.dumps({'mapped_platforms':len(mapping),'unique_clips':len(assets),'missing':missing,'bytes':sum(x['bytes'] for x in assets)},ensure_ascii=False))
