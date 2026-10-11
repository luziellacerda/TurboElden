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
// Graphic options are available only in Settings > EFEITOS.
// Preserve the existing call signatures without drawing or consuming main-menu touches.
static void drawGraphicsToggle(void*,void*){}
static bool touchGraphicsToggle(void*,const void*){return false;}
