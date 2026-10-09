"""Select a fully verified R95 backup. Old channel retained until separate cleanup."""
from pathlib import Path
import copy, datetime, hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-snes-light-maps-r95-20261009')
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
OLD='test-up-to-4-players-r94'
NEW='test-up-to-4-players-r95'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text('utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
    active=read(REPO/'release-channels/ACTIVE.json')
    assert active==read(BACKUP/'release-channels/ACTIVE.json')
    assert active['channels']['test-4p']['directory']==OLD
    package=read(ROOT/'evidence/package.json');jr=read(WORK/'java-build-receipt.json')
    assert package['version']=='R95' and package['allPackageEntriesVerified'] and package['alignment16KiB']
    assert package['runtimeCoresEnginesUnchangedFromR94'] and not package['archivedDreamcastEffectIncluded']
    assert sha(WORK/'java-build-receipt.json')==package['javaReceiptSHA256']
    dest=BACKUP/NEW;assert not dest.exists();dest.mkdir()
    origins={}
    def put(src,name):
        dst=dest/name;assert dst.resolve().is_relative_to(dest.resolve())
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst)
        origins[name]=str(src)
    for n,h in jr['sourceHashes'].items():
        assert sha(WORK/'java'/n)==h
        put(WORK/'java'/n,'java/'+n)
    assert len(jr['sourceHashes'])==220
    for p in (WORK/'carousel-inputs').rglob('*'):
        if p.is_file():put(p,p.relative_to(WORK).as_posix())
    for p in (BACKUP/OLD/'assets').rglob('*'):
        if p.is_file():put(p,'assets/'+p.relative_to(BACKUP/OLD/'assets').as_posix())
    for n in ('JAVA-SOURCE-MANIFEST.json','java-build-receipt.json'):put(WORK/n,n)
    for mod,dex in [('client','classes28.dex'),('rooms','classes35.dex')]:
        p=WORK/'compiled-final'/(mod+'-dex')/'classes.dex';assert sha(p)==jr[mod+'DexSHA256'];put(p,'compiled/'+dex)
    put(WORK/'native/libturbo_carousel.so','compiled/libturbo_carousel.so')
    cmd=read(WORK/'carousel-command.json')
    cmd['command']=[a.replace('{BACKUP}/'+OLD+'/', '{BACKUP}/'+NEW+'/') for a in cmd['command']]
    assert all(OLD not in a for a in cmd['command']);write(dest/'carousel-command.json',cmd)
    assert sha(dest/'compiled/libturbo_carousel.so')==package['protectedEntries']['lib/arm64-v8a/libturbo_carousel.so']
    apk=Path(package['temporaryApk']);assert sha(apk)==package['sha256'];put(apk,apk.name)
    inventory={p.relative_to(dest).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in dest.rglob('*') if p.is_file()}
    channel=copy.deepcopy(active['channels']['test-4p'])
    channel.update(version='R95',directory=NEW,branch='fix/station-snes-light-maps-r95-20261009',sourceCommit=None,
        sourceCommitStatus='pending',sourceDirectory='versions/'+ROOT.name,apk=apk.name,apkSHA256=package['sha256'],
        javaSourceCount=220,installed=False,installedDevices=[],installationReceipt=None,
        descriptiveEditionsReviewed=5,onlineApprovalChanged=False,coverLEDsEnabled=True,sharedCarouselLighting=True,holdFramesBeforeLast=2,starsLoweredHeightFraction=0.020,installationStatus='R95 not installed yet')
    active['channels']['test-4p']=channel
    guard=read(BACKUP/'BUILD-INPUTS-VERIFIED.json')
    guard['files']={n:v for n,v in guard['files'].items() if not n.startswith(OLD+'/')}
    for n,v in inventory.items():guard['files'][NEW+'/'+n]=dict(v,origin=origins.get(n,'Canonical R81 carousel command; channel path only'))
    guard['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    guard['updatedBy']='R95 verified source and package consolidation'
    write(BACKUP/'BUILD-INPUTS-VERIFIED.json',guard)
    for p in [REPO/'release-channels/ACTIVE.json',BACKUP/'release-channels/ACTIVE.json']:write(p,active)
    receipt=dict(version='R95',verified=True,backupDirectory=str(dest),apkSHA256=package['sha256'],
        verifiedFiles=inventory,sourceCount=220,previousChannel=OLD,cleanupPending=True,serverChanged=False)
    write(ROOT/'evidence/consolidation.json',receipt)
    print(json.dumps(dict(version='R95',verifiedFiles=len(inventory),apkSHA256=package['sha256'],backup=str(dest))))
if __name__=='__main__':main()
