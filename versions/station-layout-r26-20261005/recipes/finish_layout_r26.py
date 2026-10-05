from pathlib import Path
C=Path(__file__).resolve().parent
N=Path(r'E:\ESTUDO APK\work\station-layout-r26-20261005\native')
def edit(n,a,b):
 p=N/n;s=p.read_text('utf8');assert s.count(a)==1,(n,a,s.count(a));p.write_text(s.replace(a,b),'utf8',newline='\n')
edit('native_skin.h','static constexpr float gameActionTextScale=.60f;','static constexpr float gameActionTextScale=.60f;\nstatic bool gameStatusNeedsLayout=true;')
edit('native_skin.h',' owner=p;oldW=w;oldH=h;oldMode=systemsMode;oldFolder=folderMode;',' owner=p;oldW=w;oldH=h;oldMode=systemsMode;oldFolder=folderMode;gameStatusNeedsLayout=true;')
edit('native_info.h','if(owner==t&&oldW==w&&oldH==h&&strcmp(strData(previous),text)==0)return;','if(!gameStatusNeedsLayout&&owner==t&&oldW==w&&oldH==h&&strcmp(strData(previous),text)==0)return;')
edit('native_info.h','owner=t;oldW=w;oldH=h;strAssign(previous,text);fitInfoText(t,r,.75f,0);','owner=t;oldW=w;oldH=h;gameStatusNeedsLayout=false;strAssign(previous,text);fitInfoText(t,r,.75f,0);')
s=(N/'native_info.h').read_text('utf8');start=s.index(' row=infoHeaderStars;');end=s.index(' clipSynopsis(infoPlayersViewport);',start)
stars=s[start:end].replace(' row=infoHeaderStars;',' auto row=infoHeaderStars;')
s=s[:start]+s[end:]
pos=s.index('static void drawSynopsisScrollbar()')
s=s[:pos]+'''// Draw after the native header background, once per visible frame.
static void drawHeaderGameStars(void*p){
 if(systemsMode||folderMode||modal(p)||at<int>(p,0x370)<2||!infoGameDetailsVisible||infoHeaderStars.w<=0)return;
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);fn<void(*)(unsigned)>(0x2e52e8)(0);
'''+stars+'}\n'+s[pos:]
(N/'native_info.h').write_text(s,'utf8',newline='\n')
edit('native_carousel.cpp','drawOnlineAction(p,matrix);\n}','drawOnlineAction(p,matrix);drawHeaderGameStars(p);\n}')
test=(C/'test_console_panel_r25.cpp').read_text('utf8')
test=test.replace('p.rating','p.count').replace('players beside stars, same row','players beside folder count, same row')
test=test.replace('#include "console_assets.h"','#include "console_assets.h"\n#include "station_header_layout.h"\n#include "station_bottom_action_layout.h"')
test=test.replace(' for(const auto&a:stationConsoleAssets){\n  auto r=', ''' for(float w:{640.f,800.f,1280.f,1920.f,2340.f,3840.f})for(float h:{480.f,720.f,1080.f,1440.f}){
  auto status=stationStatusRect(w,h),stars=stationHeaderStarsRect(w,h);
  check(near(status.y,stars.y)&&near(status.h,stars.h),"header metadata vertically aligned");
  check(status.x+status.w<stars.x&&stars.x+stars.w<w*.634f,"header status/star/search do not overlap");
  for(int i=0;i<6;i++){
   auto r=stationBottomGameAction(w,h,i);
   check(near(r.w,w*.15f*.88f),"all game buttons are twelve percent narrower");
   check(near(r.x+r.w*.5f,w*.1f+i*w*.16f),"button center retained");
   check(r.x>0&&r.x+r.w<w&&r.y+r.h<h,"action bounds on screen");
   if(i<5)check(r.x+r.w<stationBottomGameAction(w,h,i+1).x,"touch targets do not overlap");
  }
  for(float width:{w*.05f,w*.12f,w*.30f}){
   auto r=stationCompactActionRect({w*.035f,h*.851f,width,h*.094f});
   check(near(r.w,width*.88f)&&near(r.x+r.w*.5f,w*.035f+width*.5f),"platform open/collection back also narrower");
  }
 }
 for(const auto&a:stationConsoleAssets){
  auto r=''')
test=test.replace('player labels, one metadata row, maximum console area, all alpha pixels, aspect and UV','player labels, folder/player row, header stars, twelve percent narrower actions, all alpha pixels, aspect and UV')
(C/'test_layout_r26.cpp').write_text(test,'utf8',newline='\n')
print('R26 header ordering, cached status fitting and shared bottom hit rectangles prepared')
