package com.bachatas4.android.runtime.pkg;

/** No loadLibrary fallback: the child bootstrap loads the pinned private library first. */
public final class PkgExtractor {
    private PkgExtractor() {}
    public static native PkgProbeResult nativeProbe(int fd);
    public static native PkgExtractResult nativeExtract(int fd, String directory, String passcode,
                                                        PkgProgressListener listener);
    public static native void nativeCancel();
}
