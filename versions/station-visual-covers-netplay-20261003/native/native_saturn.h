// Yaba Sanshiro 1.20.46 0.2.1 Android integration; an isolated process is started only on explicit launch.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool saturnCore(const void*id){return uiContains(strData(id),"yabasanshiro")||uiContains(strData(id),"YabaSanshiro")||uiContains(strData(id),"saturn")||uiContains(strData(id),"Saturn");}
static jclass saturnBridge;static jmethodID saturnLaunch;
static bool saturnException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("Sega Saturn Java integration failed");return true;
}
static bool openSaturn(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!saturnBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.SaturnBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=saturnException(env);
  if(!failed&&local){
   saturnBridge=(jclass)env->NewGlobalRef(local);
   saturnLaunch=env->GetStaticMethodID(saturnBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!saturnException(env)&&saturnBridge&&saturnLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(saturnBridge,saturnLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(saturnException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"Sega Saturn Yaba Sanshiro 1.20.46 settings opened":"Sega Saturn Yaba Sanshiro 1.20.46 Android launch dispatched");}
 return ok;
}
static UiString saturnRunHook(const void*core,const void*game){
 if(!saturnCore(core))return vitaRunHook(core,game);
 UiString result={};
 if(!openSaturn(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Saturn integrado.");

 }
 return result;
}
static bool saturnFreshHook(const void*core){return saturnCore(core)?false:vitaFreshHook(core);}
static bool saturnBundledHook(const void*core){return saturnCore(core)?true:vitaBundledHook(core);}
static bool saturnInstalledHook(void*p,const void*core){return saturnCore(core)?true:vitaInstalledHook(p,core);}
static bool saturnAssetsHook(void*p,const void*core){return saturnCore(core)?true:vitaAssetsHook(p,core);}
static bool saturnPackHook(const void*core,void*url,void*path){
 if(!saturnCore(core))return vitaPackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // Yaba Sanshiro 1.20.46 is bundled; no Libretro support package is downloaded.
}
static bool saturnDefinitionsHook(const void*core,void*title,void*options){
 if(!saturnCore(core))return vitaDefinitionsHook(core,title,options);
 strAssign(title,"Sega Saturn");return false;
}
static void saturnSettingsHook(void*p,const void*tab){
 if(!saturnCore(tab)){vitaSettingsHook(p,tab);return;}
 if(openSaturn("",true))requestSettingsClose(p);
}

// Add Sega Saturn to the original native settings list, using its vector<string> ABI.
static NativeVector saturnKnownCoresHook(){
 NativeVector result=vitaKnownCoresHook();
 for(B*it=result.begin;it&&it<result.end;it+=24)if(saturnCore(it))return result;
 U bytes=result.begin?(U)(result.end-result.begin):0;
 B*next=(B*)fn<void*(*)(U)>(0x39d9c0)(bytes+24);
 if(bytes)memcpy(next,result.begin,bytes);
 memset(next+bytes,0,24);strAssign(next+bytes,"Sega Saturn");
 if(result.begin)fn<V>(0x39d820)(result.begin);
 result.begin=next;result.end=next+bytes+24;result.capacity=result.end;return result;
}
