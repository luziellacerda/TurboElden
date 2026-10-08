"""Retire only named obsolete/duplicate APKs; retain every older source directory."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
WORK=Path(r'E:\ESTUDO APK\work')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    evidence=json.loads((ROOT/'evidence/backup-reproduction.json').read_text())
    assert evidence['javaReproduced'] and evidence['carouselReproduced']
    expected='e42a3dc15d2badcad489520b00d6115b4e0047c9998393760c244c665f548235'
    current=BACKUP/'test-up-to-4-players-r85/TurboStations-Premium-R85-20261008.apk'
    assert sha(current)==expected
    obsolete={
      BACKUP/'test-up-to-4-players-r84/TurboStations-Premium-R84-20261008.apk':'3dd465fba8681b8de2cf32b2d87d24c1dcc478a7b6c38be4c5d4d1716bcb9495',
      WORK/'station-title-count-r85-20261008/package/TurboStations-Premium-R85-20261008.apk':expected}
    for p,d in obsolete.items():
        assert p.is_file() and not p.is_symlink() and p.resolve()==p.absolute()
        assert p.resolve().is_relative_to(BACKUP.resolve()) or p.resolve().is_relative_to(WORK.resolve())
        assert sha(p)==d
    for p in obsolete:p.unlink()
    active=json.loads((ROOT.parents[1]/'release-channels/ACTIVE.json').read_text())
    wanted={BACKUP/c['directory']/c['apk'] for c in active['channels'].values()}
    assert set(BACKUP.rglob('*.apk'))==wanted
    result=dict(onlyNamedApksRemoved=True,allSourceDirectoriesPreserved=True,removed=[str(p) for p in obsolete],remainingCanonicalApks=2)
    (ROOT/'evidence/cleanup.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
    print('Only named obsolete APKs removed; stable R76 and current R85 remain.')
if __name__=='__main__':main()
