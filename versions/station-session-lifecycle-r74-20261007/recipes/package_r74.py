"""Package four reviewed R74 replacements over exact R73, then verify every entry.

Requires existing authorized signing environment. Contains no key, password or
default password. Does not install, change server state or mark gameplay stable.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,importlib.util,json,os,shutil,struct,subprocess,sys,zipfile
from prepare_engine_registry import (BASE,BASE_SHA,OLD_RUNTIME,NATIVE_MANIFEST,FLUSH_SHA,
    DEFAULT_WORK,DEFAULT_DELTA,sha,require,native_identity,engine_delta)

sys.dont_write_bytecode=True
CLIENT_SHA='1a04582a02804ecbe4b075dd487118a171b0b0f305dbb8884015bbede09b25d7'
ROOMS_BASE='d6ffa9060289e1afa1e39234c3bacedc8ead197fddcdc171b954bd580240be9e'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
MANIFEST_PATCH_SHA='529553d4c84887bf4b96e555a0c25e20412e9cecbff503414e8b071e0985879d'
MANIFEST_READER_SHA='86be68b02bf053bbb2ca0ee6c7c057f557b8e34190c2c1b1ac54e40ba17de3a0'
DEX_GATE_SHA='3dee834410b422761a197a37669730a010dcf1e5dd194b0b74a7a58308cb6fa6'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module
def zsha(z,name):
    with z.open(name) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(name):return name.startswith('META-INF/') and name.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def read(path):return json.loads(Path(path).read_text('utf8'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',required=True,help='Reviewed R74 version directory containing Java recipes and manifest')
    p.add_argument('--workspace',default=DEFAULT_WORK);p.add_argument('--native-work',default=r'E:\R74fixed')
    p.add_argument('--native-delta',default=DEFAULT_DELTA);p.add_argument('--base',default=str(BASE))
    p.add_argument('--lifecycle-tests',default=r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\session-tests-final\test-receipt.json')
    p.add_argument('--output',default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R74-20261007.apk')
    a=p.parse_args();snapshot=Path(a.snapshot).resolve();w=Path(a.workspace).resolve();delta=Path(a.native_delta).resolve()
    base=Path(a.base).resolve();output=Path(a.output).resolve();native_dir=Path(a.native_work).resolve()
    require(snapshot.name=='station-session-lifecycle-r74-20261007','Exact R74 source snapshot required')
    require(w.drive.upper()=='E:' and output.drive.upper()=='G:','Use E: for all build/temp files and G: for final artifact')
    require(w.is_dir() and output.parent.is_dir() and not output.exists(),'Existing workspace/output directory; never overwrite APK')
    require(sha(base)==BASE_SHA,'Exact R73 APK required')
    before_recipe=sha(__file__);registry_recipe=sha(Path(__file__).with_name('prepare_engine_registry.py'))
    build_module=load('r74_package_java_build',snapshot/'recipes/build_candidate.py')
    _,_,sources,overlay_path=build_module.verified_sources()
    source_hashes={name:sha(path) for name,path in sorted(sources.items())}
    build_path=w/'evidence/build.json';tests_path=w/'evidence/local-tests.json'
    build=read(build_path);tests=read(tests_path);lifecycle_path=Path(a.lifecycle_tests);lifecycle=read(lifecycle_path)
    require(build['compiled'] and build['baseSHA256']==BASE_SHA,'Java baseline mismatch')
    require(build['sourceHashes']==tests['sourceHashes']==source_hashes,'Tested and compiled Java sources differ')
    require(build['sourceCount']==tests['productionSourceCount']==lifecycle['productionSourceCount']==len(sources)==201,'Java source composition differs')
    require(build['overlayManifestSHA256']==sha(overlay_path),'Java overlay changed after build')
    require(build['buildRecipeSHA256']==sha(snapshot/'recipes/build_candidate.py'),'Java build recipe changed')
    require(tests['success'] and tests['countedChecks']==1206 and tests['buildReceiptSHA256']==sha(build_path),'Regression suite incomplete or stale')
    require(tests['recipeSHA256']==sha(snapshot/'recipes/run_tests.py'),'Java regression recipe changed')
    require(lifecycle['localChecks']==101 and lifecycle['sourceGuardCount']==len(lifecycle['sourceGuards'])==42,'New lifecycle fixture incomplete')
    require(len(lifecycle['sha256'])==6 and all(source_hashes.get(n)==h for n,h in lifecycle['sha256'].items()),'Lifecycle fixture targets different sources')
    dex=w/'java/build/rooms-dex/classes.dex'
    require(sha(dex)==build['roomsDexSHA256']==tests['roomsDexSHA256']!=ROOMS_BASE,'DEX35 identity mismatch')
    require(build['clientDexSHA256']==tests['clientDexSHA256']==CLIENT_SHA and build['clientDexUnchanged'],'DEX28 must remain R71/R73')
    require(build['changedDexSlots']==['classes35.dex'],'Only DEX35 may change')

    runtime,native,native_receipt=native_identity(native_dir,delta)
    native_tests={name:read(delta/'tests'/name) for name in ('lifecycle-probe-result.json','recovery-input-result.json','pacing-result.json')}
    native_manifest=read(delta/'native-delta-manifest.json')
    require(native_tests['lifecycle-probe-result.json']['deltaManifestSHA256']==sha(delta/'native-delta-manifest.json'),'Native lifecycle probe is stale')
    for result_name,recipe_name in [('lifecycle-probe-result.json','lifecycle_probe.py'),('recovery-input-result.json','recovery_input_probe.py'),('pacing-result.json','pacing_probe.py')]:
        require(native_tests[result_name]['testRecipeSHA256']==sha(delta/'tests'/recipe_name),'Native test recipe changed: '+recipe_name)
    input_result=native_tests['recovery-input-result.json']['results']
    require(input_result[0]['exitCode']==2 and input_result[1]['exitCode']==0,'Native input regression did not pass')
    require(input_result[1]['sourceSHA256']==native['sourceDelta']['runloop.c']['afterSHA256'],'Input probe uses wrong runloop')
    pacing=native_tests['pacing-result.json'];pr=pacing['results'];pf=pacing['fragments']
    require(pr[0]['native']['stickyFlagsAfterCatchup']==200 and pr[1]['native']['stickyFlagsAfterCatchup']==0,'Native pacing regression did not pass')
    require(pr[1]['frontendSHA256']==native['sourceDelta']['network/netplay/netplay_frontend.c']['afterSHA256'],'Pacing probe uses wrong frontend')
    require(pf[0]['recoveryPollSHA256']==pf[1]['recoveryPollSHA256']==FLUSH_SHA,'R73 nonblocking flush changed')
    require(native_manifest['preservedRecoveryPollSHA256']==FLUSH_SHA,'Native delta flush mismatch')
    registry_path=w/'evidence/engine-registry.json';registry=read(registry_path)
    engine_file=Path(registry['manifest']);manifest_file=w/'AndroidManifest.xml'
    require(Path(registry['runtime']).resolve()==runtime.resolve(),'Engine runtime path differs')
    require(registry['runtimeSHA256']==native['runtimeSHA256'] and registry['nativeBuildReceiptSHA256']==sha(native_receipt),'Registry/native receipt mismatch')
    require(registry['nativeOverlayManifestSHA256']==NATIVE_MANIFEST and sha(engine_file)==registry['manifestSHA256'],'Engine registry stale')
    require(registry['removeExistingIds']==[] and registry['existingEntriesToPreserve']==8 and len(registry['registryAdditions'])==2,'Server update must append two, preserve eight')
    engine=read(engine_file);manifest_receipt=read(w/'evidence/manifest.json')
    patch_path=snapshot/'recipes/patch_session_manifest.py'
    reader_path=snapshot.parent/'station-online-layout-r71-20261007/recipes/patch_navigation_manifest.py'
    require(sha(patch_path)==MANIFEST_PATCH_SHA and sha(reader_path)==MANIFEST_READER_SHA,'Manifest tooling changed')
    patcher=load('r74_package_manifest_patch',patch_path);reader=load('r74_package_manifest_reader',reader_path)
    dex_gate_path=snapshot.parent/'station-collection-videos-r67-20261007/recipes/dex_gates.py'
    require(sha(dex_gate_path)==DEX_GATE_SHA,'DEX gate changed');gates=load('r74_package_dex_gate',dex_gate_path)
    replacements={'classes35.dex':dex,'lib/arm64-v8a/libstation_retroarch.so':runtime,
                  'assets/station-online/engines.json':engine_file,'AndroidManifest.xml':manifest_file}
    replacement_hashes={name:sha(path) for name,path in replacements.items()}
    with zipfile.ZipFile(base) as z:
        require(zsha(z,'classes35.dex')==ROOMS_BASE and zsha(z,'classes28.dex')==CLIENT_SHA,'R73 modules differ')
        expected_engine,additions=engine_delta(json.loads(z.read('assets/station-online/engines.json')),native['runtimeSHA256'])
        require(engine==expected_engine and registry['registryAdditions']==additions,'Unexpected engine changes')
        expected_manifest,expected_receipt=patcher.patch(z.read('AndroidManifest.xml'),reader)
        require(manifest_file.read_bytes()==expected_manifest and manifest_receipt==expected_receipt,'Manifest must only add exact private Service')
        class_gate=gates.verify_modules(z,{'classes35.dex':dex.read_bytes()})
        require('Lorg/emulationstation/frontend/netplay/StationSessionService;' in gates.definitions(dex.read_bytes()),'Private Service class missing')
        require(len(z.namelist())==len(set(z.namelist())),'Duplicate base entries')

    # Signing credentials remain in existing environment; no literal password fallback.
    tools=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
    jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
    temp=w/'temp';temp.mkdir(exist_ok=True);env=dict(os.environ,TEMP=str(temp),TMP=str(temp))
    for key in ('STATION_KEYSTORE','STATION_KEY_ALIAS','STATION_KS_PASS','STATION_KEY_PASS'):
        require(bool(env.get(key)),'Missing existing signing environment: '+key)
    def run(command,label):
        r=subprocess.run(list(map(str,command)),env=env,capture_output=True)
        (w/'evidence'/('package-'+label+'-private.log')).write_bytes(r.stdout+r.stderr)
        require(r.returncode==0,'Operation failed; inspect private package log: '+label)
        return (r.stdout+r.stderr).decode('utf8','replace')
    exported=subprocess.run([str(jdk/'keytool.exe'),'-exportcert','-keystore',env['STATION_KEYSTORE'],'-alias',env['STATION_KEY_ALIAS'],'-storepass:env','STATION_KS_PASS'],env=env,capture_output=True)
    require(exported.returncode==0,'Could not read existing signing certificate')
    require(hashlib.sha256(exported.stdout).hexdigest()==CERT,'Key must match installed app certificate')
    require(CERT in run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',base],'base-cert'),'Base signer differs')
    unsigned=w/'unsigned-r74.apk';signed=w/'signed-r74.apk'
    require(not unsigned.exists() and not signed.exists(),'Do not overwrite prior packaging attempts')
    require(shutil.disk_usage(w).free>2*base.stat().st_size+128*1024**2 and shutil.disk_usage(output.parent).free>base.stat().st_size+64*1024**2,'Insufficient package space')
    with zipfile.ZipFile(base) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
        for info in old.infolist():
            if signature(info.filename):continue
            item=copy.copy(info);item.extra=b''
            if item.filename in replacements:item.file_size=replacements[item.filename].stat().st_size
            if item.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if item.filename.endswith('.so') else 4
                offset=new.fp.tell()+30+len(item.filename.encode('utf8'))
                if offset%alignment:
                    pad=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
            with new.open(item,'w') as dst:
                with (replacements[item.filename].open('rb') if item.filename in replacements else old.open(info)) as src:
                    shutil.copyfileobj(src,dst,1024*1024)
    run([tools/'zipalign.exe','-c','-P','16','4',unsigned],'unsigned-alignment')
    run([jdk/'java.exe','-Djava.io.tmpdir='+str(temp),'-jar',tools/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false',
         '--ks',env['STATION_KEYSTORE'],'--ks-key-alias',env['STATION_KEY_ALIAS'],'--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',signed,unsigned],'sign')
    require(CERT in run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',signed],'output-cert'),'Signed certificate differs')
    run([tools/'zipalign.exe','-c','-P','16','4',signed],'signed-alignment')
    changed=[];preserved=0
    with zipfile.ZipFile(base) as old,zipfile.ZipFile(signed) as new:
        names={n for n in old.namelist() if not signature(n)}
        require(names=={n for n in new.namelist() if not signature(n)},'Entries added/removed')
        require(len(new.namelist())==len(set(new.namelist())),'Duplicate output entries')
        for name in sorted(names):
            prior=zsha(old,name);actual=zsha(new,name);expected=replacement_hashes.get(name,prior)
            require(actual==expected and old.getinfo(name).compress_type==new.getinfo(name).compress_type,'Entry mismatch: '+name)
            if actual!=prior:changed.append(name)
            else:preserved+=1
        require(changed==sorted(replacements),'Exactly four replacements required')
        require(gates.verify_modules(new,{})==class_gate,'Final DEX class gate differs')
        require(zsha(new,'classes28.dex')==CLIENT_SHA,'Client DEX changed')
        videos=sum(1 for name in names if name.lower().endswith('.mp4'))
    require({n:sha(p) for n,p in replacements.items()}==replacement_hashes,'Inputs changed during package')
    require({n:sha(p) for n,p in sources.items()}==source_hashes,'Java sources changed during package')
    require(sha(__file__)==before_recipe and sha(Path(__file__).with_name('prepare_engine_registry.py'))==registry_recipe,'Packaging recipes changed')
    signed_sha=sha(signed)
    # Exclusive creation prevents overwriting a concurrently published artifact.
    with output.open('xb') as dst,signed.open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
    require(sha(output)==signed_sha,'Final G: copy differs')
    receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),apk=str(output),sha256=signed_sha,bytes=output.stat().st_size,
      baseSHA256=BASE_SHA,changed=changed,added=[],preservedEntries=preserved,allPackageEntriesVerified=True,certificateSHA256=CERT,
      alignment16KiB=True,classGate=class_gate,clientDexUnchanged=True,clientDexSHA256=CLIENT_SHA,roomsDexSHA256=sha(dex),
      runtimeSHA256=native['runtimeSHA256'],engineManifestSHA256=sha(engine_file),androidManifestSHA256=sha(manifest_file),
      privateService=patcher.SERVICE,manifestExistingNodesUnchanged=True,coreLibrariesUnchanged=True,allOtherDexAndNativeLibrariesPreserved=True,
      allMediaPreserved=True,totalVideos=videos,nativeBuildReceiptSHA256=sha(native_receipt),nativeOverlayManifestSHA256=NATIVE_MANIFEST,
      nativeTests={n:sha(delta/'tests'/n) for n in native_tests},serverRegistryAdditionsRequired=True,serverAdditions=additions,
      serverExistingEntriesToPreserve=8,serverActivationVerified=False,buildReceiptSHA256=sha(build_path),testReceiptSHA256=sha(tests_path),
      lifecycleTestReceiptSHA256=sha(lifecycle_path),packageRecipeSHA256=before_recipe,registryRecipeSHA256=registry_recipe,
      installed=False,androidGameplay=False,stable=False)
    (w/'evidence/package.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    for path in (unsigned,signed):
        require(path.resolve().parent==w and path.name in ('unsigned-r74.apk','signed-r74.apk'),'Unexpected cleanup target')
        path.unlink()
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
