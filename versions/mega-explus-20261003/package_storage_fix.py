from pathlib import Path
import hashlib, json, os, re, struct, subprocess, zipfile
R=Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003')
HERE=Path(__file__).resolve().parent
BASE=R/'TurboStations-SNES-Mega-EXPlus-20261003.apk'
OUT=R/'TurboStations-SNES-Mega-CONTROLES-CORRIGIDOS-20261003.apk'
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R)
def run(*a):subprocess.run(list(map(str,a)),check=True)
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def signature(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.RSA','.DSA','.EC','.SF'))
def class_defs(d):
    def u(o):return struct.unpack_from('<I',d,o)[0]
    strings=[]
    for i in range(u(56)):
        o=u(u(60)+4*i)
        while d[o]&128:o+=1
        o+=1;strings.append(d[o:d.index(0,o)].decode('utf-8',errors='replace'))
    types=[strings[u(u(68)+4*i)] for i in range(u(64))]
    return [types[u(u(100)+32*i)] for i in range(u(96))]
assert sha(BASE)=='e87a352bc61ce6b2f120d4657451471313a1e4e7671e37c572d9904fcc1ef7be'
replacements={};removed=set()
S=Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003')
with zipfile.ZipFile(BASE) as z:
    names=set(z.namelist());class_map={}
    for n in names:
        if n.endswith('.dex'):
            for cls in class_defs(z.read(n)):class_map[cls]=n
modules=[('Lcom/imagine/BaseActivity;',S/'snes-storage-module.apk'),('Lcom/mdimagn/BaseActivity;',R/'mega-storage-module.apk')]
for cls,archive in modules:
    with zipfile.ZipFile(archive) as z:replacements[class_map[cls]]=z.read('classes.dex')
for cls,root in [('Snes',S),('Mega',R)]:
    descriptor='Lorg/emulationstation/frontend/'+cls+'Bootstrap;'
    replacements[class_map[descriptor]]=(root/'bridge-dex/classes.dex').read_bytes()
    prefix='snes' if cls=='Snes' else 'mega'
    source=HERE.parent/(prefix+'-explus-20261003')/'java/org/emulationstation/frontend'/(cls+'Bootstrap.java')
    replacements['assets/'+prefix+'-explus/source/'+cls+'Bootstrap.java']=source.read_bytes()
assert len([n for n in replacements if n.endswith('.dex')])==4
replacements['assets/mega-explus/source/fix_native_storage.py']=(HERE/'fix_native_storage.py').read_bytes()
# Whole-app DEX definition gate (not just a string search).
definitions={}
with zipfile.ZipFile(BASE) as z:
    for n in sorted(names|set(replacements)):
        if n.endswith('.dex'):
            data=replacements[n] if n in replacements else z.read(n)
            for cls in class_defs(data):
                assert cls not in definitions,('duplicate class',cls,n,definitions.get(cls))
                definitions[cls]=n
assert 'Lcom/mdimagn/BaseActivity;' in definitions
assert 'Lcom/imagine/BaseActivity;' in definitions
assert 'Lorg/emulationstation/frontend/MegaBootstrap;' in definitions
assert 'Lorg/emulationstation/frontend/SnesBootstrap;' in definitions

unsigned=R/'unsigned.apk';aligned=R/'aligned.apk'
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(unsigned,'w',allowZip64=True) as b:
    seen=set()
    for info in a.infolist():
        n=info.filename
        if signature(n) or n in removed:continue
        b.writestr(info,replacements[n] if n in replacements else a.read(n));seen.add(n)
    for n,data in replacements.items():
        if n not in seen:b.writestr(n,data,compress_type=zipfile.ZIP_STORED if n.endswith(('.so','.dex')) else zipfile.ZIP_DEFLATED)
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink() # exact disposable build output; never a workspace tree
run(JDK/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true',
    '--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey',
    '--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned)
run(JDK/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',OUT)
run(BT/'zipalign.exe','-c','-P','16','4',OUT)
changed=[];preserved=[]
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
    old={n for n in a.namelist() if not signature(n)}
    new={n for n in b.namelist() if not signature(n)}
    assert old-new==removed
    assert new-old==set(replacements)-old
    for n in sorted(old&new):
        if digest(a.read(n))!=digest(b.read(n)):changed.append(n);assert n in replacements,n
        else:preserved.append(n)
    assert set(changed)==set(replacements)&old
    assert all(a.read(n)==b.read(n) for n in old if n.startswith('lib/'))
    assert a.read('AndroidManifest.xml')==b.read('AndroidManifest.xml')
aligned.unlink()
report=dict(apk=str(OUT),sha256=sha(OUT),bytes=OUT.stat().st_size,base_sha256=sha(BASE),
    source_commit='1c12fac5ce49badaadff2e2f210dcc30b89f4943',version='MD.emu 1.5.85 official prerelease; SNES EX+ retained',
    changed=changed,added=sorted(new-old),removed=sorted(removed),preserved_entries=len(preserved),
    dex_definitions=len(definitions),duplicate_definitions=0,integrated_native_sha256=sha(R/'libmdemu_station.so'),native_adaptations=json.loads((R/'native-relocations.json').read_text()),
    preserved_snes_complete=True,native_activity_directory_overrides=True,shared_configuration_imported=False,station_login_catalog_download_dex_preserved=True,
    all_other_engines_preserved=True,resources_and_design_assets_preserved=True,
    installed=False,runtime_verified=False,promoted_to_stable=False)
(R/'storage-build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('added',)},ensure_ascii=False,indent=2))
