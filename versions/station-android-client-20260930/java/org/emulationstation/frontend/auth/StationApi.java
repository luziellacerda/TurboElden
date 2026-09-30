package org.emulationstation.frontend.auth;

import android.util.Base64;
import android.os.Build;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import org.json.JSONObject;

/** Version 1 wire client. The exact envelope and fields are part of the server handoff. */
final class StationApi {
    static final String CHALLENGE = "TurboRamaStationAndroid/activation-challenge/v1";
    static final String ACTIVATE = "TurboRamaStationAndroid/activate/v1";
    static final String ACTIVATED = "TurboRamaStationAndroid/activated/v1";
    static final String SESSION_CHALLENGE = "TurboRamaStationAndroid/session-challenge/v1";
    static final String OPEN_SESSION = "TurboRamaStationAndroid/open-session/v1";
    static final String SESSION = "TurboRamaStationAndroid/session/v1";
    static final String PROFILE = "TurboRamaStationAndroid/profile/v1";
    static final String CATALOG = "TurboRamaStationAndroid/catalog/v1";
    static final String DOWNLOAD = "TurboRamaStationAndroid/download/v1";

    private StationApi() {}

    private static JSONObject identity(String domain, String deviceId) throws Exception {
        JSONObject value = new JSONObject();
        value.put("schemaVersion", 1);
        value.put("domain", domain);
        value.put("productId", StationConfig.PRODUCT);
        value.put("applicationId", StationConfig.APPLICATION);
        value.put("deviceId", deviceId);
        value.put("clientVersion", StationConfig.CLIENT_VERSION);
        value.put("deviceManufacturer", Build.MANUFACTURER);
        value.put("deviceModel", Build.MODEL);
        value.put("androidSdk", Build.VERSION.SDK_INT);
        return value;
    }

    static JSONObject activationChallenge(String code, KeyPair device) throws Exception {
        String id = StationCrypto.deviceId(device.getPublic());
        JSONObject request = identity("TurboRamaStationAndroid/request-activation-challenge/v1", id);
        request.put("activationCode", code);
        request.put("devicePublicKey", StationCrypto.b64(device.getPublic().getEncoded()));
        JSONObject answer = verified("/v1/station/activations/challenge", request, null, CHALLENGE);
        checkIdentity(answer, id);
        if (answer.optString("challengeId").isEmpty() ||
                StationCrypto.unb64(answer.optString("nonce")).length != 32)
            throw new SecurityException("Desafio inválido");
        return answer;
    }

    static JSONObject activate(String code, KeyPair device, JSONObject challenge) throws Exception {
        String id = StationCrypto.deviceId(device.getPublic());
        JSONObject proof = identity(ACTIVATE, id);
        proof.put("activationCode", code);
        proof.put("devicePublicKey", StationCrypto.b64(device.getPublic().getEncoded()));
        proof.put("challengeId", challenge.getString("challengeId"));
        proof.put("nonce", challenge.getString("nonce"));
        JSONObject answer = verified("/v1/station/activations/complete",
                signedRequest(proof, device), null, ACTIVATED);
        checkIdentity(answer, id);
        if (answer.optString("licenseId").isEmpty() ||
                !challenge.getString("challengeId").equals(answer.optString("challengeId")) ||
                !challenge.getString("nonce").equals(answer.optString("nonce")))
            throw new SecurityException("Ativação inválida");
        return answer;
    }

    static JSONObject openSession(String licenseId, KeyPair device) throws Exception {
        String id = StationCrypto.deviceId(device.getPublic());
        JSONObject ask = identity("TurboRamaStationAndroid/request-session-challenge/v1", id);
        ask.put("licenseId", licenseId);
        JSONObject challenge = verified("/v1/station/challenges", ask, null, SESSION_CHALLENGE);
        checkIdentity(challenge, id);
        if (!licenseId.equals(challenge.optString("licenseId")) ||
                challenge.optString("challengeId").isEmpty() ||
                StationCrypto.unb64(challenge.optString("nonce")).length != 32)
            throw new SecurityException("Desafio de sessão inválido");
        JSONObject proof = identity(OPEN_SESSION, id);
        proof.put("licenseId", licenseId);
        proof.put("challengeId", challenge.getString("challengeId"));
        proof.put("nonce", challenge.getString("nonce"));
        JSONObject session = verified("/v1/station/sessions", signedRequest(proof, device),
                null, SESSION);
        checkIdentity(session, id);
        if (!licenseId.equals(session.optString("licenseId")) ||
                !challenge.getString("challengeId").equals(session.optString("challengeId")) ||
                !challenge.getString("nonce").equals(session.optString("nonce")) ||
                session.optString("sessionId").isEmpty() ||
                session.optString("accessToken").isEmpty() ||
                session.optInt("expiresInSeconds", 0) < 30 ||
                session.optInt("expiresInSeconds", 0) > 3600)
            throw new SecurityException("Sessão inválida");
        return session;
    }

    static JSONObject profile(String token, String licenseId, String deviceId, String sessionId) throws Exception {
        JSONObject profile = verified("/v1/station/me", null, token, PROFILE);
        checkIdentity(profile, deviceId);
        if (!licenseId.equals(profile.optString("licenseId")) ||
                !sessionId.equals(profile.optString("sessionId")))
            throw new SecurityException("Perfil de outra licença");
        return profile;
    }

    static JSONObject catalog(String token, String platform, String cursor,
                              String deviceId, String sessionId) throws Exception {
        String query = "?platform=" + java.net.URLEncoder.encode(platform, "UTF-8")
                + "&cursor=" + java.net.URLEncoder.encode(cursor, "UTF-8");
        JSONObject result = verified("/v1/station/catalog" + query, null, token, CATALOG);
        checkIdentity(result, deviceId);
        if (!sessionId.equals(result.optString("sessionId")))
            throw new SecurityException("Catálogo de outra sessão");
        if (!platform.equals(result.optString("platform")))
            throw new SecurityException("Catálogo de outra plataforma");
        return result;
    }

    static JSONObject authorizeDownload(String token, String itemId,
                                        String deviceId, String sessionId) throws Exception {
        JSONObject request = identity("TurboRamaStationAndroid/request-download/v1", deviceId);
        request.put("itemId", itemId);
        JSONObject result = verified("/v1/station/downloads/authorize", request, token, DOWNLOAD);
        checkIdentity(result, deviceId);
        if (!sessionId.equals(result.optString("sessionId")))
            throw new SecurityException("Download de outra sessão");
        if (!itemId.equals(result.optString("itemId")))
            throw new SecurityException("Autorização de outro jogo");
        return result;
    }

    private static JSONObject signedRequest(JSONObject payload, KeyPair key) throws Exception {
        byte[] bytes = StationCrypto.utf8(payload.toString());
        JSONObject envelope = new JSONObject();
        envelope.put("payload", StationCrypto.b64(bytes));
        envelope.put("signature", StationCrypto.sign(key.getPrivate(), bytes));
        return envelope;
    }

    private static void checkIdentity(JSONObject answer, String deviceId) {
        if (answer.optInt("schemaVersion") != 1 ||
                !StationConfig.PRODUCT.equals(answer.optString("productId")) ||
                !StationConfig.APPLICATION.equals(answer.optString("applicationId")) ||
                !deviceId.equals(answer.optString("deviceId")))
            throw new SecurityException("Identidade do produto ou aparelho inválida");
    }

    private static JSONObject verified(String path, JSONObject body, String token, String domain)
            throws Exception {
        JSONObject envelope = request(path, body, token);
        if (!StationConfig.SERVER_KEY_ID.equals(envelope.optString("keyId")))
            throw new SecurityException("Chave do servidor desconhecida");
        byte[] bytes = StationCrypto.unb64(envelope.getString("payload"));
        if (bytes.length > 2_000_000) throw new SecurityException("Resposta excessiva");
        StationCrypto.verifyServer(bytes, envelope.getString("signature"), envelope.getString("keyId"));
        JSONObject payload = new JSONObject(new String(bytes, StandardCharsets.UTF_8));
        if (!domain.equals(payload.optString("domain")))
            throw new SecurityException("Tipo de resposta inválido");
        return payload;
    }

    private static JSONObject request(String path, JSONObject body, String token) throws Exception {
        if (!StationConfig.ready()) throw new IllegalStateException("Servidor ainda não configurado");
        URL base = new URL(StationConfig.BASE_URL);
        if (!"https".equals(base.getProtocol()) || base.getUserInfo() != null ||
                base.getQuery() != null || base.getRef() != null || !"".equals(base.getPath()))
            throw new SecurityException("URL do servidor inválida");
        URL url = new URL(base, path);
        if (!base.getHost().equals(url.getHost()) || base.getPort() != url.getPort())
            throw new SecurityException("Destino externo bloqueado");
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setInstanceFollowRedirects(false);
        connection.setConnectTimeout(8000);
        connection.setReadTimeout(10000);
        connection.setRequestProperty("Accept", "application/json");
        if (token != null) connection.setRequestProperty("Authorization", "Bearer " + token);
        try {
            if (body != null) {
                connection.setRequestMethod("POST");
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                byte[] data = StationCrypto.utf8(body.toString());
                if (data.length > 8192) throw new SecurityException("Pedido excessivo");
                try (OutputStream output = connection.getOutputStream()) { output.write(data); }
            }
            int status = connection.getResponseCode();
            if (status != 200) throw new StationFailure(status);
            try (InputStream input = connection.getInputStream()) {
                ByteArrayOutputStream output = new ByteArrayOutputStream();
                byte[] chunk = new byte[4096];
                for (int n; (n = input.read(chunk)) != -1;) {
                    output.write(chunk, 0, n);
                    if (output.size() > 3_000_000) throw new SecurityException("Resposta excessiva");
                }
                return new JSONObject(output.toString("UTF-8"));
            }
        } finally { connection.disconnect(); }
    }

    static final class StationFailure extends Exception {
        final int status;
        StationFailure(int status) { super("HTTP " + status); this.status = status; }
    }
}
