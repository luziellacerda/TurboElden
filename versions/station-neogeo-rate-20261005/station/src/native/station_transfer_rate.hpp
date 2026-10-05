#pragma once
#include <cstdint>

namespace station {
// Effective network bytes delivered to staging; never estimate unfinished bytes.
struct TransferRate {
    bool started = false;
    int64_t first = 0, last = 0, total = -1;
    uint64_t sinceMillis = 0;
    double observe(int64_t received, int64_t expected, uint64_t nowMillis) {
        if (!started || received < last || expected != total || nowMillis < sinceMillis) {
            started = true; first = received; last = received;
            total = expected; sinceMillis = nowMillis;
            return 0;
        }
        last = received;
        const uint64_t elapsed = nowMillis - sinceMillis;
        return elapsed >= 500 ? double(received - first) * 1000.0 / double(elapsed) : 0;
    }
};
}
