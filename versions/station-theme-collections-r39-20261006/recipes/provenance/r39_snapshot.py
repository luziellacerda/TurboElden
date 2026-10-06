from pathlib import Path
import json,hashlib,shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');R=Path('work/TurboElden-git');D=R/'versions/station-theme-collections-r39-20261006';OLD=R/'versions/station-carousel-scope-r38-20261006'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not D.exists()
D.mkdir();(D/'native').mkdir();(D/'recipes').mkdir()
(D/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n','utf8')
m=json.loads((OLD/'SOURCE-MANIFEST.json').read_text('utf8'));prior=m['native'];m['native']={p.name:sha(p) for p in (W/'native').iterdir() if p.is_file()}
assert set(prior)<=set(m['native'])
for name,digest in m['native'].items():
 if prior.get(name)!=digest:shutil.copy2(W/'native'/name,D/'native'/name)
(D/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2),'utf8')
for group in ('data','assets','metadata-xml'):shutil.copytree(W/group,D/group)
for group in ('evidence','tests'):
 (D/group).mkdir()
 for p in (W/group).iterdir():
  if p.is_file() and p.suffix in ('.json','.log','.cpp','.h','.hpp','.c','.py'):shutil.copy2(p,D/group/p.name)
for src,dst in [('r39_restore.py','restore_r39.py'),('r39_portable_build.py','build_r39.py'),('r39_portable_tests.py','test_r39.py')]:shutil.copy2(src,D/'recipes'/dst)
s=(W/'package_r39.py').read_text('utf8').replace("W = Path(r'E:\\ESTUDO APK\\work\\station-theme-collections-r39-20261006')","W = Path(__file__).resolve().parent")
(D/'recipes/package_r39.py').write_text(s,'utf8')
(D/'recipes/provenance').mkdir()
for p in Path('.').glob('r39*'):
 if p.is_file() and p.suffix in ('.py','.cjs','.h','.cpp'):shutil.copy2(p,D/'recipes/provenance'/p.name)
shutil.copy2(W/'build-result.json',D/'STATUS.json')
for file in ('alignment.log','signature.log','unsigned-alignment.log'):shutil.copy2(W/file,D/'evidence'/file)
# External native dependency directory contains baseline headers + two retained media objects.
external={};dep=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
for p in dep.iterdir():
 if p.is_file() and p.suffix in ('.h','.hpp','.o','.so'):external[str(p)]=sha(p)
np=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\neogeo_previews.o');external[str(np)]=sha(np)
(D/'EXTERNAL-BUILD-INPUTS.json').write_text(json.dumps(external,indent=2),'utf8')
assets={p.relative_to(D).as_posix():sha(p) for group in ('assets','metadata-xml','data') for p in (D/group).rglob('*') if p.is_file()}
(D/'ASSET-MANIFEST.json').write_text(json.dumps(assets,indent=2),'utf8')
shutil.copy2(Path(r'G:\BAKUP SISTEMA APP 03-10-2026\metadata-publica-20261006\source.json'),D/'evidence/public-metadata-source.json')
print('R39 snapshot',len(m['native']),'native sources',len(assets),'assets',len(external),'external build inputs')
