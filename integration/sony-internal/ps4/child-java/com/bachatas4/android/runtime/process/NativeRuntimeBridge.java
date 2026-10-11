package com.bachatas4.android.runtime.process;

import android.view.Surface;
import java.util.function.IntConsumer;

/** JNI names and descriptors pinned to Bachata S4 0.2.4. Loaded only by Ps4ClassLoader. */
public final class NativeRuntimeBridge {
    private static volatile IntConsumer exitListener;
    private NativeRuntimeBridge() {}
    public static void setExitListener(IntConsumer listener) { exitListener = listener; }
    public static native int run(Surface surface, boolean catalogue, String[] argv,
                                 String[] environment, String workingDirectory, int outputFd);
    public static native void stop();
    public static void onNativeExit(int code) {
        IntConsumer listener = exitListener;
        if (listener != null) listener.accept(code);
    }
}
