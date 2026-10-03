#include "native/station_info_layout.h"
constexpr bool verifyLayouts(){
 constexpr float widths[]={640,800,1080,1280,1360,1920,2340,3840};
 constexpr float heights[]={360,480,720,768,1080,1440,2160,2340};
 for(float w:widths)for(float h:heights)for(int photo=0;photo<2;photo++){
  // Same selected game cover boundary used by coverSlot/contentLeft.
  float left=w*.025f+h*.740f*.72f+w*.022f;
  // Production is landscape; only check usable native card formations.
  if(left>w*.7f)continue;
  auto layout=stationInfoLayout(w,h,left,photo);
  if(layout.text.w<=0||layout.text.h<=0||layout.text.x<0||layout.text.y<0)return false;
  if(layout.text.x+layout.text.w>w*.966f||layout.text.y+layout.text.h>h*.831f)return false;
  if(layout.photo){
   if(!photo||layout.console.w<=0||layout.console.h<=0)return false;
   if(layout.text.x+layout.text.w>=layout.console.x)return false;
   if(layout.console.x+layout.console.w>w*.966f)return false;
  }
 }
 return true;
}
static_assert(verifyLayouts(),"Text and console rectangles must stay on screen without overlaps");
