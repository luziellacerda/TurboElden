// X1 BOX 1.2.8 0.2.1 Android integration; an isolated process is started only on explicit launch.
// Other engines retain the original functions and ABI. All UI is inside this APK.
static bool xboxClassicCore(const void*id){const char*s=strData(id);return uiContains(s,"x1box")||strcmp(s,"Xbox clássico")==0||strcmp(s,"xbox")==0;}
static jclass xboxClassicBridge;static jmethodID xboxClassicLaunch;
static bool xboxClassicException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionDescribe();env->ExceptionClear();log("Xbox clássico Java integration failed");return true;
}
static bool openXbox(const char*path,bool settings){
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 if(!xboxClassicBridge){
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.XboxBootstrap");
  jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  bool failed=xboxClassicException(env);
  if(!failed&&local){
   xboxClassicBridge=(jclass)env->NewGlobalRef(local);
   xboxClassicLaunch=env->GetStaticMethodID(xboxClassicBridge,"launch","(Landroid/app/Activity;Ljava/lang/String;Z)Z");
  }
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
  if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!xboxClassicException(env)&&xboxClassicBridge&&xboxClassicLaunch){
  jstring game=env->NewStringUTF(path?path:"");
  ok=env->CallStaticBooleanMethod(xboxClassicBridge,xboxClassicLaunch,activity,game,settings);
  env->DeleteLocalRef(game);if(xboxClassicException(env))ok=false;
 }
 env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log(settings?"Xbox clássico X1 BOX 1.2.8 settings opened":"Xbox clássico X1 BOX 1.2.8 Android launch dispatched");}
 return ok;
}
static UiString xboxClassicRunHook(const void*core,const void*game){
 if(!xboxClassicCore(core))return saturnRunHook(core,game);
 UiString result={};
 if(!openXbox(strData(game),false)){
  strAssign(&result,"Não foi possível abrir o Xbox integrado.");

 }
 return result;
}
static bool xboxClassicFreshHook(const void*core){return xboxClassicCore(core)?false:saturnFreshHook(core);}
static bool xboxClassicBundledHook(const void*core){return xboxClassicCore(core)?true:saturnBundledHook(core);}
static bool xboxClassicInstalledHook(void*p,const void*core){return xboxClassicCore(core)?true:saturnInstalledHook(p,core);}
static bool xboxClassicAssetsHook(void*p,const void*core){return xboxClassicCore(core)?true:saturnAssetsHook(p,core);}
static bool xboxClassicPackHook(const void*core,void*url,void*path){
 if(!xboxClassicCore(core))return saturnPackHook(core,url,path);
 strAssign(url,"");strAssign(path,"");return false; // X1 BOX 1.2.8 is bundled; no Libretro support package is downloaded.
}
static bool xboxClassicDefinitionsHook(const void*core,void*title,void*options){
 if(!xboxClassicCore(core))return saturnDefinitionsHook(core,title,options);
 strAssign(title,"Xbox clássico");return false;
}
static void xboxClassicSettingsHook(void*p,const void*tab){
 if(!xboxClassicCore(tab)){saturnSettingsHook(p,tab);return;}
 if(openXbox("",true))requestSettingsClose(p);
}

// Add Xbox clássico to the original native settings list, using its vector<string> ABI.
static NativeVector xboxClassicKnownCoresHook(){
 NativeVector result=saturnKnownCoresHook();
 for(B*it=result.begin;it&&it<result.end;it+=24)if(xboxClassicCore(it))return result;
 U bytes=result.begin?(U)(result.end-result.begin):0;
 B*next=(B*)fn<void*(*)(U)>(0x39d9c0)(bytes+24);
 if(bytes)memcpy(next,result.begin,bytes);
 memset(next+bytes,0,24);strAssign(next+bytes,"Xbox clássico");
 if(result.begin)fn<V>(0x39d820)(result.begin);
 result.begin=next;result.end=next+bytes+24;result.capacity=result.end;return result;
}
