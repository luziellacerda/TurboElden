#include <cassert>
#include <cstdio>
#include "station_compact_topbar.h"
#include "station_ribbon_placement.h"
int main(){int n=0;for(int h=320;h<=3840;h+=8){
 float line=stationTopbarBottom(h),top=h*.115f,width=h*.740f*.72f;
 assert(line<h*.105f);assert(stationTopbarActionY(h)+h*.059f<line);
 assert(h*.008f+h*.066f<line);assert(h*.018f+h*.05f<line);assert(h*.084f<line);
 for(int percent=10;percent<=100;percent+=5){
   auto ribbon=stationPlaceRibbon(0,top,width*percent/100.f,100);
   assert(ribbon.y+ribbon.h*108.f/1254.f>line+1.5f);n++;
 }n++;
 }std::printf("PASS %d header and unchanged-ribbon geometries; only black header reduced\n",n);}
