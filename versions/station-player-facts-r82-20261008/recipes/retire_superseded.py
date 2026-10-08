"""Retire only the verified obsolete R81 APK and duplicate E: APK; keep all older sources and build artifacts."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
WORK=Path(r'E:\ESTUDO APK\work\station-player-facts-r82-20261008')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text('utf8'))
def files(root):
    assert root.is_dir() and not root.is_symlink() and not root.is_junction()
    found=[]
    for p in root.rglob('*'):
        assert not p.is_symlink() and not p.is_junction() and p.resolve().is_relative_to(root.resolve())
        if p.is_file():found.append(p)
    return found
def main():
    rep=read(ROOT/'evidence/backup-reproduction.json');assert rep['javaReproduced'] and rep['carouselReproduced']
    receipt=read(ROOT/'evidence/consolidation.json');new=Path(receipt['backupDirectory'])
    assert new.resolve()==BACKUP.resolve()/'test-up-to-4-players-r82'
    assert {p.relative_to(new).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in files(new)}==receipt['verifiedFiles']
    active=read(REPO/'release-channels/ACTIVE.json');assert active['channels']['test-4p']['apkSHA256']==receipt['apkSHA256']
    package=read(ROOT/'evidence/package.json');temp=Path(package['temporaryApk'])
    assert temp.resolve()==WORK.resolve()/'package/TurboStations-Premium-R82-20261008.apk'
    assert not temp.is_symlink() and sha(temp)==receipt['apkSHA256']
    old=BACKUP/'test-up-to-4-players-r81';resolved=old.resolve(strict=True)
    assert resolved==BACKUP.resolve()/'test-up-to-4-players-r81' and resolved.parent==BACKUP.resolve()
    previous=read(BACKUP/'BACKUP-COMPLETE.json')['files']
    for p in files(old):
        rec=previous[p.relative_to(BACKUP).as_posix()];assert sha(p)==rec['sha256'] and p.stat().st_size==rec['bytes']
    # Historical R81 sources must be committed, not only present in a working folder.
    result=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'cat-file','-e','HEAD:versions/station-online-readiness-r81-20261008/JAVA-SOURCE-MANIFEST.json'],cwd=REPO,capture_output=True)
    assert result.returncode==0
    old_apk=resolved/'TurboStations-Premium-R81-20261008.apk'
    assert old_apk.resolve().parent==resolved and old_apk.is_file() and not old_apk.is_symlink()
    assert sha(old_apk)==package['baseSHA256']
    old_apk.unlink();temp.unlink()
    expected={BACKUP/c['directory']/c['apk'] for c in active['channels'].values()}
    assert set(BACKUP.rglob('*.apk'))==expected
    receipt.update(cleanupPending=False,canonicalApkCount=2,removed=[str(old_apk),str(temp)],previousSourceDirectoryPreserved=True)
    (ROOT/'evidence/consolidation.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    print('Only obsolete R81 APK and exact duplicate R82 APK retired; older sources preserved, two canonical installers remain.')
if __name__=='__main__':main()
