#include <string>
#include <cstring>
#include <cstdio>
struct UiString {std::string value;};
static const char* strData(const void* p){return static_cast<const char*>(p);}
static bool uiContains(const char*s,const char*n){return std::strstr(s,n)!=nullptr;}
static bool presentationKeyEqual(const char*a,const char*b){return !std::strcmp(a,b);}
static void strAssign(UiString*p,const char*s){p->value=s;}
static UiString gamecubeCommandHook(const void*){return UiString{"legacy"};}
static bool megaCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"mdemu_station")||strcmp(s,"Mega Drive")==0||strcmp(s,"MegaDrive")==0||
        strcmp(s,"MegaDrive - BR")==0||strcmp(s,"megadrive")==0||strcmp(s,"megadrivebr")==0;
}
static UiString megaCommandHook(const void*folder){
 const char*key=strData(folder);
 if(presentationKeyEqual(key,"MegaDrive")||presentationKeyEqual(key,"MegaDrive - BR")||
    presentationKeyEqual(key,"Mega Drive")||presentationKeyEqual(key,"megadrive")||
    presentationKeyEqual(key,"megadrivebr")||presentationKeyEqual(key,"genesis")){
  UiString result={};strAssign(&result,"libretro: core=mdemu_station.so");return result;
 }
 return gamecubeCommandHook(folder);
}
int main(){int count=0;
 const char* yes[]={"mdemu_station.so","libmdemu_station.so","Mega Drive","MegaDrive","MegaDrive - BR","megadrive","megadrivebr"};
 for(auto s:yes){if(!megaCore(s))return 1;++count;}
 const char* no[]={"genesis_plus_gx_libretro_android.so","Master System","gamegear","picodrive","snes9x","Super Nintendo","PlayStation",""};
 for(auto s:no){if(megaCore(s))return 2;++count;}
 const char* routes[]={"MegaDrive","MegaDrive - BR","Mega Drive","megadrive","megadrivebr","genesis"};
 for(auto s:routes){if(megaCommandHook(s).value!="libretro: core=mdemu_station.so")return 3;++count;}
 const char* fallback[]={"Super Nintendo","snes","mastersystem","Master System","gamegear","sg1000","sega32x","wii","saturn"};
 for(auto s:fallback){if(megaCommandHook(s).value!="legacy")return 4;++count;}
 printf("PASS %d native Mega routing checks\n",count);return 0;
}
