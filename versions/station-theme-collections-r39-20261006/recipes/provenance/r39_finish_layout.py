from pathlib import Path
import shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native';D=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native')
def edit(n,a,b):
 p=N/n;s=p.read_text('utf8');assert a in s,(n,a[:75]);p.write_text(s.replace(a,b),'utf8')
edit('native_carousel.cpp','if(textOffset==0x7f8||textOffset==0xa58||(systemsMode&&(textOffset==0x928||textOffset==0xb88)))return;','if(textOffset==0x7f8||textOffset==0xa58||textOffset==0x928||textOffset==0xb88)return;')
edit('native_carousel.cpp','settingsSkinText(p);skinText(p);','settingsSkinText(p);skinText(p);\n if(gui&&!systemsMode&&!folderMode&&p==(B*)gui+0xe00)layoutPrimaryGameLabel(p);')
edit('native_carousel.cpp','drawHeaderGameStars(p);','drawPlayButtonStars(p);')
edit('native_info.h','static void drawHeaderGameStars(void*p){','static void drawPlayButtonStars(void*p){')
edit('native_info.h','auto row=infoHeaderStars;float size=infoMetadataIcon,step=size*1.15f;','auto row=infoPlayStars;float size=row.h,step=size*1.15f;')
edit('native_info.h','||infoHeaderStars.w<=0)return;','||infoPlayStars.w<=0)return;')
insert='''// The existing primary action label owns its text; fit stars beside it without changing the action.
static StationInfoRect infoPlayStars{};
static void layoutPrimaryGameLabel(void*t){
 float w=at<float>(gui,0x54),h=at<float>(gui,0x58);auto r=stationBottomGameAction(w,h,0);
 static void*owner;static float oldW,oldH;alignas(8) static B previous[24]={};
 const char*label=strData((B*)t+0xd0);
 if(owner==t&&oldW==w&&oldH==h&&strcmp(strData(previous),label)==0&&!gameStatusNeedsLayout)return;
 owner=t;oldW=w;oldH=h;strAssign(previous,label);
 auto layout=stationPrimaryRatingLayout(r,actionLabelInset(r.h));
 float used=fitGameTitleOneLine(t,label,{layout.label.x,layout.label.y,layout.label.w,layout.label.h},gameActionTextScale);
 infoPlayStars={layout.label.x+used+layout.gap,layout.stars.y,layout.stars.w,layout.stars.h};
}
'''
edit('native_info.h','// Draw after the native header background, once per visible frame.',insert+'// Draw after the native primary button fill, once per visible frame.')
edit('native_skin.h','static bool settingsSkinRect(U,float,float,float,float,unsigned);','static bool settingsSkinRect(U,float,float,float,float,unsigned);\nstatic void drawTopAction(float,float,float,float,int,bool);')
edit('native_skin.h','rounded(x,y,w,h,active?0x147D32ff:0x151D17ff);skinTopIndex++;','drawTopAction(x,y,w,h,skinTopIndex,active);skinTopIndex++;')
edit('native_skin.h','// Replace native glow with the flat button fill.','// Native action style supplies its own rim and fill.')
edit('native_skin.h','place((B*)p+0x1470,w*.848f,h*.023f,w*.127f,h*.059f,.70f,1);','place((B*)p+0x1470,w*.848f+actionLabelInset(h*.059f),h*.023f,w*.127f-actionLabelInset(h*.059f)-h*.009f,h*.059f,.62f,0);')
edit('native_skin.h','place((B*)p+0x15a0,w*.718f,h*.023f,w*.118f,h*.059f,.70f,1);','place((B*)p+0x15a0,w*.718f+actionLabelInset(h*.059f),h*.023f,w*.118f-actionLabelInset(h*.059f)-h*.009f,h*.059f,.62f,0);')
edit('native_skin.h','#include "native_lottie_gear.h"','''#include "native_lottie_gear.h"
static void drawTopAction(float x,float y,float w,float h,int index,bool active){
 if(index>1){rounded(x,y,w,h,0x151D17ff);return;}
 drawGameAction(x,y,w,h,index==1?8:folderMode?10:9,false,active,false);
}''')
shutil.copy2(D/'native_game_actions.h',N/'native_game_actions.h')
edit('native_game_actions.h','0x62F49Bff,0x66C9FFff};','0x62F49Bff,0x66C9FFff,0x66C9FFff,0x62F49Bff,0xB699FFFF};')
edit('native_game_actions.h','slot<8?slot:5','slot<11?slot:5')
edit('native_game_actions.h','if(slot==0){m.quad','''if(slot==8){for(int row=0;row<2;row++)for(int col=0;col<2;col++)box(.12f+col*.46f,.12f+row*.46f,.30f,.30f);}
 else if(slot==9){box(.12f,.12f,.76f,.76f);line(.25f,.5f,.44f,.69f);line(.44f,.69f,.76f,.31f);}
 else if(slot==10){line(.12f,.24f,.43f,.24f);line(.43f,.24f,.55f,.36f);line(.55f,.36f,.88f,.36f);line(.88f,.36f,.88f,.82f);line(.88f,.82f,.12f,.82f);line(.12f,.82f,.12f,.24f);}
 else if(slot==0){m.quad''')
edit('station_game_meta_row.h','gap*3.4f-row*.5f)/7.6f','gap*2.4f-row*.5f)/2.f')
edit('station_game_meta_row.h','float stars=icon*5+icon*.15f*4;','float stars=0; // Rating moved into the primary action button.')
edit('station_game_meta_row.h','-players-stars-3*gap','-players-2*gap')
edit('station_game_meta_row.h','starsX=playersX+players+gap','starsX=playersX+players')
p=N/'station_bottom_action_layout.h';s=p.read_text('utf8');s+='''
// Rating layout in the first game action; caller measures the actual native label.
struct StationPrimaryRatingLayout {StationActionRect label,stars;float gap;};
static StationPrimaryRatingLayout stationPrimaryRatingLayout(StationActionRect r,float inset){
 float star=r.h*.30f,group=star*5.6f,gap=r.h*.22f;
 return {{r.x+inset,r.y,r.w-inset-r.h*.16f-group-gap,r.h},
         {r.x+r.w-r.h*.16f-group,r.y+(r.h-star)*.5f,group,star},gap};
}
''';p.write_text(s,'utf8')
# Adapt old tests only to the explicitly changed rating location.
p=W/'tests/test_ui_r37.cpp';s=p.read_text('utf8').replace('meta.title,meta.count,meta.players,meta.stars','meta.title,meta.count,meta.players').replace('for(int i=0;i<4;i++){','for(int i=0;i<3;i++){').replace('row.stars.x-row.players.x-row.players.w-gap','row.stars.x-row.players.x-row.players.w');p.write_text(s,'utf8')
print('Header duplicates removed; stars beside primary action; top-right controls restyled')
