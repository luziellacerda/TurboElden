package org.emulationstation.frontend.netplay;

/** Actual Dolphin NetPlay API. Native symbols are compiled into the isolated
 * online Dolphin library; this class deliberately does not load ordinary libdolp.
 *
 * The owner passes a fresh official NetplaySession and GameFile. Collect its
 * launchGame flow and launch Dolphin's real EmulationActivity: its fragment calls
 * RunNetPlay and consumes the original BootSessionData. Do not open RetroArch.
 *
 * Session operations run on one worker, never the UI thread. Close transport may
 * run independently to cancel a blocked connect; await that worker before the
 * official session's closeBlocking releases its pointers. Never release native
 * pointers from two owners concurrently.
 */
public final class StationDolphinBridge {
    private StationDolphinBridge() {}
    public static final String PROTOCOL="station-stream.v3";
    public static final String DATAGRAM_FORMAT="DPL1";
    public static final int MAX_DATAGRAM=1392, MAX_FRAME=1400;

    /** Native masks use bits 1..4 (slot 1 = 0x02); convert app device masks << 1.
     * Configure after original Dolphin init/directory initialization, before
     * creating the official session. Initial epoch must be positive (1 is valid).
     * Library selection happens earlier, before DolphinApplication loads JNI. */
    public static native boolean nativeConfigure(boolean host,int authenticatedSlot,
            int authenticatedSlotMask,int directPort,long epoch,String nickname);
    public static native boolean nativeConnect(Object officialSession,boolean host);
    public static native void nativeSelectGame(Object officialSession,Object officialGameFile);
    /** Exact authenticated slot to current native PID. Zero means not connected. */
    public static native int nativePlayerForSlot(Object officialSession,int authenticatedSlot);
    /** Four entries each: authenticated slot, or zero for an unused port. */
    public static native boolean nativeMapControllers(Object officialSession,int[] gamecube,int[] wiimotes);
    public static native boolean nativeStartGame(Object officialSession);
    /** Returns only after CPU idle is synchronized, without advancing a frame. */
    public static native boolean nativePauseAtEpoch(Object officialSession,long epoch);
    /** Freeze immediately on the WSS control thread, including a blocked Join.
     * This is NOT pausedAtEpoch/CPU-idle evidence; the worker must still invoke
     * nativePauseAtEpoch before sending the global recovery barrier ACK. */
    public static native boolean nativeSuspendTransport(long epoch);
    /** Publish every accepted AtomicReference control immediately, including
     * pause=false. Positive serial must increase for each accepted revision.
     * False means stale/superseded or inactive; do not turn supersession fatal. */
    public static native boolean nativeControl(long epoch,long controlSerial,boolean pause);
    /** Only call after fresh, authenticated global STATE paused=false for this epoch.
     * Local drain or READY alone does not authorize this call. */
    public static native boolean nativeResumeAtEpoch(long epoch,long controlSerial);
    public static native byte[] nativeTakeOutgoing(int authenticatedRemoteSlot,int timeoutMs);
    /** 1 accepted, 0 temporarily blocked/not attached, -1 invalid. Retry 0 with
     * the same ID and bytes, without an outer ACK; -1 is a protocol failure. */
    public static native int nativeDeliver(int authenticatedRemoteSlot,long uniqueDeliveryId,byte[] completeFrame);
    /** True means ENet received the complete datagram. Only then acknowledge the
     * outer Station byte offset. False on this bounded wait means keep waiting;
     * it does not authorize reconnecting or closing the emulator. */
    public static native boolean nativeAwaitDelivery(long uniqueDeliveryId,int timeoutMs);
    public static native boolean nativeDrained();
    public static native String nativeFailure();
    /** Permanent categorical protocol/core error. Freezes without destroying
     * the engine. Independent of Connect; nativeResume rejects any failure. */
    public static native void nativeFail(String categoricalCode);
    public static final int ACTIVE=1, HOST=2, CLIENT_CONNECTED=4, SERVER_CONNECTED=8,
            CORE_RUNNING=16, CPU_STEPPING=32, SUSPENDED=64, FAILED=128,
            LOCAL_DRAINED=256, EXACT_HOST_ROSTER=512;
    /** Read on the session worker. CORE_RUNNING includes normal paused cores;
     * CPU idle is established only by a successful nativePauseAtEpoch ACK. */
    public static native int nativeStatus(Object officialSession);
    public static native long nativeAcknowledgedEpoch();
    /** Exact registered roster, also bits 1..4, never the app's bits 0..3. */
    public static native int nativeRegisteredSlots(Object officialSession);
    /** Call only from the explicit human Exit/Cancel action. Independent of the
     * worker lock, so blocked Connect can be cancelled without tearing pointers.
     * Idempotent before configure; accepts null when official construction fails. */
    public static native boolean nativeAuthorizeHumanExit(Object officialSession);
    /** After human authorization: close transport, await worker, official
     * closeBlocking/StopEmulation, RESULT, then terminate the exclusive process.
     * Fatal or WSS failure pauses; it does not authorize closing a running core. */
    public static native void nativeCloseTransport();
}
