from pathlib import Path
import hashlib,json,os,subprocess,zipfile,copy,datetime,shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'flycast-integration'
BASE=P/'TurboramaStation-Dolphin-2609-7.apk';OUT=P/'TurboramaStation-Flycast-v2.7-44-retorno-rapido.apk'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TMP']=os.environ['TEMP']=str(R/'tmp')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())=='5bce795e714ce943d887dd127bfb28c501b8fc55b2f748520348c705ed30dc03'
removed=set() # Previous Flycast was downloaded, not embedded in the base APK.
replacements={}
with zipfile.ZipFile(R/'merged-template.apk') as z:
    for n in z.namelist():
        if n in ['AndroidManifest.xml','resources.arsc','classes.dex','classes13.dex'] or n.startswith(('res/','assets/flycast-integration/')):
            replacements[n]=z.read(n)
for f in (R/'merged/lib/arm64-v8a').glob('*.so'):
    if f.name!='libdolphin_libretro_android.so':replacements['lib/arm64-v8a/'+f.name]=f.read_bytes()
replacements['lib/arm64-v8a/libturbo_carousel.so']=(P/'libturbo_carousel.so').read_bytes()
replacements['classes14.dex']=(R/'bridge-dex/classes.dex').read_bytes()
assert 'lib/arm64-v8a/libflycast.so' in replacements
assert not (set(replacements)&removed)
# Include the small integration source alongside upstream licensing/provenance.
for f in [R/'prepare.py',R/'integrate.py',R/'native_patch.py',R/'package.py',P/'native_flycast.h',R/'native_bridge.c',R/'navigation-abi.json']:
    replacements['assets/flycast-integration/source/'+f.name]=f.read_bytes()
for f in (R/'java').rglob('*.java'):
    replacements['assets/flycast-integration/source/'+f.relative_to(R/'java').as_posix()]=f.read_bytes()
for f in (R/'bios-assets').iterdir():
    if f.is_file():replacements['assets/flycast-bios/'+f.name]=f.read_bytes()
replacements['assets/flycast-integration/bios-manifest.json']=(R/'bios-manifest.json').read_bytes()
unsigned=R/'flycast-unsigned.apk';aligned=R/'flycast-aligned.apk'
def run(*a):subprocess.run(list(map(str,a)),check=True)
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
    seen=set()
    for info in z.infolist():
        n=info.filename
        if n.startswith('META-INF/') or n in removed:continue
        out.writestr(info,replacements.get(n,z.read(n)));seen.add(n)
    for n,b in replacements.items():
        if n not in seen:out.writestr(n,b,compress_type=zipfile.ZIP_STORED if n.endswith(('.so','.dex','.arsc')) else zipfile.ZIP_DEFLATED)
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink()
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
run(BT/'zipalign.exe','-c','-P','16','4',OUT)
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
    an={n for n in a.namelist() if not n.startswith('META-INF/')};bn={n for n in b.namelist() if not n.startswith('META-INF/')}
    assert an-bn==removed,an-bn
    changed=sorted(n for n in an&bn if sha(a.read(n))!=sha(b.read(n)))
    assert all(n in replacements for n in changed)
    assert all(a.read(f'classes{i}.dex')==b.read(f'classes{i}.dex') for i in range(2,13))
    preserved_engines=[n for n in an if n.startswith('lib/') and n not in removed and not n.endswith('libturbo_carousel.so')]
    assert all(a.read(n)==b.read(n) for n in preserved_engines)
    assert not any('dolphin_libretro' in n.lower() or n=='assets/packs/Dolphin.zip' for n in bn)
    # No donor dependency may accidentally overwrite an existing library.
    assert set(changed).intersection(preserved_engines)==set()
    native_main_identical=a.read('lib/arm64-v8a/libmain.so')==b.read('lib/arm64-v8a/libmain.so')
aligned.unlink()
report=dict(apk=str(OUT),sha256=sha(OUT.read_bytes()),bytes=OUT.stat().st_size,time=datetime.datetime.now().isoformat(),
    base=str(BASE),base_sha256=sha(BASE.read_bytes()),official_flycast='v2.7-44-ge36e9df2d',commit='e36e9df2dcc1487acdb1dc7725766f1f5ba029b5',
    original_official_apk_sha256=sha((R/'flycast-official-current.apk').read_bytes()),source_rebuilt=False,
    official_engine_embedded=True,standalone_flycast_dependency=False,old_flycast_route_disabled=True,old_dolphin_still_removed=True,bundled_bios_count=9,incomplete_disc_guard=True,native_return_button=True,turborama_native_menu_background=True,menu_touch_transition_queue=True,
    changed=changed,added=sorted(bn-an),preserved_other_native_libraries=len(preserved_engines),
    original_frontend_libmain_identical=native_main_identical,classes2_through12_identical=True,
    installed=False,runtime_verified=False,gameplay_verified=False,promoted_to_stable=False)
(R/'build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
for f in ['native_carousel.cpp','native_flycast.h','libturbo_carousel.so']:
    shutil.copy2(P/f,R/f)
print(json.dumps({k:v for k,v in report.items() if k not in ['added','changed']},ensure_ascii=False,indent=2))
