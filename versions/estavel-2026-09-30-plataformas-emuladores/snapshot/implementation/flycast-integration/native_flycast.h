// Flycast v2.7-44 Android integration. Never load the removed Libretro engine.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool flycastCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"flycast")||uiContains(s,"Flycast")||uiContains(s,"reicast");
}
static jclass flycastBridge;static jmethodID flycastLaunch;
static bool flycastException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("FLYCAST Java integration failed");return true;
}
static bool openFlycast(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!flycastBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.FlycastBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=flycastException(env);
  if(!failed&&local){
   flycastBridge=(jclass)env->NewGlobalRef(local);
   flycastLaunch=env->GetStaticMethodID(flycastBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!flycastException(env)&&flycastBridge&&flycastLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(flycastBridge,flycastLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(flycastException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"FLYCAST official settings opened":"FLYCAST official Android launch dispatched");}
 return ok;
}
static UiString flycastRunHook(const void*core,const void*game){
 if(!flycastCore(core))return dolphinRunHook(core,game);
 UiString result={};
 if(!openFlycast(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Flycast integrado.");
  JNIEnv*env=videoEnv();
  if(env&&flycastBridge){
   jmethodID method=env->GetStaticMethodID(flycastBridge,"getLastLaunchError","()Ljava/lang/String;");
   jstring message=method?(jstring)env->CallStaticObjectMethod(flycastBridge,method):nullptr;
   if(!flycastException(env)&&message){
    const char*text=env->GetStringUTFChars(message,nullptr);if(text){strAssign(&result,text);env->ReleaseStringUTFChars(message,text);}
   }
   if(message)env->DeleteLocalRef(message);flycastException(env);
  }
 }
 return result;
}
static bool flycastFreshHook(const void*core){return flycastCore(core)?false:dolphinFreshHook(core);}
static bool flycastBundledHook(const void*core){return flycastCore(core)?true:dolphinBundledHook(core);}
static bool flycastInstalledHook(void*p,const void*core){return flycastCore(core)?true:dolphinInstalledHook(p,core);}
static bool flycastAssetsHook(void*p,const void*core){return flycastCore(core)?true:dolphinAssetsHook(p,core);}
static bool flycastPackHook(const void*core,void*url,void*path){
 if(!flycastCore(core))return dolphinPackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // No Libretro support-pack download; existing support files are migrated locally.
}
static bool flycastDefinitionsHook(const void*core,void*title,void*options){
 if(!flycastCore(core))return dolphinDefinitionsHook(core,title,options);
 strAssign(title,"Flycast v2.7-44 — configurações próprias");return false;
}
static void flycastSettingsHook(void*p,const void*tab){
 if(!flycastCore(tab)){dolphinSettingsHook(p,tab);return;}
 if(openFlycast("",true))requestSettingsClose(p);
}
