"""Build R69 over the verified R68 tree; generated media and temporary files stay on E:."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess

snapshot=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--output',default=r'E:\ESTUDO APK\work\station-collection-media-r69-20261007-final')
a=p.parse_args();work=Path(a.output).resolve()
base=Path(r'E:\ESTUDO APK\work\station-collection-corners-r68-20261007-final')
assert work.drive.upper()=='E:' and not work.exists()
receipt=json.loads((base/'evidence/build.json').read_text('utf8'))
mapping=json.loads((snapshot/'mapping.json').read_text('utf8'))
ffmpeg,ffprobe=shutil.which('ffmpeg'),shutil.which('ffprobe')
assert ffmpeg and ffprobe
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name,h in receipt['nativeSources'].items():assert sha(base/'native'/name)==h,name
assert sha(base/'libturbo_carousel.so')==receipt['nativeSHA256']
for row in mapping['videos']:
 source=Path(row.get('sourceDirectory',mapping['sourceDirectory']))/row['file']
 assert sha(source)==row['sourceSha256'],row['file']
assert shutil.disk_usage(work.parent).free>4*1024**3
work.mkdir()
for folder in ['native','temp','tests','media','frames','evidence']:(work/folder).mkdir()
env=dict(os.environ,TEMP=str(work/'temp'),TMP=str(work/'temp'))
for name in receipt['nativeSources']:shutil.copyfile(base/'native'/name,work/'native'/name)
for source in (snapshot/'native').iterdir():shutil.copyfile(source,work/'native'/source.name)
current={p.name:sha(p) for p in (work/'native').iterdir() if p.is_file()}
changed=sorted(name for name,h in receipt['nativeSources'].items() if current[name]!=h)
assert changed==sorted(['native_formation.h','native_system_video720.h','collection_corner_policy.h','collection_video_policy.h','video720_posters.h']),changed
assert set(current)==set(receipt['nativeSources'])
def run(cmd,label):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,env=env)
 (work/'evidence'/(label+'.log')).write_bytes(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(label+': '+r.stderr.decode('utf8','replace')[-2000:])
 return r.stdout.decode('utf8','replace')
def probe(path,label):
 return json.loads(run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',path],label))
host=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
run([host,'-std=c++17','-Wall','-Wextra','-Werror','-I',work/'native',snapshot/'tests/collection_corners.cpp','-o',work/'tests/corners.exe'],'corners-compile')
result=run([work/'tests/corners.exe'],'corners-test');assert 'PASS 66 ' in result
formation=(work/'native/native_formation.h').read_text('utf8')
wiring=['r.allGames=collectionAllGames(index);','stationCollectionCorners::allGamesKind(folderMeta[index].kind)',
 'mappingAllGames=r.allGames;mappingCover=true;','mappingCover=false;mappingAllGames=false;',
 'roundedQuad(q,src,dst,mappingCover&&mappingAllGames);','roundedQuad(vertices,src,dst,mappingAllGames);',
 'cornerRadius(r.w,r.h,r.allGames)']
for statement in wiring:assert statement in formation,statement
assert 'roundedQuad(q,4,5,r.allGames);' in (work/'native/native_system_video720.h').read_text('utf8')
assert 'roundedCoverFill(' in (work/'native/native_skin.h').read_text('utf8')
one_decoder=snapshot.parent/'station-current-r55-20261006/tests/native/test_video_policy.cpp'
run([host,'-std=c++17','-Wall','-Wextra','-I',work/'native',one_decoder,'-o',work/'tests/decoder.exe'],'decoder-compile')
run([work/'tests/decoder.exe'],'decoder-test')
print(result.strip(),flush=True)
assembly=['.section .rodata.station_collections_r69,"a",%progbits'];media=[]
for row in mapping['videos']:
 source=Path(row.get('sourceDirectory',mapping['sourceDirectory']))/row['file']
 original=probe(source,'source-'+row['key'])
 stream=next(s for s in original['streams'] if s['codec_type']=='video' and not s.get('disposition',{}).get('attached_pic'))
 assert stream['width']==stream['height'], 'Preserve full aspect: inspect non-square source'
 output=work/'media'/Path(row['asset']).name
 run([ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-i',source,'-map','0:V:0',
  '-vf','scale=720:720:flags=lanczos,setsar=1,fps=30','-an','-sn','-dn','-map_metadata','-1',
  '-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast',
  '-crf','20','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',output],'encode-'+row['key'])
 outprobe=probe(output,'probe-'+row['key']);assert len(outprobe['streams'])==1
 v=outprobe['streams'][0]
 assert (v['codec_type'],v['codec_name'],v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'],v['has_b_frames'])==('video','h264',720,720,'30/1','yuv420p',0)
 assert abs(float(v['duration'])-float(stream['duration']))<=1/30+.00001
 run([ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-xerror','-i',output,'-map','0:V:0','-f','null','-'],'decode-'+row['key'])
 frame=work/'frames'/(row['key']+'.rgb565')
 run([ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-i',output,'-map','0:V:0','-frames:v','1','-vf','vflip','-pix_fmt','rgb565le','-f','rawvideo',frame],'frame-'+row['key'])
 assert frame.stat().st_size==720*720*2
 symbol=row['symbol'];assembly+=['.balign 16','.global '+symbol,'.hidden '+symbol,'.type '+symbol+',%object',symbol+':','.incbin "'+frame.as_posix()+'"','.size '+symbol+',.-'+symbol]
 media.append(dict(row,output=str(output),sha256=sha(output),bytes=output.stat().st_size,frameSHA256=sha(frame),probe=outprobe,fullFrameDecodePassed=True,sourceFps=stream['r_frame_rate'],playbackSpeed=1,cropped=False,stretched=False))
 print('Prepared '+row['key'],flush=True)
 asm=work/'collection_previews.S'
 asm.write_text('\n'.join(assembly)+'\n','utf8')
cmd=list(receipt['command']);compiler=cmd[0]
run([compiler,'--target=aarch64-linux-android26','-c',asm,'-o',work/'collection_previews.o'],'previews-object')
cmd[cmd.index(str(base/'native/native_carousel.cpp'))]=str(work/'native/native_carousel.cpp')
cmd[cmd.index(str(base/'libturbo_carousel.so'))]=str(work/'libturbo_carousel.so')
cmd.append(str(work/'collection_previews.o'))
dependencies={str(Path(v)):sha(v) for v in cmd if str(v).endswith('.o')}
for name,h in receipt['objects'].items():assert dependencies[name]==h,name
run(cmd,'native-build')
routes=snapshot/'tests/collection_routes.cpp'
assert routes.exists()
run([host,'-std=c++17','-Wall','-Wextra','-Werror','-finput-charset=UTF-8','-fexec-charset=UTF-8','-I',work/'native',routes,'-o',work/'tests/routes.exe'],'routes-compile')
route_result=run([work/'tests/routes.exe'],'routes-test');assert 'PASS' in route_result
record=dict(createdUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),base='R68',
 baseAPK=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R68-20261007.apk',
 baseSHA256='72ce7c2cbb3d7cf14ad122b0b98e42a41563114bbbc5c925caedbdee49ff66c3',
 nativeSHA256=sha(work/'libturbo_carousel.so'),nativeSources=current,baseNativeSHA256=receipt['nativeSHA256'],
 changedNativeSources=changed,addedNativeSources=[],cornerPolicyResult=result.strip(),sourceWiringChecks=len(wiring)+2,oneDecoderPolicyPassed=True,routeResult=route_result.strip(),
 objects=dependencies,command=cmd,videos=media,proportionsChanged=False,emulatorChanged=False,compiled=True,installed=False)
(work/'evidence/build.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n','utf8')
print(route_result.strip());print('R69 native and media ready.')
