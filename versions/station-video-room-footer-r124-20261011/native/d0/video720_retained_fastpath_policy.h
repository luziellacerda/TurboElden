#pragma once

// Pure gate for the completed-video retained-frame path. Every condition is
// deliberately affirmative: if any fact cannot be demonstrated in the current
// render call, native_system_video720.h falls back to the established path.
namespace video720RetainedFastPath {
struct State {
 bool completed;
 bool slotsIdle;
 bool sourcesReady;
 bool contextMatches;
 bool previewProgramValid;
 int currentProgram;
};

constexpr bool eligible(const State&s){
 return s.completed&&s.slotsIdle&&s.sourcesReady&&s.contextMatches&&
        s.previewProgramValid&&s.currentProgram>0;
}
}
