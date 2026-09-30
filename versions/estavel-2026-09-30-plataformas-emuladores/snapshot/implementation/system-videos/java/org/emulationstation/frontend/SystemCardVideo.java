package org.emulationstation.frontend;

import android.app.Activity;
import android.app.Application;
import android.content.res.AssetFileDescriptor;
import android.graphics.SurfaceTexture;
import android.media.MediaCodecInfo;
import android.media.MediaCodecList;
import android.media.MediaFormat;
import android.media.MediaPlayer;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.util.Log;
import android.view.Surface;
import java.util.concurrent.atomic.AtomicBoolean;

/** Decoder only. Frames are drawn by the existing native rounded card, never by an Android View. */
public final class SystemCardVideo {
    private static final String TAG = "TurboSystemVideo";
    private static volatile Session active;
    private static volatile boolean foreground = true;
    private static Handler worker;
    private static boolean registered;
    private static int hardwareProfile;
    private static volatile boolean preferLite;

    private static final class Session {
        final SurfaceTexture texture;
        final Surface surface;
        final AtomicBoolean frame = new AtomicBoolean();
        String asset;
        volatile boolean valid = true, failed, hasFrame;
        boolean surfacesReleased;
        volatile long lastDraw = SystemClock.uptimeMillis();
        MediaPlayer player; // Worker thread only.
        Session(int id, String asset) {
            this.asset = asset;
            texture = new SurfaceTexture(id);
            texture.setDefaultBufferSize(1120, 800);
            surface = new Surface(texture);
        }
    }

    private static synchronized Handler worker() {
        if (worker == null) {
            HandlerThread thread = new HandlerThread("SystemCardVideo", android.os.Process.THREAD_PRIORITY_BACKGROUND);
            thread.start();
            worker = new Handler(thread.getLooper());
        }
        return worker;
    }

    private static synchronized void register(Activity activity) {
        if (registered) return;
        activity.getApplication().registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks() {
            private boolean frontend(Activity a) { return a.getClass().getName().equals("org.emulationstation.frontend.ESActivity"); }
            public void onActivityResumed(Activity a) { foreground = frontend(a); if (!foreground) stop(); }
            public void onActivityPaused(Activity a) { if (frontend(a)) { foreground = false; stop(); } }
            public void onActivityStopped(Activity a) { if (frontend(a)) stop(); }
            public void onActivityDestroyed(Activity a) { if (frontend(a)) stop(); }
            public void onActivityCreated(Activity a, Bundle b) { }
            public void onActivityStarted(Activity a) { }
            public void onActivitySaveInstanceState(Activity a, Bundle b) { }
        });
        registered = true;
    }

    // Invoked on the SDL OpenGL thread, with its context current.
    public static boolean start(Activity activity, int texture, String asset) {
        if (activity == null || !foreground || activity.isFinishing() || !activity.hasWindowFocus()) return false;
        if (asset == null || !asset.startsWith("turbo-system-videos/") || asset.contains("..")) return false;
        register(activity);
        stop();
        final Handler handler = worker();
        final Session session;
        try { session = new Session(texture, asset); }
        catch (RuntimeException error) { Log.w(TAG, "Surface unavailable; animated loading card", error); return false; }
        active = session;
        session.texture.setOnFrameAvailableListener(st -> {
            if (active == session && session.valid) session.frame.set(true);
        }, handler);
        final android.content.res.AssetManager assets = activity.getApplicationContext().getAssets();
        handler.post(() -> {
            if (active != session || !session.valid) { release(session); return; }
            try {
                int profile = hardwareProfile();
                if (profile == 0) throw new IllegalStateException("No supported hardware atlas decoder");
                android.app.ActivityManager manager = (android.app.ActivityManager) activity.getApplicationContext().getSystemService(android.content.Context.ACTIVITY_SERVICE);
                boolean lite = preferLite || profile < 2 || (manager != null && manager.isLowRamDevice());
                session.asset = "turbo-system-videos/atlas-" + (lite ? "lite" : "hd") + ".mp4";
                session.texture.setDefaultBufferSize(lite ? 1120 : 1680, lite ? 800 : 1200);
                MediaPlayer player = new MediaPlayer();
                session.player = player;
                player.setSurface(session.surface);
                player.setVolume(0f, 0f);
                player.setOnErrorListener((mp, what, extra) -> {
                    session.failed = true;
                    if (session.asset.endsWith("atlas-hd.mp4")) preferLite = true;
                    session.valid = false;
                    Log.w(TAG, "Atlas playback failed " + what + "/" + extra);
                    release(session);
                    return true;
                });
                player.setOnPreparedListener(mp -> {
                    if (active != session || !session.valid || !foreground) { release(session); return; }
                    try {
                        mp.setLooping(true);
                        mp.setVolume(0f, 0f);
                        mp.start();
                        Log.i(TAG, "Playing all visible native cards from one atlas: " + session.asset);
                    } catch (RuntimeException error) { session.failed = true; session.valid = false; release(session); }
                });
                try (AssetFileDescriptor fd = assets.openFd(session.asset)) {
                    player.setDataSource(fd.getFileDescriptor(), fd.getStartOffset(), fd.getLength());
                }
                player.prepareAsync();
                handler.postDelayed(new Runnable() {
                    public void run() {
                        if (active != session || !session.valid) return;
                        if (!foreground || SystemClock.uptimeMillis() - session.lastDraw > 900) {
                            if (active == session) active = null;
                            session.valid = false;
                            release(session);
                            return;
                        }
                        handler.postDelayed(this, 300);
                    }
                }, 300);
            } catch (Exception error) {
                session.failed = true;
                session.valid = false;
                Log.w(TAG, "Preparation unavailable; animated loading card", error);
                release(session);
            }
        });
        return true;
    }

    // Worker only: one shared stream, selected for available hardware capabilities.
    private static int hardwareProfile() {
        if (hardwareProfile != 0) return hardwareProfile < 0 ? 0 : hardwareProfile;
        int best = 0;
        for (MediaCodecInfo info : new MediaCodecList(MediaCodecList.REGULAR_CODECS).getCodecInfos()) {
            if (info.isEncoder()) continue;
            String name = info.getName().toLowerCase(java.util.Locale.ROOT);
            boolean hardware = Build.VERSION.SDK_INT >= 29 ? info.isHardwareAccelerated()
                    : !name.startsWith("omx.google.") && !name.startsWith("c2.android.") && !name.startsWith("c2.google.");
            if (!hardware) continue;
            try {
                MediaCodecInfo.VideoCapabilities caps = info.getCapabilitiesForType("video/avc").getVideoCapabilities();
                if (caps.areSizeAndRateSupported(1120, 800, 18)) best = Math.max(best, 1);
                if (caps.areSizeAndRateSupported(1680, 1200, 18)) best = 2;
            } catch (IllegalArgumentException ignored) { }
        }
        hardwareProfile = best == 0 ? -1 : best;
        return best;
    }

    // Only latch an already decoded frame. No file IO, waits, Bitmaps or prepare() here.
    public static int update(float[] transform) {
        Session session = active;
        if (session == null) return -1;
        if (session.failed) return -2;
        if (!session.valid || !foreground) return -1;
        session.lastDraw = SystemClock.uptimeMillis();
        synchronized (session) {
            if (!session.valid) return session.failed ? -2 : -1;
            try {
                if (session.frame.getAndSet(false)) {
                    session.texture.updateTexImage();
                    session.hasFrame = true;
                }
                if (session.hasFrame) session.texture.getTransformMatrix(transform);
                return session.hasFrame ? 1 : 0;
            } catch (RuntimeException error) {
                session.failed = true;
                session.valid = false;
                worker().post(() -> release(session));
                return -2;
            }
        }
    }

    public static void stop() {
        Session session = active;
        active = null;
        if (session == null) return;
        session.valid = false;
        releaseSurfaces(session);
        worker().post(() -> release(session));
    }

    private static void releaseSurfaces(Session session) {
        synchronized (session) {
            if (session.surfacesReleased) return;
            session.surfacesReleased = true;
            try { session.surface.release(); session.texture.release(); }
            catch (RuntimeException ignored) { }
            session.hasFrame = false;
        }
    }

    private static void release(Session session) {
        // Potentially slow codec teardown stays off the GL thread and outside its monitor.
        MediaPlayer player = session.player;
        session.player = null;
        if (player != null) {
            try { player.setOnPreparedListener(null); player.setOnErrorListener(null); player.release(); }
            catch (RuntimeException ignored) { }
        }
        releaseSurfaces(session);
    }
}
