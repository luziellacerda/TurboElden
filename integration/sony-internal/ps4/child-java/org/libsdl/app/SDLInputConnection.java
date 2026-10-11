package org.libsdl.app;

/** Exact pinned PS4 JNI_OnLoad declarations; isolated from Station SDL. */
public final class SDLInputConnection {
    public static native void nativeCommitText(java.lang.String p0, int p1);
    public static native void nativeGenerateScancodeForUnichar(char p0);
}
