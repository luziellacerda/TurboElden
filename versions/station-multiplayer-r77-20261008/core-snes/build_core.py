"""Build only the isolated SNES Multitap core. Never package an APK or modify upstream."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008\snes')
ALIAS=Path(r'E:\R77Snes')
BASE=Path(r'E:\StationNetplayWork\upstream\libretro--bsnes-mercury-79d7f9de218b')
OLD=Path(r'E:\StationNetplayWork\engine-build\bsnes\obj\local\arm64-v8a\libretro.so')
NDK=Path(r'E:\TurboEdenEngine\android-ndk-r28c')
TOOLS=NDK/'toolchains/llvm/prebuilt/windows-x86_64/bin'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log,cwd=None):
    env=dict(os.environ,TMP=str(WORK),TEMP=str(WORK))
    with log.open('w',encoding='utf-8') as output:
        result=subprocess.run([str(x) for x in args],cwd=cwd,env=env,stdout=output,stderr=subprocess.STDOUT)
    if result.returncode: raise RuntimeError(str(log)+' exit '+str(result.returncode)+'\n'+log.read_text(encoding='utf-8',errors='replace')[-7000:])

def section(path,name):
    # ELF64 little-endian: section bytes, independent of debug path and build-id.
    import struct
    b=path.read_bytes();assert b[:6]==b'\x7fELF\x02\x01'
    off=struct.unpack_from('<Q',b,40)[0];size,count,si=struct.unpack_from('<HHH',b,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',b,off+i*size) for i in range(count)]
    ss=sections[si];strings=b[ss[4]:ss[4]+ss[5]]
    for s in sections:
        n=strings[s[0]:].split(b'\0')[0].decode()
        if n==name:return b[s[4]:s[4]+s[5]]
    raise AssertionError(name)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['baseline','candidate'],required=True);a=p.parse_args()
    assert ALIAS.resolve()==WORK.resolve() and ' ' not in str(ALIAS)
    assert sha(BASE/'target-libretro/libretro.cpp')=='90bfb5826f9e2e85a05d11137eeeebdbc05359b7eba3632d4296e87c5dae007a'
    src=BASE if a.stage=='baseline' else ALIAS/'source'
    expected='90bfb5826f9e2e85a05d11137eeeebdbc05359b7eba3632d4296e87c5dae007a' if a.stage=='baseline' else 'e0d95df5f51a215457a9dc693d1797450e1e41179b96229b04c738a0277fa3c7'
    assert sha(src/'target-libretro/libretro.cpp')==expected
    output=ALIAS/a.stage;output.mkdir(parents=True,exist_ok=True)
    args=[NDK/'ndk-build.cmd','-C',(src/'target-libretro').as_posix(),'APP_BUILD_SCRIPT='+(src/'target-libretro/jni/Android.mk').as_posix(),
      'PROFILE=performance','APP_ABI=arm64-v8a','APP_PLATFORM=android-26','NDK_OUT='+(output/'obj').as_posix(),'NDK_LIBS_OUT='+(output/'lib').as_posix(),'-j4','V=1']
    run(args,output/'build.log')
    binary=output/'obj/local/arm64-v8a/libretro.so'
    # Match the shipping recipe: copy ndk-build's installed/stripped library,
    # retaining the object ELF separately for disassembly and reproduction.
    installed=output/'lib/arm64-v8a/libretro.so'
    stripped=output/'libstation_bsnes.so';shutil.copy2(installed,stripped)
    run([TOOLS/'llvm-strip.exe','--strip-debug',stripped],output/'strip.log')
    headers=subprocess.check_output([str(TOOLS/'llvm-readelf.exe'),'-h','-l','-d',str(stripped)],text=True)
    exports=subprocess.check_output([str(TOOLS/'llvm-nm.exe'),'--dynamic','--defined-only',str(stripped)],text=True)
    (output/'elf.txt').write_text(headers+'\n'+exports,encoding='utf-8')
    assert 'AArch64' in headers
    aligns=[int(x.split()[-1],16) for x in headers.splitlines() if x.strip().startswith('LOAD ')]
    assert aligns and min(aligns)>=16384
    for name in ['retro_init','retro_run','retro_load_game','retro_set_controller_port_device','retro_serialize','retro_unserialize']:
        assert re.search(r'\b'+name+r'\b',exports),name
    text=section(binary,'.text');baseline=section(OLD,'.text')
    receipt={'utc':datetime.now(timezone.utc).isoformat(),'stage':a.stage,'upstreamCommit':'79d7f9de218b6ffa65a80bbdc5828532bc239232',
      'sourceWrapperSHA256':expected,'command':[str(x) for x in args],'sha256':sha(stripped),'bytes':stripped.stat().st_size,
      'symbolsSHA256':sha(binary),'ndkInstalledSHA256':sha(installed),'recipeSHA256':sha(Path(__file__)),
      'textSHA256':hashlib.sha256(text).hexdigest(),'baselineTextSHA256':hashlib.sha256(baseline).hexdigest(),
      'textEqualsInstalledBaseline':text==baseline,'loadAlignment':min(aligns),'architecture':'AArch64','androidExecuted':False,'gameplayValidated':False}
    if a.stage=='baseline':
        assert text==baseline,'baseline text not reproduced; inspect before candidate'
        assert sha(stripped)=='cc14438319709f3b7868b3e652c731f6df472ff21bb01e4a65234ba2cc6f368b','baseline shipping binary not reproduced'
        receipt['fullBinaryEqualsInstalledBaseline']=True
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))

if __name__=='__main__':main()
