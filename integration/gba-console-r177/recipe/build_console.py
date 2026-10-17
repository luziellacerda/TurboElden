"""Add GBA hardware art to the exact R167 renderer inherited by signed R176.

Private input reconstruction is independently pinned to all 14 R167 headers.
Linux/Windows NDK r28c baselines have identical runtime sections; only the
non-allocated compiler comment and ELF section-table offset differ.
No engine, frontend, game geometry, shader or DEX is modified by this stage.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, struct, subprocess, sys
from PIL import Image
sys.dont_write_bytecode = True
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PINS={'r133_console_assets.h':'cb67032b429be6dff580da032c0bafdaee4653a953417a1ae5a11ba4f382abd3',
      'r133_station_console_keys.h':'77d641267ce21cb4e39fb8fb10d6be211748c7d61880afd9f8ce8f659366d603',
      'r133_native_console.h':'e3e4873faed5037baf0f4f8ec4f34ab4be2077e351777ea2e84e5af27b5607b7',
      'native_carousel.cpp':'c8ce063f7b1459553b39f4169507ef1a51f7f5b61fb5fb9398e0ac7bf0a36ec2'}
ART_SHA='78ced9b7059e0f5fc6138dad06a1de2ecbbd2a2e3a749891934b10017688218e'

def need(value,message):
    if not value:raise ValueError(message)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def frozen(commit):
    result={}
    for p in [HERE/'build_console.py',HERE.parent/'native/station_gba_console_aliases.h']:
        name=p.relative_to(REPO).as_posix()
        raw=subprocess.check_output(['git','-C',str(REPO),'show',commit+':'+name])
        need(raw==p.read_bytes(),'Build source differs from frozen commit: '+name)
        result[name]=sha(p)
    return result
def load_alignment(raw):
    start=struct.unpack_from('<Q',raw,32)[0];size,count=struct.unpack_from('<HH',raw,54)
    loads=[struct.unpack_from('<IIQQQQQQ',raw,start+i*size) for i in range(count)]
    loads=[v for v in loads if v[0]==1]
    need(loads and all(v[7]>=16384 and (v[2]-v[3])%16384==0 for v in loads),'Native 16 KiB LOAD alignment')
    return min(v[7] for v in loads)

def build(task,commit):
    pins=frozen(commit);baseline=task/'renderer-baseline'
    equivalent=json.loads((baseline/'runtime-equivalence.json').read_text())
    need(equivalent['allRuntimeSectionsIdentical'] and equivalent['loadedBytesIdenticalExceptNonRuntimeSectionTablePointer'] and
         equivalent['changedSections']==['.comment'] and equivalent['donorSha256']=='82017952a6bf44a7a8c9098a3ef568fb0d2b809d99211be0e17785a77559d22a',
         'Installed renderer runtime must reproduce before adding art')
    need(sha(baseline/'libturbo_carousel.so')==equivalent['rebuiltSha256'],'Reproduced native input changed')
    recovered=json.loads((task/'inputs/recovered-r167/source-recovery.json').read_text())
    need(recovered['passed'] and recovered['originalR167HeaderPinsMatched']==14,'Original R167 source proof required')
    for name,pin in recovered['headerSha256'].items():need(sha(baseline/'overlay'/name)==pin,'R167 header differs: '+name)
    command=json.loads((baseline/'command.json').read_text())
    parent=next(Path(v) for v in command if v.endswith('/r133-parent/overlay'))
    for name,pin in PINS.items():need(sha(parent/name)==pin,'Original console renderer source differs: '+name)
    image=task/'inputs/gba-console-public-domain-960.png'
    need(sha(image)==ART_SHA,'Reviewed public-domain GBA photograph differs')
    im=Image.open(image);need(im.size==(960,663) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255),'Original transparent photograph required')
    rgba=im.tobytes()
    out=task/'renderer';out.mkdir(parents=True,exist_ok=False)
    overlay=out/'overlay';shutil.copytree(baseline/'overlay',overlay)
    for name in PINS:shutil.copyfile(parent/name,overlay/name)
    shutil.copyfile(HERE.parent/'native/station_gba_console_aliases.h',overlay/'station_gba_console_aliases.h')
    generated=overlay/'station_gba_console_asset.h'
    with generated.open('w') as f:
        f.write('// Existing public-domain photo by Evan-Amos; decoded pixels only, no art edits.\n#pragma once\nstatic const unsigned char stationConsole_gba[]={\n')
        for offset in range(0,len(rgba),32):f.write(','.join(str(v) for v in rgba[offset:offset+32])+',\n')
        f.write('};\n')
    original=(parent/'r133_console_assets.h').read_bytes()
    anchor=b'{"ps4",512,512,stationConsole_ps4}};'
    replacement=b'{"ps4",512,512,stationConsole_ps4},{"gba",960,663,stationConsole_gba}};'
    need(original.count(anchor)==1,'One closed original console asset table required')
    prefix=b'#include "station_gba_console_asset.h"\n'
    changed=prefix+original.replace(anchor,replacement,1)
    need(changed.removeprefix(prefix).replace(replacement,anchor,1)==original,'Original 22 hardware photos must remain exact')
    (overlay/'r133_console_assets.h').write_bytes(changed)
    original=(parent/'r133_station_console_keys.h').read_bytes()
    newline=b'\r\n' if b'\r\n' in original else b'\n'
    anchor=b'static const StationConsoleAlias stationConsoleAliases[]={'
    prefix=b'#include "station_gba_console_aliases.h"'+newline
    insertion=newline+b' STATION_GBA_CONSOLE_ALIASES'
    need(original.count(anchor)==1,'One original hardware alias table required')
    changed=prefix+original.replace(anchor,anchor+insertion,1)
    need(changed.removeprefix(prefix).replace(anchor+insertion,anchor,1)==original,'Existing hardware aliases must remain exact')
    (overlay/'r133_station_console_keys.h').write_bytes(changed)
    command=[str(overlay) if v==str(baseline/'overlay') else str(overlay/'native_carousel.cpp') if v==str(baseline/'overlay/native_carousel.cpp') else v for v in command]
    raw=out/'unlabelled.so';command[command.index('-o')+1]=str(raw);command[command.index('-MF')+1]=str(out/'dependencies.d')
    save(out/'command.json',command)
    result=subprocess.run(command,capture_output=True,env={**os.environ,'TMPDIR':str(out)},timeout=1800)
    (out/'build.log').write_bytes(result.stdout+result.stderr);need(result.returncode==0,'Console build failed; inspect build.log')
    binary=raw.read_bytes()
    for before,after in [('PS3 • ABRIR EMULADOR','PS3 • CONFIGURAÇÃO'),('PS4 • ABRIR EMULADOR','PS4 • CONFIGURAÇÃO')]:
        a,b=before.encode(),after.encode();need(len(a)==len(b) and binary.count(a+b'\0')==1,'Pinned inherited PS3/PS4 settings label changed');binary=binary.replace(a+b'\0',b+b'\0',1)
    final=out/'libturbo_carousel.so';final.write_bytes(binary)
    tools=Path(command[0]).parent
    exports=lambda p: {l.split()[-1] for l in subprocess.check_output([tools/'llvm-nm','-D','--defined-only',p],text=True).splitlines() if len(l.split())>=2}
    dynamic=lambda p: [l.strip() for l in subprocess.check_output([tools/'llvm-readelf','-d',p],text=True).splitlines() if any(v in l for v in ['(NEEDED)','(SONAME)'])]
    need(exports(final)==exports(baseline/'installed-r167.so'),'Console change altered native exports')
    need(dynamic(final)==dynamic(baseline/'installed-r167.so'),'Console change altered native dependencies')
    dependencies=(out/'dependencies.d').read_text().replace('\\\n','').replace('\\ ',' ')
    for name in ['r133_console_assets.h','r133_station_console_keys.h','r133_native_console.h','station_gba_console_asset.h','station_gba_console_aliases.h']:
        need(str(overlay/name) in dependencies,'Intended GBA console source was shadowed: '+name)
    need(frozen(commit)==pins,'Source changed during native build')
    result={'schema':'station.gba-console.native.r177.v1','passed':True,'sourceCommit':commit,'sourceSha256':pins,
            'installedRendererSha256':equivalent['donorSha256'],'baselineRuntimeReproduced':True,'baselineCompilerCommentDifference':True,
            'outputSha256':sha(final),'outputBytes':final.stat().st_size,'minimumLoadAlignment':load_alignment(binary),
            'previousConsolePhotosAndAliasesPreserved':True,'gbaAliases':9,'gbaPhotoDimensions':[960,663],
            'gbaOriginalPhotoSha256':ART_SHA,'gbaRgbaSha256':hashlib.sha256(rgba).hexdigest(),'photoPixelsModified':False,
            'frontendModified':False,'dexModified':False,'emulationModified':False,'existingDrawAndTextureCacheReused':True,
            'newTimersOrThreads':0,'physicalVisualVerified':False}
    save(out/'receipt.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);p.add_argument('--source-commit',required=True)
    a=p.parse_args();build(a.task,a.source_commit)
