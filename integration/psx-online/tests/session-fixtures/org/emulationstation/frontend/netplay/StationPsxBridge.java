// Test fixture dispatch only; real schema preserved. Never packaged.
// SPDX-License-Identifier: GPL-2.0-or-later
package org.emulationstation.frontend.netplay;

/** JNI for the opt-in PSX owner. No method executes a core from the Java thread. */
public final class StationPsxBridge {
    private StationPsxBridge() {}
    static Runnable beforeStatus;static long[] status=new long[20];static int resumeCalls,controlCalls,failCalls,exitCalls;static long controlEpoch,controlSerial;static boolean controlPause,controlVisible;
    static void reset(){status=new long[20];resumeCalls=controlCalls=failCalls=exitCalls=0;beforeStatus=null;}
    public static boolean nativePrepare(String c,String r,String h,byte[] b,int s,int m){return true;}
    public static void nativePreparationFailed(String s){}public static void nativeAuthorizeHumanExit(){exitCalls++;}
    public static void nativeFail(String c){failCalls++;}public static int nativeControl(long e,long s,boolean p,boolean v){controlCalls++;controlEpoch=e;controlSerial=s;controlPause=p;controlVisible=v;return 0;}
    public static int nativeResume(long e,long s){resumeCalls++;return 0;}public static long[] nativeTakeCommit(){return null;}
    // EXACT 20-field status, all 64-bit. RendererReady does NOT imply core READY.
    // 0 coreReady,1 failed,2 localPaused,3 humanAuthorized,4 epoch,5 controlSerial,
    // 6 nextFrame,7 stateSerial,8 paused,9 stateReady,10 inFrame,11 applyingState,
    // 12 closed,13 pauseAckValid,14 pauseAckEpoch,15 pauseAckSerial,
    // 16 pauseAckNextFrame,17 pauseAckStateSerial,18 initialStateSynced,19 drained.
    public static final int STATUS_FIELDS=20, CORE_READY=0, FAILED=1, LOCAL_PAUSED=2,
            HUMAN_AUTHORIZED=3, EPOCH=4, CONTROL_SERIAL=5, NEXT_FRAME=6, STATE_SERIAL=7,
            PAUSED=8, STATE_READY=9, IN_FRAME=10, APPLYING_STATE=11, CLOSED=12,
            ACK_VALID=13, ACK_EPOCH=14, ACK_SERIAL=15, ACK_FRAME=16, ACK_STATE=17,
            INITIAL_STATE_SYNCED=18, DRAINED=19;
    // Names used by the common Session; aliases have the same fixed schema.
    public static final int STATUS_LENGTH=STATUS_FIELDS, S_FAILED=FAILED,
            S_PAUSE_VALID=ACK_VALID, S_PAUSE_EPOCH=ACK_EPOCH, S_PAUSE_SERIAL=ACK_SERIAL,
            S_INITIAL_SYNCED=INITIAL_STATE_SYNCED, S_DRAINED=DRAINED;
    public static long[] nativeStatus(){if(beforeStatus!=null)beforeStatus.run();return status.clone();}
}
