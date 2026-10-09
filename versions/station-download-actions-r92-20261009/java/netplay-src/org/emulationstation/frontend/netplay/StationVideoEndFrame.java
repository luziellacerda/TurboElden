package org.emulationstation.frontend.netplay;

/** Packaged previews are CFR30. Hold the last displayed frame minus two frames. */
final class StationVideoEndFrame {
    static long positionMs(int durationMs){
        long count=(Math.max(0L,(long)durationMs)*30L+500L)/1000L;
        long index=Math.max(0L,count-1L-2L);
        return (index*1000L+15L)/30L;
    }
}
