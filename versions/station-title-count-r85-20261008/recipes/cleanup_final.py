from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];WORK=Path(r"E:\ESTUDO APK\work\station-title-count-r85-20261008")
BACKUP=Path(r"G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008")
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
pkg=json.loads((ROOT/'evidence/package.json').read_text());repro=json.loads((ROOT/'evidence/backup-reproduction.json').read_text())
assert repro['javaReproduced'] and repro['carouselReproduced']
assert sha(BACKUP/'test-up-to-4-players-r85/TurboStations-Premium-R85-20261008.apk')==pkg['sha256']
files={WORK/'package-before-letter-b/TurboStations-Premium-R85-20261008.apk':'77436bf817f56f9cec58ff0ca3663b5d0af6c0c4c20889553809c28903c37e84',WORK/'package-before-hide-profile/TurboStations-Premium-R85-20261008.apk':'449933b7cf9c77d330221da64ea764fffb15db9a673bd4602ae73d937f026e45',WORK/'package-seventh/TurboStations-Premium-R85-20261008.apk':'7cf4a0517e5f03ea03a1692b4192176640593d9c7ea3f2f1b3e585e234fcc796',WORK/'package-fourth/TurboStations-Premium-R85-20261008.apk':'4906c83dede6f3fe791944c3fb8d319a5f54c564c169f2a76cc06e1c3cd66ff7',WORK/'package-fifth/TurboStations-Premium-R85-20261008.apk':'593307ae5fd90d9845532b200ac9e97737ffca1d0cb0e239034e9d9fa8241057',WORK/'package-third/TurboStations-Premium-R85-20261008.apk':'1818a502a40f2718f92e5e51a0bc42bb070fbd1875a1efc0237a7eba767f296e',WORK/'package-second/TurboStations-Premium-R85-20261008.apk':'8e82a76f846d6396f1d9382464625246f8308313c8c63ed022e81f5454b444d8',Path(pkg['temporaryApk']):pkg['sha256']}
files={p:d for p,d in files.items() if p.exists()}
for p,d in files.items():
 assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(WORK.resolve()) and p.resolve()==p.absolute()
 assert sha(p)==d
for p in files:p.unlink()
active=json.loads((ROOT.parents[1]/'release-channels/ACTIVE.json').read_text());wanted={BACKUP/c['directory']/c['apk'] for c in active['channels'].values()}
assert set(BACKUP.rglob('*.apk'))==wanted
(ROOT/'evidence/cleanup-final.json').write_text(json.dumps({'removedOnlyExactTemporaryApks':True,'remainingCanonicalApks':2,'sourcesPreserved':True},indent=2)+'\n')
print('Final temporary APKs removed; R76 and R85 preserved')
