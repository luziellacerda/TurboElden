"""Compare exact R71/R75 media routing with independent server UTF-8 fixtures.

No Android, decoder, network, game or APK is run. The production folder/video
routing functions are extracted verbatim; only their in-memory GUI data is
adapted to a host process. All compiler outputs and logs stay on E:.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,subprocess

SNAPSHOT=Path(__file__).resolve().parent.parent
BASE_NATIVE=Path(r'E:\ESTUDO APK\work\station-online-layout-r71-20261007-carousel-final\native')
SYSTEM_HEADER=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native\system_video720_assets.h')
DEFAULT=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-map-r75-20261007\tests')
PINS={
 'baseHeader':'10daa6b42d46d7bc1f099e705d9fa258af8c1a43a0ef6a0a7d4071cacbfe64f9',
 'candidateHeader':'5ca0f4f114037e605b698067b34d01cb6f0aef2ba4c3d223117801d8a71a693b',
 'folders':'71fa0864f7833c1e2cf29eac8c7a0bf97ff15115625fd55789819a69d23b1944',
 'video':'901d01341f3c316e02ca5b07cc278f5bc0864cff9ba39da7ce52030888261cc6',
 'systems':'2d0e351bed93dd3f26548f6b92157f232b81a3df9586cd65c0900f1ce1df3cf5',
 'catalog':'ab719e7345f74afbe38ec0a96d9897efb82fe4c4343908229e34f3f29db74acf',
 'mapping':'daa147fbd4a8ea1864419c8d6fafe81122814a3910c22ff8d05272841b7f6405',
}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def function(source,anchor):
 start=source.index(anchor);opening=source.index('{',start);depth=0
 for end in range(opening,len(source)):
  if source[end]=='{':depth+=1
  elif source[end]=='}':
   depth-=1
   if depth==0:return source[start:end+1]
 raise ValueError('Function not found: '+anchor)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',default=str(DEFAULT));a=parser.parse_args()
 out=Path(a.output).resolve()
 require(out.drive.upper()=='E:' and out==DEFAULT.resolve(),'Use the authorized R75 tests directory on E:')
 inputs={'baseHeader':SNAPSHOT.parent/'station-online-layout-r71-20261007/native-carousel/collection_video_policy.h',
         'candidateHeader':SNAPSHOT/'native/collection_video_policy.h','folders':BASE_NATIVE/'native_folders.h',
         'video':BASE_NATIVE/'native_system_video720.h','systems':SYSTEM_HEADER,
         'catalog':SNAPSHOT/'tests/fixtures/catalog-bindings-r67.json',
         'mapping':SNAPSHOT/'tests/fixtures/media-mapping-r67.json'}
 for name,path in inputs.items():require(sha(path)==PINS[name],'Frozen input differs: '+name)
 old=inputs['baseHeader'].read_bytes();new=inputs['candidateHeader'].read_bytes()
 bad=b'COLE\xc3\x83\xe2\x80\xa1\xc3\x83\xc6\x92O';fixed=b'COLE\\u00c7\\u00c3O'
 require(old.count(bad)==5 and old.replace(bad,fixed)==new,'Only five UTF-8 literal corrections allowed')
 source=SNAPSHOT/'tests/collection_routes.cpp';test_source=source.read_text('utf8');test_sha=sha(source)
 catalog=json.loads(inputs['catalog'].read_text('utf8'));mapping=json.loads(inputs['mapping'].read_text('utf8'))
 # Each expected path and asset is checked against independent catalog/media
 # fixtures, never against collectionVideoDefinitions in either native header.
 references=re.findall(r'^\s*\{"(neogeo-[^"]+)","([^"]+)","([^"]+)"\},',test_source,re.M)
 require(len(references)==6,'Six independent Neo Geo expectations required')
 for key,path,asset in references:
  binding=next(row for row in catalog['bindings'] if row['key']==key)
  media=next(row for row in mapping['videos'] if row['key']==key)
  require(any(row['platform']=='neogeo' and row['folderPath']==path for row in binding['matches']),'Expected path differs from catalog: '+key)
  require(media['asset']=='assets/'+asset,'Expected asset differs from owner media mapping: '+key)
 require(sum('COLEÇÃO' in path for _,path,_ in references)==5,'Five independent UTF-8 accented paths required')
 folders=function(inputs['folders'].read_text('utf8'),'static const CollectionVideoDef*folderVideo(void*p,int index)')
 video=function(inputs['video'].read_text('utf8'),'static const char*video720Asset(void*p,int index)')
 extracted=(folders+'\n'+video+'\n').encode('utf8')
 out.mkdir(parents=True,exist_ok=True);temp=out/'temp';temp.mkdir(exist_ok=True)
 compiler=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
 env=dict(os.environ,TEMP=str(temp),TMP=str(temp));results=[]
 for label,header in [('baseline',old),('candidate',new)]:
  folder=out/label;folder.mkdir(exist_ok=True)
  (folder/'collection_video_policy.h').write_bytes(header)
  (folder/'system_video720_assets.h').write_bytes(inputs['systems'].read_bytes())
  (folder/'production_video_routes.h').write_bytes(extracted)
  binary=folder/'routes.exe'
  command=[str(compiler),'-std=c++17','-Wall','-Wextra','-Werror','-finput-charset=UTF-8','-fexec-charset=UTF-8',
           '-I',str(folder),str(source),'-o',str(binary)]
  compile_result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',env=env)
  (folder/'compile.log').write_text(compile_result.stdout+compile_result.stderr,'utf8')
  require(compile_result.returncode==0,'Compiler failed: '+label)
  run=subprocess.run([str(binary)],capture_output=True,text=True,encoding='utf8',env=env,timeout=15)
  (folder/'run.log').write_text(run.stdout+run.stderr,'utf8')
  result=json.loads(run.stdout)
  require(result['otherFailures']==0,'Unrelated behavior regressed: '+label)
  if label=='baseline':require(run.returncode==1 and result['failures']==result['neoFailures']==51,'Old mismatch not reproduced precisely')
  else:require(run.returncode==0 and result['failures']==0,'Corrected mappings did not pass')
  results.append(dict(label=label,headerSHA256=hashlib.sha256(header).hexdigest(),exitCode=run.returncode,
                      **result,compilerCommand=command,compilerLogSHA256=sha(folder/'compile.log'),runLogSHA256=sha(folder/'run.log')))
 require(results[0]['checks']==results[1]['checks'],'Baseline/candidate check counts differ')
 require(sha(source)==test_sha and all(sha(p)==PINS[n] for n,p in inputs.items()),'Source changed during test')
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),success=True,scope=__doc__,
   sourceSHA256=PINS,testSourceSHA256=test_sha,recipeSHA256=sha(__file__),compilerSHA256=sha(compiler),
   independentCatalogCommit=catalog['commit'],independentCatalogPath=catalog['path'],
   independentCatalogSHA256=catalog['sha256'],independentNeoFixtures=6,changedLiterals=5,
   productionFolderVideoSHA256=hashlib.sha256(folders.encode()).hexdigest(),
   productionVideoAssetSHA256=hashlib.sha256(video.encode()).hexdigest(),results=results,
   fallbackRoutingExecuted=True,mainPlatformVideoPreserved=True,cdPolicyPreserved=True,
   allGamesR71Preserved=True,androidExecuted=False,decoderExecuted=False,apkBuilt=False)
 for target in (out/'route-tests.json',SNAPSHOT/'evidence/route-tests.json'):
  target.write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps({'success':True,'checksPerBuild':results[1]['checks'],'baselineFailures':results[0]['failures'],
                   'candidateFailures':results[1]['failures'],'report':str(out/'route-tests.json')},indent=2))

if __name__=='__main__':main()
