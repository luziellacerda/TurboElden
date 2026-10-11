#pragma once
// GuiStore/SDL thread only. Compile the existing programs in its current GL
// context while loading still owns the screen, never in a worker context.
struct StartupLoadingBridge {
 void(*ready)(void*,bool);unsigned(*stage)(void*);bool resolved;
};
static StartupLoadingBridge startupLoadingBridge;
static bool startupLoadingBridgeAvailable(){
 auto&b=startupLoadingBridge;if(!b.resolved){
  b.resolved=true;void*lib=dlopen("libstation_frontend.so",2);
  if(lib){b.ready=(decltype(b.ready))dlsym(lib,"StationLoading_graphicsReady");
   b.stage=(decltype(b.stage))dlsym(lib,"StationLoading_stage");}
 }
 return b.ready&&b.stage;
}
struct StartupLoadingPreparation {
 void*owner;void*context;bool prepared,disabled;
};
static StartupLoadingPreparation startupLoadingPreparation;
static void startupLoadingBeforeUpdate(void*p){
 if(at<int>(p,0x370)!=0){
  // Preserve the inherited revalidation/recovery path after a context change.
  if(stationGraphicsEnabled(1u))prewarmMagazinePrograms();return;
 }
 auto&s=startupLoadingPreparation;auto&b=startupLoadingBridge;
 if(s.owner!=p){s={};s.owner=p;b.ready(p,false);}
 if(!stationGraphicsEnabled(1u)){
  if(!s.prepared||!s.disabled){s.prepared=true;s.disabled=true;b.ready(p,true);}
  return; // Effects disabled: no EGL query, shader or field work.
 }
 void*context=magazineContext();
 if(s.disabled||s.context!=context){
  s.disabled=false;s.prepared=false;s.context=context;b.ready(p,false);
 }
 // Stage bit 1 is set by the real black loading draw. Its next SDL update
 // occurs after that render, so initialization cannot precede the first frame.
 if(!context||s.prepared||(b.stage(p)&1u)==0)return;
 bool complete=prewarmMagazinePrograms();s.prepared=true;b.ready(p,true);
 // A driver rejection already selects the inherited R104/R106/base-art
 // fallback. Complete that attempt rather than retrying it forever in loading.
 __android_log_print(complete?4:5,"TurboCarousel",
  "MAGAZINE loading preparation completed; programsReady=%d; inherited fallback preserved",complete?1:0);
}
static void startupIntroHook(void*p,float delta){
 if(at<int>(p,0x370)==0&&(startupLoadingBridge.stage(p)&2u)==0){
  // Keep the original elapsed intro clock, but do not advance phases or run
  // the cover-ready timeout until the terminal catalog/graphics frame was drawn.
  at<float>(p,0x374)+=delta;return;
 }
 fn<void(*)(void*,float)>(0x2291b0)(p,delta);
}
