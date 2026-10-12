"""Compile local Android probes; paths are explicit CLI parameters and no USB is used."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = {
    'native-core-probe.c': 'f0c04ab0f65ce5f4baca4498ecf717b86e2aeb856a125cf079a49c241c53ed1c',
    'native-core-frame-probe.c': '527966b203362c95c704d65a1d33b81b3a6719e09a14245f8e7a957ef09bd1ef',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ndk', type=Path, required=True)
    parser.add_argument('--libretro-header-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=['load', 'frames', 'all'], default='all')
    args = parser.parse_args()
    if 'Pkg.Revision = 28.2.13676358' not in (args.ndk / 'source.properties').read_text():
        raise ValueError('NDK r28c revision 28.2.13676358 required')
    if not (args.libretro_header_dir / 'libretro.h').is_file():
        raise ValueError('The pinned Mercury libretro.h directory is required')
    toolchain = args.ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin'
    compiler = toolchain / 'aarch64-linux-android26-clang.cmd'
    readelf = toolchain / 'llvm-readelf.exe'
    args.output.mkdir(parents=True, exist_ok=True)
    sources = ['native-core-probe.c'] if args.kind == 'load' else ['native-core-frame-probe.c'] if args.kind == 'frames' else list(SOURCE_SHA256)
    receipts = []
    for name in sources:
        source = ROOT / name
        if digest(source) != SOURCE_SHA256[name]:
            raise ValueError('Reviewed probe source mismatch: ' + name)
        binary = args.output / source.stem
        command = [str(compiler), '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                   '-fPIE', '-pie', '-Wl,-z,max-page-size=16384', '-I',
                   str(args.libretro_header_dir), str(source), '-ldl', '-o', str(binary)]
        subprocess.run(command, check=True)
        headers = subprocess.check_output([str(readelf), '-h', '-l', str(binary)], text=True)
        alignments = [int(line.split()[-1], 16) for line in headers.splitlines() if line.strip().startswith('LOAD ')]
        if 'AArch64' not in headers or not alignments or min(alignments) < 16384:
            raise ValueError('Unexpected executable ABI or LOAD alignment')
        if not re.search(r'Type:\s+DYN', headers) or '/system/bin/linker64' not in headers:
            raise ValueError('Android PIE executable expected')
        receipts.append({
            'sourceFile': name, 'sourceSHA256': digest(source),
            'binaryFile': binary.name, 'binarySHA256': digest(binary),
            'binaryBytes': binary.stat().st_size, 'architecture': 'AArch64',
            'minimumAndroidAPI': 26, 'minimumLoadAlignment': min(alignments),
            'ndkRevision': '28.2.13676358', 'compiled': True, 'androidExecuted': False,
            'gameplayValidated': False,
        })
    report = {'schemaVersion': 1, 'probes': receipts, 'usesUsb': False}
    (args.output / 'probe-build-receipt.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
