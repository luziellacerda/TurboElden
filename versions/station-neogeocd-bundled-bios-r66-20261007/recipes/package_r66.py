"""R66: prepare the BIOS already embedded in R65 automatically. No cartridge or recovery claim."""
from pathlib import Path
import zipfile, struct, shutil, hashlib, subprocess, json, os, copy, datetime

W = Path(__file__).resolve().parent
dexReceipt = json.loads((W/'evidence/build.json').read_text('utf8'))
B = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R65-20261007.apk')
O = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R66-20261007.apk')
U = W / 'unsigned.apk'
J = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP'] = os.environ['TMP'] = str(W)

def sha(p):
    with open(p, 'rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def zsha(z, n):
    with z.open(n) as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def signature(n):
    return n.startswith('META-INF/') and n.upper().endswith(('.MF', '.SF', '.RSA', '.DSA', '.EC'))
def run(args, name):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True, encoding='utf8', errors='replace')
    (W / (name + '.log')).write_text(result.stdout + result.stderr, 'utf8')
    assert result.returncode == 0, (result.stdout + result.stderr)[-4000:]
    return result.stdout + result.stderr

base_hash = '1858459b62a38a85cdd9fbeaafc68d3560008f154f99dd1431752aa0594eb081'
assert sha(B) == base_hash
assert not U.exists() and not O.exists(), 'Do not overwrite a prior candidate'
assert shutil.disk_usage(W).free > B.stat().st_size + 16 * 1024 * 1024
assert shutil.disk_usage(O.parent).free > B.stat().st_size + 32 * 1024 * 1024
replacements = {'classes30.dex':W/'dex/classes.dex'}
additions = {}
with zipfile.ZipFile(B) as reference:
    for asset in (W/'assets').rglob('*'):
        if asset.is_file():
            entry=asset.relative_to(W).as_posix()
            (replacements if entry in reference.namelist() else additions)[entry]=asset
assert sha(W/'dex/classes.dex')==dexReceipt['dexSHA256']
with zipfile.ZipFile(B) as old:
    def put(out, info):
        name = info.filename
        path = replacements.get(name) or additions.get(name)
        item = copy.copy(info)
        item.extra = b''
        item.file_size = path.stat().st_size if path else info.file_size
        if item.compress_type == zipfile.ZIP_STORED:
            alignment = 16384 if name.endswith('.so') else 4
            offset = out.fp.tell() + 30 + len(name.encode())
            if offset % alignment:
                pad = (-(offset + 4)) % alignment
                item.extra = struct.pack('<HH', 0xffff, pad) + bytes(pad)
        with out.open(item, 'w') as dst:
            with (path.open('rb') if path else old.open(info)) as src:
                shutil.copyfileobj(src, dst, 1024 * 1024)
    print('Packaging R66: bundled BIOS automatic preparation; exact R65 base', flush=True)
    with zipfile.ZipFile(U, 'w', allowZip64=True) as out:
        for info in old.infolist():
            if not signature(info.filename): put(out, info)
        for name,path in additions.items():
            assert name not in old.namelist()
            info=zipfile.ZipInfo(name);info.compress_type=zipfile.ZIP_DEFLATED
            put(out,info)
run([BT / 'zipalign.exe', '-c', '-P', '16', '4', U], 'unsigned-alignment')
print('Signing with the original application certificate', flush=True)
run([J / 'java.exe', '-Djava.io.tmpdir=' + str(W), '-jar', BT / 'lib/apksigner.jar', 'sign',
     '--alignment-preserved', 'true', '--v4-signing-enabled', 'false', '--ks',
     os.environ['STATION_KEYSTORE'], '--ks-key-alias', os.environ['STATION_KEY_ALIAS'],
     '--ks-pass', 'env:STATION_KS_PASS', '--key-pass', 'env:STATION_KEY_PASS', '--out', O, U], 'sign')
certificate = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert certificate in run([J / 'java.exe', '-jar', BT / 'lib/apksigner.jar', 'verify', '--print-certs', O], 'signature')
run([BT / 'zipalign.exe', '-c', '-P', '16', '4', O], 'alignment')
print('Checking complete package preservation against the verified base', flush=True)
changes, preserved = [], 0
with zipfile.ZipFile(B) as before, zipfile.ZipFile(O) as after:
    old_names = {n for n in before.namelist() if not signature(n)}
    new_names = {n for n in after.namelist() if not signature(n)}
    assert new_names == old_names | set(additions)
    for name,path in additions.items():assert zsha(after,name)==sha(path)
    assert len(after.namelist()) == len(set(after.namelist()))
    for name in sorted(old_names):
        got, prior = zsha(after, name), zsha(before, name)
        expected = sha(replacements[name]) if name in replacements else prior
        assert got == expected, name
        if got != prior: changes.append(name)
        else: preserved += 1
    assert set(changes)=={n for n,p in replacements.items() if zsha(before,n)!=sha(p)}
    assert zsha(after,'resources.arsc')=='1e33730bf8fc2b7bd4c6994c2254b2dffb3e44fff8b359e22a51627dde9103dd'
    assert zsha(before,'classes30.dex')=='9dc641418b05663f0b548dbb01b3e2dab398fd73122a2b734b8509c19f68b080'
    assert zsha(after,'classes30.dex')==dexReceipt['dexSHA256']
    rooms = zsha(after, 'classes35.dex')
    assert rooms == zsha(before,'classes35.dex') == 'b11459d8bf42e12d26ed5103b9ed62d1e0df674cfc31c79bffe49b48756f2a97'
    assert zsha(after,'lib/arm64-v8a/libturbo_carousel.so')==zsha(before,'lib/arm64-v8a/libturbo_carousel.so')
result = {
    'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'base': str(B), 'baseSHA256': base_hash, 'apk': str(O), 'sha256': sha(O),
    'bytes': O.stat().st_size, 'certificateSHA256': certificate, 'changed': changes,
    'preservedEntries': preserved, 'addedAssets': {n:sha(p) for n,p in additions.items()},
    'roomsDexSHA256': rooms, 'allPackageEntriesVerified': True, 'alignment16KiB': True,
    'onlineRuntimeChanged':False, 'netplayProtocolChanged':False, 'timeoutPolicyChanged':False,
    'nativeEmulatorsAndUserSettingsPreserved':True, 'neoCdBridgeChanged':True, 'bundledBIOSPreparedAutomatically':True, 'newBIOSAssetsAdded':False, 'cartridgeFaultFixed':False, 'neoCdAndroidGameplayVerified':False, 'installed':False, 'stable':False,
    'androidControlsVerified':False, 'disconnectFixed':False, 'twoDeviceGameplayVerified':False,
}
(W / 'build-result.json').write_text(json.dumps(result, indent=2), 'utf8')
assert U.resolve().parent == W.resolve() and U.name == 'unsigned.apk'
U.unlink()
print(json.dumps(result, indent=2))
