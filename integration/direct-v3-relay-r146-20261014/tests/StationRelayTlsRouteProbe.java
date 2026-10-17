package org.emulationstation.frontend.netplay;

import java.io.IOException;
import java.lang.reflect.Field;
import java.math.BigInteger;
import java.net.*;
import java.security.*;
import java.security.cert.*;
import java.util.*;
import javax.net.ssl.*;

/** Runs the actual proposed TLS source with inert JSSE boundaries; no network. */
public final class StationRelayTlsRouteProbe {
    private static int checks;
    private static final ProbeTrust SYSTEM = new ProbeTrust();
    private static X509TrustManager captured;
    private static void require(boolean value, String label) {
        if (!value) throw new AssertionError(label);
        checks++;
    }
    private static byte[] pin(String hex) { return HexFormat.of().parseHex(hex); }
    private static byte[] capturedPin()throws Exception {
        for (Field field : captured.getClass().getDeclaredFields()) {
            if (field.getType() == byte[].class) {
                field.setAccessible(true);
                return ((byte[]) field.get(captured)).clone();
            }
        }
        throw new AssertionError("Actual pin closure missing");
    }
    private static void rejected(Checked action, String label)throws Exception {
        try { action.run(); throw new AssertionError(label + " accepted"); }
        catch (CertificateException expected) { checks++; }
    }
    private interface Checked { void run()throws Exception; }

    public static final class ProbeProvider extends Provider {
        public ProbeProvider() {
            super("StationRouteProbe", "1", "Inert JSSE test boundaries");
            put("TrustManagerFactory.StationProbe", ProbeTrustFactory.class.getName());
            put("SSLContext.TLS", CaptureContext.class.getName());
        }
    }
    public static final class ProbeTrustFactory extends TrustManagerFactorySpi {
        protected void engineInit(KeyStore value) {}
        protected void engineInit(ManagerFactoryParameters value) {}
        protected TrustManager[] engineGetTrustManagers() { return new TrustManager[]{SYSTEM}; }
    }
    public static final class CaptureContext extends SSLContextSpi {
        protected void engineInit(KeyManager[] keys, TrustManager[] trust, SecureRandom random) {
            require(keys == null && trust.length == 1 && trust[0] instanceof X509TrustManager,
                    "Actual TLS context receives one pinned system manager");
            captured = (X509TrustManager) trust[0];
        }
        protected SSLSocketFactory engineGetSocketFactory() { return new NoNetworkFactory(); }
        protected SSLServerSocketFactory engineGetServerSocketFactory() { throw new UnsupportedOperationException(); }
        protected SSLEngine engineCreateSSLEngine() { throw new UnsupportedOperationException(); }
        protected SSLEngine engineCreateSSLEngine(String host, int port) { throw new UnsupportedOperationException(); }
        protected SSLSessionContext engineGetServerSessionContext() { return null; }
        protected SSLSessionContext engineGetClientSessionContext() { return null; }
    }
    private static final class NoNetworkFactory extends SSLSocketFactory {
        public String[] getDefaultCipherSuites() { return new String[0]; }
        public String[] getSupportedCipherSuites() { return new String[0]; }
        private Socket reject()throws IOException { throw new IOException("Host probe forbids socket creation"); }
        public Socket createSocket(Socket s, String host, int port, boolean close)throws IOException { return reject(); }
        public Socket createSocket(String host, int port)throws IOException { return reject(); }
        public Socket createSocket(String host, int port, InetAddress local, int localPort)throws IOException { return reject(); }
        public Socket createSocket(InetAddress host, int port)throws IOException { return reject(); }
        public Socket createSocket(InetAddress host, int port, InetAddress local, int localPort)throws IOException { return reject(); }
    }
    private static final class ProbeTrust implements X509TrustManager {
        int checks; boolean reject;
        public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0]; }
        public void checkClientTrusted(X509Certificate[] chain, String type)throws CertificateException {
            checkServerTrusted(chain, type);
        }
        public void checkServerTrusted(X509Certificate[] chain, String type)throws CertificateException {
            checks++;
            if (reject) throw new CertificateException("Untrusted fixture CA");
        }
    }
    private static final class FixtureKey implements PublicKey {
        private final byte[] bytes;
        FixtureKey(byte[] bytes) { this.bytes = bytes.clone(); }
        public String getAlgorithm() { return "fixture"; }
        public String getFormat() { return "X.509"; }
        public byte[] getEncoded() { return bytes.clone(); }
    }
    private static final class FixtureCertificate extends X509Certificate {
        private final PublicKey key;
        FixtureCertificate(byte[] bytes) { key = new FixtureKey(bytes); }
        public PublicKey getPublicKey() { return key; }
        public void checkValidity() {}
        public void checkValidity(Date date) {}
        public int getVersion() { return 3; }
        public BigInteger getSerialNumber() { return BigInteger.ONE; }
        public Principal getIssuerDN() { return () -> "fixture"; }
        public Principal getSubjectDN() { return () -> "fixture"; }
        public Date getNotBefore() { return new Date(0); }
        public Date getNotAfter() { return new Date(Long.MAX_VALUE); }
        public byte[] getTBSCertificate() { return new byte[0]; }
        public byte[] getSignature() { return new byte[0]; }
        public String getSigAlgName() { return "fixture"; }
        public String getSigAlgOID() { return "0.0"; }
        public byte[] getSigAlgParams() { return new byte[0]; }
        public boolean[] getIssuerUniqueID() { return null; }
        public boolean[] getSubjectUniqueID() { return null; }
        public boolean[] getKeyUsage() { return null; }
        public int getBasicConstraints() { return -1; }
        public byte[] getEncoded() { return new byte[0]; }
        public void verify(PublicKey key) {}
        public void verify(PublicKey key, String provider) {}
        public String toString() { return "inert certificate fixture"; }
        public boolean hasUnsupportedCriticalExtension() { return false; }
        public Set<String> getCriticalExtensionOIDs() { return null; }
        public Set<String> getNonCriticalExtensionOIDs() { return null; }
        public byte[] getExtensionValue(String oid) { return null; }
    }

    public static void main(String[] args)throws Exception {
        String oldAlgorithm = Security.getProperty("ssl.TrustManagerFactory.algorithm");
        Security.insertProviderAt(new ProbeProvider(), 1);
        Security.setProperty("ssl.TrustManagerFactory.algorithm", "StationProbe");
        try {
            URI legacy = StationRelayTls.endpoint(), direct = StationRelayTls.multiplayerEndpoint();
            require(legacy.toString().equals("wss://app.lzgames.com.br/v1/station/online/relay"), "Legacy v1 authority/path unchanged");
            require(direct.toString().equals("wss://downloads-station.lzgames.com.br/v1/station/online/multiplayer/relay"), "Direct v3 reviewed URI");
            require(direct.getRawUserInfo() == null && direct.getRawQuery() == null && direct.getRawFragment() == null,
                    "Direct URI has no credentials/query/fragment");
            require(direct.getScheme().equals("wss") && direct.getPort() == -1, "Direct URI uses default TLS port");
            StationRelayTls.create();
            require(Arrays.equals(capturedPin(), pin("13f9dcbb7a9687c2f88ff73de5621cfab849d0ec02191dcdd1ee8a6275dacba7")),
                    "Legacy factory keeps API SPKI");
            StationRelayTls.createMultiplayer();
            require(Arrays.equals(capturedPin(), pin("bcd134d59fcdbb35e0343c86d31a666cc95cf158d70b27aceceefd19158d072f")),
                    "Dedicated direct factory uses direct SPKI");
            require(!Arrays.equals(capturedPin(), pin("13f9dcbb7a9687c2f88ff73de5621cfab849d0ec02191dcdd1ee8a6275dacba7")),
                    "Direct factory cannot accidentally use API pin");
            X509TrustManager directManager = captured;
            byte[] fixtureSpki = "station-route-fixture-SPKI".getBytes(java.nio.charset.StandardCharsets.US_ASCII);
            X509Certificate[] chain = {new FixtureCertificate(fixtureSpki)};
            int before = SYSTEM.checks;
            rejected(() -> directManager.checkServerTrusted(chain, "RSA"), "Direct real pin rejects unrelated fixture SPKI");
            require(SYSTEM.checks == before + 1, "Dedicated factory always invokes system CA trust");
            byte[] fixturePin = MessageDigest.getInstance("SHA-256").digest(fixtureSpki);
            StationRelayTls.pinned(SYSTEM, fixturePin);
            captured.checkServerTrusted(chain, "RSA"); checks++;
            X509TrustManager validPinnedManager = captured;
            SYSTEM.reject = true;
            rejected(() -> validPinnedManager.checkServerTrusted(chain, "RSA"), "Correct SPKI cannot bypass rejected system CA");
            SYSTEM.reject = false;
            rejected(() -> validPinnedManager.checkServerTrusted(new X509Certificate[0], "RSA"), "Empty chain rejected");
            rejected(() -> validPinnedManager.checkServerTrusted(null, "RSA"), "Null chain rejected");
            StationRelayTls.pinned(SYSTEM, new byte[32]);
            X509TrustManager wrongPinManager = captured;
            rejected(() -> wrongPinManager.checkServerTrusted(chain, "RSA"), "Valid system trust cannot bypass wrong SPKI");
            StationRelayTls.create();
            require(Arrays.equals(capturedPin(), pin("13f9dcbb7a9687c2f88ff73de5621cfab849d0ec02191dcdd1ee8a6275dacba7")),
                    "Selecting direct factory never changes subsequent legacy factory");
            System.out.println("{\"schema\":\"station.r146.direct-v3.tls-host-probe.v1\",\"passed\":true,\"checks\":" + checks +
                    ",\"networkAccessed\":false,\"physicalGameplayValidated\":false}");
        } finally {
            SYSTEM.reject = false;
            Security.setProperty("ssl.TrustManagerFactory.algorithm", oldAlgorithm);
            Security.removeProvider("StationRouteProbe");
        }
    }
}
