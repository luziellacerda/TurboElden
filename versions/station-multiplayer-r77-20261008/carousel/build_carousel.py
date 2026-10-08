"""Reproduce the exact R75 carousel, then change only the player evidence display binding."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BASE=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-map-r75-20261007\native-build')
BASE_RECEIPT='e55001da0b995e9326aa376b1423eb76de04af40ddd7b6c98da8d13816c140a7'
BASE_NATIVE='3c2e22bc94f3432280e2b08c2f26ab33508cd1278ee9bd750b48d45c35105a8b'
def require(value,message):
 if not value:raise RuntimeError(message)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dependencies(source,includes):
 result={}
 def visit(p):
  p=p.resolve()
  if str(p)in result:return
  result[str(p)]=sha(p)
  for name in re.findall(r'^\s*#\s*include\s*"([^"\n]+)"',p.read_text('utf8'),re.M):
   child=next((d/name for d in [p.parent,*includes] if(d/name).is_file()),None)
   require(child is not None,'Missing quoted include '+name);visit(child)
 visit(source);return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008\carousel-build'));a=p.parse_args();work=a.output.resolve()
 require(work.drive.upper()=='E:' and not work.exists(),'Use a new E: output directory')
 require(sha(BASE/'evidence/build.json')==BASE_RECEIPT,'R75 receipt changed')
 receipt=json.loads((BASE/'evidence/build.json').read_text('utf8'))
 require(sha(BASE/'libturbo_carousel.so')==receipt['nativeSHA256']==BASE_NATIVE,'R75 library changed')
 require(len(receipt['nativeSources'])==65 and len(receipt['objects'])==7,'R75 composition changed')
 for name,h in receipt['nativeSources'].items():require(sha(BASE/'native'/name)==h,'R75 source changed '+name)
 for path,h in receipt['objects'].items():require(sha(path)==h,'R75 object changed '+path)
 overlay=json.loads((HERE/'OVERLAY-MANIFEST.json').read_text('utf8'))
 require(set(overlay['sources'])=={'native_info.h','native_players_evidence.h','station_catalog_player_label.h'},'Overlay scope')
 for name,h in overlay['sources'].items():require(sha(HERE/name)==h,'Overlay changed '+name)
 command=list(receipt['command']);source=str(BASE/'native/native_carousel.cpp');output=str(BASE/'libturbo_carousel.so')
 require(command.count(source)==command.count(output)==1,'Source/output arguments')
 includes=[Path(command[i+1]) for i,v in enumerate(command) if v=='-I']
 original=dependencies(Path(source),includes)
 require(original==receipt['quotedDependencies'],'R75 external includes changed')
 compiler=Path(command[0]);host=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
 recipe_hash=sha(__file__);manifest_hash=sha(HERE/'OVERLAY-MANIFEST.json')
 for name in ('native','tests','temp','evidence'):(work/name).mkdir(parents=True)
 env=dict(os.environ,TEMP=str(work/'temp'),TMP=str(work/'temp'));executions=[]
 def run(argv,label):
  argv=list(map(str,argv));r=subprocess.run(argv,capture_output=True,env=env,timeout=300)
  log=work/'evidence'/(label+'.log');log.write_bytes(r.stdout+r.stderr)
  executions.append({'label':label,'command':argv,'exitCode':r.returncode,'logSHA256':sha(log)})
  require(r.returncode==0,label+': '+r.stderr.decode('utf8','replace')[-2400:]);return r.stdout.decode('utf8','replace').strip()
 baseline=list(command);baseline[baseline.index(output)]=str(work/'baseline-r75.so')
 run(baseline,'baseline-reproduction');require(sha(work/'baseline-r75.so')==BASE_NATIVE,'R75 byte reproduction failed; stop')
 for name in receipt['nativeSources']:shutil.copyfile(BASE/'native'/name,work/'native'/name)
 for name in overlay['sources']:shutil.copyfile(HERE/name,work/'native'/name)
 sources={f.name:sha(f) for f in (work/'native').iterdir() if f.is_file()}
 changed=sorted(n for n,h in receipt['nativeSources'].items() if sources[n]!=h)
 added=sorted(set(sources)-set(receipt['nativeSources']))
 require(changed==['native_info.h'] and added==['native_players_evidence.h','station_catalog_player_label.h'],'Native change scope')
 common=[host,'-std=c++17','-Wall','-Wextra','-Werror','-finput-charset=UTF-8','-fexec-charset=UTF-8','-I',work/'native']
 tests={
  'player-label':ROOT/'tests/catalog_player_label.cpp',
  'corners':ROOT.parent/'station-collection-media-r69-20261007/tests/collection_corners.cpp',
  'decoder':ROOT.parent/'station-current-r55-20261006/tests/native/test_video_policy.cpp',
  'navigation':ROOT.parent/'station-collection-navigation-r70-20261007/tests/navigation.cpp',
  'routes':ROOT.parent/'station-online-layout-r71-20261007/tests/collection_all_video.cpp',
  'settings':ROOT.parent/'station-collection-navigation-r70-20261007/tests/collection_settings.cpp'}
 test_hashes={n:sha(f) for n,f in tests.items()};results={}
 for name in ['player-label','corners','decoder']:
  run(common+[tests[name],'-o',work/'tests'/(name+'.exe')],name+'-compile');results[name]=run([work/'tests'/(name+'.exe')],name+'-test');require(results[name].startswith('PASS'),name+' result')
 run([host,'-std=c++17','-O2','-finput-charset=UTF-8','-fexec-charset=UTF-8','-I',work/'native',tests['navigation'],'-o',work/'tests/navigation.exe'],'navigation-compile')
 results['navigation']=run([work/'tests/navigation.exe'],'navigation-test');require(results['navigation'].startswith('PASS 3584 '),'Navigation regression')
 symbols=re.findall(r'extern const unsigned char (\w+)\[\];',(work/'native/video720_posters.h').read_text('utf8'))
 stubs=work/'tests/poster_symbols.cpp';stubs.write_text('extern "C" {\n'+'\n'.join('extern const unsigned char '+s+'[]={0};' for s in symbols)+'\n}\n','utf8')
 run(common+[tests['routes'],stubs,'-o',work/'tests/routes.exe'],'routes-compile');results['routes']=run([work/'tests/routes.exe'],'routes-test');require(results['routes'].startswith('PASS 3444 '),'Routes regression')
 run(common+['-Wno-unused-function','-fsyntax-only',tests['settings']],'settings-test')
 command[command.index(source)]=str(work/'native/native_carousel.cpp');command[command.index(output)]=str(work/'libturbo_carousel.so')
 candidate_dependencies=dependencies(work/'native/native_carousel.cpp',includes)
 expected={}
 for path,h in original.items():
  old=Path(path);relative=old.relative_to(BASE/'native') if old.is_relative_to(BASE/'native') else None
  if relative==Path('station_players_label.h'):continue
  equivalent=work/'native'/relative if relative else old
  expected[str(equivalent.resolve())]=overlay['sources'].get(str(relative),h)
 for name,h in overlay['sources'].items():expected[str((work/'native'/name).resolve())]=h
 require(candidate_dependencies==expected,'External include or unexpected dependency changed')
 run(command,'carousel-build')
 elf=run([compiler.parent/'llvm-readelf.exe','-h','-l',work/'libturbo_carousel.so'],'elf-check')
 aligns=[int(line.split()[-1],16) for line in elf.splitlines() if line.strip().startswith('LOAD ')]
 require('AArch64' in elf and aligns and min(aligns)>=16384,'ELF alignment')
 require(sha(__file__)==recipe_hash and sha(HERE/'OVERLAY-MANIFEST.json')==manifest_hash,'Recipe changed during compilation')
 require(sources=={f.name:sha(f) for f in (work/'native').iterdir() if f.is_file()},'Staged sources changed')
 require(candidate_dependencies==dependencies(work/'native/native_carousel.cpp',includes),'Includes changed during compilation')
 for n,h in test_hashes.items():require(sha(tests[n])==h,'Test changed '+n)
 for path,h in receipt['objects'].items():require(sha(path)==h,'Object changed '+path)
 record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled':True,'baseNativeSHA256':BASE_NATIVE,'baselineReproductionSHA256':sha(work/'baseline-r75.so'),'nativeSHA256':sha(work/'libturbo_carousel.so'),'nativeBytes':(work/'libturbo_carousel.so').stat().st_size,'nativeSources':sources,'changedNativeSources':changed,'addedNativeSources':added,'objects':receipt['objects'],'baseQuotedDependencies':original,'quotedDependencies':candidate_dependencies,'command':command,'baselineCommand':baseline,'overlayManifestSHA256':manifest_hash,'recipeSHA256':recipe_hash,'compilerSHA256':sha(compiler),'testSources':{n:{'path':str(tests[n]),'sha256':h} for n,h in test_hashes.items()},'results':results,'executions':executions,'minimumLoadAlignment':min(aligns),'mediaChanged':False,'geometryChanged':False,'ratingsChanged':False,'emulatorChanged':False,'displayBinding':'Exact signed catalogue itemId/revision/contentSha256 and reviewed asset; unknown em dash','packaged':False,'installed':False,'physicalDisplayVerified':False}
 (work/'evidence/build.json').write_text(json.dumps(record,indent=2)+'\n','utf8');(HERE/'build-result.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
 print(json.dumps({'compiled':True,'nativeSHA256':record['nativeSHA256'],'results':results,'path':str(work/'libturbo_carousel.so')},indent=2))
if __name__=='__main__':main()
