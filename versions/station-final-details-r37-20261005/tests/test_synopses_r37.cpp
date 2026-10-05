#include <cstdio>
#include <cstring>
#include <cstdlib>
struct GameInfo {const char*system;const char*id;const char*name;const char*pages;const char*source;int pageCount;};
#include "../native/station_game_infos.h"
#include "station_game_lookup.h"
static int checks=0;
static void check(bool value,const char*message){++checks;if(!value){std::fprintf(stderr,"FAIL: %s\n",message);std::exit(1);}}
int main(){
 check(NSTATIONGAMEINFOS==2212,"exact frozen catalog count");
 for(int i=0;i<NSTATIONGAMEINFOS;++i){
  const auto&r=stationGameInfos[i];
  check(i==0||std::strcmp(stationGameInfos[i-1].id,r.id)<0,"strict ID sorting");
  check(findStationGameInfo(r.system,r.id)==&r,"all IDs find exact matching entry");
  check(findStationGameInfo("wrong-platform",r.id)==nullptr,"reject wrong platform");
  check(r.name&&r.name[0]&&r.source&&r.source[0],"names and provenance present");
  check(r.pages&&std::strlen(r.pages)>=30&&r.pageCount==1,"full nonempty scrollable synopsis");
  check(std::strchr(r.pages,'\f')==nullptr,"no hidden pagination truncation");
 }
 check(findStationGameInfo("Super Nintendo","")==nullptr,"unknown before first");
 check(findStationGameInfo("Super Nintendo","zzzz")==nullptr,"unknown after last");
 const auto*b=findStationGameInfo("Super Nintendo","826da6daebe9edbebffb3721f83abf12");
 check(b&&std::strstr(b->pages,"Rash e Pimple")&&std::strstr(b->pages,"Gamescape"),"Battletoads regression");
 const char*old="ab9773189dbfc1571ca0d56adb13ff32";
 check(stationSynopsisNeedsOverride(old,"Old Towers"),"exact reviewed title-only override");
 check(!stationSynopsisNeedsOverride(old,"Old Towers revised server synopsis"),"new server prose wins");
 check(!stationSynopsisNeedsOverride(old,"Old Towers "),"changed value not overridden");
 check(!stationSynopsisNeedsOverride(old,""),"empty handled by ordinary fallback");
 check(!stationSynopsisNeedsOverride("other-id","Old Towers"),"other ID not overridden");
 check(!stationSynopsisNeedsOverride(nullptr,"Old Towers"),"null ID safe");
 check(!stationSynopsisNeedsOverride(old,nullptr),"null description safe");
 check(!stationSynopsisNeedsOverride(nullptr,nullptr),"both null safe");
 std::printf("PASS: %d C++ runtime checks; all %d exact IDs/platforms; Battletoads and exact override verified.\n",checks,NSTATIONGAMEINFOS);
 return 0;
}