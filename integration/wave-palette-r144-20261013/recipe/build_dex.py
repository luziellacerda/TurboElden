"""Assemble only the twelve opacity constants in the real R143 Wave class."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,zipfile
from common import *
TYPE='Lorg/emulationstation/frontend/station/StationWaveBackground;'
REL='org/emulationstation/frontend/station/StationWaveBackground.smali'
METHOD='.method private updatePalette(I)V'
TOOLS={'java':'1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406','javac':'9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549','apktool':'dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423'}
def norm(raw):return raw.decode('utf-8').replace('\r\n','\n')
def method_span(t):
 a=t.index(METHOD);return a,t.index('.end method',a)+len('.end method')
def replace(raw,pairs):
 t=norm(raw);a,b=method_span(t);counts={old:0 for old in pairs}
 def f(m):
  value=int(m[2],16)
  if value not in pairs:return m[0]
  counts[value]+=1;return m[1]+hex(pairs[value])
 changed=re.sub(r'(\bconst v\d+, )(0x[0-9a-f]+)',f,t[a:b]);need(all(v==1 for v in counts.values()),'Exactly twelve unique palette constants required')
 return t[:a]+changed+t[b:]
def class_maps(p):return {'L'+f.relative_to(p).as_posix()[:-6]+';':digest(f.read_bytes()) for f in p.rglob('*.smali')}
def main():
 p=argparse.ArgumentParser();
 for n in ['base','jdk-bin','apktool','out']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--source-commit',required=True);a=p.parse_args();pins=verify_commit(a.source_commit)
 need(sha(a.base)==BASE and a.base.stat().st_size==BASE_BYTES,'Exact R143 donor required')
 toolpaths={'java':a.jdk_bin/'java.exe','javac':a.jdk_bin/'javac.exe','apktool':a.apktool};need({k:sha(v) for k,v in toolpaths.items()}==TOOLS,'Exact toolchain required')
 with zipfile.ZipFile(a.base) as z:
  need(entry_sha(z,PARTITION)==DEX and entry_sha(z,'classes35.dex')==PRESERVED_DEX35 and entry_sha(z,CAROUSEL)==CAROUSEL_SHA and entry_sha(z,'lib/arm64-v8a/libstation_retroarch.so')==RETRO,'Exact current visual/gameplay bindings required')
  retained={n:entry_sha(z,n) for n in sorted(ROOT_DEX-{PARTITION})}
 out=isolated(a.out);out.mkdir(parents=True);tools=out/'tools';tools.mkdir();sources=[ROOT/'recipe'/n for n in ['DecodeDolphinPartition.java','VerifyScopedPartition.java','AssembleScopedPartition.java']]
 run([toolpaths['javac'],'-encoding','UTF-8','--release','17','-cp',a.apktool,'-d',tools,*sources])
 cp=str(tools)+';'+str(a.apktool);java=[toolpaths['java'],'-cp',cp]
 donor=out/'donor-smali';run(java+['DecodeDolphinPartition',a.base,PARTITION,DEX,donor])
 final=out/'patched-smali';shutil.copytree(donor,final)
 evidence=read(ROOT/'java/evidence/java-source-preservation.json');need(evidence['passed'] and evidence['changedArgbConstants']==12 and evidence['rgbBitsPreserved'] and not evidence['roomActivityModified'],'Online room brightness-only proof required')
 pairs={int(k,16):int(v,16) for k,v in evidence['replacements'].items()};need(len(pairs)==12 and len(set(pairs.values()))==12 and all((k&0xffffff)==(v&0xffffff) and v>>24>k>>24 for k,v in pairs.items()),'Only ARGB opacity increase permitted')
 raw=(donor/REL).read_bytes();patched=replace(raw,pairs);need(replace(patched.encode(),{v:k for k,v in pairs.items()})==norm(raw),'Inverse must recover entire original Wave class')
 (final/REL).write_bytes(patched.encode('utf-8'))
 scope=out/'scope.properties';scope.write_text('schema=station.wave-palette.scoped-types.r144.v1\npartition='+PARTITION+'\ndonorSha256='+DEX+'\nfamilies='+TYPE+'\noriginalAllowed='+TYPE+'\nfinalAllowed='+TYPE+'\n',encoding='utf-8')
 output=out/PARTITION;assembled=run(java+['AssembleScopedPartition',a.base,PARTITION,DEX,final,output,scope])
 container=out/'final-container.apk'
 with zipfile.ZipFile(container,'w',zipfile.ZIP_STORED) as z:z.writestr(PARTITION,output.read_bytes())
 actual=out/'final-smali';run(java+['DecodeDolphinPartition',container,PARTITION,sha(output),actual])
 preservedProof=run(java+['VerifyScopedPartition',a.base,PARTITION,DEX,actual,scope])
 before,after=class_maps(donor),class_maps(actual);need(len(before)==len(after)==272 and set(before)==set(after) and {n for n in before if before[n]!=after[n]}=={TYPE},'No other class may change')
 need(replace((actual/REL).read_bytes(),{v:k for k,v in pairs.items()})==norm(raw),'Postassembly inverse must recover all original Wave instructions and metadata')
 retainedClasses={n:h for n,h in before.items() if n!=TYPE};need({n:after[n] for n in retainedClasses}==retainedClasses,'All 271 unrelated classes byte exact')
 need(verify_commit(a.source_commit)==pins and {k:sha(v) for k,v in toolpaths.items()}==TOOLS,'Frozen sources/tools changed')
 receipt=dict(schema='station.r144.wave-palette.dex.v1',passed=True,compiled=True,sourceCommit=a.source_commit,sourceFiles=pins,baselineApkSha256=BASE,baselineDexSha256=DEX,outputDexSha256=sha(output),preservedDex35Sha256=PRESERVED_DEX35,preservedDexSha256=retained,inputSha256=TOOLS,originalClassCount=272,finalClassCount=272,unchangedClasses=271,baselineClassSha256=before,outputClassSha256=after,unchangedClassSha256=retainedClasses,unrelatedClassesByteIdentical=True,inversePassed=True,modifiedClasses=[TYPE],modifiedMethods=['updatePalette(I)V'],changedArgbConstants=12,rgbBitsPreserved=True,geometryAndSchedulingUnchanged=True,addedClasses=[],removedClasses=[],addedMethods=[],assemblyProof=assembled,preservationProof=preservedProof,testsPackaged=False,sdkOrDependenciesPackaged=False,**state_fields())
 (out/'dex-compilation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'revision':'R144','unchangedClasses':271,'modifiedOpacityConstants':12,'outputDexSha256':receipt['outputDexSha256']}))
if __name__=='__main__':main()
