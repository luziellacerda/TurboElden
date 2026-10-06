#pragma once
// SDL rendering thread owns this state. No worker, timer or per-frame disk read.
static bool stationThemeLoaded,stationThemeLoadAttempted;
static bool stationThemePreference(bool write,int&value){
 JNIEnv*env=videoEnv();if(!env)return false;
 if(env->PushLocalFrame(16)<0){if(env->ExceptionCheck())env->ExceptionClear();return false;}
 bool ok=false;
 do{
  jobject activity=videoActivity();if(!activity||env->ExceptionCheck())break;
  jclass context=env->FindClass("android/content/Context");if(!context)break;
  jmethodID get=env->GetMethodID(context,"getSharedPreferences","(Ljava/lang/String;I)Landroid/content/SharedPreferences;");if(!get)break;
  jstring name=env->NewStringUTF("station_appearance");if(!name)break;
  jstring key=env->NewStringUTF("theme");if(!key)break;
  jobject prefs=env->CallObjectMethod(activity,get,name,0);if(!prefs||env->ExceptionCheck())break;
  jclass type=env->FindClass("android/content/SharedPreferences");if(!type)break;
  if(!write){
   jmethodID read=env->GetMethodID(type,"getInt","(Ljava/lang/String;I)I");if(!read)break;
   int stored=env->CallIntMethod(prefs,read,key,0);if(env->ExceptionCheck())break;
   value=stored==1?1:0;ok=true;
  }else{
   jmethodID edit=env->GetMethodID(type,"edit","()Landroid/content/SharedPreferences$Editor;");if(!edit)break;
   jobject editor=env->CallObjectMethod(prefs,edit);if(!editor||env->ExceptionCheck())break;
   jclass et=env->FindClass("android/content/SharedPreferences$Editor");if(!et)break;
   jmethodID put=env->GetMethodID(et,"putInt","(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;");
   if(!put)break;
   env->CallObjectMethod(editor,put,key,value);if(env->ExceptionCheck())break;
   jmethodID commit=env->GetMethodID(et,"commit","()Z");if(!commit)break;
   ok=env->CallBooleanMethod(editor,commit)==JNI_TRUE&&!env->ExceptionCheck();
  }
 }while(false);
 if(env->ExceptionCheck()){env->ExceptionClear();ok=false;}
 env->PopLocalFrame(nullptr);return ok;
}
static void stationThemeTryLoad(){
 if(stationThemeLoadAttempted)return;
 if(!videoEnv())return; // SDL not attached yet; no IO was attempted.
 stationThemeLoadAttempted=true;int value=0;
 stationThemeLoaded=stationThemePreference(false,value);
 if(stationThemeLoaded){stationThemeId=value;stationThemeRevision++;}
 log(stationThemeLoaded?(stationThemeId?"THEME loaded blue":"THEME loaded black"):"THEME preference unavailable; black default");
}
static bool stationThemeChoose(int value){
 if(value<0||value>1)return false;
 if(stationThemeLoaded&&stationThemeId==value)return true;
 if(!stationThemePreference(true,value)){log("THEME save failed; previous palette retained");return false;}
 stationThemeId=value;stationThemeLoaded=stationThemeLoadAttempted=true;stationThemeRevision++;
 log(value?"THEME saved blue":"THEME saved black");return true;
}
