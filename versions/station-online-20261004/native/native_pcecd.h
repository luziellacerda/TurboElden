// Updated accurate Beetle PCE core applies only to PC Engine CD. HuCards retain their route.
static bool pceCdCore(const void*id){const char*s=strData(id);return uiContains(s,"mednafen_pce_libretro")||strcmp(s,"mednafen_pce")==0;}
static UiString pcePrepare(){
 UiString result={};JNIEnv*env=videoEnv();if(!env){strAssign(&result,"A preparação do PC Engine CD não está disponível.");return result;}
 jobject activity=videoActivity();if(!activity){strAssign(&result,"A tela do aplicativo não está disponível.");return result;}
 jclass ac=env->GetObjectClass(activity);jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
 jobject loader=env->CallObjectMethod(activity,get);jclass lc=env->GetObjectClass(loader);jmethodID load=env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;");
 jstring name=env->NewStringUTF("org.emulationstation.frontend.PlatformAssets");jclass cls=(jclass)env->CallObjectMethod(loader,load,name);
 if(!env->ExceptionCheck()&&cls){
  jmethodID prep=env->GetStaticMethodID(cls,"preparePce","(Landroid/content/Context;Ljava/lang/String;)Ljava/lang/String;");
  UiString home=fn<UiString(*)()>(0x36c224)();jstring path=env->NewStringUTF(strData(&home));
  jstring error=prep?(jstring)env->CallStaticObjectMethod(cls,prep,activity,path):nullptr;
  if(error){const char*text=env->GetStringUTFChars(error,nullptr);if(text){strAssign(&result,text);env->ReleaseStringUTFChars(error,text);}env->DeleteLocalRef(error);}
  env->DeleteLocalRef(path);if(home.data[0]&1)fn<V>(0x39d820)(at<void*>(&home,16));
 }
 if(env->ExceptionCheck()){env->ExceptionDescribe();env->ExceptionClear();strAssign(&result,"Falha na preparação da BIOS do PC Engine CD.");}
 if(cls)env->DeleteLocalRef(cls);env->DeleteLocalRef(name);env->DeleteLocalRef(lc);env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);env->DeleteLocalRef(activity);return result;
}
static UiString refreshRunHook(const void*core,const void*game){if(pceCdCore(core)){UiString error=pcePrepare();if(*strData(&error))return error;}return mameRunHook(core,game);}
static bool refreshFreshHook(const void*core){return pceCdCore(core)?false:classicFreshHook(core);}
static bool refreshBundledHook(const void*core){return pceCdCore(core)?true:classicBundledHook(core);}
static bool refreshInstalledHook(void*p,const void*core){return pceCdCore(core)?true:classicInstalledHook(p,core);}
static bool refreshAssetsHook(void*p,const void*core){return pceCdCore(core)?true:classicAssetsHook(p,core);}
static bool refreshPackHook(const void*core,void*url,void*path){if(!pceCdCore(core))return classicPackHook(core,url,path);strAssign(url,"");strAssign(path,"");return false;}
static bool refreshDefinitionsHook(const void*core,void*title,void*options){return classicDefinitionsHook(core,title,options);}
static void refreshSettingsHook(void*p,const void*tab){mameSettingsHook(p,tab);}
static NativeVector refreshKnownCoresHook(){return classicKnownCoresHook();}
