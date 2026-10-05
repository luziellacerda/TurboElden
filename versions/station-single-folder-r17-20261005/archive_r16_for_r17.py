from pathlib import Path
import hashlib,shutil,json,datetime
p=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\TurboStations-Desempenho-Offline-R16-20261005.apk')
dest=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais')/p.name
w=Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005')
expected='b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert p.resolve().parent==Path(r'E:\ESTUDO APK\work\station-download-performance-20261005').resolve()
assert dest.resolve().parent==Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais').resolve()
if p.exists():
 assert sha(p)==expected
 if not dest.exists():shutil.copyfile(p,dest)
 assert sha(dest)==expected
 p.unlink()
assert sha(dest)==expected
(w/'r16-archive.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'from':str(p),'archive':str(dest),'sha256':expected,'duplicateRemovedAfterVerification':True},indent=2),'utf8')
print('R16 archived with matching SHA; only verified duplicate removed')
