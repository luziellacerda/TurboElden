from pathlib import Path,PurePosixPath
import json,urllib.request,hashlib,re
R=Path(r'E:\StationNetplayWork');tree=json.loads((R/'upstream/overlay-tree.json').read_text('utf-8'));commit=tree['commit'];by={x['path']:x for x in tree['tree'] if x['type']=='blob'}
out=R/'assets/station-online/overlays';pending=['COPYING','gamepads/flat/snes.cfg','gamepads/flat/genesis.cfg','gamepads/flat/neogeo.cfg'];done={}
while pending:
 name=pending.pop(0)
 if name in done:continue
 assert name in by and '..' not in PurePosixPath(name).parts,name
 url='https://raw.githubusercontent.com/libretro/common-overlays/'+commit+'/'+name
 data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Station-source-audit'}),timeout=30).read()
 assert len(data)<=4*1024*1024
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==by[name]['sha']
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 done[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 if name.endswith('.cfg'):
  s=data.decode('utf-8-sig')
  for value in re.findall(r'=\s*"?([^"\s]+\.(?:png|cfg))"?',s):pending.append(str(PurePosixPath(name).parent/value))
(R/'evidence/overlay-sources.json').write_text(json.dumps({'repository':'https://github.com/libretro/common-overlays','commit':commit,'license':'CC-BY-4.0; COPYING included unchanged','files':done},indent=2),'utf-8')
(out/'ATTRIBUTION.txt').write_text('Flat gamepad overlays by the libretro/common-overlays contributors.\nSource: https://github.com/libretro/common-overlays/tree/'+commit+'\nLicense: CC-BY-4.0, see COPYING. Configurations and images unchanged.\n','utf-8')
print('Verified official overlays:',len(done))
