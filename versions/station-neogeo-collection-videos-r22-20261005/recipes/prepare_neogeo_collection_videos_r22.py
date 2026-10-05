"""Prepare only the three user-supplied Neo Geo collection clips; no APK mutation."""
from pathlib import Path
import hashlib, json, shutil, subprocess

W = Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005')
SOURCE = Path(r"G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas\Sele;'ao")
MAPPING = [('fatalfury.mp4', 'fatalfury'), ('megal slug.mp4', 'metalslug'), ('samurayshodow.mp4', 'samuraishodown')]
FF = shutil.which('ffmpeg'); PROBE = shutil.which('ffprobe')
assert FF and PROBE
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def run(args):
    return subprocess.run([str(x) for x in args], check=True, capture_output=True).stdout
def probe(p):
    return json.loads(run([PROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', p]))
W.mkdir(exist_ok=False)
for name in ['media', 'previews', 'evidence', 'native']: (W/name).mkdir()
assembly = ['.section .rodata.station_neogeo_collection_previews,"a",%progbits']
rows=[]
for name, key in MAPPING:
    src=SOURCE/name; original=probe(src)
    source_stream=next(s for s in original['streams'] if s['codec_type']=='video' and not s.get('disposition',{}).get('attached_pic'))
    assert (source_stream['width'], source_stream['height'])==(960,960)
    dst=W/'media'/('720-collection-neogeo-'+key+'.mp4')
    run([FF,'-nostdin','-hide_banner','-loglevel','error','-i',src,'-map','0:V:0',
         '-vf','scale=720:720:flags=lanczos,setsar=1,fps=30','-an','-sn','-dn',
         '-map_metadata','-1','-c:v','libx264','-profile:v','baseline','-level:v','3.1',
         '-pix_fmt','yuv420p','-preset','fast','-crf','20','-maxrate','3500k',
         '-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',dst])
    raw=W/'previews'/(key+'.rgb565')
    run([FF,'-nostdin','-hide_banner','-loglevel','error','-i',dst,'-map','0:V:0','-frames:v','1','-vf','vflip','-pix_fmt','rgb565le','-f','rawvideo',raw])
    run([FF,'-nostdin','-hide_banner','-loglevel','error','-i',dst,'-map','0:V:0','-frames:v','1',W/'previews'/(key+'.png')])
    assert raw.stat().st_size==720*720*2
    # Decode every frame, checking for corrupt packets, before accepting the clip.
    run([FF,'-nostdin','-hide_banner','-loglevel','error','-xerror','-i',dst,'-map','0:V:0','-f','null','-'])
    result=probe(dst); assert len(result['streams'])==1
    stream=result['streams'][0]
    assert (stream['width'],stream['height'],stream['r_frame_rate'],stream['pix_fmt'])==(720,720,'30/1','yuv420p')
    assert stream['codec_name']=='h264' and stream['has_b_frames']==0
    assert abs(float(stream['duration'])-float(source_stream['duration']))<=1/30
    symbol='station_neogeo_collection_'+key
    assembly += ['.balign 16','.global '+symbol,'.hidden '+symbol,'.type '+symbol+',%object',symbol+':','.incbin "'+raw.as_posix()+'"','.size '+symbol+',.-'+symbol]
    rows.append({'source':str(src),'sourceSha256':sha(src),'sourceProbe':original,
                 'asset':'assets/turbo-system-videos/'+dst.name,'output':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size,
                 'preview':str(raw),'previewSha256':sha(raw),'symbol':symbol,'probe':result,
                 'sourceFps':24,'outputFps':30,'speed':1,'noCrop':True,'noStretch':True,'audio':False,'allFramesDecoded':True})
    print('Prepared',name,dst.stat().st_size,flush=True)
asm=W/'neogeo_previews.S';asm.write_text('\n'.join(assembly)+'\n','utf8')
run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','-c',asm,'-o',W/'neogeo_previews.o'])
(W/'media-manifest.json').write_text(json.dumps({'videos':rows,'objectSha256':sha(W/'neogeo_previews.o'),'sourceFrameRateNote':'24 fps original frames sampled to 30 fps without changing playback duration; no synthetic motion interpolation','onlyFocusedPlays':True,'geometry':'720x720 square original cell','preparedOnly':True},indent=2)+'\n','utf8')
print('Prepared media only:',W)
