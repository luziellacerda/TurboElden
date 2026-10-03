// Official EX+ UI/controls, own :megadrive process. No Libretro MEGA launch.
static bool megaCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"mdemu_station")||strcmp(s,"Mega Drive")==0||strcmp(s,"MegaDrive")==0||
        strcmp(s,"MegaDrive - BR")==0||strcmp(s,"megadrive")==0||strcmp(s,"megadrivebr")==0;
}
static jclass megaBridge;static jmethodID megaLaunch;
static bool megaException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("MEGA Java integration failed");return true;
}
static bool openMega(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!megaBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.MegaBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=megaException(env);
  if(!failed&&local){
   megaBridge=(jclass)env->NewGlobalRef(local);
   megaLaunch=env->GetStaticMethodID(megaBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!megaException(env)&&megaBridge&&megaLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(megaBridge,megaLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(megaException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"MEGA official settings opened":"MEGA official Android launch dispatched");}
 return ok;
}
static UiString megaRunHook(const void*core,const void*game){
 if(!megaCore(core))return snesRunHook(core,game);
 UiString result={};
 if(!openMega(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o MD.emu integrado.");
  JNIEnv*env=videoEnv();
  if(env&&megaBridge){
   jmethodID method=env->GetStaticMethodID(megaBridge,"getLastLaunchError","()Ljava/lang/String;");
   jstring message=method?(jstring)env->CallStaticObjectMethod(megaBridge,method):nullptr;
   if(!megaException(env)&&message){
    const char*text=env->GetStringUTFChars(message,nullptr);if(text){strAssign(&result,text);env->ReleaseStringUTFChars(message,text);}
   }
   if(message)env->DeleteLocalRef(message);megaException(env);
  }
 }
 return result;
}
static bool megaDefinitionsHook(const void*core,void*title,void*options){
 if(!megaCore(core))return snesDefinitionsHook(core,title,options);
 strAssign(title,"MD.emu 1.5.85 — configurações próprias");return false;
}
static void megaSettingsHook(void*p,const void*tab){
 if(!megaCore(tab)){snesSettingsHook(p,tab);return;}
 if(openMega("",true))requestSettingsClose(p);
}

static UiString gamecubeCommandHook(const void*);
static UiString megaCommandHook(const void*folder){
 const char*key=strData(folder);
 if(presentationKeyEqual(key,"MegaDrive")||presentationKeyEqual(key,"MegaDrive - BR")||
    presentationKeyEqual(key,"Mega Drive")||presentationKeyEqual(key,"megadrive")||
    presentationKeyEqual(key,"megadrivebr")||presentationKeyEqual(key,"genesis")){
  UiString result={};strAssign(&result,"libretro: core=mdemu_station.so");return result;
 }
 return gamecubeCommandHook(folder);
}
static bool megaFreshHook(const void*c){return megaCore(c)?false:refreshFreshHook(c);}
static bool megaBundledHook(const void*c){return megaCore(c)?true:refreshBundledHook(c);}
static bool megaInstalledHook(void*p,const void*c){return megaCore(c)?true:refreshInstalledHook(p,c);}
static bool megaAssetsHook(void*p,const void*c){return megaCore(c)?true:refreshAssetsHook(p,c);}
static bool megaPackHook(const void*c,void*u,void*p){if(!megaCore(c))return refreshPackHook(c,u,p);strAssign(u,"");strAssign(p,"");return false;}
