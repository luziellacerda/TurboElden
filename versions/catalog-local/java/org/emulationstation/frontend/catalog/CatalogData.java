package org.emulationstation.frontend.catalog;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/** Immutable, locally bundled snapshot; no connections, credentials or external file writes. */
public final class CatalogData {
    public static final String ASSET = "turboretro/catalog.json";
    public static final String SHA256 = "4c09c066c592acd5481067ff2b9df0409f01016bf93cd517e298655a899f7792";
    public static final int MAX_BYTES = 16 * 1024 * 1024;

    private CatalogData() {}

    public static boolean matches(String url, String destination) {
        // Only in-memory catalogue GETs, never downloads or other HTTP requests.
        if (url == null || destination != null) return false;
        try {
            URI uri = new URI(url);
            String scheme = uri.getScheme();
            if (!("https".equalsIgnoreCase(scheme) || "http".equalsIgnoreCase(scheme))) return false;
            if (!"samboxmanager.squareweb.app".equalsIgnoreCase(uri.getHost())) return false;
            if (uri.getRawUserInfo() != null || uri.getRawQuery() != null || uri.getRawFragment() != null) return false;
            int port = uri.getPort();
            if (port != -1 && !(port == 443 && "https".equalsIgnoreCase(scheme))
                    && !(port == 80 && "http".equalsIgnoreCase(scheme))) return false;
            String path = uri.getRawPath();
            if ("/drawers.json".equals(path)) return true;
            String prefix = "/drawers.json/";
            String suffix = "/android";
            if (path == null || path.length() <= prefix.length() + suffix.length()
                    || !path.startsWith(prefix) || !path.endsWith(suffix)) return false;
            String segment = path.substring(prefix.length(), path.length() - suffix.length());
            return !segment.isEmpty() && segment.indexOf('/') < 0;
        } catch (URISyntaxException | IllegalArgumentException ex) {
            return false;
        }
    }

    public static byte[] readVerified(InputStream input) throws IOException {
        if (input == null) throw new IOException("Catalogo local indisponivel.");
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            ByteArrayOutputStream output = new ByteArrayOutputStream(8 * 1024 * 1024);
            byte[] buffer = new byte[32768];
            int count;
            while ((count = input.read(buffer)) != -1) {
                if (count == 0) continue;
                if (output.size() > MAX_BYTES - count) throw new IOException("Catalogo local excede o limite.");
                digest.update(buffer, 0, count);
                output.write(buffer, 0, count);
            }
            byte[] expected = new byte[32];
            for (int i = 0; i < expected.length; i++) {
                expected[i] = (byte) Integer.parseInt(SHA256.substring(i * 2, i * 2 + 2), 16);
            }
            if (!MessageDigest.isEqual(expected, digest.digest())) throw new IOException("Catalogo local corrompido.");
            return output.toByteArray();
        } catch (NoSuchAlgorithmException ex) {
            throw new IOException("SHA-256 indisponivel.", ex);
        }
    }
}
