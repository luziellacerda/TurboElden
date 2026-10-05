"""Compile the Station rate JNI and optionally the real R11 carousel, without replacing DEX."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--ndk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-carousel', action='store_true')
    args = parser.parse_args()
    work, output = args.work_root.resolve(), args.output.resolve()
    if output.is_relative_to(work):
        raise ValueError('Output must be separate from source')
    output.mkdir(parents=True, exist_ok=False)
    host = 'windows-x86_64' if os.name == 'nt' else 'linux-x86_64'
    suffix = '.exe' if os.name == 'nt' else ''
    compiler = args.ndk / 'toolchains/llvm/prebuilt' / host / 'bin' / ('clang++' + suffix)
    common = [str(compiler), '--target=aarch64-linux-android26', '-std=c++17', '-shared', '-fPIC', '-O2',
              '-Wl,-z,max-page-size=16384', '-Wl,--no-undefined']
    subprocess.run([*common, '-fvisibility=hidden', '-Wall', '-Wextra', '-Werror',
                    '-Wno-return-type-c-linkage', '-static-libstdc++', '-Wl,--exclude-libs,ALL',
                    str(work / 'station/src/native/station_frontend.cpp'), '-ldl', '-llog',
                    '-o', str(output / 'libstation_frontend.so')], check=True)
    files = [output / 'libstation_frontend.so']
    if args.build_carousel:
        native = work / 'native'
        subprocess.run([*common, '-nostdlib', '-fno-exceptions', '-fno-rtti', '-fno-stack-protector',
                        '-fno-builtin', '-Wl,-soname,libturbo_carousel.so',
                        str(native / 'native_carousel.cpp'), str(native / 'video720_posters.o'),
                        '-L', str(native), '-lc', '-ldl', '-llog',
                        '-o', str(output / 'libturbo_carousel.so')], check=True)
        files.append(output / 'libturbo_carousel.so')
    report = dict(apkSigned=False, installed=False, dexChanged=False,
                  files={file.name: dict(bytes=file.stat().st_size,
                                         sha256=hashlib.sha256(file.read_bytes()).hexdigest()) for file in files})
    (output / 'compiled-modules.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
