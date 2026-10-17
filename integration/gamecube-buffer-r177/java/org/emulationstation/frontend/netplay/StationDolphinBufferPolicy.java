package org.emulationstation.frontend.netplay;

import java.io.IOException;

/** The GameCube fixed-delay pad buffer for this online run only. */
final class StationDolphinBufferPolicy {
    private static final String PREVIOUS_OPTIONS = "backend=dolphin-station-v1\nwire=DPL1\nsettingsPolicy=official-pinned-gameini+host-synchronized-strict-v1\ntraversal=direct\nupnp=false\nindex=false\nqos=false\nchunkedUploadLimit=false\nnetworkMode=fixeddelay\npadBuffer=5\nclientBuffer=1\nsaveLoad=true\nsaveWrite=true\nsyncAllWii=false\nsyncCodes=false\ncheats=false\nrecordInputs=false\nstrictSettingsSync=true\ngolfMode=false\nremoteGbas=false\nsaves=session-only\n";
    private static final String GAMECUBE_OPTIONS =
        PREVIOUS_OPTIONS.replace("padBuffer=5\n", "padBuffer=8\n");

    private StationDolphinBufferPolicy() {}

    // The profile constructor has a shared temporary for all platforms. Its
    // non-Dolphin branches do not use this value; preserve the old value there.
    static String options(String platform) {
        return "gamecube".equals(platform) ? GAMECUBE_OPTIONS : PREVIOUS_OPTIONS;
    }

    static void configure(String platform) throws Exception {
        if (!"gamecube".equals(platform)) return;

        // NativeConfigure establishes the unchanged fixed-delay policy first.
        // NativeHost reads BufferSize while constructing the real server and
        // sends that shared target to each client. Do not change the separate
        // client buffer, CPU selection, renderer, clocks or offline settings.
        Class<?> config = Class.forName(
            "org.dolphinemu.dolphinemu.features.settings.model.NativeConfig");
        Class<?>[] signature = {Integer.TYPE, String.class, String.class,
                                String.class, Integer.TYPE};
        config.getMethod("setInt", signature).invoke(
            null, 4, "Dolphin", "NetPlay", "BufferSize", 8);
        Object active = config.getMethod("getInt", signature).invoke(
            null, 3, "Dolphin", "NetPlay", "BufferSize", -1);
        if (!Integer.valueOf(8).equals(active))
            throw new IOException("DOLPHIN_GAMECUBE_PAD_BUFFER");
        Object client = config.getMethod("getInt", signature).invoke(
            null, 3, "Dolphin", "NetPlay", "BufferSizeClient", -1);
        if (!Integer.valueOf(1).equals(client))
            throw new IOException("DOLPHIN_CLIENT_PAD_BUFFER_CHANGED");

        android.util.Log.i("StationDolphin", "GC_PAD_BUFFER current-run=8 verified");
    }
}
