package org.emulationstation.frontend.station;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import java.util.concurrent.CopyOnWriteArrayList;

/** Menu graphics only: these flags do not change emulator frame rates or input. */
public final class StationGraphicsPreferences {
    public static final int LED = 1;
    public static final int VIDEO = 1 << 1;
    public static final int CLOUDS = 1 << 2;
    public static final int ICONS = 1 << 3;
    public static final int CELL_EFFECTS = 1 << 4;
    public static final int UI_TRANSITIONS = 1 << 5;
    public static final int ALL = LED | VIDEO | CLOUDS | ICONS | CELL_EFFECTS | UI_TRANSITIONS;
    public static final int SKY = 0;
    public static final int WAVES = 1;
    public static final int OFF = 2;

    private static final String FILE = "station_graphics_r117";
    private static volatile StationGraphicsPreferences instance;
    private final SharedPreferences saved;
    private final Handler main = new Handler(Looper.getMainLooper());
    private final CopyOnWriteArrayList<Listener> listeners = new CopyOnWriteArrayList<>();
    private volatile State state;
    private boolean announcementPending;

    public interface Listener { void onGraphicsChanged(State state); }

    /** Immutable state, also the exact mask/mode contract consumed by JNI. */
    public static final class State {
        public final int individualMask;
        public final boolean masterDisabled;
        public final int backgroundMode;
        public final long revision;

        public State(int individualMask, boolean masterDisabled, int backgroundMode, long revision) {
            this.individualMask = individualMask & ALL;
            this.masterDisabled = masterDisabled;
            this.backgroundMode = sanitizeMode(backgroundMode);
            this.revision = Math.max(0L, revision);
        }

        public static State defaults() { return new State(ALL, false, SKY, 0L); }
        public int effectiveMask() { return masterDisabled ? 0 : individualMask; }
        public boolean isEnabled(int effect) {
            int bits = effect & ALL;
            return bits != 0 && (effectiveMask() & bits) == bits;
        }
        public boolean backgroundAllowed() { return isEnabled(CLOUDS) && backgroundMode != OFF; }
        public int effectiveBackgroundMode() { return backgroundAllowed() ? backgroundMode : OFF; }
        public State withEffect(int effect, boolean enabled) {
            int bits = effect & ALL;
            int next = enabled ? individualMask | bits : individualMask & ~bits;
            return next == individualMask ? this : new State(next, masterDisabled, backgroundMode, nextRevision());
        }
        public State withMasterDisabled(boolean disabled) {
            return disabled == masterDisabled ? this : new State(individualMask, disabled, backgroundMode, nextRevision());
        }
        public State withBackgroundMode(int mode) {
            int next = sanitizeMode(mode);
            return next == backgroundMode ? this : new State(individualMask, masterDisabled, next, nextRevision());
        }
        private long nextRevision() { return revision == Long.MAX_VALUE ? 1L : revision + 1L; }
    }

    private StationGraphicsPreferences(Context context) {
        saved = context.getSharedPreferences(FILE, Context.MODE_PRIVATE);
        state = new State(saved.getInt("individual_mask", ALL), saved.getBoolean("master_disabled", false),
                saved.getInt("background_mode", SKY), saved.getLong("revision", 0L));
    }

    public static StationGraphicsPreferences get(Context context) {
        if (context == null) throw new IllegalArgumentException("Context required");
        StationGraphicsPreferences found = instance;
        if (found == null) {
            synchronized (StationGraphicsPreferences.class) {
                found = instance;
                if (found == null) {
                    Context app = context.getApplicationContext();
                    instance = found = new StationGraphicsPreferences(app == null ? context : app);
                }
            }
        }
        return found;
    }

    public State snapshot() { return state; }
    public int effectiveMask() { return state.effectiveMask(); }
    public int individualMask() { return state.individualMask; }
    public boolean masterDisabled() { return state.masterDisabled; }
    public boolean isEnabled(int effect) { return state.isEnabled(effect); }
    public boolean backgroundAllowed() { return state.backgroundAllowed(); }
    public int backgroundMode() { return state.backgroundMode; }
    public int effectiveBackgroundMode() { return state.effectiveBackgroundMode(); }
    public long revision() { return state.revision; }
    public void addListener(Listener listener) { if (listener != null) listeners.addIfAbsent(listener); }
    public void removeListener(Listener listener) { listeners.remove(listener); }

    public void setEnabled(int effect, boolean enabled) { update(effect, enabled, null, null); }
    public void setMasterDisabled(boolean disabled) { update(0, false, disabled, null); }
    public void toggleMasterDisabled() {
        State changed;
        synchronized (this) { changed = store(state.withMasterDisabled(!state.masterDisabled)); }
        announce(changed);
    }
    public void setBackgroundMode(int mode) { update(0, false, null, mode); }

    private void update(int effect, boolean enabled, Boolean master, Integer mode) {
        State changed;
        synchronized (this) {
            State next = master != null ? state.withMasterDisabled(master.booleanValue())
                    : mode != null ? state.withBackgroundMode(mode.intValue()) : state.withEffect(effect, enabled);
            changed = store(next);
        }
        announce(changed);
    }
    private State store(State next) {
        if (next == state) return null;
        state = next;
        saved.edit().putInt("individual_mask", next.individualMask).putBoolean("master_disabled", next.masterDisabled)
                .putInt("background_mode", next.backgroundMode).putLong("revision", next.revision).apply();
        return next;
    }
    private void announce(State changed) {
        if (changed == null) return;
        synchronized (this) {
            if (announcementPending) return;
            announcementPending = true;
        }
        main.post(() -> {
            State latest;
            synchronized (StationGraphicsPreferences.this) { announcementPending = false; latest = state; }
            for (Listener listener : listeners) {
                try { listener.onGraphicsChanged(latest); }
                catch (RuntimeException error) {
                    android.util.Log.w("StationGraphics", "Listener failed: " + error.getClass().getSimpleName());
                }
            }
        });
    }
    private static int sanitizeMode(int mode) { return mode == WAVES || mode == OFF ? mode : SKY; }
}
