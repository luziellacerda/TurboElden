// Vita3K 0.2.1 Android integration; an isolated process is started only on explicit launch.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool vitaCore(const void*id){return uiContains(strData(id),"vita3k")||uiContains(strData(id),"psvita")||uiContains(strData(id),"Psvita")||uiContains(strData(id),"PS Vita");}
static jclass vitaBridge;static jmethodID vitaLaunch;
static bool vitaException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("PS Vita Java integration failed");return true;
}
static bool openVita(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!vitaBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.VitaBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=vitaException(env);
  if(!failed&&local){
   vitaBridge=(jclass)env->NewGlobalRef(local);
   vitaLaunch=env->GetStaticMethodID(vitaBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!vitaException(env)&&vitaBridge&&vitaLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(vitaBridge,vitaLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(vitaException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"PS Vita Vita3K settings opened":"PS Vita Vita3K Android launch dispatched");}
 return ok;
}
static UiString vitaRunHook(const void*core,const void*game){
 if(!vitaCore(core))return xbox360RunHook(core,game);
 UiString result={};
 if(!openVita(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Vita integrado.");

 }
 return result;
}
static bool vitaFreshHook(const void*core){return vitaCore(core)?false:xbox360FreshHook(core);}
static bool vitaBundledHook(const void*core){return vitaCore(core)?true:xbox360BundledHook(core);}
static bool vitaInstalledHook(void*p,const void*core){return vitaCore(core)?true:xbox360InstalledHook(p,core);}
static bool vitaAssetsHook(void*p,const void*core){return vitaCore(core)?true:xbox360AssetsHook(p,core);}
static bool vitaPackHook(const void*core,void*url,void*path){
 if(!vitaCore(core))return xbox360PackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // Vita3K is bundled; no Libretro support package is downloaded.
}
static bool vitaDefinitionsHook(const void*core,void*title,void*options){
 if(!vitaCore(core))return xbox360DefinitionsHook(core,title,options);
 strAssign(title,"PS Vita");return false;
}
static void vitaSettingsHook(void*p,const void*tab){
 if(!vitaCore(tab)){xbox360SettingsHook(p,tab);return;}
 if(openVita("",true))requestSettingsClose(p);
}

// Add PS Vita to the original native settings list, using its vector<string> ABI.
static NativeVector vitaKnownCoresHook(){
 NativeVector result=xbox360KnownCoresHook();
 for(B*it=result.begin;it&&it<result.end;it+=24)if(vitaCore(it))return result;
 U bytes=result.begin?(U)(result.end-result.begin):0;
 B*next=(B*)fn<void*(*)(U)>(0x39d9c0)(bytes+24);
 if(bytes)memcpy(next,result.begin,bytes);
 memset(next+bytes,0,24);strAssign(next+bytes,"PS Vita");
 if(result.begin)fn<V>(0x39d820)(result.begin);
 result.begin=next;result.end=next+bytes+24;result.capacity=result.end;return result;
}
