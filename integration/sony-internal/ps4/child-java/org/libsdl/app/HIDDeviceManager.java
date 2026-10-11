package org.libsdl.app;

/** Exact pinned PS4 JNI_OnLoad declarations; isolated from Station SDL. */
public final class HIDDeviceManager {
    public native void HIDDeviceRegisterCallback();
    public native void HIDDeviceReleaseCallback();
    public native void HIDDeviceConnected(int p0, java.lang.String p1, int p2, int p3, java.lang.String p4, int p5, java.lang.String p6, java.lang.String p7, int p8, int p9, int p10, int p11, boolean p12);
    public native void HIDDeviceDisconnected(int p0);
    public native void HIDDeviceInputReport(int p0, byte[] p1);
    public native void HIDDeviceOpenPending(int p0);
    public native void HIDDeviceOpenResult(int p0, boolean p1);
    public native void HIDDeviceReportResponse(int p0, byte[] p1);
}
