"""Package verified R67 media/native output over the exact R66, preserving every other entry."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, os, shutil, struct, subprocess, sys, zipfile
sys.dont_write_bytecode = True
from source_composition import verified_composition
from dex_gates import verify_modules

parser = argparse.ArgumentParser()
parser.add_argument('--workspace', default=r'E:\ESTUDO APK\work\station-collection-videos-r67-20261007')
parser.add_argument('--output', default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R67-20261007.apk')
args = parser.parse_args()
work, output = Path(args.workspace).resolve(), Path(args.output).resolve()
assert work.drive.upper() == 'E:' and output.drive.upper() == 'G:'
receipt = json.loads((work / 'evidence/build.json').read_text('utf8'))
base = Path(receipt['baseAPK'])
unsigned = work / 'unsigned.apk'
assert not unsigned.exists() and not output.exists(), 'Preserve previous outputs'
assert receipt['oneDecoderPolicyTestsPassed'] and len(receipt['videos']) == 9
assert all(row['fullFrameDecodePassed'] for row in receipt['videos'])
assert receipt['menuMaximumFps'] == 30 and receipt['idleDialogFps'] == 15
tools = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
java = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
env = dict(os.environ, TEMP=str(work / 'temp'), TMP=str(work / 'temp'))
for name in ('STATION_KEYSTORE', 'STATION_KEY_ALIAS', 'STATION_KS_PASS', 'STATION_KEY_PASS'):
    assert env.get(name), 'Provide original signing credentials privately: ' + name

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def zsha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def signature(name):
    return name.startswith('META-INF/') and name.upper().endswith(('.MF', '.SF', '.RSA', '.DSA', '.EC'))

def run(arguments, label):
    result = subprocess.run(list(map(str, arguments)), capture_output=True, text=True, encoding='utf8', errors='replace', env=env)
    (work / 'evidence' / (label + '.log')).write_text(result.stdout + result.stderr, 'utf8')
    if result.returncode:
        raise RuntimeError(label + ' failed; inspect its local log')
    return result.stdout + result.stderr

assert sha(base) == receipt['baseSHA256'] == 'e4397fd743c410ea060f17446706d9475b5568caad379e1a6df37672c60398d1'
assert sha(work / 'libturbo_carousel.so') == receipt['nativeSHA256']
replacements = {'lib/arm64-v8a/libturbo_carousel.so': work / 'libturbo_carousel.so'}
client = json.loads((work / 'java/evidence/build.json').read_text('utf8'))
assert client['compiled'] and client['base'] == 'R66' and client['baseAPK'] == receipt['baseSHA256']
assert client['requestProofIntegrated'] and client['java8API34']
resolved = verified_composition()
assert client['sourceHashes'] == {name:sha(source) for name,source in resolved.items()}
for name, expected in client['sourceHashes'].items():assert sha(work / 'java' / name) == expected, name
assert sha(work / 'java/build/client.jar') == client['clientJarSHA256']
assert sha(work / 'java/build/rooms.jar') == client['roomsJarSHA256']
for slot,module in [('classes28.dex','client'),('classes35.dex','rooms')]:
    source=work / 'java/build' / (module+'-dex') / 'classes.dex'
    assert sha(source) == client[module+'DexSHA256']
    replacements[slot]=source
for row in receipt['videos']:
    assert sha(row['output']) == row['sha256']
    replacements[row['asset']] = Path(row['output'])
certificate = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert certificate in run([java, '-jar', tools / 'lib/apksigner.jar', 'verify', '--print-certs', base], 'base-signature')
with zipfile.ZipFile(base) as old:
    assert len(old.namelist()) == len(set(old.namelist()))
    class_gate = verify_modules(old,{name:source.read_bytes() for name,source in replacements.items() if name.endswith('.dex')})
    additions = set(replacements) - set(old.namelist())
    assert len(additions) == 3
    expected_size = base.stat().st_size + sum(p.stat().st_size - (old.getinfo(n).file_size if n not in additions else 0) for n, p in replacements.items())
    assert shutil.disk_usage(work).free > expected_size + 32 * 1024**2, 'Insufficient E: packaging space'
    assert shutil.disk_usage(output.parent).free > expected_size + 32 * 1024**2, 'Insufficient G: final artifact space'
    with zipfile.ZipFile(unsigned, 'w', allowZip64=True) as new:
        infos = [info for info in old.infolist() if not signature(info.filename)]
        infos += [zipfile.ZipInfo(name) for name in sorted(additions)]
        for info in infos:
            name = info.filename
            item = copy.copy(info)
            item.extra = b''
            if name in replacements:
                item.file_size = replacements[name].stat().st_size
                # AssetManager.openFd requires MP4 assets to be stored, never deflated.
                item.compress_type = zipfile.ZIP_STORED
            if item.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if name.endswith('.so') else 4
                offset = new.fp.tell() + 30 + len(name.encode('utf8'))
                if offset % alignment:
                    pad = (-(offset + 4)) % alignment
                    item.extra = struct.pack('<HH', 0xffff, pad) + bytes(pad)
            with new.open(item, 'w') as dst:
                with (replacements[name].open('rb') if name in replacements else old.open(info)) as src:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
run([tools / 'zipalign.exe', '-c', '-P', '16', '4', unsigned], 'unsigned-alignment')
run([java, '-Djava.io.tmpdir=' + str(work / 'temp'), '-jar', tools / 'lib/apksigner.jar', 'sign',
     '--alignment-preserved', 'true', '--v4-signing-enabled', 'false', '--ks', env['STATION_KEYSTORE'],
     '--ks-key-alias', env['STATION_KEY_ALIAS'], '--ks-pass', 'env:STATION_KS_PASS',
     '--key-pass', 'env:STATION_KEY_PASS', '--out', output, unsigned], 'sign')
assert certificate in run([java, '-jar', tools / 'lib/apksigner.jar', 'verify', '--print-certs', output], 'signature')
run([tools / 'zipalign.exe', '-c', '-P', '16', '4', output], 'alignment')
changes, preserved = [], 0
with zipfile.ZipFile(base) as old, zipfile.ZipFile(output) as new:
    old_names = {n for n in old.namelist() if not signature(n)}
    new_names = {n for n in new.namelist() if not signature(n)}
    assert new_names == old_names | additions and len(new.namelist()) == len(set(new.namelist()))
    for name in sorted(new_names):
        before = zsha(old, name) if name in old_names else None
        expected = sha(replacements[name]) if name in replacements else before
        assert zsha(new, name) == expected, name
        if before != expected:
            changes.append(name)
        else:
            preserved += 1
    assert {n for n in changes if n.endswith('.dex')} == {'classes28.dex','classes35.dex'}
    videos = [n for n in new_names if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4')]
    assert len(videos) == 55
    for name in videos:
        assert new.getinfo(name).compress_type == zipfile.ZIP_STORED
        inspected = subprocess.run([shutil.which('ffprobe'), '-v', 'error', '-show_streams', '-of', 'json', 'pipe:0'], input=new.read(name), capture_output=True, env=env, check=True)
        streams = json.loads(inspected.stdout)['streams']
        assert len(streams) == 1
        stream = streams[0]
        assert (stream['codec_type'], stream['codec_name'], stream['width'], stream['height'], stream['r_frame_rate']) == ('video', 'h264', 720, 720, '30/1'), name
    assert zsha(new, 'classes30.dex') == '1dcfa1e69686a326e22c54b9adc7c6013644e69d14642664e2ab7b5e2eee4ff4'
    assert zsha(new, 'classes35.dex') == client['roomsDexSHA256']
    assert zsha(new, 'assets/station-online/engines.json') == zsha(old, 'assets/station-online/engines.json')
    assert zsha(new, 'lib/arm64-v8a/libstation_retroarch.so') == zsha(old, 'lib/arm64-v8a/libstation_retroarch.so')
result = dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), apk=str(output),
              sha256=sha(output), bytes=output.stat().st_size, baseSHA256=receipt['baseSHA256'],
              certificateSHA256=certificate, changed=changes, added=sorted(additions),
              preservedEntries=preserved, allPackageEntriesVerified=True, alignment16KiB=True,
              packagedVideoCount=55, allVideos720Square30fpsSilent=True, allVideoAssetsStored=True,
              onlyFocusedPlays=True, menuMaximumFps=30, idleDialogFps=15,
              requestProofIntegrated=True, classGate=class_gate, originalEmulatorsPreserved=True,
              nativeRuntimeAndEnginesPreserved=True, originalRSAIdentityPreserved=True,
              hardwareAttestationVerified=False, installed=False, stable=False)
(work / 'evidence/package.json').write_text(json.dumps(result, indent=2) + '\n', 'utf8')
# Only remove the unsigned intermediate created by this script after full verification.
assert unsigned.resolve().parent == work and unsigned.name == 'unsigned.apk'
unsigned.unlink()
print(json.dumps(result, indent=2))
