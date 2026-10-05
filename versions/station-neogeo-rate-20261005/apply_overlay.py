"""Apply only the reviewed Station library changes to the existing R11 Windows work root."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent

def normalized(path): return path.read_text(encoding='utf-8-sig').replace('\r\n','\n').encode()
def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-root',type=Path,required=True)
    parser.add_argument('--backup-directory',type=Path)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args();manifest=json.loads((ROOT/'overlay-manifest.json').read_text())
    planned=[]
    for row in manifest:
        source=ROOT.parent/row['sourceVersion']/row['path']
        target=args.work_root/row['path']
        if sha(normalized(source))!=row['newSha256']:raise ValueError('Published overlay source changed: '+row['path'])
        if target.exists():
            actual=sha(normalized(target))
            if actual==row['newSha256']:continue
            if actual not in [row['previousSha256'],*row.get('acceptedPreviousSha256',[])]:raise ValueError('Current source differs; preserve and reconcile: '+row['path'])
        elif row['previousSha256'] is not None:raise ValueError('Existing Station source missing: '+row['path'])
        planned.append((row,source,target))
    if args.apply:
        if not args.backup_directory:parser.error('--backup-directory required with --apply')
        args.backup_directory.mkdir(parents=True,exist_ok=False)
        for row,source,target in planned:
            if target.exists():
                backup=args.backup_directory/row['path'];backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
        (args.backup_directory/'applied.json').write_text(json.dumps([row for row,_,_ in planned],indent=2))
    print(('Applied' if args.apply else 'Verified')+' '+str(len(planned))+' Station source files')

if __name__=='__main__':main()
