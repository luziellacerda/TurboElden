// One focused 720p30 loop. Three warm players plus one transient preview decoder.
#include "system_video720_assets.h"
#include "video720_posters.h"
#include "video720_policy.h"
static constexpr int video720SlotCount=4;
static jclass video720Class;
static jmethodID video720Start,video720Update,video720Stop,video720Capacity,video720Visibility;
static bool video720JniFailed;
struct Video720Slot {const char*asset;unsigned texture,lastPollAt,startedAt;bool ready,visible,dirty,scratch;float transform[16];};
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
// Retry belongs to the asset, not a scratch slot, so one bad clip cannot starve the rest.
struct Video720Frame {const char*asset;unsigned texture,retryAt,lastUse;bool ready;};
static constexpr int video720FrameCount=sizeof(systemVideo720Definitions)/sizeof(systemVideo720Definitions[0]);
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
static bool video720Contains(const char*const*assets,int count,const char*asset){
 for(int i=0;i<count;i++)if(video720Same(assets[i],asset))return true;return false;
}
static bool video720CanStart(const char*asset,unsigned now){
 auto*f=video720Retained(asset,true);return f&&(!f->retryAt||(int)(now-f->retryAt)>=0);
}
static bool video720NeedsFrame(const char*asset,unsigned now){
 auto*f=video720Retained(asset,true);return f&&!f->ready&&video720CanStart(asset,now);
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
 if(!v.ready||!v.dirty||!v.texture||videoGLContext()!=video720Context)return;
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
static void retireVideo720Slot(int index,bool retain=true){
 auto&slot=video720Slots[index];if(retain)retainVideo720Frame(slot);
 JNIEnv*env=videoEnv();if(env&&video720Class&&video720Stop){env->CallStaticVoidMethod(video720Class,video720Stop,index);videoJniException(env);}
 if(videoGLContext()==video720Context)video720DeleteTexture(slot.texture);
 slot={};
}
static void pauseSystemVideo720(){
 // Release every decoder on list/settings entry, retain only bounded GPU previews.
 // Repeated hidden-menu frames do no work after the first release.
 for(int i=0;i<video720SlotCount;i++)if(video720Slots[i].asset||video720Slots[i].texture)retireVideo720Slot(i,true);
}
static void stopSystemVideo720(){
 for(int i=0;i<video720SlotCount;i++)if(video720Slots[i].asset||video720Slots[i].texture)retireVideo720Slot(i,false);
 clearVideo720Frames();video720UseCounter=0;
}
static const char*video720Asset(void*p,int index){
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
static void drawSystemVideo720(void*p){
 if(!systemsMode||modal(p)||at<int>(p,0x370)!=3){pauseSystemVideo720();return;}
 if(!paintedCount||!loadSpaceGL())return;
 JNIEnv*env=videoEnv();if(!ensureVideoJni(env)||!ensureVideo720Jni(env))return;
 void*context=videoGLContext();if(!context)return;
 if(video720Context!=context){stopSystemVideo720();video720Context=context;video720PreviewProgram=0;}
 int limit=env->CallStaticIntMethod(video720Class,video720Capacity);if(videoJniException(env))return;
 if(limit<0)limit=0;if(limit>video720SlotCount)limit=video720SlotCount;
 unsigned now=fn<unsigned(*)()>(0x39e240)();
 int cursor=at<int>(p,0xf0);
 const char*focusedAsset=video720Asset(p,cursor);
 const char*warm[3]={};int warmCount=0;
 // Reserve one decoder for uncached visible previews. Under constrained hardware,
 // preserve the focus first and the previous (left) neighbour before the next one.
 int warmBudget=limit>1?(limit-1<3?limit-1:3):limit;
 auto addWarm=[&](const char*asset){
  if(asset&&warmCount<warmBudget&&!video720Contains(warm,warmCount,asset))warm[warmCount++]=asset;
 };
 addWarm(focusedAsset);addWarm(video720Asset(p,cursor-1));addWarm(video720Asset(p,cursor+1));
 // A one-decoder device must briefly retain the focused frame while it prepares
 // missing sides. Once sides are ready, the focused player resumes its normal loop.
 if(limit==1){
  auto*f=video720Retained(focusedAsset);
  bool canPark=!focusedAsset||(f&&f->ready)||!video720CanStart(focusedAsset,now);
  if(canPark)for(int i=0;i<paintedCount;i++){
   const char*asset=video720Asset(p,painted[i].index);
   if(!video720Same(asset,focusedAsset)&&video720NeedsFrame(asset,now)){warmCount=0;break;}
  }
 }
 const char*scratch=nullptr;
 if(limit>warmCount){
  // Finish an in-flight scratch before selecting a new one: paint-order changes
  // during a slide must not repeatedly cancel the same preparation.
  for(auto&v:video720Slots)if(v.asset&&!video720Contains(warm,warmCount,v.asset)&&video720PaintedAsset(p,v.asset)&&video720NeedsFrame(v.asset,now)){scratch=v.asset;break;}
  int bestDistance=0x7fffffff;
  if(!scratch)for(int i=0;i<paintedCount;i++){
   const char*asset=video720Asset(p,painted[i].index);
   int distance=painted[i].index-cursor;if(distance<0)distance=-distance;
   if(!video720Contains(warm,warmCount,asset)&&video720NeedsFrame(asset,now)&&distance<bestDistance){scratch=asset;bestDistance=distance;}
  }
 }
 const char*wanted[video720SlotCount]={};int wantedCount=0;
 for(int i=0;i<warmCount;i++)wanted[wantedCount++]=warm[i];
 if(scratch)wanted[wantedCount++]=scratch;
 // Retain before pausing/preempting. Only the focus may continue decoding after
 // a first frame; every other player pauses from its Java frame callback.
 for(int i=0;i<video720SlotCount;i++){
  auto&v=video720Slots[i];if(!v.asset)continue;
  bool keep=video720Contains(wanted,wantedCount,v.asset);
  bool visible=keep&&video720Same(v.asset,focusedAsset)&&video720Contains(warm,warmCount,v.asset);
  if(v.visible&&!visible){
   retainVideo720Frame(v);v.visible=false;
   if(v.texture){env->CallStaticVoidMethod(video720Class,video720Visibility,i,(jboolean)false);videoJniException(env);}
  }
  if(!keep){retireVideo720Slot(i);continue;}
  v.scratch=video720Same(v.asset,scratch);
 }
 static const char*loggedFocus;
 if(loggedFocus!=focusedAsset){loggedFocus=focusedAsset;__android_log_print(4,"TurboCarousel","VIDEO focus-only 720p30, warm3+scratch1: %s",focusedAsset?focusedAsset:"none");}
 SpaceState restore;VideoExternalBinding external;auto&g=laserGL;auto&s=spaceGL;
 if(!restore.program)return;
 float mvp[16];g.GetUniformfv(restore.program,at<int>((void*)base,0x3cf4c8),mvp);
 bool liveSupported=ensureSystemVideoProgram();
 if(!ensureVideo720PreviewProgram())return;
 for(int k=0;k<paintedCount;k++)seedVideo720Preview(video720Asset(p,painted[k].index));
 if(!liveSupported)wantedCount=0;
 for(int n=0;n<wantedCount;n++){
  int slot=-1;
  for(int j=0;j<video720SlotCount;j++)if(video720Same(video720Slots[j].asset,wanted[n])){slot=j;break;}
  if(slot<0){
   if(!video720CanStart(wanted[n],now))continue;
   for(int j=0;j<video720SlotCount;j++)if(!video720Slots[j].asset){slot=j;video720Slots[j].asset=wanted[n];break;}
  }
  if(slot<0)continue;auto&v=video720Slots[slot];
  bool visible=video720Same(v.asset,focusedAsset)&&video720Contains(warm,warmCount,v.asset);
  bool visibilityChanged=v.visible!=visible;v.visible=visible;v.scratch=video720Same(v.asset,scratch);
  if(!v.texture){
   s.ActiveTexture(0x84c0);s.GenTextures(1,&v.texture);s.BindTexture(0x8d65,v.texture);
   s.TexParameteri(0x8d65,0x2801,0x2601);s.TexParameteri(0x8d65,0x2800,0x2601);
   s.TexParameteri(0x8d65,0x2802,0x812f);s.TexParameteri(0x8d65,0x2803,0x812f);
   jobject a=videoActivity();jstring asset=env->NewStringUTF(v.asset);
   bool started=a&&env->CallStaticBooleanMethod(video720Class,video720Start,a,slot,(jint)v.texture,asset,(jboolean)visible);
   env->DeleteLocalRef(asset);if(a)env->DeleteLocalRef(a);
   v.startedAt=now;
   if(videoJniException(env)||!started){video720Backoff(v.asset,now,1000);retireVideo720Slot(slot,false);continue;}
  }
  if(v.texture&&visibilityChanged){env->CallStaticVoidMethod(video720Class,video720Visibility,slot,(jboolean)visible);videoJniException(env);}
 }
 int result[video720SlotCount]={};float matrices[video720SlotCount][16];
 for(int i=0;i<video720SlotCount;i++){
  auto&v=video720Slots[i];if(!v.texture)continue;
  // Native backup deadline covers seek-complete/preparation callbacks that never
  // deliver a frame. Back off this asset and let another scratch use the slot.
  if(!v.ready&&(unsigned)(now-v.startedAt)>20000){video720Backoff(v.asset,now,10000);retireVideo720Slot(i,false);continue;}
  if(v.ready&&!v.visible&&!v.scratch&&(unsigned)(now-v.lastPollAt)<1000)continue;
  v.lastPollAt=now;
  result[i]=env->CallStaticIntMethod(video720Class,video720Update,i,systemVideoTransform);
  if(videoJniException(env))result[i]=-2;
  if(result[i]<0){video720Backoff(v.asset,now,result[i]==-2?10000:1000);retireVideo720Slot(i,false);continue;}
  if(result[i]>0){
   env->GetFloatArrayRegion(systemVideoTransform,0,16,matrices[i]);if(videoJniException(env)){result[i]=0;continue;}
   bool first=!v.ready;memcpy(v.transform,matrices[i],sizeof(v.transform));v.ready=true;
   if(first||v.visible)v.dirty=true;
   auto*f=video720Retained(v.asset);
   if(first||!f||!f->ready)retainVideo720Frame(v);
   if(v.scratch){
    // Release the decoder only after the GL copy is complete. FBO failure also
    // receives a cooldown, instead of endlessly retrying one broken preview.
    f=video720Retained(v.asset);
    if(!f||!f->ready)video720Backoff(v.asset,now,10000);
    retireVideo720Slot(i,false);result[i]=0;
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
