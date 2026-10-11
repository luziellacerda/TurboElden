// SPDX-License-Identifier: GPL-2.0-or-later
// Exact original LibretroPlayer owner adapter. No instruction patch, no second
// emulator loop and no network wait inside retro_run or the SDL owner.
#include "StationPsxOwner.hpp"
#include "PsxPinnedOptions.h"
#include <algorithm>
#include <atomic>
#include <cstring>
#ifndef STATION_PSX_OWNER_HOST_PROBE
#include <dlfcn.h>
#endif
#ifndef STATION_PSX_OWNER_HOST_PROBE
#include <elf.h>
#endif
#include <fstream>
#include <map>
#include <mutex>
#include <thread>
#include <sstream>
#include <string>
#ifndef STATION_PSX_OWNER_HOST_PROBE
#include <sys/mman.h>
#include <unistd.h>
#endif

namespace station::psx::owner {
namespace {
constexpr char OwnerSha[]="62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6";
constexpr char CoreSha[]="e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9";
constexpr std::size_t Pause=0x68a, Quit=0x689, Running=0x74a;
constexpr std::uintptr_t CoreGlobal=0x3cf338, Rows=0x3cf2d0, Pending=0x3c7b18;
using Env=bool(*)(unsigned,void*);using Poll=void(*)();
using Input=std::int16_t(*)(unsigned,unsigned,unsigned,unsigned);
using Void=void(*)();using SetEnv=void(*)(Env);using SetPoll=void(*)(Poll);
using SetInput=void(*)(Input);using SetPort=void(*)(unsigned,unsigned);
using Size=std::size_t(*)();using Save=bool(*)(void*,std::size_t);
using Load=bool(*)(const void*,std::size_t);
struct Value{const char* value;const char* label;};
struct Definition{const char* key;const char* desc;const char* descCategorized;
 const char* info;const char* infoCategorized;const char* categoryKey;
 Value values[128];const char* defaultValue;};
struct Options{const void* categories;const Definition* definitions;};
struct Intl{const Options* us;const Options* local;};
struct Variable{const char* key;const char* value;};
static_assert(sizeof(Definition)==2104);
struct Segment{std::uintptr_t va;std::vector<std::uint8_t> bytes;};
struct Runtime {
 std::mutex setup;
 Config config{};std::string home,system,saves;std::vector<Segment> coreExec;
 std::atomic<bool> prepared{},installed{},bad{},ready{},human{},localPause{};
 std::atomic<Session*> session{};std::uintptr_t base{};std::uint8_t* core{};
 std::thread::id owner{};bool bound{},coreVerified{},optionsVerified{},factoryCalled{};
 Digest defaults{},options{};
 bool savedPause{},temporaryPause{},leased{},insideRun{},stateAuthorized{},closed{};
 Lease lease{};std::size_t stateBytes{};
 void*(*dlsymOriginal)(void*,const char*){};
 int(*eventsOriginal)(void*){};std::uint64_t(*counterOriginal)(){};
 std::string(*homeOriginal)(){};
 SetEnv setEnv{};SetPoll setPoll{};SetInput setInput{};SetPort setPort{};
 Env env{};Poll poll{};Input input{};Void run{},reset{},unload{},deinit{};
 Size size{};Save save{};Load load{};
};
Runtime r;
std::span<const std::uint8_t> bytes(const std::string& s){return {reinterpret_cast<const std::uint8_t*>(s.data()),s.size()};}
bool hexDigest(const char* value,Digest& out){
 if(!value||std::strlen(value)!=64)return false;
 for(std::size_t i=0;i<32;++i){auto nib=[](char c)->int{return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;};
 int a=nib(value[2*i]),b=nib(value[2*i+1]);if(a<0||b<0)return false;out[i]=std::uint8_t(a*16+b);}return true;
}
bool path(const char* s){if(!s||s[0]!='/'||std::strlen(s)>1024)return false;
 std::string p=s;if(p.find('\\')!=p.npos||p.find('\n')!=p.npos||p.find('\r')!=p.npos)return false;
 std::istringstream input(p);std::string part;while(std::getline(input,part,'/'))if(part==".."||part==".")return false;return true;}
bool child(const std::string& a,const std::string& root){return a==root||(a.size()>root.size()+1&&a.starts_with(root)&&a[root.size()]=='/');}
bool ownerThread(){return r.bound&&r.owner==std::this_thread::get_id();}
std::uint8_t& field(std::size_t offset){return r.core[offset];}
void fail(const char* why){bool first=!r.bad.exchange(true);if(auto* s=r.session.load())s->automaticStop(why);
 if(first&&r.config.onFailure)r.config.onFailure(why,r.config.user);}
void updateLocal(bool v){if(r.localPause.exchange(v)!=v&&r.config.onLocalPause)r.config.onLocalPause(v,r.config.user);}
bool boundedString(const char* p,std::size_t cap=4096){return p&&strnlen(p,cap)<cap;}
#ifndef STATION_PSX_OWNER_HOST_PROBE
bool readElf(std::span<const std::uint8_t> image,const char* hash,std::vector<Segment>& segments){
 Digest expected{};if(!hexDigest(hash,expected)||sha256(image)!=expected||image.size()<sizeof(Elf64_Ehdr))return false;
 Elf64_Ehdr eh{};std::memcpy(&eh,image.data(),sizeof eh);
 if(std::memcmp(eh.e_ident,ELFMAG,4)||eh.e_ident[EI_CLASS]!=ELFCLASS64||eh.e_ident[EI_DATA]!=ELFDATA2LSB||eh.e_machine!=EM_AARCH64||eh.e_phentsize!=sizeof(Elf64_Phdr)||eh.e_phnum>64)return false;
 if(eh.e_phoff>image.size()||std::size_t(eh.e_phnum)*sizeof(Elf64_Phdr)>image.size()-eh.e_phoff)return false;
 for(unsigned i=0;i<eh.e_phnum;++i){Elf64_Phdr ph{};std::memcpy(&ph,image.data()+eh.e_phoff+i*sizeof ph,sizeof ph);
 if(ph.p_type!=PT_LOAD||!(ph.p_flags&PF_X))continue;
 if(!ph.p_filesz||ph.p_offset>image.size()||ph.p_filesz>image.size()-ph.p_offset||ph.p_vaddr>UINTPTR_MAX-ph.p_filesz)return false;
 segments.push_back({ph.p_vaddr,{image.begin()+ph.p_offset,image.begin()+ph.p_offset+ph.p_filesz}});}
 return !segments.empty();
}
bool sameLoaded(std::uintptr_t base,const std::vector<Segment>& ss){
 for(const auto& s:ss)if(!base||base>UINTPTR_MAX-s.va||std::memcmp(reinterpret_cast<void*>(base+s.va),s.bytes.data(),s.bytes.size()))return false;return true;
}
bool checkCore(void* address){if(r.coreVerified)return true;Dl_info d{};
 if(!address||!dladdr(address,&d)||!sameLoaded(reinterpret_cast<std::uintptr_t>(d.dli_fbase),r.coreExec)){fail("CORE_BINARY_MISMATCH");return false;}
 r.coreVerified=true;return true;
}
#else
bool checkCore(void*){return false;} // Host fixture never validates/loads a fake ELF.
#endif
bool bindOwner(){auto* c=*reinterpret_cast<std::uint8_t**>(r.base+CoreGlobal);if(!c){fail("OWNER_BIND_MISSING");return false;}
 if(!r.bound){r.core=c;r.owner=std::this_thread::get_id();r.bound=true;}
 if(!ownerThread()||r.core!=c){fail("OWNER_THREAD_MISMATCH");return false;}return true;
}
bool exactCallback(void* p,std::uintptr_t off){return reinterpret_cast<std::uintptr_t>(p)==r.base+off;}
bool captureOptions(const Options* options){
 if(!options||!options->definitions)return false;std::map<std::string,std::string> actual;
 for(std::size_t i=0;i<=std::size(station_psx::compiled_defaults);++i){auto& d=options->definitions[i];if(!d.key)break;
 if(i==std::size(station_psx::compiled_defaults)||!boundedString(d.key,128)||!boundedString(d.defaultValue,128)||!actual.emplace(d.key,d.defaultValue).second)return false;
 const char* wanted=station_psx::pinned_option(d.key);if(!wanted)return false;
 bool exists=false;for(unsigned n=0;n<128&&d.values[n].value;++n){if(!boundedString(d.values[n].value,128))return false;if(!std::strcmp(d.values[n].value,wanted))exists=true;}if(!exists)return false;
 }
 if(actual.size()!=std::size(station_psx::compiled_defaults))return false;
 std::string canonical;for(const auto& [key,value]:actual){const char* expected=station_psx::lookup(station_psx::compiled_defaults,key.c_str());if(!expected||value!=expected)return false;canonical+=key+'='+value+'\n';}
 Digest expected{};if(!hexDigest(station_psx::compiled_defaults_sha256,expected)||sha256(bytes(canonical))!=expected)return false;
 r.defaults=expected;if(!hexDigest(station_psx::options_sha256,r.options)||sha256(bytes(station_psx::canonical_options))!=r.options)return false;
 r.optionsVerified=true;return true;
}
bool environment(unsigned command,void* data){
 if(!ownerThread()){fail("CORE_ENV_WRONG_THREAD");return false;}
 switch(command){
 case 52:if(data){*static_cast<unsigned*>(data)=2;return true;}return false; // GET_CORE_OPTIONS_VERSION
 case 39:if(data){*static_cast<unsigned*>(data)=0;return true;}return false; // LANGUAGE_ENGLISH
 case 67:if(captureOptions(static_cast<Options*>(data)))return true;fail("COMPILED_OPTIONS_MISMATCH");return false;
 case 68:{auto* intl=static_cast<Intl*>(data);if(intl&&captureOptions(intl->us))return true;fail("COMPILED_OPTIONS_MISMATCH");return false;}
 case 15:{auto* v=static_cast<Variable*>(data);if(!v||!boundedString(v->key,128))return false;
 v->value=station_psx::pinned_option(v->key);if(!v->value){fail("UNKNOWN_CORE_OPTION");return false;}return true;}
 case 17:if(data){*static_cast<bool*>(data)=false;return true;}return false;
 case 9:if(data){*static_cast<const char**>(data)=r.system.c_str();return true;}return false;
 case 31:if(data){*static_cast<const char**>(data)=r.saves.c_str();return true;}return false;
 case 7:fail("CORE_REQUESTED_SHUTDOWN");return false;
 case 70:fail("CORE_OPTION_MUTATION");return false;
 case 64:return false; // FASTFORWARDING_OVERRIDE is not approved online
 case 49:case (49|0x10000):if(data){*static_cast<bool*>(data)=false;return true;}return false;
 case (51|0x10000):return false; // INPUT_BITMASKS: use exact IDs0..13
 case 53:case 54:case 16:fail("UNEXPECTED_OPTIONS_ABI");return false;
 default:return r.env?r.env(command,data):false;
 }
}
void setEnvironment(Env cb){if(!exactCallback(reinterpret_cast<void*>(cb),0x2b29f8)){fail("ENV_CALLBACK_MISMATCH");return;}r.env=cb;r.setEnv(environment);}
void inputPoll(){if(!ownerThread()||!r.insideRun||!r.leased){fail("INPUT_WITHOUT_OWNER_LEASE");return;}/* Original poll was sampled once at the pre-core checkpoint. */}
std::int16_t inputState(unsigned port,unsigned device,unsigned index,unsigned id){
 if(!ownerThread()||!r.insideRun||!r.leased){fail("INPUT_WITHOUT_OWNER_LEASE");return 0;}
 if(port>1||device!=1||index||id>13)return 0;return (r.lease.frame.pads[port]>>id)&1;
}
void setInputPoll(Poll cb){if(!exactCallback(reinterpret_cast<void*>(cb),0x2b587c)){fail("POLL_CALLBACK_MISMATCH");return;}r.poll=cb;r.setPoll(inputPoll);}
void setInputState(Input cb){if(!exactCallback(reinterpret_cast<void*>(cb),0x2b62b0)){fail("INPUT_CALLBACK_MISMATCH");return;}r.input=cb;r.setInput(inputState);}
void setController(unsigned port,unsigned device){if(!ownerThread()){fail("PORT_WRONG_THREAD");return;}(void)device;if(port<2)r.setPort(port,1); /* Signed StandardPad pins override original per-user device prefs in this process only. */}
void deniedReset(){fail("RESET_BLOCKED");}
bool guardedSave(void* p,std::size_t n){return ownerThread()&&r.stateAuthorized&&n==r.stateBytes&&r.save&&r.save(p,n);}
bool guardedLoad(const void* p,std::size_t n){return ownerThread()&&r.stateAuthorized&&n==r.stateBytes&&r.load&&r.load(p,n);}
void unloadGame(){if(!r.closed){fail("AUTOMATIC_UNLOAD_BLOCKED");return;}if(r.unload)r.unload();}
void deinitCore(){if(!r.closed){fail("AUTOMATIC_DEINIT_BLOCKED");return;}if(r.deinit)r.deinit();}
void runCore(){
 auto* s=r.session.load();if(!ownerThread()||!s||!r.leased||r.insideRun||r.bad.load()||r.localPause.load()){fail("RUN_WITHOUT_REAL_LEASE");return;}
 r.insideRun=true;try{r.run();}catch(...){r.insideRun=false;s->ownerAbort(r.lease,"CORE_EXCEPTION");r.leased=false;fail("CORE_EXCEPTION");return;}r.insideRun=false;
 if(!field(Running)||field(Quit)||r.bad.load()){s->ownerAbort(r.lease,"CORE_STOPPED_DURING_RUN");r.leased=false;field(Running)=1;field(Quit)=0;fail("CORE_STOPPED_DURING_RUN");return;}
 auto result=s->ownerComplete(r.lease);r.leased=false;if(result!=Result::Ok&&result!=Result::Superseded)fail("OWNER_COMPLETE_REJECTED");
}
void* resolveCoreSymbol(std::uintptr_t pc,const char* name,void* p){
 struct Hook {const char* name;std::uintptr_t pc;void** original;void* wrapper;};
 const Hook hooks[]={
 {"retro_set_environment",0x2bcfc8,reinterpret_cast<void**>(&r.setEnv),reinterpret_cast<void*>(setEnvironment)},
 {"retro_set_input_poll",0x2bd028,reinterpret_cast<void**>(&r.setPoll),reinterpret_cast<void*>(setInputPoll)},
 {"retro_set_input_state",0x2bd040,reinterpret_cast<void**>(&r.setInput),reinterpret_cast<void*>(setInputState)},
 {"retro_run",0x2bd0e8,reinterpret_cast<void**>(&r.run),reinterpret_cast<void*>(runCore)},
 {"retro_reset",0x2bd100,reinterpret_cast<void**>(&r.reset),reinterpret_cast<void*>(deniedReset)},
 {"retro_unload_game",0x2bd0d0,reinterpret_cast<void**>(&r.unload),reinterpret_cast<void*>(unloadGame)},
 {"retro_deinit",0x2bd070,reinterpret_cast<void**>(&r.deinit),reinterpret_cast<void*>(deinitCore)},
 {"retro_set_controller_port_device",0x2bd160,reinterpret_cast<void**>(&r.setPort),reinterpret_cast<void*>(setController)},
 {"retro_serialize",0x2bd190,reinterpret_cast<void**>(&r.save),reinterpret_cast<void*>(guardedSave)},
 {"retro_unserialize",0x2bd1a8,reinterpret_cast<void**>(&r.load),reinterpret_cast<void*>(guardedLoad)}};
 for(auto h:hooks)if(!std::strcmp(name,h.name)){if(pc!=h.pc||!p){fail("CORE_SYMBOL_CALLSITE_MISMATCH");return nullptr;}*h.original=p;return h.wrapper;}
 if(!std::strcmp(name,"retro_serialize_size")){if(pc!=0x2bd178||!p){fail("STATE_SIZE_CALLSITE_MISMATCH");return nullptr;}r.size=reinterpret_cast<Size>(p);}
 return p;
}
__attribute__((noinline)) void* symbol(void* handle,const char* name){
 auto caller=reinterpret_cast<std::uintptr_t>(__builtin_return_address(0));void* p=r.dlsymOriginal(handle,name);
 auto pc=caller-r.base;if(pc<0x2bcfc8||pc>0x2bd1a8||!r.installed.load()||!name)return p;
 if(!bindOwner()||!checkCore(p))return nullptr;
 return resolveCoreSymbol(pc,name,p);
}
void menuGuards(){
 auto* begin=*reinterpret_cast<std::uint8_t**>(r.base+Rows);auto* end=*reinterpret_cast<std::uint8_t**>(r.base+Rows+8);
 if(begin&&end>=begin&&std::size_t(end-begin)<=56*64&&(end-begin)%56==0)
 for(auto* p=begin;p<end;p+=56){int action{};std::memcpy(&action,p,4);if(action==1||action==2||action==3)p[32]=0;}
 *reinterpret_cast<int*>(r.base+Pending)=-1;
 if(field(Quit)){field(Quit)=0;fail("CORE_REQUESTED_EXIT");}
 if(!field(Running)&&!r.closed){field(Running)=1;fail("AUTOMATIC_OWNER_STOP_BLOCKED");}
}
__attribute__((noinline)) int events(void* event){
 auto caller=reinterpret_cast<std::uintptr_t>(__builtin_return_address(0));
 if(caller!=r.base+0x2abe4c||!r.installed.load())return r.eventsOriginal(event);
 if(!bindOwner())return 0;
 for(unsigned suppressed=0;suppressed<64;++suppressed){int result=r.eventsOriginal(event);
 if(!result){menuGuards();return 0;}
 std::uint32_t type{};if(event)std::memcpy(&type,event,4);
 if(type==0x100&&!r.closed)continue; // never treat lifecycle SDL_QUIT as human authorization
 return result;}
 // Continue draining on the next owner iteration; never fabricate a quit event.
 menuGuards();return 0;
}
bool applyState(void*,std::span<const std::uint8_t> state){if(!ownerThread()||state.size()!=r.stateBytes||!r.load)return false;
 r.stateAuthorized=true;bool okay=false;try{okay=r.load(state.data(),state.size());}catch(...){okay=false;}r.stateAuthorized=false;return okay;
}
void checkpoint(){
 if(!ownerThread()||!r.core){fail("CHECKPOINT_WRONG_OWNER");return;}
 r.savedPause=field(Pause)!=0;r.temporaryPause=true;field(Pause)=1;updateLocal(r.savedPause);
 if(r.leased){auto* s=r.session.load();if(s)s->ownerAbort(r.lease,"MISSED_REAL_RUN");r.leased=false;fail("MISSED_REAL_RUN");}
 if(!field(Running)||field(Quit)){field(Running)=1;field(Quit)=0;fail("AUTOMATIC_OWNER_STOP_BLOCKED");}
 if(r.human.load()){
 if(auto* s=r.session.load()){s->authorizeHumanExit();s->ownerCheckpoint();auto closed=s->ownerClose();if(closed!=Result::Ok&&closed!=Result::Closed)return;}
 r.closed=true;field(Running)=0;return;}
 if(r.bad.load())return;
 if(!r.factoryCalled){
 if(field(8)!=1||!r.coreVerified||!r.optionsVerified||!r.poll||!r.input||!r.run||!r.size||!r.save||!r.load||!r.setPort){fail("LOADED_CORE_INCOMPLETE");return;}
 r.stateBytes=r.size();if(!r.stateBytes||r.stateBytes>MaxState){fail("STATE_SIZE_INVALID");return;}
 r.setPort(0,1);r.setPort(1,1);r.factoryCalled=true;
 Session* s=nullptr;try{s=r.config.onCoreReady(r.stateBytes,r.defaults,r.options,r.config.user);}catch(...){s=nullptr;}
 if(!s){fail("SESSION_FACTORY_REJECTED");return;}r.session.store(s);r.ready.store(true);
 }
 auto* s=r.session.load();auto result=s->ownerCheckpoint();
 if(result==Result::WrongOwner||result==Result::Invalid||result==Result::Failed){fail("SESSION_CHECKPOINT_REJECTED");return;}
 auto status=s->status();
 if(r.config.localSlot==1&&s->stateRequested()&&status.paused&&status.pause.valid&&!status.inFrame&&!status.applyingState){
 std::vector<std::uint8_t> state(r.stateBytes);r.stateAuthorized=true;bool okay=false;try{okay=r.save(state.data(),state.size());}catch(...){okay=false;}r.stateAuthorized=false;
 if(!okay){fail("STATE_SERIALIZE_REJECTED");return;}
 auto published=s->ownerPublishState(std::move(state),status.nextFrame);if(published!=Result::Ok&&published!=Result::Wait){fail("STATE_PUBLISH_REJECTED");return;}
 }else if(r.config.localSlot==2&&status.paused){auto applied=s->ownerApplyState(applyState,r.core);if(applied==Result::Failed){fail("STATE_APPLY_REJECTED");return;}}
 if(r.savedPause)return; // native menu pause is independent of network pause
 s->ownerCheckpoint();if(s->needsLocalSample()){
 field(Pause)=r.savedPause?1:0;r.poll();r.savedPause=field(Pause)!=0;updateLocal(r.savedPause);field(Pause)=1;if(field(Quit)||!field(Running)){field(Quit)=0;field(Running)=1;fail("INPUT_REQUESTED_STOP");return;}
 
 if(r.localPause.load())return;
 std::uint16_t pad{};for(unsigned i=0;i<14;++i)if(r.input(0,1,0,i))pad|=std::uint16_t(1u<<i);
 auto sampled=s->ownerSampleLocal(pad);if(sampled!=Result::Ok&&sampled!=Result::Duplicate&&sampled!=Result::Backpressure){fail("INPUT_SAMPLE_REJECTED");return;}}
 if(s->ownerBegin(r.lease)==Result::Ok){r.leased=true;field(Pause)=0;}
}
void finishCheckpoint(){
 if(!ownerThread()||!r.temporaryPause)return;
 if(r.leased){if(auto* s=r.session.load())s->ownerAbort(r.lease,"CORE_NOT_EXECUTED");r.leased=false;fail("CORE_NOT_EXECUTED");}
 if(!r.closed){field(Pause)=r.savedPause?1:0;if(!field(Running)||field(Quit)){field(Running)=1;field(Quit)=0;fail("AUTOMATIC_OWNER_STOP_BLOCKED");}}
 r.temporaryPause=false;
}
__attribute__((noinline)) std::uint64_t counter(){
 auto caller=reinterpret_cast<std::uintptr_t>(__builtin_return_address(0));
 if(r.installed.load()&&caller==r.base+0x2ae600)checkpoint();
 else if(r.installed.load()&&caller==r.base+0x2ae61c)finishCheckpoint();
 return r.counterOriginal();
}
__attribute__((noinline)) std::string home(){auto caller=reinterpret_cast<std::uintptr_t>(__builtin_return_address(0));
 if(r.installed.load()&&caller==r.base+0x2a99d8)return r.home;
 return r.homeOriginal(); // settings/assets/HOME outside exact save setup preserved
}
#ifndef STATION_PSX_OWNER_HOST_PROBE
int protection(std::uintptr_t page){std::ifstream f("/proc/self/maps");std::string line;
 while(std::getline(f,line)){unsigned long begin{},end{};char flags[5]{};
 if(std::sscanf(line.c_str(),"%lx-%lx %4s",&begin,&end,flags)==3&&page>=begin&&page<end)return (flags[0]=='r'?PROT_READ:0)|(flags[1]=='w'?PROT_WRITE:0)|(flags[2]=='x'?PROT_EXEC:0);}
 return -1;
}
#endif
} // anonymous
bool prepare(const Config& c){std::lock_guard lock(r.setup);
 if(r.prepared.load()||r.installed.load()||c.localSlot<1||c.localSlot>2||!c.gameApprovedForHleStandardTwoPorts||!c.onCoreReady||!path(c.sessionHome)||!path(c.systemDirectory)||!path(c.saveDirectory))return false;
 std::string h=c.sessionHome;while(h.size()>1&&h.back()=='/')h.pop_back();if(h=="/"||!child(c.systemDirectory,h)||!child(c.saveDirectory,h))return false;
 r.config=c;r.home=h;r.system=c.systemDirectory;r.saves=c.saveDirectory;r.prepared.store(true);return true;
}
#ifndef STATION_PSX_OWNER_HOST_PROBE
bool install(std::uintptr_t base,std::span<const std::uint8_t> ownerElf,std::span<const std::uint8_t> coreElf){std::lock_guard lock(r.setup);
 if(!r.prepared.load()||r.installed.load()||!base)return false;
 std::vector<Segment> ownerExec,coreExec;if(!readElf(ownerElf,OwnerSha,ownerExec)||!readElf(coreElf,CoreSha,coreExec)||!sameLoaded(base,ownerExec))return false;
 const std::uintptr_t offsets[]={0x3bf7f8,0x3c2a00,0x3c2cc0,0x3bf6d8};
 void* replacements[]={reinterpret_cast<void*>(events),reinterpret_cast<void*>(counter),reinterpret_cast<void*>(symbol),reinterpret_cast<void*>(home)};
 void* originals[4]{};auto pagesize=sysconf(_SC_PAGESIZE);if(pagesize<=0)return false;std::map<std::uintptr_t,int> pages;
 for(unsigned i=0;i<4;++i){originals[i]=*reinterpret_cast<void**>(base+offsets[i]);if(!originals[i])return false;auto page=(base+offsets[i])&~(std::uintptr_t(pagesize)-1);auto prot=protection(page);if(prot<0||(prot&PROT_EXEC))return false;pages[page]=prot;}
 std::vector<std::uintptr_t> changed;for(auto [page,prot]:pages){if(mprotect(reinterpret_cast<void*>(page),pagesize,prot|PROT_WRITE)!=0){for(auto old:changed)mprotect(reinterpret_cast<void*>(old),pagesize,pages[old]);return false;}changed.push_back(page);}
 r.base=base;r.coreExec=std::move(coreExec);r.eventsOriginal=reinterpret_cast<decltype(r.eventsOriginal)>(originals[0]);r.counterOriginal=reinterpret_cast<decltype(r.counterOriginal)>(originals[1]);r.dlsymOriginal=reinterpret_cast<decltype(r.dlsymOriginal)>(originals[2]);r.homeOriginal=reinterpret_cast<decltype(r.homeOriginal)>(originals[3]);
 // Set all state before publishing any GOT pointer. Caller guarantees Player has
 // not started; no partially installed hooks can race the original SDL thread.
 for(unsigned i=0;i<4;++i)*reinterpret_cast<void**>(base+offsets[i])=replacements[i];r.installed.store(true);
 bool okay=true;for(auto [page,prot]:pages)if(mprotect(reinterpret_cast<void*>(page),pagesize,prot)!=0)okay=false;
 if(!okay){fail("GOT_PROTECTION_RESTORE_FAILED");return false;}return true;
}
#else
bool install(std::uintptr_t,std::span<const std::uint8_t>,std::span<const std::uint8_t>){return false;}
#endif
Session* session(){return r.session.load();}
bool coreReady(){return r.ready.load();}
bool localPaused(){return r.localPause.load();}
bool failed(){return r.bad.load();}
void authorizeHumanExit(){r.human.store(true);}
const char* ownerHash(){return OwnerSha;}
const char* coreHash(){return CoreSha;}
} // namespace station::psx::owner
