from pathlib import Path
import hashlib,json,re,shutil,subprocess,zipfile
ROOT=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
BASE=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003\TurboStations-Capas4-Sinopses-LED-Netplay-R4-20261003.apk')
N=ROOT/'native';OUT=ROOT/'video/previews';OUT.mkdir(parents=True,exist_ok=True)
ffmpeg=shutil.which('ffmpeg');assert ffmpeg
sha=lambda p:hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
entries=re.findall(r'\{"([^"]+)","([^"]+)"\}',(N/'system_video720_assets.h').read_text())
assets=list(dict.fromkeys(asset for key,asset in entries))
rows=[];header=['// Generated from actual first frames of the packaged videos, never from photographs.','struct Video720Poster {const char*asset;const unsigned char*pixels;};','extern "C" {']
assembly=['.section .rodata.station_video_previews,"a",%progbits']
with zipfile.ZipFile(BASE) as z:
 for index,asset in enumerate(assets):
  src=OUT/'input.mp4';raw=OUT/(Path(asset).stem+'.rgb565')
  info=z.getinfo('assets/'+asset);assert info.compress_type==zipfile.ZIP_STORED
  if not raw.exists():
   with z.open(info) as a,src.open('wb') as b:shutil.copyfileobj(a,b)
   subprocess.run([ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-i',str(src),'-frames:v','1','-vf','scale=720:720,vflip','-pix_fmt','rgb565le','-f','rawvideo','-y',str(raw)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   src.unlink()
  assert raw.stat().st_size==720*720*2
  name=f'station_video_frame_{index}'
  header.append(f'extern const unsigned char {name}[];')
  assembly.extend(['.balign 16',f'.global {name}',f'.hidden {name}',f'.type {name},%object',f'{name}:',f'.incbin "{raw.as_posix()}"',f'.size {name},.-{name}'])
  with z.open(info) as stream:video_sha=hashlib.file_digest(stream,'sha256').hexdigest()
  rows.append({'asset':asset,'videoSha256':video_sha,'previewSha256':sha(raw),'width':720,'height':720,'bytes':raw.stat().st_size})
  print('Prepared video frame',index+1,'/',len(assets),flush=True)
header.extend(['}','static const Video720Poster video720Posters[]={'])
for index,asset in enumerate(assets):header.append(f'{{"{asset}",station_video_frame_{index}}},')
header.append('};')
(N/'video720_posters.h').write_text('\n'.join(header)+'\n')
(N/'video720_posters.S').write_text('\n'.join(assembly)+'\n')
subprocess.run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','-c',str(N/'video720_posters.S'),'-o',str(N/'video720_posters.o')],check=True)
(ROOT/'evidence/video-preview-inputs.json').write_text(json.dumps({'sourceApk':str(BASE),'previews':rows,'maximumGpuPreviewBytes':8*720*720*2,'allVideoPayloadsUnchanged':True},indent=2)+'\n')
print('Video preview object ready',sha(N/'video720_posters.o'))
