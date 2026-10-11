"""Compact native settings with two explicit human Sony launcher actions.

Preserves native tabs, value actions, scrolling and the original 48dp targets.
Sony owns one row above the options viewport. Static cards restore the existing
matrix before drawing; JNI runs only after a completed human tap.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json

SOURCE_SHA='7d7e4d388319594d7bfc934105d1d09c75af09a3887f4b1f8bb1dcf14d9b3abb'

BRIDGE='''// Human settings hand-off only. No game path, online command or frame polling.
static bool openStationSonySettings(const char*platform){
 if(!platform||(strcmp(platform,"ps3")!=0&&strcmp(platform,"ps4")!=0))return false;
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 jclass activityClass=nullptr,loaderClass=nullptr,bridge=nullptr;
 jobject loader=nullptr;jstring className=nullptr,system=nullptr;bool accepted=false;
 do{
  activityClass=env->GetObjectClass(activity);if(!activityClass||env->ExceptionCheck())break;
  jmethodID getLoader=env->GetMethodID(activityClass,"getClassLoader","()Ljava/lang/ClassLoader;");
  if(!getLoader||env->ExceptionCheck())break;
  loader=env->CallObjectMethod(activity,getLoader);if(!loader||env->ExceptionCheck())break;
  loaderClass=env->GetObjectClass(loader);if(!loaderClass||env->ExceptionCheck())break;
  jmethodID load=env->GetMethodID(loaderClass,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;");
  if(!load||env->ExceptionCheck())break;
  className=env->NewStringUTF("org.emulationstation.frontend.offline.StationSonyOfflineActivity");
  if(!className||env->ExceptionCheck())break;
  bridge=(jclass)env->CallObjectMethod(loader,load,className);if(!bridge||env->ExceptionCheck())break;
  jmethodID open=env->GetStaticMethodID(bridge,"openSettings","(Landroid/app/Activity;Ljava/lang/String;)Z");
  if(!open||env->ExceptionCheck())break;
  system=env->NewStringUTF(platform);if(!system||env->ExceptionCheck())break;
  accepted=env->CallStaticBooleanMethod(bridge,open,activity,system)==JNI_TRUE;
 }while(false);
 if(env->ExceptionCheck()){env->ExceptionClear();accepted=false;log("Sony settings bridge unavailable");}
 if(system)env->DeleteLocalRef(system);if(bridge)env->DeleteLocalRef(bridge);
 if(className)env->DeleteLocalRef(className);if(loaderClass)env->DeleteLocalRef(loaderClass);
 if(loader)env->DeleteLocalRef(loader);if(activityClass)env->DeleteLocalRef(activityClass);
 env->DeleteLocalRef(activity);
 if(accepted){stopSystemVideo();pauseRetroMusicForGame();log("Sony settings request dispatched");}
 return accepted;
}
'''

# Whole UI methods are pinned and exactly reversible; non-UI methods stay intact.
REPLACEMENTS=(
 ('''static void*settingsEffectsLabel;
''',
  '''static void*settingsEffectsLabel;
static void*settingsSonyPs3Text;static void*settingsSonyPs4Text;
'''),
 ('''static StationThemeRect settingsEffectsRect,settingsBackRect,settingsNetworkRect,settingsSkyRect;
''',
  '''static StationThemeRect settingsEffectsRect,settingsBackRect,settingsNetworkRect,settingsSkyRect;
static StationThemeRect settingsSonyPs3Rect,settingsSonyPs4Rect;
static float settingsRowsY,settingsRowsClipHeight;
'''),
 ('''static void settingsRefreshThemeLabels(bool failed=false){
 if(!settingsThemeLabel)return;
 setLongText(settingsThemeLabel,failed?"COR: FALHA AO SALVAR":"COR DO FUNDO");
 setLongText(settingsThemeBlack,stationThemeId==0?"PRETO":"AZUL");
 int background=stationGraphicsBackground();setLongText(settingsThemeBlue,background==1?"ESTILO DO FUNDO ONDAS":background==0?"ESTILO DO FUNDO CÉU":"FUNDO DESLIGADO");
}
''',
  '''static void settingsRefreshThemeLabels(bool failed=false){
 if(!settingsThemeLabel)return;
 setLongText(settingsThemeLabel,failed?"COR: ERRO":"COR DO FUNDO");
 setLongText(settingsThemeBlack,stationThemeId==0?"PRETO":"AZUL");
 int background=stationGraphicsBackground();setLongText(settingsThemeBlue,background==1?"ONDAS":background==0?"CÉU":"DESLIGADO");
}
'''),
 ('''static void requestSettingsClose(void*p){
''', BRIDGE+'''static void requestSettingsClose(void*p){
'''),
 ('''static void layoutSettingsSkin(void*p){
 if(!at<B>(p,0x2050))return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 B*tabs=at<B*>(p,0x2078),*tabsEnd=at<B*>(p,0x2080),*rows=at<B*>(p,0x2110),*rowsEnd=at<B*>(p,0x2118);
 static void*owner;static B*oldTabs;static B*oldRows;static U oldTabsSize,oldRowsSize;static const void*firstLabel;static float oldW,oldH;
 U nt=tabs?(tabsEnd-tabs)/0x40:0,nr=rows?(rowsEnd-rows)/0x48:0;const void*first=nr?at<void*>(rows,0x28):nullptr;
 bool changed=owner!=p||w!=oldW||h!=oldH||tabs!=oldTabs||rows!=oldRows||nt!=oldTabsSize||nr!=oldRowsSize||first!=firstLabel||at<float>(p,0x2054)!=w*.025f||at<float>(p,0x205c)!=w*.95f;
 if(!changed&&nr&&at<float>(rows,8)!=w*.323f)changed=true;if(!changed)return;
 bool ownerChanged=owner!=p||w!=oldW||h!=oldH;
 owner=p;oldW=w;oldH=h;oldTabs=tabs;oldRows=rows;oldTabsSize=nt;oldRowsSize=nr;firstLabel=first;
 if(ownerChanged||settingsTapHeight<=0)settingsTapHeight=settingsMinimumTarget(w,h);
 float gap=h*.012f,tap=settingsTapHeight;
 settingsBackRect={w*.825f,h*.045f,w*.128f,tap};settingsNetworkRect={w*.635f,h*.045f,w*.173f,tap};
 float themeY=h*.045f+tap+gap,themeHeight=tap+gap;
 settingsSkyRect={w*.323f,themeY,w*.205f,tap};
 settingsContentY=themeY+themeHeight+h*.022f;settingsContentHeight=h*.87f-settingsContentY;
 if(settingsContentHeight<tap*2+gap)settingsContentHeight=tap*2+gap;
 settingsTabClipHeight=settingsContentHeight-tap-gap;
 settingsEffectsRect={w*.053f,settingsContentY+settingsTabClipHeight+gap,w*.229f,tap};
 settingsTextInset=tap*.16f;
 bounds(p,0x2054,w*.025f,h*.025f,w*.95f,h*.95f);
 bounds(p,0x20d8,w*.045f,settingsContentY,w*.246f,settingsTabClipHeight);
 bounds(p,0x2064,w*.323f,settingsContentY,w*.63f,settingsContentHeight);
 float tabStep=tap+gap,rowStep=tap+gap;
 for(U i=0;i<nt;i++){
  B*tab=tabs+i*0x40;float y=settingsContentY+i*tabStep;
  bounds(tab,0x18,w*.053f,y,w*.229f,tap);at<float>(tab,0x28)=y+settingsTextInset;
  void*label=at<void*>(tab,0x30);if(label){place(label,w*.066f,y+settingsTextInset,w*.202f,tap*.68f,.74f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xEFF5FFff);}
 }
 float maxTabs=nt*tabStep-settingsTabClipHeight;if(maxTabs<0)maxTabs=0;at<float>(p,0x20ec)=maxTabs;if(at<float>(p,0x20e8)>maxTabs)at<float>(p,0x20e8)=maxTabs;
 for(U i=0;i<nr;i++){
  B*row=rows+i*0x48;float y=settingsContentY+i*rowStep;
  bounds(row,8,w*.323f,y,w*.405f,tap);bounds(row,0x18,w*.74f,y,w*.213f,tap);
  void*label=at<void*>(row,0x28),*value=at<void*>(row,0x38);
  if(label){place(label,w*.338f,y+settingsTextInset,w*.373f,tap*.68f,.74f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xEFF5FFff);}
  if(value){place(value,w*.752f,y+settingsTextInset,w*.189f,tap*.68f,.74f,1);fn<void(*)(void*,unsigned)>(0x2d2c48)(value,0x46DBFFff);}
 }
 float content=nr*rowStep;if(content<settingsContentHeight)content=settingsContentHeight;at<float>(p,0x2130)=content;
 float maxRows=content-settingsContentHeight;if(at<float>(p,0x2128)>maxRows)at<float>(p,0x2128)=maxRows;
 place((B*)p+0x2138,w*.052f,h*.045f,w*.52f,tap,.86f,0);
 if(settingsBackOwner!=p){
  settingsEffectsGesture={};themeSwitchGesture={};settingsActionPressed=false;settingsBackOwner=p;
  settingsEffectsLabel=createInfoText(p,0xEFF5FFff);setLongText(settingsEffectsLabel,"EFEITOS GRÁFICOS");
  settingsBackText=createInfoText(p,0xEFF5FFff);setLongText(settingsBackText,"VOLTAR");
  settingsNetplayText=createInfoText(p,0xEFF5FFff);setLongText(settingsNetplayText,"ONLINE");
  settingsThemeLabel=createInfoText(p,0x9EAABCff);settingsThemeBlack=createInfoText(p,0x46DBFFff);settingsThemeBlue=createInfoText(p,0x9EAABCff);settingsRefreshThemeLabels();
 }
 place(settingsEffectsLabel,settingsEffectsRect.x+w*.013f,settingsEffectsRect.y+settingsTextInset,settingsEffectsRect.w-w*.026f,tap*.68f,.67f,0);
 place(settingsThemeLabel,w*.063f,themeY+settingsTextInset,w*.236f,tap*.68f,.65f,0);
 place(settingsThemeBlack,w*.545f,themeY+settingsTextInset,w*.115f,tap*.68f,.69f,0);
 place(settingsThemeBlue,w*.69f,themeY+settingsTextInset,w*.25f,tap*.68f,.49f,0);
 place(settingsBackText,settingsBackRect.x,settingsBackRect.y,settingsBackRect.w,settingsBackRect.h,.72f,1);
 place(settingsNetplayText,settingsNetworkRect.x,settingsNetworkRect.y,settingsNetworkRect.w,settingsNetworkRect.h,.69f,1);
 place((B*)p+0x2268,w*.323f,h*.90f,w*.63f,h*.035f,.65f,0);
 fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2138,0xEFF5FFff);fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2268,0x9EAABCff);
 __android_log_print(4,"TurboCarousel","SETTINGS grouped layout; tabs=%lu; options=%lu; tap=%.1f; original actions retained",nt,nr,tap);
}
''',
  '''static void layoutSettingsSkin(void*p){
 if(!at<B>(p,0x2050))return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 B*tabs=at<B*>(p,0x2078),*tabsEnd=at<B*>(p,0x2080),*rows=at<B*>(p,0x2110),*rowsEnd=at<B*>(p,0x2118);
 static void*owner;static B*oldTabs;static B*oldRows;static U oldTabsSize,oldRowsSize;static const void*firstLabel;static float oldW,oldH;
 U nt=tabs?(tabsEnd-tabs)/0x40:0,nr=rows?(rowsEnd-rows)/0x48:0;const void*first=nr?at<void*>(rows,0x28):nullptr;
 bool changed=owner!=p||w!=oldW||h!=oldH||tabs!=oldTabs||rows!=oldRows||nt!=oldTabsSize||nr!=oldRowsSize||first!=firstLabel||at<float>(p,0x2054)!=w*.025f||at<float>(p,0x205c)!=w*.95f;
 if(!changed&&nr&&at<float>(rows,8)!=w*.303f)changed=true;if(!changed)return;
 bool ownerChanged=owner!=p||w!=oldW||h!=oldH;
 owner=p;oldW=w;oldH=h;oldTabs=tabs;oldRows=rows;oldTabsSize=nt;oldRowsSize=nr;firstLabel=first;
 if(ownerChanged||settingsTapHeight<=0)settingsTapHeight=settingsMinimumTarget(w,h);
 // Compact presentation; every logical target still uses the original 48dp tap.
 float gap=h*.006f,tap=settingsTapHeight,headerY=h*.038f;
 settingsBackRect={w*.825f,headerY,w*.128f,tap};settingsNetworkRect={w*.635f,headerY,w*.173f,tap};
 // Color/Lottie shares the header; it no longer consumes a separate content row.
 float themeY=headerY;
 settingsSkyRect={w*.391f,themeY,w*.145f,tap};
 settingsContentY=headerY+tap+gap+h*.012f;settingsContentHeight=h*.875f-settingsContentY;
 if(settingsContentHeight<tap*2+gap)settingsContentHeight=tap*2+gap;
 settingsTabClipHeight=settingsContentHeight-tap-gap;
 // Sony owns the first right-column row. Native options begin strictly below it.
 float sonyWidth=(w*.65f-gap)*.5f;
 settingsSonyPs3Rect={w*.303f,settingsContentY,sonyWidth,tap};
 settingsSonyPs4Rect={w*.303f+sonyWidth+gap,settingsContentY,sonyWidth,tap};
 settingsRowsY=settingsContentY+tap+gap;settingsRowsClipHeight=settingsContentHeight-tap-gap;
 settingsEffectsRect={w*.053f,settingsContentY+settingsTabClipHeight+gap,w*.208f,tap};
 settingsTextInset=tap*.20f;
 bounds(p,0x2054,w*.025f,h*.025f,w*.95f,h*.95f);
 bounds(p,0x20d8,w*.045f,settingsContentY,w*.225f,settingsTabClipHeight);
 bounds(p,0x2064,w*.303f,settingsRowsY,w*.65f,settingsRowsClipHeight);
 float tabStep=tap+gap,rowStep=tap+gap;
 for(U i=0;i<nt;i++){
  B*tab=tabs+i*0x40;float y=settingsContentY+i*tabStep;
  bounds(tab,0x18,w*.053f,y,w*.208f,tap);at<float>(tab,0x28)=y+settingsTextInset;
  void*label=at<void*>(tab,0x30);if(label){place(label,w*.066f,y+settingsTextInset,w*.181f,tap*.60f,.68f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xEFF5FFff);}
 }
 float maxTabs=nt*tabStep-settingsTabClipHeight;if(maxTabs<0)maxTabs=0;at<float>(p,0x20ec)=maxTabs;if(at<float>(p,0x20e8)>maxTabs)at<float>(p,0x20e8)=maxTabs;
 for(U i=0;i<nr;i++){
  B*row=rows+i*0x48;float y=settingsRowsY+i*rowStep;
  bounds(row,8,w*.303f,y,w*.425f,tap);bounds(row,0x18,w*.74f,y,w*.213f,tap);
  void*label=at<void*>(row,0x28),*value=at<void*>(row,0x38);
  if(label){place(label,w*.318f,y+settingsTextInset,w*.393f,tap*.60f,.68f,0);fn<void(*)(void*,unsigned)>(0x2d2c48)(label,0xEFF5FFff);}
  if(value){place(value,w*.752f,y+settingsTextInset,w*.189f,tap*.60f,.68f,1);fn<void(*)(void*,unsigned)>(0x2d2c48)(value,0x46DBFFff);}
 }
 float content=nr*rowStep;if(content<settingsRowsClipHeight)content=settingsRowsClipHeight;at<float>(p,0x2130)=content;
 float maxRows=content-settingsRowsClipHeight;if(at<float>(p,0x2128)>maxRows)at<float>(p,0x2128)=maxRows;
 place((B*)p+0x2138,w*.052f,headerY,w*.25f,tap,.80f,0);
 if(settingsBackOwner!=p){
  settingsEffectsGesture={};themeSwitchGesture={};settingsActionPressed=false;settingsBackOwner=p;
  settingsEffectsLabel=createInfoText(p,0xEFF5FFff);setLongText(settingsEffectsLabel,"EFEITOS GRÁFICOS");
  settingsSonyPs3Text=createInfoText(p,0xEFF5FFff);setLongText(settingsSonyPs3Text,"PS3 • ABRIR EMULADOR");
  settingsSonyPs4Text=createInfoText(p,0xEFF5FFff);setLongText(settingsSonyPs4Text,"PS4 • ABRIR EMULADOR");
  settingsBackText=createInfoText(p,0xEFF5FFff);setLongText(settingsBackText,"VOLTAR");
  settingsNetplayText=createInfoText(p,0xEFF5FFff);setLongText(settingsNetplayText,"ONLINE");
  settingsThemeLabel=createInfoText(p,0x9EAABCff);settingsThemeBlack=createInfoText(p,0x46DBFFff);settingsThemeBlue=createInfoText(p,0x9EAABCff);settingsRefreshThemeLabels();
 }
 place(settingsEffectsLabel,settingsEffectsRect.x+w*.013f,settingsEffectsRect.y+settingsTextInset,settingsEffectsRect.w-w*.026f,tap*.60f,.63f,0);
 place(settingsSonyPs3Text,settingsSonyPs3Rect.x+w*.013f,settingsSonyPs3Rect.y+settingsTextInset,settingsSonyPs3Rect.w-w*.026f,tap*.60f,.64f,1);
 place(settingsSonyPs4Text,settingsSonyPs4Rect.x+w*.013f,settingsSonyPs4Rect.y+settingsTextInset,settingsSonyPs4Rect.w-w*.026f,tap*.60f,.64f,1);
 place(settingsThemeLabel,w*.315f,themeY+settingsTextInset,w*.070f,tap*.60f,.49f,0);
 place(settingsThemeBlack,w*.535f,themeY+tap*.12f,w*.076f,tap*.36f,.55f,0);
 place(settingsThemeBlue,w*.535f,themeY+tap*.51f,w*.076f,tap*.31f,.45f,0);
 place(settingsBackText,settingsBackRect.x,settingsBackRect.y+settingsTextInset,settingsBackRect.w,tap*.60f,.66f,1);
 place(settingsNetplayText,settingsNetworkRect.x,settingsNetworkRect.y+settingsTextInset,settingsNetworkRect.w,tap*.60f,.64f,1);
 place((B*)p+0x2268,w*.303f,h*.90f,w*.65f,h*.035f,.65f,0);
 fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2138,0xEFF5FFff);fn<void(*)(void*,unsigned)>(0x2d2c48)((B*)p+0x2268,0x9EAABCff);
 __android_log_print(4,"TurboCarousel","SETTINGS compact layout; tabs=%lu; options=%lu; tap=%.1f; original actions retained",nt,nr,tap);
}
'''),
 ('''static void settingsSkinText(void*t){
 if(!settingsPainting||!gui)return;float w=at<float>(gui,0x54);
 for(B*r=at<B*>(gui,0x2110);r&&r<at<B*>(gui,0x2118);r+=0x48){
  bool label=t==at<void*>(r,0x28),value=t==at<void*>(r,0x38);if(!label&&!value)continue;
  float y=at<float>(r,12)-at<float>(gui,0x2128)+settingsTextInset;fn<void(*)(void*,float,float,float)>(0x277194)(t,w*(label?.338f:.752f),y,0);return;
 }
}
''',
  '''static void settingsSkinText(void*t){
 if(!settingsPainting||!gui)return;float w=at<float>(gui,0x54);
 for(B*r=at<B*>(gui,0x2110);r&&r<at<B*>(gui,0x2118);r+=0x48){
  bool label=t==at<void*>(r,0x28),value=t==at<void*>(r,0x38);if(!label&&!value)continue;
  float y=at<float>(r,12)-at<float>(gui,0x2128)+settingsTextInset;fn<void(*)(void*,float,float,float)>(0x277194)(t,w*(label?.318f:.752f),y,0);return;
 }
}
'''),
 ('''static bool settingsSkinRect(U caller,float x,float y,float w,float h,unsigned color){
 if(!settingsPainting)return false;
 if(caller==0x226ee8){
  rect(x,y,w,h,0x06080Dff);float sw=at<float>(gui,0x54),sh=at<float>(gui,0x58),gap=sh*.012f;
  rect(sw*.043f,settingsContentY-gap,sw*.25f,settingsContentHeight+gap*2,0x101620ff);
  rect(sw*.304f,settingsContentY-gap,1.0f,settingsContentHeight+gap*2,0x334153ff);
  rect(sw*.05f,settingsSkyRect.y-gap*.5f,sw*.90f,1.0f,0x334153ff);
  rect(sw*.052f,sh*.032f,sw*.044f,2.f,0x46DBFFff);
  rect(sw*.101f,sh*.032f,sw*.014f,2.f,0x244EB3ff);
  return true;
 }
 if(caller==0x226f14)return true;if(caller>=0x21a958&&caller<0x21b0c8)return true;
 if(caller==0x227134){bool selected=(color>>8)==0x147D32;settingsConsoleCard(x,y+2,w,h-4,selected?0x14283Fff:0x101620ff,selected?0x3C728Eff:0x25303Eff,selected?0x46DBFFff:0);return true;}
 if(caller==0x22757c){float full=at<float>(gui,0x54)*.63f;rect(x,y+2,full,h-4,0x151F2Eff);rect(x,y+h-2,full,1,0x25303Eff);return true;}
 if(caller==0x2275a8){rect(x,y+8,1,h-16,0x334153ff);return true;}
 if((caller>=0x2271ac&&caller<=0x22722c)||(caller>=0x22760c&&caller<=0x22768c)){if(w>h)h=2.f;else w=2.f;rect(x,y,w,h,0xEFF5FFff);return true;}
 return false;
}
''',
  '''// Reset the same renderer matrix before each owned background; font rendering
// may leave a different transform. Visual cards are slim, logical targets stay 48dp.
static void settingsOwnedCard(void*matrix,const StationThemeRect&r,unsigned fill,unsigned rim,unsigned rail=0){
 fn<void(*)(const void*)>(0x2e5640)(matrix);
 settingsConsoleCard(r.x,r.y+r.h*.16f,r.w,r.h*.68f,fill,rim,rail);
}
static bool settingsSkinRect(U caller,float x,float y,float w,float h,unsigned color){
 if(!settingsPainting)return false;
 if(caller==0x226ee8){
  rect(x,y,w,h,0x070B12ff);float sw=at<float>(gui,0x54),sh=at<float>(gui,0x58),gap=sh*.006f;
  rect(sw*.284f,settingsContentY-gap,1.0f,settingsContentHeight+gap*2,0x223043ff);
  rect(sw*.05f,settingsContentY-gap,sw*.90f,1.0f,0x223043ff);
  rect(sw*.052f,sh*.032f,sw*.044f,2.f,0x46DBFFff);
  rect(sw*.101f,sh*.032f,sw*.014f,2.f,0x476AD2ff);
  return true;
 }
 if(caller==0x226f14)return true;if(caller>=0x21a958&&caller<0x21b0c8)return true;
 if(caller==0x227134){
  bool selected=(color>>8)==0x147D32;
  if(selected){rect(x,y+h*.16f,w,h*.68f,0x152840ff);rect(x+3,y+h*.26f,3,h*.48f,0x46DBFFff);}
  else rect(x+w*.05f,y+h*.84f,w*.90f,1.f,0x192536ff);
  return true;
 }
 if(caller==0x22757c){float full=at<float>(gui,0x54)*.65f;rect(x,y+h*.16f,full,h*.68f,0x0E1724ff);rect(x,y+h*.85f,full,1,0x223043ff);return true;}
 if(caller==0x2275a8){rect(x,y+h*.26f,1,h*.48f,0x223043ff);return true;}
 if((caller>=0x2271ac&&caller<=0x22722c)||(caller>=0x22760c&&caller<=0x22768c)){if(w>h)h=2.f;else w=2.f;rect(x,y,w,h,0xEFF5FFff);return true;}
 return false;
}
'''),
 ('''static void drawSettingsSkinHook(void*p,void*matrix){
 if(!at<B>(p,0x2050))return;layoutSettingsSkin(p);
 static unsigned themeRevision=~0u;static int background=-1;int currentBackground=stationGraphicsBackground();if(themeRevision!=stationThemeRevision||background!=currentBackground){themeRevision=stationThemeRevision;background=currentBackground;settingsRefreshThemeLabels();}
 settingsPainting=true;fn<void(*)(void*,void*)>(0x226e5c)(p,matrix);settingsPainting=false;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);fn<void(*)(const void*)>(0x2e5640)(matrix);
 rect(w*.053f,settingsSkyRect.y,w*.895f,settingsSkyRect.h,0x101722ff);rect(w*.053f,settingsSkyRect.y+settingsSkyRect.h-1,w*.895f,1,0x25303Eff);drawSettingsSkySwitch(p,matrix);
 auto e=settingsEffectsRect;settingsConsoleCard(e.x,e.y,e.w,e.h,0x142038ff,0x3C728Eff,0x46DBFFff);
 if(settingsEffectsLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsEffectsLabel,matrix);
 if(settingsThemeLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeLabel,matrix);
 if(settingsThemeBlack)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlack,matrix);
 if(settingsThemeBlue)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlue,matrix);
 auto n=settingsNetworkRect;bool networkPressed=settingsActionPressed&&settingsPressedAction==2;settingsConsoleCard(n.x,n.y,n.w,n.h,networkPressed?0x3262C8ff:0x244EB3ff,networkPressed?0xEFF5FFff:0x3C728Eff);if(settingsNetplayText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsNetplayText,matrix);
 auto b=settingsBackRect;bool backPressed=settingsActionPressed&&settingsPressedAction==1;settingsConsoleCard(b.x,b.y,b.w,b.h,backPressed?0x244EB3ff:0x151F2Eff,backPressed?0xEFF5FFff:0x334153ff);if(settingsBackText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsBackText,matrix);
}
''',
  '''static void drawSettingsSkinHook(void*p,void*matrix){
 if(!at<B>(p,0x2050))return;layoutSettingsSkin(p);
 static unsigned themeRevision=~0u;static int background=-1;int currentBackground=stationGraphicsBackground();if(themeRevision!=stationThemeRevision||background!=currentBackground){themeRevision=stationThemeRevision;background=currentBackground;settingsRefreshThemeLabels();}
 settingsPainting=true;fn<void(*)(void*,void*)>(0x226e5c)(p,matrix);settingsPainting=false;
 float w=at<float>(p,0x54);fn<void(*)(const void*)>(0x2e5640)(matrix);
 rect(w*.303f,settingsSkyRect.y+settingsSkyRect.h*.16f,w*.312f,settingsSkyRect.h*.68f,0x0D1623ff);
 // All owned cards precede owned text. Never reuse a transform left by a font.
 settingsOwnedCard(matrix,settingsEffectsRect,0x14263Dff,0x233D58ff,0x46DBFFff);
 bool ps3Pressed=settingsActionPressed&&settingsPressedAction==3,ps4Pressed=settingsActionPressed&&settingsPressedAction==4;
 settingsOwnedCard(matrix,settingsSonyPs3Rect,ps3Pressed?0x254B7Dff:0x14283Fff,ps3Pressed?0x74BDFFff:0x294764ff,0x74BDFFff);
 settingsOwnedCard(matrix,settingsSonyPs4Rect,ps4Pressed?0x403760ff:0x212239ff,ps4Pressed?0xA59AE6ff:0x383B59ff,0xA59AE6ff);
 bool networkPressed=settingsActionPressed&&settingsPressedAction==2,backPressed=settingsActionPressed&&settingsPressedAction==1;
 settingsOwnedCard(matrix,settingsNetworkRect,networkPressed?0x254B7Dff:0x183454ff,networkPressed?0x74BDFFff:0x294764ff);
 settingsOwnedCard(matrix,settingsBackRect,backPressed?0x24334Aff:0x111C2Bff,backPressed?0x8EAACAff:0x26364Bff);
 drawSettingsSkySwitch(p,matrix);
 if(settingsEffectsLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsEffectsLabel,matrix);
 if(settingsSonyPs3Text)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsSonyPs3Text,matrix);
 if(settingsSonyPs4Text)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsSonyPs4Text,matrix);
 if(settingsThemeLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeLabel,matrix);
 if(settingsThemeBlack)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlack,matrix);
 if(settingsThemeBlue)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsThemeBlue,matrix);
 if(settingsNetplayText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsNetplayText,matrix);
 if(settingsBackText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsBackText,matrix);
}
'''),
 ('''static bool touchSettingsSkinHook(void*p,const void*event){
 layoutSettingsSkin(p);float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 int effectsAction=settingsEffectsGesture.touch(type,id,x,y,settingsEffectsRect);if(effectsAction>=0){if(effectsAction==1)openGraphicsPanel();return true;}
 int skyAction=themeSwitchGesture.touch(type,id,x,y,settingsSkyRect);
 if(skyAction>=0){if(skyAction==1){stationThemeSaveFailed=!stationThemeChoose(1-stationThemeId);settingsRefreshThemeLabels(stationThemeSaveFailed);}return true;}
 bool inside=stationThemeContains(settingsBackRect,x,y),network=stationThemeContains(settingsNetworkRect,x,y);
 if(type==0){settingsActionPressed=inside||network;settingsPressedAction=network?2:1;settingsActionFinger=id;if(settingsActionPressed)return true;}
 if(settingsActionPressed&&id==settingsActionFinger){
  if(type!=1&&type!=2){settingsActionPressed=false;return true;}
  if(type==2){settingsActionPressed=false;if(settingsPressedAction==1&&inside)requestSettingsClose(p);else if(settingsPressedAction==2&&network&&openStationNetplay())requestSettingsClose(p);}return true;
 }
 return fn<bool(*)(void*,const void*)>(0x2269fc)(p,event);
}
''',
  '''static bool touchSettingsSkinHook(void*p,const void*event){
 layoutSettingsSkin(p);float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 int effectsAction=settingsEffectsGesture.touch(type,id,x,y,settingsEffectsRect);if(effectsAction>=0){if(effectsAction==1)openGraphicsPanel();return true;}
 int skyAction=themeSwitchGesture.touch(type,id,x,y,settingsSkyRect);
 if(skyAction>=0){if(skyAction==1){stationThemeSaveFailed=!stationThemeChoose(1-stationThemeId);settingsRefreshThemeLabels(stationThemeSaveFailed);}return true;}
 bool inside=stationThemeContains(settingsBackRect,x,y),network=stationThemeContains(settingsNetworkRect,x,y);
 bool ps3=stationThemeContains(settingsSonyPs3Rect,x,y),ps4=stationThemeContains(settingsSonyPs4Rect,x,y);
 if(type==0){settingsActionPressed=inside||network||ps3||ps4;settingsPressedAction=ps4?4:ps3?3:network?2:1;settingsActionFinger=id;if(settingsActionPressed)return true;}
 if(settingsActionPressed&&id==settingsActionFinger){
  if(type!=1&&type!=2){settingsActionPressed=false;return true;}
  if(type==2){settingsActionPressed=false;if(settingsPressedAction==1&&inside)requestSettingsClose(p);else if(settingsPressedAction==2&&network&&openStationNetplay())requestSettingsClose(p);else if(settingsPressedAction==3&&ps3&&openStationSonySettings("ps3"))requestSettingsClose(p);else if(settingsPressedAction==4&&ps4&&openStationSonySettings("ps4"))requestSettingsClose(p);}return true;
 }
 return fn<bool(*)(void*,const void*)>(0x2269fc)(p,event);
}
'''),
)

def patch(original:bytes)->bytes:
    if hashlib.sha256(original).hexdigest()!=SOURCE_SHA:
        raise ValueError('Exact current R124 native_settings.h required')
    text=original.decode('utf-8')
    for old,new in REPLACEMENTS:
        if text.count(old)!=1:
            raise ValueError('Native settings anchor changed: '+old[:80])
        text=text.replace(old,new,1)
    result=text.encode('utf-8')
    verify(original,result)
    return result

def verify(original:bytes,patched:bytes)->dict:
    if hashlib.sha256(original).hexdigest()!=SOURCE_SHA:
        raise ValueError('Settings source identity mismatch')
    text=patched.decode('utf-8')
    for old,new in reversed(REPLACEMENTS):
        if text.count(new)!=1:
            raise ValueError('Settings patch must be unique and exact')
        text=text.replace(new,old,1)
    if text.encode('utf-8')!=original:
        raise ValueError('An unrelated settings byte changed')
    return {
        'sourceSha256':SOURCE_SHA,
        'patchedSha256':hashlib.sha256(patched).hexdigest(),
        'exactInverse':True,
        'changedMethods':['settingsRefreshThemeLabels','layoutSettingsSkin','settingsSkinText','settingsSkinRect','drawSettingsSkinHook','touchSettingsSkinHook'],
        'addedMethods':['openStationSonySettings','settingsOwnedCard'],
        'originalTabsAndEmulatorDispatchUnchanged':True,
        'originalOptionValueActionsUnchanged':True,
        'oneOptionsRowReservedForSonySettings':True,
        'compactSettingsPresentation':True,
        'minimum48DpLogicalTargetsRetained':True,
        'slimVisualCardsDoNotReduceTouchTargets':True,
        'sonyActionsAboveOptions':True,
        'colorControlSharesHeader':True,
        'sidebarNarrowedWithoutChangingTabs':True,
        'nativeOptionsViewportExpanded':True,
        'sonyRowSeparateFromNativeOptionsViewport':True,
        'optionsRenderAndTouchExcludedFromSonyRow':True,
        'originalScrollDispatchUnchanged':True,
        'ownedCardMatrixRestoredBeforeEveryDraw':True,
        'cardsDrawnBeforeOwnedLabels':True,
        'sameStaticPrimitiveProgram':True,
        'newGpuProgramsAdded':False,
        'newFramebufferOrFilterAdded':False,
        'graphicsPanelEntryPreserved':True,
        'videoLoopPreferenceChangedByThisPatch':False,
        'externalSettingsLauncherOnly':True,
        'humanTapOnly':True,
        'jniPerFrameAdded':False,
        'backgroundLoopsAdded':False,
        'gameLaunchRoutesChanged':False,
        'onlineMethodsChanged':False,
        'nativePublicExportsAdded':False,
        'physicalValidation':False,
    }

def patch_settings(native_source:bytes,original_header:bytes)->tuple[bytes,bytes,dict]:
    """Build adapter: owned text guard, local override header and flags.

    Write the header beside the generated .cpp only after the exact R128
    baseline was compiled and compared. Quoted includes select that local
    header for the final compilation; the baseline input stays untouched.
    """
    if native_source.count(b'#include "native_settings.h"')!=1:
        raise ValueError('The native source must use its single quoted settings include')
    patched=patch(original_header)
    flags=verify(original_header,patched)
    old=b'p==settingsEffectsLabel||isStoreUiLabel(p)'
    new=b'p==settingsEffectsLabel||p==settingsSonyPs3Text||p==settingsSonyPs4Text||isStoreUiLabel(p)'
    if native_source.count(old)!=1 or new in native_source:
        raise ValueError('Exact settings owned-label rendering guard required')
    changed=native_source.replace(old,new,1)
    if changed.replace(new,old,1)!=native_source:
        raise ValueError('Unrelated native rendering byte changed')
    flags['nativeCppByteIdentical']=False
    flags['nativeCppChange']='two-owned-settings-labels-in-existing-textRenderHook-exclusion'
    flags['nativeCppExactInverse']=True
    flags['sonyLabelsDrawnOnlyByOpenSettingsModal']=True
    return changed,patched,flags

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('source','out','receipt'):
        parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    original=args.source.read_bytes();patched=patch(original)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(patched)
    args.receipt.write_text(json.dumps(verify(original,patched),indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
