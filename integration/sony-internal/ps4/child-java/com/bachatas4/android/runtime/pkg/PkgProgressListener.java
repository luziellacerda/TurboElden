package com.bachatas4.android.runtime.pkg;

public interface PkgProgressListener {
    /** Exact native GetMethodID signature (JJLjava/lang/String;)V. */
    void onProgress(long completed, long total, String relativePath);
}
