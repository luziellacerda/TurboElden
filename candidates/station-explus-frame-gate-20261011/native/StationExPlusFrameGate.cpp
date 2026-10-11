// SPDX-License-Identifier: GPL-3.0-or-later
#include "StationExPlusFrameGate.hpp"

#include <limits>
#include <stdexcept>

namespace station::explus {

std::uint16_t allowedBits(Backend backend) {
    switch (backend) {
    case Backend::Snes9x: return 0xfff0; // Actual SnesKey bit positions 4..15.
    case Backend::GenesisPlusGx: return 0x0fff; // Actual MdKey positions code-1.
    }
    return 0;
}

bool validConfig(Config c) {
    const unsigned max = c.backend == Backend::Snes9x ? 5 :
        c.backend == Backend::GenesisPlusGx ? 4 : 0;
    return max && c.slots >= 2 && c.slots <= max &&
        c.localSlot >= 1 && c.localSlot <= c.slots && c.epoch > 0;
}

InputAssembly::InputAssembly(Config c) : config_(c) {
    if (!validConfig(c) || c.localSlot != 1)
        throw std::invalid_argument("Invalid authenticated host configuration");
}

Result InputAssembly::offer(std::uint8_t auth, std::uint8_t claimed,
    std::uint64_t epoch, std::uint64_t index, std::uint16_t pads) {
    std::lock_guard lock{mutex_};
    if (auth < 1 || auth > config_.slots || auth != claimed ||
        (pads & ~allowedBits(config_.backend))) return Result::Invalid;
    if (epoch != config_.epoch) return Result::WrongEpoch;
    if (index < next_) return Result::Stale;
    if (index - next_ >= kWindow) return Result::Backpressure;
    auto& row = rows_[index % kWindow];
    if (!row.used) {
        row = {};
        row.used = true;
        row.frame = {epoch, index, config_.slots, {}};
    }
    if (row.frame.epoch != epoch || row.frame.index != index) return Result::Conflict;
    const auto bit = std::uint8_t(1U << (auth - 1));
    if (row.present & bit) return row.frame.pads[auth - 1] == pads ?
        Result::Duplicate : Result::Conflict;
    row.frame.pads[auth - 1] = pads;
    row.present |= bit;
    return Result::Ok;
}

Result InputAssembly::complete(Frame& frame) const {
    std::lock_guard lock{mutex_};
    const auto& row = rows_[next_ % kWindow];
    if (!row.used || row.frame.index != next_ ||
        row.present != std::uint8_t((1U << config_.slots) - 1)) return Result::Wait;
    frame = row.frame;
    return Result::Ok;
}

Result InputAssembly::advance() {
    std::lock_guard lock{mutex_};
    auto& row = rows_[next_ % kWindow];
    if (!row.used || row.frame.index != next_ ||
        row.present != std::uint8_t((1U << config_.slots) - 1)) return Result::Wait;
    if (next_ == std::numeric_limits<std::uint64_t>::max()) return Result::Invalid;
    row = {};
    ++next_;
    return Result::Ok;
}

Result InputAssembly::reset(std::uint64_t epoch, std::uint64_t next) {
    std::lock_guard lock{mutex_};
    if (epoch < config_.epoch || next == std::numeric_limits<std::uint64_t>::max())
        return Result::Invalid;
    config_.epoch = epoch;
    next_ = next;
    rows_ = {};
    return Result::Ok;
}

FrameGate::FrameGate(Config c) : config_(c), wantedEpoch_(c.epoch) {
    if (!validConfig(c)) throw std::invalid_argument("Invalid session configuration");
}

Result FrameGate::requestPause(std::uint64_t epoch, std::uint64_t serial) {
    std::lock_guard lock{mutex_};
    if (closed_ || !serial || epoch < wantedEpoch_) return Result::Invalid;
    if (serial < wantedSerial_) return Result::Stale;
    if (serial == wantedSerial_) return epoch == wantedEpoch_ ?
        Result::Duplicate : Result::Conflict;
    wantedEpoch_ = epoch;
    wantedSerial_ = serial;
    return Result::Ok;
}

Result FrameGate::checkOwnerLocked() {
    const auto id = std::this_thread::get_id();
    if (!hasOwner_) { owner_ = id; hasOwner_ = true; }
    return owner_ == id ? Result::Ok : Result::WrongOwner;
}

Result FrameGate::checkpointLocked() {
    if (checkOwnerLocked() != Result::Ok) return Result::WrongOwner;
    if (inFrame_ || applyingState_) return Result::Wait;
    if (exitRequested_ && humanAuthorized_) {
        closed_ = true;
        paused_ = true;
        rows_ = {};
        return Result::HumanRequired;
    }
    if (closed_) return Result::HumanRequired;
    if (wantedSerial_ > ackSerial_) {
        paused_ = true;
        stateApplied_ = false;
        config_.epoch = wantedEpoch_;
        ackSerial_ = wantedSerial_;
        localPads_ = 0;
        rows_ = {};
        // Consumed receipt history remains so a transport retry can distinguish
        // old consumed delivery from an unexecuted frame. Epoch still validates.
    }
    return paused_ ? Result::Paused : Result::Ok;
}

Result FrameGate::ownerCheckpoint() {
    std::lock_guard lock{mutex_};
    return checkpointLocked();
}

PauseAck FrameGate::pauseAck() const {
    std::lock_guard lock{mutex_};
    return {config_.epoch, ackSerial_, next_,
        !closed_ && hasOwner_ && paused_ && !inFrame_ && !applyingState_ && ackSerial_ &&
        ackSerial_ == wantedSerial_ && config_.epoch == wantedEpoch_};
}

Result FrameGate::ownerApplyState(std::uint64_t epoch, std::uint64_t serial,
    std::uint64_t next, std::span<const std::uint8_t> state,
    StateApply apply, void* core) {
    std::unique_lock lock{mutex_};
    if (checkOwnerLocked() != Result::Ok) return Result::WrongOwner;
    if (closed_ || inFrame_ || applyingState_ || !paused_ || !serial || serial != ackSerial_ ||
        serial != wantedSerial_ || epoch != config_.epoch || epoch != wantedEpoch_ ||
        next == std::numeric_limits<std::uint64_t>::max() || !apply || state.empty() ||
        state.size() > kMaxStateBytes) return Result::Invalid;
    applyingState_ = true;
    stateApplied_ = false;
    lock.unlock(); // The core callback runs on its owner, never under a network lock.
    bool succeeded{};
    try { succeeded = apply(core, state); } catch (...) { succeeded = false; }
    lock.lock();
    applyingState_ = false;
    if (!succeeded || serial != wantedSerial_ || epoch != wantedEpoch_)
        return Result::Invalid;
    next_ = next;
    rows_ = {};
    stateApplied_ = true;
    return Result::Ok;
}

Result FrameGate::resume(std::uint64_t epoch, std::uint64_t serial) {
    std::lock_guard lock{mutex_};
    if (closed_ || inFrame_ || applyingState_ || !paused_ || !hasOwner_ || !stateApplied_ || !serial ||
        serial != ackSerial_ || serial != wantedSerial_ || epoch != config_.epoch ||
        epoch != wantedEpoch_) return Result::Invalid;
    paused_ = false;
    return Result::Ok;
}

Result FrameGate::enqueue(std::uint8_t host, const Frame& f, std::uint64_t id) {
    std::lock_guard lock{mutex_};
    if (host != 1 || !id || closed_ || f.slots != config_.slots) return Result::Invalid;
    for (std::size_t i = 0; i < f.pads.size(); ++i)
        if ((i >= f.slots && f.pads[i]) || (f.pads[i] & ~allowedBits(config_.backend)))
            return Result::Invalid;
    for (const auto& row : consumed_)
        if (row.used && row.id == id)
            return row.frame == f ? Result::Consumed : Result::Conflict;
    for (const auto& row : rows_)
        if (row.used && row.id == id)
            return row.frame == f ? Result::Duplicate : Result::Conflict;
    if (f.epoch != config_.epoch || f.epoch != wantedEpoch_) return Result::WrongEpoch;
    if (!stateApplied_ || ackSerial_ != wantedSerial_) return Result::Paused;
    if (f.index < next_) return Result::Stale;
    if (f.index - next_ >= kWindow) return Result::Backpressure;
    auto& row = rows_[f.index % kWindow];
    if (row.used) return row.id == id && row.frame == f ?
        Result::Duplicate : Result::Conflict;
    // Ordered delivery IDs are allocated by the endpoint; a reused lower ID is
    // invalid after the bounded receipt history has expired, not new input.
    if (id <= highestDelivery_) return Result::Stale;
    row = {f, id, true};
    highestDelivery_ = id;
    return Result::Ok;
}

Result FrameGate::begin(Lease& out) {
    std::lock_guard lock{mutex_};
    if (checkOwnerLocked() != Result::Ok) return Result::WrongOwner;
    if (inFrame_) return Result::Conflict;
    const auto status = checkpointLocked();
    if (status != Result::Ok) return status;
    const auto& row = rows_[next_ % kWindow];
    if (!row.used || row.frame.epoch != config_.epoch || row.frame.index != next_)
        return Result::Wait;
    if (nextLease_ == std::numeric_limits<std::uint64_t>::max()) return Result::Invalid;
    executing_ = {row.frame, row.id, nextLease_++};
    out = executing_;
    inFrame_ = true;
    return Result::Ok;
}

Result FrameGate::complete(const Lease& lease, Consumption& out) {
    std::lock_guard lock{mutex_};
    if (checkOwnerLocked() != Result::Ok) return Result::WrongOwner;
    if (!inFrame_ || lease.token != executing_.token ||
        lease.deliveryId != executing_.deliveryId || lease.frame != executing_.frame)
        return Result::Invalid;
    if (next_ == std::numeric_limits<std::uint64_t>::max()) return Result::Invalid;
    auto& row = rows_[next_ % kWindow];
    consumed_[next_ % kWindow] = row;
    out = {row.id, row.frame.epoch, row.frame.index};
    row = {};
    inFrame_ = false;
    ++next_;
    checkpointLocked(); // A requested pause becomes acknowledged AFTER actual execution.
    return Result::Ok;
}

Result FrameGate::captureLocal(std::uint8_t player, unsigned key, bool pushed,
    std::uint16_t& out) {
    std::lock_guard lock{mutex_};
    if (closed_ || player != 0) return Result::Invalid;
    unsigned bit{};
    if (config_.backend == Backend::Snes9x) {
        if (key < 4 || key > 15) return Result::Invalid;
        bit = key;
    } else {
        if (key < 1 || key > 12) return Result::Invalid;
        bit = key - 1;
    }
    const auto mask = std::uint16_t(1U << bit);
    localPads_ = pushed ? std::uint16_t(localPads_ | mask) :
        std::uint16_t(localPads_ & ~mask);
    out = localPads_;
    return Result::Ok;
}

void FrameGate::clearLocal() { std::lock_guard lock{mutex_}; localPads_ = 0; }
std::uint16_t FrameGate::localPads() const {
    std::lock_guard lock{mutex_}; return localPads_;
}
std::uint64_t FrameGate::nextFrame() const {
    std::lock_guard lock{mutex_}; return next_;
}
Result FrameGate::authorizeHumanExit() {
    std::lock_guard lock{mutex_};
    if (closed_) return Result::Invalid;
    humanAuthorized_ = true;
    return Result::Ok;
}
Result FrameGate::requestExit() {
    std::lock_guard lock{mutex_};
    if (!humanAuthorized_) return Result::HumanRequired;
    exitRequested_ = true;
    return Result::Ok;
}
bool FrameGate::closed() const { std::lock_guard lock{mutex_}; return closed_; }

} // namespace station::explus
