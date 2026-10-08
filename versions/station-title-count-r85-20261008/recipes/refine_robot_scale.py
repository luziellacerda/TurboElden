"""Increase only the game settings robot and its touch bounds by 30%."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
p=WORK/'carousel-inputs/d0/station_collection_settings_layout.h'
s=p.read_text('utf8')
old='if(!systems)return {w*.8775f-h*.05f,h*.455f,h*.10f,h*.075f};'
new='if(!systems)return {w*.8775f-h*.065f,h*.44375f,h*.130f,h*.0975f};'
assert old in s;p.write_text(s.replace(old,new),'utf8')
for name in ['native','package']:
 src=(WORK/name).resolve();dst=(WORK/(name+'-seventh')).resolve()
 assert src.parent==WORK.resolve() and dst.parent==WORK.resolve() and not dst.exists()
 src.rename(dst)
# The last canonical APK is still the scope-and-gradient build, unchanged.
assert json.loads((ROOT.parents[1]/'release-channels/ACTIVE.json').read_text())['channels']['test-4p']['apkSHA256']=='b8a153802c5c9e564679d726a6074b96307705a0e1677dfd4c8abd6677497ef2'
print('Game settings robot enlarged 30%; center preserved; systems/collections unchanged')
