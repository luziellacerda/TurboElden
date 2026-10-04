// Direct JNI dispatch from native controls; no synthetic input or public relay.
static jclass stationNetplayBridge;static jmethodID stationNetplayLaunch,stationNetplayLaunchGame;
static bool dispatchStationNetplay(const char* itemId){
 JNIEnv*env=videoEnv();if(!env)return false;jobject activity=videoActivity();if(!activity)return false;
 if(!stationNetplayBridge){
  jclass ac=env->GetObjectClass(activity);jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
  jobject loader=get?env->CallObjectMethod(activity,get):nullptr;jclass lc=loader?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=env->NewStringUTF("org.emulationstation.frontend.netplay.StationNetplayActivity");jclass local=load?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  if(!env->ExceptionCheck()&&local){stationNetplayBridge=(jclass)env->NewGlobalRef(local);stationNetplayLaunch=env->GetStaticMethodID(stationNetplayBridge,"launch","(Landroid/app/Activity;)Z");stationNetplayLaunchGame=env->GetStaticMethodID(stationNetplayBridge,"launchGame","(Landroid/app/Activity;Ljava/lang/String;)Z");}
  if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);
 }
 bool ok=false;
 if(!env->ExceptionCheck()&&stationNetplayBridge){
  if(itemId&&stationNetplayLaunchGame){jstring id=env->NewStringUTF(itemId);ok=env->CallStaticBooleanMethod(stationNetplayBridge,stationNetplayLaunchGame,activity,id);env->DeleteLocalRef(id);}
  else if(stationNetplayLaunch)ok=env->CallStaticBooleanMethod(stationNetplayBridge,stationNetplayLaunch,activity);
 }
 if(env->ExceptionCheck()){env->ExceptionClear();log("NETPLAY menu unavailable");ok=false;}env->DeleteLocalRef(activity);
 if(ok){stopSystemVideo();pauseRetroMusicForGame();log("NETPLAY direct menu dispatched");}return ok;
}
static bool openStationNetplay(){return dispatchStationNetplay(nullptr);}
static void drawOnlineAction(void*p,void*matrix){
 if(systemsMode||modal(p)||at<int>(p,0x370)<2)return;
 static void*owner;
 if(owner!=p){owner=p;onlineActionText=createInfoText(p,gameActionTextColor);setLongText(onlineActionText,"JOGAR ONLINE");}
 float w=at<float>(p,0x54),h=at<float>(p,0x58),gap=w*.010f,bw=(w*.95f-5*gap)/6,x=w*.025f+bw+gap;
 fn<void(*)(const void*)>(0x2e5640)(matrix);drawGameAction(x,h*.908f,bw,h*.065f,1,false,false,false);
 place(onlineActionText,x,h*.908f,bw,h*.065f,gameActionTextScale,1);
 if(onlineActionText)fn<void(*)(void*,void*)>(0x2d2dc4)(onlineActionText,matrix);
}
static bool touchOnlineAction(void*p,const void*event){
 static bool pressed;static U finger;
 if(systemsMode||modal(p)||at<int>(p,0x370)<2){pressed=false;return false;}
 float w=at<float>(p,0x54),h=at<float>(p,0x58),gap=w*.010f,bw=(w*.95f-5*gap)/6,x0=w*.025f+bw+gap;
 float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 bool inside=x>=x0&&x<=x0+bw&&y>=h*.908f&&y<=h*.973f;
 if(type==0){pressed=inside;finger=id;return pressed;}
 if(!pressed||id!=finger)return false;
 if(type==1&&!inside){pressed=false;return true;}
 if(type==2){pressed=false;if(inside){int selected=fn<int(*)(void*)>(0x21b0c8)(p);if(selected>=0){void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);if(begin&&selected<(end-begin)/0xe8)dispatchStationNetplay(strData(begin+(U)selected*0xe8));}}}
 return true;
}
