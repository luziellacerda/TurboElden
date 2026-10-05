
#include <string>
#include <cstring>
#include <cstdio>
#include <cstdlib>
struct UiString { std::string value; };
static int checks=0, opened=0, delegated=0, closed=0;
static bool setting=false, allowed=true;
static std::string path;
static void check(bool ok){checks++;if(!ok){fprintf(stderr,"Failed N64 route check %d\n",checks);exit(2);}}
static const char* strData(const void* p){return ((const UiString*)p)->value.c_str();}
static void strAssign(void* p,const char* s){((UiString*)p)->value=s;}
static bool presentationKeyEqual(const char* key,const char* alias){
 while(*key&&*alias){char a=*key++,b=*alias++;if(a>='A'&&a<='Z')a+=32;if(b>='A'&&b<='Z')b+=32;if(a!=b)return false;}
 return *key==*alias;
}
static bool openN64(const char* p,bool s){opened++;setting=s;path=p;return allowed;}
static void requestSettingsClose(void*){closed++;}
static UiString megaRunHook(const void*,const void*){delegated++;return {};}
static bool megaDefinitionsHook(const void*,void*,void*){delegated++;return false;}
static void megaSettingsHook(void*,const void*){delegated++;}
static UiString megaCommandHook(const void*){delegated++;return {};}
static bool megaFreshHook(const void*){delegated++;return true;}
static bool megaBundledHook(const void*){delegated++;return false;}
static bool megaInstalledHook(void*,const void*){delegated++;return false;}
static bool megaAssetsHook(void*,const void*){delegated++;return false;}
static bool megaPackHook(const void*,void*,void*){delegated++;return true;}
// Complete Mupen64Plus AE Android UI and controls, isolated :n64 / :n64core.
static bool n64Core(const void* id){
 const char*s=strData(id);
 return strcmp(s,"mupen64plus_ae_android.so")==0 ||
        strcmp(s,"mupen64plus_next_gles3_libretro_android.so")==0 ||
        strcmp(s,"Nintendo 64")==0 || strcmp(s,"Nintendo 64 - BR")==0 ||
        strcmp(s,"n64")==0 || strcmp(s,"n64br")==0;
}
static UiString n64RunHook(const void*core,const void*game){
 if(!n64Core(core))return megaRunHook(core,game);
 UiString result={};
 if(!openN64(strData(game),false))strAssign(&result,"Não foi possível abrir o Mupen64Plus AE integrado. Confira o arquivo instalado.");
 return result;
}
static bool n64DefinitionsHook(const void*core,void*title,void*options){
 if(!n64Core(core))return megaDefinitionsHook(core,title,options);
 strAssign(title,"Mupen64Plus AE — configurações próprias");return false;
}
static void n64SettingsHook(void*p,const void*tab){
 if(!n64Core(tab)){megaSettingsHook(p,tab);return;}
 if(openN64("",true))requestSettingsClose(p);
}
static UiString n64CommandHook(const void*folder){
 const char*key=strData(folder);
 if(presentationKeyEqual(key,"Nintendo 64")||presentationKeyEqual(key,"Nintendo 64 - BR")||
    presentationKeyEqual(key,"n64")||presentationKeyEqual(key,"n64br")){
  UiString result={};strAssign(&result,"libretro: core=mupen64plus_ae_android.so");return result;
 }
 return megaCommandHook(folder);
}
static bool n64FreshHook(const void*c){return n64Core(c)?false:megaFreshHook(c);}
static bool n64BundledHook(const void*c){return n64Core(c)?true:megaBundledHook(c);}
static bool n64InstalledHook(void*p,const void*c){return n64Core(c)?true:megaInstalledHook(p,c);}
static bool n64AssetsHook(void*p,const void*c){return n64Core(c)?true:megaAssetsHook(p,c);}
static bool n64PackHook(const void*c,void*u,void*p){if(!n64Core(c))return megaPackHook(c,u,p);strAssign(u,"");strAssign(p,"");return false;}

int main(){
 // Real bundled resolver prepends lib at 0x2a8e2c..0x2a8e3c.
 // Exercise the result passed to run, not only an unresolved command alias.
 for(const char* name:{"mupen64plus_ae_android.so","mupen64plus_next_gles3_libretro_android.so"}){
  UiString core{std::string("lib")+name},game{"/storage/emulated/0/EmulationStation/roms/.station-v2/nintendo-64/id/content/game.z64"};
  int d=delegated,o=opened;check(n64Core(&core));check(n64RunHook(&core,&game).value.empty());
  check(opened==o+1&&delegated==d&&!setting&&path==game.value);
 }
 for(const char* name:{"Nintendo 64","Nintendo 64 - BR","n64","n64br","nintendo-64","nintendo-64--br","NINTENDO-64","NINTENDO 64"}){
  UiString key{name};check(n64CommandHook(&key).value=="libretro: core=mupen64plus_ae_android.so");
  int c=closed,o=opened;n64SettingsHook(nullptr,&key);check(opened==o+1&&closed==c+1&&setting&&path.empty());
 }
 for(const char* name:{"mupen64plus_ae_android.so","mupen64plus_next_gles3_libretro_android.so","mupen64plus_next_gles3"}){
  for(const char* root:{"","lib","/data/app/pkg/lib/arm64/lib","/data/user/0/pkg/files/cores/","C:\\cores\\lib"}){
   UiString core{std::string(root)+name},game{"/some path/Corrida.z64"},title,u,p;
   int d=delegated;check(n64Core(&core));check(n64RunHook(&core,&game).value.empty());check(!setting&&path==game.value);
   n64SettingsHook(nullptr,&core);check(setting&&path.empty());
   check(!n64FreshHook(&core));check(n64BundledHook(&core));check(n64InstalledHook(nullptr,&core));check(n64AssetsHook(nullptr,&core));
   check(!n64DefinitionsHook(&core,&title,nullptr));check(title.value.find("Mupen64Plus AE")!=std::string::npos);
   check(!n64PackHook(&core,&u,&p));check(delegated==d);
  }
 }
 for(const char* name:{"","l","li","lib","/n64/pcsx_rearmed.so","/Nintendo 64/fceumm.so","mupen64plus_ae_android.so.old","xmupen64plus_next_gles3","Super Nintendo","snes9x_libretro_android.so","MegaDrive","mdemu_station.so","MAME","Neo Geo","Nintendo DS","GameCube","PSP","Flycast"}){
  UiString key{name},title,u,p;int d=delegated,o=opened;
  check(!n64Core(&key));n64RunHook(&key,&key);n64CommandHook(&key);n64SettingsHook(nullptr,&key);
  n64DefinitionsHook(&key,&title,nullptr);n64FreshHook(&key);n64BundledHook(&key);n64InstalledHook(nullptr,&key);n64AssetsHook(nullptr,&key);n64PackHook(&key,&u,&p);
  check(delegated==d+9&&opened==o);
 }
 allowed=false;UiString key{"libmupen64plus_ae_android.so"},game{"/missing.z64"};int d=delegated,c=closed;
 check(!n64RunHook(&key,&game).value.empty());n64SettingsHook(nullptr,&key);check(delegated==d&&closed==c);
 printf("PASS %d N64 routing checks: bundled prefix, paths, catalog slugs, own settings, no legacy fallback on launch failure\n",checks);
}
