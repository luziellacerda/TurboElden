#pragma once
// Installation/download state and the selected game's stars share the top bar.
// Include station_info_layout.h first; no new input controls are introduced.
static constexpr StationInfoRect stationStatusRect(float w,float h){return {w*.410f,h*.031f,w*.142f,h*.043f};}
static constexpr StationInfoRect stationHeaderStarsRect(float w,float h){return {w*.562f,h*.031f,w*.060f,h*.043f};}
