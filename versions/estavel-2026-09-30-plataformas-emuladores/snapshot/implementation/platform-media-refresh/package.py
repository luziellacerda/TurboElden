from pathlib import Path
import hashlib,json,os,subprocess,zipfile,datetime,copy,struct,shutil,re,xml.etree.ElementTree as ET
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-media-refresh';V=R/'psvita'
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk';OUT=BASE
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def file_sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
sha=lambda b:hashlib.sha256(b).hexdigest()
base_sha=file_sha(BASE);assert base_sha=='2f93a8ad604f6060d3b26adde507698dacf8ea999e0b507700417599410b58c7'
assert (V/'vita-module-built.apk').is_file()
shutil.copy2(Path(__file__),R/'package.py')
media=json.loads((R/'media-manifest.json').read_text(encoding='utf-8'))
replacements={'lib/arm64-v8a/libturbo_carousel.so':(P/'libturbo_carousel.so').read_bytes(),
    'classes8.dex':(V/'classes8.dex').read_bytes(),'classes24.dex':(V/'bridge-dex/classes.dex').read_bytes(),
    'assets/turboretro/catalog.json':(V/'catalog-with-psvita.json').read_bytes(),
    'assets/platform-media-refresh/media-manifest.json':(R/'media-manifest.json').read_bytes(),
    'assets/platform-media-refresh/power-policy.json':(R/'power-policy.json').read_bytes(),
    'assets/platform-media-refresh/psvita-catalog-change.json':(V/'catalog-change.json').read_bytes()}
source_names=['native_carousel.cpp','native_system_video720.h','native_space3d.h','native_menu_power.h','native_psvita.h','system_video720_assets.h']
for name in source_names:replacements['assets/platform-media-refresh/source/'+name]=(P/name).read_bytes()
for name in ['prepare.py','apply.py','package.py']:replacements['assets/platform-media-refresh/source/'+name]=(R/name).read_bytes()
for item in media['videos']:
    path=R/'media'/Path(item['asset']).name;assert file_sha(path)==item['sha256'];replacements[item['asset']]=path.read_bytes()
with zipfile.ZipFile(BASE) as base,zipfile.ZipFile(V/'vita-module-built.apk') as built:
    existing=set(base.namelist())
    for name in built.namelist():
        if name in ['AndroidManifest.xml','resources.arsc','classes.dex','classes23.dex'] or name.startswith('lib/arm64-v8a/'):
            assert name not in existing or name in ['AndroidManifest.xml','resources.arsc','classes.dex'], 'Unexpected library collision: '+name
            replacements[name]=built.read(name)
        elif name.startswith(('res/','assets/')) and not name.startswith('assets/dexopt/'):
            if name not in existing:replacements[name]=built.read(name)
    # Keep archived source copies internally consistent wherever these same active filenames were embedded.
    for name in existing:
        leaf=Path(name).name
        if name.startswith('assets/') and leaf in source_names:replacements[name]=(P/leaf).read_bytes()
    backup=R/'before/replaced-entries.zip'
    with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as saved:
        for name in replacements:
            if name in existing and name!='lib/arm64-v8a/libturbo_carousel.so':saved.writestr(name,base.read(name))
def dex_classes(d):
    count,off=struct.unpack_from('<II',d,56);strings=[]
    for i in range(count):
        pos=struct.unpack_from('<I',d,off+4*i)[0]
        while d[pos]&128:pos+=1
        pos+=1;strings.append(d[pos:d.index(0,pos)].decode('utf-8',errors='replace'))
    count,off=struct.unpack_from('<II',d,64);types=[strings[struct.unpack_from('<I',d,off+4*i)[0]] for i in range(count)]
    count,off=struct.unpack_from('<II',d,96)
    return {types[struct.unpack_from('<I',d,off+32*i)[0]] for i in range(count)}
with zipfile.ZipFile(BASE) as z:
    assert dex_classes(z.read('classes.dex'))==dex_classes(replacements['classes.dex'])
    assert dex_classes(z.read('classes8.dex'))==dex_classes(replacements['classes8.dex'])
    all_classes=set()
    for name in z.namelist():
        if re.fullmatch(r'classes\d*\.dex',name):all_classes.update(dex_classes(z.read(name)))
    for name in ['classes23.dex','classes24.dex']:
        added=dex_classes(replacements[name]);assert not all_classes.intersection(added),(name,sorted(all_classes.intersection(added))[:10]);all_classes.update(added)
old_public=ET.parse(V/'frontend-decoded/res/values/public.xml').getroot();new_public=ET.parse(V/'merged/res/values/public.xml').getroot()
ids={(e.get('type'),e.get('name')):e.get('id') for e in new_public if e.tag=='public'}
assert all(ids[(e.get('type'),e.get('name'))]==e.get('id') for e in old_public if e.tag=='public')
aligned=R/'refresh-aligned.apk'
def write_aligned(out,entry,data):
    info=copy.copy(entry) if isinstance(entry,zipfile.ZipInfo) else zipfile.ZipInfo(entry)
    if not isinstance(entry,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if entry.endswith(('.so','.dex','.arsc','.mp4')) else zipfile.ZIP_DEFLATED
    if info.filename.startswith('assets/') and info.filename.endswith('.mp4'):info.compress_type=zipfile.ZIP_STORED
    info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
        alignment=16384 if info.filename.endswith('.so') else 4
        offset=out.fp.tell()+30+len(info.filename.encode('utf-8'))
        if offset%alignment:
            pad=(-(offset+4))%alignment;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
    out.writestr(info,data)
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(aligned,'w',allowZip64=True) as out:
    seen=set()
    for info in z.infolist():
        name=info.filename
        if name.startswith('META-INF/'):continue
        write_aligned(out,info,replacements[name] if name in replacements else z.read(name));seen.add(name)
    for name,data in replacements.items():
        if name not in seen:write_aligned(out,name,data)
print('APK assembled; signing and preserving unchanged engines.',flush=True)
def run(*args):subprocess.run(list(map(str,args)),check=True)
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(J,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',OUT,aligned)
run(J,'-jar',BT/'lib/apksigner.jar','verify',OUT)
aligned.unlink()
previous=json.loads((R/'before/entry-hashes.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(OUT) as z:
    for name,digest in previous.items():
        if name not in replacements:assert sha(z.read(name))==digest,'Unexpected change: '+name
    for name,data in replacements.items():assert sha(z.read(name))==sha(data),name
    videos=[n for n in z.namelist() if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4')]
    assert len(videos)==33 and all(z.getinfo(n).compress_type==zipfile.ZIP_STORED for n in videos)
    changed=[n for n in previous if n in replacements and sha(z.read(n))!=previous[n]]
record={'apk':str(OUT),'sha256':file_sha(OUT),'bytes':OUT.stat().st_size,'base_sha256':base_sha,
    'native_module_sha256':file_sha(P/'libturbo_carousel.so'),'built_at':datetime.datetime.now().astimezone().isoformat(),
    'removed_platforms':['atari7800','supergrafx'],'updated_videos':['xbox360','Pc Engine','Pc Engine cd'],
    'added_platform':'Psvita','vita_games':23,'vita_covers':22,'vita_engine':'Vita3K 0.2.1 official continuous APK, isolated :psvita process',
    'vita_archive_support':'libarchive 3.8.9 RAR/RAR5 conversion to installable ZIP; owner firmware setup required',
    'menu_power_policy':json.loads((R/'power-policy.json').read_text()),'all_videos_stored':True,
    'video_count':len(videos),'fps':30,'playback_speed':1.0,'focus_only':True,'loop':True,
    'existing_engines_identical':True,'existing_resource_ids_preserved':True,'new_dex_class_collisions':False,
    'changed':changed,'installed':False,'runtime_verified':False,'promoted_to_stable':False}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['changed','menu_power_policy']},ensure_ascii=False,indent=2))
