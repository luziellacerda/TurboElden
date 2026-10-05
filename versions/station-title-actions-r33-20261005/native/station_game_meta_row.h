#pragma once
static constexpr float stationGameMetadataScale=.70f*1.50f;
struct StationGameMetaRow {StationInfoRect title,count,players,stars;float advance;};
static constexpr StationGameMetaRow stationGameMetaRow(float width,float height,float left,float top){
 if(!(width>0&&height>0&&left>=0&&top>=0)||left>=width*.965f)return {};
 float available=width*.965f-left,row=height*.060f,gap=available*.012f;
 float count=available*.20f,players=available*.11f,stars=available*.18f;
 float title=available-count-players-stars-3*gap;
 float countX=left+title+gap,playersX=countX+count+gap,starsX=playersX+players+gap;
 return {{left,top,title,row},{countX,top,count,row},{playersX,top,players,row},{starsX,top,stars,row},height*.075f};
}
