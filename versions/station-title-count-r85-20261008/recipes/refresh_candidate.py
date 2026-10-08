from pathlib import Path
import json,hashlib,shutil,os,datetime
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
WORK=Path(r"E:\ESTUDO APK\work\station-title-count-r85-20261008")
BACKUP=Path(r"G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008")
DEST=BACKUP/'test-up-to-4-players-r85'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
package=read(ROOT/'evidence/package.json');apk=DEST/'TurboStations-Premium-R85-20261008.apk'
assert sha(apk)=='b8a153802c5c9e564679d726a6074b96307705a0e1677dfd4c8abd6677497ef2'
for rel in ['carousel-inputs/'+n for n in read(ROOT/'evidence/native-build.json')['changedSources']]+['carousel-inputs/d0/station_compact_topbar.h','carousel-command.json']:
 shutil.copyfile(WORK/rel,DEST/rel)
shutil.copyfile(WORK/'native/libturbo_carousel.so',DEST/'compiled/libturbo_carousel.so')
assert sha(DEST/'compiled/libturbo_carousel.so')==package['changedEntrySHA256']['lib/arm64-v8a/libturbo_carousel.so']
tmp=apk.with_suffix('.apk.new');assert not tmp.exists();shutil.copyfile(Path(package['temporaryApk']),tmp)
assert sha(tmp)==package['sha256'];os.replace(tmp,apk)
for p in [REPO/'release-channels/ACTIVE.json',BACKUP/'release-channels/ACTIVE.json']:
 a=read(p);assert a['channels']['test-4p']['version']=='R85';a['channels']['test-4p']['apkSHA256']=package['sha256'];write(p,a)
g=read(BACKUP/'BUILD-INPUTS-VERIFIED.json')
for p in DEST.rglob('*'):
 if p.is_file():
  n=p.relative_to(BACKUP).as_posix();g['files'][n]={'sha256':sha(p),'bytes':p.stat().st_size,'origin':'R85 count visibility correction observed on Motorola'}
write(BACKUP/'BUILD-INPUTS-VERIFIED.json',g)
c=read(ROOT/'evidence/consolidation.json');c['apkSHA256']=package['sha256'];c['verifiedFiles']={p.relative_to(DEST).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in DEST.rglob('*') if p.is_file()};c['physicalCountVisibilityCorrected']=True;write(ROOT/'evidence/consolidation.json',c)
print('Corrected R85 canonical files verified and refreshed')
