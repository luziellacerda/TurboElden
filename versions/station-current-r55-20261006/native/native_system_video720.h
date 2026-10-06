// One focused 720p30 loop; every adjacent cell uses a packaged/retained frame.
#include "system_video720_assets.h"
#include "video720_posters.h"
#include "video720_policy.h"
#include "r53_video_policy.h"
static constexpr int video720SlotCount=r53VideoPolicy::slotCount;
static jclass video720Class;
static jmethodID video720Start,video720Update,video720Stop,video720Capacity,video720Visibility;
static bool video720JniFailed;
struct Video720Slot {const char*asset;unsigned texture,lastPollAt,startedAt;bool ready,visible,dirty,stopPending;void*context;float transform[16];};
static Video720Slot video720Slots[video720SlotCount];
static void*video720Context;
static unsigned video720UseCounter;
static unsigned video720PreviewProgram;static int video720PreviewMVP;
static bool ensureVideo720Jni(JNIEnv*env){
 if(!env||video720JniFailed)return false;if(video720Class)return true;
 jobject activity=videoActivity();if(!activity)return false;
 jclass ac=env->GetObjectClass(activity);
 jmethodID get=env->GetMethodID(ac,"getClassLoader","()Ljava/lang/ClassLoader;");
 jobject loader=get?env->CallObjectMethod(activity,get):nullptr;
 jclass lc=loader?env->GetObjectClass(loader):nullptr;
 jmethodID method=lc?env->GetMethodID(lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;"):nullptr;
 jstring name=env->NewStringUTF("org.emulationstation.frontend.SystemCardVideo720");
 jclass local=method?(jclass)env->CallObjectMethod(loader,method,name):nullptr;
 if(!videoJniException(env)&&local){
  video720Class=(jclass)env->NewGlobalRef(local);
  video720Start=env->GetStaticMethodID(video720Class,"start","(Landroid/app/Activity;IILjava/lang/String;Z)Z");
  video720Update=env->GetStaticMethodID(video720Class,"update","(I[F)I");
  video720Stop=env->GetStaticMethodID(video720Class,"stop","(I)V");
  video720Capacity=env->GetStaticMethodID(video720Class,"capacity","()I");
  video720Visibility=env->GetStaticMethodID(video720Class,"setVisible","(IZ)V");
 }
 if(local)env->DeleteLocalRef(local);env->DeleteLocalRef(name);
 if(lc)env->DeleteLocalRef(lc);if(loader)env->DeleteLocalRef(loader);
 env->DeleteLocalRef(ac);env->DeleteLocalRef(activity);
 if(videoJniException(env)||!video720Class||!video720Start||!video720Update||!video720Stop||!video720Capacity||!video720Visibility){video720JniFailed=true;return false;}
 return true;
}
// One RGB565 720x720 retained video frame per visited unique clip, independent of players.
// Retry belongs to the asset, independently of decoder ownership.
struct Video720Frame {const char*asset;unsigned texture,retryAt,lastUse;bool ready;};
static constexpr int video720FrameCount=sizeof(systemVideo720Definitions)/sizeof(systemVideo720Definitions[0])+sizeof(collectionVideoDefinitions)/sizeof(collectionVideoDefinitions[0]);
static Video720Frame video720Frames[video720FrameCount];
static unsigned video720FrameFbo;
static void video720DeleteTexture(unsigned texture){
 static void(*remove)(int,const unsigned*);
 if(!remove)remove=(void(*)(int,const unsigned*))dlsym(dlopen("libGLESv2.so",2),"glDeleteTextures");
 if(remove&&texture)remove(1,&texture);
}
static Video720Frame*video720Retained(const char*asset,bool create=false){
 if(!asset)return nullptr;Video720Frame*free=nullptr;
 for(auto&f:video720Frames){if(f.asset&&strcmp(f.asset,asset)==0)return &f;if(!f.asset&&!free)free=&f;}
 if(create&&free){free->asset=asset;return free;}return nullptr;
}
static bool video720Same(const char*a,const char*b){return a&&b&&strcmp(a,b)==0;}
static bool video720CanStart(const char*asset,unsigned now){
 auto*f=video720Retained(asset,true);return f&&(!f->retryAt||(int)(now-f->retryAt)>=0);
}
static void video720Backoff(const char*asset,unsigned now,unsigned delay){
 if(auto*f=video720Retained(asset,true))f->retryAt=now+delay;
}
static bool video720PaintedAsset(void*,const char*);
static bool video720FrameTexture(Video720Frame*f){
 if(f->texture){f->lastUse=++video720UseCounter;return true;}
 Video720Frame*oldest=nullptr;unsigned count=0;
 for(auto&candidate:video720Frames)if(candidate.texture){
  count++;
  if(&candidate!=f&&(!gui||!video720PaintedAsset(gui,candidate.asset))&&
      (!oldest||video720Older(candidate.lastUse,oldest->lastUse)))oldest=&candidate;
 }
 if(count>=video720TextureBudget){
  if(!oldest)return false;
  video720DeleteTexture(oldest->texture);oldest->texture=0;oldest->ready=false;
 }
 auto&s=spaceGL;s.GenTextures(1,&f->texture);if(!f->texture)return false;
 s.BindTexture(0x0de1,f->texture);s.TexImage2D(0x0de1,0,0x1907,720,720,0,0x1907,0x8363,nullptr);
 s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);
 s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);
 f->lastUse=++video720UseCounter;return true;
}
static bool ensureVideo720PreviewProgram(){
 auto&g=laserGL;if(video720PreviewProgram&&g.IsProgram(video720PreviewProgram))return true;
 const char*vertex="#version 100\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}";
 const char*fragment="#version 100\nprecision mediump float;uniform sampler2D frame;varying vec2 uv;void main(){gl_FragColor=vec4(texture2D(frame,uv).rgb,1.);}";
 video720PreviewProgram=compileSpaceProgram(vertex,fragment,true);if(!video720PreviewProgram)return false;
 video720PreviewMVP=g.GetUniformLocation(video720PreviewProgram,"MVPMatrix");g.UseProgram(video720PreviewProgram);
 spaceGL.Uniform1i(g.GetUniformLocation(video720PreviewProgram,"frame"),0);return true;
}
static void seedVideo720Preview(const char*asset){
 auto*f=video720Retained(asset,true);if(!f)return;f->lastUse=++video720UseCounter;if(f->ready)return;
 for(const auto&poster:video720Posters)if(video720Same(asset,poster.asset)){
  spaceGL.ActiveTexture(0x84c0);if(!video720FrameTexture(f))return;
  spaceGL.BindTexture(0x0de1,f->texture);
  // First decoded video frame, packed bottom row first to match retained FBO UVs.
  spaceGL.TexImage2D(0x0de1,0,0x1907,720,720,0,0x1907,0x8363,poster.pixels);
  f->ready=true;return;
 }
}
static void clearVideo720Frames(){
 bool same=videoGLContext()==video720Context;
 for(auto&f:video720Frames){if(same)video720DeleteTexture(f.texture);f={};}
 if(same&&video720FrameFbo){
  static void(*remove)(int,const unsigned*);
  if(!remove)remove=(void(*)(int,const unsigned*))dlsym(dlopen("libGLESv2.so",2),"glDeleteFramebuffers");
  if(remove)remove(1,&video720FrameFbo);
 }
 video720FrameFbo=0;
}
static void retainVideo720Frame(Video720Slot&v){
 if(!v.ready||!v.dirty||!v.texture||!v.context||videoGLContext()!=v.context||v.context!=video720Context)return;
 auto*f=video720Retained(v.asset,true);if(!f)return;
 SpaceState restore;VideoExternalBinding external;auto&g=laserGL;auto&s=spaceGL;
 if(!ensureSystemVideoProgram())return;
 s.ActiveTexture(0x84c0);
 if(!video720FrameTexture(f))return;
 if(!video720FrameFbo)s.GenFramebuffers(1,&video720FrameFbo);
 s.BindFramebuffer(0x8d40,video720FrameFbo);s.FramebufferTexture2D(0x8d40,0x8ce0,0x0de1,f->texture,0);
 if(s.CheckFramebufferStatus(0x8d40)!=0x8cd5){video720DeleteTexture(f->texture);f->texture=0;f->ready=false;return;}
 s.Viewport(0,0,720,720);s.Disable(0x0c11);s.Disable(0x0b71);s.Disable(0x0b44);s.Disable(0x0be2);s.Disable(0x809e);s.ColorMask(1,1,1,1);
 const float identity[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
 g.UseProgram(systemVideoProgram);g.UniformMatrix4fv(systemVideoMVP,1,0,identity);g.UniformMatrix4fv(systemVideoUV,1,0,v.transform);
 s.BindTexture(0x8d65,v.texture);
 Vertex q[4]={{-1,-1,0,0,0xffffffff},{-1,1,0,1,0xffffffff},{1,-1,1,0,0xffffffff},{1,1,1,1,0xffffffff}};
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);
 f->ready=true;v.dirty=false;
}
static bool retireVideo720Slot(int index,bool retain=true){
 auto&slot=video720Slots[index];
 if(!slot.asset&&!slot.texture){slot={};return true;}
 if(retain&&!slot.stopPending)retainVideo720Frame(slot);
 slot.visible=false;slot.stopPending=true;
 // Do not forget a decoder if JNI is temporarily unavailable. Retry on the next
 // render, and never create its replacement until Java has accepted every stop.
 JNIEnv*env=videoEnv();if(!env||!video720Class||!video720Stop)return false;
 env->CallStaticVoidMethod(video720Class,video720Stop,index);if(videoJniException(env))return false;
 // A pending stop can outlive an EGL context. Never delete its name in a new one.
 if(slot.context&&videoGLContext()==slot.context)video720DeleteTexture(slot.texture);
 slot={};return true;
}
static void pauseSystemVideo720(){
 // Release every decoder on list/settings entry, retain only bounded GPU previews.
 // Repeated hidden frames do no work after release; a failed JNI stop is retried.
 for(int i=0;i<video720SlotCount;i++)if(video720Slots[i].asset||video720Slots[i].texture)retireVideo720Slot(i,true);
}
static void stopSystemVideo720(){
 for(int i=0;i<video720SlotCount;i++)if(video720Slots[i].asset||video720Slots[i].texture)retireVideo720Slot(i,false);
 clearVideo720Frames();video720UseCounter=0;
}
static const char*video720Asset(void*p,int index){
 if(folderMode){
  U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
  if(index<0||!visible||visible+index>=end||visible[index]>=(U)folderCount)return nullptr;
  if(const auto*v=folderVideo(p,index))return v->asset;
  for(const auto&v:systemVideo720Definitions)if(strcmp(folderPlatform,v.key)==0)return v.asset;
  return nullptr;
 }
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
 if(index<0||!visible||visible+index>=end||visible[index]>=(U)systemCount)return nullptr;
 const char*key=strData(items+visible[index]*0xe8+0x60);
 for(const auto&v:systemVideo720Definitions)if(strcmp(key,v.key)==0)return v.asset;
 return nullptr;
}
static bool video720PaintedAsset(void*p,const char*asset){
 for(int i=0;i<paintedCount;i++)if(video720Same(video720Asset(p,painted[i].index),asset))return true;
 return false;
}
static r53VideoPolicy::Menu video720Menu(void*p){
 U begin=at<U>(p,0xf8),end=at<U>(p,0x100);
 U count=begin&&end>=begin?(end-begin)/sizeof(U):0;
 return {systemsMode,modal(p),at<int>(p,0x370),count>0x7fffffffu?0x7fffffff:(int)count};
}
static void drawSystemVideo720(void*p){
 auto menu=video720Menu(p);
 if(!r53VideoPolicy::menuAllowsVideo(menu)||paintedCount<=0){pauseSystemVideo720();return;}
 void*context=videoGLContext();
 if(!context||!loadSpaceGL()){pauseSystemVideo720();return;}
 if(video720Context!=context){stopSystemVideo720();video720Context=context;video720PreviewProgram=0;}
 SpaceState restore;VideoExternalBinding external;auto&g=laserGL;auto&s=spaceGL;
 if(!restore.program){pauseSystemVideo720();return;}
 float mvp[16];g.GetUniformfv(restore.program,at<int>((void*)base,0x3cf4c8),mvp);
 if(!ensureVideo720PreviewProgram()){pauseSystemVideo720();return;}
 // Poster rendering has no dependency on Java/MediaPlayer availability.
 bool liveSupported=ensureSystemVideoProgram();
 JNIEnv*env=videoEnv();bool jniReady=ensureVideoJni(env)&&ensureVideo720Jni(env);
 int limit=0;
 if(jniReady){limit=env->CallStaticIntMethod(video720Class,video720Capacity);if(videoJniException(env)){jniReady=false;limit=0;}}
 unsigned now=fn<unsigned(*)()>(0x39e240)();
 int cursor=at<int>(p,0xf0);const char*focusedAsset=video720Asset(p,cursor);
 bool focusPainted=false;
 for(int k=0;k<paintedCount;k++)if(painted[k].index==cursor){focusPainted=true;break;}
 r53VideoPolicy::Slot policySlots[video720SlotCount];
 for(int i=0;i<video720SlotCount;i++){
  const auto&v=video720Slots[i];
  // A stop that failed must finish even when navigation returns to that asset.
  policySlots[i]={v.stopPending?nullptr:v.asset,v.texture!=0||v.stopPending};
 }
 r53VideoPolicy::Frame frame{menu,paintedCount,focusPainted,liveSupported&&jniReady,limit,focusedAsset};
 auto decision=r53VideoPolicy::decide(frame,policySlots);
 bool stopped=true;
 for(int i=0;i<video720SlotCount;i++)if(decision.retireMask&(1u<<i))if(!retireVideo720Slot(i))stopped=false;
 if(!stopped){pauseSystemVideo720();decision.wantedAsset=nullptr;decision.keepSlot=decision.startSlot=-1;}
 static const char*loggedFocus;
 if(loggedFocus!=decision.wantedAsset){loggedFocus=decision.wantedAsset;__android_log_print(4,"TurboCarousel","VIDEO single focused decoder; static adjacent previews: %s",loggedFocus?loggedFocus:"none");}
 for(int k=0;k<paintedCount;k++)seedVideo720Preview(video720Asset(p,painted[k].index));
 int activeSlot=decision.keepSlot;
 if(decision.startSlot>=0&&video720CanStart(decision.wantedAsset,now)){
  int slot=decision.startSlot;auto&v=video720Slots[slot];v.asset=decision.wantedAsset;
  s.ActiveTexture(0x84c0);s.GenTextures(1,&v.texture);v.context=context;
  if(v.texture){
   s.BindTexture(0x8d65,v.texture);
   s.TexParameteri(0x8d65,0x2801,0x2601);s.TexParameteri(0x8d65,0x2800,0x2601);
   s.TexParameteri(0x8d65,0x2802,0x812f);s.TexParameteri(0x8d65,0x2803,0x812f);
   jobject a=videoActivity();jstring asset=a?env->NewStringUTF(v.asset):nullptr;
   bool failed=videoJniException(env);
   bool started=!failed&&a&&asset&&env->CallStaticBooleanMethod(video720Class,video720Start,a,slot,(jint)v.texture,asset,(jboolean)true);
   if(videoJniException(env))started=false;
   if(asset)env->DeleteLocalRef(asset);if(a)env->DeleteLocalRef(a);
   v.startedAt=now;
   if(started){v.visible=true;activeSlot=slot;}
   else{video720Backoff(v.asset,now,1000);retireVideo720Slot(slot,false);activeSlot=-1;}
  }else{video720Backoff(v.asset,now,1000);retireVideo720Slot(slot,false);activeSlot=-1;}
 }
 if(activeSlot>=0){
  auto&v=video720Slots[activeSlot];
  if(v.texture&&!v.stopPending&&!v.visible){
   env->CallStaticVoidMethod(video720Class,video720Visibility,activeSlot,(jboolean)true);
   if(videoJniException(env)){video720Backoff(v.asset,now,1000);retireVideo720Slot(activeSlot,false);activeSlot=-1;}
   else v.visible=true;
  }
 }
 int result[video720SlotCount]={};float matrices[video720SlotCount][16];
 if(activeSlot>=0){
  int i=activeSlot;auto&v=video720Slots[i];
  if(v.texture&&!v.stopPending){
   // Keep the existing first-frame timeout and per-asset retry policy.
   if(!v.ready&&(unsigned)(now-v.startedAt)>20000){video720Backoff(v.asset,now,10000);retireVideo720Slot(i,false);}
   else{
    v.lastPollAt=now;result[i]=env->CallStaticIntMethod(video720Class,video720Update,i,systemVideoTransform);
    if(videoJniException(env))result[i]=-2;
    if(result[i]<0){video720Backoff(v.asset,now,result[i]==-2?10000:1000);retireVideo720Slot(i,false);result[i]=0;}
    else if(result[i]>0){
     env->GetFloatArrayRegion(systemVideoTransform,0,16,matrices[i]);
     if(videoJniException(env)){video720Backoff(v.asset,now,10000);retireVideo720Slot(i,false);result[i]=0;}
     else{
      bool first=!v.ready;memcpy(v.transform,matrices[i],sizeof(v.transform));v.ready=true;v.dirty=true;
      auto*f=video720Retained(v.asset);if(first||!f||!f->ready)retainVideo720Frame(v);
     }
    }
   }
  }
 }
 // A retained frame survives decoder retirement and remains visible during
 // prepare/seek. Exactly one source is drawn for each native carousel cell.
 for(int k=0;k<paintedCount;k++){
  const auto&r=painted[k];const char*asset=video720Asset(p,r.index);if(!asset)continue;
  int live=-1;
  for(int i=0;i<video720SlotCount;i++)if(r.index==cursor&&result[i]>0&&video720Same(video720Slots[i].asset,asset)){live=i;break;}
  if(live>=0){
   g.UseProgram(systemVideoProgram);g.UniformMatrix4fv(systemVideoMVP,1,0,mvp);
   s.ActiveTexture(0x84c0);s.BindTexture(0x8d65,video720Slots[live].texture);
   g.UniformMatrix4fv(systemVideoUV,1,0,matrices[live]);
  }else{
   const auto*f=video720Retained(asset);if(!f||!f->ready)continue;
   g.UseProgram(video720PreviewProgram);g.UniformMatrix4fv(video720PreviewMVP,1,0,mvp);
   s.ActiveTexture(0x84c0);s.BindTexture(0x0de1,f->texture);
  }
  float lo=.00138889f,hi=.99861111f;
  Vertex q[4]={{r.x,r.y,lo,hi,0xffffffff},{r.x,r.y+r.h,lo,lo,0xffffffff},{r.x+r.w,r.y,hi,hi,0xffffffff},{r.x+r.w,r.y+r.h,hi,lo,0xffffffff}};
  roundedQuad(q,4,5);
 }
}
