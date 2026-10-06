from pathlib import Path
import subprocess,sys,shutil,json,hashlib
D=Path(__file__).resolve().parent.parent;V=D.parent
assert len(sys.argv)==2
O=Path(sys.argv[1]).resolve();assert O.drive.upper()=='E:' and not O.exists()
subprocess.run([sys.executable,str(V/'station-final-details-r37-20261005/recipes/restore_r37.py'),str(O)],check=True)
for name in json.loads((D/'REMOVED-SOURCES.json').read_text('utf8')):
 p=(O/'native'/name).resolve();assert p.parent==(O/'native').resolve() and p.is_file();p.unlink()
shutil.copytree(D/'native',O/'native',dirs_exist_ok=True)
for group,files in json.loads((D/'SOURCE-MANIFEST.json').read_text('utf8')).items():
 actual={p.relative_to(O/group).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/group).rglob('*') if p.is_file()}
 assert actual==files,group
for name in ('temp','evidence','tests','data'):(O/name).mkdir(exist_ok=True)
for name in ('tests','data'):shutil.copytree(D/name,O/name,dirs_exist_ok=True)
shutil.copyfile(D/'evidence/native-build-input.json',O/'evidence/native-build-input.json')
for name in ('build_r38.py','package_r38.py','test_r38.py'):shutil.copyfile(D/'recipes'/name,O/name)
print('Complete R38 native/profile/Java sources restored; all hashes match:',O)
