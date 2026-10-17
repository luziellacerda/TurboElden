"""Scoped R177 GameCube online pad buffer eight candidate on the exact signed R176.

Stages never install, contact a phone, alter the backup or deploy the server.
Output is private. No synthetic classpath, replacement key or old finalizer.
"""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, zipfile
from manifest_delta import patch as patch_manifest

REPO=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BASE_SHA='d444e920418d130c2da338f0fc8ff96d2f5cf0484c64f0ed3cf15fda071aba65'
BASE_SIZE=2714270818
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
DEX_PINS={'classes35.dex':'be5f233f1cccf7f5e94e77bea10c5e8e8452619d407d2c129f34479ce8572413'}
OWNERS={'StationDolphinSession','StationDolphinLaunch','StationMultiplayerProfile','StationDolphinBufferPolicy'}
NATIVE=['StationPsxEntry.cpp','StationPsxOwner.cpp','StationPsxProtocol.cpp','StationPsxSha256.cpp']
WRAPPERS={'psx':'libstation_psx_online.so','n64':'libstation_mupen64plus_runtime.so','dolphin':'libstation_dolphin_runtime.so'}
PREFIX='lib/arm64-v8a/'
ENGINE='assets/station-online/engines.json'
ALLOWED=set(DEX_PINS)|{'AndroidManifest.xml',ENGINE}|{PREFIX+n for n in WRAPPERS.values()}

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
    actual=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    need(actual==revision,'Build must run from frozen HEAD')
    sources=list(HERE.glob('*.py'))+list(HERE.glob('*.java'))+[HERE/'COMPILER-INPUTS.json',HERE.parent/'signing/sign.py',HERE.parent/'signing/package_server_kit.py']
    sources.append(HERE.parent/'java/org/emulationstation/frontend/netplay/StationDolphinBufferPolicy.java')
    sources+=list((REPO/'integration/psx-online/native').glob('*.cpp'))+list((REPO/'integration/psx-online/native').glob('*.hpp'))+[REPO/'integration/psx-online/native/PsxPinnedOptions.h']
    sources+=[REPO/'integration/psx-updater-r170/recipe/manifest_delta.py',HERE.parent/'SCOPE.json']
    parent=json.loads((task/'inputs/parent-compile-receipt.json').read_text())
    need(parent['passed'] and parent['sourceCommit']=='ff5022c878782dc2aa86642f226585735e668c4d','Frozen R176 compiler provenance')
    for name,pin in parent['sourceSha256'].items():
        # No prior source may change outside the new GameCube presentation overlay.
        blob=subprocess.check_output(['git','-C',str(REPO),'show',revision+':'+name])
        need(digest(blob)==pin,'Unrequested R176 source changed: '+name)
    result={}
    for source in sorted(set(sources)):
        name=source.relative_to(REPO).as_posix();raw=source.read_bytes()
        expected=subprocess.check_output(['git','-C',str(REPO),'show',revision+':'+name])
        need(expected==raw,'Source differs from frozen commit: '+name);result[name]=digest(raw)
    for name,pin in json.loads((HERE/'COMPILER-INPUTS.json').read_text()).items():
        need(sha(task/'inputs'/name)==pin,'Real R176 classpath changed: '+name)
    return result

def compile_dex(task,sdk,revision):
    base=task/'inputs/TurboStations-Premium-R176.apk'
    need(base.stat().st_size==BASE_SIZE and sha(base)==BASE_SHA,'Exact signed R176 required')
    pins=freeze(revision,task);out=fresh(task/'compile')
    inputs=task/'inputs';classes=fresh(out/'classes');android=sdk/'platforms/android-36/android.jar'
    classpath=[]  # Policy uses only the actual Android API and reflective pinned JNI.
    sources=[HERE.parent/'java/org/emulationstation/frontend/netplay/StationDolphinBufferPolicy.java']
    run(['javac','--release','8','-encoding','UTF-8','-Xlint:-options','-proc:none','-sourcepath','','-cp',os.pathsep.join(map(str,[android,*classpath])),'-d',classes,*sources],out/'javac.log')
    program=sorted(classes.rglob('*.class'))
    need(all(belongs(p.relative_to(classes).as_posix().removesuffix('.class')+';',OWNERS) for p in program),'Foreign JVM class')
    overlay=fresh(out/'overlay');d8=sdk/'build-tools/36.0.0/lib/d8.jar'
    command=['java','-cp',d8,'com.android.tools.r8.D8','--release','--min-api','26','--lib',android,'--output',overlay]
    for dep in classpath:command+=['--classpath',dep]
    log=run([*command,*program],out/'d8.log')
    need(not re.search(r'(?im)^\s*(warning|error)\b',log),'D8 diagnostic requires review')
    tools=fresh(out/'tools');apktool=inputs/'apktool.jar'
    run(['javac','--release','17','-encoding','UTF-8','-cp',apktool,'-d',tools,*sorted(HERE.glob('*.java'))],out/'helpers.log')
    cp=os.pathsep.join(map(str,[tools,apktool]))
    run(['java','-cp',cp,'VerifyNativeConfigAbi',base],out/'native-config-abi.log')
    oz=out/'overlay.zip'
    with zipfile.ZipFile(oz,'x') as z:z.write(overlay/'classes.dex','classes.dex')
    decoded=out/'overlay-smali'
    run(['java','-cp',cp,'DecodeDolphinPartition',oz,'classes.dex',sha(overlay/'classes.dex'),decoded],out/'decode-overlay.log')
    overlay_files=projections(decoded)
    need(all(belongs(descriptor(n),OWNERS) for n in overlay_files),'D8 emitted a foreign owner')
    scopes={}
    for partition,pin in DEX_PINS.items():
        names=OWNERS
        donor=out/(partition+'-smali')
        run(['java','-cp',cp,'DecodeDolphinPartition',base,partition,pin,donor],out/(partition+'-decode.log'))
        original=projections(donor)
        permitted=lambda n:belongs(descriptor(n),names)
        from patch_payload import patch
        before, added = patch(donor, decoded)
        final = before | added
        need(set(overlay_files) == added and len(before) == 3, 'Exact three existing classes and one new policy')
        expected_changed = {n: sha(donor/n) for n in final}
        write(out/'session-hook.json', dict(passed=True, sessionSource='exact signed R176; effective session equals R173 before patch',
              onlyAddedConfigureHook=True, scratchRegister='v0', receiverRegister='v7',
              scratchOverwrittenByOriginalNextInstruction=True, optionsChecksUpdated=5,
              existingLaunchAndProfileChecksPreserved=True, javaSessionCompiled=False))
        scope=out/(partition+'.scope')
        fields={'schema':'station.gamecube-buffer.scoped-types.r177.v1','partition':partition,'donorSha256':pin,
                'families':'|'.join(sorted(('Lorg/emulationstation/frontend/netplay/'+n+';') for n in names)),
                'originalAllowed':'|'.join(sorted(map(descriptor,before))),'finalAllowed':'|'.join(sorted(map(descriptor,final)))}
        scope.write_text(''.join(k+'='+v+'\n' for k,v in fields.items()))
        run(['java','-cp',cp,'AssembleScopedPartition',base,partition,pin,donor,out/partition,scope],out/(partition+'-assemble.log'))
        check=out/(partition+'.zip')
        with zipfile.ZipFile(check,'x') as z:z.write(out/partition,partition)
        decoded_final=out/(partition+'-final')
        run(['java','-cp',cp,'DecodeDolphinPartition',check,partition,sha(out/partition),decoded_final],out/(partition+'-readback.log'))
        run(['java','-cp',cp,'VerifyScopedPartition',base,partition,pin,decoded_final,scope],out/(partition+'-verify.log'))
        actual=projections(decoded_final);unchanged={n:h for n,h in original.items() if n not in before}
        need(set(actual)==(set(original)-before)|final and all(actual[n]==h for n,h in unchanged.items()),'Unrelated class changed')
        need(all(actual[n]==expected_changed[n] for n in final),'Productive helper/session differs from reviewed patch')
        scopes[partition]={'baselineSha256':pin,'candidateSha256':sha(out/partition),'beforeClassCount':len(original),'afterClassCount':len(actual),
            'unrelatedClassCount':len(unchanged),'unrelatedProjectionSha256':digest(canonical(unchanged)),
            'originalAllowedTypes':sorted(map(descriptor,before)),'finalAllowedTypes':sorted(map(descriptor,final))}
    run(['java','-cp',cp,'CheckDexReferences',base,out],out/'final-references.log')
    with zipfile.ZipFile(base) as z:manifest=patch_manifest(z.read('AndroidManifest.xml'))
    (out/'AndroidManifest.xml').write_bytes(manifest)
    need(freeze(revision,task)==pins,'Source changed during compile')
    write(out/'receipt.json',{'schema':'station.r177.compile.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,
          'baselineApkSha256':BASE_SHA,'partitions':scopes,'manifestSha256':digest(manifest),'minimumSdk':26,'targetSdk':34,
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

def native(task,ndk,revision):
    out=fresh(task/'native');compiled=json.loads((task/'compile/receipt.json').read_text())
    pins=freeze(revision,task);need(compiled['sourceSha256']==pins and compiled['passed'],'Frozen compiled payload required')
    need('Pkg.Revision = 28.2.13676358' in (ndk/'source.properties').read_text(),'Same production NDK r28c required')
    tools=ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin'
    base=task/'inputs/TurboStations-Premium-R176.apk'
    need(sha(base)==BASE_SHA,'Exact R176 native donor')
    with zipfile.ZipFile(base) as z:
        previous={k:fingerprint(z.read(PREFIX+n)) for k,n in WRAPPERS.items()}
        payload=previous['psx']['payloadSha256']
        need(all(v['payloadSha256']==payload for v in previous.values()),'Parent payload identity disagreement')
        need(all(entry_sha(z,n)==h for n,h in payload.items()),'Actual parent payload mismatch')
        old_registry=json.loads(z.read(ENGINE))
    payload={**payload,**{n:sha(task/'compile'/n) for n in [*DEX_PINS,'AndroidManifest.xml']}}
    transforms={**previous['psx']['productiveTransforms'],**{'station-r177/'+n:h for n,h in pins.items()}}
    markers={};identities={};abi={}
    for kind,name in WRAPPERS.items():
        identity=copy.deepcopy(previous[kind]);identity.update(baseApkSha256=BASE_SHA,payloadSha256=payload,productiveTransforms=transforms)
        identity.update(parentFingerprintSha256=digest(canonical(previous[kind])))
        if kind!='psx':identity['psxRuntimeSha256']=markers['psx']['runtimeSha256']
        if kind=='dolphin':
            base_options=identity['options'];need(base_options.count('padBuffer=5\n')==1,'Legacy Dolphin pad-buffer identity')
            identity['platformOptions']={'gamecube':base_options.replace('padBuffer=5\n','padBuffer=8\n'),'wii':base_options}
            identity['gamecubePadBufferOverride']={'layer':4,'section':'NetPlay','key':'BufferSize','value':8}
            config={'schemaVersion':1,'controllerProfile':'dolphin-gamecube-four-ports-v1','devices':[1,1,1,1],'coreOptions':identity['platformOptions']['gamecube']}
            identity['controllerProfileSha256']['gamecube']=digest(json.dumps(config,ensure_ascii=False,separators=(',',':')).replace('/','\\/').encode())
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
        abi[kind]={'exportsPreserved':True,'exportCount':len(exported(symbols)),'parentSha256':sha(parent_binary),'candidateSha256':sha(binary),'nativeSourcesUnchangedSinceR176':True,'psxInputDelayFrames':8 if kind=='psx' else None}
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
        if p=='psx':need(row['options'].count('inputDelayFrames=8\n')==1,'Preserve stable R176 PSX input delay')
        if p=='gamecube':
            need(row['options'].count('padBuffer=5\n')==1,'Exact original GameCube pad buffer')
            row['options']=row['options'].replace('padBuffer=5\n','padBuffer=8\n')
        row['engineId']=row['engineId'].rsplit('-',1)[0]+'-'+markers[kind]['runtimeSha256'][:12]
        row['runtimeSha256']=markers[kind]['runtimeSha256'];selected[p]=row['engineId']
    need(len(selected)==4 and len(registry['engines'])==13,'Four renewed owners only')
    for before,after in zip(old_registry['engines'],registry['engines']):
        expected=copy.deepcopy(before)
        if expected['platform']=='gamecube':expected['options']=expected['options'].replace('padBuffer=5\n','padBuffer=8\n')
        need({k:v for k,v in expected.items() if k not in ['engineId','runtimeSha256']}=={k:v for k,v in after.items() if k not in ['engineId','runtimeSha256']},'Unrequested engine policy changed')
    write(out/'engines.json',registry)
    write(out/'abi-contract.json',{'schema':'station.r177.identity-wrapper-abi.v1','passed':True,'scope':'Three runtime identity wrappers; all actual core/dependency bytes verified separately by full APK and private kit comparison','wrappers':abi})
    need((out/'engines.json').stat().st_size<=32768,'Engine reader limit')
    need(freeze(revision,task)==pins,'Source changed during native build')
    write(out/'receipt.json',{'schema':'station.r177.native.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,'markers':markers,'engineIds':selected,'payloadSha256':payload,'preservedCoreBinaries':True,'psxInputDelayFramesBefore':8,'psxInputDelayFramesAfter':8,'gamecubePresentationRecognized':True,'gamecubeOnlineCpuThread':None,'gamecubePadBufferBefore':5,'gamecubePadBufferAfter':8,'gamecubeCpuOverrideRemoved':True,'gamecubeRuntimeOverride':'CurrentRun NetPlay.BufferSize=8; Active verified before nativeConnect; normal R173 CPU selection preserved','otherEmulationOptionsPreserved':True,'offlineLibrariesRebuilt':False,'ndkHost':'linux-x86_64','ndkVersion':'28.2.13676358'})
    print('NATIVE_IDENTITIES_PASSED',json.dumps(selected),flush=True)

def package(task,revision):
    out=fresh(task/'package');compiled=json.loads((task/'compile/receipt.json').read_text());identity=json.loads((task/'native/receipt.json').read_text())
    pins=freeze(revision,task);need(compiled['sourceSha256']==identity['sourceSha256']==pins,'Same frozen sources required')
    base=task/'inputs/TurboStations-Premium-R176.apk';need(sha(base)==BASE_SHA,'Exact R176 package donor')
    replacements={n:task/'compile'/n for n in [*DEX_PINS,'AndroidManifest.xml']}
    replacements[ENGINE]=task/'native/engines.json';replacements.update({PREFIX+n:task/'native'/n for n in WRAPPERS.values()})
    need(set(replacements)==ALLOWED,'Six-entry scope')
    for n in DEX_PINS:need(sha(replacements[n])==compiled['partitions'][n]['candidateSha256'],'DEX receipt mismatch')
    need(sha(replacements['AndroidManifest.xml'])==compiled['manifestSha256'],'Manifest receipt mismatch')
    for kind,name in WRAPPERS.items():need(sha(replacements[PREFIX+name])==identity['markers'][kind]['runtimeSha256'],'Native receipt mismatch')
    expected={};before={};unsigned=out/'TurboStations-Premium-R177-unsigned.apk'
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
    write(out/'unsigned-package.json',{'schema':'station.r177.package.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,
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
