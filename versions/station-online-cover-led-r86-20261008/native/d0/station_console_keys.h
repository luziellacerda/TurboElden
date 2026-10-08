// The server exports labels; explicit folder aliases also supported.
struct StationConsoleAlias{const char*alias;const char*key;};
static const StationConsoleAlias stationConsoleAliases[]={
 {"Super Nintendo","snes"},{"Super Nintendo - BR","snes"},{"snes","snes"},{"snesbr","snes"},{"super-nintendo","snes"},{"super-nintendo--br","snes"},
 {"MegaDrive","megadrive"},{"MegaDrive - BR","megadrive"},{"Mega Drive","megadrive"},{"megadrive","megadrive"},{"megadrivebr","megadrive"},{"megadrive--br","megadrive"},{"mega-drive","megadrive"},
 {"Nintendo 64","n64"},{"Nintendo 64 - BR","n64"},{"n64","n64"},{"n64br","n64"},{"nintendo-64","n64"},{"nintendo-64--br","n64"},
 {"Neo Geo","neogeo"},{"neogeo","neogeo"},{"neo-geo","neogeo"},
 {"Neo Geo CD","neogeocd"},{"neogeocd","neogeocd"},{"neo-geo-cd","neogeocd"},
 {"naomi","naomi"},{"Sega Naomi","naomi"},{"naomi2","naomi2"},{"Naomi 2","naomi2"},{"Sega Naomi 2","naomi2"},
 {"Dreamcast","dreamcast"},{"Sega Dreamcast","dreamcast"},{"sega-dreamcast","dreamcast"},{"cps1","cps1"},{"CPS 1","cps1"},{"CPS-1","cps1"},{"CAPCOM Play System 1","cps1"},{"capcom-play-system-1","cps1"},{"cps2","cps2"},{"CPS 2","cps2"},{"CPS-2","cps2"},{"CAPCOM Play System 2","cps2"},{"capcom-play-system-2","cps2"},{"cps3","cps3"},{"CPS 3","cps3"},{"CPS-3","cps3"},{"CAPCOM Play System 3","cps3"},{"capcom-play-system-3","cps3"}
};
static const char*stationConsoleKey(const char*key){
 if(!key)return nullptr;
 for(const auto&a:stationConsoleAliases)if(presentationKeyEqual(key,a.alias))return a.key;
 return nullptr;
}
