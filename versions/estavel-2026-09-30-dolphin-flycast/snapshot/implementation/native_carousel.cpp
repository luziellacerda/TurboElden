// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// TurboramaStation native system carousel. Baseline ABI a1ae357d... only.
// Original GuiStore renderer, touch handling, catalog and download code remain in libmain.
using U=unsigned long; using B=unsigned char;
extern "C" {
void* dlopen(const char*,int); void* dlsym(void*,const char*);
struct DlInfo {const char* fname;void* base;const char* symbol;void* address;};
int dladdr(const void*,DlInfo*); int mprotect(void*,U,int); long sysconf(int);
int __android_log_print(int,const char*,const char*,...);
void* memcpy(void*,const void*,U); void* memset(void*,int,U); U strlen(const char*); int strcmp(const char*,const char*);
int mkdir(const char*,unsigned); void* fopen(const char*,const char*); U fwrite(const void*,U,U,void*); int fclose(void*);
}
#include "native_policy.h"
#include "systems.h"
#include "relocations.h"
static bool storeUiHideMessage;
static void layoutSearchPresentation(void*);
static void stopSystemVideo720();
static void pauseRetroMusicForGame();
static void drawSystemVideo720(void*);
static void stopSystemVideo();
static U base; static bool systemsMode=true; static void* gui; static int lastSystem;
alignas(16) static B facade[0x138]; static B* items; static int systemCount;
static int syncedRevision=-1; static U syncedItems; static U syncedSize; static char systemLabel[24]="PLATAFORMAS";
struct NativeVector {B* begin; B* end; B* capacity;};
static unsigned coverCheckAt;static bool coverCheckPending;
static bool modelReady; static bool started; static unsigned lastBackTick; static bool handledBack;
template<class T> static T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
template<class T> static T fn(U a){return reinterpret_cast<T>(base+a);}
using V=void(*)(void*);
static void log(const char*msg){__android_log_print(4,"TurboCarousel","%s",msg);}
static void strAssign(void*p,const char*s){
 static void* sym;
 if(!sym)sym=dlsym(dlopen("libmain.so",2),"_ZNSt6__ndk112basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEE6assignEPKc");
 ((void*(*)(void*,const char*))sym)(p,s);
}
static const char* strData(const void*p){const B*b=(const B*)p;return b[0]&1?*(const char*const*)(b+16):(const char*)b+1;}
static bool starts(const char*t,const char*prefix){while(*prefix){if(*t++!=*prefix++)return false;}return true;}
static void initModel(){
 if(modelReady)return;
 fn<V>(0x18876c)(facade);
 mkdir("/data/data/org.emulationstation.frontend/files/native-systems",0700);
 for(int i=0;i<NSYSTEMS;i++){
  const auto&s=systems[i];void*f=fopen(s.path,"wb");if(f){fwrite(s.image,1,s.length,f);fclose(f);}
 }
 at<int>(facade,0xa8)=0x54530001;at<int>(facade,0x50)=1;
 modelReady=true;
}
static void clearTextures(void*); static void invalidate(void*); static void rebuildHook(void*); static void refreshHook(void*);
static void exportCatalog(void*real){
 void*f=fopen("/storage/emulated/0/EmulationStation/native-catalog.tsv","wb");if(!f)return;
 const U fields[]={0,0x60,0x18,0x90,0x78};
 for(B*it=at<B*>(real,0x88);it<at<B*>(real,0x90);it+=0xe8){
  for(int j=0;j<5;j++){
   const char*t=strData(it+fields[j]);for(;*t;t++){char c=(*t=='\t'||*t=='\n'||*t=='\r')?' ':*t;fwrite(&c,1,1,f);}
   fwrite(j==4?"\n":"\t",1,1,f);
  }
 }
 fclose(f);log("Native catalog identity export complete");
}
static void syncModel(void*p){
 initModel();void*real=fn<void*(*)()>(0x1887dc)();
 if(at<int>(real,0x50)!=2)return;
 int rev=at<int>(real,0xa8);U begin=at<U>(real,0x88),size=at<U>(real,0x90)-begin;
 if(rev==syncedRevision&&begin==syncedItems&&size==syncedSize)return;
 syncedRevision=rev;syncedItems=begin;syncedSize=size;
 exportCatalog(real);
 // Only entries with no artwork URL receive system artwork. Real game cover URLs/cache are preserved.
 int defaults=0;
 for(B*it=at<B*>(real,0x88);it<at<B*>(real,0x90);it+=0xe8){
  if(!*strData(it+0x48)&&!*strData(it+0xc8))for(int j=0;j<NSYSTEMS;j++){
   if(strcmp(strData(it+0x60),systems[j].key)==0){strAssign(it+0xc8,systems[j].path);defaults++;break;}
  }
 }
 if(defaults)__android_log_print(4,"TurboCarousel","Default system artwork for %d games without a catalog cover URL",defaults);
 // Use precisely the same native list as the original platform panel, including its order.
 // A 24-byte return value uses x8, matching std::vector<string>'s Android AArch64 ABI.
 NativeVector names=fn<NativeVector(*)(void*)>(0x18f610)(real);
 int rawCount=(int)((names.end-names.begin)/24),count=0;
 B**selectedNames=(B**)fn<void*(*)(U)>(0x39d9c0)((U)(rawCount?rawCount:1)*sizeof(B*));
 for(int i=0;i<rawCount;i++){
  B*name=names.begin+i*24;const char*key=strData(name);
  if(strcmp(key,"colecovision")==0||strcmp(key,"fds")==0||strcmp(key,"gameandwatch")==0||strcmp(key,"Gameboy")==0||strcmp(key,"Odyssey 2")==0)continue;
  selectedNames[count++]=name;
 }
 bool changed=count!=systemCount;
 for(int i=0;i<count&&!changed;i++)changed=strcmp(strData(selectedNames[i]),strData(items+i*0xe8+0x60))!=0;
 if(!changed){fn<V>(0x39d820)(selectedNames);fn<V>(0x15f5c4)(&names);at<int>(facade,0x50)=2;return;}
 if(systemsMode)clearTextures(p);
 B*next=(B*)fn<void*(*)(U)>(0x39d9c0)((U)count*0xe8);memset(next,0,(U)count*0xe8);
 int selection=0;
 for(int i=0;i<count;i++){
  const char*key=strData(selectedNames[i]);const SystemDef*art=nullptr;
  for(int j=0;j<NSYSTEMS;j++)if(strcmp(key,systems[j].key)==0){art=&systems[j];break;}
  B*item=next+i*0xe8;strAssign(item,key);strAssign(item+0x18,art?art->title:key);strAssign(item+0x60,key);
  if(art)strAssign(item+0xc8,art->path);
  if(lastSystem<systemCount&&strcmp(key,strData(items+lastSystem*0xe8+0x60))==0)selection=i;
  __android_log_print(4,"TurboCarousel","SYSTEM %d; filter=%s; art=%d",i,key,art!=nullptr);
 }
 fn<V>(0x39d820)(selectedNames);fn<V>(0x15f5c4)(&names);
 for(int i=0;i<systemCount;i++)for(int j=0;j<4;j++){
  const U offsets[]={0,0x18,0x60,0xc8};B*value=items+i*0xe8+offsets[j];if(value[0]&1)fn<V>(0x39d820)(at<void*>(value,16));
 }
 if(items)fn<V>(0x39d820)(items);items=next;systemCount=count;lastSystem=selection;
 at<void*>(facade,0x88)=items;at<void*>(facade,0x90)=items+(U)count*0xe8;at<void*>(facade,0x98)=items+(U)count*0xe8;
 at<int>(facade,0xa8)++;at<int>(facade,0x50)=2;
 int n=0,v=count;char digits[10];do{digits[n++]=(char)('0'+v%10);v/=10;}while(v);int k=0;while(n)systemLabel[k++]=digits[--n];
 memcpy(systemLabel+k," PLATAFORMAS",13);
 if(systemsMode){
  invalidate(p);rebuildHook(p);
  int cursor=0;U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
  for(U*it=visible;it&&it<end;it++)if(*it==(U)selection){cursor=(int)(it-visible);break;}
  at<int>(p,0xf0)=cursor;at<float>(p,0xf4)=(float)cursor;refreshHook(p);
 }
 __android_log_print(4,"TurboCarousel","Native original platform list: %d systems",count);
}
static void* getHook(){
 U caller=(U)__builtin_return_address(0)-base;
 // Redirect read-only store views, never CatalogService workers/update/launch or the constructor.
 if(systemsMode&&((caller>=0x215400&&caller<0x2170d0)||
   (caller>=0x21b0c8&&caller<0x21bfa0)||(caller>=0x227b30&&caller<0x227d44)||
   (caller>=0x2280e8&&caller<0x22a154)||(caller>=0x22c0d8&&caller<0x22c5cc)||
   (caller>=0x22e5dc&&caller<0x2302d8))){
  initModel();return facade;
 }
 return fn<void*(*)()>(0x1887dc)();
}
static void clearTextures(void*p){
 fn<void(*)(void*,void*)>(0x23688c)((B*)p+0x208,at<void*>(p,0x210));
 at<void*>(p,0x208)=(B*)p+0x210;at<U>(p,0x210)=0;at<U>(p,0x218)=0;
 fn<void(*)(void*,void*)>(0x2368fc)((B*)p+0x250,at<void*>(p,0x258));
 at<void*>(p,0x250)=(B*)p+0x258;at<U>(p,0x258)=0;at<U>(p,0x260)=0;
}
static void invalidate(void*p){
 at<void*>(p,0x100)=at<void*>(p,0xf8);at<int>(p,0x110)=-1;
 at<void*>(p,0x688)=at<void*>(p,0x680);
 at<int>(p,0xf0)=0;at<float>(p,0xf4)=0;
 at<int>(p,0x220)=-1;at<U>(p,0x228)=~0UL;
 at<B>(p,0x5e4)=0;at<B>(p,0x5f0)=0;at<int>(p,0x578)=-1;at<int>(p,0x584)=0;
}
static void rebuildHook(void*p){
 gui=p;
 if(systemsMode){initModel();at<B>(p,0x148)=0;strAssign((B*)p+0x150,"");}
 // Preserve the native query in platforms as well as in game lists.
 fn<V>(0x21b134)(p);
}
static void refreshHook(void*p){gui=p;fn<V>(0x215400)(p);}
static void showSystems(void*p){
 if(systemsMode)return;
 clearTextures(p);systemsMode=true;
 strAssign((B*)p+0x150,"");strAssign((B*)p+0x650,"");at<B>(p,0x148)=0;
 invalidate(p);rebuildHook(p);
 at<int>(p,0xf0)=lastSystem;at<float>(p,0xf4)=(float)lastSystem;
 refreshHook(p);log("MODE systems; selection restored");
}
static void enterSystem(void*p){
 if(!systemsMode)return;
 int cursor=at<int>(p,0xf0);U*begin=at<U*>(p,0xf8);U*end=at<U*>(p,0x100);
 if(cursor<0||begin+cursor>=end)return;U index=begin[cursor];if(index>=(U)systemCount)return;
 const char*key=strData(items+index*0xe8+0x60);
 stopSystemVideo();lastSystem=(int)index;clearTextures(p);systemsMode=false;
 // Save the full platform index, because the visible list can be filtered by search.
 // A previous system's consecutive cover HTTP errors must not stop the newly selected system.
 at<int>(fn<void*(*)()>(0x1887dc)(),0x11c)=0;
 // Same filter field and rebuildVisible route used by applyFilterChip; no old panel or index guessing.
 strAssign((B*)p+0x150,key);strAssign((B*)p+0x650,"");at<B>(p,0x148)=0;
 invalidate(p);rebuildHook(p);refreshHook(p);
 coverCheckAt=fn<unsigned(*)()>(0x39e240)();coverCheckPending=true;
 __android_log_print(4,"TurboCarousel","MODE games; filter=%s; visible=%lu",key,(at<U>(p,0x100)-at<U>(p,0xf8))/8);
}
static void acceptHook(void*p){if(systemsMode)enterSystem(p);else fn<V>(0x23424c)(p);}
static void cardHook(void*p){if(systemsMode)enterSystem(p);else fn<V>(0x22c5cc)(p);}
static void filterHook(void*p){showSystems(p);}
static void actionHook(void*p,int a){
 if(systemsMode){if(a==0)enterSystem(p);else if(a==4)fn<void(*)(void*,int)>(0x234028)(p,a);return;}
 if(a==4){showSystems(p);return;}
 fn<void(*)(void*,int)>(0x234028)(p,a);
}
static void topHook(void*p,int a){
 if(a==1){showSystems(p);return;}
 if(systemsMode&&a==0)return;
 fn<void(*)(void*,int)>(0x22d6d8)(p,a);
}
static void deleteHook(void*p){if(!systemsMode)fn<V>(0x23447c)(p);}
static void launchHook(void*p,U a){if(!systemsMode){pauseRetroMusicForGame();fn<void(*)(void*,U)>(0x232e00)(p,a);}}
static void prioritizeHook(void*p){if(!systemsMode)fn<V>(0x227d44)(p);}
static void toggleHook(void*p){if(!systemsMode)fn<V>(0x21c340)(p);}
static void searchHook(void*p){
 layoutSearchPresentation(p);fn<V>(0x21c35c)(p);layoutSearchPresentation(p);
 __android_log_print(4,"TurboCarousel","SEARCH opened; context=%s; active=%d; nativeKeyboard=%d",systemsMode?"platforms":"games",at<B>(p,0x648),at<B>(p,0x598));
}
static void textHook(void*p,const void*s){
 const char*text=strData(s);const char*replacement=nullptr;
 if(gui){
  if(starts(text,"PLATAFORMA")||strcmp(text,"SISTEMAS")==0)replacement="PLATAFORMAS";
  if(!systemsMode&&strcmp(text,"SAIR")==0)replacement="VOLTAR";
  if(systemsMode&&(strcmp(text,"BAIXAR")==0||strcmp(text,"JOGAR")==0))replacement="ABRIR";
 }
 if(replacement){alignas(8) B tmp[24]={};tmp[0]=(B)(strlen(replacement)*2);memcpy(tmp+1,replacement,strlen(replacement)+1);fn<void(*)(void*,const void*)>(0x2d2c70)(p,tmp);}
 else fn<void(*)(void*,const void*)>(0x2d2c70)(p,s);
}
// Restrict the existing bottom action vector to its first (Open) button in Systems.
// No replacement control, overlay, or hit-test coordinates are introduced.
struct ButtonScope{
 void*p;U end;bool active;
 ButtonScope(void*g):p(g),end(at<U>(g,0xdf0)),active(systemsMode){if(active&&end>at<U>(g,0xde8))at<U>(g,0xdf0)=at<U>(g,0xde8)+20;}
 ~ButtonScope(){if(active)at<U>(p,0xdf0)=end;}
};
static void nativeText(void*p,const char*t){
 alignas(8) B s[24]={}; U n=strlen(t); if(n>22)return;s[0]=(B)(n*2);memcpy(s+1,t,n+1);
 fn<void(*)(void*,const void*)>(0x2d2c70)(p,s);
}
#include "native_formation.h"
#include "native_skin.h"
#include "native_info.h"
#include "native_laser.h"
#include "native_space3d.h"
#include "native_system_video.h"
#include "native_system_video720.h"
#include "native_retro_music.h"
#include "native_loading_progress.h"
#include "native_settings.h"
#include "native_search_download.h"
#include "native_dolphin.h"
#include "native_flycast.h"
static void* heading;
static void textRenderHook(void*p,void*matrix){
 if(p==settingsBackText||isStoreUiLabel(p))return;
 if(gui&&(p==(B*)gui+0x6c8||p==(B*)gui+0x1dd0||p==(B*)gui+0x1f00))return;
 // Information is painted once below cards, not again by the native child loop.
 if(isSystemInfoText(p))return;
 if(gui&&(U)p>(U)gui+0x700&&(U)p<(U)gui+0x16d0){
  const char*t=strData((B*)p+0xd0);const char*replacement=nullptr;
  if(strcmp(t,"LOJA")==0)heading=p;
  if(systemsMode&&(strcmp(t,"SAVES")==0||strcmp(t,"APAGAR")==0||strcmp(t,"ATUALIZAR")==0||strcmp(t,"SAIR")==0||strcmp(t,"VOLTAR")==0))return;
  // Compact root header: one system name; redundant subtitle and hint are hidden.
  U textOffset=(U)p-(U)gui;
  if(textOffset==0x7f8||textOffset==0xa58||(systemsMode&&(textOffset==0x928||textOffset==0xb88)))return;
  if(systemsMode&&(U)p-(U)gui==0xe00)replacement="ABRIR";
  else if(p==heading)replacement=systemsMode?"PLATAFORMAS":"LOJA";
  else if(starts(t,"PLATAFORMA")||strcmp(t,"SISTEMAS")==0)replacement="PLATAFORMAS";
  else if(systemsMode&&t[0]=='I'&&t[1]=='N'&&t[2]=='S'&&t[3]=='T')replacement=systemLabel;
  else if(!systemsMode&&strcmp(t,"SAIR")==0)replacement="VOLTAR";
  if(replacement&&strcmp(t,replacement)!=0)nativeText(p,replacement);
 }
 settingsSkinText(p);skinText(p);fn<void(*)(void*,void*)>(0x2d2dc4)(p,matrix);
}
static void renderHook(void*p,void*matrix){
 if(!systemsMode||modal(p))stopSystemVideo();
 gui=p;void*local=fn<void*(*)(void*)>(2584496)(p);
 formationMatrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(matrix,local);
 layoutSkin(p);ButtonScope scope(p);fn<void(*)(void*,void*)>(0x22fb88)(p,matrix);
}
static bool modal(void*p){return at<B>(p,0x2050)||at<B>(p,0x1830)||at<B>(p,0x1d98)||at<B>(p,0x648)||at<B>(p,0x5e4);}
static bool mapped(void*cfg,const char*key,const void*input){
 alignas(8) B s[24]={};s[0]=(B)(strlen(key)*2);memcpy(s+1,key,strlen(key)+1);
 alignas(8) B copy[24]={};memcpy(copy,input,20);
 return fn<bool(*)(void*,const void*,const void*)>(0x279d2c)(cfg,s,copy);
}
static bool inputHook(void*p,void*cfg,const void*in){
 gui=p;
 int rawKey=at<int>((void*)in,8);
 if(at<int>((void*)in,12)&&at<B>(p,0x2050)&&(rawKey==27||rawKey==0x4000010e)){
  requestSettingsClose(p);return true;
 }
 if(at<int>((void*)in,12)&&!modal(p)&&at<int>(p,0x370)>=2){
  int id=at<int>((void*)in,8);
  // Native keyboard navigation (Input device -1). Reuses moveCursor/onAccept, same as mapped controller actions.
  if(systemsMode&&at<int>((void*)in,0)==-1){
   if(id==0x4000004f||id==0x40000050){fn<void(*)(void*,int)>(0x2318d0)(p,id==0x4000004f?1:-1);return true;}
   if(id==13||id==32){enterSystem(p);return true;}
  }
  if(mapped(cfg,"b",in)||id==27||id==0x4000010e){
   // Android 16 can deliver both the key and predictive callback for one press.
   unsigned tick=fn<unsigned(*)()>(0x39e240)();
   if(handledBack && (unsigned)(tick-lastBackTick)<250)return true;
   handledBack=true;lastBackTick=tick;
if(!systemsMode){showSystems(p);return true;} else {fn<void(*)(void*,int)>(0x234028)(p,4);return true;}}
 }
 ButtonScope scope(p); bool handled=fn<bool(*)(void*,void*,const void*)>(0x2354d4)(p,cfg,in); if(systemsMode && at<B>(p,0x5e4)){at<B>(p,0x5e4)=0;enterSystem(p);} return handled;
}
static bool touchHook(void*p,const void*event){gui=p;if(formationTouch(p,event))return true; ButtonScope scope(p);return fn<bool(*)(void*,const void*)>(0x234878)(p,event);}
static void updateHook(void*p,int delta){
 gui=p;syncModel(p);
 if(!started){started=true;
 auto setHint=(int(*)(const char*,const char*))dlsym(dlopen("libSDL2.so",2),"SDL_SetHint");
 if(setHint)setHint("SDL_ANDROID_TRAP_BACK_BUTTON","1");invalidate(p);rebuildHook(p);log("Native carousel active; original GuiStore update/render retained");}
 fn<void(*)(void*,int)>(0x231bac)(p,delta);
 if(!systemsMode&&coverCheckPending&&(unsigned)(fn<unsigned(*)()>(0x39e240)()-coverCheckAt)>5000){
  coverCheckPending=false;void*real=fn<void*(*)()>(0x1887dc)();U*visible=at<U*>(p,0xf8);U*end=at<U*>(p,0x100);
  for(int i=0;i<3&&visible+i<end;i++){B*it=at<B*>(real,0x88)+visible[i]*0xe8;
   __android_log_print(4,"TurboCarousel","COVER %s; local=%s; flags=%d/%d/%d; errors=%d; url=%s",strData(it+0x18),strData(it+0xc8),it[0xe0],it[0xe1],it[0xe2],at<int>(real,0x11c),strData(it+0x48));}
 }
}
struct Hook{U original;void*replacement;};
static Hook hooks[]={
 {0x2a9718,(void*)flycastRunHook},{0x2a89a8,(void*)flycastFreshHook},
 {0x2a87d8,(void*)flycastBundledHook},{0x18b098,(void*)flycastInstalledHook},
 {0x18aaf0,(void*)flycastAssetsHook},{0x18a8a8,(void*)flycastPackHook},
 {0x2a6850,(void*)flycastDefinitionsHook},{0x2228f8,(void*)flycastSettingsHook},
 {0x219034,(void*)layoutSearchPresentationHook},{0x22f270,(void*)drawSearchPresentationHook},
 {0x219c4c,(void*)drawKeyboardPresentationHook},{0x22cef4,(void*)layoutMessagePresentationHook},
 {0x22d090,(void*)drawMessagePresentationHook},{0x2302d8,(void*)drawToastPresentationHook},
 {0x228e7c,(void*)drawDownloadPresentationHook},
 {0x373c54,(void*)loadingShowHook},{0x373ddc,(void*)loadingHideHook},
 {0x2bd298,(void*)loadingCoreHook},{0x2bdcb0,(void*)loadingGameHook},
 {0x2e9304,(void*)pauseTextCacheHook},
 {0x2170d0,(void*)retroMusicHook},
 {0x21dd24,(void*)settingsClosedHook},{0x226e5c,(void*)drawSettingsSkinHook},{0x2269fc,(void*)touchSettingsSkinHook},
 {0x2a39cc,(void*)auroraSkinHook},
 {0x22a154,(void*)flowFormationHook},{0x22833c,(void*)coverFormationHook},{0x2e5470,(void*)stripsFormationHook},
 {0x2e2800,(void*)clipFormationHook},{0x2278c0,(void*)coverAtFormationHook},
 {0x2e2c38,(void*)rectHook},{0x2280e8,(void*)infoSkinHook},{0x22ea88,(void*)topSkinHook},{0x22e5dc,(void*)buttonsSkinHook},
 {0x2d2dc4,(void*)textRenderHook},{0x1887dc,(void*)getHook},{0x21b134,(void*)rebuildHook},{0x215400,(void*)refreshHook},
 {0x23424c,(void*)acceptHook},{0x22c5cc,(void*)cardHook},{0x21c900,(void*)filterHook},
 {0x234028,(void*)actionHook},{0x22d6d8,(void*)topHook},{0x23447c,(void*)deleteHook},
 {0x232e00,(void*)launchHook},{0x227d44,(void*)prioritizeHook},{0x21c340,(void*)toggleHook},
 {0x21c35c,(void*)searchHook},{0x2d2c70,(void*)textHook},{0x22fb88,(void*)renderHook},
 {0x2354d4,(void*)inputHook},{0x234878,(void*)touchHook},{0x231bac,(void*)updateHook}
};
__attribute__((constructor)) static void install(){
 void*lib=dlopen("libmain.so",2);void*sym=dlsym(lib,"_ZN14CatalogService3getEv");DlInfo info={};
 if(!sym||!dladdr(sym,&info)){log("ERROR libmain unavailable");return;}base=(U)info.base;
 if((U)sym-base!=0x1887dc||at<unsigned>((void*)base,0x234028)!=0xd10583ff){log("ERROR unsupported baseline ABI; untouched");return;}
 // Patch only loader relocations (GOT and vtable). Never copy machine instructions or use a guessed trampoline.
 U page=(U)sysconf(39);if(page!=4096&&page!=16384)page=4096;int count=0;
 for(const auto&r:relocations)for(const auto&h:hooks)if(r[1]==h.original){
  void**slot=(void**)(base+r[0]);if((U)*slot!=base+h.original)continue;
  U pg=(U)slot&~(page-1);if(mprotect((void*)pg,page,3)){log("ERROR writable relocation failed");continue;}
  *slot=h.replacement;mprotect((void*)pg,page,1);count++;
 }
 __android_log_print(4,"TurboCarousel","Native module loaded; %d verified relocation hooks",count);
}


