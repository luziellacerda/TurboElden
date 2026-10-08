#pragma once
#include <jni.h>
#include "station_catalog_player_label.h"
static JNIEnv*videoEnv();
static jobject videoActivity();
static jclass playerBridge;static jmethodID playerLabel,playerGeneration;
static bool stationPlayerBridge(JNIEnv*env){
 if(!env)return false;if(playerBridge&&playerLabel&&playerGeneration)return true;
 jobject activity=videoActivity();if(!activity)return false;
 if(env->PushLocalFrame(12)<0){env->ExceptionClear();env->DeleteLocalRef(activity);return false;}
 jclass ac=env->GetObjectClass(activity);
 jmethodID get=ac?env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;"):nullptr;
 jobject loader=get&&!env->ExceptionCheck()?env->CallObjectMethod(activity,get):nullptr;
 jclass lc=loader&&!env->ExceptionCheck()?env->GetObjectClass(loader):nullptr;
 jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
 jstring name=!env->ExceptionCheck()?env->NewStringUTF("org.emulationstation.frontend.station.StationCatalogPlayerEvidence"):nullptr;
 jclass local=load&&name&&!env->ExceptionCheck()?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
 jmethodID method=local&&!env->ExceptionCheck()?env->GetStaticMethodID(local,"labelFor","(Ljava/lang/String;)[B"):nullptr;
 jmethodID revision=local&&!env->ExceptionCheck()?env->GetStaticMethodID(local,"generation","()I"):nullptr;
 if(method&&revision&&!env->ExceptionCheck()){
  jclass global=(jclass)env->NewGlobalRef(local);
  if(global&&!env->ExceptionCheck()){playerBridge=global;playerLabel=method;playerGeneration=revision;}
 }
 if(env->ExceptionCheck())env->ExceptionClear();env->PopLocalFrame(nullptr);env->DeleteLocalRef(activity);
 static int reported=-1;int status=playerBridge?1:0;
 if(reported!=status){reported=status;__android_log_print(4,"StationPlayers","native bridge=%d",status);}
 return playerBridge&&playerLabel&&playerGeneration;
}
// Four tiny in-memory version reads per second only while the game list is visible.
// No catalogue/network/disk work on the render thread, and no background timer.
static int stationPlayersGeneration(){
 static unsigned checked;static int generation=-1;
 unsigned now=fn<unsigned(*)()>(0x39e240)();if(checked&&(unsigned)(now-checked)<250)return generation;checked=now;
 JNIEnv*env=videoEnv();if(!stationPlayerBridge(env))return generation;
 jint value=env->CallStaticIntMethod(playerBridge,playerGeneration);
 if(env->ExceptionCheck()){env->ExceptionClear();return generation;}
 generation=value;return generation;
}
static void stationVerifiedPlayers(const char*id,char*out,size_t capacity){
 stationUnknownPlayers(out,capacity);if(!id||!*id)return;
 JNIEnv*env=videoEnv();if(!stationPlayerBridge(env))return;
 if(env->PushLocalFrame(3)<0){env->ExceptionClear();return;}
 jstring key=env->NewStringUTF(id);
 jbyteArray data=key&&!env->ExceptionCheck()?(jbyteArray)env->CallStaticObjectMethod(playerBridge,playerLabel,key):nullptr;
 int accepted=0;
 if(data&&!env->ExceptionCheck()){
  jsize length=env->GetArrayLength(data);
  if(length>=1&&length<=7){char value[8]={};env->GetByteArrayRegion(data,0,length,(jbyte*)value);
   if(!env->ExceptionCheck())accepted=stationPlayerEvidenceLabel(value,(size_t)length,out,capacity)?1:0;}
 }
 if(env->ExceptionCheck())env->ExceptionClear();env->PopLocalFrame(nullptr);
 static int previous=-1;int status=accepted?stationPlayerPictogramCount(out):0;
 if(previous!=status){previous=status;__android_log_print(4,"StationPlayers","native pictograms=%d",status);}
}
