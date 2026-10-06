#pragma once
static bool stationButtonKeyEqual(const char*a,const char*b){
 while(*a&&*b){char x=*a++,y=*b++;if(x>='A'&&x<='Z')x+=32;if(y>='A'&&y<='Z')y+=32;if(x!=y)return false;}
 while(*a==' ')a++;while(*b==' ')b++;return !*a&&!*b;
}
struct StationButtonAlias{const char*key;const char*shortName;};
static const StationButtonAlias stationButtonAliases[]={
{"3ds","3DS"},
{"Playstation 1","PS1"},
{"Playstation 2","PS2"},
{"Playstation 2 - BR","PS2 BR"},
{"PSP","PSP"},
{"Psvita","PS VITA"},
{"Switch","SWITCH"},
{"wii","WII"},
{"wiiu","WII U"},
{"Arcade","ARCADE"},
{"atari2600","ATARI 2600"},
{"atari7800","ATARI 7800"},
{"Atomiswave","ATOMISWAVE"},
{"colecovision","COLECOVISION"},
{"cps1","CPS1"},
{"cps2","CPS2"},
{"cps3","CPS3"},
{"Dreamcast","DREAMCAST"},
{"fds","FDS"},
{"gameandwatch","GAME & WATCH"},
{"gamegear","GAME GEAR"},
{"Gameboy","GAME BOY"},
{"Gba","GBA"},
{"Gameboy Color","GBC"},
{"jaguar","JAGUAR"},
{"mame","MAME"},
{"Master System","MASTER SYSTEM"},
{"MegaDrive","MEGA DRIVE"},
{"MegaDrive - BR","MEGA DRIVE BR"},
{"model2","MODEL 2"},
{"Nintendo 64","N64"},
{"Nintendo 64 - BR","N64 BR"},
{"Nintendo DS","NDS"},
{"Neo Geo","NEO GEO"},
{"Neo Geo CD","NEO GEO CD"},
{"Nintendinho","NES"},
{"Odyssey 2","ODYSSEY 2"},
{"Pc Engine","PC ENGINE"},
{"Pc Engine cd","PCE CD"},
{"sega32x","32X"},
{"Super Nintendo","SNES"},
{"Super Nintendo - BR","SNES BR"},
{"sufami","SUFAMI TURBO"},
{"supergrafx","SUPERGRAFX"},
{"fbneo","FB NEO"},
{"GameCube","GAMECUBE"},
{"xbox360","XBOX 360"},
{"saturn","SATURN"},
{"xbox","XBOX"},
{"Psp - BR","PSP BR"},
{"naomi","NAOMI"},
{"naomi2","NAOMI 2"},
};
static const char*stationButtonShortName(const char*key,const char*fallback){
 for(auto a:stationButtonAliases)if(stationButtonKeyEqual(key,a.key))return a.shortName;
 return fallback;
}
static const char*stationButtonFullName(const char*key,const char*fallback){
 if(stationButtonKeyEqual(key,"Super Nintendo - BR"))return "Super Nintendo BR";
 if(stationButtonKeyEqual(key,"MegaDrive - BR"))return "Mega Drive BR";
 if(stationButtonKeyEqual(key,"Nintendo 64 - BR"))return "Nintendo 64 BR";
 if(stationButtonKeyEqual(key,"Playstation 2 - BR"))return "PlayStation 2 BR";
 if(stationButtonKeyEqual(key,"Psp - BR"))return "PSP BR";
 return fallback;
}
