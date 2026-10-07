"""Bind the R73 manifest to the newly compiled Windows runtime without enabling other cores."""
from pathlib import Path
import argparse,copy,hashlib,json,re,zipfile

p=argparse.ArgumentParser();p.add_argument('--native-work',default=r'E:\R73fixed');p.add_argument('--workspace',default=r'E:\ESTUDO APK\work\station-recovery-handshake-r73-20261007-build');a=p.parse_args()
w=Path(a.workspace);n=Path(a.native_work);snapshot=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
runtime=n/'libstation_retroarch.so';digest=sha(runtime)
assert digest!='d66267cd42507388f86034deb47e9f9670875784efb9afabfb8ffc64e3f3a856'
base=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R72-20261007.apk')
with base.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='a8d3d28bb70618c52debf6e4cb0acaaf1f3bd1de19fe410dda85f6953caaec8e'
with zipfile.ZipFile(base) as z:original=json.loads(z.read('assets/station-online/engines.json'))
candidate=copy.deepcopy(original);additions=[]
for old,new in zip(original['engines'],candidate['engines']):
 assert old['runtimeSha256']=='d66267cd42507388f86034deb47e9f9670875784efb9afabfb8ffc64e3f3a856'
 new['runtimeSha256']=digest
 new['engineId']=re.sub(r'-rs2-d66267cd4250$', '-rs3-'+digest[:12],old['engineId'])
 assert new['engineId']!=old['engineId']
 assert {k:v for k,v in old.items() if k not in ('runtimeSha256','engineId')}=={k:v for k,v in new.items() if k not in ('runtimeSha256','engineId')}
 if old.get('launchReady'):
  assert old['platform'] in ('snes','megadrive') and old['recoveryProtocol']=='station-stream.v2'
  additions.append(dict(id=new['engineId'],platform=new['platform'],coreSha256=new['coreSha256'],runtimeSha256=digest,recoveryProtocol='station-stream.v2'))
 else:assert old['platform']=='neogeo'
assert len(additions)==2
out=w/'assets/station-online/engines.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n','utf8')
e=snapshot/'evidence';e.mkdir(exist_ok=True)
(e/'server-engine-registry-additions.json').write_text(json.dumps(additions,indent=2)+'\n','utf8')
(e/'engine-manifest.json').write_bytes(out.read_bytes())
(w/'evidence/engine-registry.json').write_text(json.dumps(dict(runtime=str(runtime),runtimeSHA256=digest,manifest=str(out),manifestSHA256=sha(out),registryAdditions=additions,neogeoLaunchReady=False,serverActivationVerified=False),indent=2)+'\n','utf8')
print(json.dumps(additions,indent=2))
