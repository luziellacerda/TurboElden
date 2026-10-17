package org.emulationstation.frontend.netplay;

import java.io.IOException;

/** Current-run GameCube policy; never writes the user's offline preferences. */
final class StationDolphinCpuPolicy {
    private StationDolphinCpuPolicy() {}

    static void configure(String platform) throws Exception {
        if (!"gamecube".equals(platform)) return;

        // Pinned Dolphin NativeConfig: CURRENT=4 and ACTIVE=3. Its NetPlay
        // server reads this setting before synchronizing the boot parameters.
        Class<?> config = Class.forName(
            "org.dolphinemu.dolphinemu.features.settings.model.NativeConfig");
        Class<?>[] signature = {Integer.TYPE, String.class, String.class,
                                String.class, Boolean.TYPE};
        config.getMethod("setBoolean", signature).invoke(
            null, 4, "Dolphin", "Core", "CPUThread", false);
        Object active = config.getMethod("getBoolean", signature).invoke(
            null, 3, "Dolphin", "Core", "CPUThread", true);
        if (!Boolean.FALSE.equals(active))
            throw new IOException("DOLPHIN_GAMECUBE_CPU_MODE");

        android.util.Log.i("StationDolphin", "GC_CPU_MODE single-core current-run verified");
    }
}
