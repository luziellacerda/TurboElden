// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>
#include <span>
#include <string>
#include <vector>
#include <enet/enet.h>

// This transport is opt-in. Ordinary Dolphin always uses the real ENet functions.
namespace Common::StationDolphin
{
constexpr std::size_t MAX_DATAGRAM = 1392;
constexpr std::size_t WINDOW_BYTES = 256 * 1024;
bool Configure(bool host, unsigned slot, unsigned slot_mask, unsigned port, std::uint64_t epoch);
bool Active();
bool IsHost();
unsigned ExpectedSlotMask();
bool Suspended();
// Only a trusted human-exit action may authorize engine destruction.
bool AuthorizeHumanExit();
bool HumanExitAllowed();
// Records a permanent native failure and freezes ENet time; never disconnects.
bool BlockAutomaticStop(const char* reason);
// CPU boot/unpause requests are retained while a signed recovery barrier is active.
bool DeferCPURun();
bool ConsumeCPURunRequest();
void Attach(ENetHost* host, bool server);
void Detach(ENetHost* host);
void AdmitGuests();
unsigned SlotForAddress(const ENetAddress& address);
bool Pause(std::uint64_t epoch);
bool PublishControl(std::uint64_t epoch, std::uint64_t serial, bool pause);
bool EmergencySuspend(std::uint64_t epoch, std::uint64_t* serial);
bool CurrentControl(std::uint64_t epoch, std::uint64_t serial, bool pause);
bool Resume(std::uint64_t epoch, std::uint64_t serial);
void Close();
void Fail(const char* reason);
std::string Failure();
// One authenticated link per remote slot. The caller preserves complete frames.
std::vector<std::uint8_t> TakeOutgoing(unsigned remote_slot, unsigned timeout_ms);
// 1 accepted/idempotent, 0 bounded backpressure/not attached yet, -1 invalid.
int Deliver(unsigned authenticated_remote_slot, std::uint64_t delivery_id,
             std::span<const std::uint8_t> frame);
// A queued frame is NOT a delivery acknowledgement. It becomes delivered only
// after the ENet socket receive wrapper has copied the complete datagram.
bool AwaitDelivery(std::uint64_t delivery_id, unsigned timeout_ms);
bool Drained();
}
