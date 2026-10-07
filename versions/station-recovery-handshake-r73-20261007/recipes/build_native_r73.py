"""Rebuild exact R71 sources with only the tested recovery-handshake flush.

No APK packaging, device access, registry mutation or signing occurs here.
All generated sources, objects, logs and receipts stay in a new E: directory.
"""
from pathlib import Path, PurePosixPath
import argparse
import datetime
import difflib
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
SNAPSHOT = Path(__file__).resolve().parent.parent
R71 = SNAPSHOT.parent / 'station-online-layout-r71-20261007'
NATIVE = R71 / 'native-recovery'
PIN = '69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
ARCHIVE_SHA = 'cecf1e3f5446724f748124d097bb9c5169c6f599404d33a8447d88fd197d17fe'
MANIFEST_SHA = '25dbe0e0e68d4348e23bfe034ff82284f95b50743973b464ea6c0a9694383eac'
FRONT_SHA = 'e221e40605aecce5f168fd68ab9f06fda1eb8297a97ba6c1aff3a6e660fa8d22'
R71_RUNTIME_SHA = 'd66267cd42507388f86034deb47e9f9670875784efb9afabfb8ffc64e3f3a856'
OLD_FUNCTION_SHA = 'f060036537bc6f98400ed74243f485573301710dbdc03f8ee66c64783f23a9ee'
NEW_FUNCTION_SHA = 'd3a42419124dda592fea217088ed4e4687bf63718f657299ac8d73ad9fa41e12'
CANDIDATE_FILE_SHA = '270d96213ef2ffd0ae4f30d8116680104d64ca502330f28911e90b6b53a80f7b'
TEST_RECIPE_SHA = '0b0a960dae80aafd2c1702169ee0c287b41959005a25433c5d47ed55eeb72d46'
FRONT_REL = 'network/netplay/netplay_frontend.c'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts}


def json_write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8', newline='\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-zip', default=r'E:\TurboStationsBuild\sources\RetroArch-' + PIN + '.zip')
    parser.add_argument('--ndk', default=r'E:\TurboEdenEngine\android-ndk-r28c')
    parser.add_argument('--output', default=r'E:\R73fixed')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out, ndk, archive = Path(args.output).resolve(), Path(args.ndk).resolve(), Path(args.source_zip).resolve()
    require(out.drive.upper() == 'E:' and ' ' not in str(out) and not out.exists(), 'Use a NEW path on E: without spaces')
    require(1 <= args.jobs <= 16, 'Invalid jobs')
    require(sha(archive) == ARCHIVE_SHA, 'Original RetroArch archive mismatch')
    require('Pkg.Revision = 28.2.13676358' in (ndk / 'source.properties').read_text(), 'NDK r28c required')
    require(sha(NATIVE / 'native/RECOVERY-SOURCE-MANIFEST.json') == MANIFEST_SHA, 'Frozen R71 manifest mismatch')
    manifest = json.loads((NATIVE / 'native/RECOVERY-SOURCE-MANIFEST.json').read_text('utf8'))
    require(manifest['upstreamCommit'] == PIN, 'Upstream revision mismatch')
    for name, expected in manifest['files'].items():
        require(sha(NATIVE / name) == expected, 'Frozen R71 source mismatch: ' + name)
    candidate_path = SNAPSHOT / 'tests/recovery_poll_candidate.h'
    require(sha(candidate_path) == CANDIDATE_FILE_SHA, 'Tested candidate file mismatch')
    candidate = candidate_path.read_text('utf8').rstrip()
    require(digest(candidate.encode()) == NEW_FUNCTION_SHA, 'Normalized candidate mismatch')
    test_path = SNAPSHOT / 'tests/recovery-flush-probe.json'
    test = json.loads(test_path.read_text('utf8'))
    require(sha(SNAPSHOT / 'tests/recovery_flush_probe.py') == TEST_RECIPE_SHA == test['testRecipeSHA256'], 'Test recipe mismatch')
    require(test['nativeSourceSHA256'] == FRONT_SHA and test['candidatePumpSHA256'] == NEW_FUNCTION_SHA,
            'Tested source or candidate differs')
    require(test['baselineFails'] and test['candidatePasses'] and test['checks'] == 22 and
            test['results']['baseline']['exitCode'] == 2 and test['results']['candidate']['exitCode'] == 0,
            'Required baseline regression/candidate test not passed')
    baseline_front = Path(r'E:\R71fixed') / ('RetroArch-' + PIN) / FRONT_REL
    require(sha(baseline_front) == FRONT_SHA, 'Local frozen R71 frontend mismatch')
    before = inventory(NATIVE)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TEMP=str(out), TMP=str(out),
               GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='core.autocrlf', GIT_CONFIG_VALUE_0='false',
               GIT_CONFIG_KEY_1='core.eol', GIT_CONFIG_VALUE_1='lf')
    out.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        prefix = 'RetroArch-' + PIN + '/'
        for entry in z.infolist():
            require(entry.filename.startswith(prefix) and '..' not in PurePosixPath(entry.filename).parts
                    and '\\' not in entry.filename and ':' not in entry.filename, 'Unsafe source archive path')
        z.extractall(out)
    src = out / ('RetroArch-' + PIN)
    patches = [NATIVE / 'engine-patches/retroarch-station-all.patch',
               NATIVE / 'engine-patches/retroarch-station-auto-password.patch']
    for name in re.findall(r'^--- a/(.+)$', patches[0].read_text(), re.M):
        f = src / name
        f.write_text(f.read_text(), encoding='utf8', newline='\n')
    for patch in patches:
        for options in (['--check'], []):
            subprocess.run(['git', '-c', 'core.autocrlf=false', '-c', 'core.eol=lf',
                            'apply', *options, str(patch)], cwd=src, env=env, check=True)
    spec = importlib.util.spec_from_file_location('r71_frozen_patch', NATIVE / 'recipes/patch_native.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply(src)
    frontend = src / FRONT_REL
    require(sha(frontend) == FRONT_SHA, 'Reconstructed frontend is not exact R71')
    original = frontend.read_text('utf8')
    start = original.index('bool station_netplay_recovery_poll(void)\n{')
    end = original.index('\n}\n#endif', start) + 2
    old = original[start:end]
    require(digest(old.encode()) == OLD_FUNCTION_SHA, 'Original recovery function mismatch')
    require(original.count(old) == 1, 'Ambiguous old function')
    updated = original[:start] + candidate + original[end:]
    frontend.write_text(updated, encoding='utf8', newline='\n')
    require(frontend.read_text('utf8').replace(candidate, old, 1) == original, 'Unexpected source delta')
    difference = ''.join(difflib.unified_diff(original.splitlines(True), updated.splitlines(True),
                                            fromfile='r71/' + FRONT_REL, tofile='r73/' + FRONT_REL))
    (out / 'recovery-handshake-r73.patch').write_text(difference, encoding='utf8', newline='\n')
    source_receipt = {
        'upstreamCommit': PIN, 'upstreamArchiveSHA256': ARCHIVE_SHA,
        'baseRuntimeSHA256': R71_RUNTIME_SHA, 'baseFrontendSHA256': FRONT_SHA,
        'frontendSHA256': sha(frontend), 'oldFunctionSHA256': OLD_FUNCTION_SHA,
        'newFunctionSHA256': NEW_FUNCTION_SHA, 'candidateFileSHA256': CANDIDATE_FILE_SHA,
        'deltaFile': FRONT_REL, 'onlyRecoveryFunctionChangedFromR71': True,
        'diffSHA256': sha(out / 'recovery-handshake-r73.patch'),
        'r71SourceManifestSHA256': MANIFEST_SHA, 'r71NativeInputs': before,
        'regressionReceiptSHA256': sha(test_path), 'regressionChecks': 22,
        'regressionScope': test['scope'], 'recipeSHA256': sha(__file__),
        'gitConfiguration': {'core.autocrlf': False, 'core.eol': 'lf', 'scope': 'child processes'},
        'sourceFolder': str(src), 'output': str(out)}
    json_write(out / 'source-receipt.json', source_receipt)
    require(before == inventory(NATIVE), 'Frozen R71 snapshot changed')
    if args.prepare_only:
        print(json.dumps({'prepared': True, 'compiled': False, **source_receipt}, indent=2))
        return
    jni = src / 'pkg/android/phoenix-common/jni'
    command = [str(ndk / 'ndk-build.cmd'), 'NDK_PROJECT_PATH=' + str(src / 'pkg/android/phoenix-common'),
               'APP_BUILD_SCRIPT=' + str(jni / 'Android.mk'), 'NDK_APPLICATION_MK=' + str(jni / 'Application.mk'),
               'NDK_OUT=' + str(out / 'obj'), 'NDK_LIBS_OUT=' + str(out / 'lib'),
               'APP_ABI=arm64-v8a', 'TARGET_ABIS=arm64-v8a', 'APP_PLATFORM=android-26',
               'NDK_NO_GL_HEADER_VER=26', 'APP_CPPFLAGS=-std=c++17', 'APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true',
               'HAVE_VULKAN=0', 'HAVE_CHEEVOS=0', 'HAVE_SAF=0', 'GIT_VERSION=', '-j' + str(args.jobs)]
    print('Compiling R73 native runtime; exact R71 plus tested nonblocking handshake flush', flush=True)
    with (out / 'build.log').open('w', encoding='utf8') as log:
        built = subprocess.run(command, cwd=jni, env=env, stdout=log, stderr=subprocess.STDOUT)
    require(built.returncode == 0, 'Native compilation failed; inspect E: build.log')
    binary, final = out / 'lib/arm64-v8a/libretroarch-activity.so', out / 'libstation_retroarch.so'
    shutil.copyfile(binary, final)
    tool = ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin'
    headers = subprocess.check_output([str(tool / 'llvm-readelf.exe'), '-h', '-l', str(final)], text=True)
    symbols = subprocess.check_output([str(tool / 'llvm-nm.exe'), '--defined-only', '--dynamic', str(final)], text=True)
    (out / 'elf-headers.txt').write_text(headers, encoding='utf8', newline='\n')
    (out / 'elf-exports.txt').write_text(symbols, encoding='utf8', newline='\n')
    alignments = [int(line.split()[-1], 16) for line in headers.splitlines() if line.strip().startswith('LOAD ')]
    exports = ['ANativeActivity_onCreate'] + ['Java_org_emulationstation_frontend_netplay_StationRetroActivity_' + n
                for n in ('stationRecoveryControl', 'stationRecoveryStatus', 'stationRecoveryStalled')]
    require('AArch64' in headers and alignments and min(alignments) >= 16384, 'ELF architecture/alignment mismatch')
    require(all(re.search(r'\b' + name + r'\b', symbols) for name in exports), 'Missing NativeActivity/JNI export')
    require(before == inventory(NATIVE), 'R71 snapshot changed during build')
    require(sha(frontend) == source_receipt['frontendSHA256'], 'Frontend changed during compilation')
    runtime_sha = sha(final)
    require(runtime_sha != R71_RUNTIME_SHA, 'Updated runtime unexpectedly equals R71')
    report = {'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'compiled': True,
              **source_receipt, 'runtimeSHA256': runtime_sha, 'runtimeBytes': final.stat().st_size,
              'runtimePath': str(final), 'ndkRevision': '28.2.13676358', 'architecture': 'AArch64',
              'minimumLoadAlignment': min(alignments), 'exportsVerified': exports,
              'minAPI': 26, 'command': command, 'buildLogSHA256': sha(out / 'build.log'),
              'recoveryProtocol': 'station-stream.v2', 'serverRegistryAdditionsRequired': True,
              'serverDeployed': False, 'apkBuilt': False, 'installed': False,
              'androidExecuted': False, 'twoDeviceGameplayVerified': False}
    json_write(out / 'result.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
