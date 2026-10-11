#pragma once
struct StationActionRect {float x,y,w,h;};
static constexpr StationActionRect stationCompactActionRect(StationActionRect r){
 float inset=r.w*.06f;r.x+=inset;r.w-=inset*2;return r;
}
// One geometry source for drawing, labels and all six original hit targets.
// Match the focused game cover (native_formation.h) and fill the remaining row.
static constexpr StationActionRect stationBottomGameAction(float w,float h,int slot){
 if(!(w>0&&h>0)||slot<0||slot>5)return {};
 float bh=h*.065f,gap=w*.009f,x=w*.025f,hero=h*.790f*.828f;
 if(slot==0)return {x,h*.922f,hero,bh};
 float secondary=(w*.95f-hero-5*gap)/5.f;
 return {x+hero+gap+(slot-1)*(secondary+gap),h*.922f,secondary,bh};
}
static constexpr StationActionRect stationCollectionAction(float x,float y,float width,float height,bool back){
 if(!(width>0&&height>0))return {};
 return {x+(back?width+height*.24f:0),y,back?height*3.f:width,height};
}

// Rating layout in the first game action; caller measures the actual native label.
struct StationPrimaryRatingLayout {StationActionRect label,stars;float gap;};
static StationPrimaryRatingLayout stationPrimaryRatingLayout(StationActionRect r,float inset){
 float star=r.h*.30f,group=star*5.6f,gap=r.h*.22f;
 return {{r.x+inset,r.y,r.w-inset-r.h*.16f-group-gap,r.h},
         {r.x+r.w-r.h*.16f-group,r.y+(r.h-star)*.5f,group,star},gap};
}

// Action text near the button center; rating/players anchored at the right rim.
struct StationPrimaryMetaLayout {
 StationActionRect label,stars,folder,count,person,players;float scale;
};
static StationPrimaryMetaLayout stationPrimaryMetaLayout(StationActionRect r,float inset,float labelWidth,float countWidth,float playersWidth,float threeSpaces,int playerIcons=1){
 if(r.w<=inset||r.h<=0)return {};
 float gap=threeSpaces,small=playersWidth>0?threeSpaces/3.f:0.f,star=r.h*.435f,stars=star*5.6f,icon=r.h*.32f;
 float available=r.w-inset-r.h*.16f;
 float people=icon*(playerIcons>0?1.f+(playerIcons-1)*.76f:0.f);
 float starsGap=gap*10.f/3.f;
 float group=stars+gap+people+small+playersWidth;
 float total=labelWidth+starsGap+group;
 if(available<=0||total<=0)return {};
 float scale=total>available?available/total:1.f;
 float right=r.x+r.w-r.h*.16f,x=right-group*scale;
 float labelX=r.x+r.w*.48f-labelWidth*scale*.5f;
 float limit=x-starsGap*scale-labelWidth*scale;
 if(labelX>limit)labelX=limit;
 if(labelX<r.x+inset)labelX=r.x+inset;
 StationPrimaryMetaLayout out{};out.scale=scale;
 out.label={labelX,r.y,labelWidth*scale,r.h};
 out.stars={x,r.y+(r.h-star*scale)*.5f,stars*scale,star*scale};x+=out.stars.w+gap*scale;
 out.person={x,r.y+(r.h-icon*scale)*.5f,people*scale,icon*scale};x+=(people+small)*scale;
 out.players={x,r.y,playersWidth*scale,r.h};return out;
}
