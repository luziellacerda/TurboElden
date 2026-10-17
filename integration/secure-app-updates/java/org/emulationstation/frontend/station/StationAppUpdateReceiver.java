package org.emulationstation.frontend.station;

import android.content.*;

/** Explicit non-exported installer callback, bound to a persisted session/nonce. */
public final class StationAppUpdateReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context,Intent intent){StationAppUpdater.installerResult(context,intent);}
}
