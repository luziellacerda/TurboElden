// GPL-2.0-or-later. Native navigation bridge for official Flycast e36e9df2d.
// Replaces the Android library header only. No Android overlay or emulation hook.
#define _GNU_SOURCE
#include <jni.h>
#include <dlfcn.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdbool.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <time.h>
#include <android/log.h>
static void *engine;
static uintptr_t engine_base;
static int *gui_state;
static int navigation_ready;
static void (*text_v)(const char*,va_list);
typedef struct {float x,y;} Vec2;
static bool (*button)(const char*,const Vec2*,int);
static bool return_pending;
static void (*push_color)(int,unsigned);
static void (*pop_color)(int);
static void (*exit_engine)(void);
static bool (*begin_child)(unsigned,const Vec2*,int,int);
static void* (*get_draw_list)(void);
static void* (*get_font)(void);
static Vec2 (*get_window_pos)(void);
static Vec2 (*get_window_size)(void);
static Vec2 (*measure_text)(void*,float,float,float,const char*,const char*,const char**);
static void (*draw_gradient)(void*,const Vec2*,const Vec2*,unsigned,unsigned,unsigned,unsigned);
static void (*draw_line)(void*,const Vec2*,const Vec2*,unsigned,float);
static void (*draw_text)(void*,void*,float,const Vec2*,unsigned,const char*,const char*,float,const void*);
static void (*draw_circle)(void*,const Vec2*,float,unsigned,int,float);
static unsigned rgba(unsigned r,unsigned g,unsigned b,unsigned a){return r|(g<<8)|(b<<16)|(a<<24);}
static void turborama_background(void){
    // Main library child only: rendered behind items, never in emulation/settings.
    // Static native primitives, without videos, timers or new textures.
    void *dl=get_draw_list(),*font=get_font();
    Vec2 p=get_window_pos(),sz=get_window_size();
    if(!dl||!font||sz.x<100||sz.y<100)return;
    Vec2 end={p.x+sz.x,p.y+sz.y};
    draw_gradient(dl,&p,&end,rgba(3,10,6,255),rgba(7,29,16,255),rgba(2,7,4,255),rgba(3,9,6,255));
    float scale=sz.y/800.f;
    if(scale<0.65f)scale=0.65f;
    Vec2 center={p.x+sz.x*.71f,p.y+sz.y*.64f};
    float radius=(sz.x<sz.y?sz.x:sz.y)*.37f;
    draw_circle(dl,&center,radius,rgba(67,205,83,15),80,1.5f*scale);
    draw_circle(dl,&center,radius+16.f*scale,rgba(67,205,83,9),80,1.f*scale);
    for(int k=0;k<12;k++){
        Vec2 a={p.x+sz.x*(.34f+.075f*k),p.y+sz.y};
        Vec2 b={a.x+sz.x*.20f,p.y};
        draw_line(dl,&a,&b,rgba(65,182,70,k%3==0?15:7),1.f*scale);
    }
    // Fitted wordmark scales down for portrait/narrow displays.
    float text_size=sz.y*.105f;
    Vec2 extent=measure_text(font,text_size,3.4e38f,0,"TURBORAMA",0,0);
    float width=sz.x*.54f;
    if(extent.x>width){text_size*=width/extent.x;extent=measure_text(font,text_size,3.4e38f,0,"TURBORAMA",0,0);}
    Vec2 title={p.x+sz.x*.69f-extent.x*.5f,p.y+sz.y*.63f};
    draw_text(dl,font,text_size,&title,rgba(80,171,95,210),"TURBORAMA",0,0,0);
    Vec2 line1={title.x,title.y-20.f*scale},line2={title.x+extent.x*.69f,line1.y};
    draw_line(dl,&line1,&line2,rgba(96,242,71,120),2.f*scale);
    line1.x=title.x+extent.x*.91f;line2.x=title.x+extent.x;
    draw_line(dl,&line1,&line2,rgba(212,40,48,200),3.f*scale);
    const char *caption="DREAMCAST  /  NAOMI  /  ATOMISWAVE";
    float caption_size=text_size*.235f;
    Vec2 cap_size=measure_text(font,caption_size,3.4e38f,0,caption,0,0);
    Vec2 cap={title.x+(extent.x-cap_size.x)*.5f,title.y+extent.y+16.f*scale};
    draw_text(dl,font,caption_size,&cap,rgba(122,157,133,210),caption,0,0,0);
    Vec2 bottom_a={p.x+sz.x*.035f,p.y+sz.y*.96f};
    Vec2 bottom_b={p.x+sz.x*.965f,bottom_a.y};
    draw_line(dl,&bottom_a,&bottom_b,rgba(66,142,78,48),1.f*scale);
}
__attribute__((noinline)) static bool library_child(unsigned id,const Vec2 *size,int child_flags,int flags){
    uintptr_t caller=(uintptr_t)__builtin_return_address(0);
    bool visible=begin_child(id,size,child_flags,flags);
    if(visible && caller==engine_base+0xafb0d4 && gui_state && *gui_state==4)
        turborama_background();
    return visible;
}

#define INFO(s) __android_log_print(ANDROID_LOG_INFO,"TurboFlycast","%s",s)
// Preserve real Android touch transitions until the renderer consumes them.
// Upstream stores only a current button bitfield; a fast down/up can disappear
// between frames. This queue feeds the original ImGui event API on its own thread.
// Only the main library is affected; gameplay input is always forwarded unchanged.
typedef struct {float x,y; int down; long long time_ns;} MenuTouch;
static int (*read_clock)(clockid_t,struct timespec*);
static long long touch_time(void){struct timespec t;if(!read_clock||read_clock(CLOCK_MONOTONIC,&t)!=0)return 0;return (long long)t.tv_sec*1000000000LL+t.tv_nsec;}
static MenuTouch touch_queue[256];
static unsigned touch_count;
static unsigned char touch_lock;
static void (*original_touch)(JNIEnv*,jobject,jint,jint,jint);
static void (*add_mouse_button)(void*,int,bool);
static void (*add_mouse_pos)(void*,float,float);
static void (*add_mouse_source)(void*,int);
static void lock_touch(void){while(__atomic_test_and_set(&touch_lock,__ATOMIC_ACQUIRE)){}}
static void unlock_touch(void){__atomic_clear(&touch_lock,__ATOMIC_RELEASE);}
static void clear_touch(void){lock_touch();touch_count=0;unlock_touch();}
static void android_menu_touch(JNIEnv *env,jobject receiver,jint x,jint y,jint buttons){
    original_touch(env,receiver,x,y,buttons);
    if(!gui_state||*gui_state!=4){clear_touch();return;}
    // Read the coordinates already transformed by upstream pointScale/rounding.
    MenuTouch e={(float)*(int*)(engine_base+0x3896798),
                 (float)*(int*)(engine_base+0x389679c),(buttons&1)!=0,touch_time()};
    lock_touch();
    if(touch_count && touch_queue[touch_count-1].down==e.down)
        touch_queue[touch_count-1]=e; // merge motion, never a press/release pair
    else if(touch_count<256)touch_queue[touch_count++]=e;
    else {touch_count=1;touch_queue[0]=e;}
    unlock_touch();
}
__attribute__((noinline)) static void menu_mouse_button(void *io,int index,bool down){
    uintptr_t caller=(uintptr_t)__builtin_return_address(0);
    if(index!=0||caller!=engine_base+0xafaadc){add_mouse_button(io,index,down);return;}
    if(!gui_state||*gui_state!=4){clear_touch();add_mouse_button(io,index,down);return;}
    MenuTouch events[256];unsigned count;
    lock_touch();count=touch_count;
    for(unsigned i=0;i<count;i++)events[i]=touch_queue[i];
    touch_count=0;unlock_touch();
    if(!count){add_mouse_button(io,index,down);return;}
    if(touch_time()-events[count-1].time_ns>2000000000LL){add_mouse_button(io,index,down);return;}
    add_mouse_source(io,1); // ImGuiMouseSource_TouchScreen
    for(unsigned i=0;i<count;i++){
        add_mouse_pos(io,events[i].x,events[i].y);
        add_mouse_button(io,0,events[i].down);
    }
    // No synthetic activation or coordinates. ImGui handles focus/hit testing.
}

static int load_engine(void){
    if(!engine)engine=dlopen("libflycast.so",RTLD_NOW);
    return engine!=0;
}
__attribute__((noinline)) static void menu_text(const char *fmt,...){
    uintptr_t caller=(uintptr_t)__builtin_return_address(0);
    if(caller==engine_base+0xafad84 && gui_state && *gui_state==4){
        // The upstream library view already reserves frame padding in this row.
        // Packed colors are ImGui's ABGR. Native touch/controller focus is retained.
        Vec2 size={0,0};
        push_color(0,0xffefffef);   // text
        push_color(21,0xff267f17); // green
        push_color(22,0xff32a322);
        push_color(23,0xff205912);
        bool pressed=button(return_pending?"VOLTANDO...":"VOLTAR AO MENU",&size,1<<4);
        pop_color(4);
        if(pressed&&!return_pending){return_pending=true;INFO("Native return button pressed on first down");exit_engine();}
        return;
    }
    va_list args;va_start(args,fmt);text_v(fmt,args);va_end(args);
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_FlycastBootstrap_installNavigation(JNIEnv *env,jclass type){
    return_pending=false;clear_touch();
    if(navigation_ready)return JNI_TRUE;
    if(!load_engine())return JNI_FALSE;
    void *set_state=dlsym(engine,"_Z12gui_setState8GuiState");
    Dl_info info;
    if(!set_state||!dladdr(set_state,&info))return JNI_FALSE;
    uintptr_t base=(uintptr_t)info.dli_fbase;
    // Pin to the verified official binary before touching the single PLT slot.
    if((uintptr_t)set_state!=base+0xaf7604 ||
       *(uint32_t*)(base+0xafad80)!=0x9416b880 ||
       *(uint32_t*)(base+0xafad84)!=0x1e249000 ||
       strcmp((char*)base+0x3c6db3,"GAMES")!=0)return JNI_FALSE;
    if(*(uint32_t*)(base+0xafb0d0)!=0x9416b34c ||
       *(uint32_t*)(base+0xafb0d4)!=0x9416b487)return JNI_FALSE;
    void **child_slot=(void**)(base+0x1190558);
    begin_child=(bool(*)(unsigned,const Vec2*,int,int))dlsym(engine,"_ZN5ImGui10BeginChildEjRK6ImVec2ii");
    if((void*)begin_child!=*child_slot || (uintptr_t)begin_child!=base+0x8e043c)return JNI_FALSE;
    void **slot=(void**)(base+0x1190e18);
    void *original=dlsym(engine,"_ZN5ImGui4TextEPKcz");
    if(*slot!=original || (uintptr_t)original!=base+0x90e2ac)return JNI_FALSE;
    gui_state=(int*)dlsym(engine,"gui_state");
    text_v=(void(*)(const char*,va_list))dlsym(engine,"_ZN5ImGui5TextVEPKcSt9__va_list");
    button=(bool(*)(const char*,const Vec2*,int))dlsym(engine,"_ZN5ImGui8ButtonExEPKcRK6ImVec2i");
    push_color=(void(*)(int,unsigned))dlsym(engine,"_ZN5ImGui14PushStyleColorEij");
    pop_color=(void(*)(int))dlsym(engine,"_ZN5ImGui13PopStyleColorEi");
    exit_engine=(void(*)(void))dlsym(engine,"_Z7dc_exitv");
    if(!gui_state||!text_v||!button||!push_color||!pop_color||!exit_engine)return JNI_FALSE;

    get_draw_list=(void*(*)(void))dlsym(engine,"_ZN5ImGui17GetWindowDrawListEv");
    get_font=(void*(*)(void))dlsym(engine,"_ZN5ImGui7GetFontEv");
    get_window_pos=(Vec2(*)(void))dlsym(engine,"_ZN5ImGui12GetWindowPosEv");
    get_window_size=(Vec2(*)(void))dlsym(engine,"_ZN5ImGui13GetWindowSizeEv");
    measure_text=(Vec2(*)(void*,float,float,float,const char*,const char*,const char**))dlsym(engine,"_ZN6ImFont13CalcTextSizeAEfffPKcS1_PS1_");
    draw_gradient=(void(*)(void*,const Vec2*,const Vec2*,unsigned,unsigned,unsigned,unsigned))dlsym(engine,"_ZN10ImDrawList23AddRectFilledMultiColorERK6ImVec2S2_jjjj");
    draw_line=(void(*)(void*,const Vec2*,const Vec2*,unsigned,float))dlsym(engine,"_ZN10ImDrawList7AddLineERK6ImVec2S2_jf");
    draw_text=(void(*)(void*,void*,float,const Vec2*,unsigned,const char*,const char*,float,const void*))dlsym(engine,"_ZN10ImDrawList7AddTextEP6ImFontfRK6ImVec2jPKcS6_fPK6ImVec4");
    draw_circle=(void(*)(void*,const Vec2*,float,unsigned,int,float))dlsym(engine,"_ZN10ImDrawList9AddCircleERK6ImVec2fjif");
    if(!get_draw_list||!get_font||!get_window_pos||!get_window_size||!measure_text||!draw_gradient||!draw_line||!draw_text||!draw_circle)return JNI_FALSE;
    // Verified gui_newFrame left-button sampling call and coordinate stores.
    if(*(uint32_t*)(base+0xafaad8)!=0x9416b026 ||
       *(uint32_t*)(base+0xafaadc)!=0xb947a688 ||
       *(uint32_t*)(base+0xaf7354)!=0xb9079948 ||
       *(uint32_t*)(base+0xaf7360)!=0xb9079d09)return JNI_FALSE;
    read_clock=(int(*)(clockid_t,struct timespec*))dlsym(RTLD_DEFAULT,"clock_gettime");
    original_touch=(void(*)(JNIEnv*,jobject,jint,jint,jint))dlsym(engine,"Java_com_flycast_emulator_periph_InputDeviceManager_touchMouseEvent");
    add_mouse_button=(void(*)(void*,int,bool))dlsym(engine,"_ZN7ImGuiIO19AddMouseButtonEventEib");
    add_mouse_pos=(void(*)(void*,float,float))dlsym(engine,"_ZN7ImGuiIO16AddMousePosEventEff");
    add_mouse_source=(void(*)(void*,int))dlsym(engine,"_ZN7ImGuiIO19AddMouseSourceEventE16ImGuiMouseSource");
    void **input_slot=(void**)(base+0x118fc10);
    if(!read_clock||!original_touch||!add_mouse_button||!add_mouse_pos||!add_mouse_source||
       *input_slot!=(void*)add_mouse_button)return JNI_FALSE;
    jclass input_class=(*env)->FindClass(env,"com/flycast/emulator/periph/InputDeviceManager");
    if(!input_class){(*env)->ExceptionClear(env);return JNI_FALSE;}
    long page_size=sysconf(_SC_PAGESIZE);
    if(page_size<=0)return JNI_FALSE;
    uintptr_t page=(uintptr_t)slot & ~((uintptr_t)page_size-1);
    if(((uintptr_t)child_slot & ~((uintptr_t)page_size-1))!=page)return JNI_FALSE;
    uintptr_t input_page=(uintptr_t)input_slot & ~((uintptr_t)page_size-1);
    // Slots are in verified RELRO pages; never make executable code writable.
    if(mprotect((void*)page,(size_t)page_size,PROT_READ|PROT_WRITE)!=0){(*env)->DeleteLocalRef(env,input_class);return JNI_FALSE;}
    if(mprotect((void*)input_page,(size_t)page_size,PROT_READ|PROT_WRITE)!=0){
        mprotect((void*)page,(size_t)page_size,PROT_READ);(*env)->DeleteLocalRef(env,input_class);return JNI_FALSE;
    }
    engine_base=base;
    JNINativeMethod method={"touchMouseEvent","(III)V",(void*)&android_menu_touch};
    int registered=(*env)->RegisterNatives(env,input_class,&method,1);
    (*env)->DeleteLocalRef(env,input_class);
    if(registered!=0){
        (*env)->ExceptionClear(env);
        mprotect((void*)page,(size_t)page_size,PROT_READ);
        mprotect((void*)input_page,(size_t)page_size,PROT_READ);
        return JNI_FALSE;
    }
    __atomic_store_n(slot,(void*)&menu_text,__ATOMIC_RELEASE);
    __atomic_store_n(child_slot,(void*)&library_child,__ATOMIC_RELEASE);
    __atomic_store_n(input_slot,(void*)&menu_mouse_button,__ATOMIC_RELEASE);
    if(mprotect((void*)page,(size_t)page_size,PROT_READ)!=0 ||
       mprotect((void*)input_page,(size_t)page_size,PROT_READ)!=0)
        __android_log_print(ANDROID_LOG_ERROR,"TurboFlycast","Could not restore navigation RELRO protection");
    navigation_ready=1;
    INFO("Native return, Turborama background and lossless menu touch installed");
    return JNI_TRUE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_FlycastBootstrap_openNativeSettings(JNIEnv *env,jclass type){
    if(!load_engine())return JNI_FALSE;
    void (*set_state)(int)=(void(*)(int))dlsym(engine,"_Z12gui_setState8GuiState");
    int *state=(int*)dlsym(engine,"gui_state");
    if(!set_state||!state||*state!=4)return JNI_FALSE;
    // GuiState::Settings=3. Called before rendering begins; no concurrent writer.
    set_state(3);return JNI_TRUE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_FlycastBootstrap_isNativeBrowser(JNIEnv *env,jclass type){
    typedef jboolean (*is_browser)(JNIEnv*,jobject);
    is_browser fn=engine?(is_browser)dlsym(engine,"Java_com_flycast_emulator_emu_JNIdc_guiIsContentBrowser"):0;
    return fn?fn(env,type):JNI_FALSE;
}
