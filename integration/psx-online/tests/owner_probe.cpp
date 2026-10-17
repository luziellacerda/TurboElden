// Host-only fixture of the actual adapter implementation. Never packaged.
#define STATION_PSX_OWNER_HOST_PROBE 1
#include "StationPsxOwner.cpp"
#include <iostream>
#include <stdexcept>
#include <thread>
using namespace station::psx;
using namespace station::psx::owner;
namespace {
unsigned checks{},polls{},runs{},saves{},loads{},factories{},failures{},pauseSignals{},ports{};
std::uint64_t coreFrame{};unsigned expectedDelay{};std::uint16_t localBits=0x0020;bool stopDuringRun{};
Session* factorySession{};std::array<std::uint8_t,0x800> coreMemory{};
std::vector<std::uint8_t> fakeOwnerMemory(0x3d0000);
void require(bool okay,const char* why){++checks;if(!okay)throw std::runtime_error(why);}
Digest identity(){Digest d{};d[0]=0x11;return d;}
Session* factory(std::size_t size,const Digest& defaults,const Digest& options,void*){
 ++factories;Digest expected{};require(size==64,"real serialized size");
 hexDigest(station_psx::compiled_defaults_sha256,expected);require(defaults==expected,"compiled defaults");
 hexDigest(station_psx::options_sha256,expected);require(options==expected,"canonical options");return factorySession;
}
void paused(bool,void*){++pauseSignals;}void failure(const char*,void*){++failures;}
void originalPoll(){++polls;}
std::int16_t originalInput(unsigned p,unsigned d,unsigned i,unsigned id){return p==0&&d==1&&!i&&id<14?((localBits>>id)&1):0;}
std::size_t size(){return 64;}
bool save(void* bytes,std::size_t n){++saves;if(n!=64)return false;std::memset(bytes,0,n);std::memcpy(bytes,&coreFrame,8);return true;}
bool load(const void* bytes,std::size_t n){++loads;if(n!=64)return false;std::memcpy(&coreFrame,bytes,8);return true;}
void port(unsigned p,unsigned d){require(p<2&&d==1,"actual standard ports");++ports;}
void originalRun(){++runs;inputPoll();require(inputState(0,1,0,5)==(coreFrame>=expectedDelay),"original local P1 maps to signed slot after neutral pipeline");
 require(inputState(1,1,0,6)==(coreFrame>=expectedDelay),"canonical remote P2 after neutral pipeline");require(!inputState(2,1,0,0),"third pad prohibited");
 require(!inputState(0,5,0,0),"analog prohibited");require(!inputState(0,1,0,15),"R3 prohibited");
 ++coreFrame;if(stopDuringRun)field(Running)=0;
}
void initialize(Session& target){
 r.base=reinterpret_cast<std::uintptr_t>(fakeOwnerMemory.data());r.core=coreMemory.data();coreMemory.fill(0);
 *reinterpret_cast<std::uint8_t**>(r.base+CoreGlobal)=r.core;
 r.bound=true;r.owner=std::this_thread::get_id();r.installed.store(false);r.bad.store(false);r.human.store(false);
 r.localPause.store(false);r.ready.store(false);r.session.store(nullptr);r.closed=false;r.factoryCalled=false;
 r.leased=false;r.insideRun=false;r.temporaryPause=false;r.stateAuthorized=false;r.coreVerified=true;
 r.config.localSlot=1;field(8)=1;field(Running)=1;r.poll=originalPoll;r.input=originalInput;r.run=originalRun;
 r.size=size;r.save=save;r.load=load;r.setPort=port;r.stateBytes=0;factorySession=&target;coreFrame=0;stopDuringRun=false;
 std::vector<Definition> rows(std::size(station_psx::compiled_defaults)+1);
 for(std::size_t i=0;i<std::size(station_psx::compiled_defaults);++i){auto row=station_psx::compiled_defaults[i];rows[i].key=row.key;rows[i].defaultValue=row.value;
 rows[i].values[0]={row.value,nullptr};const char* pinned=station_psx::pinned_option(row.key);if(std::strcmp(row.value,pinned))rows[i].values[1]={pinned,nullptr};}
 Options opts{nullptr,rows.data()};require(captureOptions(&opts),"capture exact V2 59 options");
 rows.back().key="unexpected";rows.back().defaultValue="bad";require(!captureOptions(&opts),"reject extra compiled option");rows.back().key=nullptr;
 rows[0].defaultValue="bad";require(!captureOptions(&opts),"reject changed compiled default");rows[0].defaultValue=station_psx::compiled_defaults[0].value;
 require(captureOptions(&opts),"restore exact fixture options");
}
void link(Session& from,Session& to,std::uint8_t remote,std::uint64_t& id){
 for(unsigned n=0;n<1024;++n){auto bytes=from.takeOutgoing();if(bytes.empty())return;auto next=++id;
 auto result=to.deliver(remote,next,bytes);require(result==Result::Ok||result==Result::Duplicate,"real protocol copied packet");
 require(to.copied(next),"transport copy receipt separate from CPU");require(to.releaseReceipt(next)==Result::Ok,"receipt release");}
 throw std::runtime_error("unbounded link");
}
void drain(Session& s){Commit c;for(unsigned n=0;n<1024&&s.takeCommit(c);++n){require(c.stamp.epoch==1&&c.stamp.stateSerial>=1,"commit exact epoch/state");require(c.outcome==Outcome::Executed||c.outcome==Outcome::AppliedState||c.outcome==Outcome::Superseded,"classified semantic commit");}}
bool guestApply(void* ptr,std::span<const std::uint8_t> bytes){require(bytes.size()==64,"guest exact size");std::memcpy(ptr,bytes.data(),8);return true;}
void sync(Session& host,Session& guest,std::uint64_t& id){
 require(host.control(1,1,true,true)==Result::Ok,"host control");require(guest.control(1,1,true,true)==Result::Ok,"guest control");
 checkpoint();require(field(Pause)==1&&!r.leased,"bootstrap no false run");finishCheckpoint();
 require(host.status().stateReady,"host real serialized initial state");link(host,guest,1,id);guest.ownerCheckpoint();std::uint64_t guestCursor{};
 require(guest.ownerApplyState(guestApply,&guestCursor)==Result::Ok,"guest actual success callback");link(guest,host,2,id);
 require(host.status().initialStateSynced&&guest.status().initialStateSynced,"initial actual applied state COMMIT");drain(host);drain(guest);
 require(host.control(1,2,false,true)==Result::Ok,"host resume control");require(guest.control(1,2,false,true)==Result::Ok,"guest resume control");
 host.ownerCheckpoint();guest.ownerCheckpoint();require(host.resume(1,2)==Result::Ok,"host exact resume");require(guest.resume(1,2)==Result::Ok,"guest exact resume");
}
}
int main(){try{
 station::psx::owner::Config c{1,"/private/session","/private/session/system","/private/session/saves",true,factory,paused,failure,nullptr};
 auto bad=c;bad.gameApprovedForHleStandardTwoPorts=false;require(!prepare(bad),"no universal HLE approval");
 bad=c;bad.saveDirectory="/offline/saves";require(!prepare(bad),"no offline saves");require(prepare(c),"prepare exact session");require(!prepare(c),"no reconfigure");
 require(!install(0,{},{}),"host fixture cannot install hooks");

 struct ResolveCase{std::uintptr_t pc;const char* name;void* target;void* wrapper;};
 const ResolveCase mapping[]={
 {0x2bcfc8,"retro_set_environment",reinterpret_cast<void*>(originalPoll),reinterpret_cast<void*>(setEnvironment)},
 {0x2bd028,"retro_set_input_poll",reinterpret_cast<void*>(originalPoll),reinterpret_cast<void*>(setInputPoll)},
 {0x2bd040,"retro_set_input_state",reinterpret_cast<void*>(originalInput),reinterpret_cast<void*>(setInputState)},
 {0x2bd0e8,"retro_run",reinterpret_cast<void*>(originalRun),reinterpret_cast<void*>(runCore)},
 {0x2bd100,"retro_reset",reinterpret_cast<void*>(originalPoll),reinterpret_cast<void*>(deniedReset)},
 {0x2bd0d0,"retro_unload_game",reinterpret_cast<void*>(originalPoll),reinterpret_cast<void*>(unloadGame)},
 {0x2bd070,"retro_deinit",reinterpret_cast<void*>(originalPoll),reinterpret_cast<void*>(deinitCore)},
 {0x2bd160,"retro_set_controller_port_device",reinterpret_cast<void*>(port),reinterpret_cast<void*>(setController)},
 {0x2bd190,"retro_serialize",reinterpret_cast<void*>(save),reinterpret_cast<void*>(guardedSave)},
 {0x2bd1a8,"retro_unserialize",reinterpret_cast<void*>(load),reinterpret_cast<void*>(guardedLoad)}};
 for(const auto& m:mapping){require(resolveCoreSymbol(m.pc,m.name,m.target)==m.wrapper,"actual resolver exact ELF return-PC hook");require(!resolveCoreSymbol(m.pc+4,m.name,m.target),"moved caller refused");r.bad.store(false);require(!resolveCoreSymbol(m.pc,m.name,nullptr),"missing real core symbol refused");r.bad.store(false);}
 require(resolveCoreSymbol(0x2bd178,"retro_serialize_size",reinterpret_cast<void*>(size))==reinterpret_cast<void*>(size)&&r.size==size,"size exact resolver");
 require(!resolveCoreSymbol(0x2bd180,"retro_serialize_size",reinterpret_cast<void*>(size)),"shifted size resolver rejected");r.bad.store(false);
 require(resolveCoreSymbol(0x2bcfe0,"retro_set_video_refresh",reinterpret_cast<void*>(originalPoll))==reinterpret_cast<void*>(originalPoll),"original video setter untouched");
 Session host({1,1,64,identity(),0}),guest({2,1,64,identity(),0});initialize(host);
 require(!session()&&!coreReady()&&factories==0,"no prepare fake core-ready");checkpoint();require(session()==&host&&coreReady()&&factories==1,"factory genuine checkpoint only");
 require(r.leased==false&&runs==0,"startup paused without run");finishCheckpoint();std::uint64_t id{};sync(host,guest,id);
 unsigned beforePoll=polls;checkpoint();require(!r.leased&&field(Pause)==1&&runs==0,"missing input skips real core via pause byte");finishCheckpoint();
 checkpoint();require(polls==beforePoll+1,"original input sampled once despite waiting");finishCheckpoint();
 for(unsigned frame=0;frame<256;++frame){
 require(guest.ownerSampleLocal(0x0040)==Result::Ok,"guest sample canonical");link(guest,host,2,id);
 checkpoint();if(!r.leased){auto st=host.status();std::cerr<<"frame="<<frame<<" core="<<coreFrame<<" pause="<<unsigned(field(Pause))<<" local="<<localPaused()<<" failed="<<failed()<<" state="<<st.stateReady<<" p="<<st.paused<<" f="<<host.failure()<<" polls="<<polls<<"\n";}require(r.leased&&field(Pause)==0,"complete exact lease enters original core gate");runCore();finishCheckpoint();
 require(!r.leased&&!host.status().inFrame&&host.status().nextFrame==frame+1&&coreFrame==frame+1,"commit only real raw run");
 link(host,guest,1,id);Lease peerLease;require(guest.ownerBegin(peerLease)==Result::Ok,"guest canonical frame");require(guest.ownerComplete(peerLease)==Result::Ok,"guest execution fixture");link(guest,host,2,id);drain(host);drain(guest);
 }
 require(runs==256&&polls==beforePoll+256,"no fake/catchup frames or repeated local sample");
 require(!guardedSave(coreMemory.data(),64)&&!guardedLoad(coreMemory.data(),64),"manual state denied");
 field(Pause)=1;checkpoint();require(localPaused()&&!r.leased,"native local menu must withhold READY");finishCheckpoint();
 field(Pause)=0;checkpoint();require(!localPaused(),"native resume signal");finishCheckpoint();
 unsigned originalSaves=saves;r.stateAuthorized=true;require(!guardedSave(coreMemory.data(),63)&&saves==originalSaves,"state exact byte bound");r.stateAuthorized=false;
 std::array<std::array<std::uint8_t,56>,4> rows{};for(unsigned i=0;i<4;++i){std::memcpy(rows[i].data(),&i,4);rows[i][32]=1;}
 *reinterpret_cast<std::uint8_t**>(r.base+Rows)=rows[0].data();*reinterpret_cast<std::uint8_t**>(r.base+Rows+8)=rows[0].data()+sizeof(rows);
 *reinterpret_cast<int*>(r.base+Pending)=2;menuGuards();require(rows[0][32]&&!rows[1][32]&&!rows[2][32]&&!rows[3][32],"save/load/exit row guarded before action");require(*reinterpret_cast<int*>(r.base+Pending)==-1,"pending manual action consumed");
 require(!environment(7,nullptr)&&failed()&&!host.status().closed,"core shutdown is failure not human exit");
 checkpoint();finishCheckpoint();require(runs==256&&!r.closed&&field(Running)==1,"failure remains responsive no automatic close");
 authorizeHumanExit();checkpoint();require(r.closed&&host.status().closed&&field(Running)==0,"explicit human closes on actual owner");finishCheckpoint();
 Session failedHost({1,1,64,identity(),0}),failedGuest({2,1,64,identity(),0});initialize(failedHost);checkpoint();finishCheckpoint();sync(failedHost,failedGuest,id);
 require(failedGuest.ownerSampleLocal(0x0040)==Result::Ok,"failed guest sample");link(failedGuest,failedHost,2,id);checkpoint();require(r.leased,"failing lease prepared");stopDuringRun=true;runCore();finishCheckpoint();
 require(failed()&&!failedHost.status().inFrame&&!failedHost.status().stateReady&&!failedHost.status().closed&&field(Running)==1,"failed original run aborts lease and no false Ready/exit");
 unsigned savesBefore=saves;std::thread wrong([&]{require(!guardedSave(coreMemory.data(),64),"IO cannot serialize");});wrong.join();require(saves==savesBefore,"no decoder invoked by IO");

 // Productive signed delay8 exercises the same real adapter checkpoints.
 Session pipelineHost({1,1,64,identity(),station_psx::input_delay_frames}),pipelineGuest({2,1,64,identity(),station_psx::input_delay_frames});
 expectedDelay=station_psx::input_delay_frames;initialize(pipelineHost);checkpoint();finishCheckpoint();sync(pipelineHost,pipelineGuest,id);
 unsigned pipelineRuns=runs,pipelinePolls=polls;
 for(unsigned frame=0;frame<256;++frame){
 require(pipelineGuest.needsLocalSample(),"pipeline future sample required once per cursor");
 require(pipelineGuest.ownerSampleLocal(0x0040)==Result::Ok,"guest sample N+signedDelay");link(pipelineGuest,pipelineHost,2,id);
 checkpoint();require(r.leased&&field(Pause)==0,"pipeline real gate has canonical future input");
 require(r.lease.frame.pads[0]==(frame<station_psx::input_delay_frames?0:0x0020)&&r.lease.frame.pads[1]==(frame<station_psx::input_delay_frames?0:0x0040),"only signed-delay synchronized neutral frames");
 runCore();finishCheckpoint();require(pipelineHost.status().nextFrame==frame+1&&coreFrame==frame+1,"pipeline cursor follows raw run only");
 link(pipelineHost,pipelineGuest,1,id);Lease peerLease;require(pipelineGuest.ownerBegin(peerLease)==Result::Ok,"guest pipeline frame post host run");
 require(pipelineGuest.ownerComplete(peerLease)==Result::Ok,"guest pipeline executed");link(pipelineGuest,pipelineHost,2,id);drain(pipelineHost);drain(pipelineGuest);
 }
 require(runs==pipelineRuns+256&&polls==pipelinePolls+256,"pipeline no fake runs or extra sampling");
 require(pipelineHost.control(1,3,true,true)==Result::Ok&&pipelineGuest.control(1,3,true,true)==Result::Ok,"pause futures for recovery");
 checkpoint();require(!r.leased&&field(Pause)==1,"real pipeline pause without extra raw run");finishCheckpoint();
 link(pipelineHost,pipelineGuest,1,id);pipelineGuest.ownerCheckpoint();std::uint64_t recoveredCursor{};
 require(pipelineGuest.ownerApplyState(guestApply,&recoveredCursor)==Result::Ok&&recoveredCursor==256,"snapshot applies exact real current frame");
 link(pipelineGuest,pipelineHost,2,id);drain(pipelineHost);drain(pipelineGuest);
 require(pipelineHost.status().initialStateSynced&&pipelineGuest.status().initialStateSynced,"snapshot peer application completes recovery");
 require(pipelineHost.control(1,4,false,true)==Result::Ok&&pipelineGuest.control(1,4,false,true)==Result::Ok,"fresh resume control");
 pipelineHost.ownerCheckpoint();pipelineGuest.ownerCheckpoint();require(pipelineHost.resume(1,4)==Result::Ok&&pipelineGuest.resume(1,4)==Result::Ok,"real exact epoch serial resume");
 expectedDelay=256+station_psx::input_delay_frames; // restart primes only the signed neutral inputs at actual cursor256.
 require(pipelineGuest.ownerSampleLocal(0x0040)==Result::Ok,"future after recovery");link(pipelineGuest,pipelineHost,2,id);
 checkpoint();require(r.leased&&r.lease.frame.pads[0]==0&&r.lease.frame.pads[1]==0,"recovery neutral prime after state and readiness");runCore();finishCheckpoint();
 require(coreFrame==257&&pipelineHost.status().nextFrame==257,"no hidden recovery catchup frame");
 authorizeHumanExit();checkpoint();finishCheckpoint();require(pipelineHost.status().closed,"human-only pipeline end");
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"realAdapterCheckpointRuns\":513,\"scope\":\"host-only fake SDL/core with real Session; no Android/ROM\"}\n";
 return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
