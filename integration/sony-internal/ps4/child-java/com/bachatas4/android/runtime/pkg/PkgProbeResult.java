package com.bachatas4.android.runtime.pkg;

public final class PkgProbeResult {
    public final String contentId;
    public final long packageSize, pfsImageSize;
    public final String titleHint;
    public final PkgStatus status;
    public final String message;
    public PkgProbeResult(String id, long bytes, long imageBytes, String title,
                          PkgStatus state, String detail) {
        contentId=id; packageSize=bytes; pfsImageSize=imageBytes;
        titleHint=title; status=state; message=detail;
    }
}
