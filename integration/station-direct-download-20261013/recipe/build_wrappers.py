#!/usr/bin/env python3
"""Renew the existing bundle fingerprints after replacing only DEX28 HTTP transport.

The emulator cores and all PSX owner/protocol sources remain byte exact. N64 and
Dolphin libraries here contain identity exports only; this never rebuilds their cores.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

REPO = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parents[1]
BASE = '19acdeceef86bc66c2475300cbd142da783850c02f5a9e2068d8652ef8523164'
OLD_DEX = '6c9c2d6df00919ca4c927c3719b932ebfb1ef46b24f2de778120a84fd8d30225'
NAMES = {'psx': 'libstation_psx_online.so', 'n64': 'libstation_mupen64plus_runtime.so',
         'dolphin': 'libstation_dolphin_runtime.so'}
NATIVE_SOURCES = ('StationPsxEntry.cpp', 'StationPsxOwner.cpp', 'StationPsxProtocol.cpp',
                  'StationPsxSha256.cpp', 'StationPsxOwner.hpp', 'StationPsxProtocol.hpp', 'PsxPinnedOptions.h')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw): return hashlib.sha256(raw).hexdigest()


def sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def marker(binary):
    selected = []
    for match in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', binary):
        end = binary.find(b'\0', match.start())
        if end < 0: continue
        raw = binary[match.start():end]
        try: value = json.loads(raw)
        except (ValueError, UnicodeError): continue
        if isinstance(value, dict) and 'baseApkSha256' in value and 'payloadSha256' in value:
            need(raw == canonical(value) and digest(raw).encode('ascii') in binary, 'Original marker integrity differs')
            selected.append(value)
    need(len(selected) == 1, 'One original marker is required')
    return selected[0]


def policy(value):
    selected = copy.deepcopy(value)
    for key in ('baseApkSha256', 'payloadSha256', 'productiveTransforms', 'parentFingerprintSha256',
                'parentRuntimeSha256', 'psxRuntimeSha256'):
        selected.pop(key, None)
    return selected


def command(args, logfile):
    result = subprocess.run([str(arg) for arg in args], capture_output=True, text=True)
    logfile.write_text(result.stdout + result.stderr)
    need(result.returncode == 0, 'Native identity compilation failed; inspect private build log')
    need(not re.search(r'(?im)^.*\bwarning:', result.stderr), 'Native compiler warnings require review')


def metadata(path, tools):
    symbols = subprocess.check_output([str(tools / 'llvm-nm'), '-D', '--defined-only', str(path)], text=True)
    dynamic = subprocess.check_output([str(tools / 'llvm-readelf'), '--dynamic', str(path)], text=True)
    import struct
    raw = path.read_bytes()
    need(raw[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', raw, 18)[0] == 183, 'ARM64 ELF required')
    offset = struct.unpack_from('<Q', raw, 32)[0]
    size, count = struct.unpack_from('<HH', raw, 54)
    loads = [struct.unpack_from('<IIQQQQQQ', raw, offset + i * size) for i in range(count)]
    alignments = [record[-1] for record in loads if record[0] == 1]
    need(alignments and min(alignments) >= 16384, '16 KiB load alignment required')
    return {'exports': sorted(line.split()[-1] for line in symbols.splitlines() if line.strip()),
            'neededLibraries': sorted(re.findall(r'\(NEEDED\).*\[(.*?)\]', dynamic)),
            'soname': re.findall(r'\(SONAME\).*\[(.*?)\]', dynamic), 'minimumLoadAlignment': min(alignments)}


def build(args):
    need(not args.out.exists(), 'Fresh identity build output required')
    need(sha(args.donor) == BASE and sha(args.dex) != OLD_DEX, 'Exact R139 donor and changed DEX required')
    receipt = json.loads(args.dex_receipt.read_text())
    need(receipt['donorSha256'] == OLD_DEX and receipt['outputSha256'] == sha(args.dex) and
         receipt['unchangedClasses'] == 266 and receipt['testsPackaged'] is False, 'Scoped HTTP DEX proof required')
    tools = args.ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin'
    need('Pkg.Revision = 28.2.13676358' in (args.ndk / 'source.properties').read_text(),
         'The original NDK r28c is required to preserve the native ABI')
    native = REPO / 'integration/psx-online/native'
    previous, original = {}, {}
    with zipfile.ZipFile(args.donor) as archive:
        need(len(archive.namelist()) == len(set(archive.namelist())) == 13860, 'Donor entry inventory differs')
        engines = json.loads(archive.read('assets/station-online/engines.json'))
        for kind, name in NAMES.items():
            raw = archive.read('lib/arm64-v8a/' + name)
            previous[kind], original[kind] = marker(raw), raw
        payload = previous['psx']['payloadSha256']
        need(len(payload) == 345 and payload['classes28.dex'] == OLD_DEX, 'Original bound payload inventory differs')
        need(all(row['payloadSha256'] == payload for row in previous.values()), 'Inherited fingerprint payload maps differ')
        for name, expected in payload.items():
            with archive.open(name) as stream:
                need(hashlib.file_digest(stream, 'sha256').hexdigest() == expected, 'Bound donor payload changed: ' + name)
    source_pins = {name: sha(native / name) for name in NATIVE_SOURCES}
    need(all(previous['psx']['productiveTransforms'].get('native/' + name) == value
             for name, value in source_pins.items()), 'Original PSX owner/protocol source changed')
    added = {str(file.relative_to(REPO / 'integration')): sha(file) for folder in ('java', 'recipe')
             for file in sorted((ROOT / folder).rglob('*')) if file.is_file() and file.suffix in ('.java', '.py')}
    transforms = dict(previous['psx']['productiveTransforms'])
    need(not set(added).intersection(transforms), 'Direct download source already appears in the frozen chain')
    transforms.update(added)
    payload = dict(payload, **{'classes28.dex': sha(args.dex)})
    args.out.mkdir(parents=True)
    records = {}
    for kind in ('psx', 'n64', 'dolphin'):
        name = NAMES[kind]
        value = copy.deepcopy(previous[kind])
        value.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
        if kind != 'psx':
            value.update(parentFingerprintSha256=digest(canonical(previous[kind])),
                         parentRuntimeSha256=digest(original[kind]), psxRuntimeSha256=records['psx']['runtimeSha256'])
        need(policy(value) == policy(previous[kind]), 'Core/controller/options/protocol policy changed')
        raw = canonical(value)
        (args.out / (name + '.fingerprint.json')).write_bytes(raw + b'\n')
        target = args.out / name
        old = args.out / (name + '.donor')
        old.write_bytes(original[kind])
        if kind == 'psx':
            source = args.out / 'StationPsxIdentity.cpp'
            source.write_text('extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
                'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode('ascii')) + ';}\n')
            sources = [native / filename for filename in NATIVE_SOURCES if filename.endswith('.cpp')]
            cmd = [tools / 'aarch64-linux-android28-clang++', '-std=c++20', '-O2', '-fPIC', '-shared',
                   '-fno-omit-frame-pointer', '-fno-optimize-sibling-calls', '-Wall', '-Wextra', '-Werror',
                   '-Wl,-z,max-page-size=16384', '-Wl,-z,relro,-z,now', '-Wl,--no-undefined',
                   '-Wl,-soname,' + name, '-I' + str(native), *sources, source, '-ldl', '-o', target]
        else:
            api = 'StationMupenRuntime' if kind == 'n64' else 'StationDolphinRuntime'
            source = args.out / (name + '.c')
            source.write_text('__attribute__((visibility("default"))) const char *' + api + 'Identity(void) { return "' + digest(raw) + '"; }\n' +
                '__attribute__((visibility("default"))) const char *' + api + 'Manifest(void) { return ' + json.dumps(raw.decode('ascii')) + '; }\n')
            cmd = [tools / 'clang', '--target=aarch64-linux-android24', '-std=c11', '-Oz', '-fPIC',
                   '-fvisibility=hidden', '-Wall', '-Wextra', '-Werror', '-shared', source, '-o', target,
                   '-Wl,--no-undefined', '-Wl,--build-id=sha1', '-Wl,-soname,' + name,
                   '-Wl,-z,max-page-size=16384', '-Wl,-z,common-page-size=16384']
        command(cmd, args.out / (name + '.build.log'))
        if kind != 'psx':
            subprocess.run([str(tools / 'llvm-strip'), '--strip-unneeded', str(target)], check=True)
        need(raw in target.read_bytes() and digest(raw).encode('ascii') in target.read_bytes(), 'New marker embedding failed')
        before, after = metadata(old, tools), metadata(target, tools)
        need(before['exports'] == after['exports'] and before['neededLibraries'] == after['neededLibraries'] and
             before['soname'] == after['soname'] == [name], 'Wrapper export/dependency contract changed')
        records[kind] = {'runtimeLibrary': name, 'runtimeSha256': sha(target), 'runtimeBytes': target.stat().st_size,
                         'fingerprintSha256': digest(raw), 'elf': after}
        old.unlink()
    need(all(sha(native / name) == value for name, value in source_pins.items()), 'Native source changed during compilation')
    updated = copy.deepcopy(engines)
    selected = []
    for before, after in zip(engines['engines'], updated['engines']):
        platform = before['platform']
        if platform not in ('psx', 'n64', 'gamecube', 'wii'):
            continue
        kind = 'dolphin' if platform in ('gamecube', 'wii') else platform
        runtime = records[kind]['runtimeSha256']
        need(before['engineId'].endswith('-' + before['runtimeSha256'][:12]), 'Original engine suffix differs')
        after.update(runtimeSha256=runtime, engineId=before['engineId'][:-12] + runtime[:12])
        need({k: v for k, v in before.items() if k not in ('engineId', 'runtimeSha256')} ==
             {k: v for k, v in after.items() if k not in ('engineId', 'runtimeSha256')}, 'Engine policy changed')
        selected.append(after)
    need(len(selected) == 4, 'Exactly four bundle identities must renew')
    (args.out / 'engines.json').write_text(json.dumps(updated, indent=2, ensure_ascii=False) + '\n')
    result = {'revision': 'DIRECT-DOWNLOAD-20261013', 'parentApkSha256': BASE,
              'changedDexEntry': 'classes28.dex', 'dexSha256': sha(args.dex),
              'dexReceiptSha256': sha(args.dex_receipt), 'payloadSha256': payload,
              'markers': records, 'engines': selected, 'enginesAssetSha256': sha(args.out / 'engines.json'),
              'emulatorCoreAndControllerPoliciesPreserved': True, 'originalPsxSourcesPreserved': source_pins,
              'registeredOnServer': False, 'signed': False, 'installed': False, 'physicalDownloadValidated': False}
    (args.out / 'runtime-identity.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('donor', 'dex', 'dex-receipt', 'ndk', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    result = build(parser.parse_args())
    print(json.dumps({'wrappersRenewed': len(result['markers']), 'engineIdentitiesRenewed': len(result['engines']),
                      'emulatorCoresRebuilt': False, 'signed': False, 'installed': False}))
