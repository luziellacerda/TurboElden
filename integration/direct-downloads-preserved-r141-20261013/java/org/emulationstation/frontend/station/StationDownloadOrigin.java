package org.emulationstation.frontend.station;

/** Dedicated, pinned origin for a single authorized artifact GET; all other routes keep BASE_URL. */
public final class StationDownloadOrigin {
    public static final String BASE_URL = "https://downloads-station.lzgames.com.br";
    public static final String TLS_SPKI_SHA256 = "bcd134d59fcdbb35e0343c86d31a666cc95cf158d70b27aceceefd19158d072f";
    private static final String PREFIX = "/v1/station/artifacts/";

    private StationDownloadOrigin() {}

    static boolean applies(String method, String path) {
        return "GET".equals(method) && path.startsWith(PREFIX)
            && StationProtocol.activationCode(path.substring(PREFIX.length()));
    }
}
