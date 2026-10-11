// Candidate only. Not linked into a shipped emulator or the R126 APK.
// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <span>
#include <thread>

namespace station::explus {

constexpr std::size_t kMaxSlots = 5;
constexpr std::size_t kWindow = 32;
constexpr std::size_t kMaxStateBytes = 16 * 1024 * 1024;
using StateApply = bool (*)(void*, std::span<const std::uint8_t>);
enum class Backend : std::uint8_t { Snes9x = 1, GenesisPlusGx = 2 };
enum class Result { Ok, Duplicate, Consumed, Wait, Paused, Backpressure,
    Invalid, Conflict, Stale, WrongEpoch, WrongOwner, HumanRequired };

struct Config {
    Backend backend;
    std::uint8_t slots;
    std::uint8_t localSlot; // Station slots are 1-based; only the host commits frames.
    std::uint64_t epoch;
};

struct Frame {
    std::uint64_t epoch{};
    std::uint64_t index{};
    std::uint8_t slots{};
    std::array<std::uint16_t, kMaxSlots> pads{};
    bool operator==(const Frame&) const = default;
};

struct PauseAck {
    std::uint64_t epoch{};
    std::uint64_t serial{};
    std::uint64_t nextFrame{};
    bool valid{}; // Set only by the actual owner at a checkpoint after the last frame.
};

struct Lease {
    Frame frame{};
    std::uint64_t deliveryId{};
    std::uint64_t token{};
};

struct Consumption {
    std::uint64_t deliveryId{};
    std::uint64_t epoch{};
    std::uint64_t frame{};
};

std::uint16_t allowedBits(Backend backend);
bool validConfig(Config config);

// Host-side input assembly. Identity is provided by the authenticated endpoint,
// not read from payloads. This is a primitive, not a network/auth implementation.
class InputAssembly {
public:
    explicit InputAssembly(Config config);
    Result offer(std::uint8_t authenticatedSlot, std::uint8_t claimedSlot,
                 std::uint64_t epoch, std::uint64_t frame, std::uint16_t pads);
    Result complete(Frame& frame) const;
    Result advance();
    Result reset(std::uint64_t epoch, std::uint64_t nextFrame);
    static constexpr std::size_t capacity() { return kWindow; }
private:
    struct InputRow { Frame frame{}; std::uint8_t present{}; bool used{}; };
    Config config_;
    std::uint64_t next_{};
    mutable std::mutex mutex_;
    std::array<InputRow, kWindow> rows_{};
};

// Nonblocking owner gate. No network I/O, wait, GPU work, timers, files or
// timeout-driven shutdown occur here. The original worker remains the only
// caller that may execute core frames and apply state.
class FrameGate {
public:
    explicit FrameGate(Config config);
    Result requestPause(std::uint64_t epoch, std::uint64_t serial);
    Result ownerCheckpoint();
    PauseAck pauseAck() const;
    Result ownerApplyState(std::uint64_t epoch, std::uint64_t serial,
                          std::uint64_t nextFrame, std::span<const std::uint8_t>,
                          StateApply apply, void* originalCore);
    Result resume(std::uint64_t epoch, std::uint64_t serial);
    Result enqueue(std::uint8_t authenticatedHostSlot, const Frame& frame,
                   std::uint64_t uniqueDeliveryId);
    Result begin(Lease& lease);
    Result complete(const Lease& lease, Consumption& consumed);
    Result captureLocal(std::uint8_t normalPlayer, unsigned keyCode, bool pushed,
                        std::uint16_t& localPads);
    void clearLocal();
    std::uint16_t localPads() const;
    std::uint64_t nextFrame() const;
    Result authorizeHumanExit();
    Result requestExit();
    bool closed() const;
    static constexpr std::size_t capacity() { return kWindow; }
    static constexpr std::size_t boundedStorageBytes() {
        return sizeof(FrameGate);
    }
private:
    struct Row { Frame frame{}; std::uint64_t id{}; bool used{}; };
    Result checkOwnerLocked();
    Result checkpointLocked();
    Config config_;
    mutable std::mutex mutex_;
    std::thread::id owner_{};
    std::array<Row, kWindow> rows_{};
    std::array<Row, kWindow> consumed_{};
    std::uint64_t next_{};
    std::uint64_t wantedEpoch_{};
    std::uint64_t wantedSerial_{};
    std::uint64_t ackSerial_{};
    std::uint64_t highestDelivery_{};
    std::uint64_t nextLease_{1};
    std::uint16_t localPads_{};
    Lease executing_{};
    bool hasOwner_{};
    bool paused_{true};
    bool stateApplied_{};
    bool inFrame_{};
    bool applyingState_{};
    bool humanAuthorized_{};
    bool exitRequested_{};
    bool closed_{};
};

} // namespace station::explus
