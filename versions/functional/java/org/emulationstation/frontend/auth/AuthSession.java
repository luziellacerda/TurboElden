package org.emulationstation.frontend.auth;

/** Process-local session. Not persisted and never passed to the original remote services. */
public final class AuthSession {
    private static volatile boolean authorized;

    private AuthSession() {}

    public static boolean isAuthorized() {
        return authorized;
    }

    public static boolean authenticate(String password) {
        if (!LocalPassword.matches(password)) {
            return false;
        }
        authorized = true;
        return true;
    }
}
