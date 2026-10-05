from pathlib import Path
import subprocess,sys,shutil,json,hashlib
D=Path(__file__).resolve().parent.parent;V=D.parent
assert len(sys.argv)==2
O=Path(sys.argv[1]).resolve();assert O.drive.upper()=='E:' and not O.exists()
subprocess.run([sys.executable,str(V/'station-platform-button-r36-20261005/recipes/restore_r36.py'),str(O)],check=True)
shutil.copytree(D/'native',O/'native',dirs_exist_ok=True)
shutil.copytree(D/'frontend',O/'frontend',dirs_exist_ok=True)
(O/'frontend/build').mkdir(exist_ok=True)
for group,files in json.loads((D/'SOURCE-MANIFEST.json').read_text('utf8')).items():
 actual={p.relative_to(O/group).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/group).rglob('*') if p.is_file()}
 assert actual==files,group
print('Complete R37 native/profile/Java sources restored; all hashes match:',O)
