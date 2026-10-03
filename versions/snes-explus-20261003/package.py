from pathlib import Path
import hashlib, json, os, re, struct, subprocess, zipfile
R=Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003')
HERE=Path(__file__).resolve().parent
BASE=Path(r'E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk')
OUT=R/'TurboStations-SNES-EXPlus-20261003.apk'
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
assert sha(BASE)=='3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17'
replacements={}
for archive,entry in [('host-module.apk','classes.dex'),('manifest-module.apk','AndroidManifest.xml')]:
    with zipfile.ZipFile(R/archive) as z:replacements[entry]=z.read(entry)
with zipfile.ZipFile(BASE) as z:
    names=set(z.namelist())
    next_dex=max(int(re.match(r'classes(\d*)\.dex$',n)[1] or 1) for n in names if re.match(r'classes\d*\.dex$',n))+1
    removed={n for n in names if n=='lib/arm64-v8a/libsnes9x_libretro_android.so'}
    assert len(removed)==1,removed
    stable_turbo=z.read('lib/arm64-v8a/libturbo_carousel.so')
    assert digest(stable_turbo)==sha(R/'native/recovered-stable.so')
with zipfile.ZipFile(R/'snes-module.apk') as z:replacements[f'classes{next_dex}.dex']=z.read('classes.dex')
replacements[f'classes{next_dex+1}.dex']=(R/'bridge-dex/classes.dex').read_bytes()
with zipfile.ZipFile(R/'Snes9xEXPlus-1c12fac5.apk') as z:
    replacements['lib/arm64-v8a/libsnes9x_explus.so']=z.read('lib/arm64-v8a/libmain.so')
    for n in z.namelist():
        if n.startswith('assets/') and not n.endswith('/'):
            assert n not in names,n
            replacements[n]=z.read(n)
replacements['lib/arm64-v8a/libturbo_carousel.so']=(R/'native/libturbo_carousel.so').read_bytes()
src=R/'source/emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943'
for path in [src/'COPYING.GPL',src/'Snes9x/COPYING']:
    replacements['assets/snes-explus/licenses/'+path.name]=path.read_bytes()
replacements['assets/snes-explus/upstream-provenance.json']=(R/'upstream-provenance.json').read_bytes()
for f in (HERE/'java').rglob('*.java'):
    replacements['assets/snes-explus/source/'+f.name]=f.read_bytes()
replacements['assets/snes-explus/source/native_snes.h']=(R/'native/native_snes.h').read_bytes()

# Whole-app DEX definition gate (not just a string search).
definitions={}
with zipfile.ZipFile(BASE) as z:
    for n in sorted(names|set(replacements)):
        if n.endswith('.dex'):
            data=replacements[n] if n in replacements else z.read(n)
            for cls in class_defs(data):
                assert cls not in definitions,('duplicate class',cls,n,definitions.get(cls))
                definitions[cls]=n
assert 'Lcom/imagine/BaseActivity;' in definitions
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
    assert set(changed)=={'AndroidManifest.xml','classes.dex','lib/arm64-v8a/libturbo_carousel.so'}
    assert b.read('lib/arm64-v8a/libsnes9x_explus.so')==replacements['lib/arm64-v8a/libsnes9x_explus.so']
aligned.unlink()
report=dict(apk=str(OUT),sha256=sha(OUT),bytes=OUT.stat().st_size,base_sha256=sha(BASE),
    source_commit='1c12fac5ce49badaadff2e2f210dcc30b89f4943',version='Snes9x EX+ 1.5.85 official prerelease',
    changed=changed,added=sorted(new-old),removed=sorted(removed),preserved_entries=len(preserved),
    dex_definitions=len(definitions),duplicate_definitions=0,upstream_native_sha256=digest(replacements['lib/arm64-v8a/libsnes9x_explus.so']),
    restored_native_baseline_exact=True,station_login_catalog_download_dex_preserved=True,
    all_other_engines_preserved=True,resources_and_design_assets_preserved=True,
    installed=False,runtime_verified=False,promoted_to_stable=False)
(R/'build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('added',)},ensure_ascii=False,indent=2))
