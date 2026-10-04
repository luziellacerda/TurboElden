// Dolphin 2609-7 Android integration. Never load the removed Libretro engine.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool dolphinCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"dolphin")||uiContains(s,"Dolphin")||strcmp(s,"wii")==0||
        strcmp(s,"gamecube")==0||strcmp(s,"GameCube")==0||strcmp(s,"gc")==0;
}
static jclass dolphinBridge;static jmethodID dolphinLaunch;
static bool dolphinException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("DOLPHIN Java integration failed");return true;
}
static bool openDolphin(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!dolphinBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.DolphinBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=dolphinException(env);
  if(!failed&&local){
   dolphinBridge=(jclass)env->NewGlobalRef(local);
   dolphinLaunch=env->GetStaticMethodID(dolphinBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!dolphinException(env)&&dolphinBridge&&dolphinLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(dolphinBridge,dolphinLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(dolphinException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"DOLPHIN official settings opened":"DOLPHIN official Android launch dispatched");}
 return ok;
}
static UiString dolphinRunHook(const void*core,const void*game){
 if(!dolphinCore(core))return fn<UiString(*)(const void*,const void*)>(0x2a9718)(core,game);
 UiString result={};
 if(!openDolphin(strData(game),false))strAssign(&result,"Não foi possível abrir o Dolphin integrado.");
 return result;
}
static bool dolphinFreshHook(const void*core){return dolphinCore(core)?false:fn<bool(*)(const void*)>(0x2a89a8)(core);}
static bool dolphinBundledHook(const void*core){return dolphinCore(core)?true:fn<bool(*)(const void*)>(0x2a87d8)(core);}
static bool dolphinInstalledHook(void*p,const void*core){return dolphinCore(core)?true:fn<bool(*)(void*,const void*)>(0x18b098)(p,core);}
static bool dolphinAssetsHook(void*p,const void*core){return dolphinCore(core)?true:fn<bool(*)(void*,const void*)>(0x18aaf0)(p,core);}
static bool dolphinPackHook(const void*core,void*url,void*path){
 if(!dolphinCore(core))return fn<bool(*)(const void*,void*,void*)>(0x18a8a8)(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // Sys is shipped with the new engine.
}
static bool dolphinDefinitionsHook(const void*core,void*title,void*options){
 if(!dolphinCore(core))return fn<bool(*)(const void*,void*,void*)>(0x2a6850)(core,title,options);
 strAssign(title,"Dolphin 2609-7 — configurações próprias");return false;
}
static void dolphinSettingsHook(void*p,const void*tab){
 if(!dolphinCore(tab)){fn<void(*)(void*,const void*)>(0x2228f8)(p,tab);return;}
 if(openDolphin("",true))requestSettingsClose(p);
}
