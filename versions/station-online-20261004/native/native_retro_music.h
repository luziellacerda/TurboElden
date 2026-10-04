// Menu music uses the original StoreMusic control. Audio is streamed by one
// Android player, never by the carousel video decoders or a Java UI overlay.
static jclass retroMusicClass;
static jmethodID retroMusicTick,retroMusicSuspend;
static unsigned retroMusicLastTick;
static bool ensureRetroMusic(JNIEnv*env,jobject activity){
 if(retroMusicClass)return true;if(!env||!activity)return false;
 jclass ac=env->GetObjectClass(activity);jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
 jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
 jclass lc=loader?env->GetObjectClass(loader):nullptr;
 jmethodID method=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
 jstring name=env->NewStringUTF("org.emulationstation.frontend.MenuRetroMusic");
 jclass local=method?(jclass)env->CallObjectMethod(loader,method,name):nullptr;
 if(!env->ExceptionCheck()&&local){
  retroMusicTick=env->GetStaticMethodID(local,"tick","(Landroid/app/Activity;Z)V");
  retroMusicSuspend=env->GetStaticMethodID(local,"suspendForGame","()V");
  if(!env->ExceptionCheck()&&retroMusicTick&&retroMusicSuspend)retroMusicClass=(jclass)env->NewGlobalRef(local);
 }
 if(env->ExceptionCheck()){env->ExceptionClear();log("RETRO MUSIC helper unavailable");}
 if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
 if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 return retroMusicClass!=nullptr;
}
static bool retroMusicSetting(void*settings,const char*key){
 alignas(8) B value[24]={};U n=strlen(key);if(n>22)return false;value[0]=(B)(n*2);memcpy(value+1,key,n+1);
 return fn<bool(*)(void*,const void*)>(0x28a0e4)(settings,value);
}
static void retroMusicSet(void*settings,const char*key,bool enabled){
 alignas(8) B value[24]={};U n=strlen(key);if(n>22)return;value[0]=(B)(n*2);memcpy(value+1,key,n+1);
 fn<void(*)(void*,const void*,bool)>(0x289680)(settings,value,enabled);
}
static void retroMusicHook(void*p){
 unsigned now=fn<unsigned(*)()>(0x39e240)();if((unsigned)(now-retroMusicLastTick)<200)return;retroMusicLastTick=now;
 JNIEnv*env=videoEnv();if(!env)return;jobject activity=videoActivity();if(!activity)return;
 if(!ensureRetroMusic(env,activity)){env->DeleteLocalRef(activity);fn<V>(0x2170d0)(p);return;}
 // The original single WAV must never play over the new playlist. Keep UI sound effects.
 void*legacy=at<void*>(p,0x230);
 if(legacy&&fn<bool(*)(void*)>(0x28bbf0)(legacy))fn<V>(0x28bbf8)(legacy);
 void*settings=fn<void*(*)()>(0x288a24)();
 // Owner requested menu music: enable once when this feature is first installed.
 // Subsequent choices in the existing native toggle are always respected.
 if(!retroMusicSetting(settings,"RetroPlaylistReady")){
  retroMusicSet(settings,"StoreMusic",true);retroMusicSet(settings,"RetroPlaylistReady",true);fn<V>(0x288a78)(settings);
 }
 env->CallStaticVoidMethod(retroMusicClass,retroMusicTick,activity,(jboolean)retroMusicSetting(settings,"StoreMusic"));
 if(env->ExceptionCheck()){env->ExceptionClear();log("RETRO MUSIC heartbeat failed");}
 env->DeleteLocalRef(activity);
}
static void pauseRetroMusicForGame(){
 JNIEnv*env=videoEnv();if(!env||!retroMusicClass||!retroMusicSuspend)return;
 env->CallStaticVoidMethod(retroMusicClass,retroMusicSuspend);
 if(env->ExceptionCheck())env->ExceptionClear();
}
