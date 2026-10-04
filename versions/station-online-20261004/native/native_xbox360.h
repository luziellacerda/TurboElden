// XenDroid 0b11201 Android integration. Dedicated experimental Xbox 360 engine.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool xbox360Core(const void*id){return uiContains(strData(id),"xendroid")||uiContains(strData(id),"xbox360")||uiContains(strData(id),"Xbox 360");}
static jclass xbox360Bridge;static jmethodID xbox360Launch;
static bool xbox360Exception(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("Xbox 360 Java integration failed");return true;
}
static bool openXbox360(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!xbox360Bridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.Xbox360Bootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=xbox360Exception(env);
  if(!failed&&local){
   xbox360Bridge=(jclass)env->NewGlobalRef(local);
   xbox360Launch=env->GetStaticMethodID(xbox360Bridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!xbox360Exception(env)&&xbox360Bridge&&xbox360Launch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(xbox360Bridge,xbox360Launch,activity,game,settings);
  env->DeleteLocalRef(game);if(xbox360Exception(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"Xbox 360 XenDroid settings opened":"Xbox 360 XenDroid Android launch dispatched");}
 return ok;
}
static UiString xbox360RunHook(const void*core,const void*game){
 if(!xbox360Core(core))return wiiuRunHook(core,game);
 UiString result={};
 if(!openXbox360(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Xbox360 integrado.");

 }
 return result;
}
static bool xbox360FreshHook(const void*core){return xbox360Core(core)?false:wiiuFreshHook(core);}
static bool xbox360BundledHook(const void*core){return xbox360Core(core)?true:wiiuBundledHook(core);}
static bool xbox360InstalledHook(void*p,const void*core){return xbox360Core(core)?true:wiiuInstalledHook(p,core);}
static bool xbox360AssetsHook(void*p,const void*core){return xbox360Core(core)?true:wiiuAssetsHook(p,core);}
static bool xbox360PackHook(const void*core,void*url,void*path){
 if(!xbox360Core(core))return wiiuPackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // XenDroid is bundled; no Libretro support package is downloaded.
}
static bool xbox360DefinitionsHook(const void*core,void*title,void*options){
 if(!xbox360Core(core))return wiiuDefinitionsHook(core,title,options);
 strAssign(title,"Xbox 360");return false;
}
static void xbox360SettingsHook(void*p,const void*tab){
 if(!xbox360Core(tab)){wiiuSettingsHook(p,tab);return;}
 if(openXbox360("",true))requestSettingsClose(p);
}

// Add Xbox 360 to the original native settings list, using its vector<string> ABI.
static NativeVector xbox360KnownCoresHook(){
 NativeVector result=wiiuKnownCoresHook();
 for(B*it=result.begin;it&&it<result.end;it+=24)if(xbox360Core(it))return result;
 U bytes=result.begin?(U)(result.end-result.begin):0;
 B*next=(B*)fn<void*(*)(U)>(0x39d9c0)(bytes+24);
 if(bytes)memcpy(next,result.begin,bytes);
 memset(next+bytes,0,24);strAssign(next+bytes,"Xbox 360");
 if(result.begin)fn<V>(0x39d820)(result.begin);
 result.begin=next;result.end=next+bytes+24;result.capacity=result.end;return result;
}
