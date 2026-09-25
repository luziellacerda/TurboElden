package org.emulationstation.frontend.auth;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/** Provisional local access only; not a server credential or DRM security boundary. */
final class LocalPassword {
    // SHA-256 of the temporary password. Anyone with the APK can replace this check.
    private static final String EXPECTED =
            "afa5166ad6cc24f0ac8350343cde24b43bdc41f90526d2acfb2f400e790b2cc4";

    private LocalPassword() {}

    static boolean matches(String password) {
        if (password == null || password.length() == 0 || password.length() > 128) {
            return false;
        }
        try {
            byte[] actual = MessageDigest.getInstance("SHA-256")
                    .digest(password.getBytes(StandardCharsets.UTF_8));
            byte[] expected = new byte[EXPECTED.length() / 2];
            for (int i = 0; i < expected.length; i++) {
                expected[i] = (byte) Integer.parseInt(EXPECTED.substring(i * 2, i * 2 + 2), 16);
            }
            return MessageDigest.isEqual(expected, actual);
        } catch (NoSuchAlgorithmException unavailable) {
            return false; // Fail closed; never treat a validation failure as successful login.
        }
    }
}
