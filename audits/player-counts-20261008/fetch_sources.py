from pathlib import Path
from urllib.request import urlopen, Request
import hashlib,json,zipfile,io
ROOT=Path(r'E:\ESTUDO APK\work\station-player-audit-20261008')
ROOT.mkdir(parents=True,exist_ok=True)
SOURCES={
 'fbneo-source.zip':'https://codeload.github.com/finalburnneo/FBNeo/zip/f963326de06f479fc9d54b0e03603feaffca393c',
 'super-bomberman-3.pdf':'https://www.retrogames.cz/manualy/SNES/Super_Bomberman_3_-_SNES_-_Manual.pdf',
 'super-bomberman-2.pdf':'https://www.videogamemanual.com/snes/Super%20Bomberman%202%20(USA).pdf',
 'secret-of-mana.pdf':'https://www.nintendo.com/es-es/games/oms/snes-classic/manuals/secret-of-mana/manual.pdf',
}
manifest=[]
for name,url in SOURCES.items():
 p=ROOT/name
 try:
  if not p.exists():
   with urlopen(Request(url,headers={'User-Agent':'TurboStations-player-audit/1.0'}),timeout=50) as r: data=r.read(150_000_001)
   assert len(data)<150_000_000
   p.write_bytes(data)
  data=p.read_bytes()
  manifest.append({'name':name,'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
  print(name,len(data),flush=True)
 except Exception as e: manifest.append({'name':name,'url':url,'error':type(e).__name__});print(name,type(e).__name__,flush=True)
(ROOT/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
