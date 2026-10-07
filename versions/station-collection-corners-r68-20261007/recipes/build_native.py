"""Build the scoped R68 collection-corner change over the verified R67 native tree."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess
snapshot=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--output',default=r'E:\ESTUDO APK\work\station-collection-corners-r68-20261007-final')
a=p.parse_args();work=Path(a.output).resolve()
base=Path(r'E:\ESTUDO APK\work\station-collection-videos-r67-20261007-final')
assert work.drive.upper()=='E:' and not work.exists()
receipt=json.loads((base/'evidence/build.json').read_text('utf8'))
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name,h in receipt['nativeSources'].items():assert sha(base/'native'/name)==h,name
assert sha(base/'libturbo_carousel.so')==receipt['nativeSHA256']
work.mkdir()
for folder in ['native','temp','tests','evidence']:(work/folder).mkdir()
env=dict(os.environ,TEMP=str(work/'temp'),TMP=str(work/'temp'))
for name in receipt['nativeSources']:shutil.copyfile(base/'native'/name,work/'native'/name)
for source in (snapshot/'native').iterdir():shutil.copyfile(source,work/'native'/source.name)
current={p.name:sha(p) for p in (work/'native').iterdir() if p.is_file()}
assert [name for name,h in receipt['nativeSources'].items() if current[name]!=h]==['native_formation.h']
assert set(current)-set(receipt['nativeSources'])=={'collection_corner_policy.h'}
def run(cmd,label):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,env=env)
 (work/'evidence'/(label+'.log')).write_bytes(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(label+': '+r.stderr.decode('utf8','replace')[-2000:])
 return r.stdout.decode('utf8','replace')
host=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
run([host,'-std=c++17','-Wall','-Wextra','-Werror','-I',work/'native',snapshot/'tests/collection_corners.cpp','-o',work/'tests/corners.exe'],'corners-compile')
result=run([work/'tests/corners.exe'],'corners-test')
assert 'PASS 24 ' in result
formation=(work/'native/native_formation.h').read_text('utf8')
assert formation.count('stationCollectionCorners::radius(systemsMode,folderMode,w,h)')==1
assert 'radius=cornerRadius(width,height)' in formation and 'radius=cornerRadius(r.w,r.h)' in formation
assert 'roundedQuad(q,4,5);' in (work/'native/native_system_video720.h').read_text('utf8')
cmd=list(receipt['command'])
cmd[cmd.index(str(base/'native/native_carousel.cpp'))]=str(work/'native/native_carousel.cpp')
cmd[cmd.index(str(base/'libturbo_carousel.so'))]=str(work/'libturbo_carousel.so')
dependencies={str(Path(v)):sha(v) for v in cmd if str(v).endswith('.o')}
run(cmd,'native-build')
record=dict(createdUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),base='R67',
 baseAPK=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R67-20261007.apk',
 baseSHA256='d746cc02b602162b19509cd44ad7cf751e320de3b52199e7d48e86e9e897228f',
 nativeSHA256=sha(work/'libturbo_carousel.so'),nativeSources=current,baseNativeSHA256=receipt['nativeSHA256'],
 changedNativeSources=['native_formation.h'],addedNativeSources=['collection_corner_policy.h'],
 cornerPolicyChecks=24,sourceWiringChecks=3,objects=dependencies,command=cmd,
 proportionsChanged=False,videosReencoded=False,emulatorChanged=False,compiled=True,installed=False)
(work/'evidence/build.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
print(result.strip());print('R68 native ready; collection corners changed for every system.')
