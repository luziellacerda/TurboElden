package org.uoyabause.android;
import android.view.Surface;
/** JNI declarations matching the official Yaba Sanshiro 1.20.46 Android port. */
public final class YabauseRunnable {
    static { System.loadLibrary("turbo_saturn"); }
    public static native int init(Object host);
    public static native void deinit();
    public static native int initViewport(Surface surface,int width,int height);
    public static native int pause();
    public static native int resume();
    public static native int isRunning();
    public static native int isReady();
    public static native void press(int key,int player);
    public static native void release(int key,int player);
    public static native void reset();
    public static native void setCpu(int cpu);
    public static native void setResolutionMode(int mode);
    public static native void setRbgResolutionMode(int mode);
    public static native void setAspectRateMode(int mode);
    public static native void setPolygonGenerationMode(int mode);
    public static native void setFilter(int filter);
    public static native void setSoundEngine(int engine);
    public static native void enableComputeShader(int enabled);
    public static native void enableFPS(int enabled);
    public static native void enableFrameskip(int enabled);
    public static native void setUseSh2Cache(int enabled);
    public static native void setUseCpuAffinity(int enabled);
    public static native void enableExtendedMemory(int enabled);
    public static native int setFrameLimitMode(int mode);
    public static native void setVolume(int volume);
    public static native String savestate(String file);
    public static native int loadstate(String file);
}
