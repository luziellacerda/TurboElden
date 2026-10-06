#pragma once
#include <cstdint>
#include <cstring>

namespace station {
// Bytes actually received during the network phase, averaged from its first event.
struct TransferRate {
    bool started = false;
    int64_t first = 0, last = 0, total = -1;
    uint64_t sinceMillis = 0, lastMillis = 0;
    double observe(int64_t received, int64_t expected, uint64_t nowMillis) {
        if (!started || received < last || expected != total || nowMillis < lastMillis) {
            started = true; first = received; last = received;
            total = expected; sinceMillis = lastMillis = nowMillis;
            return 0;
        }
        last = received; lastMillis = nowMillis;
        const uint64_t elapsed = nowMillis - sinceMillis;
        return elapsed >= 500 ? double(received - first) * 1000.0 / double(elapsed) : 0;
    }
};

enum class TransferPhase : int { Unknown = 0, Waiting = 1, Downloading = 2, Preparing = 3 };

inline TransferPhase transferPhase(bool active, int result, const char* message) {
    if (!active || result != 0 || !message) return TransferPhase::Unknown;
    if (std::strcmp(message, "Baixando") == 0) return TransferPhase::Downloading;
    if (std::strcmp(message, "Preparando") == 0 ||
        std::strcmp(message, "Verificando integridade") == 0 ||
        std::strcmp(message, "Conferindo arquivo já baixado") == 0) return TransferPhase::Preparing;
    return TransferPhase::Waiting;
}

// The renderer requests Progress for an exact item before drawing its counters.
// Never select a different job when that known item is inactive or has changed.
// Older callers without an item selection may use only a unique active match.
template<class Jobs, class Key>
const typename Jobs::mapped_type* exactActiveJob(const Jobs& jobs, const Key& selected,
                                               int64_t received, int64_t total) {
    const auto matches = [&](const auto& job) {
        return job.progress.active && job.result == 0 &&
            job.progress.received == received && job.progress.total == total;
    };
    if (!selected.empty()) {
        const auto found = jobs.find(selected);
        return found != jobs.end() && matches(found->second) ? &found->second : nullptr;
    }
    const typename Jobs::mapped_type* result = nullptr;
    for (const auto& entry : jobs) {
        if (!matches(entry.second)) continue;
        if (result) return nullptr;
        result = &entry.second;
    }
    return result;
}
}
