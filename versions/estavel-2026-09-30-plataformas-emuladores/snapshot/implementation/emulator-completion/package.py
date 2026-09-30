from pathlib import Path
import copy, datetime, hashlib, json, os, shutil, struct, subprocess, zipfile

P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'emulator-completion'
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk'
EXPECTED='776a550a0901cd90a31ceaf21ad649b1b70d4f20f51f3e2ef35b51f3f8c45d84'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def run(*args):subprocess.run(list(map(str,args)),check=True)
assert file_sha(BASE)==EXPECTED
assert file_sha(Path(json.loads((R/'before/base.json').read_text())['frozen']))==EXPECTED
with zipfile.ZipFile(R/'wiiu-counter-built.apk') as z:
    changed={'classes19.dex':z.read('classes.dex'),
             'lib/arm64-v8a/libturbo_wiiu_counter_jni.so':z.read('lib/arm64-v8a/libturbo_wiiu_counter_jni.so')}
changed['classes20.dex']=(R/'wiiu-archive-final/dex/classes.dex').read_bytes()
changed['lib/arm64-v8a/libturbo_wiiu_archive.so']=(R/'wiiu-archive-final/libturbo_wiiu_archive.so').read_bytes()
changed['classes24.dex']=(R/'vita-dex-final/classes.dex').read_bytes()
sources={
 'VitaEntryActivity.java':R/'VitaEntryActivity.java',
 'WiiUEntryActivity.java':R/'wiiu-archive-final/java/org/emulationstation/frontend/WiiUEntryActivity.java',
 'WiiUArchive.java':R/'wiiu-archive-final/java/org/emulationstation/frontend/WiiUArchive.java',
 'wiiu_archive_bridge.c':R/'wiiu-archive-final/wiiu_archive_bridge.c',
 'wiiu_counter_jni.c':Path(__file__).parent/'wiiu-finish-proposed/wiiu_counter_jni.c',
}
for name,path in sources.items():changed['assets/emulator-completion/source/'+name]=path.read_bytes()
changed['assets/emulator-completion/libarchive-LICENSE']=(R/'wiiu-archive-final/libarchive-COPYING').read_bytes()
firmware=json.loads((R/'firmware/manifest.json').read_text())
provenance={'base_sha256':EXPECTED,'wiiu':'Register four original DataStore native methods against relocated class; bounded private RAR preparation.',
            'psvita':'Correct required firmware mask6 (main2+fonts4); install hash-verified owner-staged official files; defer activity launches while paused.',
            'firmware_bundled':False,'firmware_sources':[{k:v for k,v in record.items() if k!='file'} for record in firmware],
            'firmware_state_source':'https://github.com/Vita3K/Vita3K/blob/e6ac4272e3e7e35e2ffd307adfacffa9e3392686/android/app/src/main/java/org/vita3k/emulator/data/FirmwareInstallState.kt',
            'other_emulator_engines_changed':False,'runtime_verified':False}
changed['assets/emulator-completion/provenance.json']=(json.dumps(provenance,indent=2)+'\n').encode()
with zipfile.ZipFile(BASE) as z:
    for name in z.namelist():
        if name.startswith('assets/') and Path(name).name in sources:changed[name]=sources[Path(name).name].read_bytes()
    with zipfile.ZipFile(R/'before/replaced-entries.zip','w',compression=zipfile.ZIP_DEFLATED) as backup:
        for name in changed:
            if name in z.namelist():backup.writestr(name,z.read(name))

aligned=R/'completed-aligned.apk'
assert not aligned.exists()
def put(out,entry,data):
    info=copy.copy(entry) if isinstance(entry,zipfile.ZipInfo) else zipfile.ZipInfo(entry)
    if not isinstance(entry,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if entry.endswith(('.so','.dex','.arsc','.mp4')) else zipfile.ZIP_DEFLATED
    info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
        alignment=16384 if info.filename.endswith('.so') else 4
        offset=out.fp.tell()+30+len(info.filename.encode())
        if offset%alignment:
            pad=(-(offset+4))%alignment;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
    out.writestr(info,data)
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(aligned,'w') as out:
    seen=set()
    for info in z.infolist():
        if info.filename.startswith('META-INF/'):continue
        put(out,info,changed.get(info.filename,z.read(info.filename)));seen.add(info.filename)
    for name,data in changed.items():
        if name not in seen:put(out,name,data)
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(J,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],
    '--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',BASE,aligned)
run(J,'-jar',BT/'lib/apksigner.jar','verify',BASE)
previous=json.loads((R/'before/entry-hashes.json').read_text())
with zipfile.ZipFile(BASE) as z:
    for name,digest in previous.items():
        if name not in changed:assert sha(z.read(name))==digest,name
    for name,data in changed.items():assert z.read(name)==data,name
    videos=[n for n in z.namelist() if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4')]
    assert len(videos)==33 and all(z.getinfo(n).compress_type==zipfile.ZIP_STORED for n in videos)
aligned.unlink()
record={'built_at':datetime.datetime.now().astimezone().isoformat(),'apk':str(BASE),'sha256':file_sha(BASE),
        'bytes':BASE.stat().st_size,'base_sha256':EXPECTED,'changed_entries':{n:sha(d) for n,d in changed.items()},
        'all_other_entries_identical':True,'existing_engine_libraries_unchanged':True,
        'frontend_native_and_video_dex_unchanged':True,'firmware_bundled':False,
        'installed':False,'runtime_verified':False,'stable_promoted':False,'git_published':False}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for filename in ['VitaEntryActivity.java']:
    shutil.copy2(sources[filename],P/'platform-media-refresh/psvita'/filename)
for filename in ['WiiUEntryActivity.java','WiiUArchive.java']:
    target=P/'wiiu-integration/java/org/emulationstation/frontend'/filename
    if target.exists():shutil.copy2(target,R/'before'/filename)
    shutil.copy2(sources[filename],target)
for filename,path in sources.items():shutil.copy2(path,R/('source-'+filename))
shutil.copy2(Path(__file__),R/'package.py')
profile_path=P/'stable-design/active-profile.json';profile=json.loads(profile_path.read_text(encoding='utf-8'))
profile.update({'pending_apk':str(BASE),'pending_apk_sha256':record['sha256'],'pending_build':str(R/'build-result.json'),
                'pending_update':'WiiU counter JNI and RAR preparation; Vita firmware setup/mask correction',
                'installation_pending':True,'installed_apk_local_file_replaced_by_pending':True,
                'latest_built_apk':str(BASE),'latest_built_apk_sha256':record['sha256'],'latest_build_record':str(R/'build-result.json')})
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['apk','sha256','bytes','all_other_entries_identical','installed']},ensure_ascii=False))
