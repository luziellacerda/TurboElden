#pragma once
// WAVES backdrop colors only. No shader, timer, geometry, I/O or UI mutation.
// Low byte is opacity; the established renderer packs this RGBA value.
struct StationWavePalette {unsigned colors[3];};
struct StationWaveAlias {const char*key;unsigned palette;};
static const StationWavePalette stationWavePalettes[]={
 {{0xFF4058B0u,0xEE5B67A0u,0xFF8B9490u}}, // SNES: three red tones
 {{0x44D98AB0u,0x369DFFA0u,0xFF405890u}}, // Nintendo 64
 {{0xAA7DFFB0u,0x9270E8A0u,0xC1A5FF90u}}, // GameCube: three purple tones
 {{0xF2F6FFB0u,0x369DFFA0u,0xF2F6FF90u}}, // Wii
 {{0x369DFFB0u,0xF2F6FFA0u,0x369DFF90u}}, // Wii U
 {{0xFF4058B0u,0x369DFFA0u,0xF2F6FF90u}}, // Switch
 {{0xFF4058B0u,0xA7B3C3A0u,0x44D98A90u}}, // PSX
 {{0x369DFFB0u,0xF2F6FFA0u,0x44D98A90u}}, // PS2
 {{0x369DFFB0u,0xF2F6FFA0u,0xA7B3C390u}}, // PSP
 {{0x369DFFB0u,0xFF4058A0u,0xA7B3C390u}}, // Mega Drive
 {{0xFF4058B0u,0x369DFFA0u,0xFF944890u}}, // 32X
 {{0xA7B3C3B0u,0x369DFFA0u,0xF2F6FF90u}}, // Saturn
 {{0xFF9448B0u,0xF2F6FFA0u,0xFFDA5290u}}, // Dreamcast
 {{0x369DFFB0u,0xF2F6FFA0u,0xFF944890u}}, // Naomi / Naomi 2
 {{0xFFDA52B0u,0x369DFFA0u,0xF2F6FF90u}}, // Neo Geo
 {{0x369DFFB0u,0xFFDA52A0u,0xF2F6FF90u}}, // CPS 1 / 2 / 3
};
static const StationWaveAlias stationWaveAliases[]={
 {"Super Nintendo",0},{"Super Nintendo - BR",0},{"snes",0},{"snesbr",0},{"super-nintendo",0},{"super-nintendo--br",0},
 {"Nintendo 64",1},{"Nintendo 64 - BR",1},{"n64",1},{"n64br",1},{"nintendo-64",1},{"nintendo-64--br",1},
 {"GameCube",2},{"Nintendo GameCube",2},{"gc",2},
 {"Wii",3},{"Nintendo Wii",3},
 {"wiiu",4},{"Wii U",4},{"Nintendo Wii U",4},
 {"Switch",5},{"Nintendo Switch",5},
 {"Playstation 1",6},{"PlayStation",6},{"PS1",6},{"psx",6},
 {"Playstation 2",7},{"Playstation 2 - BR",7},{"ps2",7},{"ps2br",7},{"playstation-2",7},{"playstation-2--br",7},
 {"PSP",8},{"Psp - BR",8},{"pspbr",8},{"psp--br",8},
 {"MegaDrive",9},{"MegaDrive - BR",9},{"Mega Drive",9},{"megadrivebr",9},{"megadrive--br",9},{"mega-drive",9},
 {"sega32x",10},{"32X",10},{"Sega 32X",10},
 {"saturn",11},{"saturno",11},{"Sega Saturn",11},
 {"Dreamcast",12},{"Sega Dreamcast",12},{"sega-dreamcast",12},
 {"naomi",13},{"Sega Naomi",13},{"naomi2",13},{"Naomi 2",13},{"Sega Naomi 2",13},
 {"Neo Geo",14},{"neogeo",14},{"neo-geo",14},
 {"cps1",15},{"CPS 1",15},{"CPS-1",15},{"CAPCOM Play System 1",15},{"capcom-play-system-1",15},
 {"cps2",15},{"CPS 2",15},{"CPS-2",15},{"CAPCOM Play System 2",15},{"capcom-play-system-2",15},
 {"cps3",15},{"CPS 3",15},{"CPS-3",15},{"CAPCOM Play System 3",15},{"capcom-play-system-3",15},
};
// presentationKeyEqual is the existing ASCII case/outer-tail-space comparison.
static const StationWavePalette* stationWavePalette(const char*key){
 if(!key||!*key)return nullptr;
 for(const auto&alias:stationWaveAliases)if(presentationKeyEqual(key,alias.key))return &stationWavePalettes[alias.palette];
 return nullptr;
}
