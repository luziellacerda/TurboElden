// SPDX-License-Identifier: GPL-2.0-or-later
// Actual protocol event waits on IO threads, synthetic owner/state only.
#include "StationPsxProtocol.hpp"
#include <chrono>
#include <future>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <thread>
using namespace station::psx;
using Clock=std::chrono::steady_clock;
using Bytes=std::vector<std::uint8_t>;
namespace {
unsigned checks{};std::uint64_t id=1;
void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
void ok(Result result,const char* message){check(result==Result::Ok,message);}
bool apply(void*,std::span<const std::uint8_t> bytes){return bytes.size()==64;}
void transfer(Session& from,Session& to,unsigned remote){
    for(;;){auto b=from.takeOutgoing();if(b.empty())return;auto n=id++;ok(to.deliver(remote,n,b),"bounded copy");check(to.copied(n),"actual receipt");ok(to.releaseReceipt(n),"release receipt");}
}
double wake(Session& session,const std::function<void()>& produce,bool expected){
    std::promise<void> started;auto startedFuture=started.get_future();
    auto io=std::async(std::launch::async,[&]{started.set_value();return session.awaitOutgoing(100);});
    startedFuture.get();std::this_thread::sleep_for(std::chrono::milliseconds(5));
    auto now=Clock::now();produce();auto result=io.get();
    double ms=std::chrono::duration<double,std::milli>(Clock::now()-now).count();
    check(result==expected,"notification result matches actual queue/closed state");
    check(ms<80,"producer notification must release IO before idle timeout");return ms;
}
}
int main(){try{
    Digest identity{};identity[0]=17;Session host({1,1,64,identity,4}),guest({2,1,64,identity,4});
    for(auto* s:{&host,&guest}){ok(s->control(1,1,true,true),"pause control");check(s->ownerCheckpoint()==Result::Paused,"actual owner ACK");}
    auto start=Clock::now();check(!host.awaitOutgoing(100),"owner may never block in IO wait");
    check(std::chrono::duration<double,std::milli>(Clock::now()-start).count()<5,"owner guard returns immediately");
    auto empty=std::async(std::launch::async,[&]{auto at=Clock::now();bool ready=host.awaitOutgoing(20);return std::pair{ready,std::chrono::duration<double,std::milli>(Clock::now()-at).count()};}).get();
    check(!empty.first&&empty.second>=10&&empty.second<100,"empty bounded wait has no invented packet");
    double snapshot=wake(host,[&]{ok(host.ownerPublishState(Bytes(64,19),0),"publish actual synthetic snapshot");},true);
    check(host.status().nextFrame==0&&!host.takeOutgoing().empty(),"wake neither consumes snapshot nor advances owner");
    // The first header was deliberately read above; publish a new exact serial
    // and use a fresh pair for the complete apply/INPUT/FRAME path.
    Session h({1,1,64,identity,4}),g({2,1,64,identity,4});
    for(auto* s:{&h,&g}){ok(s->control(1,1,true,true),"fresh control");s->ownerCheckpoint();}
    ok(h.ownerPublishState(Bytes(64,23),0),"fresh state");transfer(h,g,1);g.ownerCheckpoint();
    double applied=wake(g,[&]{ok(g.ownerApplyState(apply,&g),"actual apply callback");},true);transfer(g,h,2);
    for(auto* s:{&h,&g}){ok(s->control(1,2,false,true),"PLAYING control");s->ownerCheckpoint();ok(s->resume(1,2),"exact permit after real ACK");}
    double input=wake(g,[&]{ok(g.ownerSampleLocal(7),"guest original input sample");},true);
    check(g.status().nextFrame==0,"outbound event never executes a core");transfer(g,h,2);
    double frame=wake(h,[&]{ok(h.ownerSampleLocal(11),"host original sample");Lease lease;ok(h.ownerBegin(lease),"host lease");ok(h.ownerComplete(lease),"actual synthetic completion");},true);
    check(h.status().nextFrame==1,"only owner completion advanced frame");transfer(h,g,1);
    double commit=wake(g,[&]{Lease lease;ok(g.ownerBegin(lease),"guest canonical lease");ok(g.ownerComplete(lease),"guest actual synthetic completion");},true);transfer(g,h,2);
    double closed=wake(h,[&]{ok(h.authorizeHumanExit(),"explicit synthetic human exit");h.ownerCheckpoint();ok(h.ownerClose(),"actual synthetic owner close");},false);
    check(h.takeOutgoing().empty()&&h.status().closed,"close wakes without fabricated data");
    std::cout<<"PASS outbound-wake checks="<<checks<<" snapshotMs="<<snapshot<<" appliedMs="<<applied<<" inputMs="<<input<<" frameMs="<<frame<<" commitMs="<<commit<<" closeMs="<<closed<<" syntheticOwner=true physicalGameplay=false\n";return 0;
}catch(const std::exception& error){std::cerr<<"FAIL "<<error.what()<<"\n";return 1;}}
