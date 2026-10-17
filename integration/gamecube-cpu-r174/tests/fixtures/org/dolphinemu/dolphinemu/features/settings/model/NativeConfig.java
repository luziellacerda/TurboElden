package org.dolphinemu.dolphinemu.features.settings.model;
public final class NativeConfig {
    public static int writes, reads;
    public static boolean refuseReadback, rejectWrite;
    public static void reset() { writes=reads=0; refuseReadback=rejectWrite=false; }
    public static void setBoolean(int layer, String file, String section, String key, boolean value) {
        if (rejectWrite) throw new IllegalStateException("synthetic unavailable setting");
        if (layer!=4 || !file.equals("Dolphin") || !section.equals("Core") ||
            !key.equals("CPUThread") || value) throw new AssertionError("Wrong or persistent write");
        writes++;
    }
    public static boolean getBoolean(int layer, String file, String section, String key, boolean fallback) {
        if (layer!=3 || !file.equals("Dolphin") || !section.equals("Core") ||
            !key.equals("CPUThread") || !fallback || writes!=1)
            throw new AssertionError("Active native readback contract differs");
        reads++;
        return refuseReadback;
    }
}
