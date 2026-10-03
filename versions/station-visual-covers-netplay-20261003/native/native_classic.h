// Bundled official Libretro Android ARM64 cores for Nintendo, Mega Drive, 32X,
// SuperGrafx, Beetle PCE Fast, N64 and PSX. 3DS uses Azahar 2126.1.2.
// PC Engine CD stays on accurate Beetle PCE (native_pcecd.h). FBNeo untouched.
static bool classicCore(const void*id){
 const char*s=strData(id);
 if(uiContains(s,"fbneo")||uiContains(s,"finalburn")||uiContains(s,"mame4droid"))return false;
 if(uiContains(s,"mednafen_pce_fast")||uiContains(s,"pce_fast"))return true;
 if(uiContains(s,"mednafen_pce_libretro")||strcmp(s,"mednafen_pce")==0)return false;
 return uiContains(s,"genesis_plus_gx")||uiContains(s,"picodrive")||
        uiContains(s,"mednafen_supergrafx")||uiContains(s,"fceumm")||
        uiContains(s,"snes9x")||uiContains(s,"gambatte")||uiContains(s,"mgba")||
        uiContains(s,"mupen64plus_next")||uiContains(s,"pcsx_rearmed")||
        uiContains(s,"pcsx-rearmed")||uiContains(s,"azahar")||
        (uiContains(s,"citra")&&!uiContains(s,"citra_touch"))||
        strcmp(s,"Nintendinho")==0||strcmp(s,"Super Nintendo")==0||
        strcmp(s,"Game Boy")==0||strcmp(s,"Game Boy Color")==0||
        strcmp(s,"Game Boy Advance")==0||strcmp(s,"Nintendo 64")==0||
        strcmp(s,"Nintendo 3DS")==0||strcmp(s,"Mega Drive")==0||
        strcmp(s,"Sega 32X")==0||strcmp(s,"PC Engine")==0||
        strcmp(s,"SuperGrafx")==0||strcmp(s,"PlayStation")==0;
}
static const char* classicOptionsId(const char*s){
 if(!s||!*s)return s;
 if(strcmp(s,"PlayStation")==0||uiContains(s,"pcsx_rearmed")||uiContains(s,"pcsx-rearmed"))return "pcsx_rearmed";
 if(strcmp(s,"Mega Drive")==0||uiContains(s,"genesis_plus_gx"))return "genesis_plus_gx";
 if(strcmp(s,"Sega 32X")==0||uiContains(s,"picodrive"))return "picodrive";
 if(strcmp(s,"PC Engine")==0||uiContains(s,"mednafen_pce_fast")||uiContains(s,"pce_fast"))return "mednafen_pce_fast";
 if(strcmp(s,"SuperGrafx")==0||uiContains(s,"mednafen_supergrafx"))return "mednafen_supergrafx";
 if(strcmp(s,"Nintendinho")==0||uiContains(s,"fceumm"))return "fceumm";
 if(strcmp(s,"Super Nintendo")==0||uiContains(s,"snes9x"))return "snes9x";
 if(strcmp(s,"Game Boy Color")==0)return "gambatte";
 if(strcmp(s,"Game Boy Advance")==0||uiContains(s,"mgba"))return "mgba";
 if(strcmp(s,"Game Boy")==0||uiContains(s,"gambatte"))return "gambatte";
 if(strcmp(s,"Nintendo 64")==0||uiContains(s,"mupen64plus_next"))return "mupen64plus_next_gles3";
 if(strcmp(s,"Nintendo 3DS")==0||uiContains(s,"azahar")||(uiContains(s,"citra")&&!uiContains(s,"citra_touch")))return "citra";
 return s;
}
static bool classicDefinitionsHook(const void*core,void*title,void*options){
 if(!classicCore(core))return mameDefinitionsHook(core,title,options);
 const char*s=strData(core);const char*id=classicOptionsId(s);
 UiString mapped={};strAssign(&mapped,id);
 bool ok=fn<bool(*)(const void*,void*,void*)>(0x2a6850)(&mapped,title,options);
 if(strcmp(s,"PlayStation")==0)strAssign(title,"PlayStation");
 else if(strcmp(s,"Mega Drive")==0)strAssign(title,"Mega Drive");
 else if(strcmp(s,"Sega 32X")==0)strAssign(title,"Sega 32X");
 else if(strcmp(s,"PC Engine")==0)strAssign(title,"PC Engine");
 else if(strcmp(s,"SuperGrafx")==0)strAssign(title,"SuperGrafx");
 else if(strcmp(s,"Nintendinho")==0)strAssign(title,"Nintendinho");
 else if(strcmp(s,"Super Nintendo")==0)strAssign(title,"Super Nintendo");
 else if(strcmp(s,"Game Boy")==0)strAssign(title,"Game Boy");
 else if(strcmp(s,"Game Boy Color")==0)strAssign(title,"Game Boy Color");
 else if(strcmp(s,"Game Boy Advance")==0)strAssign(title,"Game Boy Advance");
 else if(strcmp(s,"Nintendo 64")==0)strAssign(title,"Nintendo 64");
 else if(strcmp(s,"Nintendo 3DS")==0)strAssign(title,"Nintendo 3DS");
 return ok;
}
static bool classicBundledHook(const void*core){return classicCore(core)?true:mameBundledHook(core);}
static bool classicFreshHook(const void*core){return classicCore(core)?false:mameFreshHook(core);}
static bool classicInstalledHook(void*p,const void*core){return classicCore(core)?true:mameInstalledHook(p,core);}
static bool classicAssetsHook(void*p,const void*core){return classicCore(core)?true:mameAssetsHook(p,core);}
static bool classicPackHook(const void*core,void*url,void*path){
 if(!classicCore(core))return mamePackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false;
}
static NativeVector classicKnownCoresHook(){
 NativeVector result=mameKnownCoresHook();
 result=mameAppendCore(result,"Nintendinho");
 result=mameAppendCore(result,"Super Nintendo");
 result=mameAppendCore(result,"Game Boy");
 result=mameAppendCore(result,"Game Boy Color");
 result=mameAppendCore(result,"Game Boy Advance");
 result=mameAppendCore(result,"Nintendo 64");
 result=mameAppendCore(result,"Nintendo 3DS");
 result=mameAppendCore(result,"Mega Drive");
 result=mameAppendCore(result,"Sega 32X");
 result=mameAppendCore(result,"PC Engine");
 result=mameAppendCore(result,"SuperGrafx");
 result=mameAppendCore(result,"PlayStation");
 return result;
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
