package org.emulationstation.frontend.station;

import java.io.*;
import java.net.*;
import java.security.*;
import java.security.cert.*;
import javax.net.ssl.*;

/** The only HTTP transport of the reconstructed Station service. */
public final class StationHttp implements StationApi.Transport {
    private final SSLSocketFactory sockets;
    private final URL origin;

    public StationHttp() throws Exception {
        origin = new URL(StationConfig.BASE_URL);
        if (!origin.getProtocol().equals("https") || origin.getUserInfo() != null
                || origin.getQuery() != null || origin.getRef() != null
                || !origin.getPath().isEmpty()) throw new SecurityException("Invalid Station origin");
        TrustManagerFactory factory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        factory.init((KeyStore)null);
        X509TrustManager system = null;
        for (TrustManager manager : factory.getTrustManagers())
            if (manager instanceof X509TrustManager) system = (X509TrustManager)manager;
        if (system == null) throw new GeneralSecurityException("System trust unavailable");
        final X509TrustManager trust = system;
        final byte[] pin = decodeHex(StationConfig.TLS_SPKI_SHA256);
        X509TrustManager pinned = new X509TrustManager() {
            public X509Certificate[] getAcceptedIssuers() { return trust.getAcceptedIssuers(); }
            public void checkClientTrusted(X509Certificate[] chain, String type) throws CertificateException {
                trust.checkClientTrusted(chain, type);
            }
            public void checkServerTrusted(X509Certificate[] chain, String type) throws CertificateException {
                trust.checkServerTrusted(chain, type);
                if (chain == null || chain.length == 0) throw new CertificateException("Missing certificate");
                try {
                    byte[] actual = MessageDigest.getInstance("SHA-256").digest(chain[0].getPublicKey().getEncoded());
                    if (!MessageDigest.isEqual(pin, actual)) throw new CertificateException("Station pin mismatch");
                } catch (GeneralSecurityException e) { throw new CertificateException("Station TLS rejected", e); }
            }
        };
        SSLContext tls = SSLContext.getInstance("TLS");
        tls.init(null, new TrustManager[]{pinned}, null);
        sockets = tls.getSocketFactory();
    }

    @Override public StationApi.Response exchange(String method, String path, byte[] body,
            String token, StationApi.Cancellation cancellation) throws IOException {
        if (!allowed(method, path) || body != null && body.length > StationProtocol.MAXIMUM_BODY_BYTES)
            throw new IOException("Unsupported Station request");
        if (token != null && !StationProtocol.activationCode(token)) throw new IOException("Invalid session token");
        cancellation.check();
        final HttpsURLConnection connection = (HttpsURLConnection)new URL(origin, path).openConnection();
        boolean handedOff = false;
        Runnable abort = connection::disconnect;
        cancellation.attach(abort);
        try {
            connection.setSSLSocketFactory(sockets);
            // The platform's hostname verifier and certificate validation remain enabled.
            connection.setInstanceFollowRedirects(false);
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(30000);
            connection.setUseCaches(false);
            connection.setRequestMethod(method);
            connection.setRequestProperty("Accept-Encoding", "identity");
            if (token != null) connection.setRequestProperty("Authorization", "Bearer " + token);
            if (body != null) {
                connection.setDoOutput(true);
                connection.setFixedLengthStreamingMode(body.length);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                try (OutputStream out = connection.getOutputStream()) { out.write(body); }
            }
            cancellation.check();
            int status = connection.getResponseCode();
            if (status / 100 == 3 || connection.getHeaderField("Location") != null)
                throw new IOException("Station redirect refused");
            String encoding = connection.getHeaderField("Content-Encoding");
            if (encoding != null && !encoding.equalsIgnoreCase("identity"))
                throw new IOException("Unexpected Station content encoding");
            InputStream stream = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
            if (stream == null) stream = new ByteArrayInputStream(new byte[0]);
            final InputStream owned = stream;
            StationApi.Response response = new StationApi.Response(status, connection.getContentType(),
                connection.getContentLengthLong(), owned, () -> {
                    try { owned.close(); } finally { cancellation.detach(abort); connection.disconnect(); }
                });
            handedOff = true;
            return response;
        } finally {
            if (!handedOff) { cancellation.detach(abort); connection.disconnect(); }
        }
    }

    static boolean allowed(String method, String path) {
        if ("POST".equals(method)) return path.equals("/v1/station/activations/challenge")
            || path.equals("/v1/station/activations/complete") || path.equals("/v1/station/challenges")
            || path.equals("/v1/station/sessions") || path.equals("/v1/station/downloads/authorize");
        if (!"GET".equals(method)) return false;
        if (path.equals("/v1/station/me") || path.equals("/v1/station/catalog")) return true;
        String covers = "/v1/station/covers/", artifacts = "/v1/station/artifacts/";
        return path.startsWith(covers) && StationProtocol.libraryId(path.substring(covers.length()))
            || path.startsWith(artifacts) && StationProtocol.activationCode(path.substring(artifacts.length()));
    }

    private static byte[] decodeHex(String value) throws GeneralSecurityException {
        if (value == null || !value.matches("[0-9a-f]{64}")) throw new GeneralSecurityException("Invalid TLS pin");
        byte[] bytes = new byte[32];
        for (int i = 0; i < bytes.length; i++) bytes[i] = (byte)Integer.parseInt(value.substring(i*2, i*2+2), 16);
        return bytes;
    }
}
