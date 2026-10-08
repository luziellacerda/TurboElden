#pragma once
#include <jni.h>
#include "station_catalog_player_label.h"
static JNIEnv*videoEnv();
static jobject videoActivity();

// Selection-time memory lookup only. No catalogue download or content hashing on the render thread.
static void stationVerifiedPlayers(const char*id,char*out,size_t capacity){
 stationUnknownPlayers(out,capacity);if(!id||!*id)return;
 JNIEnv*env=videoEnv();if(!env)return;
 static jclass bridge;static jmethodID label;
 if(!bridge){
  jobject activity=videoActivity();if(!activity)return;
  if(env->PushLocalFrame(12)<0){env->ExceptionClear();env->DeleteLocalRef(activity);return;}
  jclass ac=env->GetObjectClass(activity);
  jmethodID get=ac?env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;"):nullptr;
  jobject loader=get&&!env->ExceptionCheck()?env->CallObjectMethod(activity,get):nullptr;
  jclass lc=loader&&!env->ExceptionCheck()?env->GetObjectClass(loader):nullptr;
  jmethodID load=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
  jstring name=!env->ExceptionCheck()?env->NewStringUTF("org.emulationstation.frontend.station.StationCatalogPlayerEvidence"):nullptr;
  jclass local=load&&name&&!env->ExceptionCheck()?(jclass)env->CallObjectMethod(loader,load,name):nullptr;
  jmethodID method=local&&!env->ExceptionCheck()?env->GetStaticMethodID(local,"labelFor","(Ljava/lang/String;)[B"):nullptr;
  if(method&&!env->ExceptionCheck()){
   jclass global=(jclass)env->NewGlobalRef(local);if(global&&!env->ExceptionCheck()){bridge=global;label=method;}
  }
  if(env->ExceptionCheck())env->ExceptionClear();env->PopLocalFrame(nullptr);env->DeleteLocalRef(activity);
 }
 if(!bridge||!label)return;
 if(env->PushLocalFrame(3)<0){env->ExceptionClear();return;}
 jstring key=env->NewStringUTF(id);
 jbyteArray data=key&&!env->ExceptionCheck()?(jbyteArray)env->CallStaticObjectMethod(bridge,label,key):nullptr;
 if(data&&!env->ExceptionCheck()){
  jsize length=env->GetArrayLength(data);
  if(length>=1&&length<=7){char value[8]={};env->GetByteArrayRegion(data,0,length,(jbyte*)value);
   if(!env->ExceptionCheck())stationPlayerEvidenceLabel(value,(size_t)length,out,capacity);}
 }
 if(env->ExceptionCheck())env->ExceptionClear();env->PopLocalFrame(nullptr);
}
