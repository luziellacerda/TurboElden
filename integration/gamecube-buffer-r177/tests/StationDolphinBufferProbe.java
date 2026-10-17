package org.emulationstation.frontend.netplay;

import org.dolphinemu.dolphinemu.features.settings.model.NativeConfig;

public final class StationDolphinBufferProbe {
    private static int checks;
    private static void check(boolean value, String why) {
        checks++;
        if (!value) throw new AssertionError(why);
    }
    private static void refused(boolean clientChanged) throws Exception {
        NativeConfig.reset();
        NativeConfig.wrongActive = !clientChanged;
        NativeConfig.client = clientChanged ? 2 : 1;
        try {
            StationDolphinBufferPolicy.configure("gamecube");
        } catch (java.io.IOException expected) {
            check(expected.getMessage().equals(clientChanged ?
                "DOLPHIN_CLIENT_PAD_BUFFER_CHANGED" : "DOLPHIN_GAMECUBE_PAD_BUFFER"),
                "precise refusal after unsuccessful effective configuration");
            return;
        }
        throw new AssertionError("Invalid effective configuration was accepted");
    }
    public static void main(String[] args) throws Exception {
        String old = StationDolphinBufferPolicy.options("wii");
        check(old.contains("\npadBuffer=5\n"), "Wii retains original pad buffer");
        check(old.contains("\nclientBuffer=1\n"), "separate client buffer retained");
        check(StationDolphinBufferPolicy.options("gamecube").equals(
            old.replace("\npadBuffer=5\n", "\npadBuffer=8\n")),
            "only GameCube pad buffer differs in serialized policy");
        for (String platform : new String[]{"wii", "psx", "n64", "snes", "", null}) {
            NativeConfig.reset();
            StationDolphinBufferPolicy.configure(platform);
            check(NativeConfig.writes == 0 && NativeConfig.reads == 0,
                  "no native configuration access outside GameCube");
            check(StationDolphinBufferPolicy.options(platform).equals(old),
                  "shared unused temporary for other platform remains exact");
        }
        NativeConfig.reset();
        StationDolphinBufferPolicy.configure("gamecube");
        check(NativeConfig.writes == 1 && NativeConfig.reads == 2,
              "one transient override and two effective readbacks");
        check(NativeConfig.value == 8 && NativeConfig.client == 1,
              "eight shared pad slots and unchanged client buffer");
        refused(false);
        refused(true);
        System.out.println("PASS checks=" + checks + " transientOnly=true cpuAndOfflineUntouched=true");
    }
}
