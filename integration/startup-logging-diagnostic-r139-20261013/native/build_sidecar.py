# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the optional logging bridge after its source commit is frozen. No ADB."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
RUNTIME_SHA256 = 'ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378'
JNI_EXPORT = 'Java_org_emulationstation_frontend_netplay_StationStartupLogging_enable'
SOURCE_DATE_EPOCH = '1791849600'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def frozen_source(path, commit):
    relative = path.relative_to(REPO).as_posix()
    data = subprocess.check_output(['git', '-C', str(REPO), 'show', commit + ':' + relative], timeout=30)
    require(path.read_bytes() == data, 'Source differs from the explicit frozen commit: ' + relative)
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ndk', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{40}', args.source_commit), 'An explicit frozen 40-character Git commit is required')
    require(args.output.is_absolute(), 'Output must be absolute')
    args.output = args.output.resolve()
    args.ndk = args.ndk.resolve()
    args.runtime = args.runtime.resolve()
    require(not args.output.exists(), 'Output directory must be new')
    for protected in (REPO.resolve(), args.ndk, args.runtime.parent):
        require(not args.output.is_relative_to(protected), 'Output overlaps a protected input directory')
    require('Pkg.Revision = 28.2.13676358' in (args.ndk / 'source.properties').read_text(), 'NDK r28c required')
    require(digest(args.runtime) == RUNTIME_SHA256, 'Exact unchanged R139 runtime required')
    source = ROOT / 'station_startup_logging.c'
    inputs = {path.relative_to(REPO).as_posix(): frozen_source(path, args.source_commit)
              for path in (source, Path(__file__).resolve(), ROOT / 'COPYING', ROOT / 'base-receipt.json')}
    compiler = args.ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    nm = compiler.with_name('llvm-nm.exe')
    require(compiler.is_file() and nm.is_file(), 'Configured Windows NDK tools required')
    args.output.mkdir(parents=True, exist_ok=False)
    library = args.output / 'libstation_startup_logging.so'
    command = [str(compiler), '--target=aarch64-linux-android26', '-std=c11', '-fPIC', '-shared', '-O2',
               '-fvisibility=hidden', '-Wall', '-Wextra', '-Werror', '-Wl,-z,max-page-size=16384',
               '-Wl,-z,relro,-z,now,--no-undefined', '-Wl,-soname,libstation_startup_logging.so',
               str(source), '-o', str(library), '-ldl', '-llog']
    environment = {**os.environ, 'SOURCE_DATE_EPOCH': SOURCE_DATE_EPOCH, 'PYTHONDONTWRITEBYTECODE': '1'}
    process = subprocess.run(command, capture_output=True, timeout=120, env=environment)
    (args.output / 'compile.log').write_bytes(process.stdout + process.stderr)
    require(process.returncode == 0, 'Sidecar compile failed; inspect the local compile log')
    binary = library.read_bytes()
    require(binary[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', binary, 18)[0] == 183, 'ARM64 ELF required')
    offset = struct.unpack_from('<Q', binary, 32)[0]
    entry_size, count = struct.unpack_from('<HH', binary, 54)
    headers = [struct.unpack_from('<IIQQQQQQ', binary, offset + i * entry_size) for i in range(count)]
    loads = [header for header in headers if header[0] == 1]
    require(loads and all(header[7] >= 16384 for header in loads), '16 KiB load alignment required')
    symbols = subprocess.check_output([str(nm), '--dynamic', '--defined-only', str(library)], text=True, timeout=30)
    names = {line.split()[-1] for line in symbols.splitlines() if line.strip()}
    require(names == {JNI_EXPORT}, 'Unexpected exported interface')
    require(digest(args.runtime) == RUNTIME_SHA256, 'Runtime changed during sidecar build')
    receipt = dict(schemaVersion=1, diagnosticOnly=True, sourceCommit=args.source_commit,
                   sourceFiles=inputs, compilerSha256=digest(compiler), ndkVersion='28.2.13676358',
                   target='aarch64-linux-android26', minimumLoadAlignment=min(header[7] for header in loads),
                   sidecarSha256=digest(library), sidecarBytes=library.stat().st_size,
                   unchangedRuntimeSha256=RUNTIME_SHA256, exports=sorted(names),
                   compileLogSha256=digest(args.output / 'compile.log'), sourceDateEpoch=SOURCE_DATE_EPOCH,
                   utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), compiled=True,
                   apkBuilt=False, installed=False, androidExecuted=False, gameplayValidated=False)
    (args.output / 'sidecar-build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', 'utf-8')
    print(json.dumps({'compiled': True, 'sidecarSha256': receipt['sidecarSha256'],
                      'sidecarBytes': receipt['sidecarBytes'], 'unchangedRuntimeSha256': RUNTIME_SHA256}))


if __name__ == '__main__':
    main()
