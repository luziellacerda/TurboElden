#include <cstring>
#include <cstdio>
#include <stdexcept>
using std::strcmp;
struct GameInfo {const char*system;const char*id;const char*name;const char*pages;const char*source;int pageCount;};
#include "native/station_game_infos.h"
#include "native/station_game_lookup.h"
int main(){
 int checks=0,mega=0,br=0,megaTexts=0,brTexts=0;
 auto check=[&](bool b){if(!b)throw std::runtime_error("native synopsis lookup");++checks;};
 for(const auto& row:stationGameInfos){
  auto found=findStationGameInfo(row.system,row.id);check(found==&row);
  check(findStationGameInfo("Wrong Platform",row.id)==nullptr);
  bool available=std::strncmp(row.pages,"Sinopse ainda",13)!=0;
  if(!strcmp(row.system,"MegaDrive")){mega++;megaTexts+=available;}
  if(!strcmp(row.system,"MegaDrive - BR")){br++;brTexts+=available;}
 }
 auto cut=findStationGameInfo("MegaDrive","ce3f245960b94e064f027ffd8aefe466");
 check(cut&&!strcmp(cut->name,"Cutthroat Island")&&std::strlen(cut->pages)>100);
 check(mega==887&&megaTexts==882);check(br==94&&brTexts==93);
 check(findStationGameInfo("MegaDrive","absent-identity")==nullptr);
 std::printf("PASS %d exact native synopsis lookup checks; Mega %d/%d and BR %d/%d descriptions\n",checks,megaTexts,mega,brTexts,br);
}
