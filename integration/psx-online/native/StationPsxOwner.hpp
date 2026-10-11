// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "StationPsxProtocol.hpp"
#include <cstddef>
#include <cstdint>
#include <span>

namespace station::psx::owner {
// The factory runs ONLY on the original SDL owner after real loadGame succeeded.
// It must return a session with exactly this state size and immutable identity.
// The caller owns that Session until process teardown, never frees it from IO.
using CoreReady = Session*(*)(std::size_t stateBytes, const Digest& compiledDefaults,
                             const Digest& pinnedOptions, void* user);
using LocalPause = void(*)(bool paused, void* user); // enqueue only; no JNI/UI wait
using Failure = void(*)(const char* category, void* user); // enqueue only
struct Config {
    std::uint8_t localSlot; // exactly 1 or 2, signed roster already validated
    const char* sessionHome; // fresh confined session root, never offline HOME
    const char* systemDirectory;
    const char* saveDirectory;
    bool gameApprovedForHleStandardTwoPorts; // per-ROM approval, NOT every PSX game
    CoreReady onCoreReady;
    LocalPause onLocalPause;
    Failure onFailure;
    void* user;
};
// Copies all config strings. Single session per private process, no reconfigure.
// prepare/install run before the original Player is launched. They run no core.
bool prepare(const Config&);
// Validates original owner/core file hashes AND executable loaded owner segments.
// The core ELF is checked again against the actual dladdr-loaded core on dlsym.
// Changes only four owner GOT pointers, never instructions or either ELF on disk.
bool install(std::uintptr_t loadedOwnerBase, std::span<const std::uint8_t> ownerElf,
             std::span<const std::uint8_t> coreElf);
Session* session(); // non-owning, null until the genuine CoreReady callback
bool coreReady();
bool localPaused(); // Java must withhold READY/resume while true
bool failed();
// ONLY call after an explicit positive human confirmation. Enqueues, never calls
// SDL/core from the caller. The real owner authorizes and closes at a checkpoint.
void authorizeHumanExit();
const char* ownerHash();
const char* coreHash();
} // namespace station::psx::owner
