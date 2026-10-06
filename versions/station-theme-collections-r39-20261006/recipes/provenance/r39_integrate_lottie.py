from pathlib import Path
import shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
def edit(n,a,b):
 p=N/n;s=p.read_text('utf8');assert a in s,(n,a[:80]);p.write_text(s.replace(a,b),'utf8')
shutil.copy2('r39_native_lottie.h',N/'native_theme_switch.h');shutil.copy2('r39_theme_switch_state.h',N/'station_theme_switch_state.h')
edit('native_carousel.cpp','#include "native_console.h"','#include "native_console.h"\n#include "native_theme_switch.h"')
edit('native_carousel.cpp','p==settingsThemeLabel||p==settingsThemeBlack||p==settingsThemeBlue||','p==settingsThemeLabel||p==settingsThemeBlack||p==settingsThemeBlue||p==stationThemeMainText||')
edit('native_carousel.cpp','drawPlayButtonStars(p);','drawPlayButtonStars(p);drawThemeSwitch(p,&formationMatrix,false);')
edit('native_carousel.cpp','gui=p;gear3Press(p,event);if(touchOnlineAction','gui=p;gear3Press(p,event);if(touchThemeSwitch(p,event,false))return true;if(touchOnlineAction')
# Keep the text labels; the two temporary buttons are replaced by the requested single switch.
edit('native_settings.h','setLongText(settingsThemeBlack,stationThemeId==0?"PRETO  (ATUAL)":"PRETO");','setLongText(settingsThemeBlack,stationThemeId==0?"PRETO":"AZUL");')
edit('native_settings.h','setLongText(settingsThemeBlue,stationThemeId==1?"AZUL  (ATUAL)":"AZUL");','setLongText(settingsThemeBlue,"TOQUE PARA TROCAR");')
edit('native_settings.h','place(settingsThemeBlack,black.x,black.y,black.w,black.h,.72f,1);place(settingsThemeBlue,blue.x,blue.y,blue.w,blue.h,.72f,1);','place(settingsThemeBlack,w*.49f,h*.153f,w*.12f,h*.066f,.72f,0);place(settingsThemeBlue,w*.65f,h*.153f,w*.28f,h*.066f,.55f,0);')
start=' for(int i=0;i<2;i++){\n  auto r=stationThemeChoice';p=N/'native_settings.h';s=p.read_text('utf8');a=s.index(start);b=s.index(' if(settingsThemeLabel)',a);s=s[:a]+' drawThemeSwitch(p,matrix,true);\n'+s[b:];p.write_text(s,'utf8')
edit('native_settings.h','int themeAction=settingsThemeGesture.touch(type,id,x,y,w,h);\n if(themeAction!=-1){if(themeAction>=0){bool saved=stationThemeChoose(themeAction);settingsRefreshThemeLabels(!saved);}return true;}','if(touchThemeSwitch(p,event,true)){settingsRefreshThemeLabels();return true;}')
edit('native_settings.h','settingsThemeGesture={};','settingsThemeGesture={};themeSwitchGesture={};')
# Clear stale gestures after leaving settings; initial labels reflect main-screen changes.
edit('native_settings.h','layoutSettingsSkin(p);settingsPainting=true;','layoutSettingsSkin(p);\n static unsigned themeRevision=~0u;if(themeRevision!=stationThemeRevision){themeRevision=stationThemeRevision;settingsRefreshThemeLabels();}\n settingsPainting=true;')
edit('native_info.h','static bool stationConsoleAvailable(const char*);','static bool stationConsoleAvailable(const char*);\nstatic void drawStationLottie(int,unsigned,StationInfoRect);\nstatic unsigned infoStarsStarted;')
edit('native_info.h','if(!changed)return;\n oldVisibleCount=','if(!changed)return;\n if(selectionChanged)infoStarsStarted=fn<unsigned(*)()>(0x39e240)();\n oldVisibleCount=')
edit('native_info.h','if(fill>0){clipSynopsis({star.x,star.y,star.w*fill,star.h});drawDetailsStar(star,0xFFD17Cffu);fn<void(*)()>(0x2e2aac)();}','''if(fill>0){
   unsigned elapsed=fn<unsigned(*)()>(0x39e240)()-infoStarsStarted;unsigned frame=elapsed>=2100u?126u:elapsed*60u/1000u;
   clipSynopsis({star.x,star.y,star.w*fill,star.h});
   // Original star occupies the central half of its square composition.
   drawStationLottie(1,frame,{star.x-star.w*.5f,star.y-star.h*.5f,star.w*2,star.h*2});fn<void(*)()>(0x2e2aac)();
  }''')
# Bundle originals, credits and prepared XMLs; downloaded ROM URLs are not included.
p=W/'package_r39.py';s=p.read_text('utf8');s=s.replace('additions = {}','''additions = {"assets/turborama-theme/"+p.name:p for p in (W/'assets').iterdir() if p.is_file()}
additions.update({"assets/station-metadata/"+p.name:p for p in (W/'metadata-xml').glob('*.xml')})''');p.write_text(s,'utf8')
print('Original Lottie switch integrated in settings and main footer; original stars in primary action; source assets bundled')
