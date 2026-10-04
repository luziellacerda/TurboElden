from pathlib import Path
import json,re,subprocess
R=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
BASE=Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003\TurboStations-SNES-Mega-HUD-LZGames-R2-20261003.apk')
OUT=R/'TurboStations-Capas4-Sinopses-LED-Netplay-R3-20261003.apk'
TOOL=r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\aapt2.exe'
ADDED={'org.emulationstation.frontend.netplay.StationNetplayActivity','org.emulationstation.frontend.netplay.StationDolphinNetplayActivity'}
def dump(p):
    text=subprocess.check_output([TOOL,'dump','xmltree',str(p),'--file','AndroidManifest.xml']).decode('utf-8')
    roots=[];stack=[]
    for line in text.splitlines():
        indent=len(line)-len(line.lstrip());value=re.sub(r' \(line=\d+\)$','',line.strip())
        if value.startswith('E: '):
            while stack and stack[-1][0]>=indent:stack.pop()
            node={'element':value[3:],'attributes':[],'children':[]}
            (stack[-1][1]['children'] if stack else roots).append(node);stack.append((indent,node))
        elif value.startswith('A: '):stack[-1][1]['attributes'].append(value[3:])
    return roots
def canonical(nodes,removed):
    out=[]
    for n in nodes:
        identity=next((a for a in n['attributes'] if ':name(' in a),'')
        if any('="'+name+'"' in identity for name in ADDED):removed.append(n);continue
        out.append({'element':n['element'],'attributes':sorted(n['attributes']),'children':canonical(n['children'],removed)})
    return sorted(out,key=lambda n:json.dumps(n,sort_keys=True))
oldextra=[];newextra=[]
old=canonical(dump(BASE),oldextra);new=canonical(dump(OUT),newextra)
assert not oldextra and len(newextra)==2
assert old==new,'Existing manifest declaration changed'
for n in newextra:
    assert n['element']=='activity'
    assert any(':exported(' in a and a.endswith('=false') for a in n['attributes'])
assert sum(any(':process(' in a and '":dolphin"' in a for a in n['attributes']) for n in newextra)==1
report={'existingDeclarationsIdentical':True,'addedInternalActivities':newextra,'newPermissions':0,'engineDeclarationsPreserved':True}
(R/'evidence/manifest-semantic-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Manifest verified: two internal Activities, all existing declarations unchanged.')
