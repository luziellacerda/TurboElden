"""Guarded candidate package over the installed R68. No installation or data reset."""
from pathlib import Path
import argparse, copy, datetime, hashlib, importlib.util, json, os, shutil, struct, subprocess, sys, zipfile
sys.dont_write_bytecode = True
from source_composition import verified_composition
from generate_engines import generate

BASE = '72ce7c2cbb3d7cf14ad122b0b98e42a41563114bbbc5c925caedbdee49ff66c3'
JAVA_BASE = 'd746cc02b602162b19509cd44ad7cf751e320de3b52199e7d48e86e9e897228f'
CERT = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
SNAPSHOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('station_dex_gate',SNAPSHOT.parent/'station-collection-videos-r67-20261007/recipes/dex_gates.py')
gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
p = argparse.ArgumentParser()
for name in ('base-apk','java-build','native-build','workspace','output','tools','jdk'): p.add_argument('--'+name,required=True)
a = p.parse_args()
base, java_build, native_build, work, output, tools, jdk = [Path(getattr(a,n)).resolve() for n in
    ('base_apk','java_build','native_build','workspace','output','tools','jdk')]
if os.name != 'nt' or work.drive.upper() != 'E:' or output.drive.upper() != 'G:':
    raise SystemExit('Production packaging uses E: workspace and G: candidate output')
if work.exists() or output.exists(): raise SystemExit('Use new paths; preserve previous packages')
def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def zsha(archive,name):
    with archive.open(name) as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def signature(name): return name.startswith('META-INF/') and name.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
if sha(base) != BASE: raise SystemExit('Exact installed R68 required; reconcile any successor first')
j = json.loads((java_build/'evidence/build.json').read_text())
n = json.loads((native_build/'result.json').read_text())
if not j['dexBuilt'] or j['apiCheckOnly'] or j['baseAPK'] != JAVA_BASE or j['sourceCount'] != 195:
    raise SystemExit('Both new DEX modules must be compiled from the recovery composition')
resolved = verified_composition()
assert j['sourceHashes'] == {name:sha(path) for name,path in resolved.items()}
for name,expected in j['sourceHashes'].items(): assert sha(java_build/name) == expected, name
for module in ('client','rooms'): assert sha(java_build/(module+'.jar')) == j[module+'JarSHA256']
runtime = native_build/'libstation_retroarch.so'
assert n['compiled'] and n['recoveryProtocol']=='station-stream.v2' and sha(runtime)==n['runtimeSHA256']
assert n['minimumLoadAlignment']>=16384 and n['architecture']=='AArch64' and n['minAPI']==26
assert n['recoveryJNIExportsPresent'] and n['recoveryInputs']==json.loads((SNAPSHOT/'native/RECOVERY-SOURCE-MANIFEST.json').read_text())['files']
manifest, additions = generate(sha(runtime))
work.mkdir(parents=True);(work/'evidence').mkdir();(work/'temp').mkdir()
engine_file = work/'engines.json'; engine_file.write_text(json.dumps(manifest,indent=2)+'\n')
(work/'server-engine-registry-additions.json').write_text(json.dumps(additions,indent=2)+'\n')
replacements={'lib/arm64-v8a/libstation_retroarch.so':runtime,'assets/station-online/engines.json':engine_file}
for slot,module in [('classes28.dex','client'),('classes35.dex','rooms')]:
    dex=java_build/(module+'-dex')/'classes.dex'; assert sha(dex)==j[module+'DexSHA256'];replacements[slot]=dex
env=dict(os.environ,TMP=str(work/'temp'),TEMP=str(work/'temp'))
for name in ('STATION_KEYSTORE','STATION_KEY_ALIAS','STATION_KS_PASS','STATION_KEY_PASS'):
    if not env.get(name): raise SystemExit('Original signing credentials required privately: '+name)
def run(command,label):
    result=subprocess.run(list(map(str,command)),capture_output=True,text=True,encoding='utf8',errors='replace',env=env)
    (work/'evidence'/(label+'.log')).write_text(result.stdout+result.stderr,'utf8')
    if result.returncode: raise RuntimeError(label+' failed; inspect the private local log')
    return result.stdout+result.stderr
java=jdk/'bin/java.exe';signer=tools/'lib/apksigner.jar';aligner=tools/'zipalign.exe'
assert CERT in run([java,'-jar',signer,'verify','--print-certs',base],'base-signature')
unsigned=work/'unsigned.apk'
with zipfile.ZipFile(base) as old:
    assert len(old.namelist())==len(set(old.namelist())) and set(replacements).issubset(old.namelist())
    assert zsha(old,'lib/arm64-v8a/libstation_retroarch.so')=='899e35279cf046242a7ae31f502078080bd6a94404770fe99e1e2e90be58a1ef'
    expected_engines=json.loads((SNAPSHOT.parent/'station-online-controls-r64-20261007/assets/station-online/engines.json').read_text())
    assert json.loads(old.read('assets/station-online/engines.json'))==expected_engines
    for engine in expected_engines['engines']:
        assert zsha(old,'lib/arm64-v8a/'+engine['library'])==engine['coreSha256']
    dex_gate=gate.verify_modules(old,{name:path.read_bytes() for name,path in replacements.items() if name.endswith('.dex')})
    required=base.stat().st_size+sum(path.stat().st_size for path in replacements.values())+32*1024**2
    assert shutil.disk_usage(work).free>required and shutil.disk_usage(output.parent).free>required
    with zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
        for info in old.infolist():
            if signature(info.filename): continue
            item=copy.copy(info);name=info.filename;item.extra=b''
            if name in replacements: item.file_size=replacements[name].stat().st_size;item.compress_type=zipfile.ZIP_STORED
            if item.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if name.endswith('.so') else 4
                offset=new.fp.tell()+30+len(name.encode('utf8'))
                if offset%alignment:
                    pad=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
            with new.open(item,'w') as destination:
                with (replacements[name].open('rb') if name in replacements else old.open(info)) as source:
                    shutil.copyfileobj(source,destination,1024*1024)
run([aligner,'-c','-P','16','4',unsigned],'unsigned-alignment')
run([java,'-Djava.io.tmpdir='+str(work/'temp'),'-jar',signer,'sign','--alignment-preserved','true',
     '--v4-signing-enabled','false','--ks',env['STATION_KEYSTORE'],'--ks-key-alias',env['STATION_KEY_ALIAS'],
     '--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',output,unsigned],'sign')
assert CERT in run([java,'-jar',signer,'verify','--print-certs',output],'signature')
run([aligner,'-c','-P','16','4',output],'alignment')
changed=[];preserved=0
with zipfile.ZipFile(base) as old,zipfile.ZipFile(output) as new:
    assert len(new.namelist())==len(set(new.namelist()))
    names={name for name in old.namelist() if not signature(name)}
    assert names=={name for name in new.namelist() if not signature(name)}
    for name in sorted(names):
        before=zsha(old,name);expected=sha(replacements[name]) if name in replacements else before
        assert zsha(new,name)==expected,name
        if before!=expected: changed.append(name)
        else: preserved+=1
    assert set(changed).issubset(replacements) and 'classes35.dex' in changed
    assert zsha(new,'classes30.dex')=='1dcfa1e69686a326e22c54b9adc7c6013644e69d14642664e2ab7b5e2eee4ff4'
    assert zsha(new,'lib/arm64-v8a/libturbo_carousel.so')=='60b944cb44a61b0c45af67ec084bb37e4ac56b21e7847c8ca7baf45c5dfb4a3d'
    videos=[name for name in names if name.startswith('assets/turbo-system-videos/') and name.endswith('.mp4')]
    assert len(videos)==55 and all(new.getinfo(name).compress_type==zipfile.ZIP_STORED for name in videos)
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),apk=str(output),apkSHA256=sha(output),
    bytes=output.stat().st_size,baseAPK=BASE,certificateSHA256=CERT,changed=changed,preservedEntries=preserved,
    allPackageEntriesVerified=True,alignment16KiB=True,classGate=dex_gate,recoveryProtocol='station-stream.v2',
    runtimeSHA256=sha(runtime),newEngineIds=[e['id'] for e in additions],originalDataNotTouched=True,
    serverRecoveryActivationRequired=True,installed=False,twoDeviceGameplayVerified=False)
(work/'evidence/package.json').write_text(json.dumps(result,indent=2)+'\n')
unsigned.unlink()
print(json.dumps(result,indent=2))
