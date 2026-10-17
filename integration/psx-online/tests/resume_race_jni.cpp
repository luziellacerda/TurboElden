// SPDX-License-Identifier: GPL-2.0-or-later
// Host JVM test only. Actual protocol; synthetic state and original-owner steps.
#include "StationPsxProtocol.hpp"
#include <jni.h>
#include <memory>
#include <array>
#include <deque>
#include <stdexcept>
#include <string>
using namespace station::psx;
namespace {
struct Pair {
    struct Packet {std::uint64_t id;std::vector<std::uint8_t> bytes;};
    std::unique_ptr<Session> host,guest;
    std::array<std::deque<Packet>,2> pending;
    std::uint64_t nextId{1};
    Session& at(int slot) {
        if(slot!=1&&slot!=2)throw std::runtime_error("TEST_SLOT");
        return slot==1?*host:*guest;
    }
    void pump() {
        for(unsigned n=0;n<10000;n++) {
            bool moved=false;
            for(int from=1;from<=2;from++) {
                auto& queue=pending[from-1];
                if(queue.empty()) {
                    auto bytes=at(from).takeOutgoing();if(bytes.empty())continue;
                    queue.push_back({nextId++,std::move(bytes)});
                }
                auto& packet=queue.front();
                auto result=at(3-from).deliver(from,packet.id,packet.bytes);
                // The real endpoint retains one bounded whole packet on Wait,
                // Paused or Backpressure, without ACK or fabricated copy proof.
                if(result==Result::Wait||result==Result::Paused||result==Result::Backpressure)continue;
                if(result!=Result::Ok&&result!=Result::Duplicate&&result!=Result::Superseded)
                    throw std::runtime_error("protocol rejects early peer packet: from="+std::to_string(from)+
                        " kind="+std::to_string(packet.bytes[8])+" result="+std::to_string(int(result)));
                if(!at(3-from).copied(packet.id)||at(3-from).releaseReceipt(packet.id)!=Result::Ok)
                    throw std::runtime_error("TEST_DELIVERY_RECEIPT");
                queue.pop_front();
                moved=true;
            }
            if(!moved) {
                Commit commit;for(int slot=1;slot<=2;slot++)while(at(slot).takeCommit(commit)){}
                return;
            }
        }
        throw std::runtime_error("TEST_PUMP_BOUND");
    }
};
std::unique_ptr<Pair> pair;
void demand(Result result,Result expected,const char* name) {
    if(result!=expected)throw std::runtime_error(name);
}
bool apply(void*,std::span<const std::uint8_t> bytes) {return bytes.size()==64;}
void failure(JNIEnv* env,const std::exception& error) {env->ThrowNew(env->FindClass("java/lang/AssertionError"),error.what());}
}
extern "C" JNIEXPORT void JNICALL
Java_org_emulationstation_frontend_netplay_StationPsxResumeRaceProbe_initializePair(JNIEnv* env,jclass,jlong epoch) {
    try {
        pair=std::make_unique<Pair>();Digest identity{};identity[0]=1;
        pair->host=std::make_unique<Session>(Config{1,std::uint64_t(epoch),64,identity,4});
        pair->guest=std::make_unique<Session>(Config{2,std::uint64_t(epoch),64,identity,4});
        for(int slot=1;slot<=2;slot++) {
            demand(pair->at(slot).control(epoch,1,true,true),Result::Ok,"TEST_PAUSE");
            demand(pair->at(slot).ownerCheckpoint(),Result::Paused,"TEST_PAUSE_ACK");
        }
        demand(pair->host->ownerPublishState(std::vector<std::uint8_t>(64,19),0),Result::Ok,"TEST_SNAPSHOT");
        pair->pump();pair->guest->ownerCheckpoint();
        demand(pair->guest->ownerApplyState(apply,pair.get()),Result::Ok,"TEST_APPLY");pair->pump();
        for(int slot=1;slot<=2;slot++) {
            demand(pair->at(slot).control(epoch,2,false,true),Result::Ok,"TEST_PLAYING");
            demand(pair->at(slot).ownerCheckpoint(),Result::Paused,"TEST_PLAYING_ACK");
            if(!pair->at(slot).drained()||!pair->at(slot).status().initialStateSynced)throw std::runtime_error("TEST_READY");
        }
    } catch(const std::exception& error) {failure(env,error);}
}
extern "C" JNIEXPORT jlongArray JNICALL
Java_org_emulationstation_frontend_netplay_StationPsxResumeRaceProbe_protocolStatus(JNIEnv* env,jclass,jint slot) {
    try {
        auto& session=pair->at(slot);auto s=session.status();
        const jlong rows[]={1,s.failed,0,0,jlong(s.epoch),jlong(s.controlSerial),jlong(s.nextFrame),jlong(s.stateSerial),
            s.paused,s.stateReady,s.inFrame,s.applyingState,s.closed,s.pause.valid,jlong(s.pause.epoch),
            jlong(s.pause.controlSerial),jlong(s.pause.nextFrame),jlong(s.pause.stateSerial),s.initialStateSynced,session.drained()};
        auto out=env->NewLongArray(20);if(out)env->SetLongArrayRegion(out,0,20,rows);return out;
    } catch(const std::exception& error) {failure(env,error);return nullptr;}
}
extern "C" JNIEXPORT jint JNICALL
Java_org_emulationstation_frontend_netplay_StationPsxResumeRaceProbe_protocolResume(JNIEnv* env,jclass,jint slot,jlong epoch,jlong serial) {
    try {return int(pair->at(slot).resume(epoch,serial));}
    catch(const std::exception& error) {failure(env,error);return -1;}
}
extern "C" JNIEXPORT jint JNICALL
Java_org_emulationstation_frontend_netplay_StationPsxResumeRaceProbe_advanceOwner(JNIEnv* env,jclass,jint slot) {
    try {
        auto& session=pair->at(slot);session.ownerCheckpoint();
        if(session.needsLocalSample())demand(session.ownerSampleLocal(1u<<(slot+4)),Result::Ok,"TEST_SAMPLE");
        Lease lease;auto result=session.ownerBegin(lease);
        if(result==Result::Ok)demand(session.ownerComplete(lease),Result::Ok,"TEST_EXECUTED");
        pair->pump();return int(result);
    } catch(const std::exception& error) {failure(env,error);return -1;}
}
extern "C" JNIEXPORT jint JNICALL
Java_org_emulationstation_frontend_netplay_StationPsxResumeRaceProbe_pendingPeerPackets(JNIEnv* env,jclass,jint slot) {
    try {pair->at(slot);return int(pair->pending[2-slot].size());}
    catch(const std::exception& error) {failure(env,error);return -1;}
}
