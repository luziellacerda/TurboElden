"""Stage the exact R76 source composition plus the explicit R77 overlay."""
from pathlib import Path
import hashlib, importlib.util, json, shutil
ROOT=Path(__file__).resolve().parent.parent
WORK=Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008')
PREVIOUS=ROOT.parent/'station-pump-wakeup-r76-20261008'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def sources():
    spec=importlib.util.spec_from_file_location('r76',PREVIOUS/'recipes/build_candidate.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m.verified_sources()[2]
def stage():
    src=sources(); previous=json.loads((PREVIOUS/'evidence/java-dex-build.json').read_text('utf8'))
    assert {n:sha(p) for n,p in src.items()}==previous['sourceHashes']
    for n,p in src.items():
        dst=WORK/'java'/n;dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():shutil.copyfile(p,dst)
    for p in (ROOT/'java').rglob('*.java'):
        dst=WORK/'java'/p.relative_to(ROOT/'java');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    (WORK/'r76-source-manifest.json').write_text(json.dumps(previous['sourceHashes'],indent=2)+'\n','utf8')
    print('R76 composition verified; R77 Java staged')
if __name__=='__main__':stage()
