"""Scoped R175 catalogue capacity repair on exact signed R174; private outputs only."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, zipfile
from manifest_delta import patch as patch_manifest

REPO=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BASE_SHA='6ab94ff0999ef2f0d5febe0d46fd27e715692c1aea8c216a2ce87d9cb8b51c4d'
BASE_SIZE=2714238050
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
DEX_PINS={'classes28.dex':'dcd7349cc874a6652f6b6530f68ab595d8d6ea92bcab59e76f06177d834bb161'}
COMPILED={'StationApi','StationCatalog','StationCatalogPoll','StationCoverQueue','StationCatalogPlayerEvidence','StationCatalogPlayerEvidenceLoader'}
HOOKED={'StationFrontend','StationHttp'}
OWNERS=COMPILED|HOOKED
NATIVE=['StationPsxEntry.cpp','StationPsxOwner.cpp','StationPsxProtocol.cpp','StationPsxSha256.cpp']
WRAPPERS={'psx':'libstation_psx_online.so','n64':'libstation_mupen64plus_runtime.so','dolphin':'libstation_dolphin_runtime.so'}
PREFIX='lib/arm64-v8a/'
ENGINE='assets/station-online/engines.json'
ALLOWED=set(DEX_PINS)|{'AndroidManifest.xml',ENGINE,PREFIX+'libstation_frontend.so'}|{PREFIX+n for n in WRAPPERS.values()}

def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def write(path,v):Path(path).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def run(command,log):
    r=subprocess.run(list(map(str,command)),capture_output=True,text=True,timeout=1800)
    Path(log).write_text(r.stdout+r.stderr)
    need(r.returncode==0,'Build command failed: '+Path(log).name)
    return r.stdout+r.stderr
def entry_sha(z,name):
    with z.open(name) as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def belongs(t,names):return t.split('/')[-1].rstrip(';').split('$')[0] in names
def projections(path):return {p.relative_to(path).as_posix():sha(p) for p in path.rglob('*.smali')}
def descriptor(path):return 'L'+str(path).removesuffix('.smali')+';'
def fresh(path):Path(path).mkdir(parents=True,exist_ok=False);return Path(path)

def freeze(revision,task):
    need(re.fullmatch('[0-9a-f]{40}',revision) is not None,'Frozen full source commit')
    need(subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()==revision,'Build from frozen HEAD')
    parent=json.loads((task/'inputs/parent-compile-receipt.json').read_text())
    need(parent['passed'] and parent['sourceCommit']=='bf155ec2bfaea7dbc31da036e2bf8d346edf7469','Exact R174 provenance')
    for name,pin in parent['sourceSha256'].items():
        need(digest(subprocess.check_output(['git','-C',str(REPO),'show',revision+':'+name]))==pin,'R174 source changed: '+name)
    sources=list(HERE.glob('*.py'))+list(HERE.glob('*.java'))+[HERE/'COMPILER-INPUTS.json']
    sources+=list((HERE.parent/'java').rglob('*.java'))+list((HERE.parent/'tests').glob('*.java'))
    sources+=list((HERE.parent/'native').iterdir())
    sources+=list((HERE.parent/'signing').glob('*.py'))+[HERE.parent/'SCOPE.json',HERE.parent/'SOURCE-PROVENANCE.json']
    sources+=list((REPO/'integration/psx-online/native').glob('*.cpp'))+list((REPO/'integration/psx-online/native').glob('*.hpp'))+[REPO/'integration/psx-online/native/PsxPinnedOptions.h']
    sources+=[REPO/'integration/psx-updater-r170/recipe/manifest_delta.py']
    pins={}
    for p in sorted(set(sources)):
        name=p.relative_to(REPO).as_posix();raw=p.read_bytes()
        need(raw==subprocess.check_output(['git','-C',str(REPO),'show',revision+':'+name]),'Unfrozen source: '+name);pins[name]=digest(raw)
    for name,pin in json.loads((HERE/'COMPILER-INPUTS.json').read_text()).items():
        need(sha(task/'inputs'/name)==pin,'Real pinned classpath changed: '+name)
    return pins

def patch_effective(donor):
    """Change two exact root methods; retain every other effective instruction and nested type."""
    root='org/emulationstation/frontend/station/'
    front=donor/(root+'StationFrontend.smali');raw=front.read_text()
    start='    iget-object v5, v3, Lorg/emulationstation/frontend/station/StationCoordinator$Library;->catalog:Lorg/emulationstation/frontend/station/StationCatalog;'
    end='    invoke-static/range {v6 .. v11}, Lorg/emulationstation/frontend/station/StationCatalogPoll;->changed(JLjava/lang/String;JLjava/lang/String;)Z'
    need(raw.count(start)==1 and raw.count(end)==1,'Exact active poll register lifetimes')
    begin=raw.index(start);stop=raw.index(end,begin)+len(end);old=raw[begin:stop]
    need(old.count('iget-')==6 and raw[stop:].startswith('\n\n    move-result v3'),'Exact revision/name comparison block')
    new='    invoke-static {v3, v4}, Lorg/emulationstation/frontend/station/StationCatalogPoll;->changed(Lorg/emulationstation/frontend/station/StationCoordinator$Library;Lorg/emulationstation/frontend/station/StationCoordinator$Library;)Z'
    front.write_text(raw[:begin]+new+raw[stop:])
    http=donor/(root+'StationHttp.smali');text=http.read_text()
    anchor='    const-string p0, "/v1/station/catalog?metadata=1"'
    need(text.count(anchor)==1 and 'maximumItems=' not in text,'Exact effective HTTP allowlist')
    addition='    const-string p0, "/v1/station/catalog?metadata=1&maximumItems=20000"\n\n    invoke-virtual {p1, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z\n\n    move-result p0\n\n    if-nez p0, :cond_a\n\n'
    # cond_a is the existing allow-return in this method, with the GET gate already passed.
    method=text[text.index('.method static allowed('):];method=method[:method.index('.end method')]
    need(anchor in method and ':cond_a\n    :goto_1\n    return v2' in method,'Existing GET success branch')
    http.write_text(text.replace(anchor,addition+anchor))
    return {'frontendOriginalBlockSha256':digest(old.encode()),'frontendReplacementBlockSha256':digest(new.encode()),
            'frontendLiveLibraries':'v3 previous, v4 fresh; existing move-result and generation/lifecycle gates retained',
            'httpPolicy':'One exact GET route appended; direct artifact/TLS/request proof/update and all nested transports retained'}

def compile_dex(task,sdk,revision):
    base=task/'inputs/TurboStations-Premium-R174.apk'
    need(base.stat().st_size==BASE_SIZE and sha(base)==BASE_SHA,'Exact signed R174 donor')
    pins=freeze(revision,task);out=fresh(task/'compile');inputs=task/'inputs'
    classes=fresh(out/'classes');android=sdk/'platforms/android-36/android.jar'
    classpath=[inputs/n for n in ['parent-program-classpath.jar','production-classpath-only.jar','rooms.jar','client.jar','sdl-abi-only.jar']]
    root=HERE.parent/'java/org/emulationstation/frontend/station';sources=[root/(n+'.java') for n in sorted(COMPILED)]
    run(['javac','--release','8','-encoding','UTF-8','-Xlint:-options','-proc:none','-sourcepath','','-cp',os.pathsep.join(map(str,[android,*classpath])),'-d',classes,*sources],out/'javac.log')
    program=sorted(classes.rglob('*.class'))
    need(all(belongs(p.relative_to(classes).as_posix().removesuffix('.class')+';',COMPILED) for p in program),'Foreign JVM class')
    overlay=fresh(out/'overlay');d8=sdk/'build-tools/36.0.0/lib/d8.jar'
    command=['java','-cp',d8,'com.android.tools.r8.D8','--release','--min-api','26','--lib',android,'--output',overlay]
    for dep in classpath:command+=['--classpath',dep]
    log=run([*command,*program],out/'d8.log');need(not re.search(r'(?im)^\s*(warning|error)\b',log),'D8 diagnostic requires review')
    tools=fresh(out/'tools');apktool=inputs/'apktool.jar'
    run(['javac','--release','17','-encoding','UTF-8','-cp',apktool,'-d',tools,*sorted(HERE.glob('*.java'))],out/'helpers.log')
    cp=os.pathsep.join(map(str,[tools,apktool]));oz=out/'overlay.zip'
    with zipfile.ZipFile(oz,'x') as z:z.write(overlay/'classes.dex','classes.dex')
    decoded=out/'overlay-smali'
    run(['java','-cp',cp,'DecodeDolphinPartition',oz,'classes.dex',sha(overlay/'classes.dex'),decoded],out/'decode-overlay.log')
    overlay_files=projections(decoded);need(all(belongs(descriptor(n),COMPILED) for n in overlay_files),'Foreign D8 type')
    scopes={}
    for partition,pin in DEX_PINS.items():
        donor=out/(partition+'-smali');run(['java','-cp',cp,'DecodeDolphinPartition',base,partition,pin,donor],out/(partition+'-decode.log'))
        original=projections(donor)
        before={n for n in original if belongs(descriptor(n),COMPILED)};final=set(overlay_files)
        need(all(any(n.endswith('/'+owner+'.smali') for n in before) for owner in COMPILED),'Donor owner missing')
        for n in before:(donor/n).unlink()
        for n in final:
            target=donor/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((decoded/n).read_bytes())
        hook=patch_effective(donor);write(out/'effective-method-hooks.json',dict(passed=True,**hook))
        hooked={'org/emulationstation/frontend/station/'+n+'.smali' for n in HOOKED}
        before|=hooked;final|=hooked
        expected_changed={n:sha(donor/n) for n in final}
        scope=out/(partition+'.scope')
        fields={'schema':'station.catalog-capacity.scoped-types.r175.v1','partition':partition,'donorSha256':pin,
                'families':'|'.join(sorted('Lorg/emulationstation/frontend/station/'+n+';' for n in OWNERS)),
                'originalAllowed':'|'.join(sorted(map(descriptor,before))),'finalAllowed':'|'.join(sorted(map(descriptor,final)))}
        scope.write_text(''.join(k+'='+v+'\n' for k,v in fields.items()))
        run(['java','-cp',cp,'AssembleScopedPartition',base,partition,pin,donor,out/partition,scope],out/(partition+'-assemble.log'))
        check=out/(partition+'.zip')
        with zipfile.ZipFile(check,'x') as z:z.write(out/partition,partition)
        decoded_final=out/(partition+'-final')
        run(['java','-cp',cp,'DecodeDolphinPartition',check,partition,sha(out/partition),decoded_final],out/(partition+'-readback.log'))
        run(['java','-cp',cp,'VerifyScopedPartition',base,partition,pin,decoded_final,scope],out/(partition+'-verify.log'))
        actual=projections(decoded_final);unchanged={n:h for n,h in original.items() if n not in before}
        need(set(actual)==(set(original)-before)|final and all(actual[n]==h for n,h in unchanged.items()),'Unrelated effective class changed')
        need(all(actual[n]==expected_changed[n] for n in final),'Productive class differs from reviewed compiler/hook')
        scopes[partition]={'baselineSha256':pin,'candidateSha256':sha(out/partition),'beforeClassCount':len(original),'afterClassCount':len(actual),
            'unrelatedClassCount':len(unchanged),'unrelatedProjectionSha256':digest(canonical(unchanged)),
            'originalAllowedTypes':sorted(map(descriptor,before)),'finalAllowedTypes':sorted(map(descriptor,final)),
            'effectiveTransportResponseBodyPreserved':actual['org/emulationstation/frontend/station/StationHttp$ResponseBody.smali']==original['org/emulationstation/frontend/station/StationHttp$ResponseBody.smali']}
    run(['java','-cp',cp,'CheckDexReferences',base,out],out/'final-references.log')
    with zipfile.ZipFile(base) as z:manifest=patch_manifest(z.read('AndroidManifest.xml'))
    (out/'AndroidManifest.xml').write_bytes(manifest)
    need(freeze(revision,task)==pins,'Source changed during compile')
    write(out/'receipt.json',{'schema':'station.r175.compile.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,
          'baselineApkSha256':BASE_SHA,'partitions':scopes,'manifestSha256':digest(manifest),'minimumSdk':26,'targetSdk':34,
          'catalogMaximumItems':20000,'completeNetworkCatalogRequired':True,'legacyOfflineCachePreserved':True,
          'sameRevisionCountRepairPublished':True,'oneGlobalCoverWorkerPreserved':True,
          'toolsSha256':{p.name:sha(p) for p in [android,d8,apktool,*classpath]},'testOrFixtureTypesPackaged':False,'apkAssembled':False})
    print('SCOPED_DEX_PASSED',json.dumps({n:{k:v for k,v in s.items() if k in ['beforeClassCount','afterClassCount','unrelatedClassCount']} for n,s in scopes.items()}),flush=True)

def fingerprint(raw):
    matches=[]
    for m in re.finditer(rb'\{"',raw):
        end=raw.find(b'\0',m.start())
        try:
            value=json.loads(raw[m.start():end].decode('ascii'))
            if isinstance(value,dict) and isinstance(value.get('payloadSha256'),dict):
                need(raw[m.start():end]==canonical(value),'Noncanonical fingerprint');matches.append(value)
        except (ValueError,UnicodeError):pass
    need(len(matches)==1,'Exactly one runtime manifest');return matches[0]

def build_frontend(task,ndk):
    import struct
    out=task/'native';root=HERE.parent/'native';tools=ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin'
    before=(root/'station_frontend-before-capacity.cpp').read_bytes();after=(root/'station_frontend.cpp').read_bytes()
    expected=before
    for old,new in [(b'total>4096',b'total>20000'),(b'GetArrayLength(rows)>4096',b'GetArrayLength(rows)>20000')]:
        need(expected.count(old)==1 and new not in expected,'Exact JNI capacity source anchors');expected=expected.replace(old,new)
    need(expected==after,'Only two JNI catalogue limits may change')
    base=task/'inputs/TurboStations-Premium-R174.apk';original=out/'frontend-parent.so'
    with zipfile.ZipFile(base) as z:original.write_bytes(z.read(PREFIX+'libstation_frontend.so'))
    need(sha(original)=='438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d','Current signed native frontend')
    flags=[tools/'clang++','--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined',
           '-fvisibility=hidden','-Wall','-Wextra','-Werror','-Wno-return-type-c-linkage','-static-libstdc++','-Wl,--exclude-libs,ALL','-I',root]
    baseline=out/'frontend-baseline-linux.so';candidate=out/'libstation_frontend.so'
    run([*flags,root/'station_frontend-before-capacity.cpp','-ldl','-llog','-o',baseline],out/'frontend-baseline-compile.log')
    def allocated(p):
        raw=p.read_bytes();need(raw[:6]==b'\x7fELF\x02\x01','AArch64 ELF required')
        offset=struct.unpack_from('<Q',raw,40)[0];size,count,index=struct.unpack_from('<HHH',raw,58)
        rows=[struct.unpack_from('<IIQQQQIIQQ',raw,offset+i*size) for i in range(count)];strings=rows[index];names=raw[strings[4]:strings[4]+strings[5]]
        return {names[r[0]:names.find(b'\0',r[0])].decode():(r[1],r[2],r[3],r[5],b'' if r[1]==8 else raw[r[4]:r[4]+r[5]]) for r in rows if r[2]&2}
    need(allocated(original)==allocated(baseline),'Every allocated baseline section must exactly reproduce effective R174 frontend')
    run([*flags,root/'station_frontend.cpp','-ldl','-llog','-o',candidate],out/'frontend-capacity-compile.log')
    def exports(p,label):
        result=run([tools/'llvm-nm','-D','--defined-only',p],out/(label+'-exports.log'))
        return {line.split()[-1] for line in result.splitlines() if len(line.split())>=2}
    need(exports(original,'frontend-parent')==exports(candidate,'frontend-candidate'),'Native frontend ABI must stay exact')
    loads=run([tools/'llvm-readelf','-lW',candidate],out/'frontend-loads.log')
    alignment=re.findall(r'^\s*LOAD\s+.*\s(0x[0-9a-fA-F]+)\s*$',loads,re.M)
    need(alignment and all(int(v,16)>=16384 for v in alignment),'Native frontend 16 KiB alignment')
    asm=run([tools/'llvm-objdump','-d','--disassemble-symbols=Java_org_emulationstation_frontend_station_StationFrontend_publishCatalog,Java_org_emulationstation_frontend_station_StationFrontend_publishPreparation',candidate],out/'frontend-capacity-disassembly.log')
    # LLVM emits >20000 for preparation and the equivalent >=20001 for JNI array length.
    preparation=re.search(r'mov\s+w8, #0x4e20[^\n]*\n[^\n]*cmp\s+w3, w8[^\n]*\n[^\n]*b\.gt\s',asm)
    catalogue=re.search(r'mov\s+w8, #0x4e21[^\n]*\n[^\n]*cmp\s+w0, w8[^\n]*\n[^\n]*b\.ge\s',asm)
    need(preparation and catalogue,'Both productive JNI comparisons must enforce a 20000-item maximum')
    write(out/'frontend-proof.json',dict(passed=True,parentSha256=sha(original),baselineLinuxSha256=sha(baseline),candidateSha256=sha(candidate),
        allAllocatedBaselineSectionsIdentical=True,onlyTwoSourceComparisonsChanged=True,maximumItems=20000,abiExportsPreserved=True,loadingGraphicsAndWarmCachePreserved=True,
        preservedBackgroundModeMaximum=3,elfLoadAlignmentBytes=16384,physicalAndroidValidated=False))
    return candidate

def native(task,ndk,revision):
    out=fresh(task/'native');compiled=json.loads((task/'compile/receipt.json').read_text())
    pins=freeze(revision,task);need(compiled['sourceSha256']==pins and compiled['passed'],'Frozen compiled payload required')
    need('Pkg.Revision = 28.2.13676358' in (ndk/'source.properties').read_text(),'Same production NDK r28c required')
    tools=ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin'
    base=task/'inputs/TurboStations-Premium-R174.apk'
    need(sha(base)==BASE_SHA,'Exact R174 native donor')
    frontend=build_frontend(task,ndk)
    with zipfile.ZipFile(base) as z:
        previous={k:fingerprint(z.read(PREFIX+n)) for k,n in WRAPPERS.items()}
        payload=previous['psx']['payloadSha256']
        need(all(v['payloadSha256']==payload for v in previous.values()),'Parent payload identity disagreement')
        need(all(entry_sha(z,n)==h for n,h in payload.items()),'Actual parent payload mismatch')
        old_registry=json.loads(z.read(ENGINE))
    payload={**payload,**{n:sha(task/'compile'/n) for n in [*DEX_PINS,'AndroidManifest.xml']},PREFIX+'libstation_frontend.so':sha(frontend)}
    transforms={**previous['psx']['productiveTransforms'],**{'station-r175/'+n:h for n,h in pins.items()}}
    markers={};identities={};abi={}
    for kind,name in WRAPPERS.items():
        identity=copy.deepcopy(previous[kind]);identity.update(baseApkSha256=BASE_SHA,payloadSha256=payload,productiveTransforms=transforms)
        identity.update(parentFingerprintSha256=digest(canonical(previous[kind])))
        if kind!='psx':identity['psxRuntimeSha256']=markers['psx']['runtimeSha256']
        raw=canonical(identity);identities[kind]=identity
        stem='StationPsxRuntime' if kind=='psx' else 'StationMupenRuntime' if kind=='n64' else 'StationDolphinRuntime'
        source=out/(kind+('.cpp' if kind=='psx' else '.c'))
        source.write_text(('extern "C" ' if kind=='psx' else '')+'__attribute__((visibility("default"))) const char* '+stem+'Identity(){return "'+digest(raw)+'";}\n'+
            ('extern "C" ' if kind=='psx' else '')+'__attribute__((visibility("default"))) const char* '+stem+'Manifest(){return '+json.dumps(raw.decode('ascii'))+';}\n',encoding='ascii')
        binary=out/name
        if kind=='psx':
            native_root=REPO/'integration/psx-online/native'
            command=[tools/'aarch64-linux-android28-clang++','-std=c++20','-O2','-fPIC','-shared','-fno-omit-frame-pointer','-fno-optimize-sibling-calls','-Wall','-Wextra','-Werror','-Wl,-z,max-page-size=16384','-Wl,-z,relro,-z,now','-Wl,--no-undefined','-Wl,-soname,'+name,'-I'+str(native_root),*[native_root/n for n in NATIVE],source,'-ldl','-o',binary]
        else:
            command=[tools/'clang','--target=aarch64-linux-android24','-std=c11','-Oz','-fPIC','-fvisibility=hidden','-Wall','-Wextra','-Werror','-shared',source,'-o',binary,'-Wl,--no-undefined','-Wl,--build-id=sha1','-Wl,-soname,'+name,'-Wl,-z,max-page-size=16384','-Wl,-z,common-page-size=16384']
        run(command,out/(kind+'-compile.log'))
        if kind!='psx':run([tools/'llvm-strip','--strip-unneeded',binary],out/(kind+'-strip.log'))
        need(fingerprint(binary.read_bytes())==identity,'Compiled productive identity differs')
        symbols=run([tools/'llvm-nm','-D','--defined-only',binary],out/(kind+'-symbols.log'))
        with zipfile.ZipFile(base) as donor:
            parent_binary=out/(kind+'-parent.so');parent_binary.write_bytes(donor.read(PREFIX+name))
        parent_symbols=run([tools/'llvm-nm','-D','--defined-only',parent_binary],out/(kind+'-parent-symbols.log'))
        exported=lambda text:{line.split()[-1] for line in text.splitlines() if len(line.split())>=2}
        need(exported(symbols)==exported(parent_symbols),'Unrequested native ABI change')
        abi[kind]={'exportsPreserved':True,'exportCount':len(exported(symbols)),'parentSha256':sha(parent_binary),'candidateSha256':sha(binary),'nativeSourcesUnchangedSinceR174':True,'psxInputDelayFrames':8 if kind=='psx' else None}
        if kind=='psx':
            bridge=(REPO/'integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxBridge.java').read_text()
            expected=set(re.findall(r'public static native \S+\s+(\w+)\(',bridge))
            actual=set(re.findall(r'Java_org_emulationstation_frontend_netplay_StationPsxBridge_(\w+)',symbols))
            need(expected==actual and 'SDL_main' in symbols and 'JNI_OnLoad' in symbols,'PSX JNI/SDL exports')
        need(stem+'Identity' in symbols and stem+'Manifest' in symbols,'Runtime identity exports')
        write(out/(kind+'-fingerprint.json'),identity)
        markers[kind]={'runtimeLibrary':name,'runtimeSha256':sha(binary),'runtimeBytes':binary.stat().st_size,'fingerprintSha256':digest(raw)}
    registry=copy.deepcopy(old_registry);selected={}
    for row in registry['engines']:
        p=row['platform']
        if p not in ['psx','n64','gamecube','wii']:continue
        kind='dolphin' if p in ['gamecube','wii'] else p
        if p=='psx':need(row['options'].count('inputDelayFrames=8\n')==1,'Preserve stable R174 PSX input delay')
        row['engineId']=row['engineId'].rsplit('-',1)[0]+'-'+markers[kind]['runtimeSha256'][:12]
        row['runtimeSha256']=markers[kind]['runtimeSha256'];selected[p]=row['engineId']
    need(len(selected)==4 and len(registry['engines'])==13,'Four renewed owners only')
    for before,after in zip(old_registry['engines'],registry['engines']):
        expected=copy.deepcopy(before)
        need({k:v for k,v in expected.items() if k not in ['engineId','runtimeSha256']}=={k:v for k,v in after.items() if k not in ['engineId','runtimeSha256']},'Unrequested engine policy changed')
    write(out/'engines.json',registry)
    write(out/'abi-contract.json',{'schema':'station.r175.identity-wrapper-abi.v1','passed':True,'scope':'Three runtime identity wrappers; all actual core/dependency bytes verified separately by full APK and private kit comparison','wrappers':abi})
    need((out/'engines.json').stat().st_size<=32768,'Engine reader limit')
    need(freeze(revision,task)==pins,'Source changed during native build')
    write(out/'receipt.json',{'schema':'station.r175.native.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,'markers':markers,'engineIds':selected,'payloadSha256':payload,'preservedCoreBinaries':True,'psxInputDelayFramesBefore':8,'psxInputDelayFramesAfter':8,'gamecubePresentationRecognized':True,'gamecubeOnlineCpuThread':False,'gamecubeRuntimeOverride':'CurrentRun Core.CPUThread=false','otherEmulationOptionsPreserved':True,'offlineLibrariesRebuilt':False,'ndkHost':'linux-x86_64','ndkVersion':'28.2.13676358'})
    print('NATIVE_IDENTITIES_PASSED',json.dumps(selected),flush=True)

def package(task,revision):
    out=fresh(task/'package');compiled=json.loads((task/'compile/receipt.json').read_text());identity=json.loads((task/'native/receipt.json').read_text())
    pins=freeze(revision,task);need(compiled['sourceSha256']==identity['sourceSha256']==pins,'Same frozen sources required')
    base=task/'inputs/TurboStations-Premium-R174.apk';need(sha(base)==BASE_SHA,'Exact R174 package donor')
    replacements={n:task/'compile'/n for n in [*DEX_PINS,'AndroidManifest.xml']}
    replacements[ENGINE]=task/'native/engines.json';replacements.update({PREFIX+n:task/'native'/n for n in WRAPPERS.values()})
    replacements[PREFIX+'libstation_frontend.so']=task/'native/libstation_frontend.so'
    need(set(replacements)==ALLOWED,'Seven-entry catalogue scope')
    for n in DEX_PINS:need(sha(replacements[n])==compiled['partitions'][n]['candidateSha256'],'DEX receipt mismatch')
    need(sha(replacements['AndroidManifest.xml'])==compiled['manifestSha256'],'Manifest receipt mismatch')
    for kind,name in WRAPPERS.items():need(sha(replacements[PREFIX+name])==identity['markers'][kind]['runtimeSha256'],'Native receipt mismatch')
    expected={};before={};unsigned=out/'TurboStations-Premium-R175-unsigned.apk'
    zipfile.ZIP64_LIMIT=(1<<32)-1
    with zipfile.ZipFile(base) as source,zipfile.ZipFile(unsigned,'x',allowZip64=False) as target:
        names=source.namelist();need(len(names)==len(set(names))==13861,'Exact unique entry count')
        for entry in source.infolist():
            name=entry.filename;before[name]=entry_sha(source,name)
            with target.open(copy.copy(entry),'w',force_zip64=False) as stream:
                if name in replacements:
                    with replacements[name].open('rb') as content:shutil.copyfileobj(content,stream,1024*1024)
                else:
                    with source.open(name) as content:shutil.copyfileobj(content,stream,1024*1024)
            expected[name]=sha(replacements[name]) if name in replacements else before[name]
    need({n for n in names if expected[n]!=before[n]}==ALLOWED,'Unexpected package difference')
    with zipfile.ZipFile(unsigned) as z:
        need(z.namelist()==names and all(entry_sha(z,n)==h for n,h in expected.items()),'Full APK readback failed')
    need(freeze(revision,task)==pins,'Source changed during package assembly')
    write(out/'unsigned-package.json',{'schema':'station.r175.package.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,
          'baseApkSha256':BASE_SHA,'unsignedApkSha256':sha(unsigned),'unsignedApkBytes':unsigned.stat().st_size,'entryCount':len(names),
          'expectedEntrySha256':expected,'replacedEntries':sorted(ALLOWED),'preservedEntryCount':len(names)-len(ALLOWED),'changedDexPartitions':sorted(DEX_PINS),'preservedDexPartitions':39,'compileReceiptSha256':sha(task/'compile/receipt.json'),'nativeReceiptSha256':sha(task/'native/receipt.json')})
    print('UNSIGNED_PACKAGE_PASSED',len(names),'entries',len(names)-len(ALLOWED),'preserved',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['compile','native','package'])
    p.add_argument('--task',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--ndk',type=Path);p.add_argument('--source-commit',required=True)
    a=p.parse_args();need(not a.task.resolve().is_relative_to(REPO),'Private outputs outside Git')
    if a.stage=='compile':compile_dex(a.task,a.sdk,a.source_commit)
    elif a.stage=='native':need(a.ndk is not None,'NDK required');native(a.task,a.ndk,a.source_commit)
    else:package(a.task,a.source_commit)
if __name__=='__main__':main()
