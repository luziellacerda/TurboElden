from pathlib import Path
from PIL import Image
import struct,json,hashlib,subprocess,shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native';out=W/'data/lottie';out.mkdir(exist_ok=True)
report={};headers=['#pragma once\n// Exact source Lottie frames, rendered at build time. RLE RGBA; one live texture per asset.\n']
for key,folder,frames in [('switch','frames',range(30,116)),('stars','star-frames',range(127)),('chatbot','chatbot-frames',range(86)),('online','online-robot-frames',range(242))]:
 crop=None
 if key in ('chatbot','online'):
  boxes=[Image.open(W/'temp/lottie-render'/folder/(str(frame)+'.png')).convert('RGBA').getchannel('A').getbbox() for frame in frames];boxes=[b for b in boxes if b];crop=(min(b[0] for b in boxes)-1,min(b[1] for b in boxes)-1,max(b[2] for b in boxes)+1,max(b[3] for b in boxes)+1)
 offsets=[];data=bytearray();sizes=set()
 for frame in frames:
  im=Image.open(W/'temp/lottie-render'/folder/(str(frame)+'.png')).convert('RGBA')
  if crop:im=im.crop(crop)
  sizes.add(im.size);raw=im.tobytes();pixels=struct.unpack('<'+'I'*(len(raw)//4),raw);offsets.append(len(data)//4)
  decoded=bytearray();i=0
  while i<len(pixels):
   color=pixels[i];j=i+1
   while j<len(pixels) and pixels[j]==color:j+=1
   data+=struct.pack('<II',j-i,color);decoded+=struct.pack('<I',color)*(j-i);i=j
  assert decoded==raw
 offsets.append(len(data)//4);assert len(sizes)==1;width,height=sizes.pop();p=out/(key+'.rle');p.write_bytes(data)
 headers += [f'extern "C" const unsigned station_lottie_{key}_rle[];\n',f'static constexpr unsigned stationLottie_{key}_width={width},stationLottie_{key}_height={height},stationLottie_{key}_frames={len(frames)};\n',f'static constexpr unsigned stationLottie_{key}_offsets[]={{'+','.join(map(str,offsets))+'};\n']
 report[key]={'width':width,'height':height,'frames':len(frames),'rleBytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'roundTripAllFrames':True,'liveRGBABytes':width*height*4,'transparentMarginCrop':crop}
headers.append('struct StationLottieAsset {const unsigned*data;const unsigned*offsets;unsigned width,height,frames;};\nstatic const StationLottieAsset stationLottieAssets[]={\n')
for key in report:headers.append('{station_lottie_'+key+'_rle,stationLottie_'+key+'_offsets,stationLottie_'+key+'_width,stationLottie_'+key+'_height,stationLottie_'+key+'_frames},\n')
headers.append('};\n')
(N/'station_lottie_assets.h').write_text(''.join(headers),'utf8')
asm='.section .rodata\n'
for key in report:asm+=f'.balign 4\n.global station_lottie_{key}_rle\nstation_lottie_{key}_rle:\n.incbin "{(out/(key+".rle")).as_posix()}"\n'
(out/'lottie_frames.S').write_text(asm,'utf8')
clang=r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang.exe'
subprocess.run([clang,'--target=aarch64-linux-android26','-c',str(out/'lottie_frames.S'),'-o',str(W/'lottie_frames.o')],check=True)
p=W/'evidence/native-build-input.json';r=json.loads(p.read_text('utf8'))
if str(W/'lottie_frames.o') not in r['command']:r['command'].insert(r['command'].index('-L'),str(W/'lottie_frames.o'))
p.write_text(json.dumps(r,indent=2),'utf8')
(W/'evidence/lottie-render-pack.json').write_text(json.dumps(report,indent=2),'utf8')
shutil.copy2(W/'assets/dark-mode-button-LICENSE.html',W/'assets/stars-LICENSE.html')
(W/'assets/stars-NOTICE.txt').write_text('stars — Marcello Gomes\nhttps://lottiefiles.com/pt/free-animation/stars-G6SjCsY2cp\nLottie Simple License: https://lottiefiles.com/page/license\nOriginal animation sampled at its 60fps; rendered at build time with lottie-web 5.13.0 (MIT).\n','utf8')
print(json.dumps(report,indent=2))
