from pathlib import Path
import json,hashlib,os,subprocess
W=Path(__file__).resolve().parent;N=W/'native';B=Path(r'E:\ESTUDO APK\work\station-back-button-r30-20261005')
p=N/'native_carousel.cpp';s=p.read_text('utf8')
assert '#include "native_installed_tag.h"' not in s
s=s.replace('#include "native_info.h"','#include "native_info.h"\n#include "native_installed_tag.h"')
s=s.replace('if(p==onlineActionText||','if(p==installedTagText||p==onlineActionText||')
s=s.replace('drawOnlineAction(p,matrix);drawHeaderGameStars(p);','drawOnlineAction(p,matrix);drawHeaderGameStars(p);drawInstalledTag(p);')
p.write_text(s,'utf8')
r=json.loads((B/'evidence/native-build.json').read_text('utf8'))
r['command']=[x.replace(str(B),str(W)) for x in r['command']]
r.update(baseAPK=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Voltar-Salas-R30-20261005.apk',baseSHA256='1768b7df440dcdf99efbd2e8ff93181eae06edaab5bb9be85e073afeb639027b',baseNative=str(B/'native'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r['baseSources']={p.name:sha(p) for p in (B/'native').iterdir() if p.is_file()}
for key in ['overlaySources','changedSources','addedSources','hostTests','soSHA256','soBytes','androidCompile']:r.pop(key,None)
(W/'evidence/native-build-input.json').write_text(json.dumps(r,indent=2),'utf8')
print('Native source ready')
