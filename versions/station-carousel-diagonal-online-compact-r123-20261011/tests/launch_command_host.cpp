#include <string>
#include <cstring>
#include <cstdio>
#include <cstdlib>
struct UiString{std::string value;};
static const char*strData(const void*p){return static_cast<const UiString*>(p)->value.c_str();}
static void strAssign(UiString*p,const char*s){p->value=s;}
static int fallbackCalls=0;
static UiString mockOriginal(const void*p){++fallbackCalls;return {std::string("__ORIGINAL_XML__:")+strData(p)};}
template<class T> static T fn(unsigned long address){if(address!=0x1888e0)std::abort();return reinterpret_cast<T>(&mockOriginal);}
static UiString gamecubeCommandHook(const void*);
static bool presentationKeyEqual(const char*key,const char*alias){
 while(*key&&*alias){
  char a=*key++,b=*alias++;if(a>='A'&&a<='Z')a=(char)(a-'A'+'a');if(b>='A'&&b<='Z')b=(char)(b-'A'+'a');
  if(a!=b)return false;
 }
 while(*key==' '||*key=='\t')key++;while(*alias==' '||*alias=='\t')alias++;
 return !*key&&!*alias;
}

static bool n64PlatformKey(const char* key){
 return presentationKeyEqual(key,"Nintendo 64") ||
        presentationKeyEqual(key,"Nintendo 64 - BR") ||
        presentationKeyEqual(key,"n64") || presentationKeyEqual(key,"n64br") ||
        presentationKeyEqual(key,"nintendo-64") || presentationKeyEqual(key,"nintendo-64--br");
}

static bool classicCommandHook(const char*key,UiString*result){
 if(presentationKeyEqual(key,"Nintendinho")||presentationKeyEqual(key,"nes")||presentationKeyEqual(key,"fds")){
  strAssign(result,"libretro: core=fceumm_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"Super Nintendo")||presentationKeyEqual(key,"Super Nintendo - BR")||
    presentationKeyEqual(key,"snes")||presentationKeyEqual(key,"sufami")){
  strAssign(result,"libretro: core=snes9x_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"Gameboy")||presentationKeyEqual(key,"gb")||
    presentationKeyEqual(key,"Gameboy Color")||presentationKeyEqual(key,"Game Boy Color")||
    presentationKeyEqual(key,"gbc")){
  strAssign(result,"libretro: core=gambatte_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"Gba")||presentationKeyEqual(key,"gba")){
  strAssign(result,"libretro: core=mgba_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"Nintendo 64")||presentationKeyEqual(key,"Nintendo 64 - BR")||
    presentationKeyEqual(key,"n64")){
  strAssign(result,"libretro: core=mupen64plus_next_gles3_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"3ds")||presentationKeyEqual(key,"nintendo3ds")){
  strAssign(result,"libretro: core=azahar_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"MegaDrive")||presentationKeyEqual(key,"MegaDrive - BR")||
    presentationKeyEqual(key,"megadrive")||presentationKeyEqual(key,"genesis")||
    presentationKeyEqual(key,"Master System")||presentationKeyEqual(key,"mastersystem")||
    presentationKeyEqual(key,"gamegear")||presentationKeyEqual(key,"sg1000")){
  strAssign(result,"libretro: core=genesis_plus_gx_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"sega32x")||presentationKeyEqual(key,"32x")||presentationKeyEqual(key,"sega 32x")){
  strAssign(result,"libretro: core=picodrive_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"Pc Engine")||presentationKeyEqual(key,"pcengine")){
  strAssign(result,"libretro: core=mednafen_pce_fast_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"supergrafx")||presentationKeyEqual(key,"SuperGrafx")){
  strAssign(result,"libretro: core=mednafen_supergrafx_libretro_android.so");return true;}
 if(presentationKeyEqual(key,"Playstation 1")||presentationKeyEqual(key,"psx")||
    presentationKeyEqual(key,"ps1")||presentationKeyEqual(key,"playstation")){
  strAssign(result,"libretro: core=pcsx_rearmed_libretro_android.so");return true;}
 return false;
}

static UiString gamecubeCommandHook(const void* folder){
 const char*key=strData(folder);
 // SwitchConfigPatcher still writes the pre-migration applicationId to the
 // legacy XML. Keep its original Android/content-URI route, changing only the
 // package to the applicationId verified in the installed R119 Manifest.
 // The bootstrap then forwards the same URI using Activity.getPackageName().
 if(presentationKeyEqual(key,"Switch")||presentationKeyEqual(key,"Nintendo Switch")||
    presentationKeyEqual(key,"nintendoswitch")||presentationKeyEqual(key,"nintendo-switch")||
    presentationKeyEqual(key,"nintendo_switch")||presentationKeyEqual(key,"nsw")||presentationKeyEqual(key,"ns")){
  UiString result={};strAssign(&result,"android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1");return result;
 }
 // Catalog folder aliases are not display labels. Route the BR editions to
 // the same embedded EX+ engines already selected for their base platforms.
 if(presentationKeyEqual(key,"megadrive--br")){
  UiString result={};strAssign(&result,"libretro: core=mdemu_station.so");return result;
 }
 if(presentationKeyEqual(key,"super-nintendo--br")){
  UiString result={};strAssign(&result,"libretro: core=snes9x_libretro_android.so");return result;
 }
 {UiString classic={};if(classicCommandHook(key,&classic))return classic;}
 if(presentationKeyEqual(key,"mame")||presentationKeyEqual(key,"Arcade")||presentationKeyEqual(key,"arcade")||
    presentationKeyEqual(key,"Neo Geo")||presentationKeyEqual(key,"neogeo")||presentationKeyEqual(key,"neo-geo")||
    presentationKeyEqual(key,"Neo Geo CD")||presentationKeyEqual(key,"neogeocd")||presentationKeyEqual(key,"neo-geo-cd")||
    presentationKeyEqual(key,"cps1")||presentationKeyEqual(key,"cps2")||presentationKeyEqual(key,"cps3")||
    presentationKeyEqual(key,"model2")){
  UiString result={};strAssign(&result,"libretro: core=mame4droid_android.so");return result;}
 if(presentationKeyEqual(key,"xbox")){UiString result={};strAssign(&result,"libretro: core=x1box_android.so");return result;}
 if(presentationKeyEqual(key,"PSP")||presentationKeyEqual(key,"Psp - BR")||presentationKeyEqual(key,"pspbr")){UiString result={};strAssign(&result,"libretro: core=ppsspp_libretro_android.so");return result;}
 if(presentationKeyEqual(key,"Pc Engine cd")||presentationKeyEqual(key,"pcenginecd")||presentationKeyEqual(key,"pc-engine-cd")){UiString result={};strAssign(&result,"libretro: core=mednafen_pce_libretro_android.so");return result;}
 if(presentationKeyEqual(key,"naomi")||presentationKeyEqual(key,"naomi2")||presentationKeyEqual(key,"Dreamcast")||presentationKeyEqual(key,"Atomiswave")){UiString result={};strAssign(&result,"libretro: core=flycast_libretro_android.so");return result;}

 if(presentationKeyEqual(key,"saturn")||presentationKeyEqual(key,"Sega Saturn")||presentationKeyEqual(key,"saturno")){UiString result={};strAssign(&result,"libretro: core=yabasanshiro_libretro_android.so");return result;}
 if(presentationKeyEqual(key,"psvita")||presentationKeyEqual(key,"PS Vita")){UiString result={};strAssign(&result,"libretro: core=vita3k_android.so");return result;}
 if(strcmp(key,"xbox360")==0||strcmp(key,"Xbox 360")==0){UiString result={};strAssign(&result,"libretro: core=xendroid_android.so");return result;}
 if(strcmp(key,"wiiu")==0||strcmp(key,"Wii U")==0){UiString result={};strAssign(&result,"libretro: core=cemu_android.so");return result;}
 if(strcmp(key,"gamecube")==0||strcmp(key,"GameCube")==0||strcmp(key,"gc")==0||strcmp(key,"wii")==0){
  UiString result={};strAssign(&result,"libretro: core=dolphin_libretro_android.so");return result;
 }
 return fn<UiString(*)(const void*)>(0x1888e0)(folder);
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

static UiString n64CommandHook(const void*folder){
 const char*key=strData(folder);
 if(n64PlatformKey(key)){
  UiString result={};strAssign(&result,"libretro: core=mupen64plus_ae_android.so");return result;
 }
 return megaCommandHook(folder);
}
struct Case{const char*input;const char*expected;};
static const Case cases[]={
{"3ds","libretro: core=azahar_libretro_android.so"},
{"arcade","libretro: core=mame4droid_android.so"},
{"atomiswave","libretro: core=flycast_libretro_android.so"},
{"dreamcast","libretro: core=flycast_libretro_android.so"},
{"gamecube","libretro: core=dolphin_libretro_android.so"},
{"gameboy","libretro: core=gambatte_libretro_android.so"},
{"gameboy-color","__ORIGINAL_XML__:gameboy-color"},
{"gba","libretro: core=mgba_libretro_android.so"},
{"master-system","__ORIGINAL_XML__:master-system"},
{"megadrive","libretro: core=mdemu_station.so"},
{"megadrive--br","libretro: core=mdemu_station.so"},
{"neo-geo","libretro: core=mame4droid_android.so"},
{"neo-geo-cd","libretro: core=mame4droid_android.so"},
{"nintendinho","libretro: core=fceumm_libretro_android.so"},
{"nintendo-64","libretro: core=mupen64plus_ae_android.so"},
{"nintendo-64--br","libretro: core=mupen64plus_ae_android.so"},
{"nintendo-ds","__ORIGINAL_XML__:nintendo-ds"},
{"odyssey-2","__ORIGINAL_XML__:odyssey-2"},
{"psp","libretro: core=ppsspp_libretro_android.so"},
{"pc-engine","__ORIGINAL_XML__:pc-engine"},
{"pc-engine-cd","libretro: core=mednafen_pce_libretro_android.so"},
{"psx","libretro: core=pcsx_rearmed_libretro_android.so"},
{"ps2","__ORIGINAL_XML__:ps2"},
{"ps2br","__ORIGINAL_XML__:ps2br"},
{"psp","libretro: core=ppsspp_libretro_android.so"},
{"psvita","libretro: core=vita3k_android.so"},
{"super-nintendo","__ORIGINAL_XML__:super-nintendo"},
{"super-nintendo--br","libretro: core=snes9x_libretro_android.so"},
{"switch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"atari2600","__ORIGINAL_XML__:atari2600"},
{"atari7800","__ORIGINAL_XML__:atari7800"},
{"colecovision","__ORIGINAL_XML__:colecovision"},
{"cps1","libretro: core=mame4droid_android.so"},
{"cps2","libretro: core=mame4droid_android.so"},
{"cps3","libretro: core=mame4droid_android.so"},
{"fbneo","__ORIGINAL_XML__:fbneo"},
{"fds","libretro: core=fceumm_libretro_android.so"},
{"gameandwatch","__ORIGINAL_XML__:gameandwatch"},
{"gamegear","libretro: core=genesis_plus_gx_libretro_android.so"},
{"jaguar","__ORIGINAL_XML__:jaguar"},
{"mame","libretro: core=mame4droid_android.so"},
{"naomi","libretro: core=flycast_libretro_android.so"},
{"naomi2","libretro: core=flycast_libretro_android.so"},
{"saturn","libretro: core=yabasanshiro_libretro_android.so"},
{"sega32x","libretro: core=picodrive_libretro_android.so"},
{"supergrafx","libretro: core=mednafen_supergrafx_libretro_android.so"},
{"wii","libretro: core=dolphin_libretro_android.so"},
{"wiiu","libretro: core=cemu_android.so"},
{"xbox","libretro: core=x1box_android.so"},
{"xbox360","libretro: core=xendroid_android.so"},
{"3ds","libretro: core=azahar_libretro_android.so"},
{"arcade","libretro: core=mame4droid_android.so"},
{"atomiswave","libretro: core=flycast_libretro_android.so"},
{"dreamcast","libretro: core=flycast_libretro_android.so"},
{"gamecube","libretro: core=dolphin_libretro_android.so"},
{"gameboy","libretro: core=gambatte_libretro_android.so"},
{"gameboy-color","__ORIGINAL_XML__:gameboy-color"},
{"gba","libretro: core=mgba_libretro_android.so"},
{"master-system","__ORIGINAL_XML__:master-system"},
{"megadrive","libretro: core=mdemu_station.so"},
{"megadrive--br","libretro: core=mdemu_station.so"},
{"neo-geo","libretro: core=mame4droid_android.so"},
{"neo-geo-cd","libretro: core=mame4droid_android.so"},
{"nintendinho","libretro: core=fceumm_libretro_android.so"},
{"nintendo-64","libretro: core=mupen64plus_ae_android.so"},
{"nintendo-64--br","libretro: core=mupen64plus_ae_android.so"},
{"nintendo-ds","__ORIGINAL_XML__:nintendo-ds"},
{"odyssey-2","__ORIGINAL_XML__:odyssey-2"},
{"psp","libretro: core=ppsspp_libretro_android.so"},
{"pc-engine","__ORIGINAL_XML__:pc-engine"},
{"pc-engine-cd","libretro: core=mednafen_pce_libretro_android.so"},
{"psx","libretro: core=pcsx_rearmed_libretro_android.so"},
{"ps2","__ORIGINAL_XML__:ps2"},
{"ps2br","__ORIGINAL_XML__:ps2br"},
{"psp","libretro: core=ppsspp_libretro_android.so"},
{"psvita","libretro: core=vita3k_android.so"},
{"super-nintendo","__ORIGINAL_XML__:super-nintendo"},
{"super-nintendo--br","libretro: core=snes9x_libretro_android.so"},
{"switch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"atari2600","__ORIGINAL_XML__:atari2600"},
{"atari7800","__ORIGINAL_XML__:atari7800"},
{"colecovision","__ORIGINAL_XML__:colecovision"},
{"cps1","libretro: core=mame4droid_android.so"},
{"cps2","libretro: core=mame4droid_android.so"},
{"cps3","libretro: core=mame4droid_android.so"},
{"fbneo","__ORIGINAL_XML__:fbneo"},
{"fds","libretro: core=fceumm_libretro_android.so"},
{"gameandwatch","__ORIGINAL_XML__:gameandwatch"},
{"gamegear","libretro: core=genesis_plus_gx_libretro_android.so"},
{"jaguar","__ORIGINAL_XML__:jaguar"},
{"mame","libretro: core=mame4droid_android.so"},
{"naomi","libretro: core=flycast_libretro_android.so"},
{"naomi2","libretro: core=flycast_libretro_android.so"},
{"saturn","libretro: core=yabasanshiro_libretro_android.so"},
{"sega32x","libretro: core=picodrive_libretro_android.so"},
{"supergrafx","libretro: core=mednafen_supergrafx_libretro_android.so"},
{"wii","libretro: core=dolphin_libretro_android.so"},
{"wiiu","libretro: core=cemu_android.so"},
{"xbox","libretro: core=x1box_android.so"},
{"xbox360","libretro: core=xendroid_android.so"},
{"megadrive","libretro: core=mdemu_station.so"},
{"super-nintendo","__ORIGINAL_XML__:super-nintendo"},
{"super-nintendo--br","libretro: core=snes9x_libretro_android.so"},
{"gameboy","libretro: core=gambatte_libretro_android.so"},
{"gameboy-color","__ORIGINAL_XML__:gameboy-color"},
{"gba","libretro: core=mgba_libretro_android.so"},
{"megadrive--br","libretro: core=mdemu_station.so"},
{"arcade","libretro: core=mame4droid_android.so"},
{"atomiswave","libretro: core=flycast_libretro_android.so"},
{"dreamcast","libretro: core=flycast_libretro_android.so"},
{"master-system","__ORIGINAL_XML__:master-system"},
{"nintendo-64","libretro: core=mupen64plus_ae_android.so"},
{"nintendo-64--br","libretro: core=mupen64plus_ae_android.so"},
{"nintendo-ds","__ORIGINAL_XML__:nintendo-ds"},
{"neo-geo","libretro: core=mame4droid_android.so"},
{"neo-geo-cd","libretro: core=mame4droid_android.so"},
{"nintendinho","libretro: core=fceumm_libretro_android.so"},
{"odyssey-2","__ORIGINAL_XML__:odyssey-2"},
{"pc-engine","__ORIGINAL_XML__:pc-engine"},
{"pc-engine-cd","libretro: core=mednafen_pce_libretro_android.so"},
{"psx","libretro: core=pcsx_rearmed_libretro_android.so"},
{"switch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"gamecube","libretro: core=dolphin_libretro_android.so"},
{"psp","libretro: core=ppsspp_libretro_android.so"},
{"psp","libretro: core=ppsspp_libretro_android.so"},
{"ps2","__ORIGINAL_XML__:ps2"},
{"ps2br","__ORIGINAL_XML__:ps2br"},
{"psvita","libretro: core=vita3k_android.so"},
{"MegaDrive - BR","libretro: core=mdemu_station.so"},
{"Super Nintendo - BR","libretro: core=snes9x_libretro_android.so"},
{"pcenginecd","libretro: core=mednafen_pce_libretro_android.so"},
{"Pc Engine cd","libretro: core=mednafen_pce_libretro_android.so"},
{"switch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"Nintendo Switch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"nintendoswitch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"nintendo-switch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"nintendo_switch","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"nsw","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"ns","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"NS","android: package=org.turboramastation.frontend class=org.yuzu.yuzu_emu.bootstrap.BootstrapActivity action=android.intent.action.VIEW data=\"%ROM_RAW%\" mime=application/octet-stream content=1"},
{"Nintendo 64 - BR","libretro: core=mupen64plus_ae_android.so"},
{"n64br","libretro: core=mupen64plus_ae_android.so"},
{"genesis","libretro: core=mdemu_station.so"},
{"Super Nintendo","libretro: core=snes9x_libretro_android.so"},
{"Playstation 1","libretro: core=pcsx_rearmed_libretro_android.so"},
{"unmapped-platform","__ORIGINAL_XML__:unmapped-platform"}
};
int main(){int failures=0;for(auto&c:cases){UiString input={c.input};UiString result=n64CommandHook(&input);if(result.value!=c.expected){++failures;std::printf("FAIL %s expected=%s got=%s\n",c.input,c.expected,result.value.c_str());}}std::printf("{\"checks\":%zu,\"failures\":%d,\"fallbackCalls\":%d}\n",sizeof(cases)/sizeof(cases[0]),failures,fallbackCalls);return failures?1:0;}
