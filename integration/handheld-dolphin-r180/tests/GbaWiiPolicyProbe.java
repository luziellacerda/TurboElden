import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.json.JSONObject;
import org.emulationstation.frontend.netplay.StationGamePlayerInfo;
import org.emulationstation.frontend.netplay.StationGbaLinkPolicy;

public final class GbaWiiPolicyProbe {
    private static int checks;
    private interface Checked { void run() throws Exception; }
    private static void check(boolean value) { checks++; if (!value) throw new AssertionError(checks); }
    private static void denied(Checked action) throws Exception {
        checks++;
        try { action.run(); throw new AssertionError("Expected refusal " + checks); }
        catch (IOException expected) { }
    }
    private static JSONObject engine() {
        return new JSONObject().put("backend", "retroarch").put("library", "libgpsp_station_online.so")
                .put("recoveryProtocol", "station-stream.v3").put("options", StationGbaLinkPolicy.OPTIONS);
    }
    private static String config(int local) {
        StringBuilder value = new StringBuilder("savefile_directory = \"/old/private/session/saves\"\n")
                .append("netplay_password = \"synthetic-only\"\nvideo_driver = \"gl\"\n");
        for (int port = 1; port <= 16; port++)
            value.append("netplay_request_device_p").append(port).append(" = \"").append(port == local).append("\"\n")
                 .append("input_libretro_device_p").append(port).append(" = \"").append(port <= 5 ? 1 : 0).append("\"\n");
        return value.toString();
    }
    public static void main(String[] args) throws Exception {
        for (int maximum = 1; maximum <= 5; maximum++)
            check(StationGbaLinkPolicy.devices("gba", StationGbaLinkPolicy.CONTROLLER, maximum, engine()).length == 1);
        check(StationGbaLinkPolicy.devices("gba", "unregistered-controller", 5, null) == null);
        denied(() -> StationGbaLinkPolicy.devices("snes", StationGbaLinkPolicy.CONTROLLER, 5, engine()));
        denied(() -> StationGbaLinkPolicy.devices("gba", StationGbaLinkPolicy.CONTROLLER, 0, engine()));
        denied(() -> StationGbaLinkPolicy.devices("gba", StationGbaLinkPolicy.CONTROLLER, 6, engine()));
        for (String key : new String[] {"backend", "library", "recoveryProtocol", "options"})
            denied(() -> StationGbaLinkPolicy.devices("gba", StationGbaLinkPolicy.CONTROLLER, 5, engine().put(key, "wrong")));

        for (int local = 1; local <= 5; local++) {
            String original = config(local);
            String changed = StationGbaLinkPolicy.configureValues(original, "/private/gba-link-saves/content");
            check(changed.contains("savefile_directory = \"/private/gba-link-saves/content\"\n"));
            check(changed.contains("netplay_password = \"synthetic-only\"\nvideo_driver = \"gl\"\n"));
            for (int port = 1; port <= 16; port++) {
                check(changed.contains("netplay_request_device_p" + port + " = \"" + (port == 1) + "\"\n"));
                check(changed.contains("input_libretro_device_p" + port + " = \"" + (port == 1 ? 1 : 0) + "\"\n"));
            }
            for (String platform : new String[] {"snes", "megadrive", "psx", "n64", "gamecube", "wii"})
                check(StationGbaLinkPolicy.configure(null, platform, null, original) == original);
        }
        denied(() -> StationGbaLinkPolicy.configureValues(config(1), "/path\nunsafe"));
        denied(() -> StationGbaLinkPolicy.configureValues(config(1), "relative"));
        denied(() -> StationGbaLinkPolicy.configureValues(config(1) + "savefile_directory = \"/duplicate\"\n", "/safe"));
        denied(() -> StationGbaLinkPolicy.configureValues(config(1) + "input_libretro_device_p1 = \"1\"\n", "/safe"));
        denied(() -> StationGbaLinkPolicy.configureValues(config(1).replace("input_libretro_device_p16 = \"0\"\n", ""), "/safe"));
        denied(() -> StationGbaLinkPolicy.configureValues(config(1) + "netplay_request_device_p17 = \"true\"\n", "/safe"));

        Path root = Files.createTempDirectory("station-r180-gba-policy-");
        try {
            File launch = root.resolve("station-online/" + repeat('a', 32) + "/retroarch.cfg").toFile();
            String transformed = StationGbaLinkPolicy.configure(launch, "gba", repeat('b', 64), config(5));
            check(root.resolve("station-online/gba-link-saves/" + repeat('b', 64)).toFile().isDirectory());
            check(transformed.contains("gba-link-saves/" + repeat('b', 64)));
            check(!launch.exists());
            denied(() -> StationGbaLinkPolicy.configure(launch, "gba", "../bad", config(1)));
            denied(() -> StationGbaLinkPolicy.configure(root.resolve("unexpected.cfg").toFile(), "gba", repeat('b', 64), config(1)));
            Path outside = Files.createDirectory(root.resolve("outside"));
            Files.createSymbolicLink(root.resolve("station-online/gba-link-saves/" + repeat('c', 64)), outside);
            denied(() -> StationGbaLinkPolicy.configure(launch, "gba", repeat('c', 64), config(1)));
        } finally {
            try (java.util.stream.Stream<Path> paths = Files.walk(root)) {
                Path[] descending = paths.sorted(java.util.Comparator.reverseOrder()).toArray(Path[]::new);
                for (Path p : descending) Files.delete(p);
            }
        }
        for (String controller : new String[] {"dolphin-gamecube-four-ports-v1", "dolphin-wii-remotes-four-v1"})
            for (int maximum = 2; maximum <= 4; maximum++) {
                int[] counts = maximum == 2 ? new int[] {2} : maximum == 3 ? new int[] {2, 3} : new int[] {2, 3, 4};
                StationGamePlayerInfo value = StationGamePlayerInfo.fromVerifiedProfile(true, maximum, counts, "local-multiplayer", controller);
                check(value.onlineApproved && value.permits(2) && value.permits(maximum) && !value.permits(5));
                check(!StationGamePlayerInfo.fromVerifiedProfile(false, maximum, counts, "local-multiplayer", controller).onlineApproved);
            }
        StationGamePlayerInfo gba = StationGamePlayerInfo.fromVerifiedProfile(true, 5, new int[] {2, 3, 4, 5}, "wireless-link", StationGbaLinkPolicy.CONTROLLER);
        check(gba.onlineApproved && gba.permits(5));
        check(!StationGamePlayerInfo.fromVerifiedProfile(true, 5, new int[] {2, 3, 4, 5}, "local-multiplayer", "dolphin-wii-remotes-four-v1").onlineApproved);
        check(!StationGamePlayerInfo.fromVerifiedProfile(true, 6, new int[] {2, 3, 4, 5, 6}, "wireless-link", StationGbaLinkPolicy.CONTROLLER).onlineApproved);
        System.out.println("{\"passed\":true,\"checks\":" + checks + ",\"androidPhysicallyTested\":false}");
    }
    private static String repeat(char value, int length) {
        char[] chars = new char[length]; java.util.Arrays.fill(chars, value); return new String(chars);
    }
}
