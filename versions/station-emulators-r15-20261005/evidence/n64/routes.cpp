#include <string>
#include <cstring>
#include <cassert>
#include <cstdio>
struct UiString{std::string value;}; static int calls=0,delegated=0;static bool setting=false;static std::string game;
static const char*strData(const void*p){return ((const std::string*)p)->c_str();}
static void strAssign(void*p,const char*s){((UiString*)p)->value=s;}
static bool presentationKeyEqual(const char*a,const char*b){return strcmp(a,b)==0;}
static bool openN64(const char*p,bool s){calls++;game=p;setting=s;return true;}
static void requestSettingsClose(void*){delegated++;}
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

int main(){int cases=0;
 for(const char* name:{"Nintendo 64","Nintendo 64 - BR","n64","n64br"}){
  std::string key=name;assert(n64CommandHook(&key).value=="libretro: core=mupen64plus_ae_android.so");cases++;
 }
 for(const char*name:{"Nintendo 64","Nintendo 64 - BR","n64","n64br","mupen64plus_ae_android.so","mupen64plus_next_gles3_libretro_android.so"}){
  std::string key=name,rom="/storage/emulated/0/EmulationStation/roms/.station-v2/n64/content/game.z64";UiString title,u,p;
  assert(n64Core(&key));n64RunHook(&key,&rom);assert(!setting&&game==rom);n64SettingsHook(nullptr,&key);assert(setting&&game.empty());
  assert(!n64FreshHook(&key));assert(n64BundledHook(&key));assert(n64InstalledHook(nullptr,&key));assert(n64AssetsHook(nullptr,&key));
  assert(!n64DefinitionsHook(&key,&title,nullptr));assert(title.value.find("Mupen64Plus AE")!=std::string::npos);assert(!n64PackHook(&key,&u,&p));cases+=10;
 }
 for(const char*name:{"Super Nintendo","MegaDrive","MAME","Neo Geo","Nintendo DS","GameCube","PSP","Flycast",""}){
  std::string key=name;UiString t,u,p;int start=delegated;assert(!n64Core(&key));n64CommandHook(&key);n64RunHook(&key,&key);n64SettingsHook(nullptr,&key);n64DefinitionsHook(&key,&t,nullptr);n64FreshHook(&key);n64BundledHook(&key);n64InstalledHook(nullptr,&key);n64AssetsHook(nullptr,&key);n64PackHook(&key,&u,&p);assert(delegated-start==9);cases+=10;
 }
 printf("PASS %d N64 routing checks: official settings/controls launch; all unrelated platforms delegated\n",cases);
}