"""Build only the opt-in PSX owner adapter; no APK/emulator modification."""
from pathlib import Path
import argparse, hashlib, json, subprocess
p=argparse.ArgumentParser()
p.add_argument('--ndk',type=Path,required=True)
p.add_argument('--pinned-options',type=Path,required=True)
p.add_argument('--protocol',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();here=Path(__file__).resolve().parent.parent/'native';a.out.mkdir(parents=True,exist_ok=True)
compiler=a.ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/aarch64-linux-android28-clang++.cmd'
files=[here/'StationPsxOwner.cpp',a.protocol/'StationPsxProtocol.cpp',a.protocol/'StationPsxSha256.cpp']
output=a.out/'libstation_psx_owner.so'
args=[str(compiler),'-std=c++20','-O2','-fPIC','-shared','-fno-omit-frame-pointer','-fno-optimize-sibling-calls','-Wall','-Wextra','-Werror','-Wl,-z,max-page-size=16384','-Wl,-z,relro,-z,now','-Wl,--no-undefined','-I'+str(here),'-I'+str(a.protocol),'-I'+str(a.pinned_options),*[str(f) for f in files],'-ldl','-o',str(output)]
r=subprocess.run(args,capture_output=True,text=True)
(a.out/'build.log').write_text(r.stdout+r.stderr,encoding='utf-8')
if r.returncode: print(r.stdout+r.stderr);raise SystemExit(r.returncode)
def pin(f):return {'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
receipt={'schemaVersion':1,'scope':'Standalone original SDL owner adapter compilation, no APK/phone/ROM execution','abi':'arm64-v8a','api':28,'flags':['C++20','O2','PIC','shared','preserve-frame-pointer','disable-sibling-calls','warnings-as-errors','16KiB-page-alignment','RELRO','NOW','no-undefined'],'sources':[pin(f) for f in files]+[pin(here/'StationPsxOwner.hpp'),pin(a.pinned_options/'PsxPinnedOptions.h'),pin(a.protocol/'StationPsxProtocol.hpp')],'output':pin(output),'passed':True,'limits':['No Android process or game executed','No productive APK, offline owner/core or route changed','Compilation does not prove physical synchronization, controller input or thermal behavior']}
(a.out/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'outputSha256':receipt['output']['sha256'],'bytes':receipt['output']['bytes']}))
