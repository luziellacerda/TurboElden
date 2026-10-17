// JVM lifecycle fixture only. Never packaged or evidence of an actual radio mode.
package android.net.wifi;
public class WifiManager {
    public static final int WIFI_MODE_FULL_HIGH_PERF=3, WIFI_MODE_FULL_LOW_LATENCY=4;
    public int creates,acquires,releases;
    public boolean denyAcquire,failAfterAcquire,failReleaseOnce;
    public WifiLock last;
    public WifiLock createWifiLock(int mode,String tag){creates++;return last=new WifiLock(mode,tag);}
    public final class WifiLock {
        public final int mode;public final String tag;public boolean referenceCounted=true,held;
        WifiLock(int mode,String tag){this.mode=mode;this.tag=tag;}
        public void setReferenceCounted(boolean value){referenceCounted=value;}
        public void acquire(){acquires++;if(denyAcquire)throw new SecurityException("fixture");held=true;if(failAfterAcquire)throw new IllegalStateException("fixture");}
        public void release(){if(failReleaseOnce){failReleaseOnce=false;throw new IllegalStateException("fixture");}if(!held)throw new IllegalStateException("under-lock fixture");held=false;releases++;}
        public boolean isHeld(){return held;}
    }
}
