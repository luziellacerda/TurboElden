#pragma once
struct StationActionRect {float x,y,w,h;};
static constexpr StationActionRect stationCompactActionRect(StationActionRect r){
 float inset=r.w*.06f;r.x+=inset;r.w-=inset*2;return r;
}
// Drawing, labels and touch all use this same rectangle for JOGAR ONLINE.
static constexpr StationActionRect stationBottomGameAction(float w,float h,int slot){
 float gap=w*.010f,bw=(w*.95f-5*gap)/6;
 return stationCompactActionRect({w*.025f+slot*(bw+gap),h*.908f,bw,h*.065f});
}

// Collections share the focus-cell width. Reserve enough of it for the arrow
// and all six letters of VOLTAR; the old 31% slot wrapped the final two letters.
static constexpr StationActionRect stationCollectionAction(float x,float y,float width,float height,bool back){
 return stationCompactActionRect({x+(back?width*.55f:0),y,width*(back?.45f:.52f),height});
}
