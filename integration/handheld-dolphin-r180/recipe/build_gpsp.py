"""Build the pinned, online-only gpSP core with a unique ELF name and 16 KiB pages."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess

COMMIT = '5819380c2ffb0900219d700a382ee68c464ebb99'
MODULE = 'gpsp_station_online'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(source, ndk, out):
    source, ndk, out = map(lambda p: Path(p).resolve(), (source, ndk, out))
    need(not out.exists() and not out.is_relative_to(source), 'Fresh private output required')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()
    need(git('rev-parse', 'HEAD') == COMMIT and not git('diff', '--name-only', 'HEAD'), 'Pinned unchanged gpSP checkout')
    need('Pkg.Revision = 28.2.13676358' in (ndk / 'source.properties').read_text(), 'Production NDK r28c')
    out.mkdir(parents=True, mode=0o700)
    jni = out / 'jni'
    jni.mkdir()
    original = (source / 'jni/Android.mk').read_text()
    need(original.count('LOCAL_PATH := $(call my-dir)') == 1
         and original.count('LOCAL_MODULE    := retro') == 1, 'Pinned official Android module recipe')
    recipe = original.replace('LOCAL_PATH := $(call my-dir)', 'LOCAL_PATH := ' + str(source / 'jni'))
    recipe = recipe.replace('LOCAL_MODULE    := retro', 'LOCAL_MODULE    := ' + MODULE)
    (jni / 'Android.mk').write_text(recipe)
    args = [ndk / 'ndk-build', '-C', source, 'NDK_PROJECT_PATH=' + str(source),
            'APP_BUILD_SCRIPT=' + str(jni / 'Android.mk'),
            'NDK_APPLICATION_MK=' + str(source / 'jni/Application.mk'),
            'NDK_TOOLCHAIN_VERSION=clang', 'APP_ABI=arm64-v8a', 'APP_PLATFORM=android-28',
            'APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true', 'APP_LDFLAGS=-Wl,-z,max-page-size=16384',
            'NDK_OUT=' + str(out / 'obj'), 'NDK_LIBS_OUT=' + str(out / 'lib'), '-j4']
    with (out / 'build.private.log').open('x') as log:
        result = subprocess.run(list(map(str, args)), stdout=log, stderr=log, timeout=600)
    need(result.returncode == 0, 'Official core build failed; inspect private log')
    binary = out / ('lib/arm64-v8a/lib' + MODULE + '.so')
    need(binary.is_file(), 'Expected new online core')
    tool = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
    elf = subprocess.check_output([str(tool), '-h', '-l', '-d', str(binary)], text=True)
    (out / 'elf.private.txt').write_text(elf)
    need('AArch64' in elf and '(SONAME)' in elf and ('[lib' + MODULE + '.so]') in elf,
         'Unique AArch64 ELF identity')
    loads = [line.split()[-1] for line in elf.splitlines() if line.strip().startswith('LOAD ')]
    need(loads and all(int(align, 16) >= 16384 for align in loads), '16 KiB load segments')
    need(not git('diff', '--name-only', 'HEAD'), 'Upstream emulator source changed during build')
    proof = dict(passed=True, upstream='https://github.com/libretro/gpsp', commit=COMMIT,
                 sourceCodeChanged=False, androidModuleNameChangedOnly=True, androidAbi='arm64-v8a',
                 androidApi=28, ndkVersion='28.2.13676358', module=MODULE,
                 sha256=sha(binary), bytes=binary.stat().st_size, elfLoadAlignments=loads,
                 generatedModuleRecipeSha256=sha(jni / 'Android.mk'),
                 scriptSha256=sha(__file__), sourceAndroidRecipeSha256=sha(source / 'jni/Android.mk'),
                 packaged=False, serverApplied=False, physicalGameplayValidated=False)
    (out / 'build-receipt.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof), flush=True)

if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--ndk', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    build(args.source, args.ndk, args.out)
