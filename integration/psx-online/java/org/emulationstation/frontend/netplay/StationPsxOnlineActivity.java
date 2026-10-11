// SPDX-License-Identifier: GPL-2.0-or-later
package org.emulationstation.frontend.netplay;

import android.os.Bundle;
import android.os.Looper;
import android.os.Process;
import java.util.concurrent.atomic.AtomicBoolean;
import android.view.KeyEvent;
import android.view.WindowManager;
import org.libsdl.app.SDLActivity;

/** Private SDL owner for the exact normal PSX renderer/core. No frontend preload. */
public final class StationPsxOnlineActivity extends SDLActivity {
    public static final String EXTRA_LAUNCH = "station.launch";
    private String privateLaunchName;
    private volatile Thread capturedOwner;
    private final AtomicBoolean joiningOwner = new AtomicBoolean();
    private boolean retiring;

    @Override protected void onCreate(Bundle savedState) {
        privateLaunchName = getIntent() == null ? null : getIntent().getStringExtra(EXTRA_LAUNCH);
        super.onCreate(savedState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        // attach consumes and verifies the app-private descriptor on an IO worker.
        // SDL's opt-in ready hook will not start until the Session is authorized.
        StationPsxSession.attach(this, privateLaunchName);
    }
    @Override protected String[] getLibraries() {
        return new String[] {"SDL2", "main", "station_psx_online"};
    }
    @Override protected String getMainSharedObject() { return "libstation_psx_online.so"; }
    @Override protected String getMainFunction() { return "SDL_main"; }
    @Override protected String[] getArguments() {
        return new String[] {"--station-psx-launch", privateLaunchName == null ? "" : privateLaunchName};
    }
    @Override protected void onResume() {
        super.onResume();
        StationPsxSession.visibility(true);
    }
    @Override protected void onPause() {
        StationPsxSession.visibility(false);
        super.onPause();
    }
    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        int key = event.getKeyCode();
        if (key == KeyEvent.KEYCODE_BACK || key == KeyEvent.KEYCODE_MENU
                || key == KeyEvent.KEYCODE_BUTTON_MODE) {
            if (event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0)
                requestHumanExit();
            return true;
        }
        // All game/controller events retain the bundled SDL implementation.
        return super.dispatchKeyEvent(event);
    }
    @Override public void onBackPressed() { requestHumanExit(); }
    private void requestHumanExit() { StationPsxSession.confirmExit(this); }
    /** Called directly by the JNI owner-start callback; not an emulator READY. */
    public void recordOwnerThread() {
        Thread caller = Thread.currentThread();
        if (caller == Looper.getMainLooper().getThread()) return;
        if (capturedOwner == null) capturedOwner = caller;
    }
    /** Used by the opt-in SDL hook/watcher; null SDL global alone is insufficient. */
    public boolean canFinishSdlOwner() {
        return StationPsxExitGate.ownerEnded(StationPsxSession.humanExitAuthorized(), mSDLThread, capturedOwner);
    }
    @Override public void finish() {
        if (!StationPsxSession.humanExitAuthorized()) { requestHumanExit(); return; }
        // SDLMain invokes finish on its own thread AFTER clearing mSDLThread.
        // Capture that actual thread and defer the UI; never join it from itself.
        if (Looper.myLooper() != Looper.getMainLooper()) recordOwnerThread();
        Thread target = capturedOwner != null ? capturedOwner : mSDLThread;
        if (!StationPsxExitGate.ended(target)) {
            if (joiningOwner.compareAndSet(false, true)) {
                Thread waiter = new Thread(() -> {
                    try { target.join(); }
                    catch (InterruptedException e) { Thread.currentThread().interrupt(); return; }
                    runOnUiThread(this::finishRetiredOwner);
                }, "Station-PSX-human-exit");
                waiter.setDaemon(true); waiter.start();
            }
            return;
        }
        if (Looper.myLooper() != Looper.getMainLooper()) runOnUiThread(this::finishRetiredOwner);
        else finishRetiredOwner();
    }
    /** Called only after root Session closed transport and Binder following a human positive. */
    public void finishRetiredOwner() {
        if (Looper.myLooper() != Looper.getMainLooper()) { runOnUiThread(this::finishRetiredOwner); return; }
        if (retiring || !StationPsxExitGate.mayRetire(StationPsxSession.humanExitAuthorized(),
                StationPsxSession.humanCleanupComplete(), StationPsxApplication.isPrivateProcess(),
                mSDLThread, capturedOwner)) return;
        retiring = true;
        // finishActivity's binder result is sent before retiring this exact private PID.
        super.finish();
        Process.killProcess(Process.myPid());
    }
}
