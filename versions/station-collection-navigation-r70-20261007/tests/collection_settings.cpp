#include "station_collection_settings_layout.h"

constexpr float distance(float a,float b){return a>b?a-b:b-a;}
constexpr bool same(float a,float b){return distance(a,b)<.001f;}
constexpr bool contains(StationActionRect r,float x,float y){
 return x>=r.x&&x<=r.x+r.w&&y>=r.y&&y<=r.y+r.h;
}
constexpr bool settingsPlacement(float w,float h){
 // Short/long authenticated names and fallback placement must all give the
 // same footer control; changes to name fitting cannot restore a top target.
 const float headerPositions[]={w*.15f,w*.22f,w*.32f};
 for(float headerX:headerPositions){
  for(int systems=0;systems<2;++systems)for(int folders=0;folders<2;++folders){
   auto r=stationCollectionSettingsRect(w,h,headerX,systems,folders);
   if(!same(r.w,h*.118f)||!same(r.h,h*.084f))return false;
   if(systems&&folders){
    if(!same(r.x+r.w,w*.965f)||!same(r.y+r.h*.5f,h*.898f))return false;
    if(!contains(r,r.x+r.w*.5f,h*.898f))return false;
    if(contains(r,headerX+r.w*.5f,h*.042f))return false;
    // Original artwork size/aspect stays fully onscreen at the native center.
    float artW=h*.059f*.34f*6.54f,artH=artW*159.f/202.f;
    float cx=r.x+r.w*.5f,cy=r.y+r.h*.5f;
    if(cx-artW*.5f<=w*.5f||cx+artW*.5f>=w)return false;
    if(cy-artH*.5f<=h*.80f||cy+artH*.5f>=h)return false;
    if(contains(r,r.x-1,r.y)||contains(r,r.x+r.w+1,r.y))return false;
   }else if(!same(r.x,headerX)||r.y!=0.f)return false;
  }
 }
 return true;
}
static_assert(settingsPlacement(2340.f,1080.f),"A56 landscape collections/profile/settings");
static_assert(settingsPlacement(2400.f,1080.f),"Other wide landscape collections/profile/settings");
static_assert(settingsPlacement(1920.f,1080.f),"16:9 collections/profile/settings");
static_assert(settingsPlacement(1280.f,720.f),"720p collections/profile/settings");
static_assert(settingsPlacement(1024.f,768.f),"4:3 collections/profile/settings");
