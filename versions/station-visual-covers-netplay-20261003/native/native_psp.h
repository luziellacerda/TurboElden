// PPSSPP 1.20.4 Android integration. Never load the removed Libretro engine.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool pspCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"ppsspp")||uiContains(s,"PPSSPP")||strcmp(s,"PSP")==0||
        uiContains(s,"Psp - BR")||uiContains(s,"pspbr");
}
static jclass pspBridge;static jmethodID pspLaunch;
static bool pspException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("PSP Java integration failed");return true;
}
static bool openPsp(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!pspBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.PspBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=pspException(env);
  if(!failed&&local){
   pspBridge=(jclass)env->NewGlobalRef(local);
   pspLaunch=env->GetStaticMethodID(pspBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!pspException(env)&&pspBridge&&pspLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(pspBridge,pspLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(pspException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"PSP official settings opened":"PSP official Android launch dispatched");}
 return ok;
}
static UiString pspRunHook(const void*core,const void*game){
 if(!pspCore(core))return ps2RunHook(core,game);
 UiString result={};
 if(!openPsp(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Psp integrado.");

 }
 return result;
}
static bool pspFreshHook(const void*core){return pspCore(core)?false:ps2FreshHook(core);}
static bool pspBundledHook(const void*core){return pspCore(core)?true:ps2BundledHook(core);}
static bool pspInstalledHook(void*p,const void*core){return pspCore(core)?true:ps2InstalledHook(p,core);}
static bool pspAssetsHook(void*p,const void*core){return pspCore(core)?true:ps2AssetsHook(p,core);}
static bool pspPackHook(const void*core,void*url,void*path){
 if(!pspCore(core))return ps2PackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // No Libretro support-pack download; existing support files are migrated locally.
}
static bool pspDefinitionsHook(const void*core,void*title,void*options){
 if(!pspCore(core))return ps2DefinitionsHook(core,title,options);
 strAssign(title,"PPSSPP 1.20.4 — configurações próprias");return false;
}
static void pspSettingsHook(void*p,const void*tab){
 if(!pspCore(tab)){ps2SettingsHook(p,tab);return;}
 if(openPsp("",true))requestSettingsClose(p);
}
