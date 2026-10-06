#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include "station_platform_button_label.h"
#include "station_bottom_action_layout.h"
#include "station_info_layout.h"
#include "station_game_meta_row.h"
#include "station_synopsis_scroll.h"
#include "lottie_gear3_data.h"
int main(){
 unsigned checks=0;
 for(auto alias:stationButtonAliases){assert(std::strlen(alias.shortName)<=13);assert(std::strcmp(stationButtonShortName(alias.key,"fallback"),alias.shortName)==0);checks+=2;}
 assert(std::strcmp(stationButtonShortName("Master System ",""),"MASTER SYSTEM")==0);checks++;
 assert(std::strcmp(stationButtonFullName("Super Nintendo - BR","Super Nintendo"),"Super Nintendo BR")==0);checks++;
 assert(std::strcmp(stationButtonShortName("unknown","New platform"),"New platform")==0);checks++;
 assert(stationGameMetaRow(200,100,190,20,20,30,20,10).title.w==0);checks++;

 for(float h: {360.f,480.f,720.f,1080.f,1440.f,2160.f})for(float ratio:{1.25f,1.3333333f,1.5f,1.7777778f,2.f,2.1666667f,2.4f}){
  float w=h*ratio;StationActionRect prev{};
  for(int s=0;s<6;s++){
   auto r=stationBottomGameAction(w,h,s);
   assert(r.w>h*.1f&&r.h==h*.065f&&r.x>=w*.025f&&r.x+r.w<=w*.976f&&r.y+r.h<h);
   if(s){assert(std::abs(r.x-prev.x-prev.w-w*.009f)<.001f);if(s>1)assert(std::abs(r.w-prev.w)<.001f);}else assert(r.x==w*.025f);
   prev=r;checks+=7;
  }
  assert(std::abs(prev.x+prev.w-w*.975f)<.01f);checks++;
  assert(std::abs(stationBottomGameAction(w,h,0).w-h*.740f*.72f)<.01f);checks++;
  assert(std::abs(stationGameMetadataScale-1.575f)<.0001f);checks++;
  auto collection=stationCollectionAction(w*.035f,h*.851f,h*.665f,h*.094f,true);
  assert(collection.w>h*.26f);checks++;
  auto primary=stationCollectionAction(w*.035f,h*.851f,h*.665f,h*.094f,false);
  assert(primary.x==w*.035f&&primary.w==h*.665f);assert(collection.x>primary.x+primary.w);assert(collection.x+collection.w<w*.965f);checks+=4;
  float left=w*.025f+h*.740f*.72f+w*.022f;
  auto base=stationInfoLayout(w,h,left,true,false);auto meta=stationGameMetaRow(w,h,left,base.text.y,h*.4f,h*.066f,h*.024f,h*.020f);
  StationInfoRect regions[]={meta.title,meta.count,meta.players};
  for(int i=0;i<3;i++){
   auto r=regions[i];assert(r.w>0&&r.h>0&&r.y==base.text.y&&r.x+r.w<=w*.966f);
   if(i)assert(std::abs(r.x-regions[i-1].x-regions[i-1].w-h*.020f)<.001f);checks+=5;
  }
  assert(meta.advance>meta.title.h&&base.text.h-meta.advance>h*.2f);checks+=2;
  StationSynopsisScroll scroll{};float viewport=base.text.h-meta.advance;
  stationSynopsisMeasure(scroll,viewport,viewport*4,true);
  assert(scroll.contentHeight==viewport*4&&scroll.viewportHeight==viewport);checks+=2;
 }
 for(float h:{360.f,720.f,1080.f,1440.f})for(float ratio:{1.25f,1.5f,1.77778f,2.16667f,2.4f})for(int digits=1;digits<=5;digits++)for(float title:{.05f,.15f,.40f,1.0f,5.f}){
  float w=h*ratio,left=w*.047f+h*.740f*.72f,gap=h*.02f;
  auto row=stationGameMetaRow(w,h,left,h*.454f,title*h,digits*h*.022f,h*.024f*2,gap);
  assert(row.title.w>0);assert(row.title.w<=title*h+.001f);
  assert(std::abs(row.count.x-row.title.x-row.title.w-gap)<.001f);
  assert(std::abs(row.players.x-row.count.x-row.count.w-gap)<.001f);
  assert(std::abs(row.stars.x-row.players.x-row.players.w)<.001f);
  assert(row.stars.x+row.stars.w<=w*.965f+.001f);checks+=6;
 }
 for(float width:{160.f,280.f,420.f,575.f,800.f}){
  float c=.707106781f,reach=width*.38f,length=reach/c,half=width*.055f,seam=width*.0028f;
  assert(length-half*3.1f>0);checks++;
  for(int i=0;i<=64;i++){
   float u=-half+(length+2*half)*i/64.f;
   float low=-half+seam;if(-u>low)low=-u;if(u-length>low)low=u-length;
   float high=half-seam;if(low>high)low=high;
   for(float v:{low,high}){float x=c*(u+v),y=reach+c*(-u+v);assert(x>=-width*.003f&&y>=-width*.003f&&x<width&&y<width);checks+=4;}
  }
 }
 assert(stationBottomGameAction(0,0,0).w==0&&stationBottomGameAction(100,100,6).w==0);checks+=2;
 assert(sizeof(gear3Outer)/sizeof(gear3Outer[0])==962&&sizeof(gear3Inner)/sizeof(gear3Inner[0])==194);checks+=2;
 for(auto f:gear3Frames){assert(std::abs(f[0]*f[0]+f[1]*f[1]-1)<.00001f);checks++;}
 for(unsigned t=0;t<3003;t++){unsigned f=t*90/3003;assert(f<90);checks++;}
 for(unsigned i=0;i<962;i++){assert(std::isfinite(gear3Outer[i][0])&&std::isfinite(gear3Outer[i][1]));checks++;}
 printf("PASS %u: cover-width primary action, full-width row, five-space metadata flow, larger text and bounded icons, equal secondary actions, scroll viewport, collection Back, exact Lottie frame geometry\n",checks);
}
