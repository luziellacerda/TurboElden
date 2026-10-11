// SPDX-License-Identifier: GPL-2.0-or-later
#include "Common/StationDolphinTransport.h"
#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <condition_variable>
#include <cstring>
#include <deque>
#include <map>
#include <mutex>
#include <arpa/inet.h>

extern "C" {
enet_uint32 __real_enet_time_get();
int __real_enet_socket_send(ENetSocket, const ENetAddress*, const ENetBuffer*, size_t);
int __real_enet_socket_receive(ENetSocket, ENetAddress*, ENetBuffer*, size_t);
int __real_enet_socket_wait(ENetSocket, enet_uint32*, enet_uint32);
}

namespace Common::StationDolphin
{
namespace
{
struct Datagram { ENetAddress from{}; std::vector<std::uint8_t> data; std::uint64_t delivery = 0; };
struct Endpoint { ENetHost* host = nullptr; bool server = false; std::deque<Datagram> incoming; std::size_t bytes = 0; };
struct Delivery { unsigned slot; std::vector<std::uint8_t> frame; bool consumed = false; };
struct State
{
  std::mutex lock; std::condition_variable changed;
  bool active = false, host = false, suspended = false, admit_guests = false, cpu_run_requested = false, human_exit = false;
  unsigned slot = 0, mask = 0, port = 0; std::uint64_t epoch = 0;
  std::uint64_t control_serial = 0, control_epoch = 0;
  bool control_pause = true;
  std::string failure;
  std::map<ENetSocket, Endpoint> endpoints;
  std::array<std::deque<std::vector<std::uint8_t>>, 5> outgoing;
  std::array<std::size_t, 5> outgoing_bytes{};
  std::map<std::uint64_t, Delivery> deliveries;
  enet_uint32 clock_start = 0, clock_offset = 0, frozen = 0;
} state;

ENetAddress SyntheticGuest(unsigned slot)
{
  return ENetAddress{htonl(0x7f000000u | slot), static_cast<enet_uint16>(40000 + slot)};
}
bool SlotAllowed(unsigned slot) { return slot >= 1 && slot <= 4 && (state.mask & (1u << slot)); }
ENetAddress LocalAddress(const Endpoint& endpoint)
{
  ENetAddress address{};
  enet_socket_get_address(endpoint.host->socket, &address);
  address.host = htonl(INADDR_LOOPBACK);
  return address;
}
Endpoint* Destination(unsigned port)
{
  for (auto& [socket, endpoint] : state.endpoints)
    if (LocalAddress(endpoint).port == port) return &endpoint;
  return nullptr;
}
Endpoint* Server()
{
  for (auto& [socket, endpoint] : state.endpoints) if (endpoint.server) return &endpoint;
  return nullptr;
}
Endpoint* Client()
{
  for (auto& [socket, endpoint] : state.endpoints) if (!endpoint.server) return &endpoint;
  return nullptr;
}
enet_uint32 ClockLocked()
{
  return state.suspended ? state.frozen : __real_enet_time_get() - state.clock_offset;
}
void FailLocked(const char* reason)
{
  if (!state.active) return;
  if (state.failure.empty()) state.failure = reason;
  if (!state.suspended) { state.frozen = ClockLocked(); state.clock_start = __real_enet_time_get(); }
  state.suspended = true;
  state.changed.notify_all();
}
std::vector<std::uint8_t> Frame(unsigned from, unsigned to, std::span<const std::uint8_t> data)
{
  std::vector<std::uint8_t> frame{'D','P','L','1',static_cast<std::uint8_t>(from),
      static_cast<std::uint8_t>(to),static_cast<std::uint8_t>(data.size() >> 8),
      static_cast<std::uint8_t>(data.size())};
  frame.insert(frame.end(), data.begin(), data.end());
  return frame;
}
}

bool Configure(bool host, unsigned slot, unsigned mask, unsigned port, std::uint64_t epoch)
{
  std::lock_guard guard(state.lock);
  if (state.active || !state.endpoints.empty() || slot < 1 || slot > 4 ||
      host != (slot == 1) || (mask & ~30u) || !(mask & 2u) || !(mask & (1u << slot)) ||
      std::popcount(mask) < 2 || port < 1024 || port > 65535 || epoch == 0) return false;
  state.host = host; state.slot = slot; state.mask = mask; state.port = port;
  state.epoch = epoch; state.failure.clear(); state.clock_offset = 0;
  state.control_serial = 0; state.control_epoch = epoch; state.control_pause = true;
  state.cpu_run_requested = false;
  state.human_exit = false;
  state.suspended = false; state.admit_guests = !host; state.active = true;
  return true;
}
bool Active() { std::lock_guard guard(state.lock); return state.active; }
bool IsHost() { std::lock_guard guard(state.lock); return state.active && state.host; }
unsigned ExpectedSlotMask() { std::lock_guard guard(state.lock); return state.active ? state.mask : 0; }
bool Suspended() { std::lock_guard guard(state.lock); return state.active && state.suspended; }
bool AuthorizeHumanExit()
{
  std::lock_guard guard(state.lock);
  if (!state.active) return true;
  state.human_exit = true;
  state.changed.notify_all();
  return true;
}
bool HumanExitAllowed() { std::lock_guard guard(state.lock); return !state.active || state.human_exit; }
bool BlockAutomaticStop(const char* reason)
{
  std::lock_guard guard(state.lock);
  if (!state.active || state.human_exit) return false;
  FailLocked(reason);
  return true;
}
bool DeferCPURun()
{
  std::lock_guard guard(state.lock);
  if (!state.active || !state.suspended) return false;
  state.cpu_run_requested = true;
  return true;
}
bool ConsumeCPURunRequest()
{
  std::lock_guard guard(state.lock);
  const bool requested = state.active && !state.suspended && state.cpu_run_requested;
  if (requested) state.cpu_run_requested = false;
  return requested;
}
void Attach(ENetHost* host, bool server)
{
  if (!host) return;
  std::lock_guard guard(state.lock);
  if (state.active) state.endpoints.emplace(host->socket, Endpoint{host, server});
}
void Detach(ENetHost* host)
{
  if (!host) return;
  std::lock_guard guard(state.lock);
  state.endpoints.erase(host->socket); state.changed.notify_all();
}
void AdmitGuests() { std::lock_guard guard(state.lock); if(state.active && state.host) { state.admit_guests=true; state.changed.notify_all(); } }
unsigned SlotForAddress(const ENetAddress& address)
{
  std::lock_guard guard(state.lock);
  if(!state.active || !state.host) return 0;
  if(address.host==htonl(INADDR_LOOPBACK))
    if(auto* endpoint=Destination(address.port);endpoint && !endpoint->server) return 1;
  const unsigned synthetic=ntohl(address.host),slot=synthetic & 0xffu;
  return (synthetic & 0xffffff00u)==0x7f000000u && address.port==40000+slot && slot>1 && SlotAllowed(slot)?slot:0;
}
bool Pause(std::uint64_t epoch)
{
  std::lock_guard guard(state.lock);
  if (!state.active || epoch < state.epoch || epoch == 0) return false;
  if (!state.suspended) { state.frozen = ClockLocked(); state.clock_start = __real_enet_time_get(); }
  state.epoch = epoch; state.suspended = true; state.changed.notify_all(); return true;
}
bool PublishControl(std::uint64_t epoch, std::uint64_t serial, bool pause)
{
  std::lock_guard guard(state.lock);
  if (!state.active || epoch == 0 || serial == 0 || epoch < state.epoch || serial < state.control_serial) return false;
  if (serial == state.control_serial) return epoch == state.control_epoch && pause == state.control_pause;
  state.control_serial = serial; state.control_epoch = epoch; state.control_pause = pause;
  if (pause)
  {
    if (!state.suspended) { state.frozen = ClockLocked(); state.clock_start = __real_enet_time_get(); }
    state.epoch = epoch; state.suspended = true;
  }
  state.changed.notify_all(); return true;
}
bool EmergencySuspend(std::uint64_t epoch, std::uint64_t* serial)
{
  std::lock_guard guard(state.lock);
  if (!state.active || epoch == 0 || epoch < state.epoch) return false;
  if (!state.suspended) { state.frozen = ClockLocked(); state.clock_start = __real_enet_time_get(); }
  state.epoch = epoch; state.control_epoch = epoch; state.control_pause = true; state.suspended = true;
  if (serial) *serial = state.control_serial;
  state.changed.notify_all(); return true;
}
bool CurrentControl(std::uint64_t epoch, std::uint64_t serial, bool pause)
{
  std::lock_guard guard(state.lock);
  return state.active && state.control_epoch==epoch && state.control_serial==serial && state.control_pause==pause;
}
bool Resume(std::uint64_t epoch, std::uint64_t serial)
{
  std::lock_guard guard(state.lock);
  if (!state.active || !state.suspended || !state.failure.empty() || epoch != state.epoch ||
      serial == 0 || serial != state.control_serial || epoch != state.control_epoch || state.control_pause) return false;
  for (const auto& [socket, endpoint] : state.endpoints) if (!endpoint.incoming.empty()) return false;
  for (const auto& queue : state.outgoing) if (!queue.empty()) return false;
  if (!state.deliveries.empty()) return false;
  state.clock_offset += __real_enet_time_get() - state.clock_start;
  state.suspended = false; state.changed.notify_all(); return true;
}
void Close()
{
  std::lock_guard guard(state.lock);
  // Native peers are released by the official NetplaySession after this call.
  // Keep endpoint records until their destructors call Detach; a new session
  // cannot reuse those sockets while the previous one is still alive.
  state.active = false; state.suspended = false; state.cpu_run_requested = false;
  for (auto& [socket, endpoint] : state.endpoints) { endpoint.incoming.clear(); endpoint.bytes = 0; }
  for (auto& queue : state.outgoing) queue.clear();
  state.outgoing_bytes.fill(0); state.deliveries.clear(); state.changed.notify_all();
}
void Fail(const char* reason) { std::lock_guard guard(state.lock); FailLocked(reason); }
std::string Failure() { std::lock_guard guard(state.lock); return state.failure; }
std::vector<std::uint8_t> TakeOutgoing(unsigned remote, unsigned timeout)
{
  std::unique_lock guard(state.lock);
  if (!SlotAllowed(remote) || remote == state.slot || (!state.host && remote != 1)) return {};
  state.changed.wait_for(guard, std::chrono::milliseconds(std::min(timeout, 1000u)),
      [&] { return !state.active || !state.outgoing[remote].empty(); });
  if (!state.active || state.outgoing[remote].empty()) return {};
  auto frame = std::move(state.outgoing[remote].front()); state.outgoing[remote].pop_front();
  state.outgoing_bytes[remote] -= frame.size(); state.changed.notify_all(); return frame;
}
int Deliver(unsigned remote, std::uint64_t id, std::span<const std::uint8_t> frame)
{
  std::lock_guard guard(state.lock);
  if (!state.active || id == 0 || !SlotAllowed(remote) || remote == state.slot ||
      (!state.host && remote != 1) || frame.size() < 9 || frame.size() > MAX_DATAGRAM + 8 ||
      std::memcmp(frame.data(), "DPL1", 4) != 0 || frame[4] != remote || frame[5] != state.slot ||
      ((unsigned(frame[6]) << 8) | frame[7]) != frame.size() - 8) return -1;
  if (auto it = state.deliveries.find(id); it != state.deliveries.end())
    return it->second.slot == remote && std::equal(frame.begin(), frame.end(), it->second.frame.begin(), it->second.frame.end())?1:-1;
  Endpoint* endpoint = state.host ? Server() : Client();
  if (!endpoint || !state.admit_guests || endpoint->bytes + frame.size() > WINDOW_BYTES || state.deliveries.size() >= 4096) return 0;
  ENetAddress from = state.host ? SyntheticGuest(remote) :
      ENetAddress{htonl(INADDR_LOOPBACK), static_cast<enet_uint16>(state.port)};
  endpoint->incoming.push_back(Datagram{from, {frame.begin()+8,frame.end()}, id});
  endpoint->bytes += frame.size() - 8;
  state.deliveries.emplace(id, Delivery{remote, {frame.begin(),frame.end()}, false});
  state.changed.notify_all(); return 1;
}
bool AwaitDelivery(std::uint64_t id, unsigned timeout)
{
  std::unique_lock guard(state.lock);
  state.changed.wait_for(guard, std::chrono::milliseconds(std::min(timeout, 1000u)), [&] {
    auto it = state.deliveries.find(id); return !state.active || it == state.deliveries.end() || it->second.consumed;
  });
  auto it = state.deliveries.find(id);
  if (!state.active || it == state.deliveries.end() || !it->second.consumed) return false;
  state.deliveries.erase(it); return true;
}
bool Drained()
{
  std::lock_guard guard(state.lock);
  if (!state.active || !state.failure.empty()) return false;
  for (const auto& [socket, endpoint] : state.endpoints) if (!endpoint.incoming.empty()) return false;
  for (const auto& queue : state.outgoing) if (!queue.empty()) return false;
  if (!state.deliveries.empty()) return false;
  return true;
}

enet_uint32 WrappedTime()
{
  std::lock_guard guard(state.lock);
  return state.active ? ClockLocked() : __real_enet_time_get();
}
int WrappedSend(ENetSocket socket, const ENetAddress* to, const ENetBuffer* buffers, size_t count)
{
  std::unique_lock guard(state.lock);
  auto it = state.endpoints.find(socket);
  if (!state.active || it == state.endpoints.end()) { guard.unlock(); return __real_enet_socket_send(socket,to,buffers,count); }
  if (!to || !buffers || count == 0) return -1;
  std::size_t length = 0;
  for (std::size_t i=0;i<count;++i) { if ((buffers[i].dataLength && !buffers[i].data) || buffers[i].dataLength > MAX_DATAGRAM-length) { FailLocked("DOLPHIN_DATAGRAM_SIZE"); return -1; } length += buffers[i].dataLength; }
  if (length == 0) return -1;
  std::vector<std::uint8_t> data; data.reserve(length);
  for (std::size_t i=0;i<count;++i) { const auto* bytes=static_cast<const std::uint8_t*>(buffers[i].data); data.insert(data.end(),bytes,bytes+buffers[i].dataLength); }
  const auto from = LocalAddress(it->second);
  if (to->host == htonl(INADDR_LOOPBACK))
  {
    if (Endpoint* target = Destination(to->port))
    {
      if (target->bytes + length > WINDOW_BYTES) { FailLocked("DOLPHIN_LOCAL_WINDOW"); return -1; }
      target->incoming.push_back(Datagram{from,std::move(data),0}); target->bytes += length;
      state.changed.notify_all(); return static_cast<int>(length);
    }
  }
  unsigned remote = 1;
  if (state.host)
  {
    const unsigned synthetic = ntohl(to->host);
    remote = synthetic & 0xffu;
    if (!it->second.server || (synthetic & 0xffffff00u) != 0x7f000000u ||
        to->port != 40000+remote || remote == 1 || !SlotAllowed(remote))
    { FailLocked("DOLPHIN_LINK_ADDRESS"); return -1; }
  }
  else if (it->second.server || to->host != htonl(INADDR_LOOPBACK) || to->port != state.port)
  { FailLocked("DOLPHIN_GUEST_ADDRESS"); return -1; }
  auto frame=Frame(state.slot,remote,data);
  state.changed.wait(guard,[&] { return !state.active || !state.failure.empty() || state.outgoing_bytes[remote]+frame.size()<=WINDOW_BYTES; });
  if (!state.active || !state.failure.empty()) return -1;
  state.outgoing_bytes[remote] += frame.size(); state.outgoing[remote].push_back(std::move(frame));
  state.changed.notify_all(); return static_cast<int>(length);
}
int WrappedReceive(ENetSocket socket, ENetAddress* from, ENetBuffer* buffers, size_t count)
{
  std::unique_lock guard(state.lock);
  auto it=state.endpoints.find(socket);
  if (!state.active || it==state.endpoints.end()) { guard.unlock(); return __real_enet_socket_receive(socket,from,buffers,count); }
  auto& endpoint=it->second; if (endpoint.incoming.empty()) return 0;
  if (!from || !buffers || count == 0) return -1;
  const auto& datagram=endpoint.incoming.front(); std::size_t capacity=0;
  for(std::size_t i=0;i<count;++i) { if(buffers[i].dataLength && !buffers[i].data) return -1; capacity+=buffers[i].dataLength; }
  if(capacity<datagram.data.size()) { FailLocked("DOLPHIN_RECEIVE_TRUNCATION"); return -1; }
  std::size_t offset=0;
  for(std::size_t i=0;i<count && offset<datagram.data.size();++i) { const auto n=std::min(buffers[i].dataLength,datagram.data.size()-offset); std::memcpy(buffers[i].data,datagram.data.data()+offset,n); offset+=n; }
  *from=datagram.from; const auto length=datagram.data.size(); const auto delivery=datagram.delivery;
  endpoint.bytes-=length; endpoint.incoming.pop_front();
  if(delivery) if(auto found=state.deliveries.find(delivery);found!=state.deliveries.end()) found->second.consumed=true;
  state.changed.notify_all(); return static_cast<int>(length);
}
int WrappedWait(ENetSocket socket, enet_uint32* condition, enet_uint32 timeout)
{
  std::unique_lock guard(state.lock);
  auto it=state.endpoints.find(socket);
  if (!state.active || it==state.endpoints.end()) { guard.unlock(); return __real_enet_socket_wait(socket,condition,timeout); }
  if(!condition) return -1;
  const auto requested=*condition;
  state.changed.wait_for(guard,std::chrono::milliseconds(std::min(timeout,1000u)),[&] {
    auto found=state.endpoints.find(socket); return !state.active || found==state.endpoints.end() || !found->second.incoming.empty();
  });
  auto found=state.endpoints.find(socket);
  *condition=0;
  if(found!=state.endpoints.end() && !found->second.incoming.empty() && (requested & ENET_SOCKET_WAIT_RECEIVE)) *condition|=ENET_SOCKET_WAIT_RECEIVE;
  if(requested & ENET_SOCKET_WAIT_SEND) *condition|=ENET_SOCKET_WAIT_SEND;
  return 0;
}
}

extern "C" enet_uint32 __wrap_enet_time_get() { return Common::StationDolphin::WrappedTime(); }
extern "C" int __wrap_enet_socket_send(ENetSocket s,const ENetAddress* a,const ENetBuffer* b,size_t n) { return Common::StationDolphin::WrappedSend(s,a,b,n); }
extern "C" int __wrap_enet_socket_receive(ENetSocket s,ENetAddress* a,ENetBuffer* b,size_t n) { return Common::StationDolphin::WrappedReceive(s,a,b,n); }
extern "C" int __wrap_enet_socket_wait(ENetSocket s,enet_uint32* c,enet_uint32 t) { return Common::StationDolphin::WrappedWait(s,c,t); }
