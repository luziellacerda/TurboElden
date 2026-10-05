
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <initializer_list>
#include "station_info_layout.h"
namespace prior {
#include "before/station_info_layout.h"
}
static int checks;
static void check(bool x){++checks;if(!x){std::fprintf(stderr,"FAIL %d\n",checks);std::exit(2);}}
template<class A,class B>static void sameRect(const A&a,const B&b){check(a.x==b.x);check(a.y==b.y);check(a.w==b.w);check(a.h==b.h);}
int main(int argc,char**){
 if(argc>1){check(!prior::stationInfoLayout(1920,1080,500,true,true).photo);return 0;}
 // Platforms and collections use systems=true; games use systems=false.
 for(float w:{320.f,720.f,800.f,1000.f,1280.f,1920.f,2400.f,3840.f})
 for(float h:{240.f,600.f,720.f,1080.f,1280.f,1920.f})
 for(float origin:{-.1f,0.f,.18f,.33f,.55f,.77f,.965f,1.25f})
 for(bool art:{false,true}){
  float left=w*origin,clamped=left<0?0:left>w*.965f?w*.965f:left;
  auto platform=stationInfoLayout(w,h,left,art,true);
  check(!platform.photo);check(platform.console.w==0.f);
  check(platform.text.x==clamped);check(platform.text.w==w*.965f-clamped);
  check(platform.text.y==h*.422f);check(platform.text.y+platform.text.h<=h*.813f);
  auto game=stationInfoLayout(w,h,left,art,false);
  auto oldGame=prior::stationInfoLayout(w,h,left,art,false);
  sameRect(game.text,oldGame.text);sameRect(game.console,oldGame.console);check(game.photo==oldGame.photo);
  auto legacy=stationInfoLayout(w,h,left,art);sameRect(legacy.text,game.text);check(legacy.photo==game.photo);
 }
 for(bool systems:{false,true})for(float w:{0.f,-1.f,std::numeric_limits<float>::quiet_NaN()}){
  auto x=stationInfoLayout(w,1080,100,true,systems);check(!x.photo);check(x.text.w==0.f);
 }
 check(stationInfoLayout(1920,1080,500,true,false).photo);
 check(!stationInfoLayout(1080,1920,200,true,false).photo);
 check(!stationInfoLayout(1920,1080,500,false,false).photo);
 std::printf("PASS %d checks: no console or reserved gap on systems/collections; games layout unchanged\n",checks);
}
