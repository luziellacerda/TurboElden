// Preparation progress counts completed native milestones, never elapsed time.
// Hook only verified loader relocations; core calls and native show/hide timing are retained.
static jclass loadingProgressClass;
static jmethodID loadingProgressMethod;
static bool loadingTracked,loadingGameReady;
static U loadingInitialFrames;
static bool ensureLoadingProgress(JNIEnv*env,jobject activity){
 if(loadingProgressClass)return true;
 jclass ac=env->GetObjectClass(activity);
 jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
 jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
 jclass lc=loader?env->GetObjectClass(loader):nullptr;
 jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
 jstring name=env->NewStringUTF("org.emulationstation.frontend.LoadingOverlay");
 jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
 if(!env->ExceptionCheck()&&local){
  loadingProgressMethod=env->GetStaticMethodID(local,"updateProgress","(Landroid/app/Activity;I)V");
  if(!env->ExceptionCheck()&&loadingProgressMethod)loadingProgressClass=(jclass)env->NewGlobalRef(local);
 }
 if(env->ExceptionCheck()){env->ExceptionClear();log("LOADING progress helper unavailable");}
 if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
 if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 return loadingProgressClass!=nullptr;
}
static void reportLoadingStep(int step){
 JNIEnv*env=videoEnv();if(!env)return;jobject activity=videoActivity();if(!activity)return;
 if(ensureLoadingProgress(env,activity))env->CallStaticVoidMethod(loadingProgressClass,loadingProgressMethod,activity,(jint)step);
 if(env->ExceptionCheck())env->ExceptionClear();env->DeleteLocalRef(activity);
}
static void loadingShowHook(const void*name){
 loadingTracked=false;loadingGameReady=false;
 fn<void(*)(const void*)>(0x373c54)(name);
}
static bool loadingCoreHook(void*core,const void*path,const void*callbacks,void*error){
 loadingTracked=true;loadingGameReady=false;
 void*state=at<void*>((void*)base,0x3cf338);
 loadingInitialFrames=state?at<U>(state,0x178):0;
 reportLoadingStep(0);
 bool ok=fn<bool(*)(void*,const void*,const void*,void*)>(0x2bd298)(core,path,callbacks,error);
 reportLoadingStep(ok?1:-1);return ok;
}
static bool loadingGameHook(void*core,const void*path,void*error){
 bool ok=fn<bool(*)(void*,const void*,void*)>(0x2bdcb0)(core,path,error);
 loadingGameReady=ok;if(loadingTracked)reportLoadingStep(ok?2:-1);return ok;
}
static void loadingHideHook(){
 U caller=(U)__builtin_return_address(0)-base;
 if(loadingTracked){
  // Native hide also occurs after a 30-second fallback and on failure.
  // Only a real video callback (software or hardware) completes milestone 3.
  void*state=at<void*>((void*)base,0x3cf338);
  bool frame=state&&at<U>(state,0x178)>loadingInitialFrames;
  if(caller==0x2abe30&&loadingGameReady&&frame)reportLoadingStep(3);
  else reportLoadingStep(-1);
 }
 loadingTracked=false;loadingGameReady=false;
 fn<void(*)()>(0x373ddc)();
}
