package org.emulationstation.frontend.auth;

final class StationNameBridge implements StationAuth.Callback {
    private final LoginActivity activity;

    StationNameBridge(LoginActivity activity) {
        this.activity = activity;
    }

    @Override public void ok(final String displayName) {
        activity.runOnUiThread(new Runnable() {
            @Override public void run() { activity.welcomeName(displayName); }
        });
    }

    @Override public void fail(String message) {}
}
