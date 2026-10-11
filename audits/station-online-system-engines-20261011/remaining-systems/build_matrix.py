"""Read-only R126 APK audit. Writes only JSON/Markdown into this audit directory.

No emulator launch, device access, archive extraction, checkout change or server call.
R120's call graph is historical input; current APK libraries and DEX classes are checked.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import zipfile


def native(path):
    p = Path(path).absolute()
    return Path('\\\\?\\' + str(p)) if os.name == 'nt' else p


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(native(path).read_text(encoding='utf-8-sig'))


def class_names(data):
    if not data.startswith(b'dex\n'):
        raise ValueError('Not a DEX file')
    strings_count, strings_offset = struct.unpack_from('<II', data, 56)
    types_count, types_offset = struct.unpack_from('<II', data, 64)
    classes_count, classes_offset = struct.unpack_from('<II', data, 96)
    strings = []
    for i in range(strings_count):
        offset = struct.unpack_from('<I', data, strings_offset + 4 * i)[0]
        while data[offset] & 128:
            offset += 1
        offset += 1
        end = data.index(0, offset)
        strings.append(data[offset:end].decode('utf-8', errors='replace'))
    types = [strings[struct.unpack_from('<I', data, types_offset + 4 * i)[0]]
             for i in range(types_count)]
    result = set()
    for i in range(classes_count):
        descriptor = types[struct.unpack_from('<I', data, classes_offset + 32 * i)[0]]
        if descriptor.startswith('L') and descriptor.endswith(';'):
            result.add(descriptor[1:-1].replace('/', '.'))
    return result


def elf_exports(data):
    if data[:5] != b'\x7fELF\x02' or data[5] != 1:
        raise ValueError('Expected ELF64 little endian')
    section_offset = struct.unpack_from('<Q', data, 40)[0]
    section_size, count = struct.unpack_from('<HH', data, 58)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data,
                section_offset + section_size * i) for i in range(count)]
    result = []
    for section in sections:
        if section[1] != 11:  # SHT_DYNSYM
            continue
        strings = sections[section[6]]
        table = data[strings[4]:strings[4] + strings[5]]
        for offset in range(section[4], section[4] + section[5], section[9]):
            name, info, visibility, index, value, size = struct.unpack_from('<IBBHQQ', data, offset)
            if index and name and info >> 4 in (1, 2):
                end = table.index(0, name)
                result.append(table[name:end].decode('utf-8', errors='replace'))
    return result


def online_platform(folder):
    return {'super-nintendo': 'snes', 'super-nintendo--br': 'snes',
            'megadrive--br': 'megadrive', 'neo-geo': 'neogeo',
            'neo-geo-cd': 'neogeocd', 'nintendo-64': 'n64',
            'nintendo-64--br': 'n64', 'ps2br': 'ps2'}.get(folder, folder)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True)
    parser.add_argument('--apk', required=True)
    parser.add_argument('--native-source', required=True)
    parser.add_argument('--verify-apk-hash', action='store_true')
    args = parser.parse_args()
    repo = Path(args.repo).absolute()
    target = Path(__file__).resolve().parent
    matrix_path = repo / 'versions/station-game-menu-controller-audit-r120-20261010/evidence/launch-matrix-r120.json'
    pin_path = repo / 'versions/station-video-room-footer-r124-20261011/CAROUSEL-INPUT-MANIFEST.json'
    r120 = read_json(matrix_path)
    pins = read_json(pin_path)
    apk_hash = None
    if args.verify_apk_hash:
        h = hashlib.sha256()
        with native(args.apk).open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        apk_hash = h.hexdigest()
        if apk_hash != 'f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d':
            raise ValueError('Input is not the signed R126 candidate')
    header_pins = []
    for name, expected in sorted(pins.items()):
        if name.startswith('d1/native_') and any(v in name for v in
                ('flycast', 'psp', 'ps2', 'psvita', 'saturn', 'wiiu', 'xbox')):
            p = Path(args.native_source) / name[3:]
            actual = digest(native(p).read_bytes()) if native(p).is_file() else None
            header_pins.append({'input': name, 'expectedSha256': expected,
                                'actualSha256': actual, 'matchesR124Pin': actual == expected})
    with zipfile.ZipFile(native(args.apk)) as z:
        names = set(z.namelist())
        registry_bytes = z.read('assets/station-online/engines.json')
        registry = json.loads(registry_bytes)
        classes = {}
        dex_evidence = []
        for name in sorted(names):
            if name.startswith('classes') and name.endswith('.dex'):
                data = z.read(name)
                found = class_names(data)
                dex_evidence.append({'entry': name, 'bytes': len(data), 'sha256': digest(data),
                                     'classCount': len(found)})
                for cls in found:
                    classes.setdefault(cls, []).append(name)
        libraries = {}
        def library(entry):
            if entry not in libraries:
                if entry not in names:
                    libraries[entry] = {'entry': entry, 'presentInR126Apk': False}
                else:
                    data = z.read(entry)
                    info = z.getinfo(entry)
                    libraries[entry] = {'entry': entry, 'presentInR126Apk': True,
                        'bytes': len(data), 'crc32': format(info.CRC, '08x'), 'sha256': digest(data)}
                    if '_libretro_' in entry:
                        exports = set(elf_exports(data))
                        required = ('retro_run', 'retro_set_environment', 'retro_set_input_poll',
                                    'retro_set_input_state', 'retro_serialize_size', 'retro_serialize',
                                    'retro_unserialize', 'retro_load_game', 'retro_set_controller_port_device')
                        libraries[entry]['libretroAbiExports'] = {v: v in exports for v in required}
                        libraries[entry]['serializationExportsDoNotProveDeterminismOrWorkingStates'] = True
            return libraries[entry]
        public_provenance = {}
        for name in sorted(names):
            if name in ('assets/flycast-integration/provenance.json',
                        'assets/psp-integration/provenance.json',
                        'assets/ps2-integration/provenance.json',
                        'assets/psvita-integration/provenance.json',
                        'assets/wiiu-integration/provenance.json',
                        'assets/xbox360-integration/provenance.json',
                        'assets/saturn-modern/provenance.json'):
                data = z.read(name)
                value = json.loads(data)
                keys = ('official_version', 'version', 'source', 'official_source', 'commit',
                        'engine_build', 'engine_commit', 'official_apk', 'official_apk_sha256',
                        'apk', 'donor_sha256', 'source_archive', 'source_sha256',
                        'source_rebuilt', 'engine_rebuilt_from_source', 'upstream_engine_rebuilt',
                        'rebuilt_from_source', 'libVita3K_sha256', 'experimental', 'process')
                public_provenance[name] = {'assetSha256': digest(data),
                                           'fields': {k: value[k] for k in keys if k in value}}
        rows = []
        alias_index = []
        for source in r120['rows']:
            folder = source['nativeFolder']
            platform = online_platform(folder)
            entries = [e for e in registry['engines'] if e.get('platform') == platform]
            selectable = [e for e in entries if e.get('launchReady') and
                          e.get('recoveryProtocol') == 'station-stream.v3']
            selected = selectable[0] if selectable else None
            normal_libraries = []
            for v in source['binding']['libraries']:
                entry = v.get('entry', 'lib/arm64-v8a/' + v['requestedName'])
                checked = dict(library(entry))
                checked['r120Bytes'] = v.get('bytes')
                checked['r120Crc32'] = v.get('crc32')
                checked['matchesR120SizeAndCrc'] = (checked.get('bytes') == v.get('bytes') and
                         checked.get('crc32') == v.get('crc32')) if 'entry' in v else None
                normal_libraries.append(checked)
            calls = []
            chain = list(source['binding'].get('activityChain', []))
            if source['binding'].get('bootstrapClass'):
                chain.insert(0, source['binding']['bootstrapClass'])
            for v in chain:
                calls.append({'name': v['name'], 'r120Dex': v.get('dexEntry'),
                              'r126Dex': classes.get(v['name'], []),
                              'presentInR126Dex': v['name'] in classes,
                              'manifestComponentFromR120': v.get('manifestComponent')})
            actual_route = ('StationN64Activity / Mupen64Plus AE' if platform == 'n64' else
                            'StationDolphinActivity / Dolphin' if platform in ('gamecube', 'wii') else
                            'StationRetroActivity / RetroArch runtime') if selected else 'unavailable-before-emulator-launch'
            missing = [v['entry'] for v in normal_libraries if not v['presentInR126Apk']]
            row = {'label': source['label'], 'nativeFolder': folder,
                   'catalogAliases': source['catalogAliases'], 'onlineCanonical': platform,
                   'normal': {'engine': source['binding']['engine'],
                       'command': source['selectedOfflineCommand'],
                       'dispatch': source['binding'].get('runDispatch'),
                       'components': calls, 'libraries': normal_libraries,
                       'missingPackagedLibraries': missing,
                       'launchCodePresent': all(v['presentInR126Dex'] for v in calls),
                       'gameplayVerifiedByThisAudit': False,
                       'historicalR120Status': source['status']},
                   'online': {'registeredInR126Apk': bool(entries),
                       'selectableLocally': bool(selected),
                       'engineId': selected.get('engineId') if selected else None,
                       'backend': selected.get('backend', 'retroarch') if selected else None,
                       'library': selected.get('library') if selected else None,
                       'runtimeLibrary': selected.get('runtimeLibrary', 'libstation_retroarch.so') if selected else None,
                       'recoveryProtocol': selected.get('recoveryProtocol') if selected else None,
                       'launchReady': selected.get('launchReady') if selected else False,
                       'maximumPlayersInEngineAsset': selected.get('maximumPlayers') if selected else None,
                       'gameModePlayerCount': 'requires-current-signed-game-profile',
                       'controllerProfiles': selected.get('controllerProfiles') if selected else [],
                       'activityRoute': actual_route,
                       'serverActivationConfirmedByThisAudit': False,
                       'approvedGameModeRequired': True,
                       'physicalGameplayVerifiedByThisAudit': False,
                       'allPlatformEntries': entries}}
            if selected:
                row['online']['coreEvidence'] = library('lib/arm64-v8a/' + selected['library'])
                row['online']['runtimeEvidence'] = library('lib/arm64-v8a/' + row['online']['runtimeLibrary'])
            rows.append(row)
            alias_index.extend({'alias': a, 'label': source['label'], 'nativeFolder': folder,
                                'onlineCanonical': platform} for a in source['catalogAliases'])
        symbols = {}
        for name, pattern in [('libyuzu-android.so', 'netPlay'), ('libflycast.so', 'ggpo'),
                              ('libppsspp_jni.so', 'sceNetAdhoc'), ('libVita3K.so', 'ScePspnetAdhoc')]:
            entry = 'lib/arm64-v8a/' + name
            symbols[name] = [v for v in elf_exports(z.read(entry)) if pattern.lower() in v.lower()]
        audit = {'kind': 'read-only-remaining-system-audit-r126',
                 'date': '2026-10-11', 'apkFilename': Path(args.apk).name,
                 'expectedApkSha256FromR126FinalReceipt': 'f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d',
                 'apkSha256ComputedByThisAudit': apk_hash,
                 'apkBytes': native(args.apk).stat().st_size,
                 'canonicalRows': len(rows), 'catalogAliases': len(alias_index),
                 'enginesInApk': len(registry['engines']),
                 'locallySelectableCanonicalRows': sum(v['online']['selectableLocally'] for v in rows),
                 'routeGraphInput': str(matrix_path.relative_to(repo)).replace('\\', '/'),
                 'routeGraphInputSha256': digest(native(matrix_path).read_bytes()),
                 'registryEntry': 'assets/station-online/engines.json',
                 'registrySha256': digest(registry_bytes),
                 'manifestSha256': digest(z.read('AndroidManifest.xml')),
                 'limits': ['Static library/class/identity evidence; no gameplay claim.',
                     'Normal call graph comes from R120 plus preserved normal binary chain; source is not inferred from current upstream.',
                     'Library absent in APK does not prove absent in current device private external-core directory.',
                     'Platform ceilings never grant a game/mode multiplayer approval.',
                     'No production activation, auth snapshot, device operation, build or productive edit performed.'],
                 'nativeHeaderPins': header_pins, 'publicProvenance': public_provenance,
                 'networkExports': symbols, 'dexEvidence': dex_evidence, 'rows': rows,
                 'aliasIndex': alias_index}
        if len(rows) != 50 or len(alias_index) != 78:
            raise ValueError('Unexpected canonical/alias row count')
        native(target / 'matrix.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        lines = ['# Matriz estática R126 — 50 linhas e 78 aliases', '',
                 'Gerada pela leitura do APK R126 assinado e da matriz histórica R120. Não comprova gameplay, cadastro em produção ou presença de cores externos no telefone atual.', '',
                 '| Sistema | Pasta | Emulador normal | Biblioteca normal no APK | Online local R126 | Backend / emulador |',
                 '|---|---|---|---|---|---|']
        for row in rows:
            n, o = row['normal'], row['online']
            normal = 'Falta: ' + ', '.join(Path(p).name for p in n['missingPackagedLibraries']) if n['missingPackagedLibraries'] else 'Presente'
            lines.append('| ' + ' | '.join([row['label'].strip(), row['nativeFolder'], n['engine'],
                         normal, 'Selecionável; perfil autenticado obrigatório' if o['selectableLocally'] else 'Indisponível: nenhum motor v3 selecionável',
                         (o['backend'] + ' / ' + o['library']) if o['selectableLocally'] else 'Sem adaptador registrado']) + ' |')
        lines += ['', 'Os dez motores históricos permanecem no registro; N64/GameCube/Wii usam os três adaptadores nativos novos. Selecionável localmente não significa ativado no servidor.',
                  '', '## Aliases do catálogo', '', '| Alias | Nome exibido | Pasta normal | Canonical online |', '|---|---|---|---|']
        for v in alias_index:
            lines.append('| ' + ' | '.join([v['alias'].strip(), v['label'].strip(), v['nativeFolder'], v['onlineCanonical']]) + ' |')
        native(target / 'MATRIX.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(json.dumps({'rows': len(rows), 'aliases': len(alias_index), 'engines': len(registry['engines']),
                          'selectableRows': audit['locallySelectableCanonicalRows'],
                          'normalLibrariesHashed': len(libraries),
                          'missingPackagedLibraries': sorted(k for k, v in libraries.items() if not v['presentInR126Apk']),
                          'missingDexClasses': sorted({v['name'] for row in rows for v in row['normal']['components'] if not v['presentInR126Dex']}),
                          'networkExports': {k: len(v) for k, v in symbols.items()},
                          'allEightHeaderPinsMatch': all(v['matchesR124Pin'] for v in header_pins),
                          'apkHashComputed': apk_hash, 'matrixSha256': digest(native(target / 'matrix.json').read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
