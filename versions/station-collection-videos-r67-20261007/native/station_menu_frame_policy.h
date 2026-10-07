#pragma once

namespace stationMenuFramePolicy {
// Menu-only ceiling. Retain the previous lower cadence of covered idle dialogs.
// Video decoding and emulator loops are governed by their own clocks.
constexpr int target(bool dialog, bool interacting, bool loading) {
    return dialog && !interacting && !loading ? 15 : 30;
}
}
