"""Compile three isolated R129 demonstration payloads, never an APK.

Uses the exact signed R128 donor. The signed catalogue, genuine downloads,
authentication, graphics and all existing emulator command routes are preserved.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, shutil, struct, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PSX=REPO/'integration/psx-online/recipe'
R124=REPO/'versions/station-video-room-footer-r124-20261011'
APK_SHA='0189527c7537845562a2be4be15c0fab976c85f4f9c7f8ab884915c8bc3052dc'
APK_BYTES=2234617901
APKTOOL_SHA='dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423'
FRONTEND='Lorg/emulationstation/frontend/station/StationFrontend;'
JAVA_PARENT='java/org/emulationstation/frontend/offline/'
SONY_JAVA=JAVA_PARENT+'StationSonyOfflineActivity.java'
POLICY_JAVA=JAVA_PARENT+'StationSonyOfflinePolicy.java'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda:stream.read(1048576),b''):h.update(part)
    return h.hexdigest()

def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def source_map():
    return {p.relative_to(ROOT).as_posix():sha(p) for directory in ('java','recipe')
            for p in sorted((ROOT/directory).rglob('*')) if p.is_file() and p.suffix in ('.java','.py')}

def run(command,out,label):
    result=subprocess.run(list(map(str,command)),capture_output=True,text=True,
        encoding='utf-8',errors='replace',env={**os.environ,'TMP':str(out/'temp'),'TEMP':str(out/'temp')})
    (out/(label+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(label+' failed; inspect isolated log')
    return result.stdout.strip()

def class_count(path):
    raw=path.read_bytes()
    if not raw.startswith(b'dex\n'):raise ValueError('Invalid DEX')
    return struct.unpack_from('<I',raw,96)[0]

def container(path,name,payload):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_STORED) as archive:archive.writestr(name,payload.read_bytes())

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('donor','jdk','android-jar','d8-jar','apktool','parent-offline','ndk','native-inputs','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    a=parser.parse_args()
    a.donor=a.donor.resolve(strict=True);a.parent_offline=a.parent_offline.resolve(strict=True);a.out=a.out.resolve()
    if a.out.exists() or ROOT in a.out.parents:raise ValueError('Use a new separate output directory')
    if sha(a.donor)!=APK_SHA or a.donor.stat().st_size!=APK_BYTES:raise ValueError('Exact signed R128 donor required')
    if sha(a.apktool)!=APKTOOL_SHA:raise ValueError('Exact apktool 3.0.3 required')
    frozen=source_map()
    parent_sources={name:sha(a.parent_offline/name) for name in (SONY_JAVA,POLICY_JAVA)}
    # Pin all productive parent sources used directly or by its native transform.
    parent_inputs={name:sha(a.parent_offline/name) for name in
        (SONY_JAVA,POLICY_JAVA,'recipe/patch_native.py','native/offline_routes.h')}
    a.out.mkdir(parents=True);(a.out/'temp').mkdir()
    java=a.jdk/'bin/java.exe';javac=a.jdk/'bin/javac.exe'
    with zipfile.ZipFile(a.donor) as archive:
        original28=archive.read('classes28.dex');original39=archive.read('classes39.dex')
        preserved={name:hashlib.sha256(archive.read(name)).hexdigest() for name in
            ('AndroidManifest.xml','classes6.dex','classes35.dex')}
        baseline_native_sha=hashlib.sha256(archive.read('lib/arm64-v8a/libturbo_carousel.so')).hexdigest()
    dex28_sha=hashlib.sha256(original28).hexdigest();dex39_sha=hashlib.sha256(original39).hexdigest()

    tools=a.out/'tools';tools.mkdir()
    helpers=[PSX/name for name in ('DecodeDolphinPartition.java','AssembleDolphinPartition.java','VerifyOptinPartition.java')]
    run([javac,'-encoding','UTF-8','--release','17','-cp',a.apktool,'-d',tools,*helpers],a.out,'smali-tools')
    cp=str(tools)+os.pathsep+str(a.apktool)
    smali=a.out/'smali28'
    run([java,'-cp',cp,'DecodeDolphinPartition',a.donor,'classes28.dex',dex28_sha,smali],a.out,'decode28')
    target_relative=Path('org/emulationstation/frontend/station/StationFrontend.smali')
    target=smali/target_relative;original=target.read_bytes()
    frontend=module(ROOT/'recipe/patch_frontend.py','demo_frontend')
    patched=frontend.patch(original);target.write_bytes(patched)
    frontend.verify(original,patched)
    expected='verifiedClasses=271 unchanged=270 changed=1 donorSHA='+dex28_sha
    verified=run([java,'-cp',cp,'VerifyOptinPartition',a.donor,'classes28.dex',dex28_sha,smali,FRONTEND],a.out,'preserve28')
    if verified!=expected:raise ValueError('Original partition preservation mismatch')
    dex28=a.out/'classes28.dex'
    run([java,'-cp',cp,'AssembleDolphinPartition',smali,dex28],a.out,'assemble28')
    if class_count(dex28)!=271:raise ValueError('Client class set changed')
    fixture=a.out/'partition-container.zip';container(fixture,'classes28.dex',dex28)
    actual=a.out/'smali28-final'
    run([java,'-cp',cp,'DecodeDolphinPartition',fixture,'classes28.dex',sha(dex28),actual],a.out,'decode28-final')
    verified=run([java,'-cp',cp,'VerifyOptinPartition',a.donor,'classes28.dex',dex28_sha,actual,FRONTEND],a.out,'preserve28-final')
    if verified!=expected:raise ValueError('Actual DEX changed an unrelated class')
    check=frontend.verify_actual(original,(actual/target_relative).read_bytes())
    check.update({'donorSha256':dex28_sha,'sha256':sha(dex28),'classCount':271,
                  'unchangedClasses':270,'changedType':FRONTEND,'factoryPreserved':True})
    write(a.out/'dex28-receipt.json',check);fixture.unlink()

    # Compile no ABI fixtures and no foreign app classes into the separate partition.
    sources=a.out/'bridge-sources';sony=sources/SONY_JAVA;sony.parent.mkdir(parents=True)
    transform=module(ROOT/'recipe/patch_sony_activity.py','demo_sony')
    sony.write_bytes(transform.patch((a.parent_offline/SONY_JAVA).read_bytes()))
    policy=sources/POLICY_JAVA;shutil.copyfile(a.parent_offline/POLICY_JAVA,policy)
    if sha(policy)!=parent_sources[POLICY_JAVA]:raise ValueError('Sony policy copy changed')
    classes=a.out/'bridge-classes';classes.mkdir()
    java_sources=[*sorted((ROOT/'java').rglob('*.java')),sony,policy]
    run([javac,'-encoding','UTF-8','--release','8','-proc:none','-cp',a.android_jar,'-d',classes,*java_sources],a.out,'bridge-javac')
    jar=a.out/'bridge.jar'
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_STORED) as archive:
        for path in sorted(classes.rglob('*.class')):
            name=path.relative_to(classes).as_posix()
            allowed=name.startswith('org/emulationstation/frontend/offline/') or re.fullmatch(
                r'org/emulationstation/frontend/station/StationLocalSonyDemos(?:\$[^/]*)?\.class',name)
            if not allowed:raise ValueError('Unexpected bridge class: '+name)
            archive.writestr(zipfile.ZipInfo(name,(1980,1,1,0,0,0)),path.read_bytes())
    dex=a.out/'bridge-dex';dex.mkdir()
    run([java,'-cp',a.d8_jar,'com.android.tools.r8.D8','--release','--min-api','28','--lib',a.android_jar,'--output',dex,jar],a.out,'bridge-d8')
    if list(dex.glob('*.dex'))!=[dex/'classes.dex']:raise ValueError('Unexpected partition count')
    dex39=a.out/'classes39.dex';shutil.copyfile(dex/'classes.dex',dex39)
    run([java,'-cp',cp,'DecodeDolphinPartition',a.donor,'classes39.dex',dex39_sha,a.out/'smali39-parent'],a.out,'decode39-parent')
    container(fixture,'classes39.dex',dex39)
    run([java,'-cp',cp,'DecodeDolphinPartition',fixture,'classes39.dex',sha(dex39),a.out/'smali39-final'],a.out,'decode39-final')
    fixture.unlink()
    def class_set(directory):return {p.relative_to(directory).as_posix() for p in directory.rglob('*.smali')}
    parent_classes=class_set(a.out/'smali39-parent');new_classes=class_set(a.out/'smali39-final')
    if not parent_classes<=new_classes:raise ValueError('An existing offline class disappeared')
    for name in new_classes:
        if not (name.startswith('org/emulationstation/frontend/offline/') or re.fullmatch(
            r'org/emulationstation/frontend/station/StationLocalSonyDemos(?:\$[^/]*)?\.smali',name)):
            raise ValueError('Foreign class in actual DEX39')
    write(a.out/'dex39-receipt.json',{'donorSha256':dex39_sha,'sha256':sha(dex39),
        'parentClassesRetained':True,'onlyOfflineAndExactDemoNamespace':True,
        'classCount':class_count(dex39),'policySourceIdentical':True,
        'compileOnlyFixturesPackaged':False,'backgroundLoopsAdded':False,
        'demoGuardBeforeEmulatorLookup':True,'externalEmulatorsEmbedded':False})

    # Reproduce the exact R128 carousel first, then add one Sony-artwork fallback.
    inventory=json.loads((R124/'CAROUSEL-INPUT-MANIFEST.json').read_text(encoding='utf-8'))
    resolved={}
    for name,digest in inventory.items():
        public=R124/'native'/name;path=public if public.is_file() else a.native_inputs/name
        if not path.is_file() or sha(path)!=digest:raise ValueError('Native input changed: '+name)
        shadow=a.native_inputs/name
        if shadow.is_file() and sha(shadow)!=digest:raise ValueError('Native shadow changed: '+name)
        resolved[name]=path
    parent_native=module(a.parent_offline/'recipe/patch_native.py','r128_native')
    original_native=parent_native.patch(resolved['d0/native_carousel.cpp'].read_bytes())
    native_out=a.out/'native';native_out.mkdir();native_source=native_out/'native_carousel.cpp'
    native_source.write_bytes(original_native)
    common=[a.ndk/'clang++.exe','--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2',
        '-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti',
        '-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so']
    includes=['-I',a.parent_offline/'native','-I',R124/'native/d0','-I',a.native_inputs/'d0',
        '-I',a.native_inputs/'d2','-I',a.native_inputs/'d1']
    objects=[resolved[n] for n in ('d1/video720_posters.o','d3/collection_previews.o','d4/lottie_frames.o')]
    tail=['-L',a.native_inputs/'d1','-lc','-ldl','-llog',resolved['d5/installed_art.o']]
    last=[resolved[n] for n in ('d6/collection_previews.o','d7/collection_previews.o','d8/collection_previews.o')]
    baseline=native_out/'baseline-carousel.so'
    run(common+includes+[native_source]+objects+tail+['-o',baseline]+last,a.out,'native-r128-baseline')
    if sha(baseline)!=baseline_native_sha:raise ValueError('R128 native baseline not byte identical')
    native_patch=module(ROOT/'recipe/patch_demo_native.py','demo_native')
    changed_native=native_patch.patch(original_native);native_source.write_bytes(changed_native)
    native_check=native_patch.verify(original_native,changed_native)
    carousel=a.out/'libturbo_carousel.so'
    run(common+includes+[native_source]+objects+tail+['-o',carousel]+last,a.out,'native-demo-art')
    def exports(path):return {line.split()[-1] for line in run([a.ndk/'llvm-nm.exe','--dynamic','--defined-only',path],a.out,path.stem+'-exports').splitlines() if len(line.split())>=3}
    if exports(baseline)!=exports(carousel):raise ValueError('Native public ABI changed')
    headers=run([a.ndk/'llvm-readelf.exe','-lW',carousel],a.out,'native-loads')
    aligns=re.findall(r'^\s*LOAD\s+.*\s(0x[0-9a-fA-F]+)\s*$',headers,re.M)
    if not aligns or not all(int(v,16)>=16384 for v in aligns):raise ValueError('Native LOAD below 16 KiB')
    if any(sha(path)!=inventory[name] for name,path in resolved.items()):raise ValueError('Native input changed during compilation')
    native_check.update({'nativeBaselineSha256':baseline_native_sha,'baselineNativeByteIdentical':True,
        'sha256':sha(carousel),'exportSetExactlyPreserved':True,'loadAlignment16KiB':True,
        'productiveInputSha256':inventory,'staticArtworkFallbackSonyOnly':True})
    write(a.out/'native-receipt.json',native_check);baseline.unlink()

    if frozen!=source_map():raise ValueError('Demo source changed during build')
    if any(sha(a.parent_offline/name)!=digest for name,digest in parent_inputs.items()):raise ValueError('R128 parent source changed during build')
    payloads={name:{'sha256':sha(a.out/name),'bytes':(a.out/name).stat().st_size}
              for name in ('classes28.dex','classes39.dex','libturbo_carousel.so')}
    receipt={'schemaVersion':1,'passed':True,'donorApkSha256':APK_SHA,
        'sourceSha256':frozen,'parentSourceSha256':parent_sources,'parentNativeSourceInputs':parent_inputs,
        'payloads':payloads,'nativeBaselineSha256':baseline_native_sha,'baselineNativeByteIdentical':True,
        'preservedParentPayloadSha256':preserved,'offlineOnly':True,'localDisplayOnly':True,
        'signedCatalogChanged':False,'realDownloadsChanged':False,'graphicsRenderMethodsChanged':False,
        'existingOnlineCodePreserved':True,'sharedDexRequiresNewRuntimeIdentities':True,
        'apkProduced':False,'signed':False,'installed':False,'physicalValidation':False}
    write(a.out/'demo-payloads.json',receipt);print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
