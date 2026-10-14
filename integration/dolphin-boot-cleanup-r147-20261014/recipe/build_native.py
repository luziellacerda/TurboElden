"""Full closed Dolphin core rebuild: exact donor first, one-line cleanup second.

Only a new frozen integration/dolphin-boot-cleanup-r147-20261014 may execute this.
The original source stage/build/native libraries are read-only inputs. No APK,
Git mutation, registry update, USB, network or binary patch is performed.
"""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, os, re, struct, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
SCOPE='integration/dolphin-boot-cleanup-r147-20261014'
ALLOWED=Path('E:/StationDolphinBootCleanupR147-20261014')
CORE='libstation_dolphin_online.so'
CORE_SHA='f7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d'
UNSTRIPPED_SHA='92b1951facb9fca6aad644026c47adcc62e09c9b5aca61629aab7e1515a270fe'
MAIN='Source/Android/jni/MainAndroid.cpp'
MAIN_SHA='272bd5a97dee85ed8190203c100b05733e5c8f70c655559d3191e2657bf7081e'
UPSTREAM='5102a0339c2177575378107b76541e47cc52122d'
SOURCE_FILES=('native/'+MAIN,'recipe/build_native.py','recipe/StationDolphinMainAndroidOverride.cmake','evidence/native-scope.json')

def need(ok,reason):
    if not ok:raise ValueError(reason)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(p):
    with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8'))
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def source_map():return {n:sha(ROOT/n) for n in SOURCE_FILES}
def git(*args):
    return subprocess.check_output(['git','-c','safe.directory='+str(REPO),'-C',str(REPO),*args])
def verify_frozen(commit,baseline_only=False):
    need(ROOT.parent.name=='integration' and ROOT.name=='dolphin-boot-cleanup-r147-20261014','Only the final published source scope may compile')
    need(len(commit)==40 and git('rev-parse',commit+'^{commit}').decode().strip()==commit,'Concrete final source commit required')
    tracked=git('ls-tree','-r','--name-only',commit,'--',SCOPE).decode().splitlines()
    need(tracked and set(SCOPE+'/'+n for n in SOURCE_FILES)<=set(tracked),'Productive source map is not frozen')
    records={}
    for relative in tracked:
        p=REPO/relative
        need(p.is_file() and not p.is_symlink() and not p.is_junction(),'Frozen source absent/reparse path')
        raw=p.read_bytes()
        need(raw==git('show',commit+':'+relative),'Frozen source drift: '+relative)
        records[relative[len(SCOPE)+1:]]=digest(raw)
    if baseline_only:return records
    spec=importlib.util.spec_from_file_location('r147_native_common',ROOT/'recipe/common.py')
    common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
    return common.verify_commit(commit)
def elf(raw):
    need(raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183,'ELF64 AArch64 required')
    shoff=struct.unpack_from('<Q',raw,40)[0];ss,sn=struct.unpack_from('<HH',raw,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',raw,shoff+i*ss) for i in range(sn)]
    exports=set();needed=[];soname=None
    for section in sections:
        if section[1] not in (6,11):continue
        linked=sections[section[6]];strings=raw[linked[4]:linked[4]+linked[5]]
        for pos in range(section[4],section[4]+section[5],section[9]):
            if section[1]==6:
                tag,value=struct.unpack_from('<qQ',raw,pos)
                if tag in (1,14):
                    name=strings[value:strings.index(0,value)].decode()
                    if tag==1:needed.append(name)
                    else:soname=name
            else:
                name,info,other,index,value,length=struct.unpack_from('<IBBHQQ',raw,pos)
                if index and info>>4 in (1,2) and other&3==0:
                    exports.add(strings[name:strings.index(0,name)].decode())
    phoff=struct.unpack_from('<Q',raw,32)[0];ps,pn=struct.unpack_from('<HH',raw,54)
    alignment=[struct.unpack_from('<IIQQQQQQ',raw,phoff+i*ps)[-1] for i in range(pn) if struct.unpack_from('<I',raw,phoff+i*ps)[0]==1]
    return dict(soname=soname,needed=needed,exports=sorted(exports),loadAlignment=alignment)
def checked_source_tree(stage,closure):
    protected_header=stage/'Source/Core/Common/scmrev.h'
    need(not protected_header.exists() and not protected_header.is_symlink() and not protected_header.is_junction(),'Original in-tree scmrev.h must remain absent; no source deletion is permitted')
    actual=set()
    for top in stage.iterdir():
        if top.name.startswith('station-'):continue
        need(not top.is_symlink() and not top.is_junction(),'Original source reparse path refused')
        candidates=top.rglob('*') if top.is_dir() else (top,)
        for item in candidates:
            need(not item.is_symlink() and not item.is_junction(),'Original source reparse path refused')
            if item.is_file():actual.add(item.relative_to(stage).as_posix())
    need(actual==set(closure['files']),'Original source tree file set changed')
    observed={}
    for name,row in closure['files'].items():
        p=stage/name
        need(p.is_file() and not p.is_symlink() and not p.is_junction(),'Closed source missing/reparse: '+name)
        need(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Original source changed: '+name)
        observed[name]=row
    need(digest(canonical(observed))==closure['canonicalTreeSha256'],'Source closure map differs')
    return observed
def verify_original_inputs(a,scope):
    for name,path in [('buildClosure',a.build_closure),('sourceClosure',a.source_closure),('graphClosure',a.graph_closure)]:
        need(sha(path)==scope['privateInputReceiptSha256'][name],'Closed private receipt differs: '+name)
    plan,tree,graph=read(a.build_closure),read(a.source_closure),read(a.graph_closure)
    need(plan['upstream']==UPSTREAM and plan['historicalCompiledCoreSha256']==CORE_SHA,'Historical motor proof differs')
    need(a.source_stage.resolve()==Path(tree['originalStage']).resolve()==Path(graph['sourceStage']).resolve(),'Original source stage identity differs')
    need(a.original_build.resolve()==Path(graph['originalBuild']).resolve(),'Original build path differs')
    need(a.ndk.resolve()==Path(graph['originalNdk']).resolve(),'Original NDK path differs')
    checked_source_tree(a.source_stage,tree)
    for row in graph['inputs']:
        p=Path(row['originalPath'])
        need(p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Original compiled include/runtime dependency changed')
    for name,row in plan['originalTools'].items():
        need(sha(row['originalPath'])==row['sha256'],'Original compiler/tool drift: '+name)
    for row in plan['dependencyArchives'].values():
        need(sha(row['originalPath'])==row['sha256'],'Original cached dependency archive drift')
    for name,checksum in plan['originalReceipts'].items():need(sha(a.source_stage/name)==checksum,'Original receipt changed')
    native=read(a.parent_native/'native-receipt.json')
    need(sha(a.parent_native/'native-receipt.json')==plan['originalNativeReceiptSha256'],'Original native receipt differs')
    need(native['compiled'] and native['androidApi']==24 and native['sourceDateEpoch']==1790576668,'Original build policy differs')
    for row in native['libraries']:
        need(sha(a.parent_native/row['name'])==row['sha256'],'Original closed native output changed')
    need(sha(a.original_build/'Source/Android/jni'/CORE)==UNSTRIPPED_SHA,'Original complete linked output differs')
    return plan,tree,graph,native
def run(command,log,environment):
    result=subprocess.run(list(map(str,command)),env=environment,capture_output=True)
    Path(log).write_bytes(result.stdout+result.stderr)
    need(result.returncode==0,'Native build phase failed; inspect '+str(log))
def cache_values(path):
    values={}
    for line in Path(path).read_text('utf-8').splitlines():
        if not line or line.startswith(('#','//')) or '=' not in line:continue
        left,value=line.split('=',1)
        if ':' in left:values[left.split(':',1)[0]]=value
    return values
def ninja_decode(value):
    return re.sub(r'\$([ $:])',lambda match:match[1],value)
def approved_main_object(build,overlay,original_row):
    matches=[]
    for line in (build/'build.ninja').read_text('utf-8').splitlines():
        match=re.fullmatch(r'build (.+MainAndroid\.cpp\.o): CXX_COMPILER__main_[^ ]+ (.+?) \|\| .+',line)
        if match and Path(ninja_decode(match[2])).resolve()==overlay.resolve():
            matches.append(build/ninja_decode(match[1]))
    need(len(matches)==1,'Exactly one main target object compiled from the frozen overlay required')
    obj=matches[0]
    need(obj.is_file() and build.resolve() in obj.resolve().parents,'Approved object must be inside the new full build')
    checksum=sha(obj)
    need(checksum!=original_row['sha256'],'Approved MainAndroid object must contain the cleanup delta')
    return obj,dict(originalRelativePath=original_row['relativePath'],productiveRelativePath=obj.relative_to(build).as_posix(),
        baselineSha256=original_row['sha256'],productiveSha256=checksum,compiledSourceSha256=sha(overlay))
def checked_generated_inputs(build,graph,overlay=None):
    result={};delta=None
    for row in graph['inputs']:
        if row['kind']!='generated':continue
        if overlay and row['relativePath']=='Source/Android/jni/CMakeFiles/main.dir/MainAndroid.cpp.o':
            _,delta=approved_main_object(build,overlay,row)
            result[row['relativePath']]=delta['productiveSha256']
            continue
        p=build/row['relativePath']
        need(p.is_file() and sha(p)==row['sha256'],'Generated input/archive differs from original full target: '+row['relativePath'])
        result[row['relativePath']]=row['sha256']
    need(len(result)==94 and (delta is not None)==bool(overlay),'Closed94 generated input set/approved object delta required')
    return result,delta
def configure_build(a,plan,phase,overlay,environment):
    phase.mkdir()
    build=phase/'build'
    tool=plan['originalTools'];cmake=Path(tool['cmake']['originalPath']);ninja=Path(tool['ninja']['originalPath'])
    args=[cmake,'-S',a.source_stage,'-B',build,'-G','Ninja',
        '-DCMAKE_MAKE_PROGRAM='+str(ninja),'-DCMAKE_TOOLCHAIN_FILE='+str(a.ndk/'build/cmake/android.toolchain.cmake'),
        '-DANDROID_ABI=arm64-v8a','-DANDROID_PLATFORM=android-24','-DANDROID_STL=c++_static',
        '-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON','-DCMAKE_BUILD_TYPE=Release',
        '-DENABLE_QT=OFF','-DENABLE_SDL=OFF','-DENABLE_TESTS=OFF','-DENABLE_DISCORD_PRESENCE=OFF',
        '-DENABLE_ANALYTICS=OFF','-DENABLE_AUTOUPDATE=OFF','-DENABLE_CCACHE=OFF','-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF',
        '-DUSE_UPNP=ON','-DUSE_MGBA=ON','-DUSE_RETRO_ACHIEVEMENTS=ON','-DENABLE_CUBEB=ON','-DENABLE_VULKAN=ON',
        '-DCMAKE_PROJECT_INCLUDE='+str(ROOT/'recipe/StationDolphinMainAndroidOverride.cmake'),
        '-DSTATION_ORIGINAL_BUILD='+a.original_build.as_posix(),'-DSTATION_ORIGINAL_STAGE='+a.source_stage.as_posix(),
        '-DSTATION_PACKAGING_ASSET_DIR='+(phase/'packaging-assets').as_posix()]
    if overlay:args.append('-DSTATION_MAIN_ANDROID_OVERLAY='+overlay.as_posix())
    run(args,phase/'configure.log',environment)
    generated_cache=cache_values(build/'CMakeCache.txt')
    need(generated_cache.get('ENABLE_CCACHE')=='OFF','No compiler cache or archived object reuse permitted')
    for name,value in plan['retainedConfiguration'].items():
        need(generated_cache.get(name)==value,'Original native feature/runtime setting changed: '+name)
    run([cmake,'--build',build,'--target','main','--parallel',str(a.jobs)],phase/'full-build.log',environment)
    return build
def qualify(build,phase,native,plan,baseline):
    tools=plan['originalTools'];result={}
    out=phase/'payloads';out.mkdir()
    for old in native['libraries']:
        matches=list(build.rglob(old['name']))
        need(len(matches)==1,'Exactly one full built native library required: '+old['name'])
        original=matches[0]
        raw=original.read_bytes();target=out/old['name'];target.write_bytes(raw)
        if baseline and old['name']==CORE:
            need(digest(raw)==UNSTRIPPED_SHA,'Original full linked/debug motor must also reproduce exactly')
        run([tools['strip']['originalPath'],'--strip-unneeded',target],phase/(old['name']+'.strip.log'),os.environ.copy())
        data=target.read_bytes();contract=elf(data)
        old_contract=elf((Path(old['_parent'])/old['name']).read_bytes())
        need(contract==old_contract,'Native SONAME/needed/exports/16KiB contract changed')
        need(min(contract['loadAlignment'])>=16384,'16KiB ELF alignment required')
        if baseline or old['name']!=CORE:
            need(digest(data)==old['sha256'],'Baseline motor/hooks are not byte exact: '+old['name'])
        elif old['name']==CORE:need(digest(data)!=CORE_SHA,'New core must include the approved cleanup')
        result[old['name']]=dict(path=str(target),sha256=digest(data),bytes=len(data),unstrippedSha256=digest(raw),elf=contract)
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('base-apk','source-stage','original-build','parent-native','build-closure','source-closure','graph-closure','ndk','out'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--source-commit',required=True);p.add_argument('--jobs',type=int,default=4)
    p.add_argument('--baseline-only',action='store_true')
    p.add_argument('--qualified-baseline',type=Path)
    a=p.parse_args();need(1<=a.jobs<=4,'Original bounded compile parallelism required')
    frozen=verify_frozen(a.source_commit,a.baseline_only);source_pins=source_map();scope=read(ROOT/'evidence/native-scope.json')
    need(scope['schema']=='station.r147.dolphin.boot-cleanup.native-scope.v1','Native scope declaration required')
    before=(a.source_stage/MAIN).read_bytes();changed=(ROOT/('native/'+MAIN)).read_bytes()
    anchor=b'  if (!boot_session_data)\n  {\n';replacement=anchor+b'    s_is_booting.Clear();\n'
    need(digest(before)==MAIN_SHA and changed.count(replacement)==1 and changed.replace(replacement,anchor,1)==before,'Whole-file inverse must recover exact original MainAndroid.cpp')
    need(digest(changed)==scope['plannedMainAndroidSha256'],'Native overlay differs from reviewed scope')
    need(not (a.baseline_only and a.qualified_baseline),'Baseline-only and reuse are mutually exclusive')
    out=a.out.resolve();allowed=ALLOWED.resolve()
    need(out==allowed or allowed in out.parents,'Output must be a fresh R147 namespace')
    need(not out.exists(),'Fresh native output required')
    plan,tree,graph,native=verify_original_inputs(a,scope)
    with zipfile.ZipFile(a.base_apk) as z:
        core=z.read('lib/arm64-v8a/'+CORE);need(digest(core)==CORE_SHA,'Actual final APK must still contain the qualified original Dolphin motor')
        for row in native['libraries']:need(digest(z.read('lib/arm64-v8a/'+row['name']))==row['sha256'],'Actual APK hooks differ from qualified donor')
    native['libraries']=[dict(row,_parent=str(a.parent_native)) for row in native['libraries']]
    out.mkdir(parents=True);environment=os.environ.copy();environment['SOURCE_DATE_EPOCH']='1790576668'
    if a.qualified_baseline:
        prior=read(a.qualified_baseline)
        need(prior['schema']=='station.r147.dolphin.boot-cleanup.baseline.v1' and prior['passed'] and prior['compiled'],'Qualified full baseline receipt required')
        need(prior['sourceSha256']==source_pins and prior['originalSourceTreeClosureSha256']==sha(a.source_closure) and prior['originalGraphClosureSha256']==sha(a.graph_closure) and prior['originalBuildClosureSha256']==sha(a.build_closure),'Reused baseline inputs/source contract differs')
        subprocess.run(['git','-c','safe.directory='+str(REPO),'-C',str(REPO),'merge-base','--is-ancestor',prior['sourceCommit'],a.source_commit],check=True,capture_output=True)
        baseline=prior['baselinePayloads'];generated_headers=prior['generatedInputSha256']
        for row in baseline.values():need(sha(row['path'])==row['sha256'],'Qualified baseline payload changed')
        need(baseline[CORE]['sha256']==CORE_SHA and baseline[CORE]['unstrippedSha256']==UNSTRIPPED_SHA,'Original donor gates required')
    else:
        baseline_build=configure_build(a,plan,out/'baseline',None,environment)
        baseline=qualify(baseline_build,out/'baseline',native,plan,True)
        generated_headers,_=checked_generated_inputs(baseline_build,graph)
        need(baseline[CORE]['sha256']==CORE_SHA,'Exact full donor reproduction must precede productive overlay')
        checked_source_tree(a.source_stage,tree)
    if a.baseline_only:
        need(verify_frozen(a.source_commit,True)==frozen and source_map()==source_pins,'Frozen sources drifted during baseline compile')
        baseline_receipt=dict(schema='station.r147.dolphin.boot-cleanup.baseline.v1',passed=True,compiled=True,
            sourceCommit=a.source_commit,sourceSha256=source_pins,completeFrozenSourceFiles=frozen,
            baselineNativeSha256=CORE_SHA,baselineUnstrippedNativeSha256=UNSTRIPPED_SHA,baselinePayloads=baseline,
            actualDonorApkSha256=sha(a.base_apk),generatedInputSha256=generated_headers,
            originalSourceTreeClosureSha256=sha(a.source_closure),originalBuildClosureSha256=sha(a.build_closure),
            originalGraphClosureSha256=sha(a.graph_closure),originalSourceStageExactlyPreserved=True,
            originalPackagingAssetsRedirected=True,inTreeScmrevAbsencePreserved=True,
            onlyBaselineBuilt=True,productiveOverlayBuilt=False,allFourHooksReproducedExactly=True,
            fullTargetsBuilt=True,archivedObjectsReused=False,androidExecuted=False,
            observedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        (out/'native-baseline-receipt.json').write_text(json.dumps(baseline_receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(dict(passed=True,compiled=True,baselineNativeSha256=CORE_SHA,productiveOverlayBuilt=False)))
        return
    productive_build=configure_build(a,plan,out/'productive',ROOT/('native/'+MAIN),environment)
    payloads=qualify(productive_build,out/'productive',native,plan,False)
    productive_generated_headers,object_delta=checked_generated_inputs(productive_build,graph,ROOT/('native/'+MAIN))
    differing_generated={name for name in generated_headers if generated_headers[name]!=productive_generated_headers[name]}
    need(differing_generated=={object_delta['originalRelativePath']},'Exactly the approved MainAndroid object may differ among94 generated inputs')
    checked_source_tree(a.source_stage,tree)
    need(verify_frozen(a.source_commit)==frozen and source_map()==source_pins,'Frozen sources drifted during compile')
    receipt=dict(schema='station.r147.dolphin.boot-cleanup.native.v1',passed=True,compiled=True,
        sourceCommit=a.source_commit,sourceSha256=source_pins,completeFrozenSourceFiles=frozen,
        baselineNativeSha256=CORE_SHA,outputNativeSha256=payloads[CORE]['sha256'],
        actualDonorApkSha256=sha(a.base_apk),baselineReproduced={'dolphinCore':True,'allFourHooks':True},
        sourceScopeDeclarationSha256=sha(ROOT/'evidence/native-scope.json'),
        originalSourceTreeClosureSha256=sha(a.source_closure),originalBuildClosureSha256=sha(a.build_closure),
        originalGraphClosureSha256=sha(a.graph_closure),originalSourceStageExactlyPreserved=True,
        originalPackagingAssetsRedirected=True,inTreeScmrevAbsencePreserved=True,
        inverseWholeFilePassed=True,onlyNativeChange='One boot-flag clear in null BootSessionData early return',
        normalRunAndSurfaceAndStopFunctionsPreserved=True,
        cpuJitCacheOptionsControllersProfilesNetworkChanged=False,frontendChanged=False,dexChanged=False,
        exportedSymbolsExactlyPreserved=True,dependenciesExactlyPreserved=True,sonameExactlyPreserved=True,
        nativeLoadAlignment=16384,baselinePayloads=baseline,payloads=payloads,
        baselineGeneratedInputSha256=generated_headers,generatedInputSha256=productive_generated_headers,
        approvedGeneratedObjectDelta=object_delta,unchangedGeneratedInputs=93,
        nativeSourceInputSha256={k:r['sha256'] for k,r in tree['files'].items()},
        buildDependencyInputSha256={r['kind']+'/'+r['relativePath']:r['sha256'] for r in graph['inputs']},
        sourceDateEpoch=1790576668,fullTargetsBuilt=True,archivedObjectsReused=False,
        compilerMetadataPathMappingOnly=True,androidExecuted=False,physicalGameplayVerified=False,
        observedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (out/'native-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,compiled=True,baselineNativeSha256=CORE_SHA,outputNativeSha256=payloads[CORE]['sha256'],allFourHooksPreserved=True,apkBuilt=False)))

if __name__=='__main__':main()
