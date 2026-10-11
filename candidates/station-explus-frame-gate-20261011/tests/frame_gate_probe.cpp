// Isolated synthetic-owner fixtures. Does not execute Snes9x or Genesis Plus GX.
// SPDX-License-Identifier: GPL-3.0-or-later
#include "StationExPlusFrameGate.hpp"
#include "StationSnapshotGuard.hpp"

#include <atomic>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <thread>
#include <vector>

using namespace station::explus;
namespace {
unsigned checks{};
void check(bool ok, const char* what) {
    ++checks;
    if (!ok) throw std::runtime_error(what);
}
void eq(Result got, Result expected, const char* what) { check(got == expected, what); }
struct SyntheticOwner { unsigned writes{}; std::thread::id writer{}; std::uint8_t state{}; };
bool applyState(void* value, std::span<const std::uint8_t> state) {
    auto& owner = *static_cast<SyntheticOwner*>(value);
    ++owner.writes;
    owner.writer = std::this_thread::get_id();
    owner.state = state[0];
    return true;
}
bool rejectState(void*, std::span<const std::uint8_t>) { return false; }
bool throwState(void*, std::span<const std::uint8_t>) { throw std::runtime_error("state"); }
constexpr std::array<std::uint8_t, 1> stateBytes{17};
void initialise(FrameGate& gate, SyntheticOwner& owner, std::uint64_t epoch = 1,
                std::uint64_t serial = 1, std::uint64_t first = 0) {
    check(!gate.pauseAck().valid, "No manufactured ACK before owner checkpoint");
    eq(gate.requestPause(epoch, serial), Result::Ok, "Request pause");
    check(!gate.pauseAck().valid, "Request alone is not ACK");
    eq(gate.resume(epoch, serial), Result::Invalid, "No resume before real owner");
    eq(gate.ownerCheckpoint(), Result::Paused, "Owner paused");
    check(gate.pauseAck().valid, "Real owner ACK");
    eq(gate.resume(epoch, serial), Result::Invalid, "No resume before state callback");
    eq(gate.ownerApplyState(epoch, serial, first, stateBytes, applyState, &owner),
       Result::Ok, "Actual callback applied on owner");
    check(owner.writer == std::this_thread::get_id(), "State owner identity");
    eq(gate.resume(epoch, serial), Result::Ok, "Resume exact epoch and serial");
}
Frame packet(Backend b, unsigned count, std::uint64_t index, std::uint64_t epoch = 1) {
    Frame f{epoch, index, static_cast<std::uint8_t>(count), {}};
    for (unsigned p = 0; p < count; ++p)
        f.pads[p] = static_cast<std::uint16_t>((1U << (p + (b == Backend::Snes9x ? 4 : 0))));
    return f;
}
void configurationAndKeys() {
    for (auto b : {Backend::Snes9x, Backend::GenesisPlusGx}) {
        check(!validConfig({b, 1, 1, 1}), "One-player room not approved by primitive");
        check(!validConfig({b, 2, 0, 1}), "Slot zero invalid");
        check(!validConfig({b, 2, 3, 1}), "Slot outside exact roster invalid");
        check(!validConfig({b, 2, 1, 0}), "Epoch zero invalid");
        FrameGate gate{{b, 2, 2, 1}};
        std::uint16_t out{};
        check(!gate.closed(), "Starts open and paused");
        eq(gate.captureLocal(1, 7, true, out), Result::Invalid, "Do not write remote pad via local deviceId");
        const unsigned lo = b == Backend::Snes9x ? 4 : 1;
        const unsigned hi = b == Backend::Snes9x ? 15 : 12;
        for (unsigned key = lo; key <= hi; ++key)
            eq(gate.captureLocal(0, key, true, out), Result::Ok, "Original key accepted");
        check(out == allowedBits(b), "All original digital controls retain exact bits");
        for (unsigned key = lo; key <= hi; ++key)
            eq(gate.captureLocal(0, key, false, out), Result::Ok, "Original key release");
        check(out == 0, "All releases clear staging");
        eq(gate.captureLocal(0, 0, true, out), Result::Invalid, "Key underflow rejected");
        eq(gate.captureLocal(0, 99, true, out), Result::Invalid, "Key overflow rejected");
        eq(gate.captureLocal(0, 7, true, out), Result::Ok, "Original A accepted");
        check(out == (b == Backend::Snes9x ? 0x0080 : 0x0040), "Exact A bind retained");
        gate.clearLocal();
        check(gate.localPads() == 0, "Disconnect/focus clear staging");
    }
    check(!validConfig({Backend::GenesisPlusGx, 5, 1, 1}), "MD does not gain fifth port");
    check(!validConfig({static_cast<Backend>(99), 2, 1, 1}), "Unknown core rejected");
}
void rosterAndFrames(Backend b, unsigned count) {
    InputAssembly assembly{{b, static_cast<std::uint8_t>(count), 1, 1}};
    std::vector<std::unique_ptr<FrameGate>> gates;
    std::vector<SyntheticOwner> cores(count);
    std::vector<std::uint64_t> digests(count, 7);
    for (unsigned p = 1; p <= count; ++p) {
        gates.push_back(std::make_unique<FrameGate>(Config{b, static_cast<std::uint8_t>(count),
            static_cast<std::uint8_t>(p), 1}));
        initialise(*gates.back(), cores[p - 1]);
    }
    eq(assembly.offer(2, 1, 1, 0, 0), Result::Invalid, "Signed slot spoof rejected");
    eq(assembly.offer(static_cast<std::uint8_t>(count + 1), static_cast<std::uint8_t>(count + 1),
        1, 0, 0), Result::Invalid, "Unknown participant rejected");
    eq(assembly.offer(1, 1, 0, 0, 0), Result::WrongEpoch, "Old epoch rejected");
    eq(assembly.offer(1, 1, 1, kWindow, 0), Result::Backpressure, "Bounded future inputs");
    for (std::uint64_t index = 0; index < 160; ++index) {
        const auto canonical = packet(b, count, index);
        for (unsigned p = 1; p <= count; ++p) {
            eq(assembly.offer(static_cast<std::uint8_t>(p), static_cast<std::uint8_t>(p),
                1, index, canonical.pads[p - 1]), Result::Ok, "Exact participant input");
            Frame ready{};
            eq(assembly.complete(ready), p == count ? Result::Ok : Result::Wait,
                "Every required slot must arrive; no default neutral remote input");
            if (p == count) check(ready == canonical, "Canonical roster order");
        }
        eq(assembly.offer(1, 1, 1, index, canonical.pads[0]), Result::Duplicate,
            "Same input retry idempotent");
        eq(assembly.offer(1, 1, 1, index, 0), Result::Conflict,
            "Different input retry rejected");
        for (unsigned p = 0; p < count; ++p) {
            auto& gate = *gates[p];
            Lease lease{};
            Consumption consumed{};
            eq(gate.begin(lease), Result::Wait, "Missing canonical frame does not execute");
            check(gate.nextFrame() == index, "No skipped emulated frame while waiting");
            eq(gate.enqueue(1, canonical, index + 1), Result::Ok, "Host canonical frame staged");
            eq(gate.enqueue(1, canonical, index + 1), Result::Duplicate, "Same DATA retry pending");
            eq(gate.begin(lease), Result::Ok, "Owner obtains exactly one frame");
            eq(gate.begin(lease), Result::Conflict, "No second parallel core loop");
            auto forged = lease;
            ++forged.token;
            eq(gate.complete(forged, consumed), Result::Invalid, "Forged frame completion rejected");
            // Deliberately synthetic state hash; not an emulator performance test.
            for (auto pad : lease.frame.pads) digests[p] = (digests[p] * 16777619U) ^ pad;
            digests[p] ^= lease.frame.index;
            eq(gate.complete(lease, consumed), Result::Ok, "ACK after synthetic owner execution");
            check(consumed.deliveryId == index + 1 && consumed.frame == index && consumed.epoch == 1,
                "Receipt tied to actually consumed DATA");
            eq(gate.complete(lease, consumed), Result::Invalid, "No duplicate advancement");
            eq(gate.enqueue(1, canonical, index + 1), Result::Consumed, "Consumed retry does not execute twice");
            check(gate.nextFrame() == index + 1, "Exactly one advancement");
        }
        for (unsigned p = 1; p < count; ++p)
            check(digests[p] == digests[0], "All fixture owners use same per-slot inputs");
        eq(assembly.advance(), Result::Ok, "Advance input assembly after commit acceptance");
        eq(assembly.offer(1, 1, 1, index, 0), Result::Stale, "Past input cannot overwrite consumed frame");
    }
}
void pauseAndStateRaces() {
    FrameGate gate{{Backend::Snes9x, 2, 1, 1}};
    SyntheticOwner owner{};
    initialise(gate, owner);
    Lease lease{};
    Consumption consumed{};
    eq(gate.enqueue(1, packet(Backend::Snes9x, 2, 0), 1), Result::Ok, "Prepare frame");
    eq(gate.begin(lease), Result::Ok, "Start real owner lease");
    eq(gate.requestPause(2, 2), Result::Ok, "Pause requested during execution");
    check(!gate.pauseAck().valid, "Executing core cannot manufacture pause ACK");
    eq(gate.ownerCheckpoint(), Result::Wait, "Checkpoint waits for current frame");
    eq(gate.complete(lease, consumed), Result::Ok, "Complete before acknowledging pause");
    const auto ack = gate.pauseAck();
    check(ack.valid && ack.epoch == 2 && ack.serial == 2 && ack.nextFrame == 1,
        "Real frame boundary acknowledges correct epoch and serial");
    eq(gate.resume(1, 1), Result::Invalid, "Old READY cannot resume");
    eq(gate.ownerApplyState(2, 2, 0, stateBytes, rejectState, nullptr), Result::Invalid,
        "Failed snapshot does not enable READY");
    eq(gate.resume(2, 2), Result::Invalid, "No resume after failed state");
    eq(gate.ownerApplyState(2, 2, 0, stateBytes, throwState, nullptr), Result::Invalid,
        "Throwing snapshot does not enable READY or close");
    check(!gate.closed(), "Failed state is not automatic logical exit");
    eq(gate.ownerApplyState(2, 2, 9, {}, applyState, &owner), Result::Invalid, "Empty state rejected");
    eq(gate.ownerApplyState(2, 2, 9, stateBytes, applyState, &owner), Result::Ok, "Snapshot on owner");
    eq(gate.resume(2, 2), Result::Ok, "Fresh exact READY resumes");
    check(gate.nextFrame() == 9, "Agreed snapshot frame installed");
    eq(gate.enqueue(1, packet(Backend::Snes9x, 2, 9, 2), 2), Result::Ok, "Input for new epoch");
    eq(gate.begin(lease), Result::Ok, "New epoch frame");
    check(lease.frame.index == 9 && lease.frame.epoch == 2, "Old queue did not leak");
    eq(gate.complete(lease, consumed), Result::Ok, "New epoch consumed");
    eq(gate.requestPause(1, 3), Result::Invalid, "Epoch cannot regress");
    eq(gate.requestPause(2, 1), Result::Stale, "Serial cannot regress");
    eq(gate.requestPause(2, 2), Result::Duplicate, "Duplicate pause idempotent");
    eq(gate.requestPause(3, 2), Result::Conflict, "Same serial different epoch invalid");
    Result foreign{};
    std::thread thread([&] { foreign = gate.ownerCheckpoint(); });
    thread.join();
    eq(foreign, Result::WrongOwner, "Worker identity remains bound");
    eq(gate.requestExit(), Result::HumanRequired, "Network failure cannot quit core");
    for (unsigned i = 0; i < 1000; ++i) {
        eq(gate.begin(lease), Result::Wait, "No input, indefinite recoverable hold");
        check(!gate.closed(), "No implicit timer/missing-input shutdown");
    }
    eq(gate.authorizeHumanExit(), Result::Ok, "Trusted explicit UI human authorization");
    eq(gate.requestExit(), Result::Ok, "Request explicit exit");
    check(!gate.closed(), "Exit only observed on owner boundary");
    eq(gate.ownerCheckpoint(), Result::HumanRequired, "Owner accepts explicit exit");
    check(gate.closed() && !gate.pauseAck().valid, "Closed cannot advertise READY");
}
void storageAndValidation() {
    FrameGate gate{{Backend::GenesisPlusGx, 2, 1, 1}};
    SyntheticOwner owner{};
    initialise(gate, owner);
    const auto canonical = packet(Backend::GenesisPlusGx, 2, 0);
    eq(gate.enqueue(2, canonical, 1), Result::Invalid, "Nonhost cannot commit another player's canonical frame");
    eq(gate.enqueue(1, canonical, 0), Result::Invalid, "Unique consumption ID required");
    auto bad = canonical;
    bad.slots = 3;
    eq(gate.enqueue(1, bad, 1), Result::Invalid, "Roster expansion rejected");
    bad = canonical;
    bad.pads[2] = 1;
    eq(gate.enqueue(1, bad, 1), Result::Invalid, "Unused slots must be zero");
    bad = canonical;
    bad.pads[0] = 0xffff;
    eq(gate.enqueue(1, bad, 1), Result::Invalid, "Peripheral/unknown input bits rejected");
    for (std::uint64_t index = 0; index < kWindow; ++index)
        eq(gate.enqueue(1, packet(Backend::GenesisPlusGx, 2, index), index + 1), Result::Ok,
            "Bounded window accepts exact frames");
    eq(gate.enqueue(1, packet(Backend::GenesisPlusGx, 2, kWindow), kWindow + 1),
        Result::Backpressure, "Full queue requests backpressure; no drop or resize");
    bad = canonical;
    bad.pads[0] = 2;
    eq(gate.enqueue(1, bad, 1), Result::Conflict, "Repeated DATA ID must have identical bytes");
    eq(gate.enqueue(1, canonical, 1000), Result::Conflict, "Same frame cannot replace canonical bytes or identity");
    check(FrameGate::boundedStorageBytes() < 16 * 1024, "Gate memory constant and below16KiB");
    Lease lease{};
    Consumption consumed{};
    std::atomic<bool> go{false};
    std::thread touch([&] {
        while (!go.load()) std::this_thread::yield();
        for (unsigned i = 0; i < 10000; ++i) {
            std::uint16_t staged{};
            gate.captureLocal(0, 7, true, staged);
            gate.captureLocal(0, 7, false, staged);
        }
    });
    go.store(true);
    for (std::uint64_t index = 0; index < kWindow; ++index) {
        eq(gate.begin(lease), Result::Ok, "Owner remains independent of UI input staging");
        check(lease.frame == packet(Backend::GenesisPlusGx, 2, index), "Local UI did not overwrite remote/current pads");
        eq(gate.complete(lease, consumed), Result::Ok, "Ordered consumption");
    }
    touch.join();
    check(gate.localPads() == 0, "Concurrent final local release retained");
    eq(gate.enqueue(1, canonical, 1), Result::Consumed, "Bounded consumed retry history");
    eq(gate.enqueue(1, packet(Backend::GenesisPlusGx, 2, kWindow), kWindow + 1), Result::Ok,
        "Credit opens after real consumption");
}
void snapshotGuards() {
    // Mirrors actual SUCCESS/error values from current Snes9x snapshot.h.
    for (int status = -6; status <= 2; ++status) {
        check(snesStateSucceeded(status) == (status == 1), "Only exact SNES SUCCESS is accepted");
        if (status < 0) check(!(!status), "Legacy if(!result) demonstrably misses negative errors");
    }
    constexpr std::array<std::uint8_t, 16> version{
        'G','E','N','P','L','U','S','-','G','X',' ','1','.','5','.','3'};
    std::vector<std::uint8_t> state(68);
    auto writeLength = [&](std::uint32_t bits) {
        for (unsigned i = 0; i < 4; ++i) state[i] = std::uint8_t(bits >> (i * 8));
    };
    std::copy(version.begin(), version.end(), state.begin() + 4);
    writeLength(0xffffffc0U); // -64
    check(mdRawEnvelope(state, 64, version) == Envelope::Valid, "Bounded exact raw envelope");
    for (std::size_t size = 0; size < state.size(); ++size)
        check(mdRawEnvelope(std::span{state}.first(size), 64, version) != Envelope::Valid,
            "Every truncation rejected before core decoder");
    writeLength(0x80000000U);
    check(mdRawEnvelope(state, 64, version) == Envelope::LengthMismatch, "INT32_MIN rejected without signed overflow");
    writeLength(0);
    check(mdRawEnvelope(state, 64, version) == Envelope::CompressedUnsupported, "Zero header rejected");
    writeLength(64);
    check(mdRawEnvelope(state, 64, version) == Envelope::CompressedUnsupported, "No unbounded compressed network snapshots");
    writeLength(0xffffffc0U);
    state[4] = '?';
    check(mdRawEnvelope(state, 64, version) == Envelope::VersionMismatch, "No legacy/foreign state format");
    state[4] = 'G';
    check(mdRawEnvelope(state, 65, version) == Envelope::LengthMismatch, "Locally pinned state size required");
    std::array<std::uint8_t, 16> dest{};
    CheckedStateCursor cursor{state};
    cursor.read(dest);
    check(cursor.remaining() == 52, "Checked decoder accounts exact bytes");
    check(cursor.take(52).size() == 52 && !cursor.remaining(), "Exact nested remaining region");
    bool rejected{};
    try { cursor.read(dest); } catch (const std::out_of_range&) { rejected = true; }
    check(rejected, "Unchecked macro cannot overread with candidate cursor");
    std::uint32_t seed{0x4258ec19};
    for (unsigned i = 0; i < 20000; ++i) {
        seed = seed * 1664525U + 1013904223U;
        writeLength(seed);
        check(mdRawEnvelope(state, 64, version) != Envelope::Valid || seed == 0xffffffc0U,
            "Only exact negative local size accepted across header fuzz corpus");
    }
}
}

int main() {
    try {
        configurationAndKeys();
        for (auto b : {Backend::Snes9x, Backend::GenesisPlusGx})
            for (unsigned slots = 2; slots <= (b == Backend::Snes9x ? 5U : 4U); ++slots)
                rosterAndFrames(b, slots);
        pauseAndStateRaces();
        storageAndValidation();
        snapshotGuards();
        std::cout << "{\"checks\":" << checks
            << ",\"fixture\":\"synthetic-owner-not-emulator-gameplay\",\"window\":" << kWindow
            << ",\"gateBytes\":" << FrameGate::boundedStorageBytes() << "}\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "FAILED after " << checks << " checks: " << ex.what() << '\n';
        return 1;
    }
}
