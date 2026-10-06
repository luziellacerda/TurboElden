#pragma once
struct StationActionRect {float x,y,w,h;};
static constexpr StationActionRect stationCompactActionRect(StationActionRect r){
 float inset=r.w*.06f;r.x+=inset;r.w-=inset*2;return r;
}
// One geometry source for drawing, labels and all six original hit targets.
// Match the focused game cover (native_formation.h) and fill the remaining row.
static constexpr StationActionRect stationBottomGameAction(float w,float h,int slot){
 if(!(w>0&&h>0)||slot<0||slot>5)return {};
 float bh=h*.065f,gap=w*.009f,x=w*.025f,hero=h*.740f*.72f;
 if(slot==0)return {x,h*.908f,hero,bh};
 float secondary=(w*.95f-hero-5*gap)/5.f;
 return {x+hero+gap+(slot-1)*(secondary+gap),h*.908f,secondary,bh};
}
static constexpr StationActionRect stationCollectionAction(float x,float y,float width,float height,bool back){
 if(!(width>0&&height>0))return {};
 return {x+(back?width+height*.24f:0),y,back?height*3.f:width,height};
}
