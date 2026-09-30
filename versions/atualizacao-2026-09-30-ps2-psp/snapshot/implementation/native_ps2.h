// ARMSX2 2.7.2 Android integration. Never load the removed Libretro engine.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool ps2Core(const void*id){const char*s=strData(id);return uiContains(s,"armsx2")||uiContains(s,"pcsx2")||uiContains(s,"ARMSX2");}
static jclass ps2Bridge;static jmethodID ps2Launch;
static bool ps2Exception(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("PS2 Java integration failed");return true;
}
static bool openPs2(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!ps2Bridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.Ps2Bootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=ps2Exception(env);
  if(!failed&&local){
   ps2Bridge=(jclass)env->NewGlobalRef(local);
   ps2Launch=env->GetStaticMethodID(ps2Bridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!ps2Exception(env)&&ps2Bridge&&ps2Launch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(ps2Bridge,ps2Launch,activity,game,settings);
  env->DeleteLocalRef(game);if(ps2Exception(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"PS2 official settings opened":"PS2 official Android launch dispatched");}
 return ok;
}
static UiString ps2RunHook(const void*core,const void*game){
 if(!ps2Core(core))return flycastRunHook(core,game);
 UiString result={};
 if(!openPs2(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Ps2 integrado.");

 }
 return result;
}
static bool ps2FreshHook(const void*core){return ps2Core(core)?false:flycastFreshHook(core);}
static bool ps2BundledHook(const void*core){return ps2Core(core)?true:flycastBundledHook(core);}
static bool ps2InstalledHook(void*p,const void*core){return ps2Core(core)?true:flycastInstalledHook(p,core);}
static bool ps2AssetsHook(void*p,const void*core){return ps2Core(core)?true:flycastAssetsHook(p,core);}
static bool ps2PackHook(const void*core,void*url,void*path){
 if(!ps2Core(core))return flycastPackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // No Libretro support-pack download; existing support files are migrated locally.
}
static bool ps2DefinitionsHook(const void*core,void*title,void*options){
 if(!ps2Core(core))return flycastDefinitionsHook(core,title,options);
 strAssign(title,"ARMSX2 2.7.2 — configurações próprias");return false;
}
static void ps2SettingsHook(void*p,const void*tab){
 if(!ps2Core(tab)){flycastSettingsHook(p,tab);return;}
 if(openPs2("",true))requestSettingsClose(p);
}
