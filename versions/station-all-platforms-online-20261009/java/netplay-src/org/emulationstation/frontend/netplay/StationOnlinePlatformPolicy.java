package org.emulationstation.frontend.netplay;

import java.io.IOException;
import org.emulationstation.frontend.station.StationPlatforms;

/** Maintainer ceilings; exact signed game modes and a working engine still determine admission. */
final class StationOnlinePlatformPolicy {
    static String platform(String raw)throws IOException {
        String folder=StationPlatforms.resolve(raw).folder;
        switch(folder){
            case "super-nintendo":case "super-nintendo--br":return "snes";
            case "megadrive":case "megadrive--br":return "megadrive";
            case "neo-geo":return "neogeo";
            case "neo-geo-cd":return "neogeocd";
            case "nintendo-64":case "nintendo-64--br":return "n64";
            default:return folder;
        }
    }
    static int maximum(String platform){
        switch(platform){
            case "snes":return 5;
            case "n64":case "dreamcast":case "gamecube":case "wii":case "wiiu":return 4;
            default:return 2;
        }
    }
    static boolean directFourPads(String platform){return "n64".equals(platform)||"dreamcast".equals(platform);}
    private StationOnlinePlatformPolicy(){}
}
