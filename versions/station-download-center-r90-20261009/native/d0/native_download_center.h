// Additional notice only. Existing download toast, progress and actions are preserved.
static jclass downloadFrontend,downloadPanel;static jmethodID downloadCountMethod,downloadOpenMethod;
static jclass downloadClass(JNIEnv*env,jobject activity,const char*name){
 jclass ac=env->GetObjectClass(activity);jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
 jobject loader=get?env->CallObjectMethod(activity,get):nullptr;jclass lc=loader?env->GetObjectClass(loader):nullptr;
 jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
 jstring text=env->NewStringUTF(name);jclass local=load?(jclass)env->CallObjectMethod(loader,load,text):nullptr;
 jclass result=local&&!env->ExceptionCheck()?(jclass)env->NewGlobalRef(local):nullptr;
 if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(text);if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);env->DeleteLocalRef(ac);return result;
}
static bool downloadLink(JNIEnv*env,jobject activity){
 if(!downloadFrontend){downloadFrontend=downloadClass(env,activity,"org.emulationstation.frontend.station.StationFrontend");if(downloadFrontend)downloadCountMethod=env->GetStaticMethodID(downloadFrontend,"downloadNoticeCount","()I");}
 if(!downloadPanel&&!env->ExceptionCheck()){downloadPanel=downloadClass(env,activity,"org.emulationstation.frontend.station.StationDownloadPanel");if(downloadPanel)downloadOpenMethod=env->GetStaticMethodID(downloadPanel,"open","(Landroid/app/Activity;)Z");}
 if(env->ExceptionCheck()){env->ExceptionClear();return false;}return downloadCountMethod&&downloadOpenMethod;
}
static int downloadNoticeCount(){
 static unsigned updated;static int count;unsigned now=fn<unsigned(*)()>(0x39e240)();if(updated&&(unsigned)(now-updated)<500)return count;updated=now;
 JNIEnv*env=videoEnv();if(!env)return count=0;jobject a=videoActivity();if(!a)return count=0;
 if(downloadLink(env,a))count=env->CallStaticIntMethod(downloadFrontend,downloadCountMethod);
 if(env->ExceptionCheck()){env->ExceptionClear();count=0;}env->DeleteLocalRef(a);return count;
}
static UiBox downloadNoticeBox(void*p){float w=at<float>(p,0x54),h=at<float>(p,0x58);return {w*.666f,stationScreenTopbarActionY(h),w*.043f,h*.059f};}
static void drawDownloadNotice(void*p){
 if(modal(p)||at<int>(p,0x370)<2)return;int count=downloadNoticeCount();if(!count)return;
 auto box=downloadNoticeBox(p);uiMatrix(&formationMatrix);uiSurface(box,0x142D20ff,0x36754Cff);
 uiStatusIcon(box.x+box.w*.26f,box.y+box.h*.50f,box.h*.38f,0x69E49Aff,false);
 char label[12]={};if(count>0){char*end=downloadNumber(label,count);*end=0;}else{label[0]='V';label[1]='E';label[2]='R';}
 uiLabel(p,56,label,&formationMatrix,{box.x+box.w*.47f,box.y,box.w*.47f,box.h},.54f,0xEAFFF2ff,1);
}
static bool touchDownloadNotice(void*p,const void*event){
 static bool pressed;static U finger;
 if(modal(p)||at<int>(p,0x370)<2||!downloadNoticeCount()){pressed=false;return false;}
 auto box=downloadNoticeBox(p);float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);int type=at<int>((void*)event,0);U id=at<U>((void*)event,8);
 bool inside=x>=box.x&&x<=box.x+box.w&&y>=box.y&&y<=box.y+box.h;
 if(type==0){pressed=inside;finger=id;return pressed;}if(!pressed||id!=finger)return false;
 if(type==1&&!inside){pressed=false;return true;}
 if(type==2){pressed=false;if(inside){JNIEnv*env=videoEnv();if(env){jobject a=videoActivity();if(a){if(downloadLink(env,a))env->CallStaticBooleanMethod(downloadPanel,downloadOpenMethod,a);if(env->ExceptionCheck())env->ExceptionClear();env->DeleteLocalRef(a);}}}}
 return true;
}
