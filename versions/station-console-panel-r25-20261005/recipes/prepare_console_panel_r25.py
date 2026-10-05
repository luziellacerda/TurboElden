from pathlib import Path
import shutil,json,hashlib
C=Path(__file__).resolve().parent;W=Path(r'E:\ESTUDO APK\work\station-console-panel-r25-20261005');B=Path(r'E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005')
assert not W.exists()
for sub in ('native','tests','evidence','temp'):(W/sub).mkdir(parents=True)
for p in (B/'native').iterdir():
    if p.is_file():shutil.copy2(p,W/'native'/p.name)
N=W/'native'
for name in ('station_console_fit.h','station_players_label.h'):shutil.copy2(C/name,N/name)
s=(N/'native_info.h').read_text('utf8')
s=s.replace('#include "station_game_panel_layout.h"','#include "station_game_panel_layout.h"\n#include "station_players_label.h"')
s=s.replace('static void*infoPlayersText;static void*infoRatingText;static void*infoRatingLabel;','static void*infoPlayersText;')
s=s.replace('static StationInfoRect infoPlayersViewport{},infoRatingViewport{},infoRatingLabelViewport{};','static StationInfoRect infoPlayersViewport{};')
s=s.replace('infoRatingText=createInfoText(p,0xFFD17Cff);infoRatingLabel=createInfoText(p,0xADBFB4ff);','')
s=s.replace('infoPlayersViewport={};infoRatingViewport={};infoRatingLabelViewport={};','infoPlayersViewport={};')
s=s.replace('infoDetailsLayout.players={infoViewport.x,h*.765f,infoViewport.w,h*.035f};\n   infoDetailsLayout.rating={infoViewport.x,h*.807f,infoViewport.w,h*.034f};',
 '''infoDetailsLayout.players={infoViewport.x+infoViewport.w*.48f,h*.765f,infoViewport.w*.52f,h*.035f};
   infoDetailsLayout.rating={infoViewport.x,h*.765f,infoViewport.w*.45f,h*.035f};''')
start=s.index('  char players[96]={};');end=s.index('  char countLabel[48]',start)
s=s[:start]+'''  char players[96]={};
  stationPlayersLabel(infoDetails?infoDetails->players:"",players,sizeof(players));
  setLongText(infoPlayersText,players);
  auto row=infoDetailsLayout.players;float icon=row.h;
  infoPlayersViewport={row.x+icon*1.35f,row.y,row.w-icon*1.35f,row.h};
  fitInfoText(infoPlayersText,infoPlayersViewport,.55f,0);
  infoGameDetailsVisible=infoPlayersViewport.w>0&&infoViewport.h>0;
'''+s[end:]
s=s.replace(' fn<void(*)(void*,bool)>(0x277228)(infoRatingText,infoGameDetailsVisible);\n','')
s=s.replace(' fn<void(*)(void*,bool)>(0x277228)(infoRatingLabel,infoGameDetailsVisible&&infoDetailsLayout.active);\n','')
s=s.replace('||t==infoRatingText||t==infoRatingLabel','')
s=s.replace('row.w*.58f/5.f','row.w/5.f')
s=s.replace(' clipSynopsis(infoRatingViewport);fn<void(*)(void*,void*)>(0x2d2dc4)(infoRatingText,&formationMatrix);fn<void(*)()>(0x2e2aac)();\n','')
s=s.replace(' if(infoDetailsLayout.active){clipSynopsis(infoRatingLabelViewport);fn<void(*)(void*,void*)>(0x2d2dc4)(infoRatingLabel,&formationMatrix);fn<void(*)()>(0x2e2aac)();}\n','')
assert all(x not in s for x in ('infoRatingText','infoRatingLabel','Nota do catálogo','Sem avaliação'))
(N/'native_info.h').write_text(s,'utf8',newline='\n')
s=(N/'station_game_panel_layout.h').read_text('utf8')
s=s.replace('const float playersHeight=height*.035f,ratingTop=top+height*.047f,ratingHeight=height*.034f;',
 'const float playersHeight=height*.035f,ratingTop=top,ratingHeight=height*.035f;')
s=s.replace('photoTop=top+height*.115f,photoBottom=height*.811f','photoTop=top+height*.045f,photoBottom=height*.818f')
s=s.replace('top+playersHeight>ratingTop','top+playersHeight>photoTop')
s=s.replace('return {{x,top,columnWidth,playersHeight},\n         {x,ratingTop,columnWidth,ratingHeight},',
 'return {{x+columnWidth*.48f,top,columnWidth*.52f,playersHeight},\n         {x,ratingTop,columnWidth*.45f,ratingHeight},')
(N/'station_game_panel_layout.h').write_text(s,'utf8',newline='\n')
s=(N/'native_console.h').read_text('utf8')
s=s.replace('#include "console_assets.h"','#include "console_assets.h"\n#include "station_console_fit.h"')
s=s.replace('struct StationConsoleTexture {unsigned id;void*context;};','struct StationConsoleTexture {unsigned id;void*context;StationConsoleCrop crop;};')
s=s.replace(' if(!texture.id){',' if(!texture.id){\n  texture.crop=stationConsoleBounds(asset.rgba,asset.width,asset.height);')
start=s.index(' float scale=slot.w/');end=s.index(' g.UseProgram(stationConsoleProgram);',start)
s=s[:start]+''' // Fit actual visible hardware, not the transparent 512-square padding.
 auto fitted=stationConsoleFit(slot,texture.crop,asset.width,asset.height);
 unsigned color=fn<unsigned(*)(unsigned)>(0x2e3980)(0xffffffffu);
 Vertex q[4]={{fitted.x,fitted.y,fitted.u0,fitted.v0,color},
              {fitted.x,fitted.y+fitted.h,fitted.u0,fitted.v1,color},
              {fitted.x+fitted.w,fitted.y,fitted.u1,fitted.v0,color},
              {fitted.x+fitted.w,fitted.y+fitted.h,fitted.u1,fitted.v1,color}};
'''+s[end:]
(N/'native_console.h').write_text(s,'utf8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old={p.name:sha(p) for p in (B/'native').iterdir() if p.is_file()}
new={p.name:sha(p) for p in N.iterdir() if p.is_file()}
changed=[p for p in old if old[p]!=new[p]];assert set(changed)=={'native_info.h','native_console.h','station_game_panel_layout.h'}
(W/'evidence/preparation.json').write_text(json.dumps({'base':str(B),'baseNativeSHA256':old,'changed':changed,'added':sorted(set(new)-set(old))},indent=2)+'\n','utf8')
print('R25 prepared: one stars/player row, no numeric rating, visible console maximized')
