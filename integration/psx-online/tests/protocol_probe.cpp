// SPDX-License-Identifier: GPL-2.0-or-later
// Synthetic owner and peer unit tests. No PSX game, JNI, SDL or server is run.
#include "StationPsxProtocol.hpp"
#include <algorithm>
#include <iostream>
#include <deque>
#include <stdexcept>
#include <thread>
using namespace station::psx;
using Bytes=std::vector<std::uint8_t>;
namespace {
unsigned checks{};
void check(bool b,const char* what){++checks;if(!b)throw std::runtime_error(what);}
void eq(Result got,Result want,const char* what){check(got==want,what);}
std::string hex(Digest d){constexpr char c[]="0123456789abcdef";std::string s;for(auto b:d){s+=c[b>>4];s+=c[b&15];}return s;}
Digest identity(){const Bytes b{'e','x','a','c','t','-','i','d','e','n','t','i','t','y'};return sha256(b);}
Config config(unsigned slot,std::size_t size=4096,unsigned delay=0){return {std::uint8_t(slot),1,size,identity(),delay};}
struct Core {unsigned runs{},applies{};std::uint64_t logical{};Bytes state;};
bool apply(void* c,std::span<const std::uint8_t> b){auto& core=*static_cast<Core*>(c);++core.applies;core.state.assign(b.begin(),b.end());core.logical=b[0];return true;}
bool reject(void* c,std::span<const std::uint8_t>){++static_cast<Core*>(c)->applies;return false;}
bool throwApply(void*,std::span<const std::uint8_t>){throw std::runtime_error("synthetic");}
struct Pair {
    Session h,g;Core hc,gc;std::uint64_t id=1;unsigned transportCopies{};
    explicit Pair(std::size_t n=4096,unsigned delay=0):h(config(1,n,delay)),g(config(2,n,delay)){hc.state=Bytes(n,19);hc.state[0]=0;gc.state=Bytes(n,0);}
    void accept(Session& s,unsigned remote,Bytes b){check(!b.empty(),"packet exists");check(b.size()<=MaxPacket,"bounded packet");
        auto n=id++;auto r=s.deliver(std::uint8_t(remote),n,b);check(r==Result::Ok||r==Result::Duplicate||r==Result::Superseded,"deliver valid packet");
        check(s.copied(n),"real bounded-copy receipt");++transportCopies;eq(s.releaseReceipt(n),Result::Ok,"outer ACK release");}
    void pump(){for(unsigned turn=0;turn<100000;++turn){bool any=false;auto b=h.takeOutgoing();if(!b.empty()){any=true;accept(g,1,std::move(b));}
        b=g.takeOutgoing();if(!b.empty()){any=true;accept(h,2,std::move(b));}if(!any)return;}throw std::runtime_error("pump bound");}
    void clearEvents(){Commit c;while(h.takeCommit(c)){}while(g.takeCommit(c)){}}
    void paused(unsigned epoch,unsigned serial){eq(h.control(epoch,serial,true,true),Result::Ok,"host pause request");eq(g.control(epoch,serial,true,true),Result::Ok,"guest pause request");
        check(!h.status().pause.valid&&!g.status().pause.valid,"IO does not fabricate CPU ACK");
        eq(h.ownerCheckpoint(),Result::Paused,"host actual checkpoint");eq(g.ownerCheckpoint(),Result::Paused,"guest actual checkpoint");}
    void resuming(unsigned epoch,unsigned serial){eq(h.control(epoch,serial,false,true),Result::Ok,"host exact resume control");eq(g.control(epoch,serial,false,true),Result::Ok,"guest exact resume control");
        eq(h.resume(epoch,serial),Result::Wait,"cannot resume before owner ACK latest revision");
        eq(h.ownerCheckpoint(),Result::Paused,"host serial confirmed idle");eq(g.ownerCheckpoint(),Result::Paused,"guest serial confirmed idle");
        eq(h.resume(epoch,serial),Result::Ok,"host resumes exact permit");eq(g.resume(epoch,serial),Result::Ok,"guest resumes exact permit");}
    void snapshot(){auto previousApplies=gc.applies;eq(h.ownerPublishState(hc.state,h.status().nextFrame),Result::Ok,"actual host state exported");pump();
        check(!g.status().stateReady&&gc.applies==previousApplies,"transport copy is not state apply");
        eq(g.ownerCheckpoint(),Result::Paused,"guest idle before apply");eq(g.ownerApplyState(apply,&gc),Result::Ok,"guest actual state callback");pump();clearEvents();}
    void init(){check(!h.status().pause.valid&&!g.status().pause.valid,"no initial fakeReady");paused(1,1);snapshot();
        check(h.drained()&&g.drained(),"all real initial receipts/queues drained");resuming(1,2);}
    void staged(unsigned hp,unsigned gp){check(h.needsLocalSample()&&g.needsLocalSample(),"sample original callbacks once per next frame");
        eq(h.ownerSampleLocal(std::uint16_t(hp)),Result::Ok,"host original input sampled");eq(g.ownerSampleLocal(std::uint16_t(gp)),Result::Ok,"guest original input sampled");
        check(!h.needsLocalSample()&&!g.needsLocalSample(),"no duplicate original input poll");pump();}
    void advance(unsigned hp,unsigned gp){staged(hp,gp);Lease a,b;
        eq(h.ownerBegin(a),Result::Ok,"host original owner lease");eq(g.ownerBegin(b),Result::Wait,"guest cannot advance before host actual run");
        check(h.takeOutgoing().empty(),"no canonical FRAME sent before authoritative execution");
        Commit c;check(!h.takeCommit(c)&&!g.takeCommit(c),"no Executed on network-copy or ownerBegin");
        ++hc.runs;++hc.logical;hc.state[0]=std::uint8_t(hc.logical);eq(h.ownerComplete(a),Result::Ok,"host actual post-retro_run");pump();
        eq(g.ownerBegin(b),Result::Ok,"guest original owner lease after host execution");
        check(a.frame==b.frame&&a.frame.pads[0]==hp&&a.frame.pads[1]==gp,"canonical pads identical in both original cores");
        ++gc.runs;++gc.logical;gc.state[0]=std::uint8_t(gc.logical);eq(g.ownerComplete(b),Result::Ok,"guest actual post-retro_run");
        pump();unsigned executions=0;while(h.takeCommit(c)){check(c.outcome==Outcome::Executed,"host observed only executed after run");++executions;}
        while(g.takeCommit(c)){check(c.outcome==Outcome::Executed,"guest observed only executed after run");++executions;}
        check(executions==4,"two local and two peer gameplay commits");check(h.drained()&&g.drained(),"frame mailboxes/outer receipts/commits drain");}
};
void hashes(){check(hex(sha256({}))=="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","SHA empty vector");
    Bytes abc{'a','b','c'};check(hex(sha256(abc))=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","SHA abc vector");
    Bytes million(1000000,'a');check(hex(sha256(million))=="cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0","SHA million a vector");}
void configuration(){for(unsigned slot:{0u,3u,255u}){bool threw=false;try{Session s(config(slot));}catch(const std::invalid_argument&){threw=true;}check(threw,"no unsupported port topology");}
    for(auto n:{std::size_t(0),MaxState+1}){bool threw=false;try{Session s(config(1,n));}catch(const std::invalid_argument&){threw=true;}check(threw,"exact state size bounded");}}
void lockstep(){Pair p;p.init();for(unsigned i=0;i<500;++i)p.advance((i*733)&StandardPadBits,(i*317)&StandardPadBits);
    check(p.hc.runs==500&&p.gc.runs==500&&p.h.status().nextFrame==500&&p.g.status().nextFrame==500,"500 real fixture executions exact");
    eq(p.h.control(1,1,true,true),Result::Stale,"old serial cannot pause new permit");eq(p.h.resume(1,1),Result::Stale,"old permit rejected");
    Result wrong=Result::Ok;std::thread t([&]{wrong=p.h.ownerCheckpoint();});t.join();eq(wrong,Result::WrongOwner,"wrong thread cannot confirm CPU pause");}
void copiesAndParser(){Pair p;p.init();eq(p.h.ownerSampleLocal(7),Result::Ok,"host input staged");eq(p.g.ownerSampleLocal(11),Result::Ok,"guest input staged");
    auto in=p.g.takeOutgoing();check(!in.empty(),"input packet");
    for(std::size_t n=0;n<in.size();++n)eq(p.h.deliver(2,p.id++,std::span(in).first(n)),Result::Invalid,"every truncated INPUT rejected");
    for(unsigned off:{0u,1u,2u,3u,4u,5u,6u,7u,9u,10u,11u}){auto b=in;b[off]^=0x40;eq(p.h.deliver(2,p.id++,b),Result::Invalid,"framing identity/reserved/length guarded");}
    auto invalid=in;invalid[36]=0x80;eq(p.h.deliver(2,p.id++,invalid),Result::Invalid,"Standard controller rejects analog/L3/R3 bits");
    auto id=p.id++;eq(p.h.deliver(2,id,in),Result::Ok,"copied INPUT");check(p.h.copied(id),"INPUT transport ACK before run is copy only");
    Commit c;check(!p.h.takeCommit(c),"no INPUT gameplay ACK before incorporation+execution");
    eq(p.h.deliver(2,id,in),Result::Duplicate,"idempotent unique ID");invalid=in;invalid[37]^=1;eq(p.h.deliver(2,id,invalid),Result::Invalid,"same receipt ID conflict rejected");
    eq(p.h.releaseReceipt(id),Result::Ok,"receipt release");eq(p.h.deliver(2,id,in),Result::Duplicate,"bounded retired ID replay exact");
    eq(p.h.releaseReceipt(id),Result::Duplicate,"retired copied receipt release remains idempotent");
    eq(p.h.releaseReceipt(UINT64_MAX),Result::Invalid,"unknown receipt release cannot pretend consumed");
    Lease hostLease;eq(p.h.ownerBegin(hostLease),Result::Ok,"host canonical real lease");
    check(p.h.takeOutgoing().empty(),"host has not completed no FRAME exists");
    ++p.hc.runs;eq(p.h.ownerComplete(hostLease),Result::Ok,"host real completion emits FRAME");
    auto frame=p.h.takeOutgoing();p.accept(p.g,1,frame);Lease lease;eq(p.g.ownerBegin(lease),Result::Ok,"frame waits for owner");
    auto tampered=lease;tampered.frame.pads[0]^=1;eq(p.g.ownerComplete(tampered),Result::Invalid,"lease cannot change inputs");
    check(p.g.status().nextFrame==0,"begin/tampered complete never advances cursor");
    eq(p.g.ownerAbort(lease,"CORE_EXCEPTION"),Result::Failed,"failed original frame releases owner lease safely");
    check(!p.g.status().inFrame&&!p.g.status().closed,"failed lease is paused not deadlocked or stopped");
    while(p.g.takeCommit(c))check(c.outcome!=Outcome::Executed,"abort never emits Executed");
    eq(p.g.ownerClose(),Result::HumanRequired,"failure not human command");eq(p.g.authorizeHumanExit(),Result::Ok,"explicit human authorization");eq(p.g.ownerClose(),Result::Ok,"actual owner shuts down");}
void epochRecovery(){Pair p;p.init();p.staged(3,9);Lease a;eq(p.h.ownerBegin(a),Result::Ok,"host begins before connection pause");
    eq(p.h.control(2,3,true,true),Result::Ok,"pause request during real frame");check(!p.h.status().pause.valid,"inflight core is not idle");eq(p.h.ownerCheckpoint(),Result::Wait,"owner checkpoint cannot ACK live lease");
    ++p.hc.runs;++p.hc.logical;p.hc.state[0]=1;eq(p.h.ownerComplete(a),Result::Ok,"real old-epoch frame returns");
    check(p.h.status().pause.valid&&p.h.status().nextFrame==1,"pause ACK only after old real frame");
    eq(p.g.control(2,3,true,true),Result::Ok,"guest epoch invalidates unexecuted old frame");eq(p.g.ownerCheckpoint(),Result::Paused,"guest original core stays paused");p.pump();p.clearEvents();
    eq(p.h.ownerPublishState(p.hc.state,0),Result::Invalid,"host cannot invent state cursor");
    eq(p.h.ownerPublishState(p.hc.state,1),Result::Ok,"host exports actual last state");p.pump();
    eq(p.g.ownerCheckpoint(),Result::Paused,"guest idle for recovery snapshot");eq(p.g.ownerApplyState(apply,&p.gc),Result::Ok,"behind guest recovers by actual state callback");p.pump();p.clearEvents();
    check(p.gc.runs==0&&p.gc.logical==1&&p.g.status().nextFrame==1,"snapshot supersedes pending frame without fake execution");
    check(p.h.drained()&&p.g.drained(),"recovery can drain with CPU paused");p.resuming(2,4);p.advance(19,27);}
void stateGuards(){for(unsigned mode=0;mode<3;++mode){Pair p;p.paused(1,1);eq(p.h.ownerPublishState(p.hc.state,0),Result::Ok,"state source");
        bool corrupt=false;for(;;){auto b=p.h.takeOutgoing();if(b.empty())break;if(mode==0&&b[8]==std::uint8_t(Kind::StateChunk)&&!corrupt){b[40]^=1;corrupt=true;}p.accept(p.g,1,b);}
        eq(p.g.ownerCheckpoint(),Result::Paused,"real state owner idle");
        auto fn=mode==1?reject:mode==2?throwApply:apply;eq(p.g.ownerApplyState(fn,&p.gc),Result::Failed,"hash/rejected/exception state never READY");
        check(!p.g.status().stateReady&&p.g.status().failed&&!p.g.status().closed,"state failure paused no automatic close");
        if(mode==0)check(p.gc.applies==0,"corrupt hash rejected before original unsafe decoder");
        p.pump();check(p.h.status().failed&&!p.h.status().closed,"peer actual state failure freezes host");}}
void boundsAndReplay(){Pair p;p.init();eq(p.h.ownerSampleLocal(1),Result::Ok,"host sample bounded");eq(p.g.ownerSampleLocal(2),Result::Ok,"guest sample bounded");auto b=p.g.takeOutgoing();
    for(unsigned i=0;i<ReceiptWindow;++i){auto id=10000+i;eq(p.h.deliver(2,id,b),Result::Ok,"bounded copies retained");check(p.h.copied(id),"receipt retained");}
    eq(p.h.deliver(2,20000,b),Result::Backpressure,"receipt window cannot grow unbounded");check(!p.h.copied(20000),"backpressure is not consumption");
    eq(p.h.releaseReceipt(10000),Result::Ok,"real receipt release restores capacity");eq(p.h.deliver(2,20000,b),Result::Ok,"copy after capacity released");
    auto over=b;over.resize(MaxPacket+1);eq(p.h.deliver(2,30000,over),Result::Invalid,"oversized DATA guarded");}
void maxState(){Pair p(MaxState);p.paused(1,1);p.snapshot();check(p.gc.state.size()==MaxState,"largest permitted state bounded and exact");check(p.h.drained()&&p.g.drained(),"max snapshot drains while paused without run");}
void staleRequest(){Pair p;p.init();eq(p.g.requestState(),Result::Ok,"guest constructs real request");auto old=p.g.takeOutgoing();
    p.paused(2,3);eq(p.h.ownerPublishState(p.hc.state,0),Result::Ok,"new epoch real state");p.pump();
    eq(p.g.ownerCheckpoint(),Result::Paused,"new guest state owner checkpoint");eq(p.g.ownerApplyState(apply,&p.gc),Result::Ok,"new guest state applied");p.pump();p.clearEvents();p.resuming(2,4);
    auto id=p.id++;eq(p.h.deliver(2,id,old),Result::Superseded,"old REQUEST_STATE replay copied and superseded");
    check(p.h.copied(id)&&!p.h.status().paused&&!p.h.stateRequested(),"old request cannot pause current game");}
void revisionBarrier(){Pair p;p.init();Lease a;
    eq(p.h.control(1,3,false,true),Result::Ok,"running false revision revokes old permit");
    check(!p.h.status().pause.valid&&p.h.status().paused,"new false serial pauses without IO ACK");
    eq(p.h.ownerBegin(a),Result::Paused,"false revision cannot begin before owner ACK");
    eq(p.h.resume(1,3),Result::Wait,"false revision cannot resume before owner checkpoint");
    eq(p.h.ownerCheckpoint(),Result::Paused,"owner confirms new false revision");
    eq(p.h.resume(1,3),Result::Ok,"exact false revision resumes after real ACK");
    p.staged(11,17);eq(p.h.ownerBegin(a),Result::Ok,"host lease before revision");
    eq(p.h.control(1,4,false,true),Result::Ok,"false revision during real core run");
    check(!p.h.status().pause.valid,"live lease invalidates new ACK");
    eq(p.h.resume(1,4),Result::Wait,"cannot resume during old active core lease");
    eq(p.h.ownerCheckpoint(),Result::Wait,"checkpoint cannot certify active lease");
    ++p.hc.runs;eq(p.h.ownerComplete(a),Result::Ok,"real frame returns under revoked permit");
    check(p.h.status().pause.valid&&p.h.status().pause.controlSerial==4,"postrun ACK uses latest false serial");
    eq(p.h.resume(1,3),Result::Stale,"old serial cannot resume revoked permit");
    eq(p.h.resume(1,4),Result::Ok,"latest false serial explicit resume");
    eq(p.h.control(1,5,true,true),Result::Ok,"ordinary pause revision");
    eq(p.h.ownerCheckpoint(),Result::Paused,"pause owner ACK");
    eq(p.h.control(1,6,false,true),Result::Ok,"false revision from paused remains gated");
    check(!p.h.status().pause.valid&&p.h.status().paused,"paused new false serial no stale ACK");
    eq(p.h.resume(1,6),Result::Wait,"paused false serial needs fresh owner ACK");
    eq(p.h.ownerCheckpoint(),Result::Paused,"paused latest serial real ACK");
    eq(p.h.resume(1,6),Result::Ok,"paused false explicit resume after checkpoint");
}
struct NetworkResult {unsigned hostRuns{},guestRuns{};};
NetworkResult simulateNetwork(unsigned delay,unsigned rttMs,unsigned durationMs){
    Pair p(4096,delay);p.init();
    struct Flight {std::uint64_t due;bool toHost;Bytes packet;};
    std::deque<Flight> flight;std::uint64_t hostNext=0,guestNext=0;
    constexpr std::uint64_t period=16667;
    auto pad=[](std::uint64_t n,unsigned slot){return std::uint16_t(((n+1)*(slot==1?733:317))&StandardPadBits);};
    for(std::uint64_t now=0;now<std::uint64_t(durationMs)*1000;now+=100){
        while(!flight.empty()&&flight.front().due<=now){auto f=std::move(flight.front());flight.pop_front();p.accept(f.toHost?p.h:p.g,f.toHost?2:1,std::move(f.packet));}
        auto run=[&](Session& session,Core& core,std::uint64_t& next,unsigned slot){
            if(now<next)return;
            eq(session.ownerCheckpoint(),Result::Ok,"original owner responsive while waiting network inputs");
            const auto frame=session.status().nextFrame;
            if(session.needsLocalSample())eq(session.ownerSampleLocal(pad(frame,slot)),Result::Ok,"one real callback sample feeds future frame");
            Lease lease;auto result=session.ownerBegin(lease);
            if(result==Result::Wait)return;
            eq(result,Result::Ok,"scheduled original frame lease");
            for(unsigned port=0;port<2;++port)check(lease.frame.pads[port]==(frame<delay?0:pad(frame-delay,port+1)),"fixed delay binds original samples and neutral bootstrap exactly");
            ++core.runs;++core.logical;core.state[0]=std::uint8_t(core.logical);
            eq(session.ownerComplete(lease),Result::Ok,"simulated actual core returns");next=now+period;
        };
        run(p.h,p.hc,hostNext,1);run(p.g,p.gc,guestNext,2);
        check(p.gc.runs<=p.hc.runs,"guest cannot execute ahead of actual host snapshot cursor");
        for(bool toHost:{false,true})for(;;){auto b=(toHost?p.g:p.h).takeOutgoing();if(b.empty())break;flight.push_back({now+std::uint64_t(rttMs)*500,toHost,std::move(b)});}
        p.clearEvents();
    }
    check(!p.h.status().failed&&!p.g.status().failed,"bounded pipeline remains healthy under simulated latency");
    return {p.hc.runs,p.gc.runs};
}
void pipeline(){auto baseline=simulateNetwork(0,50,2000),delayed=simulateNetwork(4,50,2000),insufficient=simulateNetwork(4,150,2000);
    check(baseline.hostRuns<50,"zero delay exposes RTT-per-frame throughput limit");
    check(delayed.hostRuns>=117&&delayed.guestRuns>=115,"four-frame pipeline sustains near60 with synthetic50msRTT");
    check(insufficient.hostRuns<delayed.hostRuns,"fixed four frames cannot conceal arbitrary internet latency");
    std::cout<<"network_simulation delay0_rtt50_host="<<baseline.hostRuns<<" delay4_rtt50_host="<<delayed.hostRuns<<" delay4_rtt50_guest="<<delayed.guestRuns<<" delay4_rtt150_host="<<insufficient.hostRuns<<" durationMs=2000\n";
    Pair p(4096,4);p.init();eq(p.h.ownerSampleLocal(7),Result::Ok,"pipeline host sample");eq(p.g.ownerSampleLocal(11),Result::Ok,"pipeline guest sample");p.pump();
    Lease a;eq(p.h.ownerBegin(a),Result::Ok,"neutral bootstrap is actual canonical lease");check(a.frame.pads[0]==0&&a.frame.pads[1]==0,"neutral first pipeline inputs");
    ++p.hc.runs;++p.hc.logical;p.hc.state[0]=1;eq(p.h.ownerComplete(a),Result::Ok,"host neutral frame actually executed");p.pump();
    p.paused(1,3);check(p.h.stateRequested()&&p.g.stateRequested(),"pause with future inputs requests fresh authoritative state");
    p.snapshot();check(p.h.drained()&&p.g.drained(),"fresh state supersedes pipeline while paused without fake execution");
    p.resuming(1,4);check(p.h.needsLocalSample()&&p.g.needsLocalSample(),"recovered pipeline resamples future inputs");
    check(p.hc.runs==1&&p.gc.runs==0&&p.g.status().nextFrame==1,"snapshot aligns behind guest no fabricated retro_run");
    auto bad=config(1);bad.inputDelay=17;bool rejected=false;try{Session invalid(bad);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"pipeline bounded to16 within frame window");
}
void commitReplayAndAdmission(){Pair p;p.init();eq(p.h.ownerSampleLocal(7),Result::Ok,"host replay sample");eq(p.g.ownerSampleLocal(11),Result::Ok,"guest replay sample");
    auto input=p.g.takeOutgoing();p.accept(p.h,2,input);Lease a,b;
    eq(p.h.ownerBegin(a),Result::Ok,"host replay lease");++p.hc.runs;eq(p.h.ownerComplete(a),Result::Ok,"host replay actual run");
    p.pump();eq(p.g.ownerBegin(b),Result::Ok,"guest replay lease");++p.gc.runs;eq(p.g.ownerComplete(b),Result::Ok,"guest replay actual run");
    auto committed=p.g.takeOutgoing();p.accept(p.h,2,committed);auto id=p.id++;
    eq(p.h.deliver(2,id,committed),Result::Duplicate,"same gameplay COMMIT under new transport id idempotent");
    check(p.h.copied(id),"duplicate COMMIT retains real copied receipt");eq(p.h.releaseReceipt(id),Result::Ok,"duplicate COMMIT outer release");
    auto conflict=committed;conflict[37]=std::uint8_t(Outcome::Superseded);
    eq(p.h.deliver(2,p.id++,conflict),Result::Invalid,"same gameplay stamp conflicting COMMIT rejected");
    p.clearEvents();check(p.h.drained()&&p.g.drained(),"replay does not fabricate extra pending work");
    for(unsigned i=0;i<512;++i){p.accept(p.h,2,input);check(!p.h.takeOutgoing().empty(),"admitted historic response exists");}
    check(p.h.takeOutgoing().empty(),"pretest output drained");auto blocked=p.id++;
    eq(p.h.deliver(2,blocked,input),Result::Backpressure,"full gameplay event window applies before outbound admission");
    check(!p.h.copied(blocked)&&p.h.takeOutgoing().empty(),"backpressure neither copied nor leaked COMMIT output");
    Commit event;check(p.h.takeCommit(event),"consumer frees one classified event");
    eq(p.h.deliver(2,blocked,input),Result::Ok,"same unadmitted delivery retries after capacity");
    check(p.h.copied(blocked)&&!p.h.takeOutgoing().empty()&&p.h.status().nextFrame==1,"retry admits once without extra coreadvance");
}
void humanExit(){Pair p;p.init();eq(p.h.automaticStop("NETWORK_TIMEOUT"),Result::HumanRequired,"timeout cannot terminate");
    check(p.h.status().failed&&!p.h.status().closed,"automatic loss pauses instead of STOP");eq(p.h.ownerClose(),Result::HumanRequired,"STOP still human gated");
    eq(p.h.authorizeHumanExit(),Result::Ok,"human chooses close");eq(p.h.ownerClose(),Result::Ok,"owner closes after authorization");}
}
int main(){try{hashes();configuration();lockstep();copiesAndParser();epochRecovery();stateGuards();boundsAndReplay();maxState();staleRequest();revisionBarrier();pipeline();commitReplayAndAdmission();humanExit();
    std::cout<<"checks="<<checks<<"; result=passed; synthetic_owner_only=true\n";return 0;}
catch(const std::exception& e){std::cerr<<"FAILED after "<<checks<<": "<<e.what()<<'\n';return 1;}}
