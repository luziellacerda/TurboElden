from pathlib import Path
import shutil,json,math,hashlib
W=Path(__file__).resolve().parent
BASE=Path(r'E:\ESTUDO APK\work\station-back-button-r30-20261005')
N=W/'native'
N.mkdir(exist_ok=True)
for p in (BASE/'native').iterdir():
    if p.is_file(): shutil.copy2(p,N/p.name)
for d in ('evidence','temp','tests','assets'): (W/d).mkdir(exist_ok=True)
def edit(name,old,new):
    p=N/name;s=p.read_text('utf8');assert s.count(old)==1,(name,old[:80],s.count(old));p.write_text(s.replace(old,new),'utf8')
def write(name,s): (N/name).write_text(s,'utf8')

write('station_bottom_action_layout.h',r'''#pragma once
struct StationActionRect {float x,y,w,h;};
static constexpr StationActionRect stationCompactActionRect(StationActionRect r){
 float inset=r.w*.06f;r.x+=inset;r.w-=inset*2;return r;
}
// One geometry source for drawing, labels and all six original hit targets.
// Natural widths follow the labels; only shrink the group on narrow viewports.
static constexpr StationActionRect stationBottomGameAction(float w,float h,int slot){
 if(!(w>0&&h>0)||slot<0||slot>5)return {};
 const float units[]={3.3f,4.45f,3.0f,3.2f,3.7f,3.1f};
 float bh=h*.065f,gap=bh*.16f,total=bh*20.75f+5*gap;
 float scale=total>w*.95f?w*.95f/total:1.f,x=w*.025f;
 for(int i=0;i<slot;i++)x+=(bh*units[i]+gap)*scale;
 return {x,h*.908f,bh*units[slot]*scale,bh};
}
static constexpr StationActionRect stationCollectionAction(float x,float y,float width,float height,bool back){
 return stationCompactActionRect({x+(back?width*.55f:0),y,width*(back?.45f:.52f),height});
}
''')
edit('native_skin.h','  x=compact.x;width=compact.w;','  if(!systemsMode)compact=stationBottomGameAction(w,h,i==0?0:i+1);\n  x=compact.x;width=compact.w;')
edit('native_skin.h','gameActionTextScale,1);','gameActionTextScale,systemsMode?1:0);')
edit('native_skin.h',' if(!systemsMode)rounded(w*.014f,h*.900f,w*.972f,h*.084f,0x080C09e8);',' if(!systemsMode){auto end=stationBottomGameAction(w,h,5);rounded(w*.014f,h*.900f,end.x+end.w-w*.014f+h*.012f,h*.084f,0x080C09e8);}')
edit('native_netplay.h','gameActionTextScale,1);','gameActionTextScale,0);')

write('station_game_meta_row.h',r'''#pragma once
struct StationGameMetaRow {StationInfoRect title,count,players,stars;float advance;};
static constexpr StationGameMetaRow stationGameMetaRow(float width,float height,float left,float top){
 if(!(width>0&&height>0&&left>=0&&top>=0)||left>=width*.965f)return {};
 float available=width*.965f-left,row=height*.040f,gap=available*.018f;
 float count=available*.15f,players=available*.085f,stars=available*.14f;
 float title=available-count-players-stars-3*gap;
 float countX=left+title+gap,playersX=countX+count+gap,starsX=playersX+players+gap;
 return {{left,top,title,row},{countX,top,count,row},{playersX,top,players,row},{starsX,top,stars,row},height*.054f};
}
''')
edit('native_info.h','#include "station_header_layout.h"','#include "station_header_layout.h"\n#include "station_game_meta_row.h"')
old='''  infoDetailsLayout=stationGamePanelLayout(w,h,infoGameLayout);
  if(infoDetailsLayout.active){
   infoTitleViewport=infoDetailsLayout.title;fitInfoText(infoTitle,infoTitleViewport,.70f,1);
   infoGameLayout.console=infoDetailsLayout.photo;
  }else{
   // Narrow screens retain a full-width synopsis and title; metadata uses the free lower band.
   infoDetailsLayout.players={infoViewport.x+infoViewport.w*.55f,h*.765f,infoViewport.w*.45f,h*.035f};
   infoDetailsLayout.count={infoViewport.x,h*.765f,infoViewport.w*.52f,h*.035f};
   if(infoViewport.y+infoViewport.h>h*.75f)infoViewport.h=h*.75f-infoViewport.y;
  }'''
new='''  auto meta=stationGameMetaRow(w,h,left,infoViewport.y);
  infoTitleViewport=meta.title;fitInfoText(infoTitle,infoTitleViewport,.70f,0);
  infoDetailsLayout.players=meta.players;infoDetailsLayout.count=meta.count;
  infoHeaderStars=meta.stars;
  infoViewport.y+=meta.advance;infoViewport.h-=meta.advance;
  if(infoGameLayout.photo){infoGameLayout.console.y+=meta.advance;infoGameLayout.console.h-=meta.advance;}
  infoGameLayout.text=infoViewport;'''
edit('native_info.h',old,new)
edit('native_info.h','  setLongText(infoPlayersText,players);','  for(char*q=players;*q;q++)if(*q==\' \'){*q=0;break;} // Numeric value beside the player icon.\n  setLongText(infoPlayersText,players);')
edit('native_info.h','  infoHeaderStars=stationHeaderStarsRect(w,h);','  // Rating remains in the single synopsis header row, never duplicated above.')

# Convert this exact two-layer Lottie asset to native stroke strips. No timers,
# texture decoding or third-party runtime is needed for this small vector asset.
asset=json.loads((W/'gear-original.json').read_text())
assert asset['w']==200 and asset['h']==200 and len(asset['layers'])==2 and not asset['assets']
circle,gear=asset['layers']
path=gear['shapes'][0]['it'][0]['ks']['k'];assert len(path['v'])==40 and path['c']
def bez(a,b,c,d,t):return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
points=[]
for i,a in enumerate(path['v']):
    j=(i+1)%len(path['v']);b=path['v'][j]
    for step in range(12):
        t=step/12
        points.append(tuple(bez(a[k],a[k]+path['o'][i][k],b[k]+path['i'][j][k],b[k],t) for k in range(2)))
def strip(pts,thickness=3):
    out=[]
    for i,p in enumerate(pts):
        prev,nxt=pts[i-1],pts[(i+1)%len(pts)]
        def norm(a,b):
            dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);assert l>1e-8
            return (-dy/l,dx/l)
        a,b=norm(prev,p),norm(p,nxt);sx,sy=a[0]+b[0],a[1]+b[1]
        factor=thickness*.5/(sx*b[0]+sy*b[1]);ox,oy=sx*factor,sy*factor
        assert math.hypot(ox,oy)<=6.0001
        out.extend([(p[0]+ox,p[1]+oy),(p[0]-ox,p[1]-oy)])
    return out+out[:2]
outer=strip(points)
ellipse=circle['shapes'][0]['it'][0];tr=circle['shapes'][0]['it'][2]['p']['k'];radius=ellipse['s']['k'][0]/2
inner=strip([(tr[0]+radius*math.cos(i*math.tau/96),tr[1]+radius*math.sin(i*math.tau/96)) for i in range(96)])
key=gear['ks']['r']['k'][0];end=gear['ks']['r']['k'][1];frames=[]
for frame in range(90):
    x=min(1,frame/end['t']);lo,hi=0.,1.
    for _ in range(50):
        t=(lo+hi)/2
        if bez(0,key['o']['x'],key['i']['x'],1,t)<x:lo=t
        else:hi=t
    ease=bez(0,key['o']['y'],key['i']['y'],1,(lo+hi)/2)
    angle=math.radians(key['s'][0]+(end['s'][0]-key['s'][0])*ease)
    frames.append((math.cos(angle),math.sin(angle)))
def array(name,values):return 'static constexpr float '+name+'[][2]={\n'+',\n'.join('{%.9ff,%.9ff}'%p for p in values)+'\n};\n'
write('lottie_gear3_data.h','// Gear 3 by Giovana Pontes. Lottie Simple License FL9.13.21.\n// Generated from the bundled original JSON; visible bounds fitted to the existing icon.\n#pragma once\n'+array('gear3Outer',outer)+array('gear3Inner',inner)+array('gear3Frames',frames))
extent=max(math.hypot(*p) for p in outer)
write('native_lottie_gear.h',r'''// Exact Gear 3 Lottie geometry and easing, sampled at the source frame rate.
#include "lottie_gear3_data.h"
static void drawLottieGearHook(void*p,float cx,float cy,float radius,unsigned color){
 if(!skinTop){fn<void(*)(void*,float,float,float,unsigned)>(0x221854)(p,cx,cy,radius,color);return;}
 unsigned tick=fn<unsigned(*)()>(0x39e240)();unsigned frame=(tick%3003u)*90u/3003u;
 float co=gear3Frames[frame][0],si=gear3Frames[frame][1];
 float scale=radius/EXTENT;
 unsigned packed=fn<unsigned(*)(unsigned)>(0x2e3980)(0xB78E3100u|(color&255));
 Vertex vertices[sizeof(gear3Outer)/sizeof(gear3Outer[0])];
 fn<void(*)(unsigned)>(0x2e52e8)(0);
 for(int layer=0;layer<2;layer++){
  const float(*data)[2]=layer?gear3Inner:gear3Outer;
  unsigned count=layer?sizeof(gear3Inner)/sizeof(gear3Inner[0]):sizeof(gear3Outer)/sizeof(gear3Outer[0]);
  for(unsigned i=0;i<count;i++){
   float x=data[i][0],y=data[i][1];if(!layer){float xx=x*co-y*si;y=x*si+y*co;x=xx;}
   vertices[i]={cx+x*scale,cy+y*scale,0,0,packed};
  }
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(vertices,count,4,5);
 }
}
'''.replace('EXTENT','%.9ff'%extent))
edit('native_skin.h','#include "native_game_actions.h"','#include "native_game_actions.h"\n#include "native_lottie_gear.h"')
edit('native_carousel.cpp','{0x22ea88,(void*)topSkinHook}','{0x22ea88,(void*)topSkinHook},{0x221854,(void*)drawLottieGearHook}')

shutil.copy2(W/'gear-original.json',W/'assets/gear-3.json')
license_text='''Gear 3 — Giovana Pontes
Source: https://lottiefiles.com/pt/free-animation/gear-3-oz2ZcDdYz1
Asset: https://assets-v2.lottiefiles.com/a/edcff18c-1186-11ee-8c70-4b6e696dc91b/C2WjSyOmq2.lottie
License: Lottie Simple License (FL9.13.21)
https://lottiefiles.com/page/license
Original JSON included. Native stroke geometry and frame table derived for the existing renderer.
This animation and its derivatives retain the Lottie Simple License; project restrictions do not override it.
'''
(W/'assets/gear-3-NOTICE.txt').write_text(license_text,'utf8')
shutil.copy2(W/'license.html',W/'assets/gear-3-LICENSE.html')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(W/'evidence/lottie-conversion.json').write_text(json.dumps({'sourceSHA256':sha(W/'gear-original.json'),'sourceFPS':asset['fr'],'durationFrames':asset['op'],'outerVertices':len(outer),'innerVertices':len(inner),'frameSamples':len(frames),'stroke':3,'color':'B78E31','extent':extent,'assetCredit':'Giovana Pontes','license':'Lottie Simple License FL9.13.21'},indent=2),'utf8')
print('Base copied, actions/metadata/Lottie prepared; installed tag added separately.')
