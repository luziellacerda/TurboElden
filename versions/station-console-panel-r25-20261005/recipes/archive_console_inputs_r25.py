from pathlib import Path
import shutil,hashlib,json
W=Path(r'E:\ESTUDO APK\work\station-console-panel-r25-20261005');B=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005');G=Path(r'G:\BAKUP SISTEMA APP 03-10-2026')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((W/'evidence/native-build.json').read_text('utf8'));records=[]
for src,dst,digest in [(B/'TurboStations-NeoGeo-Laser-R24-20261005.apk',G/'apks-candidatos-visuais/TurboStations-NeoGeo-Laser-R24-20261005.apk',r['baseSHA256']),
 (W/'libturbo_carousel.so',G/'binarios-compilados/station-console-panel-r25-20261005/libturbo_carousel.so',r['soSHA256'])]:
 assert src.resolve().parent in (B.resolve(),W.resolve()) and dst.resolve().is_relative_to(G.resolve())
 assert src.is_file() and sha(src)==digest;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(src,dst)
 assert sha(dst)==digest and src.stat().st_size==dst.stat().st_size
 records.append({'source':str(src),'archive':str(dst),'sha256':digest,'bytes':src.stat().st_size,'copyVerifiedBeforeRemovingDuplicate':True});src.unlink()
# Completed R24 GL renders only. Source/test script/refs and final JSON remain in E.
for directory in sorted((B/'tests').glob('angle-*')):
 assert directory.is_dir() and directory.resolve().parent==(B/'tests').resolve()
 target=G/'evidencias-visuais/station-neogeo-laser-r24-20261005'/directory.name
 for src in sorted(directory.rglob('*')):
  if not src.is_file():continue
  assert src.resolve().is_relative_to(directory.resolve())
  dst=target/src.relative_to(directory);assert dst.resolve().is_relative_to(G.resolve())
  dst.parent.mkdir(parents=True,exist_ok=True);digest=sha(src)
  if not dst.exists():shutil.copy2(src,dst)
  assert sha(dst)==digest
  records.append({'source':str(src),'archive':str(dst),'sha256':digest,'bytes':src.stat().st_size,'copyVerifiedBeforeRemovingDuplicate':True});src.unlink()
 for child in sorted(directory.rglob('*'),key=lambda x:len(x.parts),reverse=True):
  if child.is_dir():child.rmdir()
 directory.rmdir()
(W/'evidence/compiled-output-archives.json').write_text(json.dumps(records,indent=2)+'\n','utf8')
r['baseAPK']=str(G/'apks-candidatos-visuais/TurboStations-NeoGeo-Laser-R24-20261005.apk');(W/'evidence/native-build.json').write_text(json.dumps(r,indent=2)+'\n','utf8')
print(json.dumps({'archivedFiles':len(records),'freeE':shutil.disk_usage(W).free}))
