#pragma once
static constexpr float stationGameMetadataScale=.70f*1.50f*1.50f;
struct StationGameMetaRow {StationInfoRect title,count,players,stars;float advance,icon,gap;};
// Widths are measured with the native font. No fixed-width columns or justified gaps.
static constexpr StationGameMetaRow stationGameMetaRow(float width,float height,float left,float top,float titleWidth,float countWidth,float playersWidth,float fiveSpaces){
 if(!(width>0&&height>0&&left>=0&&top>=0&&titleWidth>=0&&countWidth>=0&&playersWidth>=0&&fiveSpaces>0)||left>=width*.965f)return {};
 float row=height*.076f,icon=height*.0408f,gap=fiveSpaces;
 // Reserve at least one short title glyph while preserving five real spaces.
 // Compact only pictograms on narrow screens; the requested font stays unchanged.
 float available=width*.965f-left;
 float maxIcon=(available-countWidth-playersWidth-gap*3.4f-row*.5f)/7.6f;
 if(maxIcon<icon)icon=maxIcon;
 if(icon<=0)return {};
 float count=icon+gap*.2f+countWidth,players=icon+gap*.2f+playersWidth;
 float stars=icon*5+icon*.15f*4;
 float titleLimit=width*.965f-left-count-players-stars-3*gap;
 if(titleLimit<=0)return {};
 float title=titleWidth<titleLimit?titleWidth:titleLimit;
 float countX=left+title+gap,playersX=countX+count+gap,starsX=playersX+players+gap;
 return {{left,top,title,row},{countX,top,count,row},{playersX,top,players,row},{starsX,top,stars,row},height*.093f,icon,gap};
}
