/* SPDX-License-Identifier: GPL-3.0-or-later */
package org.emulationstation.frontend.netplay;

/** Separate app_process audit class. This class must never enter the APK. */
public final class StationStartupLogging {
    private static native boolean enable(String exactRuntimePath);

    private static void expect(boolean condition) {
        if (!condition) throw new IllegalStateException("Probe assertion");
    }

    public static void main(String[] args) {
        try {
            expect(args.length == 2);
            String runtime = args[0];
            System.load(args[1]);
            expect(!enable(null));
            expect(!enable("libstation_retroarch.so"));
            expect(!enable("/data/local/tmp/incorrect.so"));
            expect(!enable("/data/local/tmp/../libstation_retroarch.so"));
            expect(!enable(runtime));
            System.load(runtime);
            expect(enable(runtime));
            expect(enable(runtime));
            System.out.println("{\"cases\":7,\"passed\":true,\"nativeActivityStarted\":false,\"gameplayValidated\":false}");
        } catch (Throwable error) {
            System.out.println("{\"passed\":false,\"category\":\"PROBE_FAILED\"}");
            System.exit(2);
        }
    }
}
