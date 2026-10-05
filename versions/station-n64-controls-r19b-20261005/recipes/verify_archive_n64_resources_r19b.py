from pathlib import Path
import subprocess,re,json,shutil,hashlib
W=Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
B=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-NeoGeo-Pastas-R18-20261005.apk')
new=W/'n64-resources-r19b.apk'
tool=r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\aapt2.exe'
def resources(p):
 r=subprocess.run([tool,'dump','resources',str(p)],capture_output=True,text=True,encoding='utf8',errors='strict');assert r.returncode==0,r.stderr
 parts=re.split(r'^    resource ',r.stdout,flags=re.M);result={}
 for part in parts[1:]:
  part=re.split(r'^  type ',part,flags=re.M)[0].rstrip();key=part.splitlines()[0];result[key]=part
 return result
old,now=resources(B),resources(new)
assert old.keys()==now.keys(),'Changed resource IDs/names'
diff=[key for key in old if old[key]!=now[key]]
assert len(diff)==11,(len(diff),diff)
for key in diff:
 assert ' n6_' in key or '/n6_' in key,key
 assert now[key].replace('tn64core.shaded.','')==old[key],key
 print(key)
receipt={'resourcesCompared':len(old),'changedResources':diff,'allResourceIDsPreserved':True,'onlyN64ClassNamesChanged':True}
(W/'compiled-resource-tests.json').write_text(json.dumps(receipt,indent=2),'utf8')
for n in ('n6_strings.xml','n6_styles.xml'):
 dest=W/'resources/res/values'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/'resource-project/res/values'/n,dest)
root=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-n64-controls-r19-20261005');root.mkdir(parents=True,exist_ok=True);dst=root/new.name
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if not dst.exists():shutil.copy2(new,dst)
assert sha(dst)==sha(new) and dst.stat().st_size==new.stat().st_size
(W/'resources-archive.json').write_text(json.dumps({'source':str(new),'archive':str(dst),'sha256':sha(dst),'copiedAndVerified':True},indent=2),'utf8')
print(json.dumps(receipt,indent=2))
