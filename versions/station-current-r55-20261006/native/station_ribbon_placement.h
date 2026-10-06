#pragma once
// Crease intersections measured on the unchanged 1254x1254 R51 artwork.
// These are the card-edge anchors, not the transparent canvas edges.
struct StationRibbonPlacement {float x,y,w,h;};
static constexpr float stationRibbonCreaseX=192.f/1254.f;
static constexpr float stationRibbonCreaseY=192.f/1254.f;
static StationRibbonPlacement stationPlaceRibbon(float x,float y,float width,float height){
 if(!(width>0&&height>0))return {0,0,0,0};
 const float side=width*.68f;
 return {x-side*stationRibbonCreaseX,y-side*stationRibbonCreaseY,side,side};
}
