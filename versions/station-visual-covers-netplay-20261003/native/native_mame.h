// MAME4droid Current 1.41.2 (MAME 0.289) Android integration; isolated :mame process on explicit launch.
// Neo Geo AES/MVS and Neo Geo CD use the same bundled engine. FBNeo stays on its own card.
static bool mameCore(const void*id){
 const char*s=strData(id);
 if(uiContains(s,"fbneo")||uiContains(s,"FB Neo")||uiContains(s,"finalburn"))return false;
 return uiContains(s,"mame4droid")||uiContains(s,"mame2003")||uiContains(s,"mame2010")||
        uiContains(s,"mame2016")||uiContains(s,"Arcade M.A.M.E")||strcmp(s,"mame")==0||
        strcmp(s,"Arcade")==0||uiContains(s,"Neo Geo")||uiContains(s,"Neo-Geo")||
        uiContains(s,"neogeo")||uiContains(s,"neogeocd")||uiContains(s,"neo-geo")||
        uiContains(s,"neocd")||uiContains(s,"cps1")||uiContains(s,"cps2")||uiContains(s,"cps3")||
        uiContains(s,"CPS-1")||uiContains(s,"CPS-2")||uiContains(s,"CPS-3")||uiContains(s,"CPS1")||
        uiContains(s,"CPS2")||uiContains(s,"CPS3")||uiContains(s,"model2")||uiContains(s,"Model 2");
}
static bool mameNeoCd(const char*s){
 return uiContains(s,"Neo Geo CD")||uiContains(s,"neogeocd")||uiContains(s,"neo-geo-cd")||
        uiContains(s,"neocd")||uiContains(s,"neocdz");
}
static bool mameNeoGeo(const char*s){
 return !mameNeoCd(s)&&(uiContains(s,"Neo Geo")||uiContains(s,"Neo-Geo")||uiContains(s,"neogeo")||uiContains(s,"neo-geo"));
}
static const char* mameRomsPath(const char*s){
 if(!s)return "/storage/emulated/0/EmulationStation/roms/mame";
 if(mameNeoCd(s))return "/storage/emulated/0/EmulationStation/roms/neo-geo-cd";
 if(mameNeoGeo(s))return "/storage/emulated/0/EmulationStation/roms/neo-geo";
 if(uiContains(s,"cps3")||uiContains(s,"CPS-3")||uiContains(s,"CPS3"))return "/storage/emulated/0/EmulationStation/roms/cps3";
 if(uiContains(s,"cps2")||uiContains(s,"CPS-2")||uiContains(s,"CPS2"))return "/storage/emulated/0/EmulationStation/roms/cps2";
 if(uiContains(s,"cps1")||uiContains(s,"CPS-1")||uiContains(s,"CPS1"))return "/storage/emulated/0/EmulationStation/roms/cps1";
 if(uiContains(s,"model2")||uiContains(s,"Model 2"))return "/storage/emulated/0/EmulationStation/roms/model2";
 return "/storage/emulated/0/EmulationStation/roms/mame";
}
static jclass mameBridge;static jmethodID mameLaunch;
static bool mameException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("MAME Java integration failed");return true;
}
static bool openMame(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!mameBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.MameBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=mameException(env);
  if(!failed&&local){
   mameBridge=(jclass)env->NewGlobalRef(local);
   mameLaunch=env->GetStaticMethodID(mameBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!mameException(env)&&mameBridge&&mameLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(mameBridge,mameLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(mameException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"MAME4droid Current 1.41.2 settings opened":"MAME4droid Current 1.41.2 Android launch dispatched");}
 return ok;
}
static UiString mameRunHook(const void*core,const void*game){
 if(!mameCore(core))return xboxClassicRunHook(core,game);
 UiString result={};
 if(!openMame(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o MAME integrado.");
 }
 return result;
}
static bool mameFreshHook(const void*core){return mameCore(core)?false:xboxClassicFreshHook(core);}
static bool mameBundledHook(const void*core){return mameCore(core)?true:xboxClassicBundledHook(core);}
static bool mameInstalledHook(void*p,const void*core){return mameCore(core)?true:xboxClassicInstalledHook(p,core);}
static bool mameAssetsHook(void*p,const void*core){return mameCore(core)?true:xboxClassicAssetsHook(p,core);}
static bool mamePackHook(const void*core,void*url,void*path){
 if(!mameCore(core))return xboxClassicPackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false;
}
static bool mameDefinitionsHook(const void*core,void*title,void*options){
 if(!mameCore(core))return xboxClassicDefinitionsHook(core,title,options);
 const char*s=strData(core);
 if(mameNeoCd(s))strAssign(title,"Neo Geo CD");
 else if(mameNeoGeo(s))strAssign(title,"Neo-Geo");
 else if(uiContains(s,"cps3")||uiContains(s,"CPS-3")||uiContains(s,"CPS3"))strAssign(title,"CPS-3");
 else if(uiContains(s,"cps2")||uiContains(s,"CPS-2")||uiContains(s,"CPS2"))strAssign(title,"CPS-2");
 else if(uiContains(s,"cps1")||uiContains(s,"CPS-1")||uiContains(s,"CPS1"))strAssign(title,"CPS-1");
 else if(uiContains(s,"model2")||uiContains(s,"Model 2"))strAssign(title,"SEGA Model 2");
 else strAssign(title,"Arcade M.A.M.E.");
 return false;
}
static void mameSettingsHook(void*p,const void*tab){
 if(!mameCore(tab)){xboxClassicSettingsHook(p,tab);return;}
 if(openMame(mameRomsPath(strData(tab)),true))requestSettingsClose(p);
}
static NativeVector mameAppendCore(NativeVector result,const char*name){
 for(B*it=result.begin;it&&it<result.end;it+=24)if(strcmp(strData(it),name)==0)return result;
 U bytes=result.begin?(U)(result.end-result.begin):0;
 B*next=(B*)fn<void*(*)(U)>(0x39d9c0)(bytes+24);
 if(bytes)memcpy(next,result.begin,bytes);
 memset(next+bytes,0,24);strAssign(next+bytes,name);
 if(result.begin)fn<V>(0x39d820)(result.begin);
 result.begin=next;result.end=next+bytes+24;result.capacity=result.end;return result;
}
static NativeVector mameKnownCoresHook(){
 NativeVector result=xboxClassicKnownCoresHook();
 result=mameAppendCore(result,"Arcade M.A.M.E.");
 result=mameAppendCore(result,"Neo-Geo");
 result=mameAppendCore(result,"Neo Geo CD");
 result=mameAppendCore(result,"CPS-1");
 result=mameAppendCore(result,"CPS-2");
 result=mameAppendCore(result,"CPS-3");
 result=mameAppendCore(result,"SEGA Model 2");
 return result;
}
