"""Compile only the console hardware panel over the byte-reproduced R132 carousel."""
from pathlib import Path
import argparse,json,os,re,subprocess,zipfile
from common import *
R124=REPO/'versions/station-video-room-footer-r124-20261011'
PARENT_RECEIPT_SHA='c2b8c5db8a6cd56dfea8c922c8c9d8bc0ed48d429851f3c58594e1bd3faf1f31'
TOOLS={'clang++.exe':'1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3','llvm-nm.exe':'90236526ebb24c232e59ec573675e32a92190b3346cf3a342c8b0eb5ad0f8203','llvm-readelf.exe':'2646e382d8b2559b5c4ae91e9a98e187ed9bd59f23936054d424049ef795ba5e'}
def run(cmd,out,label):
 env={**os.environ,'TEMP':str(out/'temp'),'TMP':str(out/'temp'),'PYTHONDONTWRITEBYTECODE':'1'}
 p=subprocess.run(list(map(str,cmd)),cwd=out,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=1800)
 (out/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8');require(p.returncode==0,'Native tool failed: '+label);return p.stdout

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('base-apk','parent-native','native-inputs','generated-native','media-inputs','art-receipt','ndk','out'): p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--source-commit',required=True);a=p.parse_args();pins=verify_source_commit(a.source_commit)
 require(sha(a.base_apk)==BASE_SHA and a.base_apk.stat().st_size==BASE_BYTES,'Exact signed R132 donor required')
 require(sha(a.parent_native/'native-receipt.json')==PARENT_RECEIPT_SHA,'Exact parent R132 native receipt required')
 parent=read(a.parent_native/'native-receipt.json');inventory=parent['inputSha256'];resolved={};input_paths={}
 for n,h in inventory.items():
  public=R124/'native'/n;f=public if public.is_file() else a.native_inputs/n
  require(f.is_file() and sha(f)==h,'Retained native input differs: '+n);resolved[n]=f;input_paths['native:'+n]=f
  shadow=a.native_inputs/n;require(not shadow.is_file() or sha(shadow)==h,'Private input shadow differs: '+n)
 generated={f.name:sha(f) for f in a.generated_native.iterdir() if f.is_file() and f.suffix in ('.cpp','.h')}
 require(generated==parent['generatedInputSha256'],'Exact generated R131 loop/Sony inputs required')
 for n in generated: input_paths['generated:'+n]=a.generated_native/n
 media=read(a.media_inputs/'sony-media.json')
 for n,h in parent['mediaInputSha256'].items():
  require(sha(a.media_inputs/n)==h,'Sony media input differs: '+n);input_paths['media:'+n]=a.media_inputs/n
 input_paths['media:sony-media.json']=a.media_inputs/'sony-media.json'
 input_paths['parent:native-receipt.json']=a.parent_native/'native-receipt.json'
 overlay=a.parent_native/'overlay/native'
 require({f.name for f in overlay.iterdir() if f.is_file()}=={'native_carousel.cpp','r132_collection_presentation.h','r132_native_folders.h','r132_native_info.h','r132_sony_system_info_rows.h','r132_startup_loading.h','r132_system_infos.h'},'Closed R132 native overlay required')
 outputs={**{'native/'+n:h for n,h in parent['transforms']['synopsis']['overlayHeaderSha256'].items()},**parent['transforms']['loading']['outputSha256']}
 for f in overlay.iterdir():
  if not f.is_file(): continue
  key='native/'+f.name;require(key in outputs and sha(f)==outputs[key],'Exact R132 overlay differs: '+f.name);input_paths['parent-overlay:'+f.name]=f
 patcher=module(ROOT/'recipe/patch_console_panel.py','r133_console_panel')
 pixels,art=patcher.read_art_inputs(a.art_receipt)
 input_paths['art:receipt']=a.art_receipt
 for k in pixels:
  input_paths['art:'+k+'.rgba']=a.art_receipt.parent/(k+'.rgba')
  original=a.art_receipt.parent.parent/'source'/('ps3-slim.source' if k=='ps3' else k+'.source')
  require(original.is_file() and sha(original)==art['arts'][k]['sourceSha256'] and original.stat().st_size==art['arts'][k]['bytes'],'Exact official original image required: '+k)
  input_paths['source-photo:'+k]=original
 cpp,headers,transform=patcher.patch((overlay/'native_carousel.cpp').read_bytes(),resolved['d0/native_console.h'].read_bytes(),resolved['d0/station_console_keys.h'].read_bytes(),resolved['d2/console_assets.h'].read_bytes(),pixels)
 frozen_inputs={n:sha(f) for n,f in input_paths.items()}
 tool=a.ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin'
 require(all(sha(tool/n)==h for n,h in TOOLS.items()),'Exact NDK compiler/read tools required')
 require(not a.out.exists(),'Fresh output directory required');a.out.mkdir(parents=True);(a.out/'temp').mkdir()
 flags=[tool/'clang++.exe','--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so']
 inc=['-I',overlay,'-I',a.generated_native,'-I',a.media_inputs/'include','-I',REPO/'integration/ps3-ps4-offline/native','-I',R124/'native/d0','-I',a.native_inputs/'d0','-I',a.native_inputs/'d2','-I',a.native_inputs/'d1']
 obj=[resolved[n] for n in ('d1/video720_posters.o','d3/collection_previews.o','d4/lottie_frames.o')]+[a.media_inputs/n for n in media['extraObjects']]
 tail=['-L',a.native_inputs/'d1','-lc','-ldl','-llog',resolved['d5/installed_art.o']]
 last=[resolved[n] for n in ('d6/collection_previews.o','d7/collection_previews.o','d8/collection_previews.o')]
 baseline=a.out/'baseline-carousel.so'
 run(flags+inc+[overlay/'native_carousel.cpp']+obj+tail+['-o',baseline]+last,a.out,'baseline-r132')
 require(sha(baseline)==CAROUSEL_SHA,'R132 carousel must reproduce byte exactly before adding consoles')
 with zipfile.ZipFile(a.base_apk) as z: require(digest(z.read('lib/arm64-v8a/libturbo_carousel.so'))==CAROUSEL_SHA,'R132 donor carousel differs')
 patched=a.out/'overlay';patched.mkdir();(patched/'native_carousel.cpp').write_bytes(cpp)
 for n,raw in headers.items(): (patched/n).write_bytes(raw)
 result=a.out/'libturbo_carousel.so'
 run(flags+['-I',patched]+inc+[patched/'native_carousel.cpp']+obj+tail+['-o',result]+last,a.out,'console-r133')
 def exports(f,label): return {l.split()[-1] for l in run([tool/'llvm-nm.exe','--dynamic','--defined-only',f],a.out,label).splitlines() if len(l.split())>=3}
 require(exports(result,'new-exports')==exports(baseline,'old-exports'),'Native exported API must be exact')
 loads=re.findall(r'^\s*LOAD\s+.*\s(0x[0-9a-fA-F]+)\s*$',run([tool/'llvm-readelf.exe','-lW',result],a.out,'loads'),re.M)
 require(loads and all(int(v,16)>=16384 for v in loads),'Native 16KiB load alignment required')
 require(source_map()==pins and all(sha(f)==frozen_inputs[n] for n,f in input_paths.items()),'Frozen R133 inputs changed during compilation')
 require(all(sha(tool/n)==h for n,h in TOOLS.items()),'NDK tools changed during compilation')
 payload={'lib/arm64-v8a/libturbo_carousel.so':{'path':str(result.resolve()),'bytes':result.stat().st_size,'sha256':sha(result)}}
 receipt={'schema':'station.console.panel.native.v1','revision':'R133','baseApkSha256':BASE_SHA,'sourceCommit':a.source_commit,'sourceSha256':pins,'approvedScopes':['console-hardware-panel-psp-ps3-ps4'],'dexChanged':False,'baselineReproduced':{'carousel':True},'payloads':payload,'transforms':{'consolePanel':transform},'inputSha256':frozen_inputs,'inputPaths':{n:str(f.resolve()) for n,f in input_paths.items()},'officialArtReceipt':art,'retainedParentNativeReceiptSha256':PARENT_RECEIPT_SHA,'nativeToolSha256':TOOLS,'originalRendererShaderLoadingVideoLedUnchanged':True,'physicalVisualValidated':False}
 write(a.out/'native-receipt.json',receipt);print(json.dumps({'revision':'R133','compiled':True,'payloads':payload,'baselineReproduced':True,'newConsoleFamilies':list(pixels),'newTimerOrDecoder':False}))
if __name__=='__main__': main()