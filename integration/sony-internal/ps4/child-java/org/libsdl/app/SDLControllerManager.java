package org.libsdl.app;

/** Exact pinned PS4 JNI_OnLoad declarations; isolated from Station SDL. */
public final class SDLControllerManager {
    public static native void nativeAddHaptic(int p0, java.lang.String p1);
    public static native void nativeAddJoystick(int p0, java.lang.String p1, java.lang.String p2, int p3, int p4, int p5, int p6, int p7, int p8, boolean p9, boolean p10, boolean p11, boolean p12);
    public static native void nativeRemoveHaptic(int p0);
    public static native void nativeRemoveJoystick(int p0);
    public static native void nativeSetupJNI();
    public static native void onNativeHat(int p0, int p1, int p2, int p3);
    public static native void onNativeJoy(int p0, int p1, float p2);
    public static native void onNativeJoySensor(int p0, int p1, long p2, float p3, float p4, float p5);
    public static native boolean onNativePadDown(int p0, int p1, int p2);
    public static native boolean onNativePadUp(int p0, int p1, int p2);
}
