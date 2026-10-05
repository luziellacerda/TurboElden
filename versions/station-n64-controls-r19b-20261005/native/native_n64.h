// Match catalog identities and the exact names used by the native resolver.
static bool n64PlatformKey(const char* key){
 return presentationKeyEqual(key,"Nintendo 64") ||
        presentationKeyEqual(key,"Nintendo 64 - BR") ||
        presentationKeyEqual(key,"n64") || presentationKeyEqual(key,"n64br") ||
        presentationKeyEqual(key,"nintendo-64") || presentationKeyEqual(key,"nintendo-64--br");
}
static bool n64Core(const void* id){
 const char* s=strData(id);
 if(n64PlatformKey(s))return true;
 // resolveCore adds "lib" to a bundled core. Other existing launch entries
 // can carry its absolute path; compare only the complete filename, not a substring.
 const char* name=s;
 for(const char* p=s;*p;p++)if(*p=='/'||*p=='\\')name=p+1;
 if(name[0]=='l'&&name[1]=='i'&&name[2]=='b')name+=3;
 return strcmp(name,"mupen64plus_ae_android.so")==0 ||
        strcmp(name,"mupen64plus_next_gles3_libretro_android.so")==0 ||
        strcmp(name,"mupen64plus_next_gles3")==0;
}
static jclass n64Bridge;static jmethodID n64Launch;
static bool n64Exception(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("N64 Java integration failed");return true;
}
static bool openN64(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!n64Bridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.N64Bootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=n64Exception(env);
  if(!failed&&local){
   n64Bridge=(jclass)env->NewGlobalRef(local);
   n64Launch=env->GetStaticMethodID(n64Bridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!n64Exception(env)&&n64Bridge&&n64Launch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(n64Bridge,n64Launch,activity,game,settings);
  env->DeleteLocalRef(game);if(n64Exception(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"N64 official settings opened":"N64 official Android launch dispatched");}
 return ok;
}

static UiString n64RunHook(const void*core,const void*game){
 if(!n64Core(core))return megaRunHook(core,game);
 UiString result={};
 if(!openN64(strData(game),false))strAssign(&result,"Não foi possível abrir o Mupen64Plus AE integrado. Confira o arquivo instalado.");
 return result;
}
static bool n64DefinitionsHook(const void*core,void*title,void*options){
 if(!n64Core(core))return megaDefinitionsHook(core,title,options);
 strAssign(title,"Mupen64Plus AE — configurações próprias");return false;
}
static void n64SettingsHook(void*p,const void*tab){
 if(!n64Core(tab)){megaSettingsHook(p,tab);return;}
 if(openN64("",true))requestSettingsClose(p);
}
static UiString n64CommandHook(const void*folder){
 const char*key=strData(folder);
 if(n64PlatformKey(key)){
  UiString result={};strAssign(&result,"libretro: core=mupen64plus_ae_android.so");return result;
 }
 return megaCommandHook(folder);
}
static bool n64FreshHook(const void*c){return n64Core(c)?false:megaFreshHook(c);}
static bool n64BundledHook(const void*c){return n64Core(c)?true:megaBundledHook(c);}
static bool n64InstalledHook(void*p,const void*c){return n64Core(c)?true:megaInstalledHook(p,c);}
static bool n64AssetsHook(void*p,const void*c){return n64Core(c)?true:megaAssetsHook(p,c);}
static bool n64PackHook(const void*c,void*u,void*p){if(!n64Core(c))return megaPackHook(c,u,p);strAssign(u,"");strAssign(p,"");return false;}
