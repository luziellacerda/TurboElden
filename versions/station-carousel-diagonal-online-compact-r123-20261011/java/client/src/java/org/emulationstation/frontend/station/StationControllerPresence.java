package org.emulationstation.frontend.station;

import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.hardware.input.InputManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.view.InputDevice;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewTreeObserver;
import java.lang.ref.WeakReference;
import java.lang.reflect.Method;
import java.util.WeakHashMap;

/** Transient presentation only. The engine retains all physical input and settings. */
public final class StationControllerPresence implements Application.ActivityLifecycleCallbacks,
        InputManager.InputDeviceListener, ViewTreeObserver.OnGlobalLayoutListener {
    private static final String DOLPHIN_ACTIVITY =
            "org.dolphinemu.dolphinemu.activities.EmulationActivity";
    private static final String DOLPHIN_OVERLAY =
            "org.dolphinemu.dolphinemu.overlay.InputOverlay";
    private static final WeakHashMap<Application, StationControllerPresence> INSTALLED =
            new WeakHashMap<>();

    private final Handler main = new Handler(Looper.getMainLooper());
    private InputManager inputs;
    private WeakReference<Activity> owner = new WeakReference<>(null);
    private View decor;
    private View overlay;
    private Method releaseTouch;
    private Method refreshTouch;
    private int originalVisibility;
    private int controllerCount;
    private boolean listening;
    private boolean hiddenByUs;
    private boolean bridgeFailed;

    private StationControllerPresence() {}

    /** Called for the original Application created by the delegating component factory. */
    public static void install(Application application) {
        if (application == null) return;
        synchronized (INSTALLED) {
            if (INSTALLED.containsKey(application)) return;
            // Application may not be attached yet when the component factory returns it.
            StationControllerPresence presence = new StationControllerPresence();
            INSTALLED.put(application, presence);
            application.registerActivityLifecycleCallbacks(presence);
        }
    }

    // Full source matching excludes keyboards, mice, remotes, touchscreens and virtual devices.
    static boolean isController(int sources, boolean virtual) {
        return !virtual && ((sources & InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD ||
                (sources & InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK);
    }

    static boolean shouldHide(boolean resumed, int count) {
        return resumed && count > 0;
    }

    @Override public void onActivityResumed(Activity activity) {
        if (!DOLPHIN_ACTIVITY.equals(activity.getClass().getName())) return;
        if (owner.get() == activity && listening) { rescan(); return; }
        release(false);
        inputs = (InputManager) activity.getSystemService(Context.INPUT_SERVICE);
        if (inputs == null || activity.getWindow() == null) return;
        owner = new WeakReference<>(activity);
        decor = activity.getWindow().getDecorView();
        bridgeFailed = false;
        inputs.registerInputDeviceListener(this, main);
        listening = true;
        if (decor != null) decor.getViewTreeObserver().addOnGlobalLayoutListener(this);
        rescan();
        // Views may be attached after the Activity resume callback. Layout owns that follow-up.
        main.post(() -> { if (owner.get() == activity && listening) apply(); });
    }

    @Override public void onActivityPaused(Activity activity) {
        if (owner.get() == activity) release(true);
    }

    @Override public void onActivityStopped(Activity activity) {
        if (owner.get() == activity) release(true);
    }

    @Override public void onActivityDestroyed(Activity activity) {
        // The original Activity may have already unloaded native input at this point.
        if (owner.get() == activity) release(false);
    }

    @Override public void onInputDeviceAdded(int id) { rescan(); }
    @Override public void onInputDeviceRemoved(int id) { rescan(); }
    @Override public void onInputDeviceChanged(int id) { rescan(); }
    @Override public void onGlobalLayout() { if (listening) apply(); }

    private void rescan() {
        if (!listening || inputs == null) return;
        int count = 0;
        for (int id : inputs.getInputDeviceIds()) {
            InputDevice device = inputs.getInputDevice(id);
            if (device != null && isController(device.getSources(), device.isVirtual())) count++;
        }
        controllerCount = count;
        apply();
    }

    private void apply() {
        if (owner.get() == null || bridgeFailed) return;
        View found = findOverlay(decor);
        if (found != overlay) {
            restore(true);
            overlay = found;
            releaseTouch = refreshTouch = null;
            if (found != null) {
                try {
                    // These public methods manage only Dolphin's touch input overrides.
                    releaseTouch = found.getClass().getMethod("onDestroy");
                    refreshTouch = found.getClass().getMethod("refreshControls");
                } catch (ReflectiveOperationException error) {
                    bridgeFailed = true;
                    return;
                }
            }
        }
        if (overlay == null) return;
        if (shouldHide(listening, controllerCount)) {
            if (!hiddenByUs && overlay.getVisibility() == View.VISIBLE) {
                originalVisibility = overlay.getVisibility();
                long now = SystemClock.uptimeMillis();
                MotionEvent cancel = MotionEvent.obtain(now, now, MotionEvent.ACTION_CANCEL, 0, 0, 0);
                try {
                    overlay.dispatchTouchEvent(cancel);
                    // CANCEL alone is insufficient in this engine; unregister clears touch overrides.
                    releaseTouch.invoke(overlay);
                    overlay.setVisibility(View.INVISIBLE);
                    hiddenByUs = true;
                } catch (ReflectiveOperationException | RuntimeException | LinkageError error) {
                    bridgeFailed = true;
                    // A failed release must not leave an apparently available touch layer disabled.
                    try { refreshTouch.invoke(overlay); }
                    catch (ReflectiveOperationException | RuntimeException | LinkageError ignored) {}
                } finally {
                    cancel.recycle();
                }
            }
        } else {
            restore(true);
        }
    }

    private static View findOverlay(View view) {
        if (view == null) return null;
        if (DOLPHIN_OVERLAY.equals(view.getClass().getName())) return view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                View found = findOverlay(group.getChildAt(i));
                if (found != null) return found;
            }
        }
        return null;
    }

    private void restore(boolean refresh) {
        if (!hiddenByUs || overlay == null) return;
        try {
            if (refresh && refreshTouch != null) refreshTouch.invoke(overlay);
            // A separate owner changing visibility to GONE retains its own decision.
            if (overlay.getVisibility() == View.INVISIBLE) overlay.setVisibility(originalVisibility);
            hiddenByUs = false;
        } catch (ReflectiveOperationException | RuntimeException | LinkageError error) {
            // Keep the view visible even if the engine has already torn down its touch input.
            if (overlay.getVisibility() == View.INVISIBLE) overlay.setVisibility(originalVisibility);
            hiddenByUs = false;
            bridgeFailed = true;
        }
    }

    private void release(boolean refresh) {
        if (listening && inputs != null) inputs.unregisterInputDeviceListener(this);
        listening = false;
        if (decor != null) {
            ViewTreeObserver observer = decor.getViewTreeObserver();
            if (observer.isAlive()) observer.removeOnGlobalLayoutListener(this);
        }
        restore(refresh);
        owner.clear();
        decor = overlay = null;
        releaseTouch = refreshTouch = null;
        controllerCount = 0;
    }

    @Override public void onActivityCreated(Activity activity, Bundle state) {}
    @Override public void onActivityStarted(Activity activity) {}
    @Override public void onActivitySaveInstanceState(Activity activity, Bundle state) {}
}
