"""Reproduce the R143 carousel, then change only the WAVES color selector.

The R133 baseline is compiled from pinned complete inputs; the R134 equal-size
settings labels are replayed and the result must equal the actual R143 ELF.
No frontend, engine, shader, media, geometry, timer or DEX is rebuilt here.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
R124 = REPO / 'versions/station-video-room-footer-r124-20261011/native'
DONOR_SHA = '508480e3671ae924f037bd32f6d71efda7a9d905c45c7b2571bd9f219add83d4'
DONOR_BYTES = 2715024399
R133_SHA = 'baf0f07c89b2a0a8e788b211809c389511830805f386647461487706bcdb9709'
R143_SHA = '867d86a5dba085fadec1e4b8dee0f8be99467551ba830607d3041b324c02b80e'
FRONTEND_SHA = '4e7ad58e1e8f8a284654120c27280eed8c124ad5301a9e87d769e41f100d8d0d'
RECEIPT_SHA = 'cc2545ff817bf86b7fbe5d49405f6a7d859ed89404965bd7fde8e1a5062e6f70'
CPP_SHA = 'c8ce063f7b1459553b39f4169507ef1a51f7f5b61fb5fb9398e0ac7bf0a36ec2'
SPACE_SHA = 'd3297d51c445a603321675b70c1b8016fdc8563597a6c78d2ddaa482d8f392c1'
OFFLINE_ROUTES_SHA = '085b5a630aa4a6e18673bebd69c9bd82609259ba1e842c579ffeb894ff3ffadb'
TOOLS = {'clang++.exe': '1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3',
         'llvm-nm.exe': '90236526ebb24c232e59ec573675e32a92190b3346cf3a342c8b0eb5ad0f8203',
         'llvm-readelf.exe': '2646e382d8b2559b5c4ae91e9a98e187ed9bd59f23936054d424049ef795ba5e'}
LABELS = [('PS3 • ABRIR EMULADOR', 'PS3 • CONFIGURAÇÃO'),
          ('PS4 • ABRIR EMULADOR', 'PS4 • CONFIGURAÇÃO')]
OLD_SELECTOR = b'static unsigned stationWaveColor(int wave){return stationThemeId==1?(wave==0?0x65BFF030u:wave==1?0x6587DE26u:0x9DCBDD1Eu):(wave==0?0x8193A630u:wave==1?0x59677526u:0x9DA8B11Eu);}'


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    require(not path.exists(), 'Refusing to overwrite receipt: ' + path.name)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def source_map():
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / 'native').glob('*.h'))} | {
        'recipe/build_native.py': sha(Path(__file__))}


def verify_source(commit, pins):
    require(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit), 'Full frozen source commit required')
    prefix = ROOT.relative_to(REPO).as_posix()
    git = ['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO)]
    for name, checksum in pins.items():
        raw = subprocess.check_output(git + ['show', commit + ':' + prefix + '/' + name], stderr=subprocess.PIPE)
        require(digest(raw) == checksum, 'Source differs from selected committed bytes: ' + name)


def patch_labels(raw):
    require(raw[:7] == b'\x7fELF\x02\x01\x01' and struct.unpack_from('<H', raw, 18)[0] == 183,
            'AArch64 little-endian ELF64 required')
    table = struct.unpack_from('<Q', raw, 32)[0]
    size, count = struct.unpack_from('<HH', raw, 54)
    require(size == 56 and 0 < count <= 128 and table + size * count <= len(raw), 'Valid ELF64 LOAD table required')
    loads = [struct.unpack_from('<IIQQQQQQ', raw, table + size * index) for index in range(count)]
    loads = [row for row in loads if row[0] == 1]
    require(loads and all(row[7] >= 16384 and (row[2] - row[3]) % 16384 == 0 for row in loads),
            'Existing native 16KiB alignment required')
    result = bytearray(raw)
    changes = []
    for old, new in LABELS:
        before, after = old.encode('utf-8'), new.encode('utf-8')
        require(len(before) == len(after) == 22 and raw.count(before + b'\0') == 1,
                'Unique complete equal-size settings label required')
        offset = raw.index(before + b'\0')
        require(any(row[2] <= offset and offset + 22 < row[2] + row[5] and not row[1] & 2 for row in loads),
                'Settings labels must remain complete strings in read-only LOAD memory')
        result[offset:offset + 22] = after
        changes.append({'offset': offset, 'bytes': 22, 'fromText': old, 'toText': new})
    inverse = bytearray(result)
    for item, (old, _) in zip(changes, LABELS):
        inverse[item['offset']:item['offset'] + 22] = old.encode('utf-8')
    require(bytes(inverse) == raw, 'R134 label inverse must recover whole compiled ELF')
    require(bytes(result[:64]) == raw[:64] and bytes(result[table:table + size * count]) == raw[table:table + size * count],
            'Equal-size label patch must preserve ELF header and LOAD table')
    return bytes(result), changes


def checked_inputs(args):
    receipt_path = args.parent_native / 'native-receipt.json'
    require(sha(receipt_path) == RECEIPT_SHA, 'Exact R133 native receipt required')
    receipt = read(receipt_path)
    remapped = read(args.input_map) if args.input_map else {}
    require(isinstance(remapped, dict) and set(remapped) <= set(receipt['inputSha256']), 'Known donor input mappings only')
    paths = {}
    for key, expected in receipt['inputSha256'].items():
        if key in remapped:
            require(isinstance(remapped[key], str), 'Mapped input path must be text: ' + key)
            path = Path(remapped[key])
        elif key.startswith('native:'):
            name = key[7:]
            public = R124 / name
            path = public if public.is_file() else args.native_inputs / name
        elif key.startswith('generated:'):
            path = args.generated_native / key[10:]
        elif key.startswith('media:'):
            path = args.media_inputs / key[6:]
        else:
            path = Path(receipt['inputPaths'][key])
        require(path.is_file() and not path.is_symlink() and sha(path) == expected, 'Frozen input differs: ' + key)
        paths[key] = path
    # These generated R133 files are the donor source, and must match transform pins.
    overlay = args.parent_native / 'overlay'
    expected_overlay = {'native_carousel.cpp': receipt['transforms']['consolePanel']['nativeCppSha256'],
                        **receipt['transforms']['consolePanel']['outputHeaderSha256']}
    require({p.name for p in overlay.iterdir() if p.is_file()} == set(expected_overlay), 'Closed R133 overlay required')
    for name, expected in expected_overlay.items():
        path = overlay / name
        require(sha(path) == expected, 'Generated R133 overlay differs: ' + name)
        paths['r133-overlay:' + name] = path
    require(sha(overlay / 'native_carousel.cpp') == CPP_SHA and sha(paths['native:d0/native_space.h']) == SPACE_SHA,
            'Exact donor CPP and wave header required')
    routes = REPO / 'integration/ps3-ps4-offline/native/offline_routes.h'
    require(sha(routes) == OFFLINE_ROUTES_SHA, 'Pinned unchanged Sony offline routes required')
    paths['source:offline_routes.h'] = routes
    return receipt, paths


def scope_inverse(original, changed):
    begin = changed.index(b'#include "station_wave_palette.h"')
    end = changed.index(b'// Three thin triangle strips', begin)
    original_end = original.index(b'// Three thin triangle strips')
    old_begin = original.index(OLD_SELECTOR)
    require(original.count(OLD_SELECTOR) == 1 and changed.count(b'#include "station_wave_palette.h"') == 1,
            'One closed wave-selector substitution required')
    require(changed[:begin] == original[:old_begin] and changed[end:] == original[original_end:],
            'Wave geometry, timing, diagonal, loading and backgrounds must remain exact')
    require(changed[:begin] + original[old_begin:original_end] + changed[end:] == original,
            'Wave header inverse must recover every original byte')
    return {'wholeHeaderInversePassed': True, 'drawNativeWavesByteIdentical': True,
            'drawNativeSpaceByteIdentical': True, 'diagonalBackdropByteIdentical': True,
            'onlyColorSelectorBlockReplaced': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base-apk', 'parent-native', 'native-inputs', 'generated-native', 'media-inputs', 'ndk', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source-commit')
    parser.add_argument('--input-map', type=Path, help='Optional private logical-input/path map; all original SHA pins remain mandatory')
    parser.add_argument('--baseline-only', action='store_true')
    args = parser.parse_args()
    require(args.base_apk.is_file() and args.base_apk.stat().st_size == DONOR_BYTES and sha(args.base_apk) == DONOR_SHA,
            'Exact signed stable R143 donor required')
    pins = source_map()
    if not args.baseline_only:
        verify_source(args.source_commit, pins)
    receipt, paths = checked_inputs(args)
    tool = args.ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin'
    require(all(sha(tool / name) == expected for name, expected in TOOLS.items()), 'Exact NDK compiler and inspectors required')
    require(not args.out.exists(), 'Fresh output directory required')
    args.out.mkdir(parents=True)
    (args.out / 'temp').mkdir()
    commands = []

    def run(command, label):
        command = list(map(str, command))
        commands.append({'label': label, 'command': command})
        environment = {**os.environ, 'TEMP': str(args.out / 'temp'), 'TMP': str(args.out / 'temp')}
        result = subprocess.run(command, cwd=args.out, capture_output=True, env=environment, timeout=1800)
        (args.out / (label + '.log')).write_bytes(result.stdout + result.stderr)
        require(result.returncode == 0, 'Native tool failed: ' + label + '; see private log')
        return result.stdout.decode('utf-8', 'replace')

    flags = [tool / 'clang++.exe', '--target=aarch64-linux-android26', '-std=c++17', '-shared', '-fPIC', '-O2',
             '-Wl,-z,max-page-size=16384', '-Wl,--no-undefined', '-nostdlib', '-fno-exceptions', '-fno-rtti',
             '-fno-stack-protector', '-fno-builtin', '-Wl,-soname,libturbo_carousel.so']
    r133_overlay = args.parent_native / 'overlay'
    r132_overlay = paths['parent-overlay:native_carousel.cpp'].parent
    include_dirs = [r133_overlay, r132_overlay, args.generated_native, args.media_inputs / 'include',
                    REPO / 'integration/ps3-ps4-offline/native', R124 / 'd0',
                    args.native_inputs / 'd0', args.native_inputs / 'd2', args.native_inputs / 'd1']
    includes = [v for directory in include_dirs for v in ('-I', directory)]
    objects = [paths['native:' + name] for name in ('d1/video720_posters.o', 'd3/collection_previews.o', 'd4/lottie_frames.o')]
    media = read(args.media_inputs / 'sony-media.json')
    objects += [args.media_inputs / name for name in media['extraObjects']]
    tail = ['-L', args.native_inputs / 'd1', '-lc', '-ldl', '-llog', paths['native:d5/installed_art.o']]
    last = [paths['native:' + name] for name in ('d6/collection_previews.o', 'd7/collection_previews.o', 'd8/collection_previews.o')]
    baseline = args.out / 'baseline-r133.so'
    run(flags + includes + [r133_overlay / 'native_carousel.cpp'] + objects + tail + ['-o', baseline] + last, 'baseline-r133')
    require(sha(baseline) == R133_SHA, 'Complete R133 carousel must reproduce byte exactly')
    donor_raw, baseline_labels = patch_labels(baseline.read_bytes())
    require(digest(donor_raw) == R143_SHA, 'Replayed R134 labels must reproduce R143 carousel byte exactly')
    with zipfile.ZipFile(args.base_apk) as archive:
        require(archive.read('lib/arm64-v8a/libturbo_carousel.so') == donor_raw, 'Actual R143 donor carousel differs')
        require(digest(archive.read('lib/arm64-v8a/libstation_frontend.so')) == FRONTEND_SHA, 'Frontend donor changed')
    (args.out / 'baseline-r143.so').write_bytes(donor_raw)
    report = {'schema': 'station.wave.palette.native.v1', 'revision': 'R144', 'baseApkSha256': DONOR_SHA,
              'passed': True, 'compiled': not args.baseline_only, 'baselineNativeSha256': R143_SHA,
              'sourceCommit': args.source_commit, 'sourceSha256': pins, 'nativeToolSha256': TOOLS,
              'retainedParentNativeReceiptSha256': RECEIPT_SHA, 'baselineReproduced': {'r133Carousel': True, 'r143Carousel': True},
              'baselineR134Labels': baseline_labels, 'dexChanged': False, 'frontendChanged': False,
              'physicalVisualValidated': False, 'payloads': {}, 'inputSha256': {key: sha(path) for key, path in paths.items()},
              'inputPaths': {key: str(path.resolve()) for key, path in paths.items()}}
    if not args.baseline_only:
        wave_original = paths['native:d0/native_space.h'].read_bytes()
        wave_new = (ROOT / 'native/native_space.h').read_bytes()
        report['transforms'] = {'waves': scope_inverse(wave_original, wave_new)}
        overlay = args.out / 'overlay'
        overlay.mkdir()
        # Identical native_skin is routed through this output directory solely so
        # its quoted native_space include resolves to the one approved replacement.
        (overlay / 'native_skin.h').write_bytes(paths['native:d0/native_skin.h'].read_bytes())
        (overlay / 'native_space.h').write_bytes(wave_new)
        (overlay / 'station_wave_palette.h').write_bytes((ROOT / 'native/station_wave_palette.h').read_bytes())
        changed = args.out / 'unlabelled-r144.so'
        run(flags + ['-I', overlay] + includes + [r133_overlay / 'native_carousel.cpp'] + objects + tail + ['-o', changed] + last,
            'waves-r144')
        final_raw, final_labels = patch_labels(changed.read_bytes())
        final = args.out / 'libturbo_carousel.so'
        final.write_bytes(final_raw)
        report['retainedR134Labels'] = final_labels
        def exports(path, label):
            return sorted(line.split()[-1] for line in run([tool / 'llvm-nm.exe', '--dynamic', '--defined-only', path], label).splitlines()
                          if len(line.split()) >= 3)
        old_exports, new_exports = exports(baseline, 'baseline-exports'), exports(final, 'new-exports')
        require(old_exports == new_exports, 'Exported native API must be exact')
        def dynamic_contract(path, label):
            text = run([tool / 'llvm-readelf.exe', '-dW', path], label)
            return {'needed': sorted(re.findall(r'\(NEEDED\).*?\[(.*?)\]', text)),
                    'soname': re.findall(r'\(SONAME\).*?\[(.*?)\]', text)}
        old_dynamic = dynamic_contract(baseline, 'baseline-dynamic')
        new_dynamic = dynamic_contract(final, 'new-dynamic')
        require(old_dynamic == new_dynamic and new_dynamic['soname'] == ['libturbo_carousel.so'],
                'Existing native dependencies and SONAME must be exact')
        loads = re.findall(r'^\s*LOAD\s+.*\s(0x[0-9a-fA-F]+)\s*$', run([tool / 'llvm-readelf.exe', '-lW', final], 'loads'), re.M)
        require(loads and all(int(value, 16) >= 16384 for value in loads), '16KiB native LOAD alignment required')
        report.update(approvedScopes=['waves-platform-rgb-and-opacity-only'], exportedSymbols=new_exports,
                      exportsExactlyPreserved=True, nativeLoadAlignment='0x4000',
                      outputNativeSha256=sha(final),
                      dynamicContract=new_dynamic, dependenciesExactlyPreserved=True, sonameExactlyPreserved=True,
                      payloads={'lib/arm64-v8a/libturbo_carousel.so': {'path': str(final.resolve()),
                                                                 'bytes': final.stat().st_size, 'sha256': sha(final)}})
    require(source_map() == pins and all(sha(path) == report['inputSha256'][key] for key, path in paths.items()),
            'Pinned source or donor input changed during build')
    require(all(sha(tool / name) == expected for name, expected in TOOLS.items()), 'NDK tools changed during build')
    write(args.out / 'commands.json', commands)
    write(args.out / 'native-receipt.json', report)
    print(json.dumps({key: report[key] for key in ('revision', 'baselineReproduced', 'payloads', 'physicalVisualValidated')}))


if __name__ == '__main__':
    main()
