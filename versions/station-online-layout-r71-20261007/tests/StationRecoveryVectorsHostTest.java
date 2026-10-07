package org.emulationstation.frontend.netplay;

/** Pass the immutable public fixture through the in-memory runner's JVM property. */
public final class StationRecoveryVectorsHostTest {
    public static void main(String[] args) throws Exception {
        String path = System.getProperty("station.recovery.vectors");
        if (path == null || path.isEmpty()) throw new AssertionError("Public recovery fixture is required");
        StationRecoveryVectorsTest.main(new String[]{path});
        if (StationRecoveryVectorsTest.checks != 32) throw new AssertionError("Expected the original 32 public vectors");
        System.out.println("StationRecoveryVectorsHostTest: 32 checks passed");
    }
}
