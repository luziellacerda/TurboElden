#pragma once
struct StationActionRect {float x,y,w,h;};
static constexpr StationActionRect stationCompactActionRect(StationActionRect r){
 float inset=r.w*.06f;r.x+=inset;r.w-=inset*2;return r;
}
// One geometry source for drawing, labels and all six original hit targets.
// Match the focused game cover (native_formation.h) and fill the remaining row.
static constexpr StationActionRect stationBottomGameAction(float w,float h,int slot){
 if(!(w>0&&h>0)||slot<0||slot>5)return {};
 float bh=h*.065f,gap=bh*.16f,x=w*.025f,hero=h*.740f*.72f;
 if(slot==0)return {x,h*.908f,hero,bh};
 const float units[]={4.45f,3.0f,3.2f,3.7f,3.1f};
 float unit=(w*.95f-hero-5*gap)/17.45f;
 x+=hero+gap;
 for(int i=1;i<slot;i++)x+=unit*units[i-1]+gap;
 return {x,h*.908f,unit*units[slot-1],bh};
}
static constexpr StationActionRect stationCollectionAction(float x,float y,float width,float height,bool back){
 return stationCompactActionRect({x+(back?width*.55f:0),y,width*(back?.45f:.52f),height});
}
