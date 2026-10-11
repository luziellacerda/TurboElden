#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the PSX opt-in SDL entry from pinned owner/protocol sources; never patch offline ELF."""
import argparse,hashlib,json,re,struct,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--ndk',type=Path,required=True);p.add_argument('--owner',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);p.add_argument('--pinned-options',type=Path,required=True);p.add_argument('--identity-source',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent.parent
compiler=a.ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/aarch64-linux-android28-clang++.cmd'
tools=compiler.parent
source=[here/'native/StationPsxEntry.cpp',a.owner/'StationPsxOwner.cpp',a.protocol/'StationPsxProtocol.cpp',a.protocol/'StationPsxSha256.cpp']
if a.identity_source:source.append(a.identity_source)
headers=[a.owner/'StationPsxOwner.hpp',a.protocol/'StationPsxProtocol.hpp',a.pinned_options/'PsxPinnedOptions.h']
a.out.mkdir(parents=True,exist_ok=True);binary=a.out/'libstation_psx_online.so'
command=[str(compiler),'-std=c++20','-O2','-fPIC','-shared','-fno-omit-frame-pointer','-fno-optimize-sibling-calls','-Wall','-Wextra','-Werror','-Wl,-z,max-page-size=16384','-Wl,-z,relro,-z,now','-Wl,--no-undefined','-Wl,-soname,libstation_psx_online.so','-I'+str(a.owner),'-I'+str(a.protocol),'-I'+str(a.pinned_options),*[str(x) for x in source],'-ldl','-o',str(binary)]
frozen={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in source+headers}
r=subprocess.run(command,capture_output=True,text=True)
(a.out/'build.log').write_text(r.stdout+r.stderr,encoding='utf8')
if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
if any(hashlib.sha256(Path(x).read_bytes()).hexdigest()!=h for x,h in frozen.items()):raise RuntimeError('Source changed during compilation')
b=binary.read_bytes()
if b[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',b,18)[0]!=183:raise RuntimeError('AArch64 ELF identity')
phoff=struct.unpack_from('<Q',b,32)[0];ents,num=struct.unpack_from('<HH',b,54)
alignments=[]
for i in range(num):
 off=phoff+i*ents
 if struct.unpack_from('<I',b,off)[0]==1:alignments.append(struct.unpack_from('<Q',b,off+48)[0])
if not alignments or any(n<16384 for n in alignments):raise RuntimeError('16KiB LOAD alignment')
exports=subprocess.check_output([str(tools/'llvm-nm.exe'),'-D','--defined-only',str(binary)],text=True)
actual=set(re.findall(r'Java_org_emulationstation_frontend_netplay_StationPsxBridge_(\w+)',exports))
bridge=here/'java/org/emulationstation/frontend/netplay/StationPsxBridge.java'
expected=set(re.findall(r'public static native \S+\s+(\w+)\(',bridge.read_text()))
if expected!=actual:raise RuntimeError('JNI exports mismatch: '+repr((expected-actual,actual-expected)))
if not re.search(r'\bSDL_main\b',exports) or not re.search(r'\bJNI_OnLoad\b',exports):raise RuntimeError('SDL/JNI bootstrap exports')
if a.identity_source and not all(re.search(r'\b'+name+r'\b',exports) for name in ('StationPsxRuntimeIdentity','StationPsxRuntimeManifest')):raise RuntimeError('Productive runtime identity exports')
needed=subprocess.check_output([str(tools/'llvm-readobj.exe'),'--needed-libs',str(binary)],text=True)
libs=re.findall(r'^\s+(lib[^\s]+\.so)\s*$',needed,re.M)
if any(n in libs for n in ['libmain.so','libSDL2.so','libpcsx_rearmed_libretro_android.so']):raise RuntimeError('Offline donor must not be linked/copied')
def pin(x):return {'file':x.name,'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
receipt={'schema':1,'passed':True,'scope':'Compile/link/ELF/JNI opt-in PSX entry only','target':'arm64-v8a','api':28,'standard':'C++20','optimization':'O2','loadAlignment':alignments,'neededLibraries':libs,'sources':[pin(x) for x in source+headers+[bridge]],'binary':pin(binary),'jniMethods':sorted(expected),'usesGenuineNormalOwnerRun':True,'offlineElfModified':False,'rendererInputReplaced':False,'limits':['No Android activity, controller or ROM executed','No physical synchronization, performance or thermal validation','No productive APK modified or installed']}
receipt['productiveIdentityEmbedded']=bool(a.identity_source)
(a.out/'entry-build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':True,'sha256':receipt['binary']['sha256'],'bytes':len(b),'jniMethods':len(actual),'alignment':alignments}))
