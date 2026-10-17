"""Rebuild the pinned R138 baseline, then only the reviewed R139 resource patch."""
from pathlib import Path, PurePosixPath
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import tarfile

ARCHIVE_SHA = 'b8f7649a5edacbe9e913d5e50f66482c0aa082fbd2237f5fd7800d00723b735a'
MANIFEST_SHA = '63049a133ed0a761133f4ffc36ce642870dc699e103a5a73ab0b7683a6d90f47'
R138_RUNTIME = '463bdb0b409e028aa34f6c9a09d291a3715ffb3eacb8f18ee28843e7373eb80f'
R138_SOURCE = 'e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2'
SOURCE = 'RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
CHANGED = 'frontend/drivers/platform_unix.c'
REPO = Path(__file__).resolve().parents[3]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(source):
    return {path.relative_to(source).as_posix(): sha(path) for path in source.rglob('*') if path.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('delivery', 'work', 'ndk', 'baseline-runtime'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--mode', choices=('baseline', 'candidate'), required=True)
    parser.add_argument('--overlay', type=Path)
    parser.add_argument('--source-freeze', type=Path)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    require(1 <= args.jobs <= 6, 'Bounded compile workers required')
    require(sha(args.baseline_runtime) == R138_RUNTIME, 'Installed R138 native runtime differs')
    archive = args.delivery / 'native/retroarch-corresponding-source.tar.gz'
    manifest = args.delivery / 'native/CORRESPONDING-SOURCE-MANIFEST.json'
    require(sha(archive) == ARCHIVE_SHA and sha(manifest) == MANIFEST_SHA, 'Corresponding source inputs differ')
    require('Pkg.Revision = 28.2.13676358' in (args.ndk / 'source.properties').read_text(), 'NDK r28c required')
    baseline = REPO / 'integration/online-snes-startup-r138/native/source/frontend/drivers/platform_unix.c'
    require(sha(baseline) == R138_SOURCE, 'R138 source baseline differs')
    expected = json.loads(manifest.read_text('utf-8'))
    expected[CHANGED] = R138_SOURCE
    source = args.work / SOURCE
    if args.mode == 'baseline':
        require(args.work.is_absolute() and not args.work.exists(), 'Fresh absolute build directory required')
        require(REPO not in args.work.resolve().parents, 'Build output must be outside frozen repository sources')
        args.work.mkdir(parents=True)
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                name = PurePosixPath(member.name)
                require(not name.is_absolute() and '..' not in name.parts and name.parts[0] == SOURCE
                        and (member.isfile() or member.isdir()), 'Unsafe source archive entry')
            tar.extractall(args.work, filter='data')
        shutil.copyfile(baseline, source / CHANGED)
    require(inventory(source) == expected, 'Source drift before build')
    if args.mode == 'candidate':
        require(args.overlay and args.source_freeze, 'Reviewed overlay and source freeze required')
        proof = json.loads((args.work / 'baseline.json').read_text('utf-8'))
        require(proof['comparison']['productiveSectionsByteIdentical'], 'R138 reconstruction must pass first')
        require(sha(args.work / 'baseline.so') == proof['runtimeSha256'], 'Baseline binary changed')
        frozen = json.loads(args.source_freeze.read_text('utf-8'))
        require(frozen['nativeSourceSha256'] == sha(args.overlay), 'Candidate differs from frozen source')
        shutil.copyfile(args.overlay, source / CHANGED)
    actual = inventory(source)
    changed = [name for name in expected if expected[name] != actual.get(name)]
    require(set(actual) == set(expected) and changed == ([CHANGED] if args.mode == 'candidate' else []),
            'Only reviewed Android resource/lifecycle source may differ')
    jni = source / 'pkg/android/phoenix-common/jni'
    command = [str(args.ndk / 'ndk-build.cmd'), 'NDK_PROJECT_PATH=' + str(source / 'pkg/android/phoenix-common'),
        'APP_BUILD_SCRIPT=' + str(jni / 'Android.mk'), 'NDK_APPLICATION_MK=' + str(jni / 'Application.mk'),
        'NDK_OUT=' + str(args.work / 'obj'), 'NDK_LIBS_OUT=' + str(args.work / 'lib'),
        'APP_ABI=arm64-v8a', 'TARGET_ABIS=arm64-v8a', 'APP_PLATFORM=android-26',
        'NDK_NO_GL_HEADER_VER=26', 'APP_CPPFLAGS=-std=c++17', 'APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true',
        'HAVE_VULKAN=0', 'HAVE_CHEEVOS=0', 'HAVE_SAF=0', 'GIT_VERSION=', '-j' + str(args.jobs)]
    log = args.work / (args.mode + '.log')
    environment = {**os.environ, 'SOURCE_DATE_EPOCH': '1791504000', 'PYTHONDONTWRITEBYTECODE': '1'}
    print('Building ' + args.mode, flush=True)
    with log.open('wb') as output:
        process = subprocess.run(command, cwd=jni, env=environment, stdout=output, stderr=subprocess.STDOUT)
    require(process.returncode == 0, 'Native compile failed; inspect private build log')
    binary = args.work / 'lib/arm64-v8a/libretroarch-activity.so'
    final = args.work / (args.mode + '.so')
    shutil.copyfile(binary, final)
    data = final.read_bytes()
    require(data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', data, 18)[0] == 183, 'ARM64 ELF required')
    offset = struct.unpack_from('<Q', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 54)
    program_headers = [struct.unpack_from('<IIQQQQQQ', data, offset + i * size) for i in range(count)]
    alignment = min(header[7] for header in program_headers if header[0] == 1)
    require(alignment >= 16384, '16 KiB ELF alignment required')
    nm = args.ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-nm.exe'
    symbols = subprocess.check_output([str(nm), '--dynamic', '--defined-only', str(final)], text=True)
    for name in ('stationRequestQuit', 'stationRecoveryStatus', 'stationMultiplayerConfigure', 'stationMultiplayerBind', 'stationMultiplayerUnbind'):
        require('Java_org_emulationstation_frontend_netplay_StationRetroActivity_' + name in symbols, 'Native interface changed')
    require('STATION_MULTIPLAYER_MAX_PLAYERS 5U' in (source / 'frontend/drivers/station_multiplayer.h').read_text(),
            'Five-player capacity must remain exact')
    report = {'revision': 'R139' if args.mode == 'candidate' else 'R138-rebuilt', 'mode': args.mode,
        'compiled': True, 'sourceArchiveSha256': ARCHIVE_SHA, 'sourceManifestSha256': MANIFEST_SHA,
        'sourceFiles': len(expected), 'changedSourceFiles': changed,
        'runtimeSha256': sha(final), 'runtimeBytes': final.stat().st_size,
        'baseRuntimeSha256': R138_RUNTIME, 'minimumLoadAlignment': alignment, 'maximumPlayers': 5,
        'sourceDateEpoch': '1791504000', 'buildLogSha256': sha(log), 'recipeSha256': sha(__file__),
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'apkBuilt': False, 'installed': False,
        'gameplayValidated': False, 'emulationAndRecoveryLoopsChanged': False}
    if args.mode == 'baseline':
        comparison = REPO / 'integration/online-snes-startup-r138/recipe/build_native_r138.py'
        require(sha(comparison) == 'e2d922758f75897644f60035fcd3a8419a0108a703d09f0a7f098f3f529654a4', 'Pinned ELF comparison helper differs')
        spec = importlib.util.spec_from_file_location('compare_r138', comparison)
        helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
        report['comparison'] = helper.compare_elf(args.baseline_runtime, final)
    else:
        report['overlaySha256'] = sha(args.overlay)
        report['sourceFreezeSha256'] = sha(args.source_freeze)
    (args.work / (args.mode + '.json')).write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
