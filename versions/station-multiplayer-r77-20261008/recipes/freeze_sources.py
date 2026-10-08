"""Freeze the exact composed source set; compilation rejects later overlay changes."""
from pathlib import Path
import hashlib,json,importlib.util
R=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('r77build',R/'recipes/build_java.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
_,_,sources,_=m.verified_sources()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
value=dict(schemaVersion=1,base='R76',sources={n:sha(p) for n,p in sorted(sources.items())},overlays={p.relative_to(R/'java').as_posix():sha(p) for p in sorted((R/'java').rglob('*.java'))})
(R/'SOURCE-MANIFEST.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
print('Source manifest frozen:',len(sources),'files')
