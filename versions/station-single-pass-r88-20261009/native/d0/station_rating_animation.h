#pragma once
// Sample the original 60-fps artwork at the 30-fps menu cadence. Play once,
// preserving its duration, then keep the final image without wrapping.
static constexpr unsigned stationRatingLoopFrame(unsigned elapsedMs){unsigned long long frame=(unsigned long long)elapsedMs*60u/1000u;return frame<80u?(unsigned)frame:79u;}
