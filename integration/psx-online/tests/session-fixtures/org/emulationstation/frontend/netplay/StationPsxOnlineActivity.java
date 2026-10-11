// Test fixture only. Never packaged.
package org.emulationstation.frontend.netplay;import android.app.*;public class StationPsxOnlineActivity extends Activity{public int retireCalls;public boolean canFinishSdlOwner(){return false;}public void recordOwnerThread(){}public void finishRetiredOwner(){retireCalls++;} }
