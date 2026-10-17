package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.util.Log;

/** Temporary startup diagnostics. The normal game path never depends on success. */
final class StationStartupLogging {
    private static final String TAG = "StationStartupDiagnostics";

    private StationStartupLogging() { }

    static native boolean enable(String exactRuntimePath);

    static void begin(Context context) {
        try {
            System.loadLibrary("station_startup_logging");
            String directory = context.getApplicationInfo().nativeLibraryDir;
            boolean enabled = enable(directory + "/libstation_retroarch.so");
            Log.i(TAG, "stage=early-logger enabled=" + enabled + " frontendLevel=1");
        } catch (Throwable ignored) {
            try {
                Log.w(TAG, "stage=early-logger enabled=false category=helper-failed");
            } catch (Throwable unavailable) { }
        }
    }

    static void cfgWritten() {
        try {
            Log.i(TAG, "stage=cfg-written log_verbosity=true frontend_log_level=3 libretro_log_level=3 log_to_file=false");
        } catch (Throwable unavailable) { }
    }
}
