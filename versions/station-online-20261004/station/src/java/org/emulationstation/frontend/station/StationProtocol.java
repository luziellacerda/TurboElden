package org.emulationstation.frontend.station;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;

/** Wire format of Servidor-pix 93efbba. Base64URL, no padding, no Suite proof domain. */
public final class StationProtocol {
    public static final String REQUEST_ACTIVATION = "TurboRamaStationAndroid/request-activation-challenge/v1";
    public static final String ACTIVATION_CHALLENGE = "TurboRamaStationAndroid/activation-challenge/v1";
    public static final String ACTIVATE = "TurboRamaStationAndroid/activate/v1";
    public static final String ACTIVATED = "TurboRamaStationAndroid/activated/v1";
    public static final String REQUEST_SESSION = "TurboRamaStationAndroid/request-session-challenge/v1";
    public static final String SESSION_CHALLENGE = "TurboRamaStationAndroid/session-challenge/v1";
    public static final String OPEN_SESSION = "TurboRamaStationAndroid/open-session/v1";
    public static final String SESSION = "TurboRamaStationAndroid/session/v1";
    public static final String PROFILE = "TurboRamaStationAndroid/profile/v1";
    public static final String CATALOG = "TurboRamaStationAndroid/catalog/v1";
    public static final String REQUEST_DOWNLOAD = "TurboRamaStationAndroid/request-download/v1";
    public static final String DOWNLOAD_GRANT = "TurboRamaStationAndroid/download-grant/v1";
    public static final int MAXIMUM_BODY_BYTES = 8192;
    public static final int CATALOG_BODY_BYTES = 64 * 1024 * 1024;
    public static final int COVER_BODY_BYTES = 5 * 1024 * 1024;

    private StationProtocol() {}

    public static String deviceId(byte[] spki) {
        return base64Url(sha256(spki));
    }

    public static boolean libraryId(String value) {
        if (value == null || value.length() < 8 || value.length() > 64 || value.indexOf("..") >= 0) return false;
        for (int index = 0; index < value.length(); index++) {
            char item = value.charAt(index);
            boolean allowed = (item >= 'A' && item <= 'Z') || (item >= 'a' && item <= 'z')
                || (item >= '0' && item <= '9') || item == '-' || item == '_';
            if (!allowed) return false;
        }
        return true;
    }

    public static boolean licenseId(String value) {
        if (value == null || value.length() < 6 || value.length() > 64) return false;
        for (int index = 0; index < value.length(); index++) {
            char item = value.charAt(index);
            boolean allowed = (item >= 'A' && item <= 'Z') || (item >= 'a' && item <= 'z')
                || (item >= '0' && item <= '9') || item == '-' || item == '_';
            if (!allowed) return false;
        }
        return true;
    }

    public static boolean activationCode(String value) {
        try {
            return base64Url(decode(value)).equals(value) && decode(value).length == 32;
        } catch (IllegalArgumentException failure) {
            return false;
        }
    }

    public static String base64Url(byte[] data) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(data);
    }

    public static byte[] decode(String value) {
        if (value == null || value.isEmpty() || value.indexOf('+') >= 0
            || value.indexOf('/') >= 0 || value.indexOf('=') >= 0 || value.indexOf(' ') >= 0) {
            throw new IllegalArgumentException("Station encoding is invalid.");
        }
        byte[] bytes = Base64.getUrlDecoder().decode(value);
        if (!base64Url(bytes).equals(value)) throw new IllegalArgumentException("Station encoding is invalid.");
        return bytes;
    }

    public static byte[] sha256(byte[] data) {
        try { return MessageDigest.getInstance("SHA-256").digest(data); }
        catch (Exception failure) { throw new IllegalStateException(failure); }
    }

    public static byte[] identity(String domain, String deviceId, String manufacturer,
            String model, int androidSdk, String extraJson) {
        String json = "{"
            + field("schemaVersion", 1)
            + "," + field("domain", domain)
            + "," + field("productId", StationConfig.PRODUCT)
            + "," + field("applicationId", StationConfig.APPLICATION)
            + "," + field("deviceId", deviceId)
            + "," + field("clientVersion", StationConfig.CLIENT_VERSION)
            + "," + field("deviceManufacturer", manufacturer)
            + "," + field("deviceModel", model)
            + "," + field("androidSdk", androidSdk)
            + (extraJson == null || extraJson.isEmpty() ? "" : "," + extraJson)
            + "}";
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        if (bytes.length > MAXIMUM_BODY_BYTES) throw new IllegalArgumentException("Station request is too large.");
        return bytes;
    }

    public static String field(String name, String value) {
        return quote(name) + ":" + quote(value);
    }

    public static String field(String name, int value) {
        return quote(name) + ":" + Integer.toString(value);
    }

    public static String quote(String value) {
        StringBuilder builder = new StringBuilder(value.length() + 2);
        builder.append('"');
        for (int index = 0; index < value.length(); index++) {
            char item = value.charAt(index);
            switch (item) {
                case '"': builder.append("\\\""); break;
                case '\\': builder.append("\\\\"); break;
                case '\b': builder.append("\\b"); break;
                case '\f': builder.append("\\f"); break;
                case '\n': builder.append("\\n"); break;
                case '\r': builder.append("\\r"); break;
                case '\t': builder.append("\\t"); break;
                default:
                    if (item < 0x20) throw new IllegalArgumentException("Station text is invalid.");
                    else builder.append(item);
                    break;
            }
        }
        builder.append('"');
        return builder.toString();
    }
}
