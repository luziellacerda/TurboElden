from pathlib import Path
import argparse,shutil,json,hashlib
p=argparse.ArgumentParser();p.add_argument('output');a=p.parse_args();out=Path(a.output).resolve();snapshot=Path(__file__).resolve().parent.parent
if out.exists():raise SystemExit('Use a new output directory; no files overwritten')
out.mkdir(parents=True)
for name in ('netplay-src','dependency-src','server','tests','evidence'):shutil.copytree(snapshot/name,out/name)
for path in (snapshot/'recipes').glob('*.py'):shutil.copyfile(path,out/path.name)
for name in ('SOURCE-MANIFEST.json','EXTERNAL-BUILD-INPUTS.json'):shutil.copyfile(snapshot/name,out/name)
for group in ('temp','build','device-evidence'):(out/group).mkdir(exist_ok=True)
manifest=json.loads((out/'SOURCE-MANIFEST.json').read_text('utf8'))
for name,expected in manifest.items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==expected,name
print(out)
