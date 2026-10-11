package org.emulationstation.frontend.sony;

import android.app.Application;

/** Created by the Sony factory before any Station/Yuzu/SDL native initializer. */
public final class Ps4Application extends Application {
    @Override public void onCreate() { super.onCreate(); }
}
