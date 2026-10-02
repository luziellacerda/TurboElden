package org.emulationstation.frontend.auth;

import android.os.Build;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.PublicKey;
import java.security.Signature;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.security.spec.MGF1ParameterSpec;
import java.security.spec.PSSParameterSpec;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;
import org.json.JSONObject;

/** Station client. List, cover, and game bytes. No stored address. */
public final class StationClient {
    private static final PSSParameterSpec PSS = new PSSParameterSpec("SHA-256", "MGF1", MGF1ParameterSpec.SHA256, 32, 1);

    private StationClient() {}

    public static String activate(android.content.Context context, String code) throws Exception {
        if (!StationConfig.ready()) throw new IllegalStateException("Station is not configured.");
        if (!StationProtocol.activationCode(code)) throw new IllegalArgumentException("Activation code is invalid.");
        PublicKey key = StationCrypto.publicKey();
        String spki = StationProtocol.base64Url(key.getEncoded());
        String deviceId = StationProtocol.deviceId(key.getEncoded());
        String manufacturer = text(Build.MANUFACTURER, 100);
        String model = text(Build.MODEL, 100);
        int sdk = Build.VERSION.SDK_INT;
        byte[] body = StationProtocol.identity(StationProtocol.REQUEST_ACTIVATION, deviceId, manufacturer, model, sdk,
            StationProtocol.field("activationCode", code) + "," + StationProtocol.field("devicePublicKey", spki));
        JSONObject challenge = verified(post(StationProtocolPath.activationChallenge(), body, null),
            StationProtocol.ACTIVATION_CHALLENGE);
        if (challenge.optInt("expiresInSeconds") != 60) throw new SecurityException("Station challenge lifetime was rejected.");
        byte[] proof = StationProtocol.identity(StationProtocol.ACTIVATE, deviceId, manufacturer, model, sdk,
            StationProtocol.field("activationCode", code) + "," + StationProtocol.field("devicePublicKey", spki)
            + "," + StationProtocol.field("challengeId", challenge.getString("challengeId"))
            + "," + StationProtocol.field("nonce", challenge.getString("nonce")));
        JSONObject activated = verified(post(StationProtocolPath.activationComplete(), envelope(proof), null),
            StationProtocol.ACTIVATED);
        String licenseId = activated.getString("licenseId");
        if (!StationProtocol.licenseId(licenseId)) throw new SecurityException("Station license was rejected.");
        return licenseId;
    }

    public static String openSession(android.content.Context context, String licenseId) throws Exception {
        if (!StationConfig.ready()) throw new IllegalStateException("Station is not configured.");
        PublicKey key = StationCrypto.publicKey();
        String deviceId = StationProtocol.deviceId(key.getEncoded());
        String manufacturer = text(Build.MANUFACTURER, 100);
        String model = text(Build.MODEL, 100);
        int sdk = Build.VERSION.SDK_INT;
        byte[] body = StationProtocol.identity(StationProtocol.REQUEST_SESSION, deviceId, manufacturer, model, sdk,
            StationProtocol.field("licenseId", licenseId));
        JSONObject challenge = verified(post(StationProtocolPath.challenge(), body, null),
            StationProtocol.SESSION_CHALLENGE);
        if (challenge.optInt("expiresInSeconds") != 60) throw new SecurityException("Station challenge lifetime was rejected.");
        byte[] proof = StationProtocol.identity(StationProtocol.OPEN_SESSION, deviceId, manufacturer, model, sdk,
            StationProtocol.field("licenseId", licenseId)
            + "," + StationProtocol.field("challengeId", challenge.getString("challengeId"))
            + "," + StationProtocol.field("nonce", challenge.getString("nonce")));
        JSONObject session = verified(post(StationProtocolPath.session(), envelope(proof), null),
            StationProtocol.SESSION);
        if (session.optInt("expiresInSeconds") != 180) throw new SecurityException("Station session lifetime was rejected.");
        String token = session.getString("accessToken");
        if (!StationProtocol.activationCode(token)) throw new SecurityException("Station session token was rejected.");
        return token;
    }

    public static String profile(String accessToken) throws Exception {
        JSONObject envelope = post(StationProtocolPath.profile(), null, accessToken);
        if (envelope == null) return "";
        JSONObject profile = verified(envelope, StationProtocol.PROFILE);
        String name = profile.optString("displayName", "");
        if (name.length() > 80) name = name.substring(0, 80);
        return name;
    }

    public static JSONObject catalog(String accessToken) throws Exception {
        Reply reply = getBytes(StationProtocolPath.catalog(), accessToken, StationProtocol.CATALOG_BODY_BYTES, 60000);
        if (reply.status == 503) return null;
        if (reply.redirect || reply.status != 200 || !jsonObject(reply.body)) {
            throw new SecurityException("Station catalog was denied.");
        }
        return verified(new JSONObject(new String(reply.body, StandardCharsets.UTF_8)), StationProtocol.CATALOG);
    }

    public static String saveCover(String accessToken, String coverId, File destination) throws Exception {
        if (!StationProtocol.libraryId(coverId)) throw new IllegalArgumentException("Station cover was rejected.");
        return saveBody(StationProtocolPath.cover(coverId), accessToken, destination,
            StationProtocol.COVER_BODY_BYTES, 20000, true);
    }

    public static String authorize(android.content.Context context, String accessToken, String itemId) throws Exception {
        if (!StationConfig.ready()) throw new IllegalStateException("Station is not configured.");
        if (!StationProtocol.libraryId(itemId)) throw new IllegalArgumentException("Station item was rejected.");
        PublicKey key = StationCrypto.publicKey();
        String deviceId = StationProtocol.deviceId(key.getEncoded());
        byte[] body = StationProtocol.identity(StationProtocol.REQUEST_DOWNLOAD, deviceId,
            text(Build.MANUFACTURER, 100), text(Build.MODEL, 100), Build.VERSION.SDK_INT,
            StationProtocol.field("itemId", itemId));
        Reply reply = send("POST", StationProtocolPath.authorize(), body, accessToken, StationProtocol.MAXIMUM_BODY_BYTES, 20000);
        if (reply.redirect || reply.status != 200 || !jsonObject(reply.body)) {
            throw new SecurityException("Station download was denied.");
        }
        JSONObject grant = verified(new JSONObject(new String(reply.body, StandardCharsets.UTF_8)), StationProtocol.DOWNLOAD_GRANT);
        if (grant.optInt("expiresInSeconds") != 60) throw new SecurityException("Station grant lifetime was rejected.");
        String grantId = grant.getString("grantId");
        if (!StationProtocol.activationCode(grantId)) throw new SecurityException("Station grant was rejected.");
        return grantId;
    }

    public static void saveGame(String accessToken, String grantId, File destination) throws Exception {
        if (!StationProtocol.activationCode(grantId)) throw new IllegalArgumentException("Station grant was rejected.");
        saveBody(StationProtocolPath.artifact(grantId), accessToken, destination, 8L * 1024L * 1024L * 1024L, 900000, false);
    }

    private static byte[] envelope(byte[] payload) throws Exception {
        String json = "{\"payload\":" + StationProtocol.quote(StationProtocol.base64Url(payload))
            + ",\"signature\":" + StationProtocol.quote(StationProtocol.base64Url(StationCrypto.sign(payload))) + "}";
        return json.getBytes(StandardCharsets.UTF_8);
    }

    private static JSONObject verified(JSONObject envelope, String domain) throws Exception {
        if (!StationConfig.STATION_ASSERTION_KEY_ID.equals(envelope.getString("keyId"))) {
            throw new SecurityException("Station response was not signed by the pinned authority.");
        }
        byte[] payload = StationProtocol.decode(envelope.getString("payload"));
        byte[] signature = StationProtocol.decode(envelope.getString("signature"));
        Signature verifier = Signature.getInstance("SHA256withRSA/PSS");
        verifier.setParameter(PSS);
        verifier.initVerify(pinnedKey());
        verifier.update(payload);
        if (!verifier.verify(signature)) throw new SecurityException("Station signature was rejected.");
        JSONObject body = new JSONObject(new String(payload, StandardCharsets.UTF_8));
        if (!domain.equals(body.getString("domain"))) throw new SecurityException("Station response domain was rejected.");
        return body;
    }

    private static PublicKey pinnedKey() throws Exception {
        byte[] spki = StationProtocol.decode(StationConfig.STATION_ASSERTION_SPKI_BASE64URL);
        return java.security.KeyFactory.getInstance("RSA").generatePublic(new java.security.spec.X509EncodedKeySpec(spki));
    }

    private static JSONObject post(String path, byte[] body, String bearer) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(StationConfig.BASE_URL + path).openConnection();
        if (connection instanceof HttpsURLConnection) {
            ((HttpsURLConnection) connection).setSSLSocketFactory(pinnedContext().getSocketFactory());
        } else {
            throw new SecurityException("Station requires HTTPS.");
        }
        connection.setInstanceFollowRedirects(false);
        connection.setConnectTimeout(10000);
        connection.setReadTimeout(10000);
        connection.setRequestMethod(body == null ? "GET" : "POST");
        connection.setRequestProperty("Accept", "application/json");
        if (bearer != null) connection.setRequestProperty("Authorization", "Bearer " + bearer);
        if (body != null) {
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            try (OutputStream output = connection.getOutputStream()) { output.write(body); }
        }
        int status = connection.getResponseCode();
        InputStream stream = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
        byte[] response = readLimited(stream);
        if (status == 503 && StationProtocolPath.profile().equals(path)) return null;
        if (status != 200 || !jsonObject(response)) throw new SecurityException("Station request was denied.");
        return new JSONObject(new String(response, StandardCharsets.UTF_8));
    }

    private static SSLContext pinnedContext() throws Exception {
        TrustManagerFactory factory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        factory.init((java.security.KeyStore) null);
        X509TrustManager system = null;
        for (TrustManager manager : factory.getTrustManagers()) {
            if (manager instanceof X509TrustManager) system = (X509TrustManager) manager;
        }
        if (system == null) throw new IllegalStateException("No system trust manager.");
        X509TrustManager base = system;
        X509TrustManager pin = new X509TrustManager() {
            public void checkClientTrusted(X509Certificate[] chain, String authType) { }
            public void checkServerTrusted(X509Certificate[] chain, String authType) throws CertificateException {
                base.checkServerTrusted(chain, authType);
                if (chain == null || chain.length == 0) throw new CertificateException("No server certificate.");
                try {
                    byte[] actual = MessageDigest.getInstance("SHA-256").digest(chain[0].getPublicKey().getEncoded());
                    if (!MessageDigest.isEqual(actual, hex(StationConfig.TLS_SPKI_SHA256))) {
                        throw new CertificateException("SPKI pin mismatch.");
                    }
                } catch (CertificateException failure) {
                    throw failure;
                } catch (Exception failure) {
                    throw new CertificateException("SPKI pin mismatch.");
                }
            }
            public X509Certificate[] getAcceptedIssuers() { return base.getAcceptedIssuers(); }
        };
        SSLContext context = SSLContext.getInstance("TLS");
        context.init(null, new TrustManager[] { pin }, null);
        return context;
    }

    private static final class Reply {
        final int status;
        final byte[] body;
        final boolean redirect;

        Reply(int status, byte[] body, boolean redirect) {
            this.status = status;
            this.body = body;
            this.redirect = redirect;
        }
    }

    private static Reply getBytes(String path, String bearer, int maximum, int readTimeout) throws Exception {
        return send("GET", path, null, bearer, maximum, readTimeout);
    }

    private static Reply send(String method, String path, byte[] body, String bearer, int maximum, int readTimeout) throws Exception {
        HttpURLConnection connection = open(path, method, bearer, readTimeout);
        try {
            if (body != null) {
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                try (OutputStream output = connection.getOutputStream()) { output.write(body); }
            }
            int status = connection.getResponseCode();
            boolean redirect = status / 100 == 3 || connection.getHeaderField("Location") != null;
            InputStream stream = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
            byte[] response = readAtMost(stream, maximum);
            return new Reply(status, response, redirect);
        } finally {
            connection.disconnect();
        }
    }

    private static String saveBody(String path, String bearer, File destination, long maximum, int readTimeout, boolean image) throws Exception {
        HttpURLConnection connection = open(path, "GET", bearer, readTimeout);
        File partial = new File(destination.getParentFile(), destination.getName() + ".part");
        try {
            int status = connection.getResponseCode();
            if (status / 100 == 3 || connection.getHeaderField("Location") != null) {
                throw new SecurityException("Station file redirect was rejected.");
            }
            if (status == 429) throw new SecurityException("Station rate limited.");
            if (status != 200) throw new SecurityException(denied(connection, status));
            long announced = connection.getContentLengthLong();
            if (announced > maximum || (!image && announced < 1)) {
                throw new SecurityException("Station file length was rejected.");
            }
            String type = connection.getContentType() == null ? "" : connection.getContentType().toLowerCase();
            String extension = image ? imageExtension(type) : "";
            if (!image && !type.startsWith("application/octet-stream")) {
                throw new SecurityException("Station file type was rejected.");
            }
            if (partial.getParentFile() != null) partial.getParentFile().mkdirs();
            long total = 0;
            try (InputStream stream = connection.getInputStream(); FileOutputStream output = new FileOutputStream(partial)) {
                byte[] buffer = new byte[8192];
                int read;
                while ((read = stream.read(buffer)) >= 0) {
                    if (image && extension.length() == 0 && total == 0) {
                        extension = sniffedExtension(buffer, read);
                        if (extension.length() == 0) throw new SecurityException("Station cover type was rejected.");
                    }
                    total += read;
                    if (total > maximum || (!image && announced > 0 && total > announced)) {
                        throw new SecurityException("Station file length was rejected.");
                    }
                    output.write(buffer, 0, read);
                }
            }
            if (total < 1 || (!image && total != announced)) {
                throw new SecurityException("Station file length was rejected.");
            }
            if (destination.exists() && !destination.delete()) throw new SecurityException("Station file was not replaced.");
            if (!partial.renameTo(destination)) throw new SecurityException("Station file was not stored.");
            return extension;
        } catch (Exception failure) {
            partial.delete();
            destination.delete();
            throw failure;
        } finally {
            connection.disconnect();
        }
    }

    private static String denied(HttpURLConnection connection, int status) {
        String code = errorCode(connection.getErrorStream());
        if (code.length() == 0) return "s" + status;
        return "s" + status + " " + code;
    }

    private static String errorCode(InputStream stream) {
        if (stream == null) return "";
        try {
            byte[] buffer = new byte[480];
            int count = 0;
            while (count < buffer.length) {
                int read = stream.read(buffer, count, buffer.length - count);
                if (read < 0) break;
                count += read;
            }
            String text = new String(buffer, 0, count, StandardCharsets.UTF_8);
            int at = text.indexOf("STATION_");
            if (at < 0) return "";
            int end = at;
            while (end < text.length()) {
                char item = text.charAt(end);
                if ((item >= 'A' && item <= 'Z') || item == '_') end++;
                else break;
            }
            if (end - at < 9 || end - at > 40) return "";
            return text.substring(at, end);
        } catch (Exception failure) {
            return "";
        }
    }

    private static String imageExtension(String type) {
        if (type.startsWith("image/png")) return "png";
        if (type.startsWith("image/jpeg") || type.startsWith("image/jpg")) return "jpg";
        if (type.startsWith("image/webp")) return "webp";
        if (type.startsWith("image/gif")) return "gif";
        return "";
    }

    private static String sniffedExtension(byte[] buffer, int count) {
        if (count >= 8 && (buffer[0] & 0xff) == 0x89 && buffer[1] == 0x50 && buffer[2] == 0x4e && buffer[3] == 0x47) return "png";
        if (count >= 3 && (buffer[0] & 0xff) == 0xff && (buffer[1] & 0xff) == 0xd8 && (buffer[2] & 0xff) == 0xff) return "jpg";
        if (count >= 6 && buffer[0] == 'G' && buffer[1] == 'I' && buffer[2] == 'F' && buffer[3] == '8') return "gif";
        if (count >= 12 && buffer[0] == 'R' && buffer[1] == 'I' && buffer[2] == 'F' && buffer[3] == 'F'
            && buffer[8] == 'W' && buffer[9] == 'E' && buffer[10] == 'B' && buffer[11] == 'P') return "webp";
        return "";
    }

    private static HttpURLConnection open(String path, String method, String bearer, int readTimeout) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(StationConfig.BASE_URL + path).openConnection();
        if (connection instanceof HttpsURLConnection) {
            ((HttpsURLConnection) connection).setSSLSocketFactory(pinnedContext().getSocketFactory());
        } else {
            throw new SecurityException("Station requires HTTPS.");
        }
        connection.setInstanceFollowRedirects(false);
        connection.setConnectTimeout(10000);
        connection.setReadTimeout(readTimeout);
        connection.setRequestMethod(method);
        if (bearer != null) connection.setRequestProperty("Authorization", "Bearer " + bearer);
        return connection;
    }

    private static byte[] readAtMost(InputStream stream, int maximum) throws Exception {
        if (stream == null) return new byte[0];
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        byte[] buffer = new byte[8192];
        int total = 0;
        int read;
        while ((read = stream.read(buffer)) >= 0) {
            total += read;
            if (total > maximum) throw new SecurityException("Response is too large.");
            output.write(buffer, 0, read);
        }
        return output.toByteArray();
    }

    private static byte[] readLimited(InputStream stream) throws Exception {
        if (stream == null) return new byte[0];
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        byte[] buffer = new byte[1024];
        int total = 0;
        int read;
        while ((read = stream.read(buffer)) >= 0) {
            total += read;
            if (total > StationProtocol.MAXIMUM_BODY_BYTES) throw new SecurityException("Response is too large.");
            output.write(buffer, 0, read);
        }
        return output.toByteArray();
    }

    private static boolean jsonObject(byte[] response) {
        if (response == null) return false;
        for (byte item : response) {
            if (item == ' ' || item == '\n' || item == '\r' || item == '\t') continue;
            return item == '{';
        }
        return false;
    }

    private static String text(String value, int maximum) {
        String clean = value == null ? "" : value.trim();
        if (clean.isEmpty()) clean = "unknown";
        if (clean.length() > maximum) clean = clean.substring(0, maximum);
        return clean;
    }

    private static byte[] hex(String value) {
        if (value == null || value.length() != 64) throw new SecurityException("TLS pin is invalid.");
        byte[] bytes = new byte[32];
        for (int i = 0; i < bytes.length; i++) {
            int high = Character.digit(value.charAt(i * 2), 16);
            int low = Character.digit(value.charAt(i * 2 + 1), 16);
            if (high < 0 || low < 0) throw new SecurityException("TLS pin is invalid.");
            bytes[i] = (byte) ((high << 4) + low);
        }
        return bytes;
    }
}
