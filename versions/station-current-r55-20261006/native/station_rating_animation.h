#pragma once
// Favourite App Icon: 80 original frames at 60 fps; no idle worker.
static unsigned stationRatingLoopFrame(unsigned elapsedMs){return (unsigned)(((unsigned long long)elapsedMs*60u/1000u)%80u);}
