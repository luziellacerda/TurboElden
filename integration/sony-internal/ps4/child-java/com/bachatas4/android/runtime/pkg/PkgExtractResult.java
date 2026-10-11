package com.bachatas4.android.runtime.pkg;

public final class PkgExtractResult {
    public final PkgStatus status;
    public final String message, contentId;
    public PkgExtractResult(PkgStatus state, String detail, String id) {
        status=state; message=detail; contentId=id;
    }
}
