#pragma once
// WAVES presentation only. Requested families vary band count, RGB and width.
// Fixed 32-segment strips reuse one stack buffer; no heap/JNI/worker/timer added.
// Low byte is opacity; the established renderer packs this RGBA value.
struct StationWavePalette {unsigned count;unsigned colors[5];float widthMultipliers[5];};
struct StationWaveAlias {const char*key;unsigned palette;};
static const StationWavePalette stationWavePalettes[]={
 {3,{0xFF4058B0u,0xEE5B67A0u,0xA7B3C390u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // SNES: red, red, gray
 {5,{0xFFDA52B0u,0x44D98AA0u,0x369DFF90u,0xFF405890u,0xFFDA5290u},{.5f,1.f,1.f,1.f,.5f}}, // Nintendo64: thin yellow, green, blue, red, thin yellow
 {4,{0xFFDA52B0u,0x44D98AA0u,0xAA7DFF90u,0xA7B3C390u,0u},{1.f,1.f,1.f,1.f,1.f}}, // GameCube: yellow, green, purple, gray
 {3,{0xF2F6FFB0u,0x369DFFA0u,0xF2F6FF90u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Wii
 {3,{0x369DFFB0u,0xF2F6FFA0u,0x369DFF90u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Wii U
 {3,{0xFF4058B0u,0x369DFFA0u,0xF2F6FF90u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Switch
 {3,{0xFF4058B0u,0x369DFFA0u,0xFFDA5290u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // PSX: red, blue, yellow
 {3,{0xFF4058B0u,0x369DFFA0u,0xFFDA5290u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // PS2: red, blue, yellow
 {3,{0x369DFFB0u,0xF2F6FFA0u,0xA7B3C390u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // PSP
 {3,{0x369DFFB0u,0xFF4058A0u,0xA7B3C390u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Mega Drive
 {3,{0xFF4058B0u,0x369DFFA0u,0xFF944890u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // 32X
 {3,{0xA7B3C3B0u,0x369DFFA0u,0xF2F6FF90u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Saturn
 {5,{0x44D98AB0u,0x369DFFA0u,0xFF405890u,0xFFDA5290u,0xFF944890u},{1.f,1.f,1.f,1.f,1.f}}, // Dreamcast: green, blue, red, yellow, orange
 {3,{0x369DFFB0u,0xF2F6FFA0u,0xFF944890u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Naomi / Naomi 2
 {3,{0xFFDA52B0u,0x369DFFA0u,0xF2F6FF90u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Neo Geo
 {3,{0x369DFFB0u,0xFFDA52A0u,0xF2F6FF90u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // CPS 1 / 2 / 3
 {3,{0xAA7DFFB0u,0xFF4058A0u,0xA7B3C390u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // NES: purple, red, gray
 {3,{0x44D98AB0u,0xFFDA52A0u,0xFF944890u,0u,0u},{1.f,1.f,1.f,1.f,1.f}}, // Final Burn Neo: green, yellow, orange
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
 {"Nintendinho",16},{"nes",16},{"Nintendo Entertainment System",16},{"Nintendo NES",16},
 {"fbneo",17},{"Final Burn Neo",17},{"FinalBurn Neo",17},{"final-burn-neo",17},
};
// presentationKeyEqual is the existing ASCII case/outer-tail-space comparison.
static const StationWavePalette* stationWavePalette(const char*key){
 if(!key||!*key)return nullptr;
 for(const auto&alias:stationWaveAliases)if(presentationKeyEqual(key,alias.key))return &stationWavePalettes[alias.palette];
 return nullptr;
}
