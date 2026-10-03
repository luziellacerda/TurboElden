package org.emulationstation.frontend.station;
public final class StationFrontendDeviceTest {
 static {System.loadLibrary("station_frontend");}
 private static native int run();
 public static void main(String[] args){int count=run();if(count<1)throw new AssertionError("No native checks executed");System.out.println("PASS "+count+" native frontend checks");}
}
