#!/usr/bin/env python3
"""Apply the three bridge sources only after all R15 source hashes are checked."""
import argparse,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--target-java',type=Path,required=True);p.add_argument('--backup',type=Path);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
version=Path(__file__).resolve().parents[1];source=version/'java/org/emulationstation/frontend';prior=version.parent/'station-emulators-r15-20261005/mame/java/org/emulationstation/frontend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changes=[]
for file in sorted(source.glob('*.java')):
 target=a.target_java/file.name
 if target.exists() and sha(target)==sha(file):continue
 original=prior/file.name
 if original.exists():assert target.is_file() and sha(target)==sha(original),'R15 source differs; reconcile before replacing '+file.name
 else:assert not target.exists(),'New class already differs: '+file.name
 changes.append((file,target))
print(json.dumps({'changes':[file.name for file,_ in changes],'dryRun':a.dry_run}))
if not a.dry_run and changes:
 assert a.backup is not None and not a.backup.exists(),'Choose a new backup directory'
 a.backup.mkdir(parents=True);a.target_java.mkdir(parents=True,exist_ok=True);manifest={}
 for file,target in changes:
  if target.exists():shutil.copy2(target,a.backup/target.name);manifest[target.name]=sha(target)
 (a.backup/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 for file,target in changes:shutil.copy2(file,target);assert sha(file)==sha(target)
