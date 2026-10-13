package org.station.audit;

/** Standalone shell-process audit. No Activity, app storage or application IPC. */
public final class R139ResourceProbe {
    private static native int[] initialize();
    private static native int[] javaOwner();
    private static native int[] nativeOwners();

    private static void require(boolean ok, String category) {
        if (!ok) throw new AssertionError(category);
    }
    private static void numbers(String category, int[] values) {
        StringBuilder text = new StringBuilder(category);
        for (int value : values) text.append(' ').append(value);
        System.out.println(text.toString());
    }
    public static void main(String[] args) throws Exception {
        require(args.length == 1, "arguments");
        System.load(args[0]);
        int[] init = initialize();
        numbers("INITIALIZE", init);
        require(init.length == 5 && init[0] == 100 && init[1] == 1 && init[2] == 1
                && init[3] == 1 && init[4] == 1, "key-initialization");
        int[] main = javaOwner();
        numbers("JAVA_MAIN", main);
        require(main.length == 3 && main[0] == 20 && main[1] == 20 && main[2] == 0,
                "java-main-ownership");
        final int[][] returned = new int[1][];
        Thread thread = new Thread(() -> returned[0] = javaOwner(), "R139-Java-owned");
        thread.start(); thread.join(5000);
        require(!thread.isAlive(), "java-owner-timeout");
        numbers("JAVA_THREAD", returned[0]);
        require(returned[0].length == 3 && returned[0][0] == 20 && returned[0][1] == 20
                && returned[0][2] == 0, "java-thread-ownership");
        int[] nativeResult = nativeOwners();
        numbers("NATIVE_OWNERS", nativeResult);
        require(nativeResult.length == 15 && nativeResult[0] == 8 && nativeResult[1] == 160
                && nativeResult[2] == 160 && nativeResult[3] == 8 && nativeResult[4] == 8
                && nativeResult[5] == 8 && nativeResult[6] == 8 && nativeResult[7] == 8
                && nativeResult[8] == 0 && nativeResult[9] == 0 && nativeResult[10] == 0
                && nativeResult[11] == 1 && nativeResult[12] == 1 && nativeResult[13] == 0
                && nativeResult[14] == 0, "native-thread-ownership");
        System.out.println("PASS R139_ANDROID_JNI_RESOURCE_PROBE");
    }
}
