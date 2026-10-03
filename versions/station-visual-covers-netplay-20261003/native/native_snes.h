// Official EX+ UI/controls, own :snes process. No Libretro SNES launch.
static bool snesCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"snes9x")||strcmp(s,"Super Nintendo")==0||
        strcmp(s,"Super Nintendo - BR")==0||strcmp(s,"snes")==0||strcmp(s,"snesbr")==0;
}
static jclass snesBridge;static jmethodID snesLaunch;
static bool snesException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("SNES Java integration failed");return true;
}
static bool openSnes(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!snesBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.SnesBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=snesException(env);
  if(!failed&&local){
   snesBridge=(jclass)env->NewGlobalRef(local);
   snesLaunch=env->GetStaticMethodID(snesBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!snesException(env)&&snesBridge&&snesLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(snesBridge,snesLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(snesException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"SNES official settings opened":"SNES official Android launch dispatched");}
 return ok;
}
static UiString snesRunHook(const void*core,const void*game){
 if(!snesCore(core))return refreshRunHook(core,game);
 UiString result={};
 if(!openSnes(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Snes9x EX+ integrado.");
  JNIEnv*env=videoEnv();
  if(env&&snesBridge){
   jmethodID method=env->GetStaticMethodID(snesBridge,"getLastLaunchError","()Ljava/lang/String;");
   jstring message=method?(jstring)env->CallStaticObjectMethod(snesBridge,method):nullptr;
   if(!snesException(env)&&message){
    const char*text=env->GetStringUTFChars(message,nullptr);if(text){strAssign(&result,text);env->ReleaseStringUTFChars(message,text);}
   }
   if(message)env->DeleteLocalRef(message);snesException(env);
  }
 }
 return result;
}
static bool snesDefinitionsHook(const void*core,void*title,void*options){
 if(!snesCore(core))return refreshDefinitionsHook(core,title,options);
 strAssign(title,"Snes9x EX+ 1.5.85 — configurações próprias");return false;
}
static void snesSettingsHook(void*p,const void*tab){
 if(!snesCore(tab)){refreshSettingsHook(p,tab);return;}
 if(openSnes("",true))requestSettingsClose(p);
}
