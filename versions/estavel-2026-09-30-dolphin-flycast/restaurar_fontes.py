"""Materialize the frozen source snapshot in a NEW directory on E:; never install or delete data."""
from pathlib import Path
import argparse,gzip,hashlib,json
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--destino',type=Path,required=True)
a=ap.parse_args()
dest=a.destino.resolve()
if dest.drive.upper()!='E:':ap.error('Use uma pasta nova na unidade E:, conforme a regra de compilacao do projeto.')
if dest.exists():ap.error('O destino ja existe. Escolha uma pasta nova para preservar o trabalho atual.')
m=json.loads((R/'MANIFESTO-ESTAVEL.json').read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
for row in m['files']:
 rel=Path(row['path']);stored=(R/row['stored_path']).resolve()
 if rel.is_absolute() or '..' in rel.parts or not stored.is_relative_to(R):raise RuntimeError('Caminho invalido no manifesto')
 b=stored.read_bytes()
 if sha(b)!=row['stored_sha256']:raise RuntimeError('Arquivo Git divergente: '+row['stored_path'])
 data=gzip.decompress(b) if row['encoding']=='gzip' else b
 if len(data)!=row['bytes'] or sha(data)!=row['sha256']:raise RuntimeError('Fonte divergente: '+row['path'])
 target=dest/rel
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_bytes(data)
(dest/'IDENTIDADE-ESTAVEL.json').write_text(json.dumps({k:v for k,v in m.items() if k!='files'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Fontes restaurados em '+str(dest/'implementation'))
print('Nenhum APK foi instalado. Base privada, assinatura e ferramentas nao fazem parte do Git.')
