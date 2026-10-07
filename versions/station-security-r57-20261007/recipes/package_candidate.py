"""Package protected DEX28/35, the auto-password runtime and its engine manifest over the exact R57 APK."""
from pathlib import Path
from dex_gates import verify_modules
import argparse, copy, datetime, hashlib, json, os, re, shutil, struct, subprocess, zipfile

BASE_COMMIT = '8980cd422d63068299b5e9946c120f81a9c94f29'
BASE_APK_SHA = 'e6159fa3564f0b30c1415b062f42e08e47ea625832e1b2640375b3e8b2b55566'
CERT_SHA = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
INPUTS = {
    'androidJar': '6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
    'stationJar': 'e41854977e9c2dab786f431449c95afb759e80c653e02cbc990434f74a2c39a2',
    'd8Jar': 'd43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0'}
win = os.name == 'nt'
bt = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
jdk = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
p = argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
p.add_argument('--base-apk', default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R57-20261006.apk')
p.add_argument('--output-apk', required=True)
p.add_argument('--keystore', required=True)
p.add_argument('--ks-key-alias', required=True)
p.add_argument('--ks-pass-env', required=True)
p.add_argument('--key-pass-env')
p.add_argument('--java', default=str(jdk / 'java.exe') if win else 'java')
p.add_argument('--apksigner-jar', default=str(bt / 'lib/apksigner.jar'))
p.add_argument('--zipalign', default=str(bt / 'zipalign.exe'))
a = p.parse_args()
workspace = Path(a.workspace).resolve()
snapshot = Path(__file__).resolve().parent.parent
base = snapshot.parent / 'station-current-r55-20261006'
auto = snapshot.parent / 'station-auto-room-access-r57-20261006'

def require(ok, message):
    if not ok:
        raise SystemExit(message)

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def zsha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def signature(name):
    return name.startswith('META-INF/') and name.upper().endswith(('.MF', '.SF', '.RSA', '.DSA', '.EC'))

receipt = json.loads((workspace / 'build/final/result.json').read_text('utf8'))
require(receipt.get('compiled') and not receipt.get('apiCheckOnly', True),
        'A real DEX build is required; api-check-only cannot produce an APK')
require(receipt.get('sourceBase') == 'R57' and receipt.get('baseCommit') == BASE_COMMIT,
        'This packager accepts only the reconciled R57 source')
require(receipt.get('inputs') == INPUTS, 'Exact production SDK, classpath and D8 required')
require(receipt.get('securityOverlay') == 'request-proof-v1', 'The composed security client and rooms are required')
manifest = json.loads((base / 'SOURCE-MANIFEST.json').read_text('utf8'))
source_hashes = {n:e['sha256'] for n,e in manifest['files'].items()
                 if n.startswith(('client/src/java/','netplay-src/','dependency-src/')) and n.endswith('.java')}
visual = snapshot.parent / 'station-layout-r57-20261006'
for name,entry in json.loads((visual/'SOURCE-MANIFEST.json').read_text('utf8'))['overlay'].items():
    if name.startswith('netplay-src/'):source_hashes[name] = entry['sha256']
for source_folder in (auto,snapshot):
    for prefix in ('client/src/java','netplay-src'):
        for f in (source_folder/prefix).rglob('*.java'):source_hashes[f.relative_to(source_folder).as_posix()] = sha(f)
require(len(source_hashes)==190 and receipt.get('sourceHashes')==source_hashes, 'Build source receipt differs')
for name,expected in source_hashes.items():require(sha(workspace/name)==expected,'Workspace source differs: '+name)
client_dex = workspace / 'build/final/client-dex/classes.dex'
dex = workspace / 'build/final/netplay-dex/classes.dex'
require(sha(client_dex) == receipt.get('clientDexSHA256'), 'Client DEX bytes changed')
require(sha(dex) == receipt.get('netplayDexSHA256'), 'Rooms DEX bytes changed')
require(sha(workspace/'build/final/station-client.jar')==receipt.get('clientJarSHA256'), 'Compiled client classpath changed')
native = auto / 'runtime/libstation_retroarch.so'
engine_manifest = auto / 'assets/station-online/engines.json'
native_receipt = json.loads((auto / 'evidence/native-build.json').read_text('utf8'))
require(sha(native) == native_receipt['runtimeSHA256'], 'Native runtime differs from its verified build')
require(native_receipt['minimumLoadAlignment'] >= 16384 and native_receipt['architecture'] == 'AArch64', 'Invalid native runtime')
engine_rows = json.loads(engine_manifest.read_text('utf8'))['engines']
require(len(engine_rows) == 3 and all(e['runtimeSha256'] == sha(native) and e['engineId'].endswith('-autopass1') for e in engine_rows), 'Runtime and engine manifest differ')
require({e['platform'] for e in engine_rows if e['launchReady']} == {'snes', 'megadrive'}, 'Launch policy changed')
replacements = {'classes28.dex': client_dex, 'classes35.dex': dex, 'lib/arm64-v8a/libstation_retroarch.so': native,
                'assets/station-online/engines.json': engine_manifest}
source_apk = Path(a.base_apk).resolve()
output_apk = Path(a.output_apk).resolve()
require(sha(source_apk) == BASE_APK_SHA, 'The exact R57 APK is required; R41 is rejected')
require(not output_apk.exists(), 'Existing APK will not be overwritten')
require(output_apk.parent.is_dir(), 'Output directory must already exist')
stage = workspace / 'package'
require(not stage.exists(), 'Use a fresh workspace; previous package result is preserved')
for folder in (workspace, output_apk.parent):
    require(shutil.disk_usage(folder).free > source_apk.stat().st_size * 2 + 64 * 1024 * 1024,
            'Insufficient space for packaging and verification')
for name in (a.ks_pass_env, a.key_pass_env or a.ks_pass_env):
    require(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name) and bool(os.environ.get(name)),
            'Set the selected password environment variable privately on the build PC')
os.umask(0o077)
stage.mkdir()
unsigned = stage / 'unsigned.apk'
signed = stage / 'signed.apk'
env = dict(os.environ, TEMP=str(workspace), TMP=str(workspace))

def run(args, name):
    r = subprocess.run(list(map(str, args)), capture_output=True, text=True,
                       encoding='utf8', errors='replace', env=env)
    (stage / (name + '.log')).write_text(r.stdout + r.stderr, encoding='utf8')
    require(r.returncode == 0, name + ' failed; inspect the private build log')
    return r.stdout + r.stderr

require(CERT_SHA in run([a.java, '-jar', a.apksigner_jar, 'verify', '--print-certs', source_apk],
                       'base-signature'), 'Base certificate differs')
with zipfile.ZipFile(source_apk) as before:
    require(len(before.namelist()) == len(set(before.namelist())), 'Duplicate ZIP entry')
    require(set(replacements).issubset(before.namelist()), 'Expected R57 modules are missing')
    class_gate = verify_modules(before, {'classes28.dex':client_dex.read_bytes(),'classes35.dex':dex.read_bytes()})
    require(zsha(before, 'lib/arm64-v8a/libstation_retroarch.so') == '22ee3f67e4a5abf4625c2776928a8011a14c5ae0568d74d9576f4b49a9514905', 'Original runtime differs')
    with zipfile.ZipFile(unsigned, 'w', allowZip64=True) as after:
        for info in before.infolist():
            if signature(info.filename):
                continue
            item = copy.copy(info)
            item.extra = b''
            item.file_size = replacements[info.filename].stat().st_size if info.filename in replacements else info.file_size
            if item.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if info.filename.endswith('.so') else 4
                offset = after.fp.tell() + 30 + len(info.filename.encode('utf8'))
                if offset % alignment:
                    pad = (-(offset + 4)) % alignment
                    item.extra = struct.pack('<HH', 0xffff, pad) + bytes(pad)
            with after.open(item, 'w') as target:
                with (replacements[info.filename].open('rb') if info.filename in replacements else before.open(info)) as source:
                    shutil.copyfileobj(source, target, 1024 * 1024)
run([a.zipalign, '-c', '-P', '16', '4', unsigned], 'unsigned-alignment')
run([a.java, '-Djava.io.tmpdir=' + str(workspace), '-jar', a.apksigner_jar, 'sign',
     '--alignment-preserved', 'true', '--v4-signing-enabled', 'false',
     '--ks', a.keystore, '--ks-key-alias', a.ks_key_alias,
     '--ks-pass', 'env:' + a.ks_pass_env, '--key-pass', 'env:' + (a.key_pass_env or a.ks_pass_env),
     '--out', signed, unsigned], 'sign')
require(CERT_SHA in run([a.java, '-jar', a.apksigner_jar, 'verify', '--print-certs', signed],
                       'signature'), 'Signing certificate differs; candidate is not published')
run([a.zipalign, '-c', '-P', '16', '4', signed], 'alignment')
preserved = 0
with zipfile.ZipFile(source_apk) as before, zipfile.ZipFile(signed) as after:
    require(len(after.namelist()) == len(set(after.namelist())), 'Duplicate candidate ZIP entry')
    require({n for n in before.namelist() if not signature(n)} ==
            {n for n in after.namelist() if not signature(n)}, 'Package entry set differs')
    for name in before.namelist():
        if signature(name):
            continue
        expected = sha(replacements[name]) if name in replacements else zsha(before, name)
        require(zsha(after, name) == expected, 'Package entry changed: ' + name)
        if name not in replacements:
            preserved += 1
    require(zsha(after, 'classes35.dex') != zsha(before, 'classes35.dex') and zsha(after,'classes28.dex') != zsha(before,'classes28.dex'), 'Both DEX deltas must be present')
with signed.open('rb') as source, output_apk.open('xb') as target:
    shutil.copyfileobj(source, target, 1024 * 1024)
    target.flush()
    os.fsync(target.fileno())
require(sha(output_apk) == sha(signed), 'Candidate copy differs')
result = {'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sourceBase': 'R57', 'baseCommit': BASE_COMMIT, 'baseSHA256': BASE_APK_SHA,
          'apk': str(output_apk), 'sha256': sha(output_apk), 'bytes': output_apk.stat().st_size,
          'certificateSHA256': CERT_SHA, 'changed': sorted(replacements), 'runtimeSHA256': sha(native), 'engineManifestSHA256': sha(engine_manifest),
          'clientDexSHA256':sha(client_dex), 'roomsDexSHA256': sha(dex), 'preservedEntries': preserved,
          'allPackageEntriesVerified': True, 'alignment16KiB': True,
          'installed': False, 'stable': False, 'twoDeviceGameplayVerified': False,
          'classGate':class_gate, 'requiresAutomaticPasswordRegistry': True, 'onlineRuntimeChanged': True, 'onlineCoresAndControlsChanged': False, 'requestProofImplemented':True, 'hardwareAttestationVerified':False}
(stage / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
print(json.dumps(result, indent=2))
