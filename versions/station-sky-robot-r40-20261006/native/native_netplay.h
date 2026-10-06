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
// Share the original action font so all six labels have identical metrics.
static void* createGameActionText(void*p){
 void*t=fn<void*(*)(U)>(0x39d9c0)(0x130);alignas(8) B empty[24]={};
 fn<void(*)(void*,void*,const void*,const void*,unsigned,int,Vec3,Vec2,unsigned)>(0x2d2a04)(t,at<void*>(p,0x10),empty,(B*)p+0xe00+0xe8,gameActionTextColor,0,Vec3{0,0,0},Vec2{0,0},0);
 fn<void(*)(void*,void*)>(0x2772c8)(p,t);return t;
}
static void drawOnlineAction(void*p,void*matrix){
 if(systemsMode||modal(p)||at<int>(p,0x370)<2)return;
 static void*owner;
 if(owner!=p){owner=p;onlineActionText=createGameActionText(p);setLongText(onlineActionText,"JOGAR ONLINE");}
 float w=at<float>(p,0x54),h=at<float>(p,0x58);auto bounds=stationBottomGameAction(w,h,1);float x=bounds.x,bw=bounds.w;
 fn<void(*)(const void*)>(0x2e5640)(matrix);drawGameAction(x,h*.908f,bw,h*.065f,1,false,false,false);
 float labelInset=actionLabelInset(h*.065f);
 place(onlineActionText,x+labelInset,h*.908f,bw-labelInset-h*.065f*.16f,h*.065f,gameActionTextScale,0);
 if(onlineActionText)fn<void(*)(void*,void*)>(0x2d2dc4)(onlineActionText,matrix);
}
static bool touchOnlineAction(void*p,const void*event){
 static bool pressed;static U finger;
 if(systemsMode||modal(p)||at<int>(p,0x370)<2){pressed=false;return false;}
 float w=at<float>(p,0x54),h=at<float>(p,0x58);auto bounds=stationBottomGameAction(w,h,1);float x0=bounds.x,bw=bounds.w;
 float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 bool inside=x>=x0&&x<=x0+bw&&y>=h*.908f&&y<=h*.973f;
 if(type==0){pressed=inside;finger=id;if(pressed)stationOnlineRobotPlayback.press(fn<unsigned(*)()>(0x39e240)());return pressed;}
 if(!pressed||id!=finger)return false;
 if(type==1&&!inside){pressed=false;return true;}
 if(type==2){pressed=false;if(inside){int selected=fn<int(*)(void*)>(0x21b0c8)(p);if(selected>=0){void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);if(begin&&selected<(end-begin)/0xe8)dispatchStationNetplay(strData(begin+(U)selected*0xe8));}}}
 return true;
}
