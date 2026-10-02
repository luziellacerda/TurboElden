package org.emulationstation.frontend.station;

/** Public connection identity copied from the verified Station client; no local-login fallback. */
public final class StationConfig {
    public static final boolean ENABLED = true;
    public static final String BASE_URL = "https://app.lzgames.com.br";
    public static final String TLS_SPKI_SHA256 = "13f9dcbb7a9687c2f88ff73de5621cfab849d0ec02191dcdd1ee8a6275dacba7";
    public static final String STATION_ASSERTION_KEY_ID = "06b41b778041d81b5b86a115a031418e0c4b0b2bd24ec8b340e62eaa82fb5268";
    public static final String STATION_ASSERTION_SPKI_BASE64URL = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAo6sEDAwUywSCV0Yh9HY6PssYu8JH5ghGtIag-lIHqVVLNU7tZoRvc3_y0uPojGMpLAk3EtY8JmYLzC1klwQw2dujbTZop8k9nHnqVj6QwjHntUFIeNzDoDdF0XdxO2nBU8op0OqVp0xPg31Zcik69Lt-2YJcfkQrINjR3Ss6d4mRm3u9RcUfksv6A9fzt-KAin4dhreICH6qn892W_Xq0X5jFFzI9w135rY3ijgYB5cyhd19i0-Y1vXFNyNVpoyk01UCbWxrL11PYBHEjbqs78eS7hZmWjyqNQLcy9n7wlwlsesq7QsK3SchzaQSCAJpXDLHHh8xz1pP_EzjUscItwIDAQAB";
    public static final String PRODUCT = "TURBORAMA_STATION_ANDROID";
    public static final String APPLICATION = "TURBORAMA_STATION_ANDROID";
    public static final String CLIENT_VERSION = "1";

    private StationConfig() {}

    public static boolean ready() {
        return ENABLED
            && BASE_URL.startsWith("https://")
            && !BASE_URL.endsWith("/")
            && TLS_SPKI_SHA256.length() == 64
            && STATION_ASSERTION_KEY_ID.length() == 64
            && STATION_ASSERTION_SPKI_BASE64URL.length() >= 300
            && STATION_ASSERTION_SPKI_BASE64URL.indexOf('+') < 0
            && STATION_ASSERTION_SPKI_BASE64URL.indexOf('/') < 0
            && STATION_ASSERTION_SPKI_BASE64URL.indexOf('=') < 0
            && STATION_ASSERTION_SPKI_BASE64URL.indexOf(' ') < 0;
    }
}
