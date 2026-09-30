// Cemu Android 0.5 Android integration. Dedicated experimental Wii U engine.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool wiiuCore(const void*id){return uiContains(strData(id),"cemu")||uiContains(strData(id),"wiiu")||uiContains(strData(id),"Wii U");}
static jclass wiiuBridge;static jmethodID wiiuLaunch;
static bool wiiuException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("Wii U Java integration failed");return true;
}
static bool openWiiU(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!wiiuBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.WiiUBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=wiiuException(env);
  if(!failed&&local){
   wiiuBridge=(jclass)env->NewGlobalRef(local);
   wiiuLaunch=env->GetStaticMethodID(wiiuBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!wiiuException(env)&&wiiuBridge&&wiiuLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(wiiuBridge,wiiuLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(wiiuException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"Wii U Cemu settings opened":"Wii U Cemu Android launch dispatched");}
 return ok;
}
static UiString wiiuRunHook(const void*core,const void*game){
 if(!wiiuCore(core))return pspRunHook(core,game);
 UiString result={};
 if(!openWiiU(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o WiiU integrado.");

 }
 return result;
}
static bool wiiuFreshHook(const void*core){return wiiuCore(core)?false:pspFreshHook(core);}
static bool wiiuBundledHook(const void*core){return wiiuCore(core)?true:pspBundledHook(core);}
static bool wiiuInstalledHook(void*p,const void*core){return wiiuCore(core)?true:pspInstalledHook(p,core);}
static bool wiiuAssetsHook(void*p,const void*core){return wiiuCore(core)?true:pspAssetsHook(p,core);}
static bool wiiuPackHook(const void*core,void*url,void*path){
 if(!wiiuCore(core))return pspPackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // Cemu is bundled; no Libretro support package is downloaded.
}
static bool wiiuDefinitionsHook(const void*core,void*title,void*options){
 if(!wiiuCore(core))return pspDefinitionsHook(core,title,options);
 strAssign(title,"Wii U");return false;
}
static void wiiuSettingsHook(void*p,const void*tab){
 if(!wiiuCore(tab)){pspSettingsHook(p,tab);return;}
 if(openWiiU("",true))requestSettingsClose(p);
}

// Add Wii U to the original native settings list, using its vector<string> ABI.
static NativeVector wiiuKnownCoresHook(){
 NativeVector result=fn<NativeVector(*)()>(0x2a5720)();
 for(B*it=result.begin;it&&it<result.end;it+=24)if(wiiuCore(it))return result;
 U bytes=result.begin?(U)(result.end-result.begin):0;
 B*next=(B*)fn<void*(*)(U)>(0x39d9c0)(bytes+24);
 if(bytes)memcpy(next,result.begin,bytes);
 memset(next+bytes,0,24);strAssign(next+bytes,"Wii U");
 if(result.begin)fn<V>(0x39d820)(result.begin);
 result.begin=next;result.end=next+bytes+24;result.capacity=result.end;return result;
}
