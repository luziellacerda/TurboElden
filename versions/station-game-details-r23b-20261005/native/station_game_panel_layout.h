// Pure geometry for the game details column. Include station_info_layout.h first.
// The caller centers the title within its rectangle; synopsis geometry is unchanged.
#pragma once

struct StationGamePanelLayout {
 StationInfoRect players,rating,photo,title;
 bool active;
};
static constexpr bool stationGamePanelFinite(float value){
 return value>=-3.402823466e+38F&&value<=3.402823466e+38F;
}
static constexpr StationGamePanelLayout stationGamePanelLayout(float width,float height,const StationInfoLayout&base){
 if(!base.photo||!stationGamePanelFinite(width)||!stationGamePanelFinite(height)||
    !(width>0.f)||!(height>0.f))return {{},{},{},{},false};
 const float x=base.console.x,columnWidth=base.console.w,top=base.text.y;
 if(!stationGamePanelFinite(x)||!stationGamePanelFinite(columnWidth)||!stationGamePanelFinite(top)||
    x<0.f||!(columnWidth>0.f)||x+columnWidth>width||top<0.f)return {{},{},{},{},false};
 const float playersHeight=height*.035f,ratingTop=top+height*.047f,ratingHeight=height*.034f;
 const float photoTop=top+height*.115f,photoBottom=height*.811f;
 const float titleTop=height*.825f,titleHeight=height*.070f;
 // Refuse impossible geometry instead of returning overlapping or negative regions.
 if(!(photoBottom>photoTop)||ratingTop+ratingHeight>photoTop||
    top+playersHeight>ratingTop||photoBottom>titleTop||titleTop+titleHeight>height*.908f)
  return {{},{},{},{},false};
 return {{x,top,columnWidth,playersHeight},
         {x,ratingTop,columnWidth,ratingHeight},
         {x,photoTop,columnWidth,photoBottom-photoTop},
         {x,titleTop,columnWidth,titleHeight},true};
}
