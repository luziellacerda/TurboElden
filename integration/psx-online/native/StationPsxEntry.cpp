// SPDX-License-Identifier: GPL-2.0-or-later
// Opt-in shim: executes the bundled normal LibretroPlayer owner, never RetroArch.
#include "StationPsxOwner.hpp"
#include "PsxPinnedOptions.h"
#include <jni.h>
#include <dlfcn.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <condition_variable>
#include <cstring>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using station::psx::Session;
using station::psx::Result;
using station::psx::Digest;
namespace owner=station::psx::owner;
constexpr char OwnerSha[]="62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6";
constexpr char CoreSha[]="e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9";
constexpr char RunSymbol[]="_ZN14LibretroPlayer3runERKNSt6__ndk112basic_stringIcNS0_11char_traitsIcEENS0_9allocatorIcEEEES8_";
constexpr char HomeSymbol[]="_ZN5Utils10FileSystem11setHomePathERKNSt6__ndk112basic_stringIcNS1_11char_traitsIcEENS1_9allocatorIcEEEE";
JavaVM* vm{};
jclass callbacks{};
jmethodID ownerThreadStarted{},rendererReady{},coreReady{},returned{},preparationFailed{},localPause{};
std::mutex mutex;
std::condition_variable wake;
struct Config {std::string core,rom,home;Digest binding{};std::uint8_t slot{};};
Config config;
bool prepared{},claimed{},ownerReturned{};
std::atomic<bool> human{false};
std::string failure;
std::unique_ptr<Session> protocol; // same process lifetime; never freed by an IO caller
std::atomic<Session*> live{nullptr};
std::uint64_t requestedEpoch{1},requestedSerial{};
bool requestedPause{true},requestedVisible{true};

struct Env {
    JNIEnv* env{};bool attached{};
    Env(){if(vm){auto r=vm->GetEnv(reinterpret_cast<void**>(&env),JNI_VERSION_1_6);
        if(r==JNI_EDETACHED&&vm->AttachCurrentThread(&env,nullptr)==JNI_OK)attached=true;}}
    ~Env(){if(attached)vm->DetachCurrentThread();}
};
std::string text(JNIEnv* env,jstring value){
    if(!value)return {};auto s=env->GetStringUTFChars(value,nullptr);if(!s)return {};
    std::string copy(s);env->ReleaseStringUTFChars(value,s);return copy;
}
std::string category(std::string s){
    if(s.empty())return "PREPARATION_FAILED";
    for(auto c:s)if(!((c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_'))return "PREPARATION_FAILED";
    if(s.size()>64)return "PREPARATION_FAILED";return s;
}
void call(jmethodID method){Env e;if(e.env&&callbacks&&method){e.env->CallStaticVoidMethod(callbacks,method);if(e.env->ExceptionCheck())e.env->ExceptionClear();}}
void call(jmethodID method,const std::string& value){Env e;if(!e.env||!callbacks||!method)return;
    auto s=e.env->NewStringUTF(value.c_str());if(s){e.env->CallStaticVoidMethod(callbacks,method,s);e.env->DeleteLocalRef(s);}if(e.env->ExceptionCheck())e.env->ExceptionClear();}
void failed(const char* why){
    auto s=category(why?why:"");
    {std::lock_guard lock(mutex);if(failure.empty())failure=s;}
    if(auto* p=live.load(std::memory_order_acquire))p->automaticStop(s.c_str());
    wake.notify_all();call(preparationFailed,s);
}
std::string canonical(const std::string& path){
    if(path.empty()||path[0]!='/'||path.size()>4096||path.find('\0')!=std::string::npos)return {};
    char out[4096];return realpath(path.c_str(),out)?std::string(out):std::string();
}
bool regular(const std::string& path){struct stat s{};return stat(path.c_str(),&s)==0&&S_ISREG(s.st_mode);}
bool directory(const std::string& path){struct stat s{};return stat(path.c_str(),&s)==0&&S_ISDIR(s.st_mode);}
std::vector<std::uint8_t> readElf(const std::string& path){
    int fd=open(path.c_str(),O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)throw std::runtime_error("ELF_OPEN");
    struct Guard{int fd;~Guard(){close(fd);}}guard{fd};
    struct stat st{};if(fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_size<64||st.st_size>16*1024*1024)throw std::runtime_error("ELF_SIZE");
    std::vector<std::uint8_t> b(std::size_t(st.st_size));std::size_t pos=0;
    while(pos<b.size()){auto n=read(fd,b.data()+pos,b.size()-pos);if(n<=0)throw std::runtime_error("ELF_READ");pos+=std::size_t(n);}return b;
}
std::string hex(Digest d){constexpr char h[]="0123456789abcdef";std::string s;for(auto b:d){s+=h[b>>4];s+=h[b&15];}return s;}
Digest verifiedElf(const std::vector<std::uint8_t>& b,const char* expected){
    auto d=station::psx::sha256(b);if(hex(d)!=expected||b[0]!=0x7f||b[1]!='E'||b[2]!='L'||b[3]!='F'||b[4]!=2||b[5]!=1||b[18]!=0xb7||b[19]!=0)throw std::runtime_error("ELF_IDENTITY");return d;
}
template<class T>T symbol(void* library,const char* name){auto p=dlsym(library,name);if(!p)throw std::runtime_error("OWNER_ABI");return reinterpret_cast<T>(p);}
void waitForHuman(){std::unique_lock lock(mutex);wake.wait(lock,[]{return human.load(std::memory_order_acquire);});}
Session* makeSession(std::size_t bytes,const Digest&,const Digest&,void*){
    Session* result{};
    {
      std::lock_guard lock(mutex);
      if(protocol||!prepared||bytes>station::psx::MaxState||bytes==0)return nullptr;
      protocol=std::make_unique<Session>(station::psx::Config{config.slot,requestedEpoch,bytes,config.binding,station_psx::input_delay_frames});
      result=protocol.get();
      if(requestedSerial)result->control(requestedEpoch,requestedSerial,requestedPause,requestedVisible);
      if(!failure.empty())result->automaticStop(failure.c_str());
      live.store(result,std::memory_order_release);
    }
    // Core was genuinely loaded; the status ACK still requires the owner checkpoint.
    // Java queues this notice and must never report READY based on this alone.
    Env e;if(e.env&&callbacks&&coreReady){e.env->CallStaticVoidMethod(callbacks,coreReady,jint(bytes));if(e.env->ExceptionCheck())e.env->ExceptionClear();}
    return result;
}
void onLocalPause(bool paused,void*){Env e;if(e.env&&callbacks&&localPause){e.env->CallStaticVoidMethod(callbacks,localPause,jboolean(paused));if(e.env->ExceptionCheck())e.env->ExceptionClear();}}
void onOwnerFailure(const char* why,void*){failed(why);}
}

extern "C" JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* source,void*){
    vm=source;JNIEnv* env{};if(vm->GetEnv(reinterpret_cast<void**>(&env),JNI_VERSION_1_6)!=JNI_OK)return JNI_ERR;
    auto c=env->FindClass("org/emulationstation/frontend/netplay/StationPsxSession");if(!c)return JNI_ERR;
    callbacks=static_cast<jclass>(env->NewGlobalRef(c));env->DeleteLocalRef(c);
    ownerThreadStarted=env->GetStaticMethodID(callbacks,"onOwnerThreadStarted","()V");
    rendererReady=env->GetStaticMethodID(callbacks,"onRendererReady","()V");
    coreReady=env->GetStaticMethodID(callbacks,"onCoreReady","(I)V");
    returned=env->GetStaticMethodID(callbacks,"onOwnerReturned","(Ljava/lang/String;)V");
    preparationFailed=env->GetStaticMethodID(callbacks,"onPreparationFailed","(Ljava/lang/String;)V");
    localPause=env->GetStaticMethodID(callbacks,"onLocalPause","(Z)V");
    return ownerThreadStarted&&rendererReady&&coreReady&&returned&&preparationFailed&&localPause&&!env->ExceptionCheck()?JNI_VERSION_1_6:JNI_ERR;
}
#define JNI(name) Java_org_emulationstation_frontend_netplay_StationPsxBridge_##name
extern "C" JNIEXPORT jboolean JNICALL JNI(nativePrepare)(JNIEnv* env,jclass,jstring core,jstring rom,jstring home,jbyteArray binding,jint slot,jint mask){
    try{
      Config c;c.core=canonical(text(env,core));c.rom=canonical(text(env,rom));c.home=canonical(text(env,home));
      if(env->ExceptionCheck()||!binding||env->GetArrayLength(binding)!=32||(slot!=1&&slot!=2)||mask!=3||
         !regular(c.core)||!regular(c.rom)||!directory(c.home))return JNI_FALSE;
      env->GetByteArrayRegion(binding,0,32,reinterpret_cast<jbyte*>(c.binding.data()));
      if(env->ExceptionCheck()||std::all_of(c.binding.begin(),c.binding.end(),[](auto b){return b==0;}))return JNI_FALSE;
      c.slot=std::uint8_t(slot);
      std::lock_guard lock(mutex);if(prepared||human.load()||!failure.empty())return JNI_FALSE;
      config=std::move(c);prepared=true;wake.notify_all();return JNI_TRUE;
    }catch(...){failed("PREPARE_EXCEPTION");return JNI_FALSE;}
}
extern "C" JNIEXPORT void JNICALL JNI(nativePreparationFailed)(JNIEnv* env,jclass,jstring why){failed(category(text(env,why)).c_str());}
extern "C" JNIEXPORT void JNICALL JNI(nativeAuthorizeHumanExit)(JNIEnv*,jclass){
    human.store(true,std::memory_order_release);owner::authorizeHumanExit();wake.notify_all();
}
extern "C" JNIEXPORT jboolean JNICALL JNI(nativeHumanExitAuthorized)(JNIEnv*,jclass){return human.load(std::memory_order_acquire);}
extern "C" JNIEXPORT jint JNICALL JNI(nativeControl)(JNIEnv*,jclass,jlong epoch,jlong serial,jboolean pause,jboolean visible){
    if(epoch<=0||serial<=0)return jint(Result::Invalid);
    std::lock_guard lock(mutex);
    if(std::uint64_t(epoch)<requestedEpoch||std::uint64_t(serial)<requestedSerial)return jint(Result::Stale);
    if(std::uint64_t(serial)==requestedSerial)return jint(std::uint64_t(epoch)==requestedEpoch&&bool(pause)==requestedPause&&bool(visible)==requestedVisible?Result::Duplicate:Result::Invalid);
    requestedEpoch=std::uint64_t(epoch);requestedSerial=std::uint64_t(serial);requestedPause=pause;requestedVisible=visible;
    if(auto* p=live.load(std::memory_order_acquire))return jint(p->control(requestedEpoch,requestedSerial,requestedPause,requestedVisible));
    return jint(Result::Wait);
}
extern "C" JNIEXPORT jint JNICALL JNI(nativeResume)(JNIEnv*,jclass,jlong epoch,jlong serial){
    if(epoch<=0||serial<=0)return jint(Result::Invalid);
    if(owner::localPaused()||owner::failed())return jint(Result::Paused);
    auto* p=live.load(std::memory_order_acquire);return p?jint(p->resume(std::uint64_t(epoch),std::uint64_t(serial))):jint(Result::Wait);
}
extern "C" JNIEXPORT jint JNICALL JNI(nativeDeliver)(JNIEnv* env,jclass,jint remote,jlong id,jbyteArray packet){
    if(!packet||id<=0||(remote!=1&&remote!=2))return jint(Result::Invalid);
    auto n=env->GetArrayLength(packet);if(n<36||n>jint(station::psx::MaxPacket))return jint(Result::Invalid);
    auto* p=live.load(std::memory_order_acquire);if(!p)return jint(Result::Wait);
    std::array<std::uint8_t,station::psx::MaxPacket> data{};env->GetByteArrayRegion(packet,0,n,reinterpret_cast<jbyte*>(data.data()));
    if(env->ExceptionCheck())return jint(Result::Invalid);
    return jint(p->deliver(std::uint8_t(remote),std::uint64_t(id),std::span(data.data(),std::size_t(n))));
}
extern "C" JNIEXPORT jboolean JNICALL JNI(nativeCopied)(JNIEnv*,jclass,jlong id){auto* p=live.load(std::memory_order_acquire);return id>0&&p&&p->copied(std::uint64_t(id));}
extern "C" JNIEXPORT jint JNICALL JNI(nativeReleaseReceipt)(JNIEnv*,jclass,jlong id){auto* p=live.load(std::memory_order_acquire);return id<=0?jint(Result::Invalid):(p?jint(p->releaseReceipt(std::uint64_t(id))):jint(Result::Wait));}
extern "C" JNIEXPORT jbyteArray JNICALL JNI(nativeTakeOutgoing)(JNIEnv* env,jclass){auto* p=live.load(std::memory_order_acquire);if(!p)return nullptr;auto b=p->takeOutgoing();if(b.empty())return nullptr;
    auto out=env->NewByteArray(jsize(b.size()));if(out)env->SetByteArrayRegion(out,0,jsize(b.size()),reinterpret_cast<const jbyte*>(b.data()));return out;}
extern "C" JNIEXPORT void JNICALL JNI(nativeAwaitOutgoing)(JNIEnv*,jclass,jint timeoutMs){
    if(timeoutMs<1||timeoutMs>100)return;
    if(auto* p=live.load(std::memory_order_acquire))p->awaitOutgoing(std::uint32_t(timeoutMs));
}
extern "C" JNIEXPORT jlongArray JNICALL JNI(nativeTakeCommit)(JNIEnv* env,jclass){auto* p=live.load(std::memory_order_acquire);station::psx::Commit c{};if(!p||!p->takeCommit(c))return nullptr;
    const jlong row[]{jlong(c.kind),jlong(c.outcome),jlong(c.stamp.epoch),jlong(c.stamp.stateSerial),jlong(c.stamp.frame)};
    auto out=env->NewLongArray(5);if(out)env->SetLongArrayRegion(out,0,5,row);return out;}
extern "C" JNIEXPORT jint JNICALL JNI(nativeRequestState)(JNIEnv*,jclass){auto* p=live.load(std::memory_order_acquire);return p?jint(p->requestState()):jint(Result::Wait);}
extern "C" JNIEXPORT void JNICALL JNI(nativeFail)(JNIEnv* env,jclass,jstring why){failed(category(text(env,why)).c_str());}
extern "C" JNIEXPORT jstring JNICALL JNI(nativeFailure)(JNIEnv* env,jclass){auto* p=live.load(std::memory_order_acquire);std::string s;
    if(p)s=p->failure();if(s.empty()){std::lock_guard lock(mutex);s=failure;}return env->NewStringUTF(s.c_str());}
extern "C" JNIEXPORT jlongArray JNICALL JNI(nativeStatus)(JNIEnv* env,jclass){
    jlong row[20]{};row[0]=owner::coreReady();row[1]=owner::failed();row[2]=owner::localPaused();row[3]=human.load(std::memory_order_acquire);
    {std::lock_guard lock(mutex);row[1]|=!failure.empty();}
    auto* p=live.load(std::memory_order_acquire);if(p){auto s=p->status();row[1]|=s.failed;
      row[4]=jlong(s.epoch);row[5]=jlong(s.controlSerial);row[6]=jlong(s.nextFrame);row[7]=jlong(s.stateSerial);
      row[8]=s.paused;row[9]=s.stateReady;row[10]=s.inFrame;row[11]=s.applyingState;row[12]=s.closed;
      row[13]=s.pause.valid;row[14]=jlong(s.pause.epoch);row[15]=jlong(s.pause.controlSerial);row[16]=jlong(s.pause.nextFrame);row[17]=jlong(s.pause.stateSerial);
      row[18]=s.initialStateSynced;row[19]=p->drained();}
    auto out=env->NewLongArray(20);if(out)env->SetLongArrayRegion(out,0,20,row);return out;
}

extern "C" __attribute__((visibility("default"))) int SDL_main(int argc,char** argv){
    call(ownerThreadStarted); // Captures the actual SDL thread even on human cancel before init.
    Config c;bool renderer{};void* library{};
    try{
      // The bundled SDL JNI inserts argv[0]; getArguments contributes two entries.
      if(argc!=3||!argv||!argv[1]||std::strcmp(argv[1],"--station-psx-launch")||!argv[2]||!argv[2][0]||std::strlen(argv[2])>128)throw std::runtime_error("LAUNCH_ARGUMENTS");
      for(auto* q=argv[2];*q;++q)if(!((*q>='a'&&*q<='z')||(*q>='A'&&*q<='Z')||(*q>='0'&&*q<='9')||*q=='_'||*q=='-'||*q=='.'))throw std::runtime_error("LAUNCH_ARGUMENTS");
      {
        std::unique_lock lock(mutex);if(claimed)throw std::runtime_error("OWNER_ALREADY_CLAIMED");claimed=true;
        wake.wait(lock,[]{return prepared||!failure.empty()||human.load(std::memory_order_acquire);});
        if(human.load())return 0;if(!failure.empty())throw std::runtime_error("PREPARATION_FAILED");c=config;
      }
      library=dlopen("libmain.so",RTLD_NOW|RTLD_NOLOAD);if(!library)throw std::runtime_error("OWNER_NOT_LOADED");
      auto run=symbol<std::string(*)(const std::string&,const std::string&)>(library,RunSymbol);
      auto setHome=symbol<void(*)(const std::string&)>(library,HomeSymbol);
      auto bridge=symbol<void(*)()>(library,"_ZN13AndroidBridge4initEv");
      auto settings=symbol<void*(*)()>(library,"_ZN8Settings11getInstanceEv");
      auto init=symbol<bool(*)()>(library,"_ZN8Renderer4initEv");
      auto deinit=symbol<void(*)()>(library,"_ZN8Renderer6deinitEv");
      Dl_info info{};if(!dladdr(reinterpret_cast<void*>(run),&info)||!info.dli_fbase||!info.dli_fname)throw std::runtime_error("OWNER_MAPPING");
      auto ownerPath=canonical(info.dli_fname);auto ownerElf=readElf(ownerPath);auto coreElf=readElf(c.core);
      verifiedElf(ownerElf,OwnerSha);verifiedElf(coreElf,CoreSha);
      auto sdl=dlopen("libSDL2.so",RTLD_NOW|RTLD_NOLOAD);if(!sdl)throw std::runtime_error("SDL_NOT_LOADED");
      auto storage=symbol<const char*(*)()>(sdl,"SDL_AndroidGetInternalStoragePath");
      auto internal=storage();auto privateRoot=internal?canonical(internal):std::string();dlclose(sdl);
      const auto prefix=privateRoot+"/station-psx-online/";
      if(privateRoot.empty()||!c.home.starts_with(prefix)||!c.home.ends_with("/home")||c.home.size()<=prefix.size()+5)throw std::runtime_error("PRIVATE_HOME");
      for(auto suffix:{"/.emulationstation","/.emulationstation/bios","/.emulationstation/saves","/.emulationstation/core-options"}){
        auto dir=c.home+suffix;if(canonical(dir)!=dir||!directory(dir))throw std::runtime_error("PRIVATE_HOME_LAYOUT");
      }
      const auto font=c.home+"/.emulationstation/resources/sst_medium_condensed.ttf";
      if(canonical(font)!=font||!regular(font))throw std::runtime_error("OWNER_FONT_MISSING");
      const auto fontBytes=readElf(font);
      if(fontBytes.size()!=479776||hex(station::psx::sha256(fontBytes))!="cdc99f42f1d69bf8b798ec9d09c4979b574242d7f77aee775322dc286f7681f4")throw std::runtime_error("OWNER_FONT_IDENTITY");
      // Exactly the original ABI with a fresh private Settings/HOME namespace.
      setHome(c.home);bridge();if(!settings())throw std::runtime_error("OWNER_SETTINGS");
      const auto bios=c.home+"/.emulationstation/bios",saves=c.home+"/.emulationstation/saves";
      if(!owner::prepare(owner::Config{c.slot,c.home.c_str(),bios.c_str(),saves.c_str(),true,makeSession,onLocalPause,onOwnerFailure,nullptr})||
         !owner::install(reinterpret_cast<std::uintptr_t>(info.dli_fbase),ownerElf,coreElf))throw std::runtime_error("OWNER_HOOK_GUARD");
      if(human.load()){dlclose(library);return 0;}
      if(!init())throw std::runtime_error("OWNER_RENDERER");renderer=true;call(rendererReady);
      auto result=run(c.core,c.rom); // Genuine static normal owner; same SDL/render/input.
      {std::lock_guard lock(mutex);ownerReturned=true;}
      if(!human.load()){failed("OWNER_RETURNED_UNEXPECTEDLY");call(returned,"OWNER_RETURNED_UNEXPECTEDLY");waitForHuman();}
      else call(returned,result.empty()?std::string():std::string("OWNER_HUMAN_EXIT"));
      // No destructor/renderer shutdown on a network timeout or preparation failure.
      deinit();renderer=false;dlclose(library);return 0;
    }catch(const std::exception& e){failed(category(e.what()).c_str());}
    catch(...){failed("ENTRY_EXCEPTION");}
    waitForHuman();
    if(renderer&&library){try{symbol<void(*)()>(library,"_ZN8Renderer6deinitEv")();}catch(...){}}
    if(library)dlclose(library);
    {std::lock_guard lock(mutex);ownerReturned=true;}call(returned,"");return 0;
}
