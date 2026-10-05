"""Rebuild the exact local RGBA header from the seven final project PNGs."""
from pathlib import Path
from PIL import Image
import sys,hashlib
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(r'E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005')
keys=['snes','megadrive','n64','neogeo','neogeocd','naomi','naomi2']
header=['// Embedded static hardware illustrations; no network request or frame decoder.',
 'struct StationConsoleAsset {const char*key;unsigned width,height;const unsigned char*rgba;};']
entries=[]
for key in keys:
 im=Image.open(root/'assets/turbo-console'/(key+'.png')).convert('RGBA')
 assert im.size==(512,512) and im.getchannel('A').getextrema()[0]==0,key
 raw=im.tobytes();header.append('static const unsigned char stationConsole_'+key+'[]={')
 header.extend(','.join(map(str,raw[i:i+128]))+',' for i in range(0,len(raw),128));header.append('};')
 entries.append('{"'+key+'",'+str(im.width)+','+str(im.height)+',stationConsole_'+key+'}')
header.append('static const StationConsoleAsset stationConsoleAssets[]={'+','.join(entries)+'};')
raw=('\r\n'.join(header)+'\r\n').encode('utf-8');p=root/'native/console_assets.h'
if p.exists():assert p.read_bytes()==raw,'Existing header differs: investigate before replacing'
else:p.write_bytes(raw)
print(hashlib.sha256(raw).hexdigest())
