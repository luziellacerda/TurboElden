// SPDX-License-Identifier: GPL-2.0-or-later
#include <jni.h>
#include <algorithm>
#include <atomic>
#include <array>
#include <memory>
#include <mutex>
#include <string>
#include <vector>
#include "Common/StationDolphinTransport.h"
#include "Core/Core.h"
#include "Core/System.h"
#include "Core/HW/CPU.h"
#include "Core/Config/NetplaySettings.h"
#include "Core/Config/MainSettings.h"
#include "Core/ConfigManager.h"
#include "Core/NetPlayClient.h"
#include "Core/NetPlayServer.h"
#include "jni/AndroidCommon/AndroidCommon.h"
#include "jni/AndroidCommon/IDCache.h"

extern "C" {
JNIEXPORT jlong JNICALL Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeHost(JNIEnv*,jobject);
JNIEXPORT jlong JNICALL Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeJoin(JNIEnv*,jobject);
JNIEXPORT void JNICALL Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeChangeGame(JNIEnv*,jobject,jobject);
JNIEXPORT jboolean JNICALL Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeDoAllPlayersHaveGame(JNIEnv*,jobject);
}

namespace
{
std::mutex operations;
// Short CPU break/run arbitration only; never held by Connect or PauseAndLock.
// The transport gate is published before waiting for this lock.
std::mutex control_gate;
std::uint64_t acknowledged_epoch = 0;
std::atomic_bool resume_cpu{false};
NetPlay::NetPlayClient* Client(JNIEnv* env,jobject session)
{
  return reinterpret_cast<NetPlay::NetPlayClient*>(env->GetLongField(session,IDCache::GetNetPlayClientPointer()));
}
NetPlay::NetPlayServer* Server(JNIEnv* env,jobject session)
{
  return reinterpret_cast<NetPlay::NetPlayServer*>(env->GetLongField(session,IDCache::GetNetPlayServerPointer()));
}
void Throw(JNIEnv* env,const char* message)
{
  jclass type=env->FindClass("java/lang/IllegalStateException");
  if(type) { env->ThrowNew(type,message); env->DeleteLocalRef(type); }
}
}

extern "C" {
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeConfigure(
    JNIEnv* env,jclass,jboolean host,jint slot,jint mask,jint port,jlong epoch,jstring nickname)
{
  std::lock_guard guard(operations);
  if(!nickname || epoch<=0 || !Common::StationDolphin::Configure(host,slot,mask,port,epoch)) return JNI_FALSE;
  acknowledged_epoch=0; resume_cpu=false;
  // These are CurrentRun overrides. The user's offline preferences are not saved or rewritten.
  Config::SetCurrent(Config::NETPLAY_TRAVERSAL_CHOICE,std::string("direct"));
  Config::SetCurrent(Config::NETPLAY_USE_UPNP,false);
  Config::SetCurrent(Config::NETPLAY_USE_INDEX,false);
  Config::SetCurrent(Config::NETPLAY_ENABLE_QOS,false);
  Config::SetCurrent(Config::NETPLAY_ENABLE_CHUNKED_UPLOAD_LIMIT,false);
  Config::SetCurrent(Config::NETPLAY_BUFFER_SIZE,u32{5});
  Config::SetCurrent(Config::NETPLAY_CLIENT_BUFFER_SIZE,u32{1});
  Config::SetCurrent(Config::NETPLAY_NETWORK_MODE,std::string("fixeddelay"));
  Config::SetCurrent(Config::NETPLAY_SAVEDATA_LOAD,true);
  Config::SetCurrent(Config::NETPLAY_SAVEDATA_WRITE,true);
  Config::SetCurrent(Config::NETPLAY_SAVEDATA_SYNC_ALL_WII,false);
  Config::SetCurrent(Config::NETPLAY_SYNC_CODES,false);
  Config::SetCurrent(Config::NETPLAY_RECORD_INPUTS,false);
  Config::SetCurrent(Config::NETPLAY_STRICT_SETTINGS_SYNC,true);
  Config::SetCurrent(Config::NETPLAY_GOLF_MODE_OVERLAY,false);
  Config::SetCurrent(Config::NETPLAY_HIDE_REMOTE_GBAS,false);
  Config::SetCurrent(Config::MAIN_ENABLE_CHEATS,false);
  Config::SetCurrent(Config::NETPLAY_ADDRESS,std::string("127.0.0.1"));
  Config::SetCurrent(Config::NETPLAY_HOST_PORT,static_cast<u16>(port));
  Config::SetCurrent(Config::NETPLAY_CONNECT_PORT,static_cast<u16>(port));
  Config::SetCurrent(Config::NETPLAY_NICKNAME,GetJString(env,nickname));
  return JNI_TRUE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeConnect(
    JNIEnv* env,jclass,jobject session,jboolean host)
{
  std::lock_guard guard(operations);
  if(!session || !Common::StationDolphin::Active() || static_cast<bool>(host)!=Common::StationDolphin::IsHost() || Client(env,session) || Server(env,session)) return JNI_FALSE;
  if(host)
  {
    auto server=Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeHost(env,session);
    if(!server || env->ExceptionCheck()) return JNI_FALSE;
    env->SetLongField(session,IDCache::GetNetPlayServerPointer(),server);
  }
  auto client=Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeJoin(env,session);
  if(!client || env->ExceptionCheck()) return JNI_FALSE;
  env->SetLongField(session,IDCache::GetNetPlayClientPointer(),client);
  reinterpret_cast<NetPlay::NetPlayClient*>(client)->AdjustPadBufferSize(u32{1});
  if(host) Common::StationDolphin::AdmitGuests();
  return JNI_TRUE;
}
JNIEXPORT void JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeSelectGame(
    JNIEnv* env,jclass,jobject session,jobject game)
{
  std::lock_guard guard(operations);
  if(!session || !game || !Server(env,session)) { Throw(env,"Dolphin host session unavailable"); return; }
  Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeChangeGame(env,session,game);
}
JNIEXPORT jint JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativePlayerForSlot(
    JNIEnv* env,jclass,jobject session,jint slot)
{
  std::lock_guard guard(operations);
  auto* server=session?Server(env,session):nullptr;
  return server?static_cast<jint>(server->StationPlayerForSlot(slot)):0;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeMapControllers(
    JNIEnv* env,jclass,jobject session,jintArray gamecube,jintArray wiimotes)
{
  std::lock_guard guard(operations);
  auto* server=session?Server(env,session):nullptr;
  if(!server || !gamecube || !wiimotes || env->GetArrayLength(gamecube)!=4 || env->GetArrayLength(wiimotes)!=4) return JNI_FALSE;
  std::array<jint,4> gc{},wii{};
  env->GetIntArrayRegion(gamecube,0,4,gc.data()); env->GetIntArrayRegion(wiimotes,0,4,wii.data());
  NetPlay::PadMappingArray gc_map{},wii_map{};
  unsigned mapped_mask=0;
  for(unsigned i=0;i<4;++i)
  {
    if(gc[i]<0 || gc[i]>4 || wii[i]<0 || wii[i]>4) return JNI_FALSE;
    gc_map[i]=gc[i]?server->StationPlayerForSlot(gc[i]):0;
    wii_map[i]=wii[i]?server->StationPlayerForSlot(wii[i]):0;
    if((gc[i] && !gc_map[i]) || (wii[i] && !wii_map[i])) return JNI_FALSE;
    if(gc[i]) mapped_mask |= 1u << gc[i];
    if(wii[i]) mapped_mask |= 1u << wii[i];
  }
  if(mapped_mask!=Common::StationDolphin::ExpectedSlotMask()) return JNI_FALSE;
  server->SetPadMapping(gc_map); server->SetWiimoteMapping(wii_map); return JNI_TRUE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeStartGame(
    JNIEnv* env,jclass,jobject session)
{
  std::lock_guard guard(operations);
  auto* server=session?Server(env,session):nullptr;
  if(!server || !Common::StationDolphin::Active() || !Common::StationDolphin::Failure().empty()) return JNI_FALSE;
  if(server->StationRegisteredSlotMask()!=Common::StationDolphin::ExpectedSlotMask()) return JNI_FALSE;
  if(!Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeDoAllPlayersHaveGame(env,session)) return JNI_FALSE;
  return server->RequestStartGame()?JNI_TRUE:JNI_FALSE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativePauseAtEpoch(
    JNIEnv* env,jclass,jobject session,jlong epoch)
{
  std::lock_guard guard(operations);
  if(!session || epoch<=0 || !Common::StationDolphin::Active()) return JNI_FALSE;
  auto& cpu=Core::System::GetInstance().GetCPU();
  // SetStepping synchronizes and can wait on GetNetPads. Break first, then wake
  // those waits without invoking StopGame or clearing the running session.
  const bool was_suspended=Common::StationDolphin::Suspended();
  const bool should_resume=cpu.GetState()!=CPU::State::Stepping;
  if(!Common::StationDolphin::Pause(epoch)) return JNI_FALSE;
  if(!was_suspended && should_resume) resume_cpu=true;
  cpu.Break();
  if(auto* client=Client(env,session)) client->StationWakeInputWaits();
  const bool ignored=cpu.PauseAndLock();
  (void)ignored;
  cpu.RestoreStateAndUnlock(false);
  acknowledged_epoch=static_cast<std::uint64_t>(epoch);
  return JNI_TRUE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeSuspendTransport(
    JNIEnv*,jclass,jlong epoch)
{
  // Must freeze ENet even while Connect holds operations. This is NOT a CPU-idle
  // ACK; the session worker still calls PauseAtEpoch before READY/pausedAtEpoch.
  auto& cpu=Core::System::GetInstance().GetCPU();
  const bool was_suspended=Common::StationDolphin::Suspended();
  const bool should_resume=cpu.GetState()!=CPU::State::Stepping;
  std::uint64_t serial=0;
  if(epoch<=0 || !Common::StationDolphin::EmergencySuspend(static_cast<std::uint64_t>(epoch),&serial)) return JNI_FALSE;
  std::lock_guard gate(control_gate);
  if(!Common::StationDolphin::CurrentControl(epoch,serial,true)) return JNI_TRUE;
  if(!was_suspended && should_resume) resume_cpu=true;
  cpu.Break();
  return JNI_TRUE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeResumeAtEpoch(
    JNIEnv*,jclass,jlong epoch,jlong serial)
{
  std::lock_guard guard(operations);
  std::lock_guard gate(control_gate);
  if(epoch<=0 || serial<=0 || acknowledged_epoch!=static_cast<std::uint64_t>(epoch) || !Common::StationDolphin::Resume(epoch,serial)) return JNI_FALSE;
  acknowledged_epoch=0;
  const bool deferred=Common::StationDolphin::ConsumeCPURunRequest();
  if(resume_cpu.exchange(false) || deferred) Core::System::GetInstance().GetCPU().SetStepping(false);
  return JNI_TRUE;
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeControl(
    JNIEnv*,jclass,jlong epoch,jlong serial,jboolean pause)
{
  // No operations lock. The exact latest revision is checked again by Resume
  // under the same transport mutex that publishes this control.
  auto& cpu=Core::System::GetInstance().GetCPU();
  const bool was_suspended=Common::StationDolphin::Suspended();
  const bool should_resume=cpu.GetState()!=CPU::State::Stepping;
  if(epoch<=0 || serial<=0 || !Common::StationDolphin::PublishControl(epoch,serial,pause)) return JNI_FALSE;
  if(pause)
  {
    std::lock_guard gate(control_gate);
    if(!Common::StationDolphin::CurrentControl(epoch,serial,true)) return JNI_TRUE;
    if(!was_suspended && should_resume) resume_cpu=true;
    cpu.Break();
  }
  return JNI_TRUE;
}
JNIEXPORT jbyteArray JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeTakeOutgoing(
    JNIEnv* env,jclass,jint slot,jint timeout)
{
  auto frame=Common::StationDolphin::TakeOutgoing(slot,std::max(timeout,0));
  if(frame.empty()) return nullptr;
  auto out=env->NewByteArray(static_cast<jsize>(frame.size()));
  if(out) env->SetByteArrayRegion(out,0,frame.size(),reinterpret_cast<const jbyte*>(frame.data()));
  return out;
}
JNIEXPORT jint JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeDeliver(
    JNIEnv* env,jclass,jint slot,jlong id,jbyteArray frame)
{
  if(!frame || id<=0) return -1;
  const auto length=env->GetArrayLength(frame);
  if(length<9 || length>static_cast<jsize>(Common::StationDolphin::MAX_DATAGRAM+8)) return -1;
  std::vector<std::uint8_t> bytes(length);
  env->GetByteArrayRegion(frame,0,length,reinterpret_cast<jbyte*>(bytes.data()));
  return Common::StationDolphin::Deliver(slot,id,bytes);
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeAwaitDelivery(
    JNIEnv*,jclass,jlong id,jint timeout)
{ return id>0 && Common::StationDolphin::AwaitDelivery(id,std::max(timeout,0))?JNI_TRUE:JNI_FALSE; }
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeDrained(JNIEnv*,jclass)
{ return Common::StationDolphin::Drained()?JNI_TRUE:JNI_FALSE; }
JNIEXPORT jstring JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeFailure(JNIEnv* env,jclass)
{ return ToJString(env,Common::StationDolphin::Failure()); }
JNIEXPORT void JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeFail(
    JNIEnv* env,jclass,jstring category)
{
  // Independent of Connect/operations. No raw message, URL or credential enters
  // native diagnostics; the Java owner supplies a small categorical code.
  auto reason=category?GetJString(env,category):std::string{};
  if(reason.empty() || reason.size()>96 || !std::all_of(reason.begin(),reason.end(),[](unsigned char c) {
      return (c>='A' && c<='Z') || (c>='0' && c<='9') || c=='_';
    })) reason="DOLPHIN_PROTOCOL_FAILURE";
  Common::StationDolphin::Fail(reason.c_str());
  if(Common::StationDolphin::Active()) Core::System::GetInstance().GetCPU().Break();
}
JNIEXPORT jint JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeStatus(
    JNIEnv* env,jclass,jobject session)
{
  std::lock_guard guard(operations);
  int flags=0;
  if(Common::StationDolphin::Active()) flags |= 1;
  if(Common::StationDolphin::IsHost()) flags |= 2;
  auto* client=session?Client(env,session):nullptr;
  auto* server=session?Server(env,session):nullptr;
  if(client && client->IsConnected()) flags |= 4;
  if(server && server->is_connected) flags |= 8;
  auto& system=Core::System::GetInstance();
  if(Core::IsRunning(system)) flags |= 16;
  if(system.GetCPU().GetState()==CPU::State::Stepping) flags |= 32;
  if(Common::StationDolphin::Suspended()) flags |= 64;
  if(!Common::StationDolphin::Failure().empty()) flags |= 128;
  if(Common::StationDolphin::Drained()) flags |= 256;
  if(server && server->StationRegisteredSlotMask()==Common::StationDolphin::ExpectedSlotMask()) flags |= 512;
  return flags;
}
JNIEXPORT jlong JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeAcknowledgedEpoch(JNIEnv*,jclass)
{
  std::lock_guard guard(operations);
  return static_cast<jlong>(acknowledged_epoch);
}
JNIEXPORT jint JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeRegisteredSlots(JNIEnv* env,jclass,jobject session)
{
  std::lock_guard guard(operations);
  auto* server=session?Server(env,session):nullptr;
  return server?static_cast<jint>(server->StationRegisteredSlotMask()):0;
}
JNIEXPORT void JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeCloseTransport(JNIEnv*,jclass)
{
  // Does not wait for operations: it must be able to cancel a blocked Join.
  // The owner releases the official session only after its connection worker returns.
  Common::StationDolphin::Close();
}
JNIEXPORT jboolean JNICALL Java_org_emulationstation_frontend_netplay_StationDolphinBridge_nativeAuthorizeHumanExit(JNIEnv*,jclass,jobject session)
{
  // Independent of operations: a human must be able to cancel a blocked Join.
  // The Java owner keeps the strong session reference until its worker returns.
  // Session may still be null when GameFile/official-session construction fails.
  // This method never dereferences it. Authorization originates only in the
  // owner's explicit human Exit action and is idempotent before configure.
  (void)session;
  return Common::StationDolphin::AuthorizeHumanExit()?JNI_TRUE:JNI_FALSE;
}
}
