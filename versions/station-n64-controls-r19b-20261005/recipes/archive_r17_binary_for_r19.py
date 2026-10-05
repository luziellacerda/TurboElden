from pathlib import Path
import hashlib, shutil, json
W=Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
src=Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005\libturbo_carousel.so')
root=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-single-folder-r17-20261005')
root.mkdir(parents=True,exist_ok=True)
dst=root/src.name
expected='4d2b962e09c7924e7b9b14042ee4b43e08d704bedae021131668303ae42fb39d'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert src.resolve().parent==Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005').resolve()
assert dst.resolve().parent==root.resolve()
assert src.is_file() and sha(src)==expected
if not dst.exists():shutil.copy2(src,dst)
assert dst.stat().st_size==src.stat().st_size and sha(dst)==expected
receipt={'source':str(src),'archive':str(dst),'sha256':expected,'copiedAndVerified':True,'removedDuplicateE':True,'sourcesPreserved':True}
src.unlink()
(W/'r17-binary-archive.json').write_text(json.dumps(receipt,indent=2),'utf8')
(src.parent/'binary-archive.json').write_text(json.dumps(receipt,indent=2),'utf8')
print(json.dumps(receipt,indent=2))
