"""Restore exact Java compiler inputs into a new E: build directory; no deletion."""
from pathlib import Path
import hashlib,json,shutil,sys
SNAPSHOT=Path(__file__).resolve().parents[1]
VERSIONS=SNAPSHOT.parent
receipt=json.loads((SNAPSHOT/'evidence/java-build.json').read_text('utf8'))
target=Path(sys.argv[1]).resolve()
if target.drive.upper()!='E:' or target.exists():
    raise SystemExit('Use a new, nonexistent build directory on E:.')
resolved={}
for raw,expected in receipt['files'].items():
    rel=Path(raw.replace('\\','/'))
    if rel.is_absolute() or '..' in rel.parts:raise SystemExit('Unsafe manifest path')
    choices=[SNAPSHOT/rel,VERSIONS/'station-online-integrated-r62-20261006'/rel,VERSIONS/'station-layout-r57-20261006'/rel,VERSIONS/'station-current-r55-20261006'/rel]
    source=next((p for p in choices if p.is_file()),None)
    if source is None or hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise SystemExit('Missing/mismatched source: '+str(rel))
    resolved[rel]=source
assert len(resolved)==161
target.mkdir(parents=True)
for rel,source in resolved.items():
    destination=target/rel;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
for name in ('build','evidence','tests','temp'):(target/name).mkdir()
for name in ('build_java.py','package_r63.py'):shutil.copyfile(SNAPSHOT/'recipes'/name,target/name)
for name in ('assets','runtime','tests'):shutil.copytree(SNAPSHOT/name,target/name,dirs_exist_ok=True)
shutil.copyfile(SNAPSHOT/'recipes/run_local_tests.py',target/'run_local_tests.py')
print('Restored all161 exact Java inputs and recipes to '+str(target))
