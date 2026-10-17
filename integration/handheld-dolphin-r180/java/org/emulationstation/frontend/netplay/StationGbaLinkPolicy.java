package org.emulationstation.frontend.netplay;

import java.io.File;
import java.io.IOException;
import org.json.JSONObject;

/** gpSP packet netplay owns one independent GBA and local P1 per participant.
 * No sockets, threads, timers, native changes or offline save imports here. */
public final class StationGbaLinkPolicy {
    public static final String CONTROLLER = "gba-gpsp-netpacket-v1";
    public static final String OPTIONS = "gpsp_serial = \"auto\"\ngpsp_rtc = \"deterministic\"\n";
    private StationGbaLinkPolicy() {}

    /** Called only from the unknown-controller branch of the verified profile.
     * All existing controller paths keep their original bytecode. */
    public static int[] devices(String platform, String controller, int maximum, JSONObject engine)
            throws Exception {
        if (!CONTROLLER.equals(controller)) return null;
        if (!"gba".equals(platform) || maximum < 1 || maximum > 5
                || !"retroarch".equals(engine.optString("backend"))
                || !"libgpsp_station_online.so".equals(engine.optString("library"))
                || !"station-stream.v3".equals(engine.optString("recoveryProtocol"))
                || !OPTIONS.equals(engine.optString("options")))
            throw new IOException("GBA_LINK_PROFILE");
        return new int[] {1};
    }

    /** Other platforms return the exact original string. The content binding
     * was verified before this method is reached; recheck its path component. */
    public static String configure(File launchConfig, String platform, String contentSha256, String config)
            throws IOException {
        if (!"gba".equals(platform)) return config;
        if (contentSha256 == null || !contentSha256.matches("[0-9a-f]{64}"))
            throw new IOException("GBA_LINK_CONTENT");
        if (launchConfig == null || !"retroarch.cfg".equals(launchConfig.getName()))
            throw new IOException("GBA_LINK_LAUNCH_FILE");
        File room = launchConfig.getAbsoluteFile().getParentFile();
        if (room == null || !room.getName().matches("[0-9a-f]{32}")
                || room.getParentFile() == null || !"station-online".equals(room.getParentFile().getName()))
            throw new IOException("GBA_LINK_ROOM_DIRECTORY");
        File parent = room.getParentFile();
        File saves = new File(new File(parent, "gba-link-saves"), contentSha256);
        if (!parent.getCanonicalFile().equals(parent.getAbsoluteFile())
                || !saves.getParentFile().getCanonicalFile().equals(saves.getParentFile().getAbsoluteFile())
                || !saves.getCanonicalFile().equals(saves.getAbsoluteFile())
                || (!saves.isDirectory() && !saves.mkdirs()))
            throw new IOException("GBA_LINK_SAVE_DIRECTORY");
        return configureValues(config, saves.toString());
    }

    /** Strict config transformation used by the real launcher and its probes. */
    public static String configureValues(String original, String saveDirectory) throws IOException {
        if (original == null || saveDirectory == null || !saveDirectory.startsWith("/")
                || saveDirectory.indexOf('"') >= 0 || saveDirectory.indexOf('\n') >= 0
                || saveDirectory.indexOf('\r') >= 0 || saveDirectory.indexOf('\\') >= 0)
            throw new IOException("GBA_LINK_CONFIG");
        StringBuilder out = new StringBuilder(original.length() + 128);
        boolean save = false;
        boolean[] request = new boolean[16], device = new boolean[16];
        for (String line : original.split("\n", -1)) {
            if (line.isEmpty()) continue;
            int separator = line.indexOf(" = ");
            String key = separator < 0 ? "" : line.substring(0, separator);
            if ("savefile_directory".equals(key)) {
                if (save) throw new IOException("GBA_LINK_DUPLICATE_SAVE");
                save = true;
                line = key + " = \"" + saveDirectory + "\"";
            } else if (key.startsWith("netplay_request_device_p")) {
                int port = port(key, "netplay_request_device_p");
                if (request[port - 1]) throw new IOException("GBA_LINK_DUPLICATE_PORT");
                request[port - 1] = true;
                line = key + " = \"" + (port == 1 ? "true" : "false") + "\"";
            } else if (key.startsWith("input_libretro_device_p")) {
                int port = port(key, "input_libretro_device_p");
                if (device[port - 1]) throw new IOException("GBA_LINK_DUPLICATE_DEVICE");
                device[port - 1] = true;
                line = key + " = \"" + (port == 1 ? "1" : "0") + "\"";
            }
            out.append(line).append('\n');
        }
        if (!save) throw new IOException("GBA_LINK_MISSING_SAVE");
        for (int port = 1; port <= 16; port++)
            if (!request[port - 1] || !device[port - 1])
                throw new IOException("GBA_LINK_MISSING_PORT");
        return out.toString();
    }

    private static int port(String key, String prefix) throws IOException {
        String suffix = key.substring(prefix.length());
        if (!suffix.matches("[1-9]|1[0-6]")) throw new IOException("GBA_LINK_PORT");
        return Integer.parseInt(suffix);
    }
}
