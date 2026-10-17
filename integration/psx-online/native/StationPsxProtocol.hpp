// SPDX-License-Identifier: GPL-2.0-or-later
// Isolated protocol component. Not linked into libmain or enabled in the app.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>
#include <string>
#include <vector>

namespace station::psx {
constexpr std::size_t MaxPayload=1392, MaxPacket=1400, LinkWindow=256*1024;
constexpr std::size_t MaxState=16*1024*1024, FrameWindow=32, ReceiptWindow=512;
constexpr std::uint64_t MaxEpoch=std::uint64_t(INT64_MAX)>>3;
constexpr std::uint16_t StandardPadBits=0x3fff; // libretro JOYPAD IDs 0..13 only.
using Digest=std::array<std::uint8_t,32>;
Digest sha256(std::span<const std::uint8_t>);

enum class Result { Ok, Duplicate, Wait, Paused, Backpressure, Invalid,
    WrongOwner, Stale, Superseded, Failed, HumanRequired, Closed };
enum class Kind : std::uint8_t { Input=1, Frame=2, StateBegin=3, StateChunk=4,
    StateEnd=5, RequestState=6, Commit=7 };
enum class Outcome : std::uint8_t { Executed=1, Superseded=2, AppliedState=3, OwnerFailed=4 };
struct Config {
    std::uint8_t localSlot; // exact authenticated two-slot roster: host=1, guest=2.
    std::uint64_t epoch;
    std::size_t stateBytes; // actual loaded Core::serializeSize(), exact and <= MaxState.
    Digest identity; // SHA256 of exact ROM/core/runtime/options/profile manifest.
    std::uint32_t inputDelay{4}; // signed fixed pipeline delay; owner samples N for N+D.

};
struct Stamp {
    std::uint64_t epoch{}, stateSerial{}, frame{};
    bool operator==(const Stamp&) const = default;
};
struct Frame {
    Stamp stamp;
    std::array<std::uint16_t,2> pads{};
    bool operator==(const Frame&) const = default;
};
struct Lease {
    Frame frame;
    std::uint64_t token{};
    bool operator==(const Lease&) const = default;
};
struct PauseAck {
    std::uint64_t epoch{}, controlSerial{}, nextFrame{}, stateSerial{};
    bool valid{}; // ONLY after the actual owner checkpoint, never an IO request.
};
struct Commit {
    Kind kind;
    Outcome outcome;
    Stamp stamp;
};
struct Status {
    PauseAck pause;
    std::uint64_t epoch{}, controlSerial{}, nextFrame{}, stateSerial{};
    bool paused{}, stateReady{}, initialStateSynced{}, inFrame{}, applyingState{}, failed{}, closed{};
};
using ApplyState=bool(*)(void*,std::span<const std::uint8_t>);

// This object performs no core/SDL/JNI/file/network operation and owns no timer.
// Only owner* calls may run on the original LibretroPlayer SDL/core owner thread.
// The adapter must reuse the loaded Core and original input callbacks; never
// call retro_run from a network thread or advance frames to obtain a pause ACK.
class Session {
public:
    explicit Session(Config);
    ~Session();
    Session(const Session&)=delete;
    Session& operator=(const Session&)=delete;
    Result control(std::uint64_t epoch,std::uint64_t localSerial,bool pause,bool visible);
    Result resume(std::uint64_t epoch,std::uint64_t exactLocalSerial);
    Result ownerCheckpoint();
    bool needsLocalSample() const;
    Result ownerSampleLocal(std::uint16_t originalPadBits);
    Result ownerBegin(Lease&);
    // Host emits canonical FRAME only here, after the actual retro_run.
    // A guest cannot advance ahead of the authoritative host snapshot cursor.
    Result ownerComplete(const Lease&); // ONLY after retro_run returned successfully.
    Result ownerAbort(const Lease&,const char* category); // clears lease, no Executed.
    Result ownerPublishState(std::vector<std::uint8_t>,std::uint64_t actualNextFrame);
    Result ownerApplyState(ApplyState,void* originalCore);
    bool stateRequested() const;
    Result requestState();
    Result authorizeHumanExit(); // trusted explicit user action only; no IO timeout.
    Result automaticStop(const char* category); // records failure, does NOT exit.
    Result ownerClose();
    Status status() const;
    std::string failure() const;
    bool drained() const; // ALSO check Java/v3 outgoing/link windows externally.

    // PXL1 packets, exact versioned PSX framing. Never Dolphin/ENet datagrams.
    // Deliver Ok means whole payload validated+copied to a BOUNDED real mailbox.
    // copied(id) is a TRANSPORT receipt, NOT proof of retro_run or state applied.
    // This permits CPU-paused STATE recovery without circular link-drain waits.
    Result deliver(std::uint8_t authenticatedRemoteSlot,std::uint64_t uniqueId,
                   std::span<const std::uint8_t> completePacket);
    bool copied(std::uint64_t uniqueId) const;
    Result releaseReceipt(std::uint64_t uniqueId); // after outer v3 DATA ACK.
    std::vector<std::uint8_t> takeOutgoing(); // one whole packet, nonblocking.
    // IO worker only: wait for an outbound notification, never dequeue or run a
    // core. Bounded to 100ms; the actual owner is never permitted to block here.
    bool awaitOutgoing(std::uint32_t timeoutMs);
    bool takeCommit(Commit&); // separate GAMEPLAY proof, never the DATA byte ACK.
private:
    struct Impl;
    std::unique_ptr<Impl> p_;
};
} // namespace station::psx
