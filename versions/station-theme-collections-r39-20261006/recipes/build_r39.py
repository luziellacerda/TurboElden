from pathlib import Path
import json,hashlib,subprocess,os
W=Path(__file__).resolve().parent;os.environ['TEMP']=os.environ['TMP']=str(W/'temp')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for file,digest in json.loads((W/'EXTERNAL-BUILD-INPUTS.json').read_text('utf8')).items():assert sha(file)==digest,file
r=json.loads((W/'evidence/native-build-input.json').read_text('utf8'));canonical=str(Path(r['command'][-1]).parent)
r['command']=[part.replace(canonical,str(W)) for part in r['command']]
asm='.section .rodata\n'
for key in ('switch','stars','chatbot','online'):asm+=f'.balign 4\n.global station_lottie_{key}_rle\nstation_lottie_{key}_rle:\n.incbin "{(W/"data/lottie"/(key+".rle")).as_posix()}"\n'
src=W/'temp/lottie_frames.S';src.write_text(asm,'utf8')
subprocess.run([str(Path(r['command'][0]).with_name('clang.exe')),'--target=aarch64-linux-android26','-c',str(src),'-o',str(W/'lottie_frames.o')],check=True)
p=subprocess.run(r['command'],capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence/android-build.log').write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,p.stderr
r.update(soSHA256=sha(W/'libturbo_carousel.so'),soBytes=(W/'libturbo_carousel.so').stat().st_size,androidCompile=True)
(W/'evidence/native-build.json').write_text(json.dumps(r,indent=2),'utf8');print(r['soSHA256'])
