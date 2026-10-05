#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
#include <limits>
#include "station_info_layout.h"
#include "station_game_panel_layout.h"

static unsigned checks;
static void check(bool ok,const char*message){
 ++checks;if(!ok){std::fprintf(stderr,"FAIL %u: %s\n",checks,message);std::exit(2);}
}
static void same(const StationInfoRect&a,const StationInfoRect&b){
 check(a.x==b.x&&a.y==b.y&&a.w==b.w&&a.h==b.h,"input rectangle must remain unchanged");
}
static bool zero(const StationInfoRect&r){return r.x==0&&r.y==0&&r.w==0&&r.h==0;}
static void inactive(const StationGamePanelLayout&p){
 check(!p.active,"invalid or unavailable column must be inactive");
 check(zero(p.players)&&zero(p.rating)&&zero(p.photo)&&zero(p.title),"inactive rectangles must be empty");
}
static void inspect(float width,float height,const StationInfoLayout&base){
 StationInfoLayout saved=base;
 auto panel=stationGamePanelLayout(width,height,base);
 same(base.text,saved.text);same(base.console,saved.console);check(base.photo==saved.photo,"input availability must remain unchanged");
 if(!base.photo){inactive(panel);return;}
 check(panel.active,"every valid existing photo column must support details");
 float tolerance=height*0.000001f;
 for(const auto&r:{panel.players,panel.rating,panel.photo,panel.title}){
  check(std::isfinite(r.x)&&std::isfinite(r.y)&&std::isfinite(r.w)&&std::isfinite(r.h),"all coordinates must be finite");
  check(r.w>0&&r.h>0,"active regions must have positive dimensions");
  check(r.x==base.console.x&&r.w==base.console.w,"all regions must occupy the full existing photo column");
  check(r.x>=0&&r.y>=0&&r.x+r.w<=width+width*0.000001f&&r.y+r.h<=height+tolerance,"regions must remain on screen");
  check(r.x+tolerance>=base.text.x+base.text.w,"details must not cover the synopsis");
 }
 check(panel.players.y==base.text.y,"players must start at the synopsis top");
 check(panel.players.h==height*.035f,"players row height");
 check(panel.rating.y==base.text.y+height*.047f,"rating starts after players plus gap");
 check(panel.rating.h==height*.034f,"rating row height");
 check(panel.photo.y==base.text.y+height*.115f,"photo starts below the metadata rows");
 check(std::fabs(panel.photo.y+panel.photo.h-height*.811f)<=tolerance,"photo ends at the required limit");
 check(panel.title.y==height*.825f&&panel.title.h==height*.070f,"game title uses the full reserved lower band");
 check(panel.players.y+panel.players.h<=panel.rating.y,"players and rating must not overlap");
 check(panel.rating.y+panel.rating.h<=panel.photo.y,"rating and photo must not overlap");
 check(panel.photo.y+panel.photo.h<=panel.title.y+tolerance,"photo and game title must not overlap");
 check(panel.title.y+panel.title.h<=height*.908f,"game title must stay above the footer");
 check(std::fabs(panel.title.x+panel.title.w*.5f-(base.console.x+base.console.w*.5f))<=width*0.000001f,"title center must match the console column center");
}

constexpr StationInfoLayout knownBase=stationInfoLayout(1920.f,1080.f,600.f,true,false);
constexpr StationGamePanelLayout knownPanel=stationGamePanelLayout(1920.f,1080.f,knownBase);
static_assert(knownPanel.active,"layout must work at compile time");
static_assert(knownPanel.title.y==1080.f*.825f,"fixed title anchor");
static_assert(knownPanel.players.x==knownBase.console.x,"same console column");

int main(){
 for(float width:{1.f,16.f,100.f,320.f,640.f,720.f,800.f,1000.f,1280.f,1920.f,2400.f,3840.f})
 for(float height:{.5f,9.f,80.f,240.f,600.f,720.f,1080.f,1280.f,1920.f})
 for(float origin:{0.f,.18f,.30f,.45f,.55f,.77f,.965f,1.25f})
 for(bool available:{false,true})for(bool systems:{false,true}){
  auto base=stationInfoLayout(width,height,width*origin,available,systems);
  inspect(width,height,base);
 }
 // Explicit aspect boundary, portrait, artwork absence and collections/platforms.
 check(stationGamePanelLayout(1000,800,stationInfoLayout(1000,800,300,true)).active,"inclusive landscape boundary");
 inactive(stationGamePanelLayout(999,800,stationInfoLayout(999,800,300,true)));
 inactive(stationGamePanelLayout(1080,1920,stationInfoLayout(1080,1920,200,true)));
 inactive(stationGamePanelLayout(1920,1080,stationInfoLayout(1920,1080,600,false)));
 inactive(stationGamePanelLayout(1920,1080,stationInfoLayout(1920,1080,600,true,true)));
 inspect(16,9,stationInfoLayout(16,9,4,true));
 const float nan=std::numeric_limits<float>::quiet_NaN(),infinity=std::numeric_limits<float>::infinity();
 for(float bad:{0.f,-1.f,nan,infinity,-infinity}){
  inactive(stationGamePanelLayout(bad,1080,knownBase));
  inactive(stationGamePanelLayout(1920,bad,knownBase));
 }
 for(float bad:{-1.f,nan,infinity,-infinity}){
  auto invalid=knownBase;invalid.console.x=bad;inactive(stationGamePanelLayout(1920,1080,invalid));
  invalid=knownBase;invalid.console.w=bad;inactive(stationGamePanelLayout(1920,1080,invalid));
  invalid=knownBase;invalid.text.y=bad;inactive(stationGamePanelLayout(1920,1080,invalid));
 }
 auto invalid=knownBase;invalid.console.w=0;inactive(stationGamePanelLayout(1920,1080,invalid));
 invalid=knownBase;invalid.console.x=1920;inactive(stationGamePanelLayout(1920,1080,invalid));
 invalid=knownBase;invalid.console.w=1921;inactive(stationGamePanelLayout(1920,1080,invalid));
 invalid=knownBase;invalid.text.y=1080*.811f;inactive(stationGamePanelLayout(1920,1080,invalid));
 invalid=knownBase;invalid.text.y=1080;inactive(stationGamePanelLayout(1920,1080,invalid));
 std::printf("PASS %u checks: game details column; complete synopsis preserved; ordered metadata/photo/title; footer clearance; landscape, portrait, tiny and invalid geometry\n",checks);
}
