"""Frozen R145 sky/background and explicitly requested console band design.

Reproduce R133, replay the retained R134 labels, then reproduce the actual
R144 carousel with its frozen headers and 158 retained inputs. Apply only the
reviewed three-header R145 inverse after the complete donor equals R144.
No compilation is permitted from a private preparation or an unfrozen scope.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import re
import subprocess
import zipfile

import common

ROOT, REPO = common.ROOT, common.REPO
PARENT = REPO / 'integration/wave-palette-r144-20261013-final'
FRONTEND_SHA = '4e7ad58e1e8f8a284654120c27280eed8c124ad5301a9e87d769e41f100d8d0d'
R133_SHA = 'baf0f07c89b2a0a8e788b211809c389511830805f386647461487706bcdb9709'
R143_SHA = '867d86a5dba085fadec1e4b8dee0f8be99467551ba830607d3041b324c02b80e'
THEME_SHA = '8a156447f7c8a8497acbfb863bd6898b10c2a7403a83f3b9afcd4fa15f6bd058'
HEADERS = ('native_space.h', 'station_wave_palette.h', 'station_theme_palette.h')
REQUESTED = {0, 1, 2, 6, 7, 12, 16, 17}
EXPECTED_REQUESTS = {
    0: (['FF4058B0', 'EE5B67A0', 'A7B3C390'], [1, 1, 1]),
    1: (['FFDA52B0', '44D98AA0', '369DFF90', 'FF405890', 'FFDA5290'], [.5, 1, 1, 1, .5]),
    2: (['FFDA52B0', '44D98AA0', 'AA7DFF90', 'A7B3C390'], [1, 1, 1, 1]),
    6: (['FF4058B0', '369DFFA0', 'FFDA5290'], [1, 1, 1]),
    7: (['FF4058B0', '369DFFA0', 'FFDA5290'], [1, 1, 1]),
    12: (['44D98AB0', '369DFFA0', 'FF405890', 'FFDA5290', 'FF944890'], [1, 1, 1, 1, 1]),
    16: (['AA7DFFB0', 'FF4058A0', 'A7B3C390'], [1, 1, 1]),
    17: (['44D98AB0', 'FFDA52A0', 'FF944890'], [1, 1, 1]),
}
NEW_ALIASES = [('Nintendinho', 16), ('nes', 16), ('Nintendo Entertainment System', 16), ('Nintendo NES', 16),
               ('fbneo', 17), ('Final Burn Neo', 17), ('FinalBurn Neo', 17), ('final-burn-neo', 17)]
CURVE = b'float u=i/32.f,x=w*u,y=h*(.47f+wave*.065f+flightSin(u*5.5f+t*.32f+wave*.7f)*.075f+flightSin(u*2.1f-t*.19f)*.025f);'
need, sha, digest, read, canonical = common.need, common.sha, common.digest, common.read, common.canonical


def source_map():
    """Native subset only; common.verify_commit pins every consumed source/evidence."""
    return {'native/' + name: sha(ROOT / 'native' / name) for name in HEADERS} | {
        'recipe/build_native.py': sha(Path(__file__))}


def write(path, value):
    need(not path.exists(), 'Refusing to overwrite native build receipt: ' + path.name)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def parent_module():
    # This whole productive parent map is fixed in reviewed common.py. Confirm
    # that the bytes were committed at R144's actual executable-source commit.
    common.verify_parent_sources()
    prefix = PARENT.relative_to(REPO).as_posix()
    for name, expected in common.PARENT_SOURCE_FILES.items():
        result = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                                 'show', common.BASE_SOURCE + ':' + prefix + '/' + name],
                                capture_output=True, timeout=90)
        need(result.returncode == 0 and digest(result.stdout) == expected,
             'Pinned R144 source must equal its actual committed bytes: ' + name)
    path = PARENT / 'recipe/build_native.py'
    spec = importlib.util.spec_from_file_location('r145_pinned_r144_native', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(module.R133_SHA == R133_SHA and module.R143_SHA == R143_SHA and
         module.FRONTEND_SHA == FRONTEND_SHA and len(module.TOOLS) == 3, 'Pinned original native recipe constants changed')
    return module


def qualified_parent(args, parent):
    need(sha(args.parent_r144_native_receipt) == common.PARENT_NATIVE_RECEIPT_SHA and
         sha(args.parent_r144_final_proof) == common.PARENT_FINAL_PROOF_SHA,
         'Exact completed R144 native and signed final receipts required')
    native, proof = read(args.parent_r144_native_receipt), read(args.parent_r144_final_proof)
    need(native.get('passed') is True and native.get('compiled') is True and native.get('revision') == 'R144' and
         native.get('sourceCommit') == proof.get('sourceCommit') == common.BASE_SOURCE and
         native.get('outputNativeSha256') == common.CAROUSEL_SHA and proof.get('passed') is True and
         proof.get('apkSha256') == common.BASE and proof.get('sourceFiles') == common.PARENT_SOURCE_FILES and
         native.get('nativeToolSha256') == parent.TOOLS and native.get('exportsExactlyPreserved') is True and
         native.get('dependenciesExactlyPreserved') is True and native.get('sonameExactlyPreserved') is True,
         'Completed actual R144 parent proof differs')
    need(len(native.get('inputSha256', {})) == 158 and
         digest(canonical(native['inputSha256'])) == common.PARENT_NATIVE_INPUT_MAP_SHA and
         set(native['inputSha256']) == set(native.get('inputPaths', {})), 'Exact retained 158-input parent map required')
    _, paths = parent.checked_inputs(args)
    input_map = {name: sha(path) for name, path in paths.items()}
    need(input_map == native['inputSha256'], 'Actual resolved native inputs must equal every retained R144 pin')
    return native, proof, paths, input_map


def palette_rows(raw):
    rows = re.findall(rb'^\s*\{(\d+),\{([^\n]+?)\},\{([^\n]+?)\}\}, // ([^\n]+)', raw, re.M)
    result = []
    for count, colors, widths, _ in rows:
        rgba = [int(value.rstrip(b'u'), 16) if value.startswith(b'0x') else int(value.rstrip(b'u')) for value in colors.split(b',')]
        multipliers = [float(value.rstrip(b'f')) for value in widths.split(b',')]
        need(len(rgba) == len(multipliers) == 5, 'Each native palette must use fixed five-slot arrays')
        result.append((int(count), rgba, multipliers))
    return result


def aliases(raw):
    start = raw.index(b'static const StationWaveAlias stationWaveAliases[]={')
    end = raw.index(b'};\n// presentationKeyEqual', start)
    return [(key.decode('utf-8'), int(index)) for key, index in re.findall(rb'\{"([^\"]+)",(\d+)\}', raw[start:end])]


def qualify_visual(paths):
    old = {'native_space.h': (PARENT / 'native/native_space.h').read_bytes(),
           'station_wave_palette.h': (PARENT / 'native/station_wave_palette.h').read_bytes(),
           'station_theme_palette.h': paths['native:d0/station_theme_palette.h'].read_bytes()}
    need(digest(old['station_theme_palette.h']) == THEME_SHA, 'Unchanged original central theme header required')
    proposed = {name: (ROOT / 'native' / name).read_bytes() for name in HEADERS}
    scope = read(ROOT / 'evidence/native-visual-scope.json')
    spec = read(ROOT / 'evidence/native-palette-spec.json')
    inverse = read(ROOT / 'evidence/native-inverse-map.json')
    need(scope.get('schema') == 'station.r145.native.visual.scope.v1' and
         scope.get('baselineExecutableSourceCommit') == common.BASE_SOURCE and
         scope.get('baselineNativeSha256') == common.CAROUSEL_SHA and
         scope.get('defaultBandCount') == 3 and scope.get('maximumApprovedBandCount') == 5 and
         spec.get('schema') == 'station.r145.native.palette-spec.v1' and
         spec.get('baselineSourceCommit') == common.BASE_SOURCE and spec.get('maxBands') == 5 and
         spec.get('segmentsPerBand') == 32 and spec.get('fixedStackVertices') == 66 and
         spec.get('alphaByBandHex') == ['B0', 'A0', '90', '90', '90'] and
         inverse.get('schema') == 'station.r145.native.inverse-map.v1' and set(inverse.get('files', {})) == set(HEADERS),
         'Reviewed native sky-blue and requested band scope required')
    declared_headers = {item['file']: item for item in scope.get('sourceHeaders', [])}
    need(set(declared_headers) == set(HEADERS), 'Scope must declare exactly the three reviewed native headers')
    for name in HEADERS:
        record = inverse['files'][name]
        need(record.get('baselineSha256') == digest(old[name]) and record.get('proposedSha256') == digest(proposed[name]),
             'Native inverse file hashes differ: ' + name)
        declaration = declared_headers[name]
        need(declaration.get('baselineSha256') == record['baselineSha256'] and
             declaration.get('proposedSha256') == record['proposedSha256'] and
             declaration.get('replacementBlockCount') == len(record['replacements']) and
             declaration.get('wholeFileInversePassed') is True,
             'Header source must equal the independently reviewed visual scope: ' + name)
        baseline_copy = ROOT / 'evidence' / ('native-baseline-r144-' + name)
        need(baseline_copy.read_bytes() == old[name], 'Retained source baseline is not the real R144 header: ' + name)
        restored = proposed[name]
        for item in reversed(record['replacements']):
            before, after = item['before'].encode('utf-8'), item['after'].encode('utf-8')
            need(restored.count(after) == 1, 'Exactly one inverse block occurrence required: ' + name)
            restored = restored.replace(after, before, 1)
        need(restored == old[name], 'Whole native header inverse failed: ' + name)
    # Protect the backdrop mask and all native-space behavior outside the reviewed
    # appearance selector/renderer block, including loading/OFF/timing selection.
    marker = b'// The existing appearance theme'
    need(proposed['native_space.h'].split(marker, 1)[0] == old['native_space.h'].split(marker, 1)[0],
         'Diagonal mask/backdrop helpers must remain byte exact')
    marker = b'static void drawNativeSpace('
    need(proposed['native_space.h'].split(marker, 1)[1] == old['native_space.h'].split(marker, 1)[1],
         'Complete native-space entry and scheduling must remain byte exact')
    need(old['native_space.h'].count(CURVE) == proposed['native_space.h'].count(CURVE) == 1,
         'Original wave-center sine/phase/time equation required')
    start = b'static const char* stationWaveSystemKey()'
    old_key = old['native_space.h'].split(start, 1)[1].split(b'static unsigned stationWaveColor(', 1)[0]
    new_key = proposed['native_space.h'].split(start, 1)[1].split(b'static const StationWavePalette* stationWaveCurrentPalette(', 1)[0]
    need(old_key == new_key, 'Original platform-selection accessor/guards must remain byte exact')
    # The blue-only branch replacements are explicitly fixed; global color mapping,
    # black branches and alpha FF cannot be repurposed as a broader theme rewrite.
    for name, replacements in {'native_space.h': [(b'0x050A15ffu', b'0x287EB5ffu'), (b'0x081827ffu', b'0x5DAEDEffu')],
                               'station_theme_palette.h': [(b'0x0B4B83ffu', b'0x287EB5ffu'), (b'0x267CBBffu', b'0x5DAEDEffu')]}.items():
        need(all(old[name].count(before) == proposed[name].count(after) == 1 for before, after in replacements),
             'Only the requested sky-blue background literal sites may change')
    theme_inverse = proposed['station_theme_palette.h'].replace(b'0x287EB5ffu', b'0x0B4B83ffu').replace(b'0x5DAEDEffu', b'0x267CBBffu')
    need(theme_inverse == old['station_theme_palette.h'], 'Central theme must differ by exactly the two blue RGB literals')
    parsed = palette_rows(proposed['station_wave_palette.h'])
    plans = spec.get('palettes', [])
    old_rows = re.findall(rb'\{\{([^\n]+?)\}\}, //', old['station_wave_palette.h'])
    need(len(parsed) == len(plans) == 18 and len(old_rows) == 16, 'Exactly 16 inherited plus two requested families required')
    for index, ((count, colors, widths), plan) in enumerate(zip(parsed, plans)):
        need(plan['index'] == index and count == plan['count'] and 3 <= count <= 5 and
             colors[:count] == [int(value, 16) for value in plan['rgba']] and
             widths[:count] == plan['widthMultipliers'] and colors[count:] == [0] * (5 - count) and
             widths[count:] == [1] * (5 - count) and
             [value & 255 for value in colors[:count]] == [176, 160, 144, 144, 144][:count], 'Native palette/spec differs')
        if index in REQUESTED:
            rgba, wanted_widths = EXPECTED_REQUESTS[index]
            need(plan.get('changedFromR144') is True and plan['rgba'] == rgba and widths[:count] == wanted_widths,
                 'Requested console palette/count/width differs')
        else:
            baseline = [int(value.rstrip(b'u'), 16) for value in old_rows[index].split(b',')]
            need(plan.get('changedFromR144') is False and count == 3 and colors[:3] == baseline and widths[:3] == [1, 1, 1],
                 'Unrequested console family must keep its exact R144 colors/count/width')
    need(aliases(proposed['station_wave_palette.h']) == aliases(old['station_wave_palette.h']) + NEW_ALIASES,
         'All inherited aliases/order must remain; only reviewed NES/FBNeo aliases may append')
    need({item['index'] for item in scope['requestedConsoleProfiles']} == REQUESTED and
         scope['requestedConsoleProfiles'] == [item for item in plans if item['changedFromR144']], 'Scope/spec console declarations differ')
    return old, proposed, {
        'wholeHeaderInversePassed': True, 'drawNativeSpaceByteIdentical': True,
        'diagonalBackdropByteIdentical': True, 'waveCurveTimingEquationByteIdentical': True,
        'unrequestedPalettesCountsWidthsPreserved': True, 'requestedPaletteSpecVerified': True,
        'onlyApprovedNativeVisualBlocksChanged': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base-apk', 'native-inputs', 'generated-native', 'media-inputs', 'ndk', 'out',
                 'parent-r144-native-receipt', 'parent-r144-final-proof'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--r133-native', '--parent-native', dest='parent_native', type=Path, required=True,
                        help='Exact original R133 native build directory with pinned receipt and overlay')
    parser.add_argument('--input-map', type=Path, help='Optional relocated original 153-input map; all retained SHA pins remain mandatory')
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    pins = common.verify_commit(args.source_commit)
    native_pins = source_map()
    need(all(pins.get(name) == checksum for name, checksum in native_pins.items()), 'Native subset differs from full frozen R145 source map')
    need(args.base_apk.is_file() and args.base_apk.stat().st_size == common.BASE_BYTES and sha(args.base_apk) == common.BASE,
         'Exact signed actual R144 donor required')
    parent = parent_module()
    parent_native, _, paths, input_map = qualified_parent(args, parent)
    originals, proposed, transforms = qualify_visual(paths)
    out = common.isolated(args.out)
    tool = args.ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin'
    need(all(sha(tool / name) == checksum for name, checksum in parent.TOOLS.items()), 'Pinned original NDK compiler/inspectors required')
    out.mkdir(parents=True)
    (out / 'temp').mkdir()
    commands = []

    def run(command, label):
        command = list(map(str, command))
        commands.append({'label': label, 'command': command})
        result = subprocess.run(command, cwd=out, capture_output=True, timeout=1800,
                                env={**os.environ, 'TEMP': str(out / 'temp'), 'TMP': str(out / 'temp')})
        (out / (label + '.log')).write_bytes(result.stdout + result.stderr)
        need(result.returncode == 0, 'Native tool failed: ' + label + '; private log retained')
        return result.stdout.decode('utf-8', 'replace')

    flags = [tool / 'clang++.exe', '--target=aarch64-linux-android26', '-std=c++17', '-shared', '-fPIC', '-O2',
             '-Wl,-z,max-page-size=16384', '-Wl,--no-undefined', '-nostdlib', '-fno-exceptions', '-fno-rtti',
             '-fno-stack-protector', '-fno-builtin', '-Wl,-soname,libturbo_carousel.so']
    r133_overlay = args.parent_native / 'overlay'
    r132_overlay = paths['parent-overlay:native_carousel.cpp'].parent
    include_dirs = [r133_overlay, r132_overlay, args.generated_native, args.media_inputs / 'include',
                    REPO / 'integration/ps3-ps4-offline/native', parent.R124 / 'd0',
                    args.native_inputs / 'd0', args.native_inputs / 'd2', args.native_inputs / 'd1']
    includes = [value for directory in include_dirs for value in ('-I', directory)]
    objects = [paths['native:' + name] for name in ('d1/video720_posters.o', 'd3/collection_previews.o', 'd4/lottie_frames.o')]
    media = read(args.media_inputs / 'sony-media.json')
    objects += [args.media_inputs / name for name in media['extraObjects']]
    tail = ['-L', args.native_inputs / 'd1', '-lc', '-ldl', '-llog', paths['native:d5/installed_art.o']]
    last = [paths['native:' + name] for name in ('d6/collection_previews.o', 'd7/collection_previews.o', 'd8/collection_previews.o')]
    cpp = r133_overlay / 'native_carousel.cpp'

    def compile_overlay(overlay, output, label):
        prefix = [] if overlay is None else ['-I', overlay]
        run(flags + prefix + includes + [cpp] + objects + tail + ['-o', output] + last, label)

    r133 = out / 'baseline-r133.so'
    compile_overlay(None, r133, 'baseline-r133')
    need(sha(r133) == R133_SHA, 'R133 native donor must reproduce byte exactly')
    r143_raw, original_labels = parent.patch_labels(r133.read_bytes())
    need(digest(r143_raw) == R143_SHA, 'R134 labels must recover the original R143 native donor byte exactly')
    (out / 'baseline-r143.so').write_bytes(r143_raw)
    r144_overlay = out / 'baseline-r144-overlay'
    r144_overlay.mkdir()
    (r144_overlay / 'native_skin.h').write_bytes(paths['native:d0/native_skin.h'].read_bytes())
    for name in ('native_space.h', 'station_wave_palette.h'):
        (r144_overlay / name).write_bytes(originals[name])
    r144_unlabelled = out / 'baseline-r144-unlabelled.so'
    compile_overlay(r144_overlay, r144_unlabelled, 'baseline-r144')
    r144_raw, r144_labels = parent.patch_labels(r144_unlabelled.read_bytes())
    need(digest(r144_raw) == common.CAROUSEL_SHA, 'Complete actual R144 native donor must reproduce byte exactly')
    r144 = out / 'baseline-r144.so'
    r144.write_bytes(r144_raw)
    with zipfile.ZipFile(args.base_apk) as archive:
        need(archive.read(common.CAROUSEL) == r144_raw, 'Actual signed R144 carousel differs from reproduced full bytes')
        need(digest(archive.read('lib/arm64-v8a/libstation_frontend.so')) == FRONTEND_SHA, 'Original frontend must remain exact')
    overlay = out / 'overlay'
    overlay.mkdir()
    (overlay / 'native_skin.h').write_bytes(paths['native:d0/native_skin.h'].read_bytes())
    for name in HEADERS:
        (overlay / name).write_bytes(proposed[name])
    unlabelled = out / 'unlabelled-r145.so'
    compile_overlay(overlay, unlabelled, 'sky-blue-bands-r145')
    final_raw, labels = parent.patch_labels(unlabelled.read_bytes())
    final = out / 'libturbo_carousel.so'
    final.write_bytes(final_raw)
    need(sha(final) != common.CAROUSEL_SHA, 'The reviewed visual overlay must change the native payload')
    before_elf, after_elf = common.elf_contract(r144_raw), common.elf_contract(final_raw)
    need(before_elf['exports'] == after_elf['exports'] and len(after_elf['exports']) == 33 and
         before_elf['needed'] == after_elf['needed'] and before_elf['soname'] == after_elf['soname'] == ['libturbo_carousel.so'] and
         after_elf['minimumLoadAlignment'] == 16384, 'Original native exports/dependencies/SONAME and 16KiB LOAD contract required')
    names = sorted(row[0] for row in after_elf['exports'])
    need(names == parent_native['exportedSymbols'], 'Export names differ from the exact R144 receipt')
    # Original LLVM inspections remain recorded independently of the Python ELF reader.
    run([tool / 'llvm-nm.exe', '--dynamic', '--defined-only', final], 'new-exports')
    run([tool / 'llvm-readelf.exe', '-dW', final], 'new-dynamic')
    run([tool / 'llvm-readelf.exe', '-lW', final], 'loads')
    need(source_map() == native_pins and common.source_map() == pins and
         all(sha(path) == input_map[name] for name, path in paths.items()) and
         sha(args.parent_r144_native_receipt) == common.PARENT_NATIVE_RECEIPT_SHA and
         sha(args.parent_r144_final_proof) == common.PARENT_FINAL_PROOF_SHA and
         all(sha(tool / name) == checksum for name, checksum in parent.TOOLS.items()),
         'Frozen sources, retained inputs, parent receipts or compiler changed during compilation')
    common.verify_parent_sources()
    report = {'schema': 'station.r145.native.sky-blue-bands.v1', 'revision': 'R145', 'passed': True, 'compiled': True,
              'sourceCommit': args.source_commit, 'sourceSha256': native_pins, 'completeFrozenSourceFiles': pins,
              'baseApkSha256': common.BASE, 'baselineNativeSha256': common.CAROUSEL_SHA,
              'baselineReproduced': {'r144Carousel': True},
              'intermediateBaselineReproduced': {'r133Carousel': True, 'r143Carousel': True},
              'intermediateBaselineSha256': {'r133': R133_SHA, 'r143': R143_SHA},
              'retainedParentNativeReceiptSha256': common.PARENT_NATIVE_RECEIPT_SHA,
              'retainedParentFinalProofSha256': common.PARENT_FINAL_PROOF_SHA,
              'retainedInputSha256': input_map, 'retainedInputPaths': {name: str(path.resolve()) for name, path in paths.items()},
              'nativeToolSha256': parent.TOOLS, 'scopeDeclarationSha256': sha(ROOT / 'evidence/native-visual-scope.json'),
              'paletteSpecSha256': sha(ROOT / 'evidence/native-palette-spec.json'),
              'nativeInverseMapSha256': sha(ROOT / 'evidence/native-inverse-map.json'),
              'transforms': {'native': transforms}, 'baselineR143Labels': original_labels,
              'baselineR144Labels': r144_labels, 'retainedR134Labels': labels,
              'dexChanged': False, 'frontendChanged': False, 'exportsExactlyPreserved': True, 'exportedSymbols': names,
              'dependenciesExactlyPreserved': True, 'sonameExactlyPreserved': True, 'nativeLoadAlignment': '0x4000',
              'dynamicContract': {'needed': after_elf['needed'], 'soname': after_elf['soname']},
              'physicalVisualValidated': False, 'actualPerformanceMeasured': False,
              'maximumApprovedWaveBands': 5, 'fixedStackVertexCount': 66,
              'requestedWorstCaseGeneratedVertices': 330, 'r144GeneratedVertices': 198,
              'outputNativeSha256': sha(final), 'payloads': {common.CAROUSEL: {'path': str(final.resolve()),
                                                                         'bytes': final.stat().st_size, 'sha256': sha(final)}}}
    write(out / 'commands.json', commands)
    write(out / 'native-receipt.json', report)
    print(json.dumps({'revision': 'R145', 'passed': True, 'baselineReproduced': report['baselineReproduced'],
                      'payloads': report['payloads'], 'physicalVisualValidated': False}))


if __name__ == '__main__':
    main()
