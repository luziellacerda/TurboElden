"""Restore the full source from the exact versioned ancestors; no binaries/secrets."""
from pathlib import Path
import shutil,json,hashlib,sys
D=Path(__file__).resolve().parent.parent
if not str(D).startswith('\\\\?\\'):D=Path('\\\\?\\'+str(D))
V=D.parent
assert len(sys.argv)==2,'Supply a NEW output directory on E: for restored sources'
O=Path(sys.argv[1]).resolve();assert O.drive.upper()=='E:' and not O.exists()
O.mkdir(parents=True)
for group,base in [('native','station-layout-r26-20261005'),('netplay-src','station-compact-lobby-r27-20261005'),('dependency-src','station-compact-lobby-r27-20261005')]:
 source=V/base/group;assert source.is_dir(),str(source)
 shutil.copytree(source,O/group)
 if (D/group).exists():shutil.copytree(D/group,O/group,dirs_exist_ok=True)
expected=json.loads((D/'SOURCE-MANIFEST.json').read_text())
for group,files in expected.items():
 actual={str(p.relative_to(O/group)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/group).rglob('*') if p.is_file()}
 assert actual==files,group
print('Complete native/Java source restored and all hashes verified:',O)
