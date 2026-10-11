package org.emulationstation.frontend.sony;

/** Selected by StationComponentFactory only in the private PS3 process. */
public final class Ps3Application extends android.app.Application {
    @Override public void onCreate() {
        super.onCreate();
        Ps3Bootstrap.requireProcess();
        // Extraction, JNI, firmware and game work start on the owner's worker.
    }
}
