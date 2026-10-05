from pathlib import Path
import shutil, subprocess, hashlib, json, imageio_ffmpeg
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004'); N=R/'native'; W=R/'visual-r14'; OLD=R/'collection-video-r13'
W.mkdir(exist_ok=False); (W/'before').mkdir(); (W/'media').mkdir(); (W/'previews').mkdir()
for name in ['native_skin.h','native_game_actions.h','native_action_motion.h','native_netplay.h','native_formation.h','native_folders.h','video720_posters.o']:
 shutil.copyfile(N/name,W/'before'/name)
def edit(name,a,b):
 p=N/name;s=p.read_text('utf8');assert s.count(a)==1,(name,a);p.write_text(s.replace(a,b),'utf8',newline='\n')
edit('native_formation.h',' if(folderMode){int index=(int)(at<float>(p,0xf4)+d+.5f);result.h=result.w/folderVideoAspect(p,index);}\n','')
edit('native_folders.h','static float folderVideoAspect(void*p,int index){const auto*v=folderVideo(p,index);return v?v->aspect:1.f;}\n','')
ff=imageio_ffmpeg.get_ffmpeg_exe(); rows=[]; asm=['.section .rodata.station_collection_previews,"a",%progbits']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((OLD/'media-manifest.json').read_text('utf8'))
for index,item in enumerate(old['videos']):
 src=Path(item['source']);assert sha(src)==item['sourceSha256']
 name=Path(item['asset']).name;dst=W/'media'/name;key=name.removeprefix('720-collection-snes-').removesuffix('.mp4')
 if item['displayAspect']==1:
  shutil.copyfile(OLD/'media'/name,dst);graph='source already square; unchanged R13 bytes'
 else:
  # Main frame retains ALL source pixels and original aspect. Only the decorative
  # backdrop is resampled to a square and blurred, offline, with no extra decoder.
  graph='[0:V:0]fps=30,setsar=1,split=2[bg][fg];[bg]scale=360:360,boxblur=20:2,eq=brightness=-0.13:saturation=0.65,scale=720:720,format=yuv444p[b];[fg]scale=720:-1,format=yuv444p[f];[b][f]overlay=0:(H-h)/2:format=yuv444,format=yuv420p[out]'
  args=[ff,'-nostdin','-hide_banner','-loglevel','error','-i',str(src),'-filter_complex',graph,'-map','[out]','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','20','-maxrate','3500k','-bufsize','7000k','-threads','2','-filter_complex_threads','1','-g','60','-bf','0','-movflags','+faststart',str(dst)]
  subprocess.run(args,check=True)
 raw=W/'previews'/(key+'.rgb565')
 subprocess.run([ff,'-nostdin','-hide_banner','-loglevel','error','-i',str(dst),'-frames:v','1','-vf','vflip','-pix_fmt','rgb565le','-f','rawvideo',str(raw)],check=True)
 subprocess.run([ff,'-nostdin','-hide_banner','-loglevel','error','-i',str(dst),'-frames:v','1',str(W/(key+'.png'))],check=True)
 assert raw.stat().st_size==720*720*2
 symbol='station_collection_video_'+str(index)
 asm+=['.balign 16','.global '+symbol,'.hidden '+symbol,'.type '+symbol+',%object',symbol+':','.incbin "'+raw.as_posix()+'"','.size '+symbol+',.-'+symbol]
 rows.append(dict(item,sha256=sha(dst),previewSha256=sha(raw),sourceAspect=item['displayAspect'],displayAspect=1,foreground='contain, uncropped, original aspect',background='offline blurred copy' if item['displayAspect']!=1 else 'original',filter=graph))
 print('Prepared full-frame square cell',key,flush=True)
(W/'collection_previews.S').write_text('\n'.join(asm)+'\n','utf8')
subprocess.run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','-c',str(W/'collection_previews.S'),'-o',str(W/'collection_previews.o')],check=True)
subprocess.run([r'C:\Program Files\LLVM\bin\ld.lld.exe','-r',str(OLD/'before/video720_posters.o'),str(W/'collection_previews.o'),'-o',str(N/'video720_posters.o')],check=True)
(W/'media-manifest.json').write_text(json.dumps({'videos':rows,'originalCellGeometryRestored':True,'allGamesUsesPlatformVideo':True,'onlyFocusedPlays':True,'offlineBackground':True},indent=2)+'\n','utf8')
