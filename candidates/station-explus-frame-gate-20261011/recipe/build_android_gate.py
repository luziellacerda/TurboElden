"""Build a reusable ARM64 static primitive, NOT an emulator/JNI library or APK."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import datetime

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sdk', type=Path, default=Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003\sdk\android-arm64'))
    p.add_argument('--ndk', type=Path, default=Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64'))
    p.add_argument('--llvm', type=Path, default=Path(r'C:\Program Files\LLVM\bin'))
    a = p.parse_args()
    out = a.out.resolve()
    if out == ROOT or ROOT in out.parents:
        raise SystemExit('Binary output must remain outside this source tree')
    out.mkdir(parents=True, exist_ok=True)
    native = ROOT/'native'
    obj = out/'StationExPlusFrameGate.o'
    archive = out/'libstation_explus_frame_gate_candidate.a'
    command = [str(a.llvm/'clang++.exe'), '--target=aarch64-linux-android26',
        '--sysroot='+str(a.ndk/'sysroot'), '-resource-dir='+str(a.ndk/'lib/clang/19'),
        '-nostdinc++', '-isystem', str(a.sdk/'include/c++/v1'), '-std=c++20', '-fPIC',
        '-O2', '-Wall', '-Wextra', '-Werror', '-c',
        str(native/'StationExPlusFrameGate.cpp'), '-o', str(obj)]
    subprocess.run(command, check=True)
    subprocess.run([str(a.llvm/'llvm-ar.exe'), 'rcs', str(archive), str(obj)], check=True)
    readelf = a.ndk/'bin/llvm-readelf.exe'
    header = subprocess.check_output([str(readelf), '-h', str(obj)], text=True)
    if 'AArch64' not in header:
        raise SystemExit('Wrong machine architecture')
    receipt = {'schema': 1, 'generatedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'candidateOnly': True, 'target': 'aarch64-linux-android26',
        'apkOrEmulatorLibrary': False, 'containsJNIOrWss': False,
        'sourceSha256': {'native/StationExPlusFrameGate.cpp': sha(native/'StationExPlusFrameGate.cpp'),
                         'native/StationExPlusFrameGate.hpp': sha(native/'StationExPlusFrameGate.hpp')},
        'objectSha256': sha(obj), 'archiveSha256': sha(archive), 'archiveBytes': archive.stat().st_size,
        'compilerSha256': sha(a.llvm/'clang++.exe'),
        'compilerVersion': subprocess.check_output([str(a.llvm/'clang++.exe'), '--version'], text=True).splitlines()[0],
        'sdkLibcxxArchiveSha256': sha(a.sdk/'lib/libc++.a'),
        'sdkLibcxxModulesJsonSha256': sha(a.sdk/'lib/libc++.modules.json'),
        'elfHeader': header.strip(),
        'limits': ['Static primitive, not a linked ANativeActivity emulator',
                   'No Snes9x/Genesis Plus GX loop, renderer or core executed',
                   'No Android runtime/ABI end-to-end or server registration check']}
    (out/'android-gate-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__': main()
