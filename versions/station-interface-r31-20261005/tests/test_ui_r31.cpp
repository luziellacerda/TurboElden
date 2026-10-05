#include <cassert>
#include <cmath>
#include <cstdio>
#include "station_bottom_action_layout.h"
#include "station_info_layout.h"
#include "station_game_meta_row.h"
#include "station_synopsis_scroll.h"
#include "lottie_gear3_data.h"
int main(){
 unsigned checks=0;
 for(float h: {360.f,480.f,720.f,1080.f,1440.f,2160.f})for(float ratio:{1.25f,1.3333333f,1.5f,1.7777778f,2.f,2.1666667f,2.4f}){
  float w=h*ratio;StationActionRect prev{};
  for(int s=0;s<6;s++){
   auto r=stationBottomGameAction(w,h,s);
   assert(r.w>h*.1f&&r.h==h*.065f&&r.x>=w*.025f&&r.x+r.w<=w*.976f&&r.y+r.h<h);
   if(s)assert(r.x>prev.x+prev.w);else assert(r.x==w*.025f);
   prev=r;checks+=7;
  }
  if(ratio>=1.77f)assert(prev.x+prev.w<w*.85f);
  auto collection=stationCollectionAction(w*.035f,h*.851f,h*.665f,h*.094f,true);
  assert(collection.w>h*.26f);checks++;
  float left=w*.025f+h*.740f*.72f+w*.022f;
  auto base=stationInfoLayout(w,h,left,true,false);auto meta=stationGameMetaRow(w,h,left,base.text.y);
  StationInfoRect regions[]={meta.title,meta.count,meta.players,meta.stars};
  for(int i=0;i<4;i++){
   auto r=regions[i];assert(r.w>0&&r.h>0&&r.y==base.text.y&&r.x+r.w<=w*.966f);
   if(i)assert(r.x>regions[i-1].x+regions[i-1].w);checks+=5;
  }
  assert(meta.advance>meta.title.h&&base.text.h-meta.advance>h*.2f);checks+=2;
  StationSynopsisScroll scroll{};float viewport=base.text.h-meta.advance;
  stationSynopsisMeasure(scroll,viewport,viewport*4,true);
  assert(scroll.contentHeight==viewport*4&&scroll.viewportHeight==viewport);checks+=2;
 }
 assert(stationBottomGameAction(0,0,0).w==0&&stationBottomGameAction(100,100,6).w==0);checks+=2;
 assert(sizeof(gear3Outer)/sizeof(gear3Outer[0])==962&&sizeof(gear3Inner)/sizeof(gear3Inner[0])==194);checks+=2;
 for(auto f:gear3Frames){assert(std::abs(f[0]*f[0]+f[1]*f[1]-1)<.00001f);checks++;}
 for(unsigned t=0;t<3003;t++){unsigned f=t*90/3003;assert(f<90);checks++;}
 for(unsigned i=0;i<962;i++){assert(std::isfinite(gear3Outer[i][0])&&std::isfinite(gear3Outer[i][1]));checks++;}
 printf("PASS %u: packed actions, row separation, scroll viewport, collection Back, exact Lottie frame geometry\n",checks);
}
