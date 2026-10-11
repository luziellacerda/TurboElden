// SPDX-License-Identifier: GPL-2.0-or-later
#include "StationPsxProtocol.hpp"
#include <algorithm>
#include <deque>
#include <map>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <thread>
#include <tuple>

namespace station::psx {
namespace {
constexpr std::size_t PayloadHeader=28, ChunkBytes=MaxPayload-PayloadHeader-4;
constexpr std::size_t CommitWindow=512, PendingOutputWindow=128;
using Bytes=std::vector<std::uint8_t>;
using Key=std::tuple<unsigned,std::uint64_t,std::uint64_t,std::uint64_t>;
Key key(Kind kind,Stamp s) {return {unsigned(kind),s.epoch,s.stateSerial,s.frame};}
void put16(Bytes& b,std::uint16_t n){b.push_back(std::uint8_t(n>>8));b.push_back(std::uint8_t(n));}
void put32(Bytes& b,std::uint32_t n){for(int i=3;i>=0;--i)b.push_back(std::uint8_t(n>>(i*8)));}
void put64(Bytes& b,std::uint64_t n){for(int i=7;i>=0;--i)b.push_back(std::uint8_t(n>>(i*8)));}
std::uint16_t get16(std::span<const std::uint8_t> b){return(std::uint16_t(b[0])<<8)|b[1];}
std::uint32_t get32(std::span<const std::uint8_t> b){std::uint32_t n=0;for(auto v:b.first(4))n=(n<<8)|v;return n;}
std::uint64_t get64(std::span<const std::uint8_t> b){std::uint64_t n=0;for(auto v:b.first(8))n=(n<<8)|v;return n;}
Bytes packet(std::uint8_t from,Kind k,Stamp s,std::span<const std::uint8_t> body={}){
    Bytes p{'P','X','L','1',from,std::uint8_t(3-from),0,0};
    p.push_back(std::uint8_t(k));p.push_back(3);p.push_back(2);p.push_back(0);
    put64(p,s.epoch);put64(p,s.stateSerial);put64(p,s.frame);
    p.insert(p.end(),body.begin(),body.end());auto size=p.size()-8;
    p[6]=std::uint8_t(size>>8);p[7]=std::uint8_t(size);return p;
}
std::string category(const char* s){
    if(!s)return "NATIVE_FAILURE";std::string out;
    for(;*s&&out.size()<64;++s)if((*s>='A'&&*s<='Z')||(*s>='0'&&*s<='9')||*s=='_')out+=*s;
    return out.empty()?"NATIVE_FAILURE":out;
}
}
struct Session::Impl {
    explicit Impl(Config v):config(v),epoch(v.epoch){}
    struct Inputs {std::array<std::uint16_t,2> pads{};unsigned present{};bool remoteInput{};};
    struct State {Stamp stamp;Digest digest{};Bytes bytes;std::size_t received{};bool end{};};
    struct Export {Stamp stamp;Digest digest{};Bytes bytes;std::size_t offset{};unsigned phase{};};
    Config config;mutable std::mutex mutex;std::thread::id owner{};bool hasOwner{};
    std::uint64_t epoch{},controlSerial{},stateSerial{},nextFrame{},nextLease{1};
    bool controlPause{true},visible{true},permit{},paused{true},stateReady{},inFrame{},applying{},
        human{},closed{},stateRequest{true},peerApplied{},pipelinePrimed{};
    std::string failure;PauseAck ack{};Lease executing{};
    Digest lastStateDigest{};Stamp lastStateStamp{};
    std::map<std::uint64_t,Inputs> inputs;
    std::map<std::uint64_t,Frame> frames;
    std::deque<Frame> history;
    std::map<std::uint64_t,Digest> receipts;
    std::deque<std::pair<std::uint64_t,Digest>> retired;
    std::deque<Bytes> outgoing,pendingOutput;std::size_t outgoingBytes{};
    std::map<Key,bool> pendingCommits;
    std::deque<Commit> commitEvents;
    std::deque<std::pair<Key,Outcome>> commitHistory;
    std::optional<State> incomingState;std::optional<Export> exportState;
    Result ownerLocked(){
        if(!hasOwner){owner=std::this_thread::get_id();hasOwner=true;}
        return owner==std::this_thread::get_id()?Result::Ok:Result::WrongOwner;
    }
    void failLocked(const char* why){if(failure.empty())failure=category(why);permit=false;paused=true;stateReady=false;ack.valid=false;}
    bool queue(Bytes b){
        if(outgoingBytes+b.size()<=LinkWindow){outgoingBytes+=b.size();outgoing.push_back(std::move(b));return true;}
        if(pendingOutput.size()>=PendingOutputWindow)return false;
        pendingOutput.push_back(std::move(b));return true;
    }
    bool event(Commit c){if(commitEvents.size()>=CommitWindow)return false;commitEvents.push_back(c);return true;}
    bool sendCommit(Kind kind,Outcome result,Stamp s){
        // Admission is transactional: backpressure must not leak a packet.
        if(commitEvents.size()>=CommitWindow)return false;
        const std::array<std::uint8_t,2> body{std::uint8_t(kind),std::uint8_t(result)};
        if(!queue(packet(config.localSlot,Kind::Commit,s,body)))return false;
        return event({kind,result,s});
    }
    void supersedeInbox(){
        // Each drop is classified, never reported as an executed frame.
        if(config.localSlot==2)for(auto& [n,f]:frames)
            if(!(inFrame&&executing.frame.stamp==f.stamp)&&!sendCommit(Kind::Frame,Outcome::Superseded,f.stamp))failLocked("COMMIT_BACKPRESSURE");
        if(config.localSlot==1)for(auto& [n,row]:inputs)if(row.remoteInput&&!(inFrame&&executing.frame.stamp.frame==n))
            if(!sendCommit(Kind::Input,Outcome::Superseded,{epoch,stateSerial,n}))failLocked("COMMIT_BACKPRESSURE");
        frames.clear();inputs.clear();
    }
    void supersedeLedger(std::uint64_t keepSerial){
        for(auto it=pendingCommits.begin();it!=pendingCommits.end();){
            auto [kind,e,s,f]=it->first;
            if(s<keepSerial){if(!event({Kind(kind),Outcome::Superseded,{e,s,f}}))failLocked("COMMIT_BACKPRESSURE");it=pendingCommits.erase(it);}
            else ++it;
        }
    }
    void ackLocked(){
        ack={epoch,controlSerial,nextFrame,stateSerial,
             hasOwner&&!inFrame&&!applying&&!closed&&paused&&controlSerial!=0};
    }
    bool sampleTarget(std::uint64_t& target)const{
        if(nextFrame>UINT64_MAX-config.inputDelay)return false;
        target=nextFrame+config.inputDelay;return target!=UINT64_MAX;
    }
    bool prime(){
        if(pipelinePrimed)return true;
        if(nextFrame>UINT64_MAX-config.inputDelay)return false;
        for(std::uint32_t i=0;i<config.inputDelay;++i){
            auto& row=inputs[nextFrame+i];row.pads={0,0};
            row.present=config.localSlot==1?3u:2u;row.remoteInput=false;
        }
        pipelinePrimed=true;return true;
    }
    bool inWindow(std::uint64_t n)const{return n>=nextFrame&&n-nextFrame<FrameWindow;}
    bool historic(Frame f)const{return std::find(history.begin(),history.end(),f)!=history.end();}
    bool historicInput(Stamp s,std::uint16_t pad)const{
        for(const auto& f:history)if(f.stamp==s&&f.pads[1]==pad)return true;return false;
    }
    Result canonical(){
        if(config.localSlot!=1||!stateReady||stateRequest||inFrame)return Result::Wait;
        auto it=inputs.find(nextFrame);if(it==inputs.end()||it->second.present!=3)return Result::Wait;
        Frame f{{epoch,stateSerial,nextFrame},it->second.pads};
        if(frames.contains(nextFrame))return frames[nextFrame]==f?Result::Duplicate:Result::Invalid;
        // A canonical lease is local until the host's actual retro_run completes.
        // A guest can never execute ahead of the authoritative host state cursor.
        frames.emplace(nextFrame,f);return Result::Ok;
    }
};
Session::Session(Config c){
    if(c.localSlot<1||c.localSlot>2||c.epoch==0||c.epoch>MaxEpoch||c.stateBytes==0||c.stateBytes>MaxState||c.inputDelay>16||
       std::all_of(c.identity.begin(),c.identity.end(),[](auto b){return b==0;}))
        throw std::invalid_argument("PSX exact two-port configuration");
    p_=std::make_unique<Impl>(c);
}
Session::~Session()=default;
Result Session::control(std::uint64_t epoch,std::uint64_t serial,bool pause,bool visible){
    auto& p=*p_;std::lock_guard lock(p.mutex);
    if(p.closed)return Result::Closed;
    if(!epoch||epoch>MaxEpoch||!serial||serial>std::uint64_t(INT64_MAX)||epoch<p.epoch||serial<p.controlSerial)return Result::Stale;
    if(serial==p.controlSerial)return epoch==p.epoch&&pause==p.controlPause&&visible==p.visible?Result::Duplicate:Result::Invalid;
    const bool pausedPipeline=pause&&p.config.inputDelay!=0&&(p.permit||p.inFrame||!p.inputs.empty());
    if(epoch!=p.epoch){p.supersedeInbox();p.epoch=epoch;p.stateRequest=true;p.peerApplied=false;
        p.incomingState.reset();p.exportState.reset();p.permit=false;p.paused=true;}
    if(pausedPipeline){p.stateRequest=true;p.peerApplied=false;}
    p.controlSerial=serial;p.controlPause=pause;p.visible=visible;p.ack.valid=false;
    // Every new authenticated revision revokes the old execution permit,
    // including pause=false. Resume requires an actual owner ACK of this serial.
    p.permit=false;p.paused=true;
    return Result::Ok;
}
Result Session::resume(std::uint64_t epoch,std::uint64_t serial){
    auto& p=*p_;std::lock_guard lock(p.mutex);
    if(p.closed)return Result::Closed;if(!p.failure.empty())return Result::Failed;
    if(epoch!=p.epoch||serial!=p.controlSerial||p.controlPause||!p.visible)return Result::Stale;
    if(!p.ack.valid||p.ack.epoch!=epoch||p.ack.controlSerial!=serial||p.inFrame||p.applying||!p.stateReady||
       p.incomingState||p.stateRequest||(p.config.localSlot==1&&!p.peerApplied))return Result::Wait;
    if(!p.prime()){p.failLocked("PIPELINE_OVERFLOW");return Result::Failed;}
    p.permit=true;p.paused=false;p.ack.valid=false;p.canonical();return Result::Ok;
}
Result Session::ownerCheckpoint(){
    auto& p=*p_;std::lock_guard lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(p.closed)return Result::Closed;if(p.inFrame||p.applying)return Result::Wait;
    if(p.human)return Result::HumanRequired;
    p.paused=!p.permit||p.controlPause||!p.visible||!p.stateReady||p.stateRequest||!p.failure.empty();
    if(p.paused)p.ackLocked();else p.ack.valid=false;
    return !p.failure.empty()?Result::Failed:(p.paused?Result::Paused:Result::Ok);
}
bool Session::needsLocalSample()const{
    auto& p=*p_;std::lock_guard lock(p.mutex);
    std::uint64_t target=0;if(!p.sampleTarget(target))return false;
    auto it=p.inputs.find(target);return !p.closed&&!p.inFrame&&!p.applying&&p.stateReady&&!p.paused&&
        (it==p.inputs.end()||!(it->second.present&(1u<<(p.config.localSlot-1))));
}
Result Session::ownerSampleLocal(std::uint16_t bits){
    auto& p=*p_;std::lock_guard lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(bits&~StandardPadBits)return Result::Invalid;if(p.closed)return Result::Closed;
    if(p.paused||!p.stateReady||p.inFrame||p.applying)return Result::Paused;
    std::uint64_t target=0;if(!p.sampleTarget(target)){p.failLocked("PIPELINE_OVERFLOW");return Result::Failed;}
    auto& row=p.inputs[target];auto bit=1u<<(p.config.localSlot-1);
    if(row.present&bit)return Result::Duplicate; // original poll must NOT repeat.
    if(p.config.localSlot==2){Bytes b;put16(b,bits);
        if(!p.queue(packet(2,Kind::Input,{p.epoch,p.stateSerial,target},b)))return Result::Backpressure;
        p.pendingCommits.emplace(key(Kind::Input,{p.epoch,p.stateSerial,target}),false);}
    row.pads[p.config.localSlot-1]=bits;row.present|=bit;
    if(p.config.localSlot!=1)return Result::Ok;
    auto c=p.canonical();return c==Result::Wait||c==Result::Duplicate?Result::Ok:c;
}
Result Session::ownerBegin(Lease& lease){
    auto& p=*p_;std::lock_guard lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(p.closed)return Result::Closed;if(!p.failure.empty())return Result::Failed;
    if(p.paused||!p.permit||p.controlPause||!p.visible||!p.stateReady||p.stateRequest)return Result::Paused;
    if(p.inFrame||p.applying)return Result::Wait;
    if(p.pendingOutput.size()>PendingOutputWindow-4||p.commitEvents.size()>CommitWindow-4)return Result::Backpressure;
    std::uint64_t target=0;if(!p.sampleTarget(target)){p.failLocked("PIPELINE_OVERFLOW");return Result::Failed;}
    auto local=p.inputs.find(target);
    if(local==p.inputs.end()||!(local->second.present&(1u<<(p.config.localSlot-1))))return Result::Wait;
    auto it=p.frames.find(p.nextFrame);if(it==p.frames.end())return Result::Wait;
    if(it->second.stamp.epoch!=p.epoch||it->second.stamp.stateSerial!=p.stateSerial)return Result::Stale;
    if(p.nextLease==UINT64_MAX){p.failLocked("LEASE_OVERFLOW");return Result::Failed;}
    lease={it->second,p.nextLease++};p.executing=lease;p.inFrame=true;p.ack.valid=false;return Result::Ok;
}
Result Session::ownerComplete(const Lease& lease){
    auto& p=*p_;std::lock_guard lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(!p.inFrame||lease!=p.executing)return Result::Invalid;
    p.inFrame=false;p.history.push_back(lease.frame);if(p.history.size()>FrameWindow*2)p.history.pop_front();
    const auto consumed=p.inputs.find(lease.frame.stamp.frame);
    const bool remoteInput=consumed!=p.inputs.end()&&consumed->second.remoteInput;
    p.frames.erase(lease.frame.stamp.frame);p.inputs.erase(lease.frame.stamp.frame);
    if(p.nextFrame==UINT64_MAX){p.failLocked("FRAME_OVERFLOW");return Result::Failed;}
    ++p.nextFrame;
    if(p.config.localSlot==1){
        Bytes pads;for(auto bits:lease.frame.pads)put16(pads,bits);
        if(!p.queue(packet(1,Kind::Frame,lease.frame.stamp,pads))){p.failLocked("FRAME_BACKPRESSURE");return Result::Failed;}
        p.pendingCommits.emplace(key(Kind::Frame,lease.frame.stamp),false);
    }
    const auto kind=p.config.localSlot==1?Kind::Input:Kind::Frame;
    const bool committed=p.config.localSlot==2||remoteInput?
        p.sendCommit(kind,Outcome::Executed,lease.frame.stamp):
        p.event({Kind::Frame,Outcome::Executed,lease.frame.stamp});
    if(!committed){p.failLocked("COMMIT_BACKPRESSURE");return Result::Failed;}
    p.canonical();
    // An epoch/pause request arriving during retro_run receives ACK only here.
    if(!p.permit||p.controlPause||!p.visible||p.stateRequest||!p.failure.empty()){p.paused=true;p.ackLocked();}
    return !p.failure.empty()?Result::Failed:Result::Ok;
}
Result Session::ownerAbort(const Lease& lease,const char* why){
    auto& p=*p_;std::lock_guard lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(!p.inFrame||lease!=p.executing)return Result::Invalid;
    p.inFrame=false;p.failLocked(why);p.frames.clear();p.inputs.clear();
    p.sendCommit(p.config.localSlot==1?Kind::Input:Kind::Frame,Outcome::OwnerFailed,lease.frame.stamp);
    p.ackLocked();return Result::Failed; // never increments nextFrame or Executed.
}
Result Session::ownerPublishState(Bytes bytes,std::uint64_t nextFrame){
    auto& p=*p_;std::lock_guard lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(p.config.localSlot!=1||bytes.size()!=p.config.stateBytes)return Result::Invalid;
    if(p.closed)return Result::Closed;if(!p.failure.empty())return Result::Failed;
    if(!p.paused||p.inFrame||p.applying||!p.ack.valid||p.exportState)return Result::Wait;
    if(nextFrame!=p.nextFrame)return Result::Invalid; // must be the actual core cursor.
    if(p.stateSerial==UINT64_MAX){p.failLocked("STATE_SERIAL_OVERFLOW");return Result::Failed;}
    p.supersedeInbox();++p.stateSerial;auto stamp=Stamp{p.epoch,p.stateSerial,nextFrame};
    auto digest=sha256(bytes);p.lastStateDigest=digest;p.lastStateStamp=stamp;
    p.exportState=Impl::Export{stamp,digest,std::move(bytes),0,0};
    p.pipelinePrimed=false;p.stateReady=true;p.peerApplied=false;p.stateRequest=false;p.ackLocked();return Result::Ok;
}
Result Session::ownerApplyState(ApplyState apply,void* core){
    auto& p=*p_;std::unique_lock lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(p.closed)return Result::Closed;if(!p.failure.empty())return Result::Failed;
    if(p.config.localSlot!=2||!apply||!core)return Result::Invalid;
    if(!p.paused||p.inFrame||p.applying||!p.ack.valid||!p.incomingState||!p.incomingState->end)return Result::Wait;
    auto state=std::move(*p.incomingState);p.incomingState.reset();p.applying=true;p.ack.valid=false;
    lock.unlock();bool ok=false;
    try{ok=sha256(state.bytes)==state.digest&&apply(core,state.bytes);}catch(...){ok=false;}
    lock.lock();p.applying=false;
    if(!ok){p.failLocked("STATE_REJECTED");p.sendCommit(Kind::StateEnd,Outcome::OwnerFailed,state.stamp);p.ackLocked();return Result::Failed;}
    if(state.stamp.epoch!=p.epoch){p.stateReady=false;p.stateRequest=true;p.permit=false;p.paused=true;
        p.sendCommit(Kind::StateEnd,Outcome::Superseded,state.stamp);p.ackLocked();return Result::Superseded;}
    p.stateSerial=state.stamp.stateSerial;p.nextFrame=state.stamp.frame;p.lastStateDigest=state.digest;p.lastStateStamp=state.stamp;
    p.supersedeLedger(p.stateSerial);p.pipelinePrimed=false;p.stateReady=true;p.stateRequest=false;
    if(!p.sendCommit(Kind::StateEnd,Outcome::AppliedState,state.stamp)){p.failLocked("COMMIT_BACKPRESSURE");return Result::Failed;}
    p.ackLocked();return Result::Ok;
}
bool Session::stateRequested()const{auto& p=*p_;std::lock_guard lock(p.mutex);return p.stateRequest&&!p.closed;}
Result Session::requestState(){
    auto& p=*p_;std::lock_guard lock(p.mutex);if(p.closed)return Result::Closed;
    p.permit=false;p.paused=true;p.stateRequest=true;p.ack.valid=false;
    if(p.config.localSlot==2&&!p.queue(packet(2,Kind::RequestState,{p.epoch,p.stateSerial,p.nextFrame})))return Result::Backpressure;
    return Result::Ok;
}
Result Session::authorizeHumanExit(){auto& p=*p_;std::lock_guard lock(p.mutex);if(p.closed)return Result::Closed;
    p.human=true;p.permit=false;p.paused=true;p.ack.valid=false;return Result::Ok;}
Result Session::automaticStop(const char* why){auto& p=*p_;std::lock_guard lock(p.mutex);if(p.closed)return Result::Closed;
    if(p.human)return Result::HumanRequired;p.failLocked(why);return Result::HumanRequired;}
Result Session::ownerClose(){auto& p=*p_;std::lock_guard lock(p.mutex);auto own=p.ownerLocked();if(own!=Result::Ok)return own;
    if(p.closed)return Result::Closed;if(!p.human)return Result::HumanRequired;if(p.inFrame||p.applying)return Result::Wait;
    p.closed=true;p.permit=false;p.paused=true;p.ack.valid=false;p.inputs.clear();p.frames.clear();p.receipts.clear();
    p.outgoing.clear();p.pendingOutput.clear();p.outgoingBytes=0;p.pendingCommits.clear();p.incomingState.reset();p.exportState.reset();return Result::Ok;}
Status Session::status()const{auto& p=*p_;std::lock_guard lock(p.mutex);return {p.ack,p.epoch,p.controlSerial,p.nextFrame,p.stateSerial,
    p.paused,p.stateReady,p.stateReady&&!p.stateRequest&&!p.incomingState&&
    (p.config.localSlot==2||p.peerApplied)&&p.failure.empty(),p.inFrame,p.applying,!p.failure.empty(),p.closed};}
std::string Session::failure()const{auto& p=*p_;std::lock_guard lock(p.mutex);return p.failure;}
bool Session::drained()const{auto& p=*p_;std::lock_guard lock(p.mutex);return !p.inFrame&&!p.applying&&p.inputs.empty()&&p.frames.empty()&&
    p.outgoing.empty()&&p.pendingOutput.empty()&&!p.exportState&&!p.incomingState&&p.pendingCommits.empty()&&p.receipts.empty();}

Result Session::deliver(std::uint8_t remote,std::uint64_t id,std::span<const std::uint8_t> b){
    auto& p=*p_;std::lock_guard lock(p.mutex);
    if(p.closed)return Result::Closed;
    if(remote!=3-p.config.localSlot||!id||b.size()<8+PayloadHeader||b.size()>MaxPacket||
       b[0]!='P'||b[1]!='X'||b[2]!='L'||b[3]!='1'||b[4]!=remote||b[5]!=p.config.localSlot||get16(b.subspan(6,2))!=b.size()-8||
       b[9]!=3||b[10]!=2||b[11]!=0)return Result::Invalid;
    const auto digest=sha256(b);
    if(auto it=p.receipts.find(id);it!=p.receipts.end())return it->second==digest?Result::Duplicate:Result::Invalid;
    for(auto& old:p.retired)if(old.first==id)return old.second==digest?Result::Duplicate:Result::Invalid;
    if(p.receipts.size()>=ReceiptWindow)return Result::Backpressure;
    Kind kind=Kind(b[8]);Stamp s{get64(b.subspan(12,8)),get64(b.subspan(20,8)),get64(b.subspan(28,8))};
    if(!s.epoch||s.epoch>MaxEpoch||s.frame==UINT64_MAX)return Result::Invalid;auto body=b.subspan(36);
    if(s.epoch>p.epoch)return Result::Wait; // authenticated control must arrive first.
    Result result=Result::Ok;
    if(kind==Kind::Input){
        if(p.config.localSlot!=1||body.size()!=2||!s.stateSerial)return Result::Invalid;
        auto bits=get16(body);if(bits&~StandardPadBits)return Result::Invalid;
        if(p.historicInput(s,bits)){if(!p.sendCommit(kind,Outcome::Executed,s))return Result::Backpressure;}
        else if(s.epoch<p.epoch||s.stateSerial<p.stateSerial||s.frame<p.nextFrame||p.stateRequest){
            if(!p.sendCommit(kind,Outcome::Superseded,s))return Result::Backpressure;result=Result::Superseded;}
        else {if(s.stateSerial!=p.stateSerial||!p.stateReady)return Result::Wait;
            if(!p.inWindow(s.frame))return Result::Backpressure;
            auto& row=p.inputs[s.frame];if((row.present&2)&&row.pads[1]!=bits)return Result::Invalid;
            row.pads[1]=bits;row.present|=2;row.remoteInput=true;auto c=p.canonical();if(c==Result::Backpressure)return c;}
    } else if(kind==Kind::Frame){
        if(p.config.localSlot!=2||body.size()!=4||!s.stateSerial)return Result::Invalid;
        Frame f{s,{get16(body.first(2)),get16(body.subspan(2,2))}};
        if((f.pads[0]|f.pads[1])&~StandardPadBits)return Result::Invalid;
        if(p.historic(f)){if(!p.sendCommit(kind,Outcome::Executed,s))return Result::Backpressure;}
        else if(s.epoch<p.epoch||s.stateSerial<p.stateSerial||s.frame<p.nextFrame||p.stateRequest){
            if(!p.sendCommit(kind,Outcome::Superseded,s))return Result::Backpressure;result=Result::Superseded;}
        else {if(s.stateSerial!=p.stateSerial||!p.stateReady)return Result::Wait;
            if(!p.inWindow(s.frame))return Result::Backpressure;
            auto it=p.inputs.find(s.frame);if(it==p.inputs.end()||!(it->second.present&2)||it->second.pads[1]!=f.pads[1])return Result::Invalid;
            if(auto old=p.frames.find(s.frame);old!=p.frames.end()&&old->second!=f)return Result::Invalid;
            p.frames.emplace(s.frame,f);}
    } else if(kind==Kind::StateBegin){
        if(p.config.localSlot!=2||body.size()!=68||!s.stateSerial)return Result::Invalid;
        if(!std::equal(p.config.identity.begin(),p.config.identity.end(),body.begin())||get32(body.subspan(64,4))!=p.config.stateBytes)return Result::Invalid;
        if(p.inFrame||p.applying)return Result::Wait;
        if(!p.paused)return Result::Paused;
        if(s.epoch<p.epoch||s.stateSerial<p.stateSerial){p.receipts.emplace(id,digest);return Result::Superseded;}
        Digest hash{};std::copy_n(body.begin()+32,32,hash.begin());
        if(p.incomingState){if(p.incomingState->stamp==s&&p.incomingState->digest==hash)result=Result::Duplicate;
            else if(s.stateSerial<=p.incomingState->stamp.stateSerial)return Result::Invalid;}
        if(result!=Result::Duplicate){if(s.stateSerial<=p.stateSerial)return Result::Invalid;
            p.supersedeInbox();p.permit=false;p.paused=true;p.stateReady=false;p.stateRequest=true;
            p.incomingState=Impl::State{s,hash,Bytes(p.config.stateBytes),0,false};p.ack.valid=false;}
    } else if(kind==Kind::StateChunk){
        if(p.config.localSlot!=2||body.size()<5||body.size()>ChunkBytes+4)return Result::Invalid;
        auto offset=get32(body);if(offset>p.config.stateBytes||body.size()-4>p.config.stateBytes-offset)return Result::Invalid;
        if(s.epoch<p.epoch||s.stateSerial<p.stateSerial){p.receipts.emplace(id,digest);return Result::Superseded;}
        if(!p.incomingState||p.incomingState->stamp!=s)return Result::Invalid;
        auto& state=*p.incomingState;auto data=body.subspan(4);
        if(offset>state.bytes.size()||data.size()>state.bytes.size()-offset)return Result::Invalid;
        if(offset<state.received){if(offset+data.size()>state.received||!std::equal(data.begin(),data.end(),state.bytes.begin()+offset))return Result::Invalid;result=Result::Duplicate;}
        else{if(offset!=state.received||state.end)return Result::Invalid;
            std::copy(data.begin(),data.end(),state.bytes.begin()+offset);state.received+=data.size();}
    } else if(kind==Kind::StateEnd){
        if(p.config.localSlot!=2||body.size()!=32)return Result::Invalid;
        if(s==p.lastStateStamp&&std::equal(p.lastStateDigest.begin(),p.lastStateDigest.end(),body.begin())){
            if(!p.sendCommit(Kind::StateEnd,Outcome::AppliedState,s))return Result::Backpressure;
            p.receipts.emplace(id,digest);return Result::Duplicate;}
        if(s.epoch<p.epoch||s.stateSerial<p.stateSerial){
            if(!p.sendCommit(Kind::StateEnd,Outcome::Superseded,s))return Result::Backpressure;
            p.receipts.emplace(id,digest);return Result::Superseded;}
        if(!p.incomingState||p.incomingState->stamp!=s)return Result::Invalid;
        auto& state=*p.incomingState;if(state.received!=state.bytes.size()||!std::equal(state.digest.begin(),state.digest.end(),body.begin()))return Result::Invalid;
        state.end=true;p.ack.valid=false;
    } else if(kind==Kind::RequestState){
        if(p.config.localSlot!=1||!body.empty())return Result::Invalid;
        if(s.epoch<p.epoch||s.stateSerial<p.stateSerial){p.receipts.emplace(id,digest);return Result::Superseded;}
        if(s.stateSerial>p.stateSerial)return Result::Invalid;
        p.stateRequest=true;p.permit=false;p.paused=true;p.ack.valid=false;
    } else if(kind==Kind::Commit){
        if(body.size()!=2)return Result::Invalid;
        auto k=Kind(body[0]);auto outcome=Outcome(body[1]);
        if((k!=Kind::Input&&k!=Kind::Frame&&k!=Kind::StateEnd)||
           (outcome!=Outcome::Executed&&outcome!=Outcome::Superseded&&outcome!=Outcome::AppliedState&&outcome!=Outcome::OwnerFailed)||
           (outcome==Outcome::AppliedState&&k!=Kind::StateEnd)||(outcome==Outcome::Executed&&k==Kind::StateEnd))return Result::Invalid;
        if((p.config.localSlot==1&&k==Kind::Input)||(p.config.localSlot==2&&k!=Kind::Input))return Result::Invalid;
        const auto commitKey=key(k,s);
        for(const auto& old:p.commitHistory)if(old.first==commitKey){
            if(old.second!=outcome)return Result::Invalid;
            p.receipts.emplace(id,digest);return Result::Duplicate;
        }
        if(p.commitEvents.size()>=CommitWindow)return Result::Backpressure;
        if(k==Kind::StateEnd){
            if(p.config.localSlot!=1)return Result::Invalid;
            if(s!=p.lastStateStamp){if(s.epoch<p.epoch||s.stateSerial<p.stateSerial){p.receipts.emplace(id,digest);return Result::Superseded;}return Result::Invalid;}
            if(outcome==Outcome::AppliedState){p.peerApplied=true;p.supersedeLedger(s.stateSerial);}
        } else {auto it=p.pendingCommits.find(key(k,s));
            if(it==p.pendingCommits.end()){
                if(s.epoch<p.epoch||s.stateSerial<p.stateSerial){p.receipts.emplace(id,digest);return Result::Superseded;}
                return Result::Invalid;}
            p.pendingCommits.erase(it);}
        if(!p.event({k,outcome,s}))return Result::Backpressure;
        p.commitHistory.emplace_back(commitKey,outcome);
        if(p.commitHistory.size()>FrameWindow*4)p.commitHistory.pop_front();
        if(outcome==Outcome::OwnerFailed)p.failLocked("REMOTE_OWNER_FAILURE");
    } else return Result::Invalid;
    p.receipts.emplace(id,digest);return result;
}
bool Session::copied(std::uint64_t id)const{auto& p=*p_;std::lock_guard lock(p.mutex);if(p.receipts.contains(id))return true;
    return std::any_of(p.retired.begin(),p.retired.end(),[&](auto& v){return v.first==id;});}
Result Session::releaseReceipt(std::uint64_t id){auto& p=*p_;std::lock_guard lock(p.mutex);auto it=p.receipts.find(id);
    if(it==p.receipts.end())return std::any_of(p.retired.begin(),p.retired.end(),[&](const auto& old){return old.first==id;})?Result::Duplicate:Result::Invalid;
    p.retired.emplace_back(id,it->second);if(p.retired.size()>ReceiptWindow)p.retired.pop_front();p.receipts.erase(it);return Result::Ok;}
Bytes Session::takeOutgoing(){
    auto& p=*p_;std::lock_guard lock(p.mutex);if(p.closed)return {};
    if(!p.outgoing.empty()){auto b=std::move(p.outgoing.front());p.outgoing.pop_front();p.outgoingBytes-=b.size();
        while(!p.pendingOutput.empty()&&p.outgoingBytes+p.pendingOutput.front().size()<=LinkWindow){
            p.outgoingBytes+=p.pendingOutput.front().size();p.outgoing.push_back(std::move(p.pendingOutput.front()));p.pendingOutput.pop_front();}return b;}
    if(!p.exportState)return {};
    auto& state=*p.exportState;Bytes body;Kind kind;
    if(state.phase==0){kind=Kind::StateBegin;body.insert(body.end(),p.config.identity.begin(),p.config.identity.end());body.insert(body.end(),state.digest.begin(),state.digest.end());put32(body,std::uint32_t(state.bytes.size()));state.phase=1;}
    else if(state.offset<state.bytes.size()){kind=Kind::StateChunk;put32(body,std::uint32_t(state.offset));auto count=std::min(ChunkBytes,state.bytes.size()-state.offset);
        body.insert(body.end(),state.bytes.begin()+state.offset,state.bytes.begin()+state.offset+count);state.offset+=count;}
    else {kind=Kind::StateEnd;body.assign(state.digest.begin(),state.digest.end());}
    auto b=packet(p.config.localSlot,kind,state.stamp,body);if(kind==Kind::StateEnd)p.exportState.reset();return b;
}
bool Session::takeCommit(Commit& out){auto& p=*p_;std::lock_guard lock(p.mutex);if(p.commitEvents.empty())return false;
    out=p.commitEvents.front();p.commitEvents.pop_front();return true;}
} // namespace station::psx
