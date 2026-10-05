"""Archive completed binary outputs only, after the coordinating task releases them."""
from pathlib import Path
import hashlib,shutil,json
W=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005')
R=Path(r'E:\ESTUDO APK\work\station-console-games-only-r21-20261005')
G=Path(r'G:\BAKUP SISTEMA APP 03-10-2026')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
build=json.loads((R/'build-result.json').read_text('utf8'))
native=json.loads((R/'evidence/native-build.json').read_text('utf8'))
integration=json.loads((W/'evidence/integration.json').read_text('utf8'))
rows=[(Path(build['apk']),G/'apks-candidatos-visuais'/Path(build['apk']).name,build['sha256'],R),
      (R/'libturbo_carousel.so',G/'binarios-compilados'/R.name/'libturbo_carousel.so',native['soSHA256'],R),
      (W/'libturbo_carousel.so',G/'binarios-compilados'/W.name/'libturbo_carousel.so',integration['soSHA256'],W)]
out=[]
for src,dst,digest,allowed in rows:
 assert src.resolve().parent==allowed.resolve() and dst.resolve().is_relative_to(G.resolve())
 if src.exists():assert sha(src)==digest
 dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copyfile(src,dst)
 assert sha(dst)==digest
 size=dst.stat().st_size
 if src.exists():
  assert src.stat().st_size==size
  src.unlink()
 out.append({'source':str(src),'archive':str(dst),'sha256':digest,'bytes':size,'copyVerifiedBeforeRemovingDuplicate':True})
 print('Archived verified output:',dst,flush=True)
(W/'evidence/compiled-output-archives.json').write_text(json.dumps(out,indent=2)+'\n','utf8')
