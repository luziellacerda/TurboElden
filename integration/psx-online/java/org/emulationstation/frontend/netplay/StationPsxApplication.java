// SPDX-License-Identifier: GPL-2.0-or-later
package org.emulationstation.frontend.netplay;
import android.app.Application;
import android.os.Build;
/** Only the dedicated PSX process: no Yuzu init, catalog, downloads or frontend preload. */
public final class StationPsxApplication extends Application {
    public static boolean isPrivateProcess() {
        return Build.VERSION.SDK_INT >= 28 &&
                "org.turboramastation.frontend:station_psx_online".equals(Application.getProcessName());
    }
    @Override public void onCreate() { super.onCreate(); }
}
