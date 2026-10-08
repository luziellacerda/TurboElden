"""Apply the owner's final game-selection-only corrections to frozen inputs."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
SRC=WORK/'carousel-inputs/d0'

def replace(name,old,new):
 p=SRC/name;s=p.read_text('utf8');assert s.count(old)==1,(name,old);p.write_text(s.replace(old,new),'utf8')

replace('native_carousel.cpp','if(gui&&p==at<void*>(gui,0x1468))applyStationProfileName(p);',
 '''if(gui&&p==at<void*>(gui,0x1468)){
  if(!systemsMode)return; // Game selection has no account name.
  applyStationProfileName(p);
 }''')
replace('native_carousel.cpp','{0x22ea88,(void*)topSkinHook},',
 '{0x22ea88,(void*)topSkinHook},{0x23e270,(void*)drawProfileAvatarHook},')
assert '{0x3c16a0,0x23e270}' in (WORK/'carousel-inputs/d1/relocations.h').read_text()
replace('native_skin.h','bounds(p,0x1420,avatarX,h*.008f,systemsMode?w*.17f:w*.706f-avatarX,h*(systemsMode?.066f:.058f));',
 '''if(systemsMode)bounds(p,0x1420,avatarX,h*.008f,w*.17f,h*.066f);
 else bounds(p,0x1420,0,0,0,0); // Hidden account has no touch target.''')
replace('native_skin.h','if(caller==0x228168){float edge=stationScreenTopbarBottom(height),start=systemsMode?0:contentLeft(gui)-width*.012f;rect(start,0,width-start,edge,0x080C09f5);rect(start,edge,width-start,1.5f,0x28E65870);return;}',
 '''if(caller==0x228168){
   float edge=stationScreenTopbarBottom(height),start=systemsMode?0:contentLeft(gui)-width*.012f;
   if(systemsMode)rect(start,0,width-start,edge,0x080C09f5);
   else fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(start,0,width-start,edge,0x080C0900u,0x080C09ffu,false,4,5);
   rect(start,edge,width-start,1.5f,0x28E65870);return;
  }''')
replace('native_skin.h','skinTop=true;skinTopIndex=0;skinTopOwner=p;\n fn<void(*)(void*,void*)>(0x22ea88)(p,matrix);',
 '''skinTop=true;skinTopIndex=0;skinTopOwner=p;
 B profileLoading=at<B>(p,0x1461);
 if(!systemsMode)at<B>(p,0x1461)=0; // Suppress only this draw's profile loading arc.
 fn<void(*)(void*,void*)>(0x22ea88)(p,matrix);
 at<B>(p,0x1461)=profileLoading;''')
replace('native_skin.h','// Native geometry for the primary platform action;',
 '''// Verified ProfileAvatar::draw(float,float,float,float), original PLT slot 0x3c16a0.
 static void drawProfileAvatarHook(void*avatar,float x,float y,float radius,float alpha){
  if(skinTop&&skinTopOwner&&!systemsMode&&avatar==(B*)skinTopOwner+0x1430)return;
  fn<void(*)(void*,float,float,float,float)>(0x23e270)(avatar,x,y,radius,alpha);
 }
// Native geometry for the primary platform action;''')
p=SRC/'native_space.h';s=p.read_text('utf8');a=s.index('// One static upper-left');b=s.index('static void drawNativeSpace',a)
s=s[:a]+'''// One continuous, static full-height fade. The lateral space left of the
// focused cover stays fully black; fade starts behind the artwork, without
// an overlapping diagonal polygon or a visible horizontal join.
static void drawGameCornerBackdrop(float w,float h){
 fn<void(*)(unsigned)>(3035880)(0);
 auto cover=coverSlot(gui,0);
 float opaqueUntil=cover.x+cover.w*.80f;
 if(opaqueUntil>=w)opaqueUntil=w*.5f;
 Vertex strip[68];unsigned count=0;
 unsigned black=fn<unsigned(*)(unsigned)>(3029376)(0x000000ffu);
 strip[count++]={0,0,0,0,black};strip[count++]={0,h,0,0,black};
 for(int i=0;i<=32;i++){
  float t=i/32.f,x=opaqueUntil+(w-opaqueUntil)*t;
  unsigned alpha=(unsigned)(255.f*(1.f-t*t*(3.f-2.f*t))+.5f);
  unsigned color=fn<unsigned(*)(unsigned)>(3029376)(alpha);
  strip[count++]={x,0,0,0,color};strip[count++]={x,h,0,0,color};
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);
}
''' + s[b:]
s=s.replace(' // Renderer::drawRect bool is vertical,',' if(!systemsMode){drawGameCornerBackdrop(w,h);return;}\n // Renderer::drawRect bool is vertical,')
s=s.replace('\n if(!systemsMode)drawGameCornerBackdrop(w,h);','')
p.write_text(s,'utf8')
p=ROOT/'build_native.py';s=p.read_text();s=s.replace("['native_formation.h'","['native_carousel.cpp','native_formation.h'");p.write_text(s,'utf8')
old='19212c8bcff669a5e0abd40ea7f74d20bb932d987a1947052a09e605c1929ab0';current='449933b7cf9c77d330221da64ea764fffb15db9a673bd4602ae73d937f026e45'
for name in ['package_candidate.py','refresh_candidate.py']:
 p=ROOT/'recipes'/name;s=p.read_text();assert old in s;p.write_text(s.replace(old,current),'utf8')
for name in ['native','package']:
 p=WORK/name;dest=WORK/(name+'-before-hide-profile');assert p.resolve().parent==WORK.resolve() and not dest.exists();p.rename(dest)
p=ROOT/'evidence/installation-motorola-r85.json';dest=p.with_name('installation-motorola-r85-before-hide-profile.json');assert not dest.exists();p.rename(dest)
print('Game-only profile visibility, header fade and continuous black left backdrop applied.')
