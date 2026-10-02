package org.emulationstation.frontend.station;

import java.io.IOException;
import java.util.*;

/** Generated from observed folders and the server ac86942 platform list. No slug inference. */
public final class StationPlatforms {
    public static final class Platform {
        public final String label, folder;
        private Platform(String label,String folder) {this.label=label;this.folder=folder;}
    }
    private static final Map<String,Platform> BY_NAME;
    static {
        Map<String,Platform> names=new LinkedHashMap<>();
        names.put("3ds",new Platform("3ds","3ds"));
        names.put("Arcade",new Platform("Arcade","arcade"));
        names.put("Atomiswave",new Platform("Atomiswave","atomiswave"));
        names.put("Dreamcast",new Platform("Dreamcast","dreamcast"));
        names.put("GameCube",new Platform("GameCube","gamecube"));
        names.put("Gameboy",new Platform("Gameboy","gameboy"));
        names.put("Gameboy Color",new Platform("Gameboy Color","gameboy-color"));
        names.put("Gba",new Platform("Gba","gba"));
        names.put("Master System ",new Platform("Master System ","master-system"));
        names.put("MegaDrive",new Platform("MegaDrive","megadrive"));
        names.put("MegaDrive - BR",new Platform("MegaDrive - BR","megadrive--br"));
        names.put("Neo Geo",new Platform("Neo Geo","neo-geo"));
        names.put("Neo Geo CD",new Platform("Neo Geo CD","neo-geo-cd"));
        names.put("Nintendinho",new Platform("Nintendinho","nintendinho"));
        names.put("Nintendo 64",new Platform("Nintendo 64","nintendo-64"));
        names.put("Nintendo 64 - BR",new Platform("Nintendo 64 - BR","nintendo-64--br"));
        names.put("Nintendo DS",new Platform("Nintendo DS","nintendo-ds"));
        names.put("Odyssey 2",new Platform("Odyssey 2","odyssey-2"));
        names.put("PSP",new Platform("PSP","psp"));
        names.put("Pc Engine",new Platform("Pc Engine","pc-engine"));
        names.put("Pc Engine cd",new Platform("Pc Engine cd","pc-engine-cd"));
        names.put("Playstation 1",new Platform("Playstation 1","psx"));
        names.put("Playstation 2",new Platform("Playstation 2","ps2"));
        names.put("Playstation 2 - BR",new Platform("Playstation 2 - BR","ps2br"));
        names.put("Psp - BR",new Platform("Psp - BR","psp"));
        names.put("Psvita",new Platform("Psvita","psvita"));
        names.put("Super Nintendo",new Platform("Super Nintendo","super-nintendo"));
        names.put("Super Nintendo - BR",new Platform("Super Nintendo - BR","super-nintendo--br"));
        names.put("Switch",new Platform("Switch","switch"));
        names.put("atari2600",new Platform("atari2600","atari2600"));
        names.put("atari7800",new Platform("atari7800","atari7800"));
        names.put("colecovision",new Platform("colecovision","colecovision"));
        names.put("cps1",new Platform("cps1","cps1"));
        names.put("cps2",new Platform("cps2","cps2"));
        names.put("cps3",new Platform("cps3","cps3"));
        names.put("fbneo",new Platform("fbneo","fbneo"));
        names.put("fds",new Platform("fds","fds"));
        names.put("gameandwatch",new Platform("gameandwatch","gameandwatch"));
        names.put("gamegear",new Platform("gamegear","gamegear"));
        names.put("jaguar",new Platform("jaguar","jaguar"));
        names.put("mame",new Platform("mame","mame"));
        names.put("naomi",new Platform("naomi","naomi"));
        names.put("naomi2",new Platform("naomi2","naomi2"));
        names.put("saturn",new Platform("saturn","saturn"));
        names.put("sega32x",new Platform("sega32x","sega32x"));
        names.put("supergrafx",new Platform("supergrafx","supergrafx"));
        names.put("wii",new Platform("wii","wii"));
        names.put("wiiu",new Platform("wiiu","wiiu"));
        names.put("xbox",new Platform("xbox","xbox"));
        names.put("xbox360",new Platform("xbox360","xbox360"));
        names.put("megadrive",names.get("MegaDrive"));
        names.put("snes",names.get("Super Nintendo"));
        names.put("snesbr",names.get("Super Nintendo - BR"));
        names.put("gb",names.get("Gameboy"));
        names.put("gbc",names.get("Gameboy Color"));
        names.put("gba",names.get("Gba"));
        BY_NAME=Collections.unmodifiableMap(names);
    }
    private StationPlatforms() {}
    public static Platform resolve(String platform) throws IOException {
        Platform result=BY_NAME.get(platform);
        if(result==null)throw new IOException("Platform has no verified local mapping: "+platform);
        return result;
    }
}
