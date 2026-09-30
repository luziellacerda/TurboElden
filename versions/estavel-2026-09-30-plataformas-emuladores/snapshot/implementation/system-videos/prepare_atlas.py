from pathlib import Path
import json,sys,subprocess,hashlib
R=Path(__file__).resolve().parent;P=R.parent
sys.path.insert(0,str(R/'tools'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
THEME=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx')
rows=json.loads((P/'theme-infos-mapping.json').read_text(encoding='utf-8'))
arts={x['chave_filtro']:x['capas'][0] for x in json.loads((P.parent/'mapa-sistemas-agrupados.json').read_text(encoding='utf-8'))}
removed={'colecovision','fds','gameandwatch','Gameboy','Odyssey 2'}
clips={};mapping=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):subprocess.run([ff,'-hide_banner','-loglevel','error','-nostdin','-y',*args],check=True)
for row in rows:
 if row['key'] in removed:continue
 slug={'arcade':'mame'}.get(row['folder'],row['folder'])
 mapping.append({'key':row['key'],'slug':slug})
 if slug in clips:continue
 src=THEME/'_theme_inc/images/caratulas'/(slug+'.mp4')
 if not src.exists():src=THEME/'_theme_inc/videos/tela1'/(slug+'.mp4')
 generated=not src.exists()
 dest=R/'assets'/(slug+'.mp4')
 if generated:src=Path(arts[row['key']])
 if not dest.exists():
  if generated:
   # Continuous, periodic camera movement; retains the correct platform's art.
   filt="scale=600:600,zoompan=z='1.05+0.035*sin(2*PI*on/144)':x='iw/2-iw/zoom/2+8*sin(2*PI*on/144)':y='ih/2-ih/zoom/2+6*cos(2*PI*on/144)':d=144:s=480x480:fps=24,setsar=1"
   inp=['-i',str(src),'-vf',filt,'-t','6']
  else:inp=['-threads','1','-i',str(src),'-vf','scale=480:480:force_original_aspect_ratio=decrease,pad=480:480:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24']
  run([*inp,'-an','-c:v','libx264','-profile:v','baseline','-pix_fmt','yuv420p','-crf','24','-preset','fast','-threads','2','-g','48','-bf','0','-movflags','+faststart',str(dest)])
 clips[slug]={'slug':slug,'source':str(src),'source_sha256':sha(src),'generated_from_art':generated,'clip':str(dest)}
 print('Clip '+slug+(' (animated artwork)' if generated else ''),flush=True)
slugs=sorted(clips);assert len(slugs)==35,len(slugs)
cols,rowsn=7,5
for item in mapping:item['tile']=slugs.index(item['slug'])
header='// Shared video atlas: every visible native card samples its own tile.\nstruct SystemVideoDef { const char* key; int tile; };\nstatic constexpr int systemVideoColumns=7,systemVideoRows=5;\nstatic const SystemVideoDef systemVideos[]={\n'
header+=''.join('{'+json.dumps(x['key'])+','+str(x['tile'])+'},\n' for x in mapping)+'};\n'
(P/'system_videos.h').write_text(header,encoding='utf-8')
args=[];filters=[]
for i,slug in enumerate(slugs):
 args+=['-stream_loop','-1','-threads','1','-i',str(R/'assets'/(slug+'.mp4'))]
 filters.append(f'[{i}:v]fps=18,scale=240:240,setsar=1,setpts=PTS-STARTPTS[v{i}]')
layout='|'.join(f'{(i%cols)*240}_{(i//cols)*240}' for i in range(len(slugs)))
filters.append(''.join(f'[v{i}]' for i in range(len(slugs)))+f'xstack=inputs={len(slugs)}:layout={layout}[atlas]')
(R/'atlas-filter.txt').write_text(';\n'.join(filters),encoding='utf-8')
hd=R/'assets/atlas-hd.mp4';lite=R/'assets/atlas-lite.mp4'
run([*args,'-filter_complex_threads','2','-filter_complex_script',str(R/'atlas-filter.txt'),'-map','[atlas]','-t','24','-an','-c:v','libx264','-profile:v','baseline','-level:v','4.0','-pix_fmt','yuv420p','-preset','fast','-crf','23','-maxrate','6000k','-bufsize','12000k','-threads','2','-g','36','-bf','0','-movflags','+faststart',str(hd)])
print('Atlas HD ready',flush=True)
run(['-threads','1','-i',str(hd),'-vf','scale=1120:800','-an','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','24','-maxrate','3000k','-bufsize','6000k','-threads','2','-g','36','-bf','0','-movflags','+faststart',str(lite)])
assets=[{'slug':p.stem,'sha256':sha(p),'bytes':p.stat().st_size,'width':w,'height':h,'fps':18} for p,w,h in [(hd,1680,1200),(lite,1120,800)]]
manifest={'mapping':mapping,'clips':[clips[s] for s in slugs],'assets':assets,'atlas_columns':7,'atlas_rows':5,'loop_seconds':24,'playback':'all visible system cards simultaneously; one muted looping atlas decoder; no selection restart','generated_platforms':[x['slug'] for x in clips.values() if x['generated_from_art']],'missing':[]}
(R/'videos-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'platforms':len(mapping),'clips':len(clips),'generated':manifest['generated_platforms'],'atlas_bytes':sum(x['bytes'] for x in assets)}),flush=True)
