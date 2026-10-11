package org.emulationstation.frontend.sony;

import android.app.Activity;
import android.app.AppComponentFactory;
import android.app.Application;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.ContentProvider;
import android.content.Intent;
import android.content.pm.ApplicationInfo;

/** Sony owners initialize only in their dedicated processes. All other owners keep their factory. */
public final class StationSonyComponentFactory extends AppComponentFactory {
    private static final String PS3_PROCESS = "org.turboramastation.frontend:station_ps3";
    private static final String PS4_PROCESS = "org.turboramastation.frontend:station_ps4";
    private volatile AppComponentFactory delegate;

    private static boolean sonyProcess() {
        String process = Application.getProcessName();
        return PS3_PROCESS.equals(process) || PS4_PROCESS.equals(process);
    }

    private AppComponentFactory delegate(ClassLoader loader) throws InstantiationException {
        AppComponentFactory value = delegate;
        if (value != null) return value;
        synchronized (this) {
            if (delegate == null) {
                try {
                    delegate = (AppComponentFactory) Class.forName(
                        "org.emulationstation.frontend.station.StationComponentFactory", true, loader)
                        .getDeclaredConstructor().newInstance();
                } catch (ReflectiveOperationException | ClassCastException cause) {
                    InstantiationException error = new InstantiationException("Station factory unavailable");
                    error.initCause(cause);
                    throw error;
                }
            }
            return delegate;
        }
    }

    @Override public ClassLoader instantiateClassLoader(ClassLoader loader, ApplicationInfo info) {
        if (sonyProcess()) return super.instantiateClassLoader(loader, info);
        try { return delegate(loader).instantiateClassLoader(loader, info); }
        catch (InstantiationException cause) { throw new IllegalStateException(cause); }
    }

    @Override public Application instantiateApplication(ClassLoader loader, String name)
            throws InstantiationException, IllegalAccessException, ClassNotFoundException {
        String process = Application.getProcessName();
        if (PS3_PROCESS.equals(process)) {
            return super.instantiateApplication(loader, "org.emulationstation.frontend.sony.Ps3Application");
        }
        if (PS4_PROCESS.equals(process)) {
            return super.instantiateApplication(loader, "org.emulationstation.frontend.sony.Ps4Application");
        }
        return delegate(loader).instantiateApplication(loader, name);
    }

    @Override public Activity instantiateActivity(ClassLoader loader, String name, Intent intent)
            throws InstantiationException, IllegalAccessException, ClassNotFoundException {
        // Existing native callers keep their class identity and Intent contract.
        // The external R130 bridge is never instantiated for that manifest leaf.
        if (!sonyProcess() && "org.emulationstation.frontend.offline.StationSonyOfflineActivity".equals(name)) {
            return super.instantiateActivity(loader, "org.emulationstation.frontend.sony.StationSonyLaunchActivity", intent);
        }
        return sonyProcess() ? super.instantiateActivity(loader, name, intent) :
            delegate(loader).instantiateActivity(loader, name, intent);
    }

    @Override public Service instantiateService(ClassLoader loader, String name, Intent intent)
            throws InstantiationException, IllegalAccessException, ClassNotFoundException {
        return sonyProcess() ? super.instantiateService(loader, name, intent) :
            delegate(loader).instantiateService(loader, name, intent);
    }

    @Override public BroadcastReceiver instantiateReceiver(ClassLoader loader, String name, Intent intent)
            throws InstantiationException, IllegalAccessException, ClassNotFoundException {
        return sonyProcess() ? super.instantiateReceiver(loader, name, intent) :
            delegate(loader).instantiateReceiver(loader, name, intent);
    }

    @Override public ContentProvider instantiateProvider(ClassLoader loader, String name)
            throws InstantiationException, IllegalAccessException, ClassNotFoundException {
        return sonyProcess() ? super.instantiateProvider(loader, name) :
            delegate(loader).instantiateProvider(loader, name);
    }
}
