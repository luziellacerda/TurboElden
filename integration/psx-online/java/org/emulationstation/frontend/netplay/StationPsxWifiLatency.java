// SPDX-License-Identifier: GPL-2.0-or-later
package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.util.Log;

/** A foreground PSX session's Wi-Fi lease. Never enables or reconnects Wi-Fi. */
final class StationPsxWifiLatency {
    private final Context context;
    private WifiManager.WifiLock lock;
    private boolean unavailable;

    StationPsxWifiLatency(Context context) {
        Context application = context.getApplicationContext();
        this.context = application != null ? application : context;
    }

    // Called only from the existing activity UI dispatcher, on lifecycle changes.
    void setActive(boolean active) {
        if (!active) {
            if (lock != null) {
                try {
                    if (lock.isHeld()) lock.release();
                    lock = null;
                    Log.i("StationPsx", "event=wifi-latency held=false");
                } catch (RuntimeException failure) {
                    // Retain the handle so a later lifecycle event can release it.
                    Log.w("StationPsx", "event=wifi-latency release-failed");
                }
            }
            unavailable = false;
            return;
        }
        if (lock != null || unavailable) return;
        try {
            Object service = context.getSystemService(Context.WIFI_SERVICE);
            if (!(service instanceof WifiManager)) {
                unavailable = true;
                Log.w("StationPsx", "event=wifi-latency unavailable");
                return;
            }
            int mode = Build.VERSION.SDK_INT >= 29
                    ? WifiManager.WIFI_MODE_FULL_LOW_LATENCY
                    : WifiManager.WIFI_MODE_FULL_HIGH_PERF;
            // Remember the handle before acquire: even a vendor exception after
            // acquisition must not lose the only handle that can release it.
            lock = ((WifiManager) service).createWifiLock(mode, "Station-PSX-online");
            lock.setReferenceCounted(false);
            lock.acquire();
            if (!lock.isHeld()) throw new IllegalStateException("WIFI_LEASE_NOT_HELD");
            Log.i("StationPsx", "event=wifi-latency mode=" + mode + " held=true");
        } catch (RuntimeException failure) {
            unavailable = true;
            // This optional OS hint never admits a room or terminates a game.
            if (lock != null) {
                try {
                    if (lock.isHeld()) lock.release();
                    lock = null;
                } catch (RuntimeException releaseFailure) {
                    Log.w("StationPsx", "event=wifi-latency release-failed");
                }
            }
            Log.w("StationPsx", "event=wifi-latency unavailable");
        }
    }
}
