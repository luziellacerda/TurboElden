"""Compare declared launch set names with the full official MAME 0.289 registry.
This does not inspect ROM members or prove gameplay compatibility.
"""
from pathlib import Path, PurePosixPath
import argparse, csv, hashlib, json, re
p=argparse.ArgumentParser();p.add_argument('--catalog-tsv',type=Path,required=True);p.add_argument('--registry',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
expected=json.loads((root/'evidence/official-sources.json').read_text('utf8'))['mame.lst']['sha256']
assert hashlib.sha256(a.registry.read_bytes()).hexdigest()==expected, 'Use the recorded MAME 0.289 registry'
drivers={};origin=None
for line in a.registry.read_text('utf8').splitlines():
    line=line.split('//',1)[0].strip()
    if line.startswith('@source:'):origin=line[len('@source:'):]
    elif origin and re.fullmatch(r'[a-z0-9_]+',line):drivers[line]=origin
rows=list(csv.DictReader(a.catalog_tsv.open(encoding='utf-8-sig',newline=''),delimiter='\t'))
cart=[];cd=[]
for row in rows:
    platform=row['platform'].lower()
    if platform not in ('neogeo','neogeocd','neo-geo','neo-geo-cd'):continue
    launch=row['artifactLaunchPath'];name=PurePosixPath(launch.replace('\\','/')).stem.lower()
    folder=json.loads(row['folderPath'])
    entry={'game':row['name'],'folder':folder,'launch':launch,'mameDriverSource':drivers.get(name),'registeredInMAME0289':name in drivers}
    (cd if platform in ('neogeocd','neo-geo-cd') else cart).append(entry)
kof=[e for e in cart if any('KING OF FIG' in part.upper() for part in e['folder'])]
result={'cartCount':len(cart),'cdCount':len(cd),'cartDriversMatched':sum(e['registeredInMAME0289'] for e in cart),'unmatched':[e for e in cart if not e['registeredInMAME0289']],'kingCollection':kof,'otherHardware':[e for e in cart if e['registeredInMAME0289'] and e['mameDriverSource']!='snk/neogeo.cpp'],'allCDLaunchPathsAreCHD':all(e['launch'].lower().endswith('.chd') for e in cd),'cartAudit':cart,'catalogSHA256':hashlib.sha256(a.catalog_tsv.read_bytes()).hexdigest(),'ROMFilesInspected':False,'liveHTTPQueried':False}
assert not a.output.exists();a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)}))
