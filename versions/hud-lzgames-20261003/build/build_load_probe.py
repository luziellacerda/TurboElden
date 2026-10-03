"""Compile Android arm64 loadability probe; never executes it on a device."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

WORK = Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
HERE = Path(__file__).resolve().parent
NDK = Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64')
SOURCE = HERE/'probe_native_load.c'
OUT = WORK/'probe/station_native_load_probe'
os.environ['TEMP'] = os.environ['TMP'] = str(WORK)
OUT.parent.mkdir(parents=True,exist_ok=True)
command = [NDK/'bin/clang.exe', '--target=aarch64-linux-android26',
           '--sysroot='+str(NDK/'sysroot'), '-std=c17', '-O2', '-Wall', '-Wextra', '-Werror',
           '-fPIE', '-pie', '-Wl,-z,max-page-size=16384', SOURCE, '-ldl', '-o', OUT]
result = subprocess.run([str(x) for x in command],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(OUT.parent/'build.log').write_text(result.stdout,encoding='utf-8')
if result.returncode:
    raise RuntimeError(result.stdout)
def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()
receipt = {'command':[str(x) for x in command], 'binary':str(OUT),'sha256':sha(OUT),
           'source_sha256':sha(SOURCE),'built':True,'executed_on_device':False,
           'scope':'dlopen RTLD_NOW + entry symbol + dlclose only; no emulation/save/control validation'}
(OUT.parent/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
