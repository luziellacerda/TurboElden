#pragma once
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
