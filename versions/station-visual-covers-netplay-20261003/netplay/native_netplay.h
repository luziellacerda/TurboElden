// Include after the JNI/video helpers. No synthetic input or engine replacement.
static jclass stationNetplayBridge;static jmethodID stationNetplayLaunch;
static bool openStationNetplay(){
 JNIEnv*env=videoEnv();if(!env)return false;jobject activity=videoActivity();if(!activity)return false;
 if(!stationNetplayBridge){
  jclass ac=env->GetObjectClass(activity);jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.netplay.StationNetplayActivity");jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  if(!env->ExceptionCheck()&&local){stationNetplayBridge=(jclass)env->NewGlobalRef(local);stationNetplayLaunch=env->GetStaticMethodID(stationNetplayBridge,"launch","(Landroid/app/Activity;)Z");}
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;if(!env->ExceptionCheck()&&stationNetplayBridge&&stationNetplayLaunch)ok=env->CallStaticBooleanMethod(stationNetplayBridge,stationNetplayLaunch,activity);
 if(env->ExceptionCheck()){env->ExceptionClear();log("NETPLAY menu unavailable");ok=false;}env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log("NETPLAY integrated networking menu dispatched");}return ok;
}
