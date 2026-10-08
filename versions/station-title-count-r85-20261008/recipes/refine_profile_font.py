"""Game header username follows the measured folder-counter line height."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
p=WORK/'carousel-inputs/d0/native_profile_name.h';s=p.read_text('utf8')
old='''  float desired=nativeInfoTextWidth(text,*name?name:"JOGADOR",.72f);
  profileScale=!systemsMode&&desired>area.w?.72f*area.w/desired:.72f;if(profileScale<.46f)profileScale=.46f;'''
new='''  nativeInfoTextWidth(text,*name?name:"JOGADOR",1.f);
  // Match actual rendered line height, even when the profile uses a different
  // native font size. Keep font size fixed; abbreviate only overlong names.
  profileScale=.72f;
  if(!systemsMode&&infoListCountText){
   float natural=at<float>(text,0x58),reference=at<float>(infoListCountText,0x58)*stationGameMetadataScale;
   if(natural>0&&reference>0)profileScale=reference/natural;
  }'''
assert old in s;s=s.replace(old,new)
# Center the same-height line within the unchanged game header.
s=s.replace('h*.05f};','h*(systemsMode?.05f:.060f)};')
p.write_text(s,'utf8')
old='593307ae5fd90d9845532b200ac9e97737ffca1d0cb0e239034e9d9fa8241057'
new='b8a153802c5c9e564679d726a6074b96307705a0e1677dfd4c8abd6677497ef2'
for name in ['package_candidate.py','refresh_candidate.py']:
 p=ROOT/'recipes'/name;s=p.read_text('utf8');assert old in s;p.write_text(s.replace(old,new),'utf8')
for name in ['native','package']:
 src=(WORK/name).resolve();dst=(WORK/(name+'-sixth')).resolve()
 assert src.parent==WORK.resolve() and dst.parent==WORK.resolve() and not dst.exists()
 src.rename(dst)
print('Game profile uses the measured counter font height; other menus unchanged')
