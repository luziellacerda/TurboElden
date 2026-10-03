"""Complete local build backup with per-file read-back verification; never uploads private files."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,shutil,time
ROOT=Path(r'G:\BAKUP SISTEMA APP 03-10-2026').resolve()
assert str(ROOT).lower()==r'g:\bakup sistema app 03-10-2026'
CANON=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002')
SOURCES=[
 (CANON,'compilacao/station-reconstruction-20261002'),
 (Path(r'E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk'),'inputs/TurboramaStation-TESTE-lado-a-lado.apk'),
 (Path(r'E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive'),'releases/estavel-station-snes-megadrive-20261003'),
 (Path(r'E:\ESTUDO APK\candidatos\2026-10-03-station-40000'),'releases/candidato-station-40000-20261003'),
 (Path(r'E:\TurboEdenEngine\android-ndk-r28c'),'ferramentas/android-ndk-r28c'),
 (Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15'),'ferramentas/android-build-tools-35-android-15'),
 (Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar'),'ferramentas/apktool_3.0.3.jar'),
 (Path(r'G:\Android\Sdk\platforms\android-34'),'ferramentas/sdk/platforms/android-34'),
 (Path(r'G:\Android\Sdk\platform-tools'),'ferramentas/sdk/platform-tools'),
 (Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot'),'ferramentas/jdk-17.0.20.101-hotspot'),
 (Path(r'C:\Python314'),'ferramentas/Python314'),
 (Path(r'C:\Program Files\CMake'),'ferramentas/CMake'),
 (Path(r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Ninja-build.Ninja_Microsoft.Winget.Source_8wekyb3d8bbwe'),'ferramentas/Ninja-build'),
 (Path(r'C:\Program Files\dotnet'),'ferramentas/dotnet'),
 (Path(r'C:\Users\Admin\.android\debug.keystore'),'assinatura-privada/debug.keystore'),
]
ROOT.mkdir(parents=True,exist_ok=True)
jobs=[];directories=[];mapping=[]
for source,relative in SOURCES:
 if not source.exists():raise RuntimeError('Missing required dependency: '+str(source))
 destination=ROOT/relative
 if not destination.resolve().is_relative_to(ROOT):raise RuntimeError('Destination outside backup')
 mapping.append({'source':str(source),'backupRelativePath':relative,'type':'directory' if source.is_dir() else 'file'})
 if source.is_dir():
  for current,subdirs,files in os.walk(source,followlinks=False):
   current=Path(current);target=destination/current.relative_to(source);directories.append(target)
   for name in subdirs+files:
    if (current/name).is_symlink():raise RuntimeError('Review symbolic dependency before backup: '+str(current/name))
   for name in files:jobs.append((current/name,target/name))
 else:jobs.append((source,destination))
total=sum(p.stat().st_size for p,_ in jobs)
if shutil.disk_usage(ROOT).free<total+1024**3:raise RuntimeError('Insufficient backup disk space')
for directory in directories:directory.mkdir(parents=True,exist_ok=True)
for _,target in jobs:target.parent.mkdir(parents=True,exist_ok=True)
print(json.dumps({'phase':'copy-and-verify','files':len(jobs),'bytes':total,'destination':str(ROOT)}),flush=True)
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy_verified(pair):
 source,target=pair;before=source.stat()
 digest=hashlib.sha256()
 if target.exists():
  # Resume only an identical previous copy; never silently overwrite a different backup.
  expected=sha(source)
  if target.stat().st_size!=before.st_size or sha(target)!=expected:raise RuntimeError('Existing backup differs: '+str(target))
 else:
  with source.open('rb') as src,target.open('xb') as dst:
   while data:=src.read(1024*1024):digest.update(data);dst.write(data)
  shutil.copystat(source,target)
  expected=digest.hexdigest()
  if sha(target)!=expected:raise RuntimeError('Read-back hash mismatch: '+str(target))
 after=source.stat()
 if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise RuntimeError('Source changed while copying: '+str(source))
 return {'path':target.relative_to(ROOT).as_posix(),'sizeBytes':before.st_size,'sha256':expected}
started=time.monotonic();last=started;records=[];copied=0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 tasks={pool.submit(copy_verified,pair) for pair in sorted(jobs,key=lambda pair:pair[0].stat().st_size,reverse=True)}
 for task in concurrent.futures.as_completed(tasks):
  entry=task.result();records.append(entry);copied+=entry['sizeBytes'];now=time.monotonic()
  if now-last>20:
   print(json.dumps({'verifiedFiles':len(records),'totalFiles':len(jobs),'verifiedBytes':copied,'totalBytes':total}),flush=True);last=now
records.sort(key=lambda r:r['path'])
manifest={'status':'complete-copy-readback-verified','root':str(ROOT),'files':len(records),'bytes':copied,'elapsedSeconds':round(time.monotonic()-started,2),'sourceMapping':mapping,'entries':records,'gitBundle':'Added separately after the delivery commit; see git/BUNDLE-MANIFEST.json','scope':'Full current Station build directory, exact APK base, stable and candidate releases, active external toolchains and signing identity. Private local backup, not Git upload.'}
path=ROOT/'MANIFESTO-ARQUIVOS-PRIVADO.json';path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={k:manifest[k] for k in ['status','root','files','bytes','elapsedSeconds','scope']}
summary['privateManifestSha256']=sha(path);summary['sourceMapping']=mapping
summary['stableApkSha256']='3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17'
summary['candidateApkSha256']='bced63f9b670b9098ffb983cf7e45335678b725d2944ee7133f77128724b9b7b'
(ROOT/'RESUMO-BACKUP.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False),flush=True)
