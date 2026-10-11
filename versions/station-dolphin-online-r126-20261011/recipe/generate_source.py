#!/usr/bin/env python3
"""Create a pinned, patched source archive without modifying the existing clone."""
import argparse, configparser, difflib, hashlib, io, json, pathlib, subprocess, tarfile

PIN = "5102a0339c2177575378107b76541e47cc52122d"
HERE = pathlib.Path(__file__).resolve().parent.parent
EXCLUDED = {
    "Externals/Qt": "Windows Qt distribution; Android native target has no Qt",
    "Externals/FFmpeg-bin": "Windows FFmpeg binary distribution",
    "Externals/SDL/SDL": "ENABLE_SDL=OFF on Android",
    "Externals/spirv_cross/SPIRV-Cross": "Only Windows/Apple add this dependency",
    "Externals/libusb/libusb": "Android excludes libusb",
    "Externals/hidapi/hidapi-src": "Android excludes hidapi",
    "Externals/cpp-ipc/cpp-ipc": "Android does not add cpp-ipc",
    "Externals/wil": "Windows implementation library",
    "Externals/gtest": "ENABLE_TESTS=OFF in production build",
}

def digest(data): return hashlib.sha256(data).hexdigest()
def write_if_changed(path, data):
    if not path.exists() or path.read_bytes()!=data: path.write_bytes(data)
def git(clone, *args):
    return subprocess.check_output(["git", "-c", "safe.directory="+str(clone), "-C", str(clone), *args])
def replace(text, old, new, count=1):
    actual = text.count(old)
    if actual != count:
        raise ValueError(f"Pinned source anchor expected {count}, got {actual}: {old[:100]!r}")
    return text.replace(old, new)

def patched_sources(clone):
    sources = {}
    def load(path): return git(clone, "show", PIN+":"+path).decode("utf-8")
    path="Source/Core/Common/CMakeLists.txt"
    s=load(path); s=replace(s,"add_library(common\n", "add_library(common\n  StationDolphinTransport.cpp\n  StationDolphinTransport.h\n")
    sources[path]=s
    path="Source/Android/jni/CMakeLists.txt"
    s=load(path); s=replace(s,"  NetPlay/Netplay.cpp\n", "  NetPlay/Netplay.cpp\n  NetPlay/StationDolphinBridge.cpp\n")
    s += '\n# Station-only libraries. Original offline libraries are never replaced.\nset_target_properties(main PROPERTIES OUTPUT_NAME station_dolphin_online)\nset_target_properties(main_hook PROPERTIES OUTPUT_NAME station_dolphin_hook)\nset_target_properties(hook_impl PROPERTIES OUTPUT_NAME station_dolphin_hook_impl)\nset_target_properties(file_redirect_hook PROPERTIES OUTPUT_NAME station_dolphin_file_redirect_hook)\nset_target_properties(gsl_alloc_hook PROPERTIES OUTPUT_NAME station_dolphin_gsl_alloc_hook)\nadd_dependencies(main main_hook file_redirect_hook gsl_alloc_hook)\ntarget_link_options(main PRIVATE\n  "-Wl,--wrap=enet_time_get"\n  "-Wl,--wrap=enet_socket_send"\n  "-Wl,--wrap=enet_socket_receive"\n  "-Wl,--wrap=enet_socket_wait"\n)\n'
    sources[path]=s
    path="Source/Android/jni/AndroidCommon/IDCache.cpp"
    s=load(path); s=replace(s,'env->FindClass("androidx/core/util/Pair")','env->FindClass("tdolphin/core/util/Pair")')
    sources[path]=s
    path="Source/Core/Core/NetPlayClient.h"
    s=load(path); s=replace(s,"  bool StopGame();\n", "  bool StopGame();\n  // Station recovery: wake input waits without stopping the NetPlay session.\n  void StationWakeInputWaits();\n")
    sources[path]=s
    path="Source/Core/Core/NetPlayClient.cpp"
    s=load(path)
    s=replace(s,'#include "Common/ENet.h"\n', '#include "Common/ENet.h"\n#include "Common/StationDolphinTransport.h"\n#include "Core/HW/CPU.h"\n')
    # Station bootstrap waits for actual native handshake, not a five-second
    # network deadline that discards the peer during temporary WSS loss.
    service='static int StationService(ENetHost* host, ENetEvent* event, enet_uint32 timeout)\n{\n  if (!Common::StationDolphin::Active())\n    return enet_host_service(host, event, timeout);\n  for (;;)\n  {\n    if (!Common::StationDolphin::Active() || Common::StationDolphin::HumanExitAllowed())\n      return 0;\n    const int result = enet_host_service(host, event, 100);\n    if (result != 0)\n      return result;\n  }\n}\n\n'
    s=replace(s,'// called from ---GUI--- thread\nNetPlayClient::~NetPlayClient()',service+'// called from ---GUI--- thread\nNetPlayClient::~NetPlayClient()')
    s=replace(s,'int net = enet_host_service(m_client, &netEvent, 5000);','int net = StationService(m_client, &netEvent, 5000);')
    s=replace(s,'while ((net = enet_host_service(m_client, &netEvent, 5000)) > 0 &&','while ((net = StationService(m_client, &netEvent, 5000)) > 0 &&')
    s=replace(s,"    enet_host_destroy(m_client);\n", "    Common::StationDolphin::Detach(m_client);\n    enet_host_destroy(m_client);\n")
    s=replace(s,"    m_client->mtu = std::min(m_client->mtu, NetPlay::MAX_ENET_MTU);\n", "    Common::StationDolphin::Attach(m_client, false);\n    m_client->mtu = std::min(m_client->mtu, NetPlay::MAX_ENET_MTU);\n")
    s=replace(s,"        m_dialog->OnConnectionLost();\n", "        if (Common::StationDolphin::Active())\n        {\n          Core::System::GetInstance().GetCPU().Break();\n          Common::StationDolphin::Fail(\"DOLPHIN_ENET_DISCONNECTED\");\n          StationWakeInputWaits();\n          break;\n        }\n        m_dialog->OnConnectionLost();\n")
    begin=s.index("bool NetPlayClient::GetNetPads("); end=s.index("void NetPlayClient::SendPadHostPoll(",begin)
    # Includes GetNetPads/WiimoteUpdate, but not unrelated socket/GUI loop checks.
    section=s[begin:end]
    section=replace(section,"if (!m_is_running.IsSet())", "if (!m_is_running.IsSet() || Common::StationDolphin::Suspended())",3)
    section=replace(section,"{\n  // The interface for this is extremely silly.", "{\n  if (Common::StationDolphin::Suspended())\n    return false;\n  // The interface for this is extremely silly.")
    s=s[:begin]+section+s[end:]
    begin=s.index("void NetPlayClient::SendPadHostPoll("); end=s.index("\n}",begin)+2
    section=s[begin:end]
    section=replace(section,"if (!m_is_running.IsSet())", "if (!m_is_running.IsSet() || Common::StationDolphin::Suspended())",2)
    s=s[:begin]+section+s[end:]
    anchor="// called from ---GUI--- thread\nstd::vector<const Player*> NetPlayClient::GetPlayers()"
    wake="void NetPlayClient::StationWakeInputWaits()\n{\n  m_wait_on_input_event.Set();\n  m_gc_pad_event.Set();\n  m_wii_pad_event.Set();\n  m_first_pad_status_received_event.Set();\n}\n\n"
    s=replace(s,anchor,wake+anchor)
    stop_guard='  if (Common::StationDolphin::BlockAutomaticStop("DOLPHIN_STOP_WITHOUT_HUMAN"))\n  {\n    Core::System::GetInstance().GetCPU().Break();\n    StationWakeInputWaits();\n    return;\n  }\n'
    for signature in ["void NetPlayClient::OnStopGame(sf::Packet& packet)","void NetPlayClient::OnPowerButton()","void NetPlayClient::InvokeStop()","void NetPlayClient::Stop()","void NetPlayClient::RequestStopGame()"]:
        s=replace(s,signature+"\n{\n",signature+"\n{\n"+stop_guard)
    s=replace(s,"bool NetPlayClient::StopGame()\n{\n","bool NetPlayClient::StopGame()\n{\n"+stop_guard.replace("    return;", "    return false;"))
    sources[path]=s
    path="Source/Core/Core/NetPlayServer.h"
    s=load(path); s=replace(s,"  u16 GetPort() const;\n", "  u16 GetPort() const;\n  PlayerId StationPlayerForSlot(unsigned int slot);\n  unsigned int StationRegisteredSlotMask();\n")
    sources[path]=s
    path="Source/Core/Core/NetPlayServer.cpp"
    s=load(path)
    s=replace(s,'#include "Common/ENet.h"\n', '#include "Common/ENet.h"\n#include "Common/StationDolphinTransport.h"\n#include "Core/System.h"\n#include "Core/HW/CPU.h"\n')
    s=replace(s,"    serverAddr.host = ENET_HOST_ANY;\n", "    serverAddr.host = Common::StationDolphin::Active() ? htonl(INADDR_LOOPBACK) : ENET_HOST_ANY;\n")
    s=replace(s,"    enet_host_destroy(m_server);", "    Common::StationDolphin::Detach(m_server);\n    enet_host_destroy(m_server);")
    s=replace(s,"      m_server->mtu = std::min(m_server->mtu, NetPlay::MAX_ENET_MTU);\n", "      Common::StationDolphin::Attach(m_server, true);\n      m_server->mtu = std::min(m_server->mtu, NetPlay::MAX_ENET_MTU);\n")
    s=replace(s,"unsigned int NetPlayServer::OnDisconnect(const Client& player)\n{", "unsigned int NetPlayServer::OnDisconnect(const Client& player)\n{\n  if (Common::StationDolphin::Active())\n  {\n    Core::System::GetInstance().GetCPU().Break();\n    Common::StationDolphin::Fail(\"DOLPHIN_ENET_PEER_LOST\");\n    return 0;\n  }")
    # A timeout event can have no peer data. Gate before reading the PID.
    s=replace(s,"      case ENET_EVENT_TYPE_DISCONNECT:\n      {", "      case ENET_EVENT_TYPE_DISCONNECT:\n      {\n        if (Common::StationDolphin::Active())\n        {\n          Core::System::GetInstance().GetCPU().Break();\n          Common::StationDolphin::Fail(\"DOLPHIN_ENET_PEER_LOST\");\n          break;\n        }")
    anchor="static PlayerId* PeerPlayerId(ENetPeer* peer)"
    mapping="PlayerId NetPlayServer::StationPlayerForSlot(unsigned int slot)\n{\n  std::lock_guard guard(m_crit.players);\n  for (const auto& [pid, player] : m_players)\n    if (player.socket && Common::StationDolphin::SlotForAddress(player.socket->address) == slot)\n      return pid;\n  return 0;\n}\n\n"
    mapping+="unsigned int NetPlayServer::StationRegisteredSlotMask()\n{\n  std::lock_guard guard(m_crit.players);\n  unsigned int mask = 0;\n  for (const auto& [pid, player] : m_players)\n  {\n    const auto slot = player.socket ? Common::StationDolphin::SlotForAddress(player.socket->address) : 0;\n    if (slot == 0 || (mask & (1u << slot)))\n      return 0;\n    mask |= 1u << slot;\n  }\n  return mask;\n}\n\n"
    s=replace(s,anchor,mapping+anchor)
    s=replace(s,"  case MessageID::StopGame:\n  {\n","  case MessageID::StopGame:\n  {\n    if (Common::StationDolphin::BlockAutomaticStop(\"DOLPHIN_REMOTE_STOP_WITHOUT_HUMAN\"))\n    {\n      Core::System::GetInstance().GetCPU().Break();\n      break;\n    }\n")
    sources[path]=s
    path="Source/Core/Core/Core.cpp"
    s=load(path)
    s=replace(s,'#include "Core/Core.h"\n','#include "Core/Core.h"\n#include "Common/StationDolphinTransport.h"\n')
    s=replace(s,'void Stop(Core::System& system)  // - Hammertime!\n{\n','void Stop(Core::System& system)  // - Hammertime!\n{\n  if (Common::StationDolphin::BlockAutomaticStop("DOLPHIN_CORE_STOP_WITHOUT_HUMAN"))\n  {\n    system.GetCPU().Break();\n    return;\n  }\n')
    sources[path]=s
    path="Source/Android/jni/NetPlay/NetPlayUICallbacks.cpp"
    s=load(path)
    s=replace(s,'#include "Core/Core.h"\n','#include "Core/Core.h"\n#include "Common/StationDolphinTransport.h"\n#include "Core/HW/CPU.h"\n')
    s=replace(s,'void NetPlayUICallbacks::StopGame()\n{\n','void NetPlayUICallbacks::StopGame()\n{\n  if (Common::StationDolphin::BlockAutomaticStop("DOLPHIN_UI_STOP_WITHOUT_HUMAN"))\n  {\n    Core::System::GetInstance().GetCPU().Break();\n    return;\n  }\n')
    sources[path]=s
    path="Source/Android/jni/MainAndroid.cpp"
    s=load(path)
    s=replace(s,'#include "Core/Core.h"\n','#include "Core/Core.h"\n#include "Common/StationDolphinTransport.h"\n#include "Core/HW/CPU.h"\n')
    s=replace(s,'JNIEXPORT void JNICALL Java_org_dolphinemu_dolphinemu_NativeLibrary_StopEmulation(JNIEnv*, jclass)\n{\n','JNIEXPORT void JNICALL Java_org_dolphinemu_dolphinemu_NativeLibrary_StopEmulation(JNIEnv*, jclass)\n{\n  if (Common::StationDolphin::BlockAutomaticStop("DOLPHIN_ANDROID_STOP_WITHOUT_HUMAN"))\n  {\n    Core::System::GetInstance().GetCPU().Break();\n    return;\n  }\n')
    sources[path]=s
    path="Source/Core/Core/HW/CPU.cpp"
    s=load(path)
    # Anchored on the CPU header to avoid reliance on other include ordering.
    s=replace(s,'#include "Core/HW/CPU.h"\n', '#include "Core/HW/CPU.h"\n#include "Common/StationDolphinTransport.h"\n')
    s=replace(s,"  std::unique_lock state_lock(m_state_change_lock);\n  while (m_state != State::PowerDown)", "  std::unique_lock state_lock(m_state_change_lock);\n  if (m_state == State::Running && Common::StationDolphin::DeferCPURun())\n    SetStateLocked(State::Stepping);\n  while (m_state != State::PowerDown)")
    s=replace(s,"  else if (SetStateLocked(State::Running))\n", "  else if (Common::StationDolphin::DeferCPURun())\n  {\n    RunAdjacentSystems(false);\n  }\n  else if (SetStateLocked(State::Running))\n")
    # CPUThreadGuard and RunOnCPUThread restore directly, bypassing SetStepping.
    # Check the same online gate before that temporary pause can resume a frame.
    s=replace(s,"    else if (unpause_on_unlock)\n", "    else if (unpause_on_unlock && !Common::StationDolphin::DeferCPURun())\n")
    sources[path]=s
    # NDK28 libc++ instantiates the C++23 unique_ptr destructor at the class
    # definition. Supply the complete BlobReader type; no executable code changes.
    path="Source/Core/DiscIO/VolumeWad.h"
    s=load(path); s=replace(s,'#include "DiscIO/Volume.h"\n','#include "DiscIO/Volume.h"\n#include "DiscIO/Blob.h"\n')
    sources[path]=s
    path="Source/Core/Core/DSP/DSPCaptureLogger.h"
    s=load(path); s=replace(s,'#include "Common/CommonTypes.h"\n','#include "Common/CommonTypes.h"\n#include "Common/PcapFile.h"\n')
    sources[path]=s
    path="CMake/ScmRevGen.cmake"
    s=load(path)
    s=replace(s,"if(GIT_FOUND)\n", 'if(DOLPHIN_STATION_ONLINE)\n  set(DOLPHIN_WC_REVISION "'+PIN+'-station-dpl1-r126")\n  set(DOLPHIN_WC_DESCRIBE "2609-7-station-dpl1-r126")\n  set(DOLPHIN_WC_BRANCH "station-dolphin-online-r126")\n  set(DOLPHIN_WC_COMMITS_AHEAD_MASTER 0)\nelseif(GIT_FOUND)\n')
    sources[path]=s
    path="CMakeLists.txt"
    s=load(path)
    s=replace(s,"-DPROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR} -DPROJECT_BINARY_DIR", "-DDOLPHIN_STATION_ONLINE=ON -DPROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR} -DPROJECT_BINARY_DIR")
    sources[path]=s
    return sources

def safe_unpack(archive, dest):
    # The tracked upstream tree has regular files and safe relative symlinks.
    dest=dest.resolve()
    for member in archive.getmembers():
        target=(dest/member.name).resolve()
        if not target.is_relative_to(dest): raise ValueError("Archive path escape")
        if member.issym() or member.islnk():
            link=(target.parent/member.linkname).resolve() if member.issym() else (dest/member.linkname).resolve()
            if not link.is_relative_to(dest): raise ValueError("Archive link escape")
    archive.extractall(dest, filter="data")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--clone", required=True); p.add_argument("--stage"); p.add_argument("--refresh-stage",action="store_true"); args=p.parse_args()
    clone=pathlib.Path(args.clone)
    if git(clone,"rev-parse","HEAD").decode().strip()!=PIN: raise ValueError("Existing clone must remain at pinned HEAD")
    if git(clone,"status","--porcelain").strip(): raise ValueError("Existing source clone has local changes; do not overwrite them")
    sources=patched_sources(clone); records=[]; patches=[]
    for path,s in sources.items():
        original=git(clone,"show",PIN+":"+path); modified=s.encode()
        records.append({"path":path,"upstreamSha256":digest(original),"patchedSha256":digest(modified)})
        patches.extend(difflib.unified_diff(original.decode().splitlines(True),s.splitlines(True),fromfile="a/"+path,tofile="b/"+path))
    modules=configparser.ConfigParser(); modules.read_string(git(clone,"show",PIN+":.gitmodules").decode())
    pins={}
    for line in git(clone,"ls-tree","-r",PIN).decode().splitlines():
        before,path=line.split("\t",1); mode,typ,sha=before.split()
        if mode=="160000": pins[path]=sha
    locks=[]
    for section in modules.sections():
        path=modules[section]["path"]; url=modules[section]["url"]
        locks.append({"path":path,"gitUrl":url,"commit":pins[path],"android":path not in EXCLUDED,"reason":EXCLUDED.get(path,"Android native dependency; feature kept enabled")})
    if len(locks)!=34: raise ValueError("Pinned dependency set changed")
    (HERE/"patches").mkdir(exist_ok=True); (HERE/"evidence").mkdir(exist_ok=True)
    patch="".join(patches).encode(); (HERE/"patches"/"dolphin-station-r126.patch").write_bytes(patch)
    (HERE/"recipe"/"dependencies.lock.json").write_text(json.dumps({"upstream":PIN,"modules":locks},indent=2)+"\n")
    added={"Source/Core/Common/StationDolphinTransport.h":HERE/"native"/"StationDolphinTransport.h","Source/Core/Common/StationDolphinTransport.cpp":HERE/"native"/"StationDolphinTransport.cpp","Source/Android/jni/NetPlay/StationDolphinBridge.cpp":HERE/"native"/"StationDolphinBridge.cpp"}
    receipt={"upstream":PIN,"existingCloneUnchanged":True,"patchSha256":digest(patch),"patchedFiles":records,"addedFiles":[{"path":dest,"sha256":digest(src.read_bytes())} for dest,src in added.items()],"modules":len(locks),"androidModules":sum(x["android"] for x in locks),"excludedModules":len(EXCLUDED),"compiled":False}
    if args.stage:
        stage=pathlib.Path(args.stage)
        if args.refresh_stage:
            previous=json.loads((stage/"station-r126-source-receipt.json").read_text())
            if previous["upstream"]!=PIN: raise ValueError("Wrong stage revision")
            for record in previous["patchedFiles"]:
                if digest((stage/record["path"]).read_bytes())!=record["patchedSha256"]: raise ValueError("Stage source has unrecorded modifications: "+record["path"])
            for record in previous["addedFiles"]:
                if digest((stage/record["path"]).read_bytes())!=record["sha256"]: raise ValueError("Stage addition has unrecorded modifications: "+record["path"])
        else:
            if stage.exists() and any(stage.iterdir()): raise ValueError("Stage must be new and empty; no checkout is modified")
            stage.mkdir(parents=True,exist_ok=True)
            data=git(clone,"archive","--format=tar",PIN)
            with tarfile.open(fileobj=io.BytesIO(data)) as tar: safe_unpack(tar,stage)
        for path,s in sources.items(): write_if_changed(stage/path,s.encode("utf-8"))
        for path,src in added.items(): write_if_changed(stage/path,src.read_bytes())
        (stage/"station-r126-source-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    (HERE/"evidence"/"generator-r126.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"upstream":PIN,"patchedFiles":len(sources),"androidModules":receipt["androidModules"],"patchSha256":receipt["patchSha256"],"compiled":False}))

if __name__=="__main__": main()
