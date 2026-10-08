"""Apply the requested game-only upper-corner backdrop to the complete inputs.

Historical candidate preparation; do not rerun on the canonical channel.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
p = WORK / 'carousel-inputs/d0/native_space.h'
s = p.read_text('utf8')
assert 'drawGameCornerBackdrop' not in s
helper = '''// Two static triangle strips: opaque at the upper corners, clear inward.
// Drawn before artwork; no timer, texture, allocation or offscreen pass.
static void drawGameCornerBackdrop(float w,float h){
 fn<void(*)(unsigned)>(3035880)(0);
 unsigned solid=fn<unsigned(*)(unsigned)>(3029376)(0x000000ffu);
 unsigned clear=fn<unsigned(*)(unsigned)>(3029376)(0x00000000u);
 const float reachX=w*.56f,reachY=h*.68f,hold=.10f;
 for(int side=0;side<2;side++){
  float origin=side?w:0,direction=side?-1.f:1.f;
  Vertex strip[5]={{origin,0,0,0,solid},
   {origin+direction*reachX*hold,0,0,0,solid},
   {origin,reachY*hold,0,0,solid},
   {origin+direction*reachX,0,0,0,clear},
   {origin,reachY,0,0,clear}};
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,5,4,5);
 }
}
'''
s = s.replace('static void drawNativeSpace(float w,float h){', helper+'static void drawNativeSpace(float w,float h){')
s = s.replace('if(!gui||at<int>(gui,0x370)!=3)return;', 'if(!gui||at<int>(gui,0x370)!=3)return;\n if(!systemsMode){drawGameCornerBackdrop(w,h);return;}')
p.write_text(s,'utf8')
p = ROOT / 'build_native.py'
s = p.read_text('utf8')
assert "'native_skin.h','station_bottom_action_layout.h'" in s
p.write_text(s.replace("'native_skin.h','station_bottom_action_layout.h'", "'native_skin.h','native_space.h','station_bottom_action_layout.h'"),'utf8')
old='4906c83dede6f3fe791944c3fb8d319a5f54c564c169f2a76cc06e1c3cd66ff7'
new='593307ae5fd90d9845532b200ac9e97737ffca1d0cb0e239034e9d9fa8241057'
for name in ['package_candidate.py','refresh_candidate.py']:
 p=ROOT/'recipes'/name;s=p.read_text('utf8');assert old in s;p.write_text(s.replace(old,new),'utf8')
for name in ['native','package']:
 src=(WORK/name).resolve();dst=(WORK/(name+'-fifth')).resolve()
 assert src.parent==WORK.resolve() and dst.parent==WORK.resolve() and not dst.exists()
 src.rename(dst)
print('Game-only corner backdrop prepared; systems and collection background preserved')
