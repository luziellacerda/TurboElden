from pathlib import Path
import subprocess,sys,shutil,json,hashlib
V=Path(__file__).resolve().parents[1];target=Path(sys.argv[1])
assert target.drive.upper()=='E:' and not target.exists()
for relative,expected in json.loads((V/'source-manifest.json').read_text('utf8')).items():
    source=V/relative
    if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=expected:
        raise SystemExit('Missing/mismatched R64 source: '+relative)
subprocess.run([sys.executable,str(V.parent/'station-auto-access-r63-20261006/recipes/restore_sources.py'),str(target)],check=True)
for folder in ('netplay-src','assets','sprite-source','tests'):
    shutil.copytree(V/folder,target/folder,dirs_exist_ok=True)
for name in ('build_java.py','run_local_tests.py','package_r64.py'):shutil.copy2(V/'recipes'/name,target/name)
(target/'recipes').mkdir(exist_ok=True)
shutil.copy2(V/'recipes/BuildControlSprites.java',target/'recipes/BuildControlSprites.java')
for relative,expected in json.loads((V/'JAVA-BUILD-RECEIPT.json').read_text('utf8'))['files'].items():
    source=target/relative
    if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=expected:
        raise SystemExit('Missing/mismatched R64 compiler input: '+relative)
print('R64 sources restored. Use build_java.py, run_local_tests.py, package_r64.py; do not run package_r63.py.')
