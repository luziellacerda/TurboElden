"""Assemble the exact R144 partitions with ten background-colour literals only.

Historical Java files are reference material. Production copies every actual
donor smali class and changes only the fixed class/method/value allowlist. A
post-assembly decode and inverse must recover the complete original classes.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import zipfile
from common import *

TOOLS = {'java': '1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406',
         'javac': '9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549',
         'apktool': 'dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423'}
TOP, BOTTOM = '0xff287eb5', '0xff5daede'
# Exact class names, exact method descriptors, old/new values and occurrence
# counts are fixed here in addition to the reviewed/frozen declaration.
EXPECTED = {
 'classes28.dex': {
  'Lorg/emulationstation/frontend/station/StationWaveBackground;': [('.method protected onDraw(Landroid/graphics/Canvas;)V','0xff050a15',TOP)],
  'Lorg/emulationstation/frontend/station/StationDownloadPanel;': [('.method protected onCreate(Landroid/os/Bundle;)V','0xff07111e',TOP)],
  'Lorg/emulationstation/frontend/station/StationDownloadUi;': [('.method static messageDialog(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/app/Dialog;','0xff0d1a2a',TOP)]},
 'classes35.dex': {
  'Lorg/emulationstation/frontend/netplay/StationHyperspaceView;': [('.method private renderBackground(II)Landroid/graphics/Bitmap;','0xff02040a',TOP),('.method private renderBackground(II)Landroid/graphics/Bitmap;','0xff071421',BOTTOM),('.method protected onDraw(Landroid/graphics/Canvas;)V','0xff02040a',TOP)],
  'Lorg/emulationstation/frontend/netplay/StationRoomsActivity;': [('.method private build()V','0xff02040a',TOP),('.method private applyGraphics()V','0xff02040a',TOP)]},
 'classes40.dex': {
  'Lorg/emulationstation/frontend/sony/Ps3Activity;': [('.method private showSettings()V','0xff081017',TOP)],
  'Lorg/emulationstation/frontend/sony/Ps4Activity;': [('.method private showSettings()V','0xff081017',TOP)]}}
COUNTS = {'classes28.dex':272, 'classes35.dex':608, 'classes40.dex':129}


def run_tool(command):
    import subprocess
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, 'Scoped DEX tool rejected the operation: '+result.stderr[-1400:])
    return result.stdout.strip()


def class_path(directory, kind):
    return Path(directory) / (kind[1:-1]+'.smali')


def class_maps(directory):
    result={}
    for path in sorted(Path(directory).rglob('*.smali')):
        need(not path.is_symlink(),'Symbolic smali refused')
        kind='L'+path.relative_to(directory).as_posix()[:-6]+';'
        need(kind not in result,'Duplicate class')
        result[kind]=digest(path.read_bytes())
    return result


def method_span(text, signature):
    needle=signature+('\r\n' if '\r\n' in text else '\n')
    need(text.count(needle)==1,'Exact unique method descriptor required: '+signature)
    start=text.index(needle)
    return start,text.index('.end method',start)+len('.end method')


def rewrite(raw, changes, inverse=False):
    text=raw.decode('utf-8')
    for signature,old,new in (reversed(changes) if inverse else changes):
        before,after=(new,old) if inverse else (old,new)
        start,end=method_span(text,signature);count=0
        def replace(match):
            nonlocal count
            if int(match[2],16)&0xffffffff != int(before,16):return match[0]
            count+=1
            value=int(after,16); signed=value-(1<<32) if value>=1<<31 else value
            return match[1]+hex(signed)
        body=re.sub(r'(\bconst\s+[vp]\d+,\s+)(-?0x[0-9a-f]+)',replace,text[start:end])
        need(count==1,'Exactly one full ARGB literal in the allowed method required')
        text=text[:start]+body+text[end:]
    return text.encode('utf-8')


def method_hashes(raw, signatures):
    text=raw.decode('utf-8');result={}
    for signature in signatures:
        start,end=method_span(text,signature)
        result[signature]=digest(text[start:end].encode('utf-8'))
    return result


def reviewed_plan():
    value=read(ROOT/'evidence/java-background-scope.json')
    need(value.get('schema')=='station.r145.sky-blue.background.scope.v1' and
         value.get('baselineApkSha256')==BASE and value.get('onlyLiteralReplacement') is True and
         value.get('wholeClassSmaliSourceInversePassed') is True and
         value.get('postassemblyMustRecoverExactDonor') is True and
         value.get('noNewFields') is value.get('noNewMethods') is value.get('noNewClasses') is True and
         value.get('networkAndGameplayChanges') is False and value.get('changedConstantCount')==10 and
         set(value.get('partitions',{}))==PARTITIONS,'Frozen ten-literal visual scope required')
    for partition,families in EXPECTED.items():
        record=value['partitions'][partition]
        need(record['classCount']==COUNTS[partition] and record['donorDexSha256']==DEX_BASE[partition] and
             set(record['modifiedClasses'])==set(families),'Exact reviewed classes and original counts required')
        need(record['modifiedMethods']=={kind:list(dict.fromkeys(row[0] for row in rows)) for kind,rows in families.items()},
             'Method allowlist differs from the closed visual scope')
        expected={(kind,signature,old,new,1) for kind,rows in families.items() for signature,old,new in rows}
        actual={(row['classType'],row['method'],row['oldArgb'],row['newArgb'],row['expectedOccurrences'])
                for row in record['constantChanges']}
        need(actual==expected and len(record['constantChanges'])==len(expected),'Literal occurrence allowlist changed')
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base','jdk-bin','apktool','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--source-commit',required=True)
    args=parser.parse_args(); pins=verify_commit(args.source_commit); declaration=reviewed_plan()
    need(args.base.is_file() and not args.base.is_symlink() and args.base.stat().st_size==BASE_BYTES and sha(args.base)==BASE,
         'Exact signed R144 APK donor required')
    paths={'java':args.jdk_bin/'java.exe','javac':args.jdk_bin/'javac.exe','apktool':args.apktool}
    need({name:sha(path) for name,path in paths.items()}==TOOLS,'Pinned JDK17 and apktool 3.0.3 required')
    with zipfile.ZipFile(args.base) as archive:
        need({name:entry_sha(archive,name) for name in PARTITIONS}==DEX_BASE and
             entry_sha(archive,CAROUSEL)==CAROUSEL_SHA and entry_sha(archive,'lib/arm64-v8a/libstation_retroarch.so')==RETRO,
             'Current visual/runtime bindings required')
        retained={name:entry_sha(archive,name) for name in sorted(ROOT_DEX-PARTITIONS)}
    output=isolated(args.out);output.mkdir(parents=True);tools=output/'tools';tools.mkdir()
    tool_sources=[ROOT/'recipe'/name for name in ('DecodeDolphinPartition.java','VerifyScopedPartition.java','AssembleScopedPartition.java')]
    run_tool([paths['javac'],'-encoding','UTF-8','--release','17','-cp',args.apktool,'-d',tools,*tool_sources])
    java=[paths['java'],'-cp',str(tools)+';'+str(args.apktool)]
    scopes={};payloads={}
    for partition in sorted(PARTITIONS):
        wanted=declaration['partitions'][partition];root=output/partition.replace('.dex','');root.mkdir()
        donor=root/'donor-smali';run_tool(java+['DecodeDolphinPartition',args.base,partition,DEX_BASE[partition],donor])
        before=class_maps(donor)
        need(before==wanted['originalClassSha256'] and len(before)==COUNTS[partition],
             'The complete donor class projection must match the reviewed actual R144 partition')
        patched=root/'patched-smali';shutil.copytree(donor,patched)
        for kind,changes in EXPECTED[partition].items():
            raw=class_path(donor,kind).read_bytes()
            need(digest(raw)==wanted['baselineClassSha256'][kind] and
                 method_hashes(raw,wanted['modifiedMethods'][kind])==wanted['methodBaselineSha256'][kind],
                 'Exact whole class and method baseline required')
            result=rewrite(raw,changes)
            need(rewrite(result,changes,inverse=True)==raw,'Preassembly inverse must recover the whole donor class')
            frozen=ROOT/'evidence/proposed-smali'/partition/(kind[1:-1]+'.smali')
            need(result==frozen.read_bytes() and digest(result)==wanted['plannedOutputClassSha256'][kind],
                 'Generated literal patch differs from the frozen seven real smali classes')
            class_path(patched,kind).write_bytes(result)
        changed=set(wanted['modifiedClasses']);scope=root/'scope.properties'
        types='|'.join(sorted(changed))
        scope.write_text('schema=station.sky-blue.scoped-types.r145.v1\npartition='+partition+'\ndonorSha256='+DEX_BASE[partition]+
                         '\nfamilies='+types+'\noriginalAllowed='+types+'\nfinalAllowed='+types+'\n',encoding='utf-8')
        artifact=output/partition
        assembly=run_tool(java+['AssembleScopedPartition',args.base,partition,DEX_BASE[partition],patched,artifact,scope])
        container=root/'final-container.apk'
        with zipfile.ZipFile(container,'w',zipfile.ZIP_STORED) as archive:archive.writestr(partition,artifact.read_bytes())
        actual=root/'final-smali';run_tool(java+['DecodeDolphinPartition',container,partition,sha(artifact),actual])
        preservation=run_tool(java+['VerifyScopedPartition',args.base,partition,DEX_BASE[partition],actual,scope])
        after=class_maps(actual)
        need(set(before)==set(after) and len(after)==COUNTS[partition] and
             {kind for kind in before if before[kind]!=after[kind]}==changed,'No unrelated class, method or metadata may change')
        inverse_classes={};inverse_methods={}
        for kind,changes in EXPECTED[partition].items():
            real=class_path(actual,kind).read_bytes();raw=class_path(donor,kind).read_bytes()
            need(digest(real)==wanted['plannedOutputClassSha256'][kind],
                 'Assembled class differs from exact frozen literal-only projection')
            inverse=rewrite(real,changes,inverse=True)
            need(inverse==raw,'Postassembly inverse must recover every original instruction, field, annotation and label')
            inverse_classes[kind]=digest(inverse)
            inverse_methods[kind]=method_hashes(inverse,wanted['modifiedMethods'][kind])
        need(inverse_classes==wanted['baselineClassSha256'] and inverse_methods==wanted['methodBaselineSha256'],
             'Complete class and target method inverse checksums differ')
        unrelated={kind:before[kind] for kind in before if kind not in changed}
        need({kind:after[kind] for kind in unrelated}==unrelated,'All nonchanged classes must remain byte exact')
        scopes[partition]=dict(baselineDexSha256=DEX_BASE[partition],outputDexSha256=sha(artifact),
              originalClassCount=len(before),finalClassCount=len(after),unchangedClasses=len(unrelated),
              modifiedClasses=wanted['modifiedClasses'],modifiedMethods=wanted['modifiedMethods'],constantChanges=wanted['constantChanges'],
              methodBaselineSha256=wanted['methodBaselineSha256'],methodInverseSha256=inverse_methods,
              inverseClassSha256=inverse_classes,onlyLiteralReplacement=True,inverseWholeClassPassed=True,
              postassemblyInversePassed=True,unrelatedClassesByteIdentical=True,unrelatedMethodsPreserved=True,
              staticInitializersPreserved=True,baselineClassSha256=before,outputClassSha256=after,unchangedClassSha256=unrelated,
              addedClasses=[],removedClasses=[],addedMethods=[],removedMethods=[],newFields=[],
              assemblyProof=assembly,preservationProof=preservation)
        payloads[partition]=dict(path=str(artifact.resolve()),bytes=artifact.stat().st_size,sha256=sha(artifact))
    need(sum(record['originalClassCount'] for record in scopes.values())==1009 and
         sum(record['unchangedClasses'] for record in scopes.values())==1002,'Account for all 1009 classes and 1002 unchanged classes')
    need(verify_commit(args.source_commit)==pins and {name:sha(path) for name,path in paths.items()}==TOOLS,
         'Frozen source or toolchain changed during assembly')
    with zipfile.ZipFile(args.base) as archive:
        need({name:entry_sha(archive,name) for name in retained}==retained,'Original retained partitions changed')
    receipt=dict(schema='station.r145.sky-blue-waves.dex.v1',passed=True,compiled=True,
                 sourceCommit=args.source_commit,sourceFiles=pins,baselineApkSha256=BASE,
                 scopeDeclarationSha256=sha(ROOT/'evidence/java-background-scope.json'),
                 productionMethodStrategy='donor-smali-literals-only',payloads=payloads,scopes=scopes,
                 preservedDexSha256=retained,inversePassed=True,inverseWholeClassPassed=True,
                 postAssemblyInversePassed=True,unrelatedMethodsPreserved=True,
                 gameplayAndNetworkLogicPreserved=True,newFields=[],newMethods=[],newClasses=[],
                 originalClassCount=1009,unchangedClasses=1002,changedClasses=7,changedMethods=9,changedArgbConstants=10,
                 geometryAndSchedulingUnchanged=True,testsPackaged=False,sdkOrDependenciesPackaged=False,
                 historicalJavaRecompiledOrRestored=False,inputSha256=TOOLS,**state_fields())
    (output/'dex-compilation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,revision='R145',classes=1009,unchangedClasses=1002,
                         changedClasses=7,changedArgbConstants=10,payloads={name:value['sha256'] for name,value in payloads.items()})))


if __name__=='__main__':main()
