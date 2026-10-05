from pathlib import Path
import subprocess,sys,shutil,json,hashlib
D=Path(__file__).resolve().parent.parent;V=D.parent
assert len(sys.argv)==2
O=Path(sys.argv[1]).resolve();assert O.drive.upper()=='E:' and not O.exists()
subprocess.run([sys.executable,str(V/'station-title-actions-r33-20261005/recipes/restore_r33.py'),str(O)],check=True)
shutil.copytree(V/'station-online-recovery-r34-20261005/netplay-src',O/'netplay-src',dirs_exist_ok=True)
shutil.copytree(D/'native',O/'native',dirs_exist_ok=True)
for group,files in json.loads((D/'SOURCE-MANIFEST.json').read_text('utf8')).items():
 actual={p.relative_to(O/group).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/group).rglob('*') if p.is_file()}
 assert actual==files,group
print('Complete R36 native/Java source restored; all hashes match:',O)
