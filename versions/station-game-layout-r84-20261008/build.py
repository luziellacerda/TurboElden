"""Compile and freeze the complete R84 source set based only on canonical R84."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile,datetime,shutil
ROOT=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-game-layout-r84-20261008')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r83')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 sources={p.relative_to(WORK/'java').as_posix():sha(p) for p in sorted((WORK/'java').rglob('*.java'))}
 baseline=json.loads((BASE/'JAVA-SOURCE-MANIFEST.json').read_text())['sources']
 added=set(sources)-set(baseline);assert len(sources)==210 and not added
 changed=[n for n in baseline if sources[n]!=baseline[n]]
 assert sorted(Path(n).name for n in changed)==[]
 for name,digest in baseline.items():assert sha(BASE/'java'/name)==digest
 jr=json.loads((BASE/'java-build-receipt.json').read_text());jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
 android=Path(r'G:\Android\Sdk\platforms\android-34\android.jar');d8=Path(r'G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar')
 assert sha(android)==jr['inputs']['androidJar'] and sha(d8)==jr['inputs']['d8Jar']
 out=WORK/'compiled-final';assert not out.exists();out.mkdir();temp=out/'temp';temp.mkdir();env=dict(os.environ,TEMP=str(temp),TMP=str(temp))
 def run(cmd,label):
  r=subprocess.run(list(map(str,cmd)),env=env,capture_output=True);(out/(label+'.log')).write_bytes(r.stdout+r.stderr);assert r.returncode==0,label
 jars={};hashes={}
 for module,prefix in [('client',('client/src/java/',)),('rooms',('netplay-src/','dependency-src/'))]:
  classes=out/(module+'-classes');classes.mkdir();cp=str(android)+(os.pathsep+str(jars['client']) if module=='rooms' else '')
  options=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]+[str(WORK/'java'/n) for n in sorted(sources) if n.startswith(prefix)]
  args=out/(module+'.args');args.write_text('\n'.join('"'+v.replace('\\','/')+'"' for v in options),encoding='utf8')
  run([jdk/'javac.exe','-J-Djava.io.tmpdir='+str(temp),'@'+str(args)],module+'-javac')
  jar=out/(module+'.jar')
  with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
   for f in sorted(classes.rglob('*.class')):
    info=zipfile.ZipInfo(f.relative_to(classes).as_posix(),(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
  jars[module]=jar;dex=out/(module+'-dex');dex.mkdir()
  cmd=[jdk/'java.exe','-Djava.io.tmpdir='+str(temp),'-cp',d8,'com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',dex]
  if module=='rooms':cmd+=['--classpath',jars['client']]
  run(cmd+[jar],module+'-d8');hashes[module+'DexSHA256']=sha(dex/'classes.dex')
 receipt=dict(version='R84',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compiled=True,sourceCount=len(sources),sourceHashes=sources,changedSources=changed,addedSources=sorted(added),baseVersion='R83',inputs=jr['inputs'],baseClientDexSHA256=jr['clientDexSHA256'],baseRoomsDexSHA256=jr['roomsDexSHA256'],recipeSHA256=sha(__file__),**hashes)
 manifest={'version':'R84','sources':sources}
 for p in [WORK/'JAVA-SOURCE-MANIFEST.json',ROOT/'JAVA-SOURCE-MANIFEST.json']:p.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
 for p in [WORK/'java-build-receipt.json',ROOT/'evidence/java-build.json']:p.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
 for name,digest in sources.items():
  dst=Path('\\\\?\\'+str((ROOT/'java'/name).resolve()));dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(WORK/'java'/name,dst);assert sha(dst)==digest
 (ROOT/'java/.gitattributes').write_text('* -text\n',encoding='utf8')
 print(json.dumps({k:v for k,v in receipt.items() if k not in ['sourceHashes','inputs']},indent=2))
if __name__=='__main__':main()
