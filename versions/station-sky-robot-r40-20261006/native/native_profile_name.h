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
}
