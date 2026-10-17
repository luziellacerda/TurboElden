package org.dolphinemu.dolphinemu.features.settings.model;

/** Host-only fixture, excluded from the product and every runtime classpath. */
public final class NativeConfig {
    public static int reads, writes, value, client;
    public static boolean wrongActive;
    public static void reset() {
        reads = writes = 0;
        value = 5;
        client = 1;
        wrongActive = false;
    }
    private static void path(String file, String section, String key) {
        if (!"Dolphin".equals(file) || !"NetPlay".equals(section) ||
            !("BufferSize".equals(key) || "BufferSizeClient".equals(key)))
            throw new AssertionError("Unrequested path, CPU or offline setting");
    }
    public static void setInt(int layer, String file, String section, String key, int number) {
        path(file, section, key);
        if (layer != 4 || !"BufferSize".equals(key) || number != 8)
            throw new AssertionError("Only the shared buffer CurrentRun override is allowed");
        writes++;
        value = number;
    }
    public static int getInt(int layer, String file, String section, String key, int fallback) {
        path(file, section, key);
        if (layer != 3 || fallback != -1) throw new AssertionError("Effective readback layer");
        reads++;
        return "BufferSizeClient".equals(key) ? client : wrongActive ? 5 : value;
    }
}
