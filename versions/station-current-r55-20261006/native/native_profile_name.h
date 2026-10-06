// Uses the authenticated displayName already published by Station Java.
// No legacy profile file, network call, background thread or user-name logging.
#include "station_profile_bridge.h"
static void applyStationProfileName(void*text){
 using RevisionFn=uint64_t(*)();using CopyFn=bool(*)(char*,size_t,uint64_t*);
 static RevisionFn revisionFn;static CopyFn copyFn;static void*resolutionOwner;
 if((!revisionFn||!copyFn)&&resolutionOwner!=gui){
  resolutionOwner=gui;void*library=dlopen("libstation_frontend.so",2);
  if(library){revisionFn=(RevisionFn)dlsym(library,"StationProfile_nameRevision");copyFn=(CopyFn)dlsym(library,"StationProfile_copyName");}
 }
 if(!revisionFn||!copyFn)return;
 static uint64_t revision;static char name[1025]={},display[1025]={};
 uint64_t available=revisionFn();if(!available)return;
 bool changed=available!=revision;
 if(changed){uint64_t copied=0;char incoming[1025]={};if(!copyFn(incoming,sizeof(incoming),&copied))return;memcpy(name,incoming,strlen(incoming)+1);revision=copied;}
 float w=at<float>(gui,0x54),h=at<float>(gui,0x58);
 StationInfoRect area{w*.055f+h*.066f+w*.012f,h*.025f,w*.115f,h*.05f};
 static void*owner;static float oldW,oldH,textW,textH;static bool oldSystems,oldFolder;
 bool geometryReset=owner==text&&(absolute(at<float>(text,0x54)-textW)>.25f||absolute(at<float>(text,0x58)-textH)>.25f);
 if(changed||owner!=text||oldW!=w||oldH!=h||oldSystems!=systemsMode||oldFolder!=folderMode||geometryReset){
  owner=text;oldW=w;oldH=h;oldSystems=systemsMode;oldFolder=folderMode;
  fitGameTitleOneLine(text,*name?name:"JOGADOR",area,.72f);
  const char*rendered=strData((B*)text+0xd0);U bytes=strlen(rendered);if(bytes>=sizeof(display))return;
  memcpy(display,rendered,bytes+1);textW=at<float>(text,0x54);textH=at<float>(text,0x58);
 }else if(strcmp(strData((B*)text+0xd0),display)!=0){
  // GuiStore may restore its legacy profile on refresh. Reapply cached real name.
  setLongText(text,display);fn<void(*)(void*,float,float)>(0x2771d8)(text,0.f,0.f);
  float line=at<float>(text,0x58)*.72f;
  place(text,area.x,area.y+(area.h-line)*.5f,0,0,.72f,0);textW=at<float>(text,0x54);textH=at<float>(text,0x58);
 }
 // Place both the real settings hit rectangle and its native drawing after the
 // measured display name. Avatar and name coordinates above remain unchanged.
 float shownWidth=at<float>(text,0x54)*.72f;if(shownWidth>area.w)shownWidth=area.w;
 float settingsX=area.x+shownWidth+w*.012f;
 bounds(gui,0x1410,settingsX,h*.006f,h*.118f,h*.093f);
 bounds(gui,0x1420,w*.055f,h*.015f,settingsX-w*.067f,h*.066f);

}

// GuiStore::drawWelcome uses its own TextComponent at +0x380. The constructor
// formerly filled it from a legacy profile; this uses the published Station name.
// ABI confirmed: ctor 0x21320c / drawWelcome getValue 0x229748 / render 0x229a04.
static void applyStationWelcome(void*p){
 if(at<int>(p,0x370)>=2)return; // No work after the welcome animation.
 using RevisionFn=uint64_t(*)();using CopyFn=bool(*)(char*,size_t,uint64_t*);
 static RevisionFn revisionFn;static CopyFn copyFn;static void*resolved;
 if((!revisionFn||!copyFn)&&resolved!=p){resolved=p;void*library=dlopen("libstation_frontend.so",2);
  if(library){revisionFn=(RevisionFn)dlsym(library,"StationProfile_nameRevision");copyFn=(CopyFn)dlsym(library,"StationProfile_copyName");}}
 if(!revisionFn||!copyFn)return;
 static void*owner;static uint64_t revision;static float oldW,oldH;
 uint64_t available=revisionFn();float w=at<float>(p,0x54),h=at<float>(p,0x58);
 if(!available||(owner==p&&revision==available&&oldW==w&&oldH==h))return;
 char name[1025]={};uint64_t copied=0;if(!copyFn(name,sizeof(name),&copied)||!*name)return;
 char greeting[1100]={};const char prefix[]="Seja bem-vindo, ";
 U prefixSize=sizeof(prefix)-1,nameSize=strlen(name);if(prefixSize+nameSize>=sizeof(greeting))return;
 memcpy(greeting,prefix,prefixSize);memcpy(greeting+prefixSize,name,nameSize+1);
 void*text=(B*)p+0x380;setLongText(text,greeting);
 // Same native centered alignment and auto-height as the original constructor.
 fn<void(*)(void*,float,float)>(0x2771d8)(text,w*.92f,0.f);
 float height=at<float>(text,0x58);fn<void(*)(void*,float,float,float)>(0x277194)(text,w*.04f,(h-height)*.5f,0.f);
 owner=p;revision=copied;oldW=w;oldH=h;
 __android_log_print(4,"StationWelcome","Native welcome uses authenticated profile; namePresent=1");
}
