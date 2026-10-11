package org.libsdl.app;

/** Exact pinned PS4 JNI_OnLoad declarations; isolated from Station SDL. */
public final class SDLActivity {
    public static native void nativeAddTouch(int p0, java.lang.String p1);
    public static native boolean nativeAllowRecreateActivity();
    public static native int nativeCheckSDLThreadCounter();
    public static native void nativeCleanupMainThread();
    public static native void nativeFocusChanged(boolean p0);
    public static native java.lang.String nativeGetHint(java.lang.String p0);
    public static native boolean nativeGetHintBoolean(java.lang.String p0, boolean p1);
    public static native java.lang.String nativeGetVersion();
    public static native void nativeInitMainThread();
    public static native void nativeLowMemory();
    public static native void nativePause();
    public static native void nativePermissionResult(int p0, boolean p1);
    public static native void nativeQuit();
    public static native void nativeResume();
    public static native int nativeRunMain(java.lang.String p0, java.lang.String p1, java.lang.Object p2);
    public static native void nativeSendQuit();
    public static native void nativeSetNaturalOrientation(int p0);
    public static native void nativeSetScreenResolution(int p0, int p1, int p2, int p3, float p4, float p5);
    public static native void nativeSetenv(java.lang.String p0, java.lang.String p1);
    public static native void nativeSetupJNI();
    public static native void onNativeAccel(float p0, float p1, float p2);
    public static native void onNativeClipboardChanged();
    public static native void onNativeDarkModeChanged(boolean p0);
    public static native void onNativeDropFile(java.lang.String p0);
    public static native void onNativeFileDialog(int p0, java.lang.String[] p1, int p2);
    public static native void onNativeInsetsChanged(int p0, int p1, int p2, int p3);
    public static native void onNativeKeyDown(int p0);
    public static native void onNativeKeyUp(int p0);
    public static native void onNativeKeyboardFocusLost();
    public static native void onNativeLocaleChanged();
    public static native void onNativeMouse(int p0, int p1, float p2, float p3, boolean p4);
    public static native void onNativePen(int p0, int p1, int p2, int p3, float p4, float p5, float p6);
    public static native void onNativePinchEnd();
    public static native void onNativePinchStart();
    public static native void onNativePinchUpdate(float p0);
    public static native void onNativeResize();
    public static native void onNativeRotationChanged(int p0);
    public static native void onNativeScreenKeyboardHidden();
    public static native void onNativeScreenKeyboardShown();
    public static native boolean onNativeSoftReturnKey();
    public static native void onNativeSurfaceChanged();
    public static native void onNativeSurfaceCreated();
    public static native void onNativeSurfaceDestroyed();
    public static native void onNativeTouch(int p0, int p1, int p2, float p3, float p4, float p5);
}
