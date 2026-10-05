from pathlib import Path
import hashlib, shutil, json
W=Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
src=Path(r'E:\ESTUDO APK\work\station-neogeo-access-20261005\TurboStations-NeoGeo-Pastas-R18-20261005.apk')
root=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais')
dst=root/src.name
expected='a29151da312830d826f6ea71ebb61cb8a39fe1c21786f719e26a61568b29b1c4'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert src.resolve().parent==Path(r'E:\ESTUDO APK\work\station-neogeo-access-20261005').resolve()
assert dst.resolve().parent==root.resolve()
assert src.is_file() and sha(src)==expected
if not dst.exists():shutil.copy2(src,dst)
assert dst.stat().st_size==src.stat().st_size and sha(dst)==expected
receipt={'source':str(src),'archive':str(dst),'sha256':expected,'bytes':src.stat().st_size,'copiedAndVerified':True,'removedDuplicateE':True}
src.unlink()
(W/'r18-archive.json').write_text(json.dumps(receipt,indent=2),'utf8')
manifest=json.loads((W/'source-base.json').read_text('utf8'));manifest['baseAPK']=str(dst)
(W/'source-base.json').write_text(json.dumps(manifest,indent=2),'utf8')
print(json.dumps(receipt,indent=2))
