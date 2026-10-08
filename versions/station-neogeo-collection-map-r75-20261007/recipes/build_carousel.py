"""Rebuild only the Neo Geo collection-name mapping over the exact R71/R74 carousel.

No APK packaging, media conversion, Java/runtime changes or device operations.
The unchanged R71 command must reproduce its recorded .so before building R75.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess


SNAPSHOT = Path(__file__).resolve().parent.parent
BASE = Path(r'E:\ESTUDO APK\work\station-online-layout-r71-20261007-carousel-final')
BASE_RECEIPT_SHA = 'e54569413e7a176719bbdb0523bc640a683208bf9662acad8436fab701e4dc1a'
BASE_NATIVE_SHA = '9671f553858ef1c98c320ea85cfa7aa29350c1a9c341a3fe08b8d46e4a8a48d7'
BASE_HEADER_SHA = '10daa6b42d46d7bc1f099e705d9fa258af8c1a43a0ef6a0a7d4071cacbfe64f9'
FIXED_HEADER_SHA = '5ca0f4f114037e605b698067b34d01cb6f0aef2ba4c3d223117801d8a71a693b'
DEFAULT_WORK = Path(r'E:\ESTUDO APK\work\station-neogeo-collection-map-r75-20261007\native-build')
BAD = bytes.fromhex('434f4c45c383e280a1c383c6924f')
GOOD = br'COLE\u00c7\u00c3O'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def quoted_dependencies(source, includes):
    """Record quoted includes, including inherited fallback include directories."""
    found = {}

    def visit(path):
        path = path.resolve()
        if str(path) in found:
            return
        found[str(path)] = sha(path)
        text = path.read_text(encoding='utf-8')
        for name in re.findall(r'^\s*#\s*include\s*"([^"\n]+)"', text, re.M):
            child = next((folder / name for folder in [path.parent, *includes]
                          if (folder / name).is_file()), None)
            require(child is not None, 'Missing quoted dependency: ' + name)
            visit(child)

    visit(source)
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=str(DEFAULT_WORK))
    args = parser.parse_args()
    work = Path(args.output).resolve()
    require(work.drive.upper() == 'E:', 'Build and temporary files must be on E:')
    require(not work.exists(), 'Refusing to overwrite an existing build: ' + str(work))
    require(sha(BASE / 'evidence/build.json') == BASE_RECEIPT_SHA, 'Base receipt mismatch')
    receipt = json.loads((BASE / 'evidence/build.json').read_text(encoding='utf-8'))
    require(sha(BASE / 'libturbo_carousel.so') == receipt['nativeSHA256'] == BASE_NATIVE_SHA,
            'Base carousel mismatch')
    require(len(receipt['nativeSources']) == 65, 'Unexpected source manifest')
    require(len(receipt['objects']) == 7, 'Unexpected object manifest')
    for name, expected in receipt['nativeSources'].items():
        require(sha(BASE / 'native' / name) == expected, 'Base source mismatch: ' + name)
    for path, expected in receipt['objects'].items():
        require(sha(path) == expected, 'Base object mismatch: ' + path)

    overlay = SNAPSHOT / 'native/collection_video_policy.h'
    base_header = (BASE / 'native/collection_video_policy.h').read_bytes()
    fixed_header = overlay.read_bytes()
    require(sha(BASE / 'native/collection_video_policy.h') == BASE_HEADER_SHA, 'Base header mismatch')
    require(base_header.count(BAD) == 5, 'Expected exactly five corrupted literals')
    require(fixed_header == base_header.replace(BAD, GOOD), 'Delta is not the five literal repairs')
    require(sha(overlay) == FIXED_HEADER_SHA, 'Repair header mismatch')
    require(BAD not in fixed_header and fixed_header.count(GOOD) == 5, 'Invalid repaired literals')

    command = list(receipt['command'])
    source_arg = str(BASE / 'native/native_carousel.cpp')
    output_arg = str(BASE / 'libturbo_carousel.so')
    require(command.count(source_arg) == command.count(output_arg) == 1, 'Unexpected build arguments')
    require({str(Path(arg)): sha(arg) for arg in command if str(arg).endswith('.o')}
            == receipt['objects'], 'Linked objects differ from receipt')
    includes = [Path(command[i + 1]) for i, arg in enumerate(command) if arg == '-I']
    original_dependencies = quoted_dependencies(Path(source_arg), includes)
    compiler = Path(command[0])
    compiler_sha = sha(compiler)
    host = Path(r'C:\Program Files\LLVM\bin\clang++.exe')
    host_sha = sha(host)
    recipe_sha = sha(__file__)

    work.mkdir(parents=True)
    for directory in ['native', 'tests', 'evidence', 'temp']:
        (work / directory).mkdir()
    env = dict(os.environ, TEMP=str(work / 'temp'), TMP=str(work / 'temp'))
    executions = []

    def run(argv, label):
        argv = list(map(str, argv))
        result = subprocess.run(argv, capture_output=True, env=env)
        log = work / 'evidence' / (label + '.log')
        log.write_bytes(result.stdout + result.stderr)
        executions.append({'label': label, 'command': argv, 'exitCode': result.returncode,
                           'log': str(log), 'logSHA256': sha(log)})
        require(result.returncode == 0, label + ': ' + result.stderr.decode('utf-8', 'replace')[-2000:])
        return result.stdout.decode('utf-8', 'replace').strip()

    # This catches drift in fallback includes, linker inputs and toolchain as well as objects.
    baseline_command = list(command)
    baseline_command[baseline_command.index(output_arg)] = str(work / 'baseline-r71.so')
    run(baseline_command, 'baseline-reproduction')
    reproduced_sha = sha(work / 'baseline-r71.so')
    require(reproduced_sha == BASE_NATIVE_SHA,
            'Unchanged R71 does not reproduce; do not proceed with the R75 patch')

    for name in receipt['nativeSources']:
        shutil.copyfile(BASE / 'native' / name, work / 'native' / name)
    shutil.copyfile(overlay, work / 'native/collection_video_policy.h')
    sources = {p.name: sha(p) for p in (work / 'native').iterdir() if p.is_file()}
    require(set(sources) == set(receipt['nativeSources']), 'Source file set changed')
    changed = sorted(name for name in sources if sources[name] != receipt['nativeSources'][name])
    require(changed == ['collection_video_policy.h'], 'Unexpected source change: ' + repr(changed))

    test_sources = {}
    for name, path in {
        'r71Routes': SNAPSHOT.parent / 'station-online-layout-r71-20261007/tests/collection_all_video.cpp',
        'r69Corners': SNAPSHOT.parent / 'station-collection-media-r69-20261007/tests/collection_corners.cpp',
        'r55Decoder': SNAPSHOT.parent / 'station-current-r55-20261006/tests/native/test_video_policy.cpp',
        'r70Settings': SNAPSHOT.parent / 'station-collection-navigation-r70-20261007/tests/collection_settings.cpp',
        'r70Navigation': SNAPSHOT.parent / 'station-collection-navigation-r70-20261007/tests/navigation.cpp',
    }.items():
        test_sources[name] = {'path': str(path), 'sha256': sha(path)}
    common = [host, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-finput-charset=UTF-8',
              '-fexec-charset=UTF-8', '-I', work / 'native']
    poster_header = (work / 'native/video720_posters.h').read_text(encoding='utf-8')
    symbols = re.findall(r'extern const unsigned char (\w+)\[\];', poster_header)
    stubs = work / 'tests/poster_symbols.cpp'
    stubs.write_text('extern "C" {\n' + '\n'.join(
        'extern const unsigned char ' + name + '[]={0};' for name in symbols) + '\n}\n', encoding='utf-8')
    run(common + [test_sources['r71Routes']['path'], stubs, '-o', work / 'tests/routes.exe'], 'routes-compile')
    routes = run([work / 'tests/routes.exe'], 'routes-test')
    require(routes.startswith('PASS '), 'Historical route test failed')
    run(common + [test_sources['r69Corners']['path'], '-o', work / 'tests/corners.exe'], 'corners-compile')
    corners = run([work / 'tests/corners.exe'], 'corners-test')
    require(corners.startswith('PASS 66 '), 'Corner regression failed')
    run(common + [test_sources['r55Decoder']['path'], '-o', work / 'tests/decoder.exe'], 'decoder-compile')
    decoder = run([work / 'tests/decoder.exe'], 'decoder-test')
    run(common + ['-Wno-unused-function', '-fsyntax-only', test_sources['r70Settings']['path']], 'settings-test')
    # Preserve the original R70 harness flags: it intentionally casts native ABI signatures.
    navigation_flags = [host, '-std=c++17', '-O2', '-finput-charset=UTF-8',
                        '-fexec-charset=UTF-8', '-I', work / 'native']
    run(navigation_flags + [test_sources['r70Navigation']['path'], '-o', work / 'tests/navigation.exe'],
        'navigation-compile')
    navigation = run([work / 'tests/navigation.exe'], 'navigation-test')
    require(navigation.startswith('PASS 3584 '), 'Navigation regression failed')

    command[command.index(source_arg)] = str(work / 'native/native_carousel.cpp')
    command[command.index(output_arg)] = str(work / 'libturbo_carousel.so')
    dependencies = quoted_dependencies(work / 'native/native_carousel.cpp', includes)
    require(len(dependencies) == len(original_dependencies), 'Dependency set size changed')
    for path, expected in original_dependencies.items():
        original = Path(path)
        relative = original.relative_to(BASE / 'native') if original.is_relative_to(BASE / 'native') else None
        equivalent = work / 'native' / relative if relative is not None else original
        target_sha = FIXED_HEADER_SHA if relative == Path('collection_video_policy.h') else expected
        require(dependencies.get(str(equivalent.resolve())) == target_sha,
                'Dependency changed beyond repaired header: ' + path)
    run(command, 'carousel-build')
    output = work / 'libturbo_carousel.so'
    elf = run([compiler.parent / 'llvm-readelf.exe', '-h', '-l', output], 'elf-check')
    aligns = [int(line.split()[-1], 16) for line in elf.splitlines() if line.strip().startswith('LOAD ')]
    require('AArch64' in elf and aligns and min(aligns) >= 16384, 'Invalid ELF/16KiB alignment')
    syms = run([compiler.parent / 'llvm-nm.exe', '--defined-only', '--print-size', output], 'poster-symbol-check')
    line = next(line for line in syms.splitlines() if line.endswith(' station_collection_r71_snes_all'))
    require(int(line.split()[1], 16) == 720 * 720 * 2, 'Dedicated SNES poster changed')
    require(sha(output) != BASE_NATIVE_SHA, 'Native output unexpectedly unchanged')
    require(sha(overlay) == FIXED_HEADER_SHA and sha(__file__) == recipe_sha, 'Inputs changed during build')
    require(sources == {p.name: sha(p) for p in (work / 'native').iterdir() if p.is_file()},
            'Composed sources changed during build')
    require(dependencies == quoted_dependencies(work / 'native/native_carousel.cpp', includes),
            'Include dependencies changed during build')
    for path, expected in receipt['objects'].items():
        require(sha(path) == expected, 'Object changed during build: ' + path)
    for info in test_sources.values():
        require(sha(info['path']) == info['sha256'], 'Historical test changed during build')

    record = {
        'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'compiled': True,
        'base': 'Final R71 carousel preserved in R74', 'baseDirectory': str(BASE),
        'baseReceiptSHA256': BASE_RECEIPT_SHA, 'baseNativeSHA256': BASE_NATIVE_SHA,
        'baselineReproductionSHA256': reproduced_sha, 'nativeSHA256': sha(output),
        'nativeBytes': output.stat().st_size, 'nativeSources': sources,
        'changedNativeSources': changed, 'addedNativeSources': [],
        'baseQuotedDependencies': original_dependencies, 'quotedDependencies': dependencies,
        'objects': receipt['objects'], 'command': command, 'baselineCommand': baseline_command,
        'compilerSHA256': compiler_sha, 'hostCompilerSHA256': host_sha,
        'historicalTestSources': test_sources, 'executions': executions,
        'routeResult': routes, 'cornerPolicyResult': corners, 'navigationResult': navigation,
        'oneDecoderPolicyPassed': True, 'decoderResult': decoder, 'settingsSyntaxPassed': True,
        'frameMetadataSlots': 58, 'packagedPosterCount': 58, 'menuTargetFPS': 30,
        'frameRatePolicyUnchanged': True, 'mainPlatformSourceUnchanged': True,
        'snesAllVideoRoutePreserved': True, 'snesBRAliasUnchanged': True,
        'minimumLoadAlignment': min(aligns), 'buildRecipeSHA256': recipe_sha,
        'externalCatalogTests': 'Separate tests/run_tests.py receipt required before packaging',
        'packaged': False, 'installed': False, 'visualPlaybackVerified': False,
    }
    write_json(work / 'evidence/build.json', record)
    (SNAPSHOT / 'evidence').mkdir(exist_ok=True)
    write_json(SNAPSHOT / 'evidence/carousel-build-r75.json', record)
    print(json.dumps({'compiled': True, 'nativeSHA256': record['nativeSHA256'],
                      'receipt': str(work / 'evidence/build.json'),
                      'receiptSHA256': sha(work / 'evidence/build.json'),
                      'routeResult': routes, 'cornerPolicyResult': corners,
                      'navigationResult': navigation}, ensure_ascii=True))


if __name__ == '__main__':
    main()
