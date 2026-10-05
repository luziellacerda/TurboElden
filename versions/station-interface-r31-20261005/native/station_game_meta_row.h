#pragma once
struct StationGameMetaRow {StationInfoRect title,count,players,stars;float advance;};
static constexpr StationGameMetaRow stationGameMetaRow(float width,float height,float left,float top){
 if(!(width>0&&height>0&&left>=0&&top>=0)||left>=width*.965f)return {};
 float available=width*.965f-left,row=height*.040f,gap=available*.018f;
 float count=available*.15f,players=available*.085f,stars=available*.14f;
 float title=available-count-players-stars-3*gap;
 float countX=left+title+gap,playersX=countX+count+gap,starsX=playersX+players+gap;
 return {{left,top,title,row},{countX,top,count,row},{playersX,top,players,row},{starsX,top,stars,row},height*.054f};
}
