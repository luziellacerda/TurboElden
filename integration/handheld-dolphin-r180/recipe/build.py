"""Scoped R180 GBA packet link, Wii player display and pre-trial GameCube restoration on exact R179.

Stages never install, contact a phone, alter the backup or deploy the server.
Output is private. No synthetic classpath, replacement key or old finalizer.
"""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, zipfile
from manifest_delta import patch as patch_manifest

REPO=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BASE_SHA='aad5358bc1920a94eda414cf3edcccd5acd46daaaa54eed73ed4c005aec7032d'
BASE_SIZE=2716859490
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
DEX_PINS={'classes35.dex':'0ddcff5826d777962aebf29063853ce572490e064239b34bae44e6cc1354ccc5'}
OWNERS={'StationDolphinSession','StationDolphinLaunch','StationMultiplayerProfile','StationDolphinBufferPolicy','StationGamePlayerInfo','StationOnlinePlatformPolicy','StationRetroLaunch','StationGbaLinkPolicy'}
NATIVE=['StationPsxEntry.cpp','StationPsxOwner.cpp','StationPsxProtocol.cpp','StationPsxSha256.cpp']
WRAPPERS={'psx':'libstation_psx_online.so','n64':'libstation_mupen64plus_runtime.so','dolphin':'libstation_dolphin_runtime.so'}
PREFIX='lib/arm64-v8a/'
ENGINE='assets/station-online/engines.json'
from registry_delta import CORE as GBA_CORE, OVERLAY as GBA_OVERLAY, core_input, restore_dolphin_identity, append_gba, assert_preserved
ADDED={GBA_CORE,GBA_OVERLAY}
ALLOWED=set(DEX_PINS)|{'AndroidManifest.xml',ENGINE}|{PREFIX+n for n in WRAPPERS.values()}|ADDED

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
def instruction_projection(raw):
    # Smali rebuilds rename branch labels and move .line across a label at the
    # same code address. Compare all other text and each label's actual target.
    lines=[line.strip() for line in raw.splitlines()
           if line.strip() and not line.strip().startswith('.line ')]
    result=[]; section=[]
    def normalized(block):
        labels={};position=0;data=False;definitions=[]
        for index,line in enumerate(block):
            if re.fullmatch(r':[A-Za-z0-9_]+',line) and not data:
                need(line not in labels,'Duplicate patched label');labels[line]=':target_'+str(position)
                definitions.append(index)
            else:position+=1
            if line.startswith(('.packed-switch ','.sparse-switch ','.array-data ')):data=True
            if line in ('.end packed-switch','.end sparse-switch','.end array-data'):data=False
        def token(match):
            value=match.group()
            return value if value.startswith('"') else labels.get(value,value)
        return [re.sub(r'"(?:\\.|[^"\\])*"|:[A-Za-z0-9_]+',token,line)
                for index,line in enumerate(block) if index not in definitions]
    for line in lines:
        if line.startswith('.method '):
            need(not section,'Nested method');section=[line]
        elif section:
            section.append(line)
            if line=='.end method':result+=normalized(section);section=[]
        else:result.append(line)
    need(not section,'Unclosed patched method');return result
def fresh(path):Path(path).mkdir(parents=True,exist_ok=False);return Path(path)

def freeze(revision,task):
    need(re.fullmatch('[0-9a-f]{40}',revision) is not None,'Frozen full source commit')
    actual=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    need(actual==revision,'Build must run from frozen HEAD')
    sources=list(HERE.glob('*.py'))+list(HERE.glob('*.java'))+[HERE/'COMPILER-INPUTS.json',HERE.parent/'signing/sign.py',HERE.parent/'signing/package_server_kit.py']
    sources += list((HERE.parent/'java').rglob('*.java')) + list((HERE.parent/'assets').glob('*.cfg'))
    sources+=list((REPO/'integration/psx-online/native').glob('*.cpp'))+list((REPO/'integration/psx-online/native').glob('*.hpp'))+[REPO/'integration/psx-online/native/PsxPinnedOptions.h']
    sources+=[REPO/'integration/psx-updater-r170/recipe/manifest_delta.py',HERE.parent/'SCOPE.json']
    parent=json.loads((task/'inputs/parent-compile-receipt.json').read_text())
    need(parent['passed'] and parent['sourceCommit']=='f2ca5b4caa3c5cffff6ac0a896dd645c685cbe96','Frozen R179 GBA-photo compiler provenance')
    for name,pin in parent['sourceSha256'].items():
        # Every parent productive source remains exact; only the new reviewed module is compiled.
        blob=subprocess.check_output(['git','-C',str(REPO),'show',revision+':'+name])
        need(digest(blob)==pin,'Unrequested R179 source changed: '+name)
    result={}
    for source in sorted(set(sources)):
        name=source.relative_to(REPO).as_posix();raw=source.read_bytes()
        expected=subprocess.check_output(['git','-C',str(REPO),'show',revision+':'+name])
        need(expected==raw,'Source differs from frozen commit: '+name);result[name]=digest(raw)
    for name,pin in json.loads((HERE/'COMPILER-INPUTS.json').read_text()).items():
        need(sha(task/'inputs'/name)==pin,'Real R179 classpath changed: '+name)
    return result

def compile_dex(task,sdk,revision):
    base=task/'inputs/TurboStations-Premium-R179.apk'
    need(base.stat().st_size==BASE_SIZE and sha(base)==BASE_SHA,'Exact signed R179 donor')
    pins=freeze(revision,task);out=fresh(task/'compile');inputs=task/'inputs'
    android=sdk/'platforms/android-36/android.jar';apktool=inputs/'apktool.jar'
    classes=fresh(out/'classes');sources=sorted((HERE.parent/'java').rglob('*.java'))
    need({p.name for p in sources}=={'StationGamePlayerInfo.java','StationGbaLinkPolicy.java'},'Only two new overlay families')
    run(['javac','--release','8','-encoding','UTF-8','-proc:none','-sourcepath','','-cp',android,'-d',classes,*sources],out/'javac.log')
    overlay=fresh(out/'overlay');d8=sdk/'build-tools/36.0.0/lib/d8.jar'
    log=run(['java','-cp',d8,'com.android.tools.r8.D8','--release','--min-api','26','--lib',android,'--output',overlay,*sorted(classes.rglob('*.class'))],out/'d8.log')
    need(not re.search(r'(?im)^\s*(warning|error)\b',log),'Review any D8 diagnostic')
    tools=fresh(out/'tools')
    run(['javac','--release','17','-encoding','UTF-8','-cp',apktool,'-d',tools,*sorted(HERE.glob('*.java'))],out/'helpers.log')
    cp=os.pathsep.join(map(str,[tools,apktool]))
    overlay_zip=out/'overlay.zip'
    with zipfile.ZipFile(overlay_zip,'x') as z:z.write(overlay/'classes.dex','classes.dex')
    decoded_overlay=out/'overlay-smali'
    run(['java','-cp',cp,'DecodeDolphinPartition',overlay_zip,'classes.dex',sha(overlay/'classes.dex'),decoded_overlay],out/'overlay-decode.log')
    rollback=inputs/'rollback-classes35.dex'
    need(sha(rollback)=='be5f233f1cccf7f5e94e77bea10c5e8e8452619d407d2c129f34479ce8572413','Exact signed pre-trial R173 classes35')
    rollback_zip=out/'rollback.zip'
    with zipfile.ZipFile(rollback_zip,'x') as z:z.write(rollback,'classes.dex')
    decoded_rollback=out/'rollback-smali'
    run(['java','-cp',cp,'DecodeDolphinPartition',rollback_zip,'classes.dex',sha(rollback),decoded_rollback],out/'rollback-decode.log')
    partition='classes35.dex';pin=DEX_PINS[partition];donor=out/(partition+'-smali')
    run(['java','-cp',cp,'DecodeDolphinPartition',base,partition,pin,donor],out/(partition+'-decode.log'))
    original=projections(donor)
    from patch_payload import patch
    before,after=patch(donor,decoded_rollback,decoded_overlay)
    need(all(belongs(descriptor(n),OWNERS) for n in before|after),'Delta escaped its named owners')
    expected_changed={n:instruction_projection((donor/n).read_text()) for n in after}
    scope=out/(partition+'.scope')
    fields={'schema':'station.three-platforms.scoped-types.r180.v1','partition':partition,'donorSha256':pin,
            'families':'|'.join(sorted('Lorg/emulationstation/frontend/netplay/'+n+';' for n in OWNERS)),
            'originalAllowed':'|'.join(sorted(map(descriptor,before))),'finalAllowed':'|'.join(sorted(map(descriptor,after)))}
    scope.write_text(''.join(k+'='+v+'\n' for k,v in fields.items()))
    run(['java','-cp',cp,'AssembleScopedPartition',base,partition,pin,donor,out/partition,scope],out/(partition+'-assemble.log'))
    check=out/(partition+'.zip')
    with zipfile.ZipFile(check,'x') as z:z.write(out/partition,partition)
    decoded=out/(partition+'-final')
    run(['java','-cp',cp,'DecodeDolphinPartition',check,partition,sha(out/partition),decoded],out/(partition+'-readback.log'))
    run(['java','-cp',cp,'VerifyScopedPartition',base,partition,pin,decoded,scope],out/(partition+'-verify.log'))
    actual=projections(decoded);unchanged={n:h for n,h in original.items() if n not in before}
    need(set(actual)==(set(original)-before)|after and all(actual[n]==h for n,h in unchanged.items()),'Unrelated class changed')
    need(all(instruction_projection((decoded/n).read_text())==v for n,v in expected_changed.items()),'DEX instructions or branch targets differ from reviewed patch')
    run(['java','-cp',cp,'CheckDexReferences',base,out],out/'final-references.log')
    with zipfile.ZipFile(base) as z:manifest=patch_manifest(z.read('AndroidManifest.xml'))
    (out/'AndroidManifest.xml').write_bytes(manifest)
    scope_proof={'baselineSha256':pin,'candidateSha256':sha(out/partition),'beforeClassCount':len(original),
       'afterClassCount':len(actual),'unrelatedClassCount':len(unchanged),'unrelatedProjectionSha256':digest(canonical(unchanged)),
       'originalAllowedTypes':sorted(map(descriptor,before)),'finalAllowedTypes':sorted(map(descriptor,after)),
       'preTrialDolphinSessionRestoredExactly':True,'eightFramePolicyRemoved':True,'onlyGbaRetroConfigTransformed':True}
    need(freeze(revision,task)==pins,'Source changed during compile')
    write(out/'receipt.json',{'schema':'station.r180.compile.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,
       'baselineApkSha256':BASE_SHA,'partitions':{partition:scope_proof},'manifestSha256':digest(manifest),'minimumSdk':26,'targetSdk':34,
       'functionalDeltas':['pre-trial GameCube restoration','Wii and GBA verified-player presentation','independent GBA P1 and private persistent online saves'],
       'androidUpdaterFixPreserved':True,'toolsSha256':{apktool.name:sha(apktool),android.name:sha(android)},'testOrFixtureTypesPackaged':False,'apkAssembled':False})
    print('SCOPED_DEX_PASSED',json.dumps(scope_proof),flush=True)

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
    base=task/'inputs/TurboStations-Premium-R179.apk'
    need(sha(base)==BASE_SHA,'Exact R179 native donor')
    with zipfile.ZipFile(base) as z:
        previous={k:fingerprint(z.read(PREFIX+n)) for k,n in WRAPPERS.items()}
        payload=previous['psx']['payloadSha256']
        need(all(v['payloadSha256']==payload for v in previous.values()),'Parent payload identity disagreement')
        need(all(entry_sha(z,n)==h for n,h in payload.items()),'Actual parent payload mismatch')
        old_registry=json.loads(z.read(ENGINE))
    gba_binary,gba_proof=core_input(task,HERE)
    payload={**payload,**{n:sha(task/'compile'/n) for n in [*DEX_PINS,'AndroidManifest.xml']},
             GBA_CORE:sha(gba_binary),GBA_OVERLAY:sha(HERE.parent/'assets/gba.cfg')}
    transforms={**previous['psx']['productiveTransforms'],**{'station-r180/'+n:h for n,h in pins.items()}}
    markers={};identities={};abi={}
    for kind,name in WRAPPERS.items():
        identity=copy.deepcopy(previous[kind]);identity.update(baseApkSha256=BASE_SHA,payloadSha256=payload,productiveTransforms=transforms)
        identity.update(parentFingerprintSha256=digest(canonical(previous[kind])))
        if kind!='psx':identity['psxRuntimeSha256']=markers['psx']['runtimeSha256']
        if kind=='dolphin':restore_dolphin_identity(identity)
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
        abi[kind]={'exportsPreserved':True,'exportCount':len(exported(symbols)),'parentSha256':sha(parent_binary),'candidateSha256':sha(binary),'nativeSourcesUnchangedSinceR179':True,'psxInputDelayFrames':8 if kind=='psx' else None}
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
        if p=='psx':need(row['options'].count('inputDelayFrames=8\n')==1,'Preserve stable R179 PSX input delay')
        if p=='gamecube':
            need(row['options'].count('padBuffer=8\n')==1,'Pinned GameCube8 options')
            row['options']=row['options'].replace('padBuffer=8\n','padBuffer=5\n')
        row['engineId']=row['engineId'].rsplit('-',1)[0]+'-'+markers[kind]['runtimeSha256'][:12]
        row['runtimeSha256']=markers[kind]['runtimeSha256'];selected[p]=row['engineId']
    need(len(selected)==4 and len(registry['engines'])==13,'Four renewed independent owners')
    with zipfile.ZipFile(base) as donor:runtime_sha=entry_sha(donor,PREFIX+'libstation_retroarch.so')
    gba=append_gba(registry,sha(gba_binary),runtime_sha);selected['gba']=gba['engineId']
    assert_preserved(old_registry,registry)
    write(out/'engines.json',registry)
    write(out/'abi-contract.json',{'schema':'station.r180.identity-wrapper-abi.v1','passed':True,'scope':'Three runtime identity wrappers; all actual core/dependency bytes verified separately by full APK and private kit comparison','wrappers':abi})
    need((out/'engines.json').stat().st_size<=32768,'Engine reader limit')
    need(freeze(revision,task)==pins,'Source changed during native build')
    write(out/'receipt.json',{'schema':'station.r180.native.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,
        'markers':markers,'engineIds':selected,'payloadSha256':payload,'preservedExistingCoreBinaries':True,
        'newGbaCore':gba_proof,'gbaLocalControllersPerPeer':1,'gbaLinkThroughOfficialNetpacket':True,
        'psxInputDelayFramesBefore':8,'psxInputDelayFramesAfter':8,'gamecubePadBufferBefore':8,'gamecubePadBufferAfter':5,
        'wiiPadBuffer':5,'gamecubeCpuOverrideRemoved':True,'gamecubeSessionRestoredFromR173':True,
        'otherEmulationOptionsPreserved':True,'offlineLibrariesRebuilt':False,'ndkHost':'linux-x86_64','ndkVersion':'28.2.13676358'})
    print('NATIVE_IDENTITIES_PASSED',json.dumps(selected),flush=True)

def package(task,revision):
    out=fresh(task/'package');compiled=json.loads((task/'compile/receipt.json').read_text());identity=json.loads((task/'native/receipt.json').read_text())
    pins=freeze(revision,task);need(compiled['sourceSha256']==identity['sourceSha256']==pins,'Same frozen sources')
    base=task/'inputs/TurboStations-Premium-R179.apk';need(sha(base)==BASE_SHA,'Exact R179 package donor')
    gba_binary,gba_proof=core_input(task,HERE)
    replacements={n:task/'compile'/n for n in [*DEX_PINS,'AndroidManifest.xml']}
    replacements[ENGINE]=task/'native/engines.json';replacements.update({PREFIX+n:task/'native'/n for n in WRAPPERS.values()})
    replacements[GBA_CORE]=gba_binary;replacements[GBA_OVERLAY]=HERE.parent/'assets/gba.cfg'
    need(set(replacements)==ALLOWED,'Six replacements and two additions only')
    expected={};before={};unsigned=out/'TurboStations-Premium-R180-unsigned.apk'
    zipfile.ZIP64_LIMIT=(1<<32)-1
    with zipfile.ZipFile(base) as source,zipfile.ZipFile(unsigned,'x',allowZip64=False) as target:
        names=source.namelist();need(len(names)==len(set(names))==13861 and not (set(names)&ADDED),'Exact unique donor entry count')
        for entry in source.infolist():
            name=entry.filename;before[name]=entry_sha(source,name)
            with target.open(copy.copy(entry),'w',force_zip64=False) as stream:
                with (replacements[name].open('rb') if name in replacements else source.open(name)) as content:shutil.copyfileobj(content,stream,1024*1024)
            expected[name]=sha(replacements[name]) if name in replacements else before[name]
        for name in sorted(ADDED):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED if name.endswith('.so') else zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            with target.open(info,'w',force_zip64=False) as stream,replacements[name].open('rb') as content:shutil.copyfileobj(content,stream,1024*1024)
            expected[name]=sha(replacements[name])
    changed={n for n in names if expected[n]!=before[n]}
    need(changed==ALLOWED-ADDED,'Unexpected donor package difference')
    with zipfile.ZipFile(unsigned) as z:
        need(z.namelist()==names+sorted(ADDED) and all(entry_sha(z,n)==h for n,h in expected.items()),'Full APK readback')
        cfg=z.read(GBA_OVERLAY).decode()
        for relative in re.findall(r'^overlay[0-9]+_desc[0-9]+_overlay = (.+)$',cfg,re.M):
            need('assets/station-online/overlays/station-local/'+relative in expected,'Missing GBA control artwork')
    need(freeze(revision,task)==pins,'Source changed during package assembly')
    write(out/'unsigned-package.json',{'schema':'station.r180.package.v1','passed':True,'sourceCommit':revision,'sourceSha256':pins,
          'baseApkSha256':BASE_SHA,'unsignedApkSha256':sha(unsigned),'unsignedApkBytes':unsigned.stat().st_size,'entryCount':len(expected),
          'expectedEntrySha256':expected,'replacedEntries':sorted(changed),'addedEntries':sorted(ADDED),'preservedEntryCount':len(names)-len(changed),
          'changedDexPartitions':sorted(DEX_PINS),'preservedDexPartitions':39,'compileReceiptSha256':sha(task/'compile/receipt.json'),'nativeReceiptSha256':sha(task/'native/receipt.json')})
    print('UNSIGNED_PACKAGE_PASSED',len(expected),'entries',len(names)-len(changed),'preserved',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['compile','native','package'])
    p.add_argument('--task',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--ndk',type=Path);p.add_argument('--source-commit',required=True)
    a=p.parse_args();need(not a.task.resolve().is_relative_to(REPO),'Private outputs outside Git')
    if a.stage=='compile':compile_dex(a.task,a.sdk,a.source_commit)
    elif a.stage=='native':need(a.ndk is not None,'NDK required');native(a.task,a.ndk,a.source_commit)
    else:package(a.task,a.source_commit)
if __name__=='__main__':main()
