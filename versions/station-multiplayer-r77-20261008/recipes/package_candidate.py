"""Package reviewed R77 inputs over the exact R76 APK; no ADB, checkout or deployment."""
from pathlib import Path, PurePosixPath
import argparse, copy, datetime, hashlib, json, os, re, shutil, struct, subprocess, zipfile

SNAPSHOT = Path(__file__).resolve().parent.parent
PREVIOUS = SNAPSHOT.parent / 'station-pump-wakeup-r76-20261008'
BASE = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R76-20261008.apk')
BASE_SHA = 'd7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51'
CERT = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
RUNTIME_SHA = '351cee4540e916468a504788911e4c5fcb4fe141e3b544b1b1255d32e1d04a26'
SNES_CORE_SHA = '0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527'
BASE_SLOTS = {
    'classes28.dex': '1a04582a02804ecbe4b075dd487118a171b0b0f305dbb8884015bbede09b25d7',
    'classes35.dex': 'c03ea2f4aa30c5e32654c575115583f72815b9701c16791c4f94c6ade753f2ff',
    'lib/arm64-v8a/libstation_retroarch.so': '804b2acfea4c6d615bf40dba30e1777015098bf7375d0745db8d117555eb2516',
    'lib/arm64-v8a/libstation_bsnes.so': 'cc14438319709f3b7868b3e652c731f6df472ff21bb01e4a65234ba2cc6f368b',
    'assets/station-online/engines.json': 'd43d6af1581691fbf88d6a15f87bea66761ef2f4d8952857028c6541b908e985',
}
PROTECTED = {
    'AndroidManifest.xml': '3a821dccd8a9853acd345f106614ec955bbf66b681b7690f907348569e8bef0d',
    'lib/arm64-v8a/libturbo_carousel.so': '3c2e22bc94f3432280e2b08c2f26ab33508cd1278ee9bd750b48d45c35105a8b',
}
WORK_ROOT = Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008')
FINAL_ROOT = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais')
AUTHORIZED_KEY = Path(r'C:\Users\Admin\.android\debug.keystore')
CATALOG_PREFIXES = ('assets/station-online/', 'assets/station-metadata/')
CATALOG_EXACT = {'assets/station-catalog/player-evidence-v1.json'}
CAROUSEL_ENTRY = 'lib/arm64-v8a/libturbo_carousel.so'

def require(ok, message):
    if not ok: raise RuntimeError(message)

def sha(path):
    with Path(path).open('rb') as file: return hashlib.file_digest(file, 'sha256').hexdigest()

def zsha(archive, entry):
    with archive.open(entry) as file: return hashlib.file_digest(file, 'sha256').hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON member')
        result[key] = value
    return result

def load(path):
    return json.loads(Path(path).read_text('utf8'), object_pairs_hook=unique)

def signature(name):
    return name.startswith('META-INF/') and name.upper().endswith(('.MF', '.SF', '.RSA', '.DSA', '.EC'))

def local_file(value):
    path = Path(value)
    require(path.is_absolute() and path.is_file(), 'Existing absolute local input required')
    path = path.resolve()
    require(path.drive.upper() in ('C:', 'E:', 'G:'), 'Local C:, E: or G: input required')
    return path

def payload(spec):
    require(set(spec) == {'path', 'sha256'}, 'Payload must declare only path/sha256')
    path = local_file(spec['path'])
    require(re.fullmatch('[0-9a-f]{64}', spec['sha256']) and sha(path) == spec['sha256'], 'Payload hash mismatch')
    return path

def elf(path):
    with path.open('rb') as file:
        header = file.read(64)
        require(len(header) == 64 and header[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', header, 18)[0] == 183, 'ARM64 little-endian ELF required')
        offset = struct.unpack_from('<Q', header, 32)[0]
        width, count = struct.unpack_from('<HH', header, 54)
        require(width >= 56 and 0 < count < 128 and offset + width * count <= path.stat().st_size, 'Invalid ELF program headers')
        loads = 0
        for index in range(count):
            file.seek(offset + width * index); row = file.read(56)
            kind, flags, start, address, physical, size, memory, align = struct.unpack('<IIQQQQQQ', row)
            if kind == 1:
                loads += 1
                require(align >= 16384 and align & (align - 1) == 0 and start % align == address % align, 'ELF LOAD must support 16KiB pages')
        require(loads > 0, 'ELF has no LOAD segment')

def dex(path):
    with path.open('rb') as file: header = file.read(36)
    require(len(header) == 36 and header[:4] == b'dex\n' and header[7] == 0 and struct.unpack_from('<I', header, 32)[0] == path.stat().st_size, 'Compiled DEX header/size mismatch')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, help='Reviewed PACKAGE-INPUTS.json')
    parser.add_argument('--gates', default=str(SNAPSHOT / 'evidence/package-gates.json'))
    parser.add_argument('--workspace', default=str(WORK_ROOT / 'package-01'))
    parser.add_argument('--output', default=str(FINAL_ROOT / 'TurboStations-Premium-R77-20261008.apk'))
    args = parser.parse_args()
    work = Path(args.workspace).resolve(); output = Path(args.output).resolve()
    require(work != WORK_ROOT.resolve() and work.is_relative_to(WORK_ROOT.resolve()) and not work.exists(), 'New child directory of the explicit E: R77 workspace required')
    require(output.parent == FINAL_ROOT.resolve() and output.suffix.lower() == '.apk' and not output.exists(), 'New APK in the approved G: output directory required')
    require(sha(BASE) == BASE_SHA, 'Exact R76 APK required; refusing another release')
    input_file = local_file(args.inputs); gates_file = local_file(args.gates)
    inputs = load(input_file); gates = load(gates_file)
    required_input_fields = {'schemaVersion', 'baseApkSHA256', 'javaBuildDirectory', 'javaBuildReceiptSHA256', 'runtime', 'snesCore', 'engines', 'catalogAssets'}
    require(required_input_fields <= set(inputs) <= required_input_fields | {'carousel'}, 'Unexpected packaging input fields')
    require(inputs['schemaVersion'] == 1 and inputs['baseApkSHA256'] == BASE_SHA, 'Input schema/base mismatch')
    java = Path(inputs['javaBuildDirectory']).resolve()
    require(java.is_relative_to(WORK_ROOT.resolve()), 'R77 Java build must be inside its explicit E: workspace')
    build_file = java / 'evidence/build.json'; build = load(build_file)
    require(sha(build_file) == inputs['javaBuildReceiptSHA256'] and build['compiled'] is True and build['base'] == 'R76', 'Reviewed R77 build receipt required')
    build_recipe = SNAPSHOT / 'recipes/build_java.py'
    require(build['buildRecipeSHA256'] == sha(build_recipe), 'Java build recipe differs from the reviewed compilation')
    require(build['baseClientDexSHA256'] == BASE_SLOTS['classes28.dex'] and build['baseRoomsDexSHA256'] == BASE_SLOTS['classes35.dex'], 'Build must identify the R76 DEX baseline')
    old_sources = load(PREVIOUS / 'evidence/java-dex-build.json')['sourceHashes']
    overlays = {p.relative_to(SNAPSHOT / 'java').as_posix(): sha(p) for p in (SNAPSHOT / 'java').rglob('*.java')}
    expected_sources = {**old_sources, **overlays}
    require(build['sourceHashes'] == expected_sources, 'Source snapshot differs from compiled source inventory')
    require(all(sha(java / 'java' / name) == digest for name, digest in expected_sources.items()), 'Staged Java sources changed after compilation')
    expected_changed = sorted(name for name, digest in expected_sources.items() if old_sources.get(name) != digest)
    require(sorted(build['changedSources']) == expected_changed and sorted(build['changedDexSlots']) == ['classes28.dex', 'classes35.dex'], 'Unexpected source/DEX change report')
    replacements = {
        'classes28.dex': java / 'java/build/client-dex/classes.dex',
        'classes35.dex': java / 'java/build/rooms-dex/classes.dex',
        'lib/arm64-v8a/libstation_retroarch.so': payload(inputs['runtime']),
        'lib/arm64-v8a/libstation_bsnes.so': payload(inputs['snesCore']),
        'assets/station-online/engines.json': payload(inputs['engines']),
    }
    if 'carousel' in inputs:
        replacements[CAROUSEL_ENTRY] = payload(inputs['carousel'])
    require(sha(replacements['classes28.dex']) == build['clientDexSHA256'] != BASE_SLOTS['classes28.dex'], 'Client DEX mismatch')
    require(sha(replacements['classes35.dex']) == build['roomsDexSHA256'] != BASE_SLOTS['classes35.dex'], 'Rooms DEX mismatch')
    require(inputs['runtime']['sha256'] == RUNTIME_SHA and inputs['snesCore']['sha256'] == SNES_CORE_SHA, 'Native artifacts differ from the reviewed final R77 identities')
    for entry, path in replacements.items():
        if entry.endswith('.so'): elf(path)
        elif entry.endswith('.dex'): dex(path)
    additions = {}
    require(isinstance(inputs['catalogAssets'], list) and len(inputs['catalogAssets']) <= 32, 'Bounded declared catalog assets required')
    for item in inputs['catalogAssets']:
        require(set(item) == {'entry', 'path', 'sha256'}, 'Catalog declaration fields invalid')
        entry = item['entry']; name = PurePosixPath(entry)
        require((entry.startswith(CATALOG_PREFIXES) or entry in CATALOG_EXACT) and '\\' not in entry and not name.is_absolute() and '..' not in name.parts and name.suffix == '.json', 'Only new JSON catalog metadata is allowed')
        require(entry not in additions and entry not in replacements and name.as_posix() == entry, 'Duplicate/noncanonical catalog entry')
        path = payload({'path': item['path'], 'sha256': item['sha256']})
        require(path.stat().st_size <= 32 * 1024**2 and isinstance(load(path), (dict, list)), 'Bounded JSON catalog asset required')
        additions[entry] = path
    require(sum(p.stat().st_size for p in additions.values()) <= 64 * 1024**2, 'Catalog assets exceed total bound')
    require(gates.get('reviewed') is True and gates.get('version') == 'R77' and gates.get('inputManifestSHA256') == sha(input_file), 'Final packaging gates are absent or stale')
    require(gates.get('javaBuildReceiptSHA256') == sha(build_file) and gates.get('runtimeSHA256') == RUNTIME_SHA and gates.get('snesCoreSHA256') == SNES_CORE_SHA, 'Gates bind different artifacts')
    receipts = gates.get('receipts', [])
    required_kinds = {'java-contract', 'java-concurrency', 'native-runtime', 'native-snes', 'server-candidate', 'catalog'}
    if 'carousel' in inputs:
        required_kinds.add('carousel')
        require(gates.get('carouselSHA256') == inputs['carousel']['sha256'], 'Gates bind a different carousel artifact')
    require(required_kinds <= {r.get('kind') for r in receipts}, 'Missing qualification scope in reviewed gates')
    for receipt in receipts:
        require(sha(local_file(receipt['path'])) == receipt['sha256'], 'Qualification receipt changed')
    require(replacements['assets/station-online/engines.json'].stat().st_size <= 32768, 'Engine metadata too large')
    engines = load(replacements['assets/station-online/engines.json'])
    require(engines['schemaVersion'] == 1 and engines.get('androidPeerPlayValidated') is False, 'Do not claim qualified Android peer play in candidate metadata')
    require(len(engines['engines']) == 3 and len({e['engineId'] for e in engines['engines']}) == 3, 'Three unique existing platform engines required')
    with zipfile.ZipFile(BASE) as old:
        old_names = {n for n in old.namelist() if not signature(n)}
        require(len(old.namelist()) == len(set(old.namelist())) and len(old_names) == 13225, 'R76 entry inventory mismatch')
        require(not (set(additions) & old_names), 'Catalog additions must not overwrite existing assets')
        for name, digest in {**BASE_SLOTS, **PROTECTED}.items(): require(zsha(old, name) == digest, 'Protected baseline mismatch: ' + name)
        prior = json.loads(old.read('assets/station-online/engines.json'))
        previous_by_platform = {e['platform']: e for e in prior['engines']}
        require({e['platform'] for e in engines['engines']} == set(previous_by_platform), 'Platform engines must be preserved')
        for entry in engines['engines']:
            previous = previous_by_platform[entry['platform']]
            for key in ('library', 'extensions', 'overlay', 'options', 'launchReady', 'license', 'sourceDirectory'):
                require(entry[key] == previous[key], 'Engine compatibility field changed: ' + key)
            require(entry['engineId'] != previous['engineId'] and entry['runtimeSha256'] == RUNTIME_SHA, 'New runtime requires new engine identity')
            native_entry = 'lib/arm64-v8a/' + entry['library']
            require(entry['coreSha256'] == (sha(replacements[native_entry]) if native_entry in replacements else zsha(old, native_entry)), 'Engine/core identity mismatch')
            if entry['platform'] == 'snes': require(entry.get('recoveryProtocol') == 'station-stream.v3', 'SNES multiplayer protocol required')
        old_media = {n: zsha(old, n) for n in old_names if n.endswith('.mp4')}
        require(len(old_media) == 59 and sum(n.startswith('assets/turbo-system-videos/') for n in old_media) == 58, 'R76 video inventory differs')
    input_hashes = {n: sha(p) for n, p in {**replacements, **additions}.items()}
    baseline_payload_hashes = {**BASE_SLOTS, **PROTECTED}
    require(all(input_hashes[n] != baseline_payload_hashes[n] for n in replacements), 'Every declared replacement must actually be new')
    recipe_sha = sha(__file__); gates_sha = sha(gates_file); inputs_sha = sha(input_file)
    tools = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
    jdk = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
    env = dict(os.environ)
    for name in ('STATION_KEYSTORE', 'STATION_KEY_ALIAS', 'STATION_KS_PASS', 'STATION_KEY_PASS'):
        require(bool(env.get(name)), 'Existing signing environment is required: ' + name)
    require(Path(env['STATION_KEYSTORE']).resolve() == AUTHORIZED_KEY.resolve(), 'Use only the explicitly authorized local signing key')
    require(shutil.disk_usage(work.parent).free > 2 * BASE.stat().st_size + 256 * 1024**2 and shutil.disk_usage(output.parent).free > BASE.stat().st_size + 128 * 1024**2, 'Insufficient free space for a safe package')
    (work / 'evidence').mkdir(parents=True); (work / 'temp').mkdir()
    env.update(TEMP=str(work / 'temp'), TMP=str(work / 'temp'))
    # Export the public certificate only. Passwords are env references, never command-line values or output.
    cert = subprocess.run([str(jdk / 'keytool.exe'), '-J-Djava.io.tmpdir=' + str(work / 'temp'), '-exportcert', '-keystore', env['STATION_KEYSTORE'], '-alias', env['STATION_KEY_ALIAS'], '-storepass:env', 'STATION_KS_PASS'], capture_output=True, env=env)
    require(cert.returncode == 0 and hashlib.sha256(cert.stdout).hexdigest() == CERT, 'Existing key must match the installed certificate exactly')
    def run(command, label):
        result = subprocess.run(list(map(str, command)), capture_output=True, env=env)
        (work / 'evidence' / ('package-' + label + '-private.log')).write_bytes(result.stdout + result.stderr)
        require(result.returncode == 0, 'Packaging tool failed; private local log: ' + label)
        return (result.stdout + result.stderr).decode('utf8', 'replace')
    def signer(path, label):
        text = run([jdk / 'java.exe', '-jar', tools / 'lib/apksigner.jar', 'verify', '--print-certs', path], label)
        found = re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]{64})\s*$', text, re.MULTILINE)
        require([h.lower() for h in found] == [CERT], 'Exactly the original single signer is required')
    signer(BASE, 'base-cert')
    unsigned = work / 'unsigned-r77.apk'; signed = work / 'signed-r77.apk'
    with zipfile.ZipFile(BASE) as old, zipfile.ZipFile(unsigned, 'w', allowZip64=True) as new:
        for info in old.infolist():
            if signature(info.filename): continue
            item = copy.copy(info); item.extra = b''
            if item.filename in replacements: item.file_size = replacements[item.filename].stat().st_size
            if item.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if item.filename.endswith('.so') else 4
                offset = new.fp.tell() + 30 + len(item.filename.encode('utf8'))
                if offset % alignment:
                    pad = (-(offset + 4)) % alignment; item.extra = struct.pack('<HH', 0xffff, pad) + bytes(pad)
            with new.open(item, 'w') as target:
                with (replacements[item.filename].open('rb') if item.filename in replacements else old.open(info)) as source:
                    shutil.copyfileobj(source, target, 1024 * 1024)
        for name, path in sorted(additions.items()):
            item = zipfile.ZipInfo(name, (2026, 10, 8, 0, 0, 0)); item.compress_type = zipfile.ZIP_DEFLATED
            with new.open(item, 'w') as target, path.open('rb') as source: shutil.copyfileobj(source, target, 1024 * 1024)
    run([tools / 'zipalign.exe', '-c', '-P', '16', '4', unsigned], 'unsigned-alignment')
    run([jdk / 'java.exe', '-Djava.io.tmpdir=' + str(work / 'temp'), '-jar', tools / 'lib/apksigner.jar', 'sign', '--alignment-preserved', 'true', '--v4-signing-enabled', 'false', '--ks', env['STATION_KEYSTORE'], '--ks-key-alias', env['STATION_KEY_ALIAS'], '--ks-pass', 'env:STATION_KS_PASS', '--key-pass', 'env:STATION_KEY_PASS', '--out', signed, unsigned], 'sign')
    signer(signed, 'signed-cert'); run([tools / 'zipalign.exe', '-c', '-P', '16', '4', signed], 'signed-alignment')
    preserved = 0; changed = []; media = {}
    with zipfile.ZipFile(BASE) as old, zipfile.ZipFile(signed) as new:
        names = {n for n in new.namelist() if not signature(n)}
        require(len(new.namelist()) == len(set(new.namelist())) and names == old_names | set(additions), 'Final entries added/removed outside the manifest')
        for name in sorted(old_names):
            before = zsha(old, name); after = zsha(new, name)
            require(after == input_hashes.get(name, before), 'Unexpected final entry bytes: ' + name)
            require(old.getinfo(name).compress_type == new.getinfo(name).compress_type, 'Existing entry compression changed: ' + name)
            if before != after: changed.append(name)
            else: preserved += 1
            if name.endswith('.mp4'): media[name] = after
        for name in additions: require(zsha(new, name) == input_hashes[name], 'Added asset mismatch: ' + name)
    require(changed == sorted(replacements) and preserved == 13225 - len(replacements) and media == old_media, 'Only declared replacements may change; all other R76 entries/media must be preserved')
    require({n: sha(p) for n, p in {**replacements, **additions}.items()} == input_hashes, 'Package input changed during signing')
    require(sha(__file__) == recipe_sha and sha(input_file) == inputs_sha and sha(gates_file) == gates_sha and sha(build_file) == inputs['javaBuildReceiptSHA256'], 'Recipe, gates or build receipt changed')
    require(sha(build_recipe) == build['buildRecipeSHA256'], 'Java build recipe changed during packaging')
    require(all(sha(java / 'java' / name) == digest for name, digest in expected_sources.items()) and {p.relative_to(SNAPSHOT / 'java').as_posix(): sha(p) for p in (SNAPSHOT / 'java').rglob('*.java')} == overlays, 'Java changed during packaging')
    require(all(sha(local_file(r['path'])) == r['sha256'] for r in receipts), 'Qualification receipt changed during packaging')
    digest = sha(signed)
    with output.open('xb') as target, signed.open('rb') as source: shutil.copyfileobj(source, target, 1024 * 1024)
    require(sha(output) == digest, 'Final G: artifact copy mismatch')
    record = dict(version='R77', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), apk=str(output), sha256=digest, bytes=output.stat().st_size,
        baseSHA256=BASE_SHA, certificateSHA256=CERT, changed=changed, added=sorted(additions), preservedEntries=preserved,
        allPackageEntriesVerified=True, alignment16KiB=True, elf16KiB=True, payloadHashes=input_hashes,
        allMediaPreserved=True, totalVideos=59, carouselVideos=58, carouselVideoHashes={n:h for n,h in media.items() if n.startswith('assets/turbo-system-videos/')},
        packageInputsSHA256=inputs_sha, packageGatesSHA256=gates_sha, javaBuildReceiptSHA256=sha(build_file), packageRecipeSHA256=recipe_sha,
        runtimeOnlineUnchanged=False, serverRegistryChangeRequired=True, installed=False, deployed=False, androidPeerPlayValidated=False)
    (work / 'evidence/package.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    # Only two files created by this attempt are removed. Never remove an APK supplied by the user.
    for path in (unsigned, signed):
        require(path.resolve().parent == work and path.name in ('unsigned-r77.apk', 'signed-r77.apk'), 'Unexpected cleanup target')
        path.unlink()
    print(json.dumps({k:v for k,v in record.items() if k != 'carouselVideoHashes'}, indent=2))

if __name__ == '__main__': main()
