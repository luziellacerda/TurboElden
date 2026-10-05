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
