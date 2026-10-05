#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <initializer_list>
#include "station_info_layout.h"
#include "station_game_panel_layout.h"
#include "station_console_fit.h"
#include "station_players_label.h"
#include "console_assets.h"
static unsigned checks;
static void check(bool x,const char*msg){++checks;if(!x){std::fprintf(stderr,"FAIL %u %s\n",checks,msg);std::exit(2);}}
static bool near(float a,float b,float e=.002f){return std::fabs(a-b)<=e;}
int main(){
 struct Label{const char*in;const char*out;};
 for(const auto&v:{Label{"1","1 player"},Label{"2","2 players"},Label{"1-2","2 players"},Label{"1-4","4 players"},Label{"1-16","16 players"},Label{"8+","8+ players"},Label{"","-"},Label{nullptr,"-"},Label{"random","-"},Label{"1--2","-"}}){char b[64];stationPlayersLabel(v.in,b,sizeof(b));check(!strcmp(b,v.out),"player label exact/catalog data");}
 for(unsigned cap=0;cap<18;cap++){char guarded[24];std::memset(guarded,'X',24);stationPlayersLabel("1-16",guarded+1,cap);check(guarded[0]=='X'&&guarded[cap+1]=='X',"label bound");if(cap)check(std::memchr(guarded+1,0,cap),"label terminates");}
 for(float w:{640.f,800.f,1280.f,1920.f,2400.f,3840.f})for(float h:{480.f,720.f,1080.f,1920.f})for(float origin:{0.f,.18f,.30f,.50f,.77f})for(bool available:{false,true})for(bool systems:{false,true}){
  auto base=stationInfoLayout(w,h,w*origin,available,systems);auto p=stationGamePanelLayout(w,h,base);
  if(!base.photo){check(!p.active,"no phantom hardware column");continue;}
  check(p.active,"existing photo layout supported");
  check(near(p.players.y,p.rating.y),"players beside stars, same row");
  check(p.rating.x+p.rating.w<=p.players.x,"metadata does not overlap");
  check(p.players.x+p.players.w<=base.console.x+base.console.w+.01f,"metadata stays in column");
  check(p.photo.y>=p.players.y+p.players.h&&p.photo.y>=p.rating.y+p.rating.h,"console below row");
  check(p.photo.y+p.photo.h<=p.title.y+.01f,"console above title");
  check(p.title.y+p.title.h<h*.908f,"title above buttons");
  check(p.photo.h>=h*(.811f-.454f-.115f),"console area at least prior area");
  for(const auto&a:stationConsoleAssets){
   auto crop=stationConsoleBounds(a.rgba,a.width,a.height);auto fit=stationConsoleFit(p.photo,crop,a.width,a.height);
   check(fit.w>0&&fit.h>0,"hardware visible");
   check(fit.x>=p.photo.x-.01f&&fit.y>=p.photo.y-.01f&&fit.x+fit.w<=p.photo.x+p.photo.w+.01f&&fit.y+fit.h<=p.photo.y+p.photo.h+.01f,"hardware inside slot");
   check(near(fit.w,p.photo.w,.02f)||near(fit.h,p.photo.h,.02f),"maximum contain scale");
   check(near(fit.w/fit.h,float(crop.right-crop.left)/(crop.bottom-crop.top)),"hardware aspect preserved");
   check(fit.u0>=0&&fit.v0>=0&&fit.u1<=1&&fit.v1<=1,"UV valid");
  }
 }
 for(const auto&a:stationConsoleAssets){
  auto r=stationConsoleBounds(a.rgba,a.width,a.height);
  unsigned count=0;for(unsigned y=0;y<a.height;y++)for(unsigned x=0;x<a.width;x++)if(a.rgba[(y*a.width+x)*4+3]){check(x>=r.left&&x<r.right&&y>=r.top&&y<r.bottom,"every visible pixel preserved");count++;}
  std::printf("CONSOLE %s %u,%u,%u,%u visible=%u\n",a.key,r.left,r.top,r.right,r.bottom,count);
 }
 unsigned char empty[4*4*4]={};auto full=stationConsoleBounds(empty,4,4);check(full.left==0&&full.top==0&&full.right==4&&full.bottom==4,"transparent fallback");
 check(stationConsoleFit({0,0,100,100},{0,0,0,0},512,512).w==0,"invalid bounds rejected");
 std::printf("PASS %u: player labels, one metadata row, maximum console area, all alpha pixels, aspect and UV\n",checks);
}
