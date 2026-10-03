"""Select the source JNI namespace/atlas before the sequential native build.

Run snes -> build imagine, EmuFramework, Snes9x -> mega -> build all for MD.emu.
This compiles the separate namespace from source, never patches instructions.
"""
from pathlib import Path
import argparse, json, hashlib

BASE=Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
SRC=BASE/'source'
p=argparse.ArgumentParser();p.add_argument('engine',choices=['snes','mega']);args=p.parse_args()
old,other=('com/imagine/', 'com/mdimagn/')
chosen=old if args.engine=='snes' else other
updated={}
count=0
for file in (SRC/'imagine/src/base/android').rglob('*.cc'):
    s=file.read_text(encoding='utf-8')
    occurrences=s.count(old)+s.count(other)
    if not occurrences: continue
    count+=occurrences
    s=s.replace(other,old).replace(old,chosen)
    file.write_text(s,encoding='utf-8',newline='\n')
    updated[str(file.relative_to(SRC))]=hashlib.sha256(file.read_bytes()).hexdigest()
assert count==8,('Unexpected JNI descriptor count',count)
atlas=SRC/'EmuFramework/include/emuframework/AssetManager.hh'
s=atlas.read_text(encoding='utf-8')
assert s.count('gpOverlay.png')+s.count('mdOverlay.png')==1
s=s.replace('mdOverlay.png','gpOverlay.png')
if args.engine=='mega':s=s.replace('gpOverlay.png','mdOverlay.png')
atlas.write_text(s,encoding='utf-8',newline='\n')
updated[str(atlas.relative_to(SRC))]=hashlib.sha256(atlas.read_bytes()).hexdigest()
receipt={'engine':args.engine,'namespace':chosen,'files':updated,'native_instruction_patching':False}
(BASE/(args.engine+'-source-selection.json')).write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
