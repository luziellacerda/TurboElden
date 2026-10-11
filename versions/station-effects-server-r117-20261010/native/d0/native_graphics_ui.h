#pragma once
// Reuse the existing Android class-loader bridge and native touch gesture.
static jclass graphicsPanel;static jmethodID graphicsOpenMethod;
static bool openGraphicsPanel(){
 JNIEnv*env=videoEnv();if(!env)return false;jobject a=videoActivity();if(!a)return false;
 if(!graphicsPanel)graphicsPanel=downloadClass(env,a,"org.emulationstation.frontend.station.StationGraphicsPanel");
 if(graphicsPanel&&!graphicsOpenMethod)graphicsOpenMethod=env->GetStaticMethodID(graphicsPanel,"open","(Landroid/app/Activity;)Z");
 bool ok=graphicsOpenMethod&&env->CallStaticBooleanMethod(graphicsPanel,graphicsOpenMethod,a);
 if(env->ExceptionCheck()){env->ExceptionClear();ok=false;}env->DeleteLocalRef(a);return ok;
}
static bool toggleGraphics(){
 static bool(*toggle)();if(!toggle)toggle=(decltype(toggle))dlsym(dlopen("libstation_frontend.so",2),"StationGraphics_toggle");
 return toggle&&toggle();
}
static StationThemeRect graphicsToggleRect(float w,float h){auto theme=stationThemeToggleRect(w,h,false);return {theme.x-w*.20f-w*.012f,theme.y,w*.20f,theme.h};}
static void*graphicsToggleText;static void*graphicsToggleOwner;
static void drawGraphicsToggle(void*p,void*matrix){
 if(!systemsMode||folderMode||modal(p)||at<int>(p,0x370)!=3)return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);auto r=graphicsToggleRect(w,h);
 bool ownerChanged=graphicsToggleOwner!=p;
 if(ownerChanged){graphicsToggleOwner=p;graphicsToggleText=createInfoText(p,0xE5F1FFff);}
 static unsigned long long previous=~0ull;static float oldW,oldH;
 auto snapshot=stationGraphicsSnapshot();
 if(ownerChanged||previous!=snapshot||oldW!=w||oldH!=h){previous=snapshot;oldW=w;oldH=h;setLongText(graphicsToggleText,(snapshot&63u)?"EFEITOS: ATIVOS":"MODO LEVE");place(graphicsToggleText,r.x,r.y,r.w,r.h,.57f,1);}
 fn<void(*)(const void*)>(0x2e5640)(matrix);rounded(r.x,r.y,r.w,r.h,(snapshot&63u)?0x152821ff:0x147D32ff);
 fn<void(*)(void*,void*)>(0x2d2dc4)(graphicsToggleText,matrix);
}
static StationThemeToggleGesture graphicsToggleGesture;
static bool touchGraphicsToggle(void*p,const void*event){
 if(!systemsMode||folderMode||modal(p)||at<int>(p,0x370)!=3){graphicsToggleGesture={};return false;}
 auto r=graphicsToggleRect(at<float>(p,0x54),at<float>(p,0x58));
 int action=graphicsToggleGesture.touch(at<int>((void*)event,0),at<U>((void*)event,8),at<float>((void*)event,0x10),at<float>((void*)event,0x14),r);
 if(action<0)return false;if(action==1)toggleGraphics();return true;
}
