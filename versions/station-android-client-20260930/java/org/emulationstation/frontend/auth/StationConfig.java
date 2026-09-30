package org.emulationstation.frontend.auth;

/** Values are replaced only in a reviewed commercial build. */
public final class StationConfig {
    public static final String PRODUCT = "TURBORAMA_STATION_ANDROID";
    public static final String APPLICATION = "TURBORAMA_STATION_ANDROID";
    public static final String CLIENT_VERSION = "1";

    // No production endpoint or verification key was supplied in the server handoff.
    // The existing installed APK keeps its current login until the contract is delivered.
    public static final boolean ENABLED = false;
    public static final String BASE_URL = "";
    public static final String SERVER_KEY_ID = "";
    public static final String SERVER_PUBLIC_KEY_SPKI_BASE64URL = "";

    private StationConfig() {}

    public static boolean ready() {
        return ENABLED && BASE_URL.startsWith("https://")
                && !SERVER_KEY_ID.isEmpty() && !SERVER_PUBLIC_KEY_SPKI_BASE64URL.isEmpty();
    }
}
