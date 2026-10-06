from pathlib import Path
import sys,subprocess,shutil,json,hashlib
D=Path(__file__).resolve().parent.parent;V=D.parent
assert len(sys.argv)==2
O=Path(sys.argv[1]).resolve();assert O.drive.upper()=='E:' and not O.exists(), 'Use a new directory on E:'
subprocess.run([sys.executable,str(V/'station-carousel-scope-r38-20261006/recipes/restore_r38.py'),str(O)],check=True)
shutil.copytree(D/'native',O/'native',dirs_exist_ok=True)
for group,files in json.loads((D/'SOURCE-MANIFEST.json').read_text('utf8')).items():
 actual={p.relative_to(O/group).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/group).rglob('*') if p.is_file()}
 assert actual==files,group
for group in ('tests','data','assets','metadata-xml'):shutil.copytree(D/group,O/group,dirs_exist_ok=True)
for group in ('temp','evidence'):(O/group).mkdir(exist_ok=True)
shutil.copy2(D/'evidence/native-build-input.json',O/'evidence/native-build-input.json')
shutil.copy2(D/'EXTERNAL-BUILD-INPUTS.json',O/'EXTERNAL-BUILD-INPUTS.json')
for name in ('build_r39.py','package_r39.py','test_r39.py'):shutil.copy2(D/'recipes'/name,O/name)
for name,digest in json.loads((D/'ASSET-MANIFEST.json').read_text('utf8')).items():assert hashlib.sha256((O/name).read_bytes()).hexdigest()==digest,name
print('R39 sources and frozen assets restored and verified:',O)
