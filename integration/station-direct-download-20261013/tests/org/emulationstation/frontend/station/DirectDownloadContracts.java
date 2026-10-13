package org.emulationstation.frontend.station;

import java.io.*;
import java.net.*;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.util.*;
import java.util.concurrent.*;
import javax.net.ssl.*;

/** Host contract tests; fixture connections are never part of the application DEX. */
public final class DirectDownloadContracts {
    private static final String GRANT = "/v1/station/artifacts/" + repeat('a', 42) + "A";
    private static final String SESSION = repeat('b', 42) + "A";
    private static final String PROOF = "v1.1791900000." + repeat('c', 22) + "." + repeat('d', 86);
    private static FakeConnection last;
    private static int opens, checks, replyStatus = 200;
    private static String replyLocation;

    private static String repeat(char ch, int count) {
        char[] value = new char[count]; Arrays.fill(value, ch); return new String(value);
    }
    private static void check(boolean condition, String label) {
        checks++; if (!condition) throw new AssertionError(label);
    }

    private static final class FakeConnection extends HttpsURLConnection {
        boolean disconnected;
        FakeConnection(URL target) { super(target); }
        @Override public void connect() {}
        @Override public boolean usingProxy() { return false; }
        @Override public void disconnect() { disconnected = true; }
        @Override public String getCipherSuite() { return "fixture"; }
        @Override public Certificate[] getLocalCertificates() { return null; }
        @Override public Certificate[] getServerCertificates() { return new Certificate[0]; }
        @Override public int getResponseCode() { return replyStatus; }
        @Override public String getContentType() { return "application/octet-stream"; }
        @Override public long getContentLengthLong() { return 3; }
        @Override public String getHeaderField(String name) { return "Location".equals(name) ? replyLocation : null; }
        @Override public InputStream getInputStream() { return new ByteArrayInputStream(new byte[]{1, 2, 3}); }
        @Override public OutputStream getOutputStream() { return new ByteArrayOutputStream(); }
    }

    private static FakeConnection exchange(StationHttp transport, String method, String path) throws Exception {
        try (StationApi.Response response = transport.exchange(method, path, null, SESSION, PROOF,
                                                               new StationApi.Cancellation())) {
            while (response.body.read() != -1) {}
        }
        return last;
    }

    private static void routesAndHeaders() throws Exception {
        URL.setURLStreamHandlerFactory(protocol -> "https".equals(protocol) ? new URLStreamHandler() {
            @Override protected URLConnection openConnection(URL target) {
                opens++; last = new FakeConnection(target); return last;
            }
        } : null);
        StationHttp transport = new StationHttp();
        check(transport.supportsRequestProof(), "proof support preserved");
        FakeConnection artifact = exchange(transport, "GET", GRANT);
        check(artifact.getURL().getHost().equals("downloads-station.lzgames.com.br"), "artifact uses direct origin");
        check(artifact.getURL().getPath().equals(GRANT), "artifact proof target preserved");
        check(artifact.getRequestProperty("Authorization").equals("Bearer " + SESSION), "session forwarded");
        check(artifact.getRequestProperty("X-Station-Request-Proof").equals(PROOF), "proof forwarded");
        check(artifact.getRequestProperty("X-Correlation-ID").matches("[0-9a-f]{32}"), "correlation generated");
        check(artifact.getRequestProperty("Accept-Encoding").equals("identity"), "uncompressed stream preserved");
        check(!artifact.getInstanceFollowRedirects(), "automatic redirect disabled");
        check(!artifact.disconnected, "complete body retains pooling");
        for (String route : Arrays.asList("/v1/station/me", "/v1/station/catalog",
                "/v1/station/catalog?metadata=1", "/v1/station/covers/fixture-game",
                "/v1/station/media/catalog?requestId=" + repeat('a', 32),
                "/v1/station/media/files/" + repeat('a', 64))) {
            FakeConnection api = exchange(transport, "GET", route);
            check(api.getURL().getHost().equals("app.lzgames.com.br"), "non-artifact origin preserved");
            check(api.getSSLSocketFactory() != artifact.getSSLSocketFactory(), "distinct TLS identities");
        }
        for (String route : Arrays.asList("/v1/station/sessions", "/v1/station/downloads/authorize",
                                          "/v1/station/online/multiplayer/command")) {
            check(exchange(transport, "POST", route).getURL().getHost().equals("app.lzgames.com.br"),
                  "authorization and commands retain tunnel origin");
        }
        for (String path : Arrays.asList(GRANT + "?x=1", GRANT + "/child", GRANT.substring(0, GRANT.length()-1),
                "https://example.com/", "//example.com/", "/v1/station/artifacts/../catalog")) {
            int before = opens;
            try {
                exchange(transport, "GET", path); throw new AssertionError("unsupported path accepted");
            } catch (IOException expected) { check(opens == before, "unsupported path never connects"); }
        }
        for (String method : Arrays.asList("POST", "HEAD", "PUT")) {
            int before = opens;
            try {
                exchange(transport, method, GRANT); throw new AssertionError("unsupported artifact method accepted");
            } catch (IOException expected) { check(opens == before, "unsupported method never connects"); }
        }
        for (int status : new int[]{301, 302, 307, 308}) {
            replyStatus = status;
            try {
                exchange(transport, "GET", GRANT); throw new AssertionError("redirect accepted");
            } catch (IOException expected) { check(last.disconnected, "redirect rejected and connection closed"); }
        }
        replyStatus = 200; replyLocation = "https://example.com/";
        try {
            exchange(transport, "GET", GRANT); throw new AssertionError("Location header accepted");
        } catch (IOException expected) { check(last.disconnected, "unexpected Location refused"); }
        replyLocation = null;
        StationApi.Cancellation cancelled = new StationApi.Cancellation(); cancelled.cancel();
        int before = opens;
        try {
            transport.exchange("GET", GRANT, null, SESSION, PROOF, cancelled);
            throw new AssertionError("cancelled request connected");
        } catch (InterruptedIOException expected) { check(opens == before, "cancel before grant consumption"); }
        StationApi.Cancellation inFlight = new StationApi.Cancellation();
        try (StationApi.Response response = transport.exchange("GET", GRANT, null, SESSION, PROOF, inFlight)) {
            inFlight.cancel(); check(last.disconnected, "in-flight cancellation closes direct stream");
        }
    }

    private static void tlsIdentity(String keyFile) throws Exception {
        KeyStore keys = KeyStore.getInstance("PKCS12");
        try (InputStream stream = new FileInputStream(keyFile)) { keys.load(stream, new char[0]); }
        KeyManagerFactory keyManagers = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        keyManagers.init(keys, new char[0]);
        SSLContext context = SSLContext.getInstance("TLS");
        context.init(keyManagers.getKeyManagers(), null, null);
        java.lang.reflect.Method factory = StationHttp.class.getDeclaredMethod("pinnedSockets", String.class);
        factory.setAccessible(true);
        for (int scenario = 0; scenario < 3; scenario++) {
            final int current = scenario;
            try (SSLServerSocket server = (SSLServerSocket) context.getServerSocketFactory().createServerSocket(0)) {
                ExecutorService executor = Executors.newSingleThreadExecutor();
                Future<?> accepting = executor.submit(() -> {
                    try (SSLSocket socket = (SSLSocket) server.accept()) {
                        socket.setSoTimeout(5000); socket.startHandshake();
                    } catch (IOException expectedRejection) { /* wrong pin/hostname closes TLS */ }
                });
                String pin = current == 1 ? StationConfig.TLS_SPKI_SHA256 : StationDownloadOrigin.TLS_SPKI_SHA256;
                String host = current == 2 ? "wrong.lzgames.com.br" : "downloads-station.lzgames.com.br";
                SSLSocketFactory sockets = (SSLSocketFactory) factory.invoke(null, pin);
                try (Socket raw = new Socket("127.0.0.1", server.getLocalPort());
                     SSLSocket socket = (SSLSocket) sockets.createSocket(raw, host, server.getLocalPort(), true)) {
                    socket.setSoTimeout(5000);
                    SSLParameters parameters = socket.getSSLParameters();
                    parameters.setEndpointIdentificationAlgorithm("HTTPS"); socket.setSSLParameters(parameters);
                    try {
                        socket.startHandshake(); check(current == 0, "TLS rejects foreign pin and hostname");
                    } catch (SSLHandshakeException rejected) {
                        check(current != 0, "trusted chain, hostname and direct pin accepted");
                    }
                } finally {
                    accepting.get(6, TimeUnit.SECONDS); executor.shutdownNow();
                }
            }
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("Private TLS fixture path required");
        routesAndHeaders(); tlsIdentity(args[0]);
        System.out.println("direct-download-contract-checks=" + checks + " tls-scenarios=3");
    }
}
