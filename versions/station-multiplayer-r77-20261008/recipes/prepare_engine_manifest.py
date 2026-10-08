"""Exact R77 motor and controller identities; all game approvals remain operator-owned."""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parent.parent
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R76-20261008.apk')
RUNTIME='351cee4540e916468a504788911e4c5fcb4fe141e3b544b1b1255d32e1d04a26'
CORE='0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527'
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
with zipfile.ZipFile(BASE) as z:
 raw=z.read('assets/station-online/engines.json');assert hashlib.sha256(raw).hexdigest()=='d43d6af1581691fbf88d6a15f87bea66761ef2f4d8952857028c6541b908e985'
 manifest=json.loads(raw)
for e in manifest['engines']:
 e['runtimeSha256']=RUNTIME
 if e['platform']=='snes':e['engineId']='bsnes-mercury-performance-79d7f9de-mt1-mp3-'+RUNTIME[:12];e['coreSha256']=CORE
 else:e['engineId']=e['engineId'].split('-rs4-')[0]+'-mp3-'+RUNTIME[:12]
 if e['launchReady']:e['recoveryProtocol']='station-stream.v3'
manifest['androidPeerPlayValidated']=False
save(R/'assets/station-online/engines.json',manifest)
snes=manifest['engines'][0]
canonical=json.dumps(dict(schemaVersion=1,controllerProfile='snes-multitap-port2-v1',devices=[1,257,1,1,1],coreOptions=snes['options']),ensure_ascii=False,separators=(',',':'))
profile_hash=hashlib.sha256(canonical.encode()).hexdigest()
catalog=json.loads((R/'catalog/proposed-registry.json').read_text('utf8'))
for p in catalog['entries']:
 p.update(runtimeSha256=RUNTIME,engineId=snes['engineId'],profileId='snes-sbomberman2-usa-battle-single-r77',profileSha256=profile_hash,maximumPlayers=4)
 p.pop('profileHash',None)
 p['operatorActionsRequired']=[x for x in p['operatorActionsRequired'] if not x.startswith('Set the final')]
 p['operatorActionsRequired'].insert(1,'Reproduce and compare the exact R77 engine/runtime/controller identity before staging the profile.')
save(R/'catalog/proposed-registry.json',catalog)
fields=['itemId','contentSha256','platform','engineId','coreSha256','runtimeSha256','profileId','profileSha256','maximumPlayers','approved','controllerProfile','mode','allowedPlayerCounts']
save(R/'server/proposed-game-profiles-r77.json',[{k:p[k] for k in fields} for p in catalog['entries']])
save(R/'PROFILE-IDENTITY.json',dict(schemaVersion=1,algorithm='SHA-256 of UTF-8 compact JSON; exact key order shown in canonical; no BOM/newline',canonical=canonical,sha256=profile_hash,gameIdentityBoundSeparatelyBySignedProfile=True,approved=False))
print(json.dumps({'runtime':RUNTIME,'snesCore':CORE,'profileSha256':profile_hash,'approved':False}))
