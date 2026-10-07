#pragma once
#include "station_bottom_action_layout.h"

// Move the existing GuiStore settings control only on collection carousels.
// Its native drawing and input both read +0x1410; no extra button is created.
static constexpr StationActionRect stationCollectionSettingsRect(float w,float h,float headerX,bool systems,bool folders){
 float width=h*.118f,height=h*.084f;
 if(systems&&folders){
  // Same vertical center as ABRIR/VOLTAR (y=.851h, height=.094h).
  return {w*.965f-width,h*(.851f+.094f*.5f)-height*.5f,width,height};
 }
 return {headerX,0.f,width,height};
}
