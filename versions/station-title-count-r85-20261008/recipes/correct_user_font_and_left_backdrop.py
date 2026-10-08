"""Undo the unrequested username enlargement and correct the user's visual scope."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
src=WORK/'carousel-inputs/d0'
p=src/'native_profile_name.h';s=p.read_text('utf8')
a=s.index('  nativeInfoTextWidth(text,*name?name:"JOGADOR",1.f);')
b=s.index('  fitGameTitleOneLine(text,',a)
s=s[:a]+'''  float desired=nativeInfoTextWidth(text,*name?name:"JOGADOR",.72f);
  profileScale=!systemsMode&&desired>area.w?.72f*area.w/desired:.72f;if(profileScale<.46f)profileScale=.46f;
'''+s[b:]
s=s.replace('h*(systemsMode?.05f:.060f)};','h*.05f};');p.write_text(s,'utf8')
p=src/'native_info.h';s=p.read_text('utf8')
s=s.replace('const float rowHeight=h*.076f,icon=h*.039f;','const float rowHeight=h*.076f,icon=h*.039f;\n  const float countScale=stationGameMetadataScale/1.5f;')
s=s.replace('nativeInfoTextWidth(infoListCountText,countLabel,stationGameMetadataScale)','nativeInfoTextWidth(infoListCountText,countLabel,countScale)')
s=s.replace('fitGameTitleOneLine(infoListCountText,countLabel,infoListCountViewport,stationGameMetadataScale)','fitGameTitleOneLine(infoListCountText,countLabel,infoListCountViewport,countScale)')
p.write_text(s,'utf8')
p=src/'native_space.h';s=p.read_text('utf8');a=s.index('// Two static triangle strips');b=s.index('static void drawNativeSpace',a)
s=s[:a]+'''// One static upper-left diagonal fade, behind the artwork and existing header.
// Preserve the established full-height left backdrop; no new bar or border.
static void drawGameCornerBackdrop(float w,float h){
 fn<void(*)(unsigned)>(3035880)(0);
 unsigned solid=fn<unsigned(*)(unsigned)>(3029376)(0x000000ffu);
 unsigned clear=fn<unsigned(*)(unsigned)>(3029376)(0x00000000u);
 float right=contentLeft(gui),coverTop=coverSlot(gui,0).y;
 Vertex strip[6]={{0,0,0,0,solid},{right,0,0,0,solid},
  {0,coverTop+h*.14f,0,0,solid},{right,stationScreenTopbarBottom(h),0,0,solid},
  {0,coverTop+h*.32f,0,0,clear},{right,coverTop+h*.065f,0,0,clear}};
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,6,4,5);
}
'''+s[b:]
s=s.replace(' if(!systemsMode){drawGameCornerBackdrop(w,h);return;}\n','')
anchor='(edge,0,w-edge,h,0x000000b3u,0x00000000u,false,4,5);'
assert anchor in s;s=s.replace(anchor,anchor+'\n if(!systemsMode)drawGameCornerBackdrop(w,h);');p.write_text(s,'utf8')
old='b8a153802c5c9e564679d726a6074b96307705a0e1677dfd4c8abd6677497ef2'
new='19212c8bcff669a5e0abd40ea7f74d20bb932d987a1947052a09e605c1929ab0'
for name in ['package_candidate.py','refresh_candidate.py']:
 p=ROOT/'recipes'/name;s=p.read_text('utf8');assert old in s;p.write_text(s.replace(old,new),'utf8')
for name in ['native','package']:
 current=(WORK/name).resolve();prior=(WORK/(name+'-before-user-correction')).resolve()
 assert current.parent==WORK.resolve() and prior.parent==WORK.resolve() and not prior.exists()
 current.rename(prior)
print('Username restored, counter smaller, original backdrop plus upper-left diagonal fade')
