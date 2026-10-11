package org.libsdl.app;

/** Exact pinned PS4 JNI_OnLoad declarations; isolated from Station SDL. */
public final class SDLAudioManager {
    public static native void nativeAddAudioDevice(boolean p0, java.lang.String p1, int p2);
    public static native void nativeRemoveAudioDevice(boolean p0, int p1);
    public static native void nativeSetupJNI();
}
