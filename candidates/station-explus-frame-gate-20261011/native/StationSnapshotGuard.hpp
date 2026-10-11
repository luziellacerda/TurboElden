// Candidate primitives only. A valid envelope is NOT proof that a core's
// nested state decoder is memory-safe. The actual decoder still needs bounds.
// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <array>
#include <cstdint>
#include <cstring>
#include <span>
#include <stdexcept>

namespace station::explus {

// Current upstream snapshot.h defines SUCCESS=1; errors are negative.
constexpr bool snesStateSucceeded(int upstreamResult) { return upstreamResult == 1; }

enum class Envelope { Valid, Truncated, CompressedUnsupported, LengthMismatch, VersionMismatch };

inline Envelope mdRawEnvelope(std::span<const std::uint8_t> state,
    std::size_t locallyProducedRawPayloadSize, std::span<const std::uint8_t, 16> exactVersion) {
    if (state.size() < 20 || locallyProducedRawPayloadSize < 16 ||
        locallyProducedRawPayloadSize > 16 * 1024 * 1024) return Envelope::Truncated;
    const std::uint32_t u = std::uint32_t(state[0]) | (std::uint32_t(state[1]) << 8) |
        (std::uint32_t(state[2]) << 16) | (std::uint32_t(state[3]) << 24);
    // Convert with 64-bit arithmetic: never negate INT32_MIN in a signed32 value.
    const std::int64_t n = u <= 0x7fffffffU ? std::int64_t(u) :
        std::int64_t(u) - 0x100000000LL;
    if (n >= 0) return Envelope::CompressedUnsupported;
    const auto bytes = static_cast<std::uint64_t>(-n);
    if (bytes != locallyProducedRawPayloadSize || bytes != state.size() - 4)
        return Envelope::LengthMismatch;
    if (std::memcmp(state.data() + 4, exactVersion.data(), exactVersion.size()))
        return Envelope::VersionMismatch;
    return Envelope::Valid;
}

// Reusable replacement primitive for the unchecked load_param macro. It is
// not inserted into state.cc/context loaders in this candidate.
class CheckedStateCursor {
public:
    explicit CheckedStateCursor(std::span<const std::uint8_t> data) : bytes_(data) {}
    void read(std::span<std::uint8_t> out) {
        if (out.size() > bytes_.size() - offset_) throw std::out_of_range("Truncated state");
        if (!out.empty()) std::memcpy(out.data(), bytes_.data() + offset_, out.size());
        offset_ += out.size();
    }
    std::span<const std::uint8_t> take(std::size_t count) {
        if (count > bytes_.size() - offset_) throw std::out_of_range("Truncated state");
        const auto chunk = bytes_.subspan(offset_, count);
        offset_ += count;
        return chunk;
    }
    std::size_t remaining() const { return bytes_.size() - offset_; }
private:
    std::span<const std::uint8_t> bytes_;
    std::size_t offset_{};
};

} // namespace station::explus
