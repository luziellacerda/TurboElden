package org.emulationstation.frontend.auth;

final class StationLoginBridge implements StationAuth.Callback {
    private final LoginActivity activity;

    StationLoginBridge(LoginActivity activity) {
        this.activity = activity;
    }

    @Override public void ok(final String displayName) {
        activity.runOnUiThread(new Runnable() {
            @Override public void run() { activity.commercialOk(displayName); }
        });
    }

    @Override public void fail(final String message) {
        activity.runOnUiThread(new Runnable() {
            @Override public void run() { activity.commercialFail(message); }
        });
    }
}
