package org.emulationstation.frontend.netplay;
import java.util.*;
import java.util.concurrent.*;
/** Test fixture only. Never shipped or linked to the application. */
public final class StationPsxBridge {
    static int result, releaseResult, calls, remote, released;
    static long deliveryId;
    static boolean admit = true;
    static Runnable beforeRelease;
    static final Set<Long> receipts = Collections.synchronizedSet(new HashSet<Long>());
    static final BlockingQueue<byte[]> outgoing = new LinkedBlockingQueue<byte[]>();
    static void reset() { result=releaseResult=calls=remote=released=0;deliveryId=0;admit=true;beforeRelease=null;receipts.clear();outgoing.clear(); }
    public static int nativeDeliver(int slot,long id,byte[] frame) { calls++;remote=slot;deliveryId=id;if(admit&&(result==0||result==1||result==8))receipts.add(id);return result; }
    public static boolean nativeCopied(long id) { return receipts.contains(id); }
    public static int nativeReleaseReceipt(long id) { if(beforeRelease!=null)beforeRelease.run();released++;if(releaseResult==0)receipts.remove(id);return releaseResult; }
    public static byte[] nativeTakeOutgoing() { return outgoing.poll(); }
}
