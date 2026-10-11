#pragma once

namespace stationMenuFramePolicy {
// Requested 30-fps menu cadence, including dialogs. Emulator clocks are separate.
constexpr int target(bool dialog, bool interacting, bool loading) {
    (void)dialog;(void)interacting;(void)loading;return 30;
}
}
