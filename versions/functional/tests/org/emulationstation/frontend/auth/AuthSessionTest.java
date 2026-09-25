package org.emulationstation.frontend.auth;

public final class AuthSessionTest {
    private static int checks;

    private static void check(boolean condition, String description) {
        if (!condition) throw new AssertionError(description);
        checks++;
    }

    public static void main(String[] args) {
        check(!AuthSession.isAuthorized(), "A new process must start unauthorized");
        for (String wrong : new String[] {null, "", "123", "TURBO123", " turbo123", "turbo123 ",
                "turbo123\n", "turbo123\u0000", "\u0442urbo123", new String(new char[129])}) {
            check(!LocalPassword.matches(wrong), "Invalid password must be rejected");
            check(!AuthSession.authenticate(wrong), "Invalid login must fail");
            check(!AuthSession.isAuthorized(), "Invalid login must not authorize");
        }
        check(LocalPassword.matches("turbo123"), "Exact temporary password must match");
        check(AuthSession.authenticate("turbo123"), "Valid login must succeed");
        check(AuthSession.isAuthorized(), "Session must be available to the SDL gate");
        check(!AuthSession.authenticate("wrong"), "Invalid retry must still fail");
        check(AuthSession.isAuthorized(), "An invalid retry must not break an active session");
        System.out.println("PASS: " + checks + " local authentication checks (no network).");
    }
}
