#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdarg>
#include <string>
using jobject=void*;using jclass=void*;using jstring=const char*;using jmethodID=const char*;constexpr int JNI_TRUE=1;
struct JNIEnv {
 int disk=0,staged=0,reads=0,writes=0,frames=0,failAt=0,calls=0;bool ex=false,failCommit=false;
 bool failure(){if(failAt&&++calls==failAt){ex=true;return true;}return false;}
 int PushLocalFrame(int){if(failure())return -1;frames++;return 0;}
 void PopLocalFrame(void*){frames--;}
 bool ExceptionCheck(){return ex;}void ExceptionClear(){ex=false;}
 jclass FindClass(const char*){return failure()?nullptr:(void*)1;}
 jmethodID GetMethodID(jclass,const char*n,const char*){return failure()?nullptr:n;}
 jstring NewStringUTF(const char*s){return failure()?nullptr:s;}
 jobject CallObjectMethod(jobject,const char*m,...){
  if(failure())return nullptr;va_list a;va_start(a,m);
  if(!strcmp(m,"getSharedPreferences")){assert(!strcmp(va_arg(a,const char*),"station_appearance"));assert(va_arg(a,int)==0);}
  else if(!strcmp(m,"putInt")){assert(!strcmp(va_arg(a,const char*),"theme"));staged=va_arg(a,int);}
  else assert(!strcmp(m,"edit"));va_end(a);return (void*)2;
 }
 int CallIntMethod(jobject,const char*m,const char*k,int fallback){assert(!strcmp(m,"getInt")&&!strcmp(k,"theme")&&fallback==0);reads++;if(failure())return 0;return disk;}
 int CallBooleanMethod(jobject,const char*m){assert(!strcmp(m,"commit"));if(failure()||failCommit)return 0;disk=staged;writes++;return 1;}
};
static JNIEnv env;static bool available=true;static JNIEnv*videoEnv(){return available?&env:nullptr;}static jobject videoActivity(){return (void*)3;}static void log(const char*){}
#include "station_theme_palette.h"
#include "native_theme_preferences.h"
static void restart(){stationThemeId=0;stationThemeLoaded=stationThemeLoadAttempted=false;stationThemeRevision=0;}
int main(){
 restart();available=false;stationThemeTryLoad();assert(!stationThemeLoadAttempted);available=true;stationThemeTryLoad();assert(stationThemeLoaded&&stationThemeId==0&&env.reads==1);
 for(int i=0;i<10000;i++)stationThemeTryLoad();assert(env.reads==1&&env.frames==0);
 assert(stationThemeChoose(1)&&stationThemeId==1&&env.disk==1);restart();stationThemeTryLoad();assert(stationThemeId==1);
 assert(stationThemeChoose(0)&&env.disk==0);restart();stationThemeTryLoad();assert(stationThemeId==0);
 assert(!stationThemeChoose(-1)&&!stationThemeChoose(2));env.failCommit=true;assert(!stationThemeChoose(1)&&stationThemeId==0&&env.frames==0);env.failCommit=false;
 env.disk=99;restart();stationThemeTryLoad();assert(stationThemeId==0);env.disk=0;
 for(int at=1;at<=20;at++){env=JNIEnv{};env.failAt=at;restart();stationThemeTryLoad();assert(!env.ex&&env.frames==0);env=JNIEnv{};env.failAt=at;stationThemeChoose(1);assert(!env.ex&&env.frames==0);}
 puts("PASS actual preference JNI adapter under simulated Android API: restore, no per-frame IO, failures and balanced local references");
}
