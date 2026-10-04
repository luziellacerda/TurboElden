from pathlib import Path
import json,shutil,hashlib
ROOT=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
HERE=Path(__file__).resolve().parent
REPO=HERE/'work/TurboElden-git' if (HERE/'work/TurboElden-git/.git').exists() else next(p for p in HERE.parents if (p/'.git').exists())
OUT=REPO/'versions/station-visual-covers-netplay-20261003'
EXCLUDED={'systems.h','space_assets.h','space3d_assets.h','space3d_brand.h','game_infos.h','console_assets.h'}
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(src,dst,allowed=None):
    for p in src.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        if allowed and p.suffix not in allowed:continue
        copy(p,dst/p.relative_to(src))
OUT.mkdir(parents=True,exist_ok=True)
tree(ROOT/'station/src',OUT/'station/src')
tree(ROOT/'station/tests',OUT/'station/tests')
tree(ROOT/'station/tools',OUT/'station/tools')
for p in (ROOT/'station').glob('*.py'):copy(p,OUT/'station'/p.name)
for name in ['HANDOFF-CAPAS-20261003.md','platform-evidence.json','HANDOFF-RECONSTRUCAO-TURBOSTATIONS.md','HANDOFF-SERVIDOR-CONEXAO-E-INSTALACAO.md']:
    if (ROOT/'station'/name).is_file():copy(ROOT/'station'/name,OUT/'station'/name)
for name in ['cover-delivery-result.json','test-results.json','frontend-manifest.json','module-manifest.json']:
    copy(ROOT/'station/build'/name,OUT/'evidence'/('station-'+name))
for p in (ROOT/'native').iterdir():
    if p.suffix in ('.h','.cpp','.glsl') and p.name not in EXCLUDED and '.before-' not in p.name:copy(p,OUT/'native'/p.name)
tree(ROOT/'netplay/src',OUT/'netplay/src')
tree(ROOT/'netplay/tests',OUT/'netplay/tests')
for p in (ROOT/'netplay').iterdir():
    if p.is_file() and p.suffix in ('.py','.h','.xml','.json','.md','.java'):copy(p,OUT/'netplay'/p.name)
for p in (ROOT/'netplay/build').glob('*.json'):copy(p,OUT/'evidence'/('netplay-'+p.name))
tree(ROOT/'evidence',OUT/'evidence')
for name in ['prepare_visual_metadata.py','audit_missing_synopses.py','prepare_console_assets.py','test_visual_metadata.py','test_station_info_layout.cpp','test_catalog_identity.cpp','native-base-hashes.json','archived-apks.json','archived-visual-r1.json','archived-controls-apk.json','build-result.json','BUILD-NOTICE.json','test_shader_angle.py']:
    if (ROOT/name).is_file():copy(ROOT/name,OUT/name)
for name in ['prepare_visual_delivery.py','finalize_netplay_manifest.py','build_visual_delivery.py','export_visual_delivery.py','verify_visual_manifest.py']:
    copy(Path(__file__).resolve().parent/name,OUT/'build'/name)
tree(ROOT/'assets/turbo-console',OUT/'assets/turbo-console')
tree(ROOT/'assets/station-metadata',OUT/'assets/station-metadata')
tree(ROOT/'server-inputs',OUT/'server-inputs',{'.tsv'})
private=[]
for name in sorted(EXCLUDED):
    p=ROOT/'native'/name
    private.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),
       'reason':'Generated image/legacy metadata header; retained locally. console_assets.h regenerated from included PNGs.'})
(OUT/'PRIVATE-BUILD-INPUTS.json').write_text(json.dumps(private,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Exported source, evidence and generated console photos to',OUT)
