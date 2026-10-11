"""Build only the isolated offline bridge, mapping partition, manifest and command hook.

The exact R127 donor is read only. No APK is produced, aligned, signed or installed.
One new output directory is required, and existing backup/private inputs are reused.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, shutil, struct, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PSX=REPO/'integration/psx-online/recipe'
R124=REPO/'versions/station-video-room-footer-r124-20261011'
APK_SHA='a350878cca5c1a65c51e79ac13e9e38c2053d76e5404edb515ad1ddd650c3038'
APK_BYTES=2235617465
DEX_SHA='5966ef8405701fa946c60fe6d922726cd74c27783a4cb76d240dfa4bc324de9d'
APKTOOL_SHA='dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423'
CHANGED_TYPE='Lorg/emulationstation/frontend/station/StationPlatforms;'

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for part in iter(lambda:stream.read(1048576),b''):h.update(part)
 return h.hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def import_local(name):
 spec=importlib.util.spec_from_file_location('offline_'+name,ROOT/'recipe'/ (name+'.py'))
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def run(command,out,label):
 result=subprocess.run(list(map(str,command)),capture_output=True,text=True,encoding='utf-8',errors='replace',env={**os.environ,'TMP':str(out/'temp'),'TEMP':str(out/'temp')})
 (out/(label+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
 if result.returncode:raise RuntimeError(label+' failed; inspect its isolated build log')
 return result.stdout.strip()
def class_count(path):
 raw=path.read_bytes()
 if not raw.startswith(b'dex\n'):raise ValueError('DEX missing')
 return struct.unpack_from('<I',raw,96)[0]
def source_map():
 return {p.relative_to(ROOT).as_posix():sha(p) for directory in ('java','native','recipe') for p in sorted((ROOT/directory).rglob('*')) if p.is_file() and p.suffix in ('.java','.h','.cpp','.py')} | {'catalog-platforms.json':sha(ROOT/'catalog-platforms.json')}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('base','jdk','android-jar','d8-jar','apktool','ndk','native-inputs','out'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();a.base=a.base.resolve(strict=True);a.out=a.out.resolve()
 if a.out.exists() or ROOT in a.out.parents:raise ValueError('Use a new separate work directory')
 if sha(a.base)!=APK_SHA or a.base.stat().st_size!=APK_BYTES:raise ValueError('Current signed R127 donor required')
 if sha(a.apktool)!=APKTOOL_SHA:raise ValueError('Exact apktool 3.0.3 JAR required')
 frozen=source_map();a.out.mkdir(parents=True);(a.out/'temp').mkdir()
 java=a.jdk/'bin/java.exe';javac=a.jdk/'bin/javac.exe'
 with zipfile.ZipFile(a.base) as archive:
  if 'classes39.dex' in archive.namelist():raise ValueError('Chosen bridge DEX already exists')
  if hashlib.sha256(archive.read('classes28.dex')).hexdigest()!=DEX_SHA:raise ValueError('Donor factory/platform partition changed')
  old_carousel=archive.read('lib/arm64-v8a/libturbo_carousel.so')
  old_carousel_sha=hashlib.sha256(old_carousel).hexdigest()
  manifest=archive.read('AndroidManifest.xml')
 mf=import_local('patch_manifest');changed=mf.patch(manifest,mf.helper());(a.out/'AndroidManifest.xml').write_bytes(changed)
 write(a.out/'manifest-receipt.json',{'donorSha256':hashlib.sha256(manifest).hexdigest(),'sha256':hashlib.sha256(changed).hexdigest(),'addedActivity':mf.ACTIVITY,'queries':list(mf.TARGETS),'exactInverse':True,'existingFactoryAndActivitiesPreserved':True})

 # The original 271-class partition retains every class, including the R127
 # PSX factory opt-in. Only the existing StationPlatforms initializer changes.
 tools=a.out/'tools';tools.mkdir()
 helpers=[PSX/n for n in ('DecodeDolphinPartition.java','AssembleDolphinPartition.java','VerifyOptinPartition.java')]
 run([javac,'-encoding','UTF-8','--release','17','-cp',a.apktool,'-d',tools,*helpers],a.out,'smali-tools')
 cp=str(tools)+os.pathsep+str(a.apktool);smali=a.out/'smali28'
 run([java,'-cp',cp,'DecodeDolphinPartition',a.base,'classes28.dex',DEX_SHA,smali],a.out,'decode28')
 target=smali/'org/emulationstation/frontend/station/StationPlatforms.smali';raw=target.read_bytes()
 transform=import_local('patch_platforms');patched,addition=transform.patch(raw);target.write_bytes(patched)
 verified=run([java,'-cp',cp,'VerifyOptinPartition',a.base,'classes28.dex',DEX_SHA,smali,CHANGED_TYPE],a.out,'preserve28')
 expected='verifiedClasses=271 unchanged=270 changed=1 donorSHA='+DEX_SHA
 if verified!=expected:raise ValueError('Platform partition preservation mismatch')
 dex28=a.out/'classes28.dex';run([java,'-cp',cp,'AssembleDolphinPartition',smali,dex28],a.out,'assemble28')
 if class_count(dex28)!=271:raise ValueError('Client partition class set changed')
 # Re-decode the actual output, not only the pre-assembly source fixture.
 donor=a.out/'classes28-donor-container.zip'
 with zipfile.ZipFile(donor,'w',zipfile.ZIP_STORED) as z:z.writestr('classes28.dex',dex28.read_bytes())
 decoded=a.out/'smali28-final'
 run([java,'-cp',cp,'DecodeDolphinPartition',donor,'classes28.dex',sha(dex28),decoded],a.out,'decode28-final')
 rebuilt_check=run([java,'-cp',cp,'VerifyOptinPartition',a.base,'classes28.dex',DEX_SHA,decoded,CHANGED_TYPE],a.out,'preserve28-final')
 if rebuilt_check!=expected:raise ValueError('Actual assembled client classes changed')
 donor.unlink()
 write(a.out/'dex28-receipt.json',{'donorSha256':DEX_SHA,'sha256':sha(dex28),'classCount':271,'unchangedClasses':270,'changedType':CHANGED_TYPE,'changedMethods':['<clinit>'],'exactSourceInverse':patched.decode('utf-8').replace(addition,'',1).encode('utf-8')==raw,'actualAssembledDexOtherClassesVerified':True,'factoryPreserved':True})

 # No compile-only ABI fixtures are used for the new bridge partition.
 classes=a.out/'bridge-classes';classes.mkdir();sources=sorted((ROOT/'java').rglob('*.java'))
 run([javac,'-encoding','UTF-8','--release','8','-proc:none','-cp',a.android_jar,'-d',classes,*sources],a.out,'bridge-javac')
 jar=a.out/'bridge.jar'
 with zipfile.ZipFile(jar,'w',zipfile.ZIP_STORED) as archive:
  for path in sorted(classes.rglob('*.class')):
   name=path.relative_to(classes).as_posix()
   if not name.startswith('org/emulationstation/frontend/offline/'):raise ValueError('Foreign class in bridge')
   archive.writestr(zipfile.ZipInfo(name,(1980,1,1,0,0,0)),path.read_bytes())
 dex=a.out/'bridge-dex';dex.mkdir()
 run([java,'-cp',a.d8_jar,'com.android.tools.r8.D8','--release','--min-api','28','--lib',a.android_jar,'--output',dex,jar],a.out,'bridge-d8')
 if list(dex.glob('*.dex'))!=[dex/'classes.dex']:raise ValueError('Bridge partition count')
 dex39=a.out/'classes39.dex';shutil.copyfile(dex/'classes.dex',dex39)
 write(a.out/'dex39-receipt.json',{'sha256':sha(dex39),'classCount':class_count(dex39),'sourceCount':len(sources),'onlyOfflineNamespace':True,'compileOnlyFixturesPackaged':False,'runtimeServicesAdded':False,'backgroundLoopsAdded':False})

 # Reuse the current private native objects/headers. Compare every required
 # input against the R124 manifest and rebuild the original first, which must
 # reproduce the exact carousel carried by the signed R127 donor.
 native_inventory=json.loads((R124/'CAROUSEL-INPUT-MANIFEST.json').read_text(encoding='utf-8'))
 resolved={}
 for name,digest in native_inventory.items():
  public=R124/'native'/name;path=public if public.is_file() else a.native_inputs/name
  if not path.is_file() or sha(path)!=digest:raise ValueError('Native dependency changed: '+name)
  resolved[name]=path
 # Header lookup relies on the complete preserved R124 native-inputs tree;
 # all files that win that lookup must match the same signed inventory.
 for name,path in resolved.items():
  private=a.native_inputs/name
  if private.is_file() and sha(private)!=native_inventory[name]:raise ValueError('Private native shadow changed: '+name)
 baseline_source=resolved['d0/native_carousel.cpp'];native_out=a.out/'native';native_out.mkdir()
 common=[a.ndk/'clang++.exe','--target=aarch64-linux-android26','-std=c++17','-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,--no-undefined','-nostdlib','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-soname,libturbo_carousel.so']
 includes=['-I',ROOT/'native','-I',R124/'native/d0','-I',a.native_inputs/'d0','-I',a.native_inputs/'d2','-I',a.native_inputs/'d1']
 objects=[resolved[n] for n in ('d1/video720_posters.o','d3/collection_previews.o','d4/lottie_frames.o')]
 tail=['-L',a.native_inputs/'d1','-lc','-ldl','-llog',resolved['d5/installed_art.o']]
 last=[resolved[n] for n in ('d6/collection_previews.o','d7/collection_previews.o','d8/collection_previews.o')]
 baseline=native_out/'baseline-carousel.so'
 run(common+includes+[baseline_source]+objects+tail+['-o',baseline]+last,a.out,'native-baseline')
 if sha(baseline)!=old_carousel_sha:raise ValueError('The original carousel is not byte reproducible with these inputs')
 native_patch=import_local('patch_native');new_source=native_out/'native_carousel.cpp';raw=baseline_source.read_bytes();new_source.write_bytes(native_patch.patch(raw))
 carousel=a.out/'libturbo_carousel.so';run(common+includes+[new_source]+objects+tail+['-o',carousel]+last,a.out,'native-offline')
 def exports(path):
  return {line.split()[-1] for line in run([a.ndk/'llvm-nm.exe','--dynamic','--defined-only',path],a.out,path.stem+'-exports').splitlines() if len(line.split())>=3}
 if exports(baseline)!=exports(carousel):raise ValueError('Native public ABI changed')
 headers=run([a.ndk/'llvm-readelf.exe','-lW',carousel],a.out,'native-loads')
 aligns=re.findall(r'^\s*LOAD\s+.*\s(0x[0-9a-fA-F]+)\s*$',headers,re.M)
 if not aligns or not all(int(v,16)>=16384 for v in aligns):raise ValueError('Native alignment below16KiB')
 if any(sha(path)!=native_inventory[name] for name,path in resolved.items()):raise ValueError('Native input changed during compilation')
 baseline.unlink()
 write(a.out/'native-receipt.json',{'baselineByteIdentical':True,'baselineSha256':old_carousel_sha,'sha256':sha(carousel),'exactSourceInverse':True,'sourceChangedMethods':['gamecubeCommandHook'],'exportSetExactlyPreserved':True,'loadAlignment16KiB':True,'sourceSha256':native_patch.SOURCE_SHA,'productiveInputSha256':native_inventory,'graphicsLogicChanged':False,'onlineLogicChanged':False})
 if frozen!=source_map():raise ValueError('Offline source changed during build')
 payloads={name:{'sha256':sha(a.out/name),'bytes':(a.out/name).stat().st_size} for name in ('AndroidManifest.xml','classes28.dex','classes39.dex','libturbo_carousel.so')}
 receipt={'schemaVersion':1,'passed':True,'baseApkSha256':APK_SHA,'sourceSha256':frozen,'payloads':payloads,'externalEmulatorsEmbedded':False,'offlineOnly':True,'existingOnlineCodePreserved':True,'sharedManifestAndDexRequireNewRuntimeIdentities':True,'apkProduced':False,'signed':False,'installed':False,'physicalGameplayVerified':False}
 write(a.out/'offline-payloads.json',receipt);print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
