from pathlib import Path
import json,hashlib,subprocess,sys
R=Path(__file__).resolve().parent;P=R.parent
SOURCE=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas')
sys.path.insert(0,str(R/'tools'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
old=json.loads((R/'videos-manifest.json').read_text(encoding='utf-8'))
old_assets={x['slug']:x for x in old['assets']};old_clips={x['slug']:x for x in old['clips']}
removed={'colecovision','fds','gameandwatch','Gameboy','Odyssey 2'}
rows=json.loads((P/'theme-infos-mapping.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mapping=[];missing=[];clips={};assets={}
for row in rows:
 if row['key'] in removed:continue
 slug={'arcade':'mame'}.get(row['folder'],row['folder']);src=SOURCE/(slug+'.mp4');dest=R/'assets'/('720-'+slug+'.mp4')
 if not src.is_file():missing.append({'key':row['key'],'expected':str(src),'state':'awaiting owner file; no substitute video'});continue
 mapping.append({'key':row['key'],'slug':slug})
 if slug in clips:continue
 source_sha=sha(src)
 cache=old_assets.get('720-'+slug);prior=old_clips.get(slug)
 valid=cache and prior and prior.get('source_sha256')==source_sha and Path(cache['source']).resolve()==src.resolve() and dest.exists() and sha(dest)==cache['sha256']
 if not valid:
  subprocess.run([ff,'-hide_banner','-loglevel','error','-nostdin','-y','-threads','1','-i',str(src),'-vf','scale=720:720:force_original_aspect_ratio=decrease:flags=lanczos,pad=720:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.2','-pix_fmt','yuv420p','-preset','fast','-crf','21','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','120','-bf','0','-movflags','+faststart',str(dest)],check=True)
 clips[slug]={'slug':slug,'source':str(src),'source_sha256':source_sha,'generated_from_art':False,'clip':str(dest)}
 assets[slug]={'slug':'720-'+slug,'width':720,'height':720,'fps':60,'sha256':sha(dest),'bytes':dest.stat().st_size,'source':str(src),'source_sha256':source_sha,'generated_from_art':False,'frame_conversion':'source timestamps retained, 60fps output repeats frames when original fps is lower; speed 1.0'}
header='// Only files from the exact owner-specified caratulas directory.\nstruct SystemVideo720Def {const char* key;const char* asset;};\nstatic const SystemVideo720Def systemVideo720Definitions[]={\n'
header+=''.join('{'+json.dumps(x['key'])+','+json.dumps('turbo-system-videos/720-'+x['slug']+'.mp4')+'},\n' for x in mapping)+'};\n'
(P/'system_video720_assets.h').write_text(header,encoding='utf-8')
m={'mapping':mapping,'clips':list(clips.values()),'assets':list(assets.values()),'source_directory':str(SOURCE),'source_policy':'Only MP4 files in the exact owner-specified folder','playback':'one 720p60 video per visible mapped card; speed 1.0; native continuous looping; no atlas or alternate source','atlas_removed':True,'generated_platforms':[],'missing':missing,'requested_quality':{'width':720,'height':720,'fps':60,'scope':'visible system cards with a source file in the requested folder','playback_speed':1.0,'loop':True,'decoding':'one MediaPlayer per unique visible clip; async prepare, native loop, release offscreen','source_fps_note':'Converted to 60fps without changing source speed; repeats frames from lower-rate sources'}}
if 'preload' in old:m['preload']=old['preload']
(R/'videos-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mapped':len(mapping),'videos':len(clips),'missing':[x['key'] for x in missing]},ensure_ascii=False))
