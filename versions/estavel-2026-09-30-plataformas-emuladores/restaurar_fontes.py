from pathlib import Path
import gzip,hashlib,json,sys
base=Path(__file__).resolve().parent
dest=Path(sys.argv[1]).resolve()
assert not dest.exists(), 'Escolha uma pasta nova para preservar fontes existentes'
m=json.loads((base/'MANIFESTO-ESTAVEL.json').read_text(encoding='utf-8'))
for f in m['files']:
    raw=(base/f['stored_path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==f['stored_sha256']
    data=gzip.decompress(raw) if f['encoding']=='gzip' else raw
    assert hashlib.sha256(data).hexdigest()==f['sha256']
    target=dest/f['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
print('Fontes restaurados:',len(m['files']),dest)
