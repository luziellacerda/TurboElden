package org.emulationstation.frontend.station;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executor;
import java.util.concurrent.RejectedExecutionException;

/** Presentation-only preference, independent of the existing graphics mask/revision. */
public final class StationCarouselStylePreferences {
    public static final int CURRENT = 0, DIAGONAL = 1, LATERAL = 2;
    private static final String FILE = "station_carousel_style_r123";
    private static volatile StationCarouselStylePreferences instance;
    private final Context context;
    private final Handler main = new Handler(Looper.getMainLooper());
    private final CopyOnWriteArrayList<Listener> listeners = new CopyOnWriteArrayList<>();
    private volatile int style = CURRENT;
    private SharedPreferences saved;
    private boolean loading, chosenBeforeLoad, announcementPending;
    private volatile boolean loaded;

    public interface Listener { void onCarouselStyleChanged(int style); }
    private StationCarouselStylePreferences(Context context) { this.context = context; }
    public static StationCarouselStylePreferences get(Context context) {
        if (context == null) throw new IllegalArgumentException("Context required");
        StationCarouselStylePreferences found = instance;
        if (found == null) synchronized (StationCarouselStylePreferences.class) {
            found = instance;
            if (found == null) {
                Context app = context.getApplicationContext();
                instance = found = new StationCarouselStylePreferences(app == null ? context : app);
            }
        }
        return found;
    }
    public int style() { return style; }
    public boolean loaded() { return loaded; }
    public void addListener(Listener listener) { if (listener != null) listeners.addIfAbsent(listener); }
    public void removeListener(Listener listener) { listeners.remove(listener); }

    /** Called once at bootstrap using StationFrontend's existing catalog worker. */
    void initialize(Executor worker) {
        synchronized (this) { if (loaded || loading) return; loading = true; }
        try { worker.execute(this::load); }
        catch (RejectedExecutionException busy) {
            synchronized (this) { loading = false; }
            android.util.Log.w("StationCarousel", "Preference bootstrap deferred");
        }
    }
    private void load() {
        try {
            SharedPreferences file = context.getSharedPreferences(FILE, Context.MODE_PRIVATE);
            int restored = sanitize(file.getInt("style", CURRENT));
            synchronized (this) {
                saved = file;
                if (chosenBeforeLoad) file.edit().putInt("style", style).apply();
                else style = restored;
                loaded = true; loading = false;
            }
            announce();
        } catch (RuntimeException failure) {
            synchronized (this) { loading = false; }
            android.util.Log.w("StationCarousel", "Preference bootstrap unavailable: " + failure.getClass().getSimpleName());
        }
    }
    public void setStyle(int value) {
        int next = sanitize(value);
        synchronized (this) {
            if (style == next && loaded) return;
            if (style == next && chosenBeforeLoad) return;
            style = next;
            if (saved == null) chosenBeforeLoad = true;
            else saved.edit().putInt("style", next).apply();
        }
        announce();
    }
    private void announce() {
        synchronized (this) { if (announcementPending) return; announcementPending = true; }
        main.post(() -> {
            synchronized (StationCarouselStylePreferences.this) { announcementPending = false; }
            int latest = style;
            for (Listener listener : listeners) {
                try { listener.onCarouselStyleChanged(latest); }
                catch (RuntimeException failure) { android.util.Log.w("StationCarousel", "Listener failed: " + failure.getClass().getSimpleName()); }
            }
        });
    }
    static int sanitize(int value) { return value == DIAGONAL || value == LATERAL ? value : CURRENT; }
}
