from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile,re,difflib
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'saturn-modern'
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk'
EXPECTED='f7596a8015093d5b5fdabe3ae9e54bba3c78b0260d0034ec3e390c6df9578538'
FROZEN=Path(r'F:\Turborama-build-archive\TurboramaStation-before-Saturn12046-f7596a80.apk')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
def run(*args):subprocess.run(list(map(str,args)),check=True)
assert digest(BASE)==EXPECTED
if not FROZEN.exists():shutil.copy2(BASE,FROZEN)
assert digest(FROZEN)==EXPECTED
source=R/'source/yabasanshiro-1.20.46/yabause'
with zipfile.ZipFile(R/'frontend-built.apk') as z:
    changed={n:z.read(n) for n in ['AndroidManifest.xml','classes.dex']}
changed.update({'classes25.dex':(R/'dex/classes.dex').read_bytes(),
 'lib/arm64-v8a/libturbo_saturn.so':(R/'libturbo_saturn.so').read_bytes(),
 'lib/arm64-v8a/libturbo_carousel.so':(P/'libturbo_carousel.so').read_bytes()})
removed={'lib/arm64-v8a/libyabasanshiro_libretro_android.so','assets/scoped-search-n64/source/native_saturn_probe.h'}
sources={'native_carousel.cpp':P/'native_carousel.cpp','native_saturn.h':P/'native_saturn.h'}
for f in (R/'java').rglob('*.java'):sources[f.name]=f
sources['ra_disabled.c']=R/'ra_disabled.c'
for name,path in sources.items():changed['assets/saturn-modern/source/'+name]=path.read_bytes()
patch=[]
for f in (R/'upstream-build-files').rglob('*'):
    if f.is_file():
        rel=f.relative_to(R/'upstream-build-files').as_posix();after=source/rel
        patch.extend(difflib.unified_diff(f.read_text().splitlines(True),after.read_text().splitlines(True),'a/'+rel,'b/'+rel))
(R/'upstream-integration.patch').write_text(''.join(patch),encoding='utf-8')
changed['assets/saturn-modern/source/upstream-integration.patch']=(R/'upstream-integration.patch').read_bytes()
changed['assets/saturn-modern/COPYING.txt']=(source/'COPYING.txt').read_bytes()
changed['assets/saturn-modern/oboe-LICENSE']=(next((R/'deps/oboe').iterdir())/'LICENSE').read_bytes()
changed['assets/saturn-modern/libpng-LICENSE']=(next((R/'deps/libpng').iterdir())/'LICENSE').read_bytes()
chdr=next((R/'deps/libchdr').iterdir());license_file=next(f for f in chdr.iterdir() if f.name.lower().startswith('license'))
changed['assets/saturn-modern/libchdr-LICENSE']=license_file.read_bytes()
provenance={'version':'Yaba Sanshiro 1.20.46 Android','official_source':'https://www.yabasanshiro.com/download',
 'source_archive':'https://d1t36rsydvwkyk.cloudfront.net/yabasanshiro-src-1.20.46.tar.gz',
 'source_sha256':'3eb2d610d178b8fd503bb13d7e50b8f8710711a26a1efb52780010a559a1b912',
 'rebuilt_from_source':True,'graphics':'OpenGL ES, upstream Android Surface/EGL renderer',
 'cpu':'ARM64 devMiyax dynamic recompiler and SH2 interpreter','sound':'Oboe',
 'vulkan_included':False,'retroachievements_included':False,'process':':saturn',
 'settings_only_loads_engine':False,'old_libretro_saturn_removed':True,'diagnostic_probe_removed':True,
 'dependencies':json.loads((R/'deps/downloads.json').read_text()),'runtime_verified':False}
changed['assets/saturn-modern/provenance.json']=json.dumps(provenance,indent=2).encode()
with zipfile.ZipFile(FROZEN) as z:
    previous={n:sha(z.read(n)) for n in z.namelist() if not n.startswith('META-INF/')}
    for n in z.namelist():
        if n.startswith('assets/') and Path(n).name in sources:changed[n]=sources[Path(n).name].read_bytes()
(R/'before/base.json').write_text(json.dumps({'file':str(FROZEN),'sha256':EXPECTED,'entry_hashes':previous},indent=2))
def put(out,entry,data):
    info=copy.copy(entry) if isinstance(entry,zipfile.ZipInfo) else zipfile.ZipInfo(entry)
    if not isinstance(entry,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if entry.endswith(('.so','.dex','.mp4','.arsc')) else zipfile.ZIP_DEFLATED
    info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
        alignment=16384 if info.filename.endswith('.so') else 4
        offset=out.fp.tell()+30+len(info.filename.encode())
        if offset%alignment:pad=(-(offset+4))%alignment;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
    out.writestr(info,data)
aligned=R/'saturn-aligned.apk';assert not aligned.exists()
# The verified full recovery is on F:. Replacing only the working APK frees
# room for both signing files on E:, where all compilation/temp files remain.
assert BASE.resolve()==(P/'TurboramaStation-Plataformas-Organizadas.apk').resolve()
assert shutil.disk_usage(R).free + BASE.stat().st_size > 2 * BASE.stat().st_size + 64*1024*1024, 'Free more build space on E before packaging'
BASE.unlink()
try:
    with zipfile.ZipFile(FROZEN) as z,zipfile.ZipFile(aligned,'w') as out:
        seen=set()
        for info in z.infolist():
            n=info.filename
            if n.startswith('META-INF/') or n in removed:continue
            put(out,info,changed.get(n,z.read(n)));seen.add(n)
        for n,data in changed.items():
            if n not in seen:put(out,n,data)
    run(BT/'zipalign.exe','-c','-P','16','4',aligned)
    run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',BASE,aligned)
    run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',BASE)
except:
    # A failed signer may leave a partial output. Restore only from the verified recovery.
    if BASE.exists():BASE.unlink()
    if aligned.exists():aligned.unlink()
    shutil.copy2(FROZEN,BASE)
    assert digest(BASE)==EXPECTED
    raise
with zipfile.ZipFile(BASE) as z:
    for n,h in previous.items():
        if n not in changed and n not in removed:assert sha(z.read(n))==h,n
    for n,data in changed.items():assert z.read(n)==data,n
    for n in removed:assert n not in z.namelist(),n
    assert all(z.getinfo(n).compress_type==zipfile.ZIP_STORED for n in z.namelist() if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4'))
aligned.unlink()
record={'built_at':datetime.datetime.now().astimezone().isoformat(),'apk':str(BASE),'sha256':digest(BASE),'bytes':BASE.stat().st_size,
 'base_sha256':EXPECTED,'backup':str(FROZEN),'changed_entries':{n:sha(b) for n,b in changed.items()},'removed_entries':sorted(removed),
 'all_other_payload_entries_identical':True,'signature_verified':True,'alignment_16k_verified':True,
 'installed':False,'runtime_verified':False,'git_published':False,'stable_promoted':False}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
f=P/'stable-design/active-profile.json';profile=json.loads(f.read_text());profile.update({'pending_apk':str(BASE),'pending_apk_sha256':record['sha256'],'pending_build':str(R/'build-result.json'),'pending_update':'Yaba Sanshiro 1.20.46 Android embedded Saturn; GLES/Oboe; isolated lifecycle','installation_pending':True,'installed_apk_local_file_replaced_by_pending':True,'latest_built_apk':str(BASE),'latest_built_apk_sha256':record['sha256'],'latest_build_record':str(R/'build-result.json')});f.write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['apk','sha256','bytes','installed','all_other_payload_entries_identical']}))
