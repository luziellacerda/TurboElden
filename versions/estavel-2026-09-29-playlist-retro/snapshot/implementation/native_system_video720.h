// One 720p stream per clip. Retained GPU frames bridge decoder restarts with no green card.
#include "system_video720_assets.h"
static constexpr int video720SlotCount=12;
static jclass video720Class;
static jmethodID video720Start,video720Update,video720Stop,video720Capacity,video720Visibility;
static bool video720JniFailed;
struct Video720Slot {const char*asset;unsigned texture,retryAt;bool ready,visible,dirty;float transform[16];};
static Video720Slot video720Slots[video720SlotCount];
static void*video720Context;
static unsigned video720NextStart;
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
// One RGB565 720x720 retained video frame per visited unique clip (27 today).
// This is decoded video in GPU memory, not a photo asset, atlas or second player.
struct Video720Frame {const char*asset;unsigned texture;bool ready;};
static constexpr int video720FrameCount=40;
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
 if(!v.ready||!v.dirty||!v.texture||videoGLContext()!=video720Context)return;
 auto*f=video720Retained(v.asset,true);if(!f)return;
 SpaceState restore;VideoExternalBinding external;auto&g=laserGL;auto&s=spaceGL;
 if(!ensureSystemVideoProgram())return;
 s.ActiveTexture(0x84c0);
 if(!f->texture){
  s.GenTextures(1,&f->texture);s.BindTexture(0x0de1,f->texture);
  s.TexImage2D(0x0de1,0,0x1907,720,720,0,0x1907,0x8363,nullptr);
  s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);
  s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);
 }
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
static void retireVideo720Slot(int index,bool retain=true){
 auto&slot=video720Slots[index];if(retain)retainVideo720Frame(slot);
 JNIEnv*env=videoEnv();if(env&&video720Class&&video720Stop){env->CallStaticVoidMethod(video720Class,video720Stop,index);videoJniException(env);}
 if(videoGLContext()==video720Context)video720DeleteTexture(slot.texture);
 slot.texture=0;slot.ready=false;slot.dirty=false;
}
static void stopSystemVideo720(){
 for(int i=0;i<video720SlotCount;i++){if(video720Slots[i].asset||video720Slots[i].texture)retireVideo720Slot(i,false);video720Slots[i]={};}
 clearVideo720Frames();video720NextStart=0;
}
static const char*video720Asset(void*p,int index){
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
 if(index<0||!visible||visible+index>=end||visible[index]>=(U)systemCount)return nullptr;
 const char*key=strData(items+visible[index]*0xe8+0x60);
 for(const auto&v:systemVideo720Definitions)if(strcmp(key,v.key)==0)return v.asset;
 return nullptr;
}
static void drawSystemVideo720(void*p){
 if(!systemsMode||modal(p)||at<int>(p,0x370)!=3){stopSystemVideo720();return;}
 if(!paintedCount||!loadSpaceGL())return;
 JNIEnv*env=videoEnv();if(!ensureVideoJni(env)||!ensureVideo720Jni(env))return;
 void*context=videoGLContext();if(!context)return;
 if(video720Context!=context){stopSystemVideo720();video720Context=context;}
 int limit=env->CallStaticIntMethod(video720Class,video720Capacity);if(videoJniException(env))return;
 if(limit<0)limit=0;if(limit>video720SlotCount)limit=video720SlotCount;
 const char*wanted[video720SlotCount];bool wantedVisible[video720SlotCount]={};
 int wantedCount=0,cursor=at<int>(p,0xf0),firstVisible=cursor,lastVisible=cursor;
 auto addWanted=[&](const char*asset,bool visible){
  if(!asset)return;
  for(int k=0;k<wantedCount;k++)if(strcmp(wanted[k],asset)==0){wantedVisible[k]=wantedVisible[k]||visible;return;}
  if(wantedCount<limit){wanted[wantedCount]=asset;wantedVisible[wantedCount++]=visible;}
 };
 for(int j=0;j<paintedCount;j++){if(painted[j].index<firstVisible)firstVisible=painted[j].index;if(painted[j].index>lastVisible)lastVisible=painted[j].index;}
 // Visible cells always have priority. Their previous/next neighbours keep the
 // exact same decoded frame/texture while paused outside the viewport.
 for(int distance=0;distance<20;distance++)for(int j=0;j<paintedCount;j++){
  if((int)absolute((float)(painted[j].index-cursor))==distance)addWanted(video720Asset(p,painted[j].index),true);
 }
 // The previous side enters directly into the large card. Give it a deeper
 // warm window while keeping the immediate next clip ready as well.
 addWanted(video720Asset(p,firstVisible-1),false);
 addWanted(video720Asset(p,lastVisible+1),false);
 for(int offset=2;offset<=4;offset++)addWanted(video720Asset(p,firstVisible-offset),false);
 addWanted(video720Asset(p,lastVisible+2),false);
 // Use remaining decoder slots for recently visited clips instead of tearing
 // them down merely because they crossed the warm-window boundary.
 for(int i=0;i<video720SlotCount;i++)if(video720Slots[i].asset)addWanted(video720Slots[i].asset,false);
 for(int i=0;i<video720SlotCount;i++)if(video720Slots[i].asset){
  bool keep=false;for(int j=0;j<wantedCount;j++)if(strcmp(wanted[j],video720Slots[i].asset)==0)keep=true;
  if(!keep){retireVideo720Slot(i);video720Slots[i]={};}
 }
 SpaceState restore;VideoExternalBinding external;auto&g=laserGL;auto&s=spaceGL;
 if(!restore.program)return;
 float mvp[16];g.GetUniformfv(restore.program,at<int>((void*)base,0x3cf4c8),mvp);
 if(!ensureSystemVideoProgram())return;
 unsigned now=fn<unsigned(*)()>(0x39e240)();
 for(int n=0;n<wantedCount;n++){
  int slot=-1;
  for(int j=0;j<video720SlotCount;j++)if(video720Slots[j].asset&&strcmp(video720Slots[j].asset,wanted[n])==0){slot=j;break;}
  if(slot<0)for(int j=0;j<video720SlotCount;j++)if(!video720Slots[j].asset){slot=j;video720Slots[j].asset=wanted[n];break;}
  if(slot<0)continue;auto&v=video720Slots[slot];
  if(v.visible&&!wantedVisible[n])retainVideo720Frame(v);
  v.visible=wantedVisible[n];
  if(!v.texture&&(!v.retryAt||(int)(now-v.retryAt)>=0)&&(!video720NextStart||(int)(now-video720NextStart)>=0)){
   s.ActiveTexture(0x84c0);s.GenTextures(1,&v.texture);s.BindTexture(0x8d65,v.texture);
   s.TexParameteri(0x8d65,0x2801,0x2601);s.TexParameteri(0x8d65,0x2800,0x2601);
   s.TexParameteri(0x8d65,0x2802,0x812f);s.TexParameteri(0x8d65,0x2803,0x812f);
   jobject a=videoActivity();jstring asset=env->NewStringUTF(v.asset);
   bool started=a&&env->CallStaticBooleanMethod(video720Class,video720Start,a,slot,(jint)v.texture,asset,(jboolean)wantedVisible[n]);
   env->DeleteLocalRef(asset);if(a)env->DeleteLocalRef(a);
   video720NextStart=now+80;
   if(videoJniException(env)||!started){retireVideo720Slot(slot,false);v.retryAt=now+1000;}
  }
  if(v.texture){env->CallStaticVoidMethod(video720Class,video720Visibility,slot,(jboolean)wantedVisible[n]);videoJniException(env);}
 }
 // Draw in native paint order so transitioning cards retain their correct stacking.
 int result[video720SlotCount];float matrices[video720SlotCount][16];
 for(int i=0;i<video720SlotCount;i++){
  result[i]=0;auto&v=video720Slots[i];if(!v.texture)continue;
  result[i]=env->CallStaticIntMethod(video720Class,video720Update,i,systemVideoTransform);
  if(videoJniException(env))result[i]=-2;
  if(result[i]<0){retireVideo720Slot(i,false);v.retryAt=now+(result[i]==-2?10000:1000);continue;}
  if(result[i]>0){
   env->GetFloatArrayRegion(systemVideoTransform,0,16,matrices[i]);if(videoJniException(env)){result[i]=0;continue;}
   bool first=!v.ready;memcpy(v.transform,matrices[i],sizeof(v.transform));v.ready=true;
   if(first||v.visible)v.dirty=true;
   auto*f=video720Retained(v.asset);
   if(first||!f||!f->ready)retainVideo720Frame(v);
  }
 }
 // Exactly one source is drawn per cell: live texture OR its retained video
 // frame. A restarted player cannot expose the blank card underneath.
 for(int k=0;k<paintedCount;k++){
  const auto&r=painted[k];const char*asset=video720Asset(p,r.index);if(!asset)continue;
  int live=-1;
  for(int i=0;i<video720SlotCount;i++)if(result[i]>0&&video720Slots[i].asset&&strcmp(video720Slots[i].asset,asset)==0){live=i;break;}
  if(live>=0){
   g.UseProgram(systemVideoProgram);g.UniformMatrix4fv(systemVideoMVP,1,0,mvp);
   s.ActiveTexture(0x84c0);s.BindTexture(0x8d65,video720Slots[live].texture);
   g.UniformMatrix4fv(systemVideoUV,1,0,matrices[live]);
  }else{
   const auto*f=video720Retained(asset);if(!f||!f->ready||!shipCompositeProgram)continue;
   g.UseProgram(shipCompositeProgram);g.UniformMatrix4fv(shipCompositeMVP,1,0,mvp);g.Uniform1f(shipCompositeOpacity,1.f);
   s.ActiveTexture(0x84c0);s.BindTexture(0x0de1,f->texture);
  }
  float lo=.00138889f,hi=.99861111f;
  Vertex q[4]={{r.x,r.y,lo,hi,0xffffffff},{r.x,r.y+r.h,lo,lo,0xffffffff},{r.x+r.w,r.y,hi,hi,0xffffffff},{r.x+r.w,r.y+r.h,hi,lo,0xffffffff}};
  roundedQuad(q,4,5);
 }
}
