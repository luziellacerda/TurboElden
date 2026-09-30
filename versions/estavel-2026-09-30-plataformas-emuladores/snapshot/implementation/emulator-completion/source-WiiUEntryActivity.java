package org.emulationstation.frontend;

import android.app.Activity;
import android.os.Bundle;
import android.os.SystemClock;
import android.content.Intent;
import android.graphics.Color;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import java.io.File;
import java.util.concurrent.atomic.AtomicBoolean;

/** Native Android preparation screen; launch and settings remain the original Cemu activities. */
public final class WiiUEntryActivity extends Activity {
    private final AtomicBoolean cancelled = new AtomicBoolean();
    private boolean preparing, launching, resumed;
    private volatile boolean reserved;
    private File pendingLaunch;
    private TextView status;
    private ProgressBar bar;
    private long lastProgress;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        if (WiiUBootstrap.initializationError() != null) {
            showError("Não foi possível iniciar o Cemu. Volte às plataformas e tente novamente."); return;
        }
        WiiUArchive.watchApplication(getApplication());
        if (getIntent().getBooleanExtra("settings", false)) {
            openCemu(null, true); return;
        }
        String path = getIntent().getStringExtra("game");
        if (path == null || path.isEmpty()) { showError("O caminho do jogo Wii U não foi informado."); return; }
        if (!WiiUArchive.beginLaunch(getApplication())) {
            showError("Há um jogo Wii U aberto ou em preparação. Feche-o antes de abrir outro."); return;
        }
        reserved = true;
        showPreparation();
        preparing = true;
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        new Thread(() -> {
            try {
                File game = WiiUArchive.prepare(getApplicationContext(), new File(path), new WiiUArchive.Progress() {
                    @Override public boolean isCancelled() { return cancelled.get(); }
                    @Override public void onProgress(int percent, String message) {
                        long now = SystemClock.uptimeMillis();
                        if (percent != 100 && now - lastProgress < 200) return;
                        lastProgress = now;
                        runOnUiThread(() -> {
                            if (!isFinishing() && !isDestroyed() && !cancelled.get()) {
                                bar.setProgress(percent);
                                status.setText(message + " · " + percent + "%");
                            }
                        });
                    }
                });
                runOnUiThread(() -> {
                    preparing = false;
                    getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                    if (!isFinishing() && !isDestroyed() && !cancelled.get()) {
                        if (resumed) openCemu(game, false); else pendingLaunch = game;
                    } else abortReservedLaunch();
                });
            } catch (Throwable error) {
                abortReservedLaunch();
                android.util.Log.e("TurboWiiU", "Preparation failed", error);
                runOnUiThread(() -> {
                    preparing = false;
                    getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                    if (!isFinishing() && !isDestroyed())
                        showError(error instanceof java.io.IOException ? error.getMessage()
                            : "Não foi possível preparar o jogo Wii U. Volte às plataformas e tente novamente.");
                });
            }
        }, "WiiUPrepare").start();
    }

    @Override protected void onResume() {
        super.onResume(); resumed = true;
        if (pendingLaunch != null && !cancelled.get()) {
            File game = pendingLaunch; pendingLaunch = null; openCemu(game, false);
        }
    }

    @Override protected void onPause() {
        resumed = false;
        super.onPause();
    }

    @Override protected void onStop() {
        resumed = false;
        // No decompression loop remains working invisibly after Home or another application.
        if (preparing && !launching) cancelled.set(true);
        super.onStop();
    }

    @Override protected void onDestroy() {
        cancelled.set(true);
        if (!preparing && !launching) abortReservedLaunch();
        super.onDestroy();
    }
    @Override public void onBackPressed() { cancelled.set(true); finish(); }

    private void openCemu(File game, boolean settings) {
        try {
            Intent next = new Intent();
            next.setClassName(this, settings ? "info.cemu.cemu.MainActivity" : "info.cemu.cemu.emulation.EmulationActivity");
            if (!settings) next.putExtra("info.cemu.cemu.LaunchPath", game.getAbsolutePath());
            launching = true; startActivity(next); finish();
        } catch (Throwable error) {
            launching = false;
            if (!settings) abortReservedLaunch();
            android.util.Log.e("TurboWiiU", "Entry failed", error);
            showError("Não foi possível abrir o Wii U. Verifique o arquivo do jogo.");
        }
    }

    private synchronized void abortReservedLaunch() {
        if (reserved) { reserved = false; WiiUArchive.abortLaunch(); }
    }

    private LinearLayout panel() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        int pad = (int) (28 * getResources().getDisplayMetrics().density);
        box.setPadding(pad, pad, pad, pad);
        box.setBackgroundColor(Color.rgb(6, 14, 8));
        setContentView(box); return box;
    }

    private TextView text(String value, int size) {
        TextView view = new TextView(this);
        view.setText(value); view.setTextColor(Color.WHITE); view.setTextSize(size);
        view.setPadding(0, 10, 0, 18); return view;
    }

    private void showPreparation() {
        LinearLayout box = panel();
        box.addView(text("TURBORAMA · WII U", 23));
        status = text("Preparando jogo Wii U · 0%", 18); box.addView(status);
        bar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        bar.setMax(100); bar.setProgressTintList(android.content.res.ColorStateList.valueOf(Color.rgb(70, 235, 99)));
        box.addView(bar, new LinearLayout.LayoutParams(-1, -2));
        box.addView(text("O arquivo baixado será preservado. A preparação usa uma pasta privada e será reutilizada na próxima abertura do mesmo jogo.", 15));
        Button cancel = new Button(this); cancel.setText("CANCELAR E VOLTAR");
        cancel.setOnClickListener(v -> { cancelled.set(true); finish(); }); box.addView(cancel);
    }

    private void showError(String message) {
        LinearLayout box = panel();
        box.addView(text(message == null ? "Não foi possível preparar o jogo Wii U." : message, 19));
        Button back = new Button(this); back.setText("VOLTAR ÀS PLATAFORMAS");
        back.setOnClickListener(v -> { cancelled.set(true); finish(); }); box.addView(back);
    }
}
