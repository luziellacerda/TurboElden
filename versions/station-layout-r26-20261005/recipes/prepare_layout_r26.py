from pathlib import Path
import shutil,json,hashlib
C=Path(__file__).resolve().parent
W=Path(r'E:\ESTUDO APK\work\station-layout-r26-20261005')
B=Path(r'E:\ESTUDO APK\work\station-console-panel-r25-20261005')
D=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
assert not W.exists()
for sub in ('native','tests','evidence','temp','device-evidence'):(W/sub).mkdir(parents=True)
N=W/'native'
for p in (B/'native').iterdir():
 if p.is_file():shutil.copy2(p,N/p.name)
for name in ('native_skin.h','native_netplay.h'):shutil.copy2(D/name,N/name)
def edit(name,old,new):
 p=N/name;s=p.read_text('utf8');assert s.count(old)==1,(name,old,s.count(old));p.write_text(s.replace(old,new),'utf8',newline='\n')
edit('station_game_panel_layout.h','StationInfoRect players,rating,photo,title;','StationInfoRect players,count,photo,title;')
edit('station_game_panel_layout.h','x+columnWidth*.48f,top,columnWidth*.52f','x+columnWidth*.55f,top,columnWidth*.45f')
edit('station_game_panel_layout.h','{x,ratingTop,columnWidth*.45f,ratingHeight}','{x,ratingTop,columnWidth*.52f,ratingHeight}')
(N/'station_header_layout.h').write_text('''#pragma once
// Installation/download state and the selected game's stars share the top bar.
// Include station_info_layout.h first; no new input controls are introduced.
static constexpr StationInfoRect stationStatusRect(float w,float h){return {w*.410f,h*.031f,w*.142f,h*.043f};}
static constexpr StationInfoRect stationHeaderStarsRect(float w,float h){return {w*.562f,h*.031f,w*.060f,h*.043f};}
''','utf8')
(N/'station_bottom_action_layout.h').write_text('''#pragma once
struct StationActionRect {float x,y,w,h;};
static constexpr StationActionRect stationCompactActionRect(StationActionRect r){
 float inset=r.w*.06f;r.x+=inset;r.w-=inset*2;return r;
}
// Drawing, labels and touch all use this same rectangle for JOGAR ONLINE.
static constexpr StationActionRect stationBottomGameAction(float w,float h,int slot){
 float gap=w*.010f,bw=(w*.95f-5*gap)/6;
 return stationCompactActionRect({w*.025f+slot*(bw+gap),h*.908f,bw,h*.065f});
}
''','utf8')
edit('native_carousel.cpp','#include "native_skin.h"','#include "station_bottom_action_layout.h"\n#include "native_skin.h"')
edit('native_carousel.cpp',' settingsSkinText(p);skinText(p);fn<void(*)(void*,void*)>(0x2d2dc4)(p,matrix);',''' settingsSkinText(p);skinText(p);
 if(gui&&!systemsMode&&!folderMode&&p==(B*)gui+0xb88){
  layoutGameStatusText(p);clipSynopsis(stationStatusRect(at<float>(gui,0x54),at<float>(gui,0x58)));
  fn<void(*)(void*,void*)>(0x2d2dc4)(p,matrix);fn<void(*)()>(0x2e2aac)();return;
 }
 fn<void(*)(void*,void*)>(0x2d2dc4)(p,matrix);''')
edit('native_skin.h','  bounds(buttons+i*20,4,x,h*(systemsMode?.851f:.908f),width,h*(systemsMode?.094f:.065f));','''  auto compact=stationCompactActionRect({x,h*(systemsMode?.851f:.908f),width,h*(systemsMode?.094f:.065f)});
  x=compact.x;width=compact.w;
  bounds(buttons+i*20,4,x,compact.y,width,compact.h);''')
edit('native_netplay.h',' float w=at<float>(p,0x54),h=at<float>(p,0x58),gap=w*.010f,bw=(w*.95f-5*gap)/6,x=w*.025f+bw+gap;',' float w=at<float>(p,0x54),h=at<float>(p,0x58);auto bounds=stationBottomGameAction(w,h,1);float x=bounds.x,bw=bounds.w;')
edit('native_netplay.h',' float w=at<float>(p,0x54),h=at<float>(p,0x58),gap=w*.010f,bw=(w*.95f-5*gap)/6,x0=w*.025f+bw+gap;',' float w=at<float>(p,0x54),h=at<float>(p,0x58);auto bounds=stationBottomGameAction(w,h,1);float x0=bounds.x,bw=bounds.w;')
edit('native_info.h','#include "station_players_label.h"','#include "station_players_label.h"\n#include "station_header_layout.h"')
edit('native_info.h','static StationInfoRect infoPlayersViewport{};','static StationInfoRect infoPlayersViewport{},infoHeaderStars{};static bool infoSinglePlayer;')
edit('native_info.h','static const char*infoConsoleKey;', '''static void layoutGameStatusText(void*t){
 static void*owner;static float oldW,oldH;alignas(8) static B previous[24]={};
 float w=at<float>(gui,0x54),h=at<float>(gui,0x58);auto r=stationStatusRect(w,h);
 const char*text=strData((B*)t+0xd0);
 // Relayout only on content/viewport changes or when the native header resets its bounds.
 if(owner==t&&oldW==w&&oldH==h&&strcmp(strData(previous),text)==0&&at<float>(t,0x54)*at<float>(t,0x38)<=r.w+.1f)return;
 owner=t;oldW=w;oldH=h;strAssign(previous,text);fitInfoText(t,r,.75f,0);
}
static const char*infoConsoleKey;''')
# Use no undocumented scale offset in the cache: the header source now reserves its exact width.
edit('native_info.h','&&at<float>(t,0x54)*at<float>(t,0x38)<=r.w+.1f','')
edit('native_skin.h',' place((B*)p+0xb88,w*.410f,h*.031f,w*.21f,h*.043f,.75f,0);',' place((B*)p+0xb88,w*.410f,h*.031f,w*(systemsMode?.21f:.142f),h*.043f,.75f,0);')
edit('native_info.h','infoTitleViewport={};infoPlayersViewport={};','infoTitleViewport={};infoPlayersViewport={};infoListCountViewport={};infoHeaderStars={};')
edit('native_info.h','infoViewport.x+infoViewport.w*.48f,h*.765f,infoViewport.w*.52f','infoViewport.x+infoViewport.w*.55f,h*.765f,infoViewport.w*.45f')
edit('native_info.h','infoDetailsLayout.rating={infoViewport.x,h*.765f,infoViewport.w*.45f','infoDetailsLayout.count={infoViewport.x,h*.765f,infoViewport.w*.52f')
edit('native_info.h','  setLongText(infoPlayersText,players);','  infoSinglePlayer=strcmp(players,"1 player")==0;\n  setLongText(infoPlayersText,players);')
edit('native_info.h','fitInfoText(infoPlayersText,infoPlayersViewport,.55f,0);','fitInfoText(infoPlayersText,infoPlayersViewport,.62f,0);')
edit('native_info.h','  float countIcon=h*.037f;infoListCountViewport={infoViewport.x+countIcon*1.35f,h*.851f,infoViewport.w-countIcon*1.35f,h*.045f};\n  fitInfoText(infoListCountText,infoListCountViewport,.80f,0);','''  auto countRow=infoDetailsLayout.count;float countIcon=countRow.h;
  infoListCountViewport={countRow.x+countIcon*1.35f,countRow.y,countRow.w-countIcon*1.35f,countRow.h};
  fitInfoText(infoListCountText,infoListCountViewport,.62f,0);
  infoHeaderStars=stationHeaderStarsRect(w,h);''')
edit('native_info.h','drawActionIcon(infoViewport.x,infoListCountViewport.y+(infoListCountViewport.h-icon)*.5f,icon,6,0x53DD8Cff);','drawActionIcon(infoDetailsLayout.count.x,infoListCountViewport.y+(infoListCountViewport.h-icon)*.5f,icon,6,0x53DD8Cff);')
edit('native_info.h',' drawDetailsPerson(row.x+row.h*.26f,row.y+row.h*.05f,row.h*.92f,0xA6DAB9ff);\n drawDetailsPerson(row.x,row.y+row.h*.20f,row.h*.77f,0x53DD8Cff);\n row=infoDetailsLayout.rating;',''' if(infoSinglePlayer)drawDetailsPerson(row.x+row.h*.12f,row.y+row.h*.05f,row.h*.92f,0x53DD8Cff);
 else{drawDetailsPerson(row.x+row.h*.26f,row.y+row.h*.05f,row.h*.92f,0xA6DAB9ff);drawDetailsPerson(row.x,row.y+row.h*.20f,row.h*.77f,0x53DD8Cff);}
 row=infoHeaderStars;''')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(W/'evidence/preparation.json').write_text(json.dumps({'base':str(B),'changes':'stars by status; count replaces old stars; aligned count/players; bottom widths -12% with actual hitboxes','sourceHashes':{p.name:sha(p) for p in N.iterdir() if p.is_file()}},indent=2)+'\n','utf8')
print('R26 prepared')
