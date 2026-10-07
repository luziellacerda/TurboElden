package org.emulationstation.frontend;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.Locale;

/** One entry point for the unchanged MAME runtime and both Neo Geo families. */
public final class MameEntryActivity extends Activity {
    private static final int SETTINGS = 41;
    private static final int IMPORT_BIOS = 42;
    private boolean settingsLaunched;
    private boolean preparing;
    private int preparationGeneration;
    private ProgressDialog progress;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        try {
            if (getIntent().getBooleanExtra("settings", false)) {
                MameBootstrap.seed(this, getIntent().getStringExtra("game"));
                Intent preferences = new Intent();
                preferences.setClassName(this, "com.seleuco.mame4droid.prefs.UserPreferences");
                preferences.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
                startActivityForResult(preferences, SETTINGS);
                settingsLaunched = true;
                return;
            }
            File rom = selectedGame();
            if (NeoCdSupport.isCd(rom)) prepareCd(null);
            else launchGame(rom, null);
        } catch (Exception error) { showError(error); }
    }

    private File selectedGame() throws IOException {
        String path = getIntent().getStringExtra("game");
        File rom = path == null ? null : new File(path);
        if (rom == null || !rom.isFile() || !rom.canRead())
            throw new IOException("O arquivo instalado não está disponível. Volte ao catálogo e confira a instalação deste jogo.");
        return rom;
    }

    private File biosHome() { return new File(getFilesDir(), "mame/station-bios/neogeocd"); }

    private void launchGame(File rom, String cdBios) throws IOException {
        if (isFinishing() || isDestroyed()) return;
        String game = rom.getAbsolutePath();
        MameBootstrap.seed(this, game);
        Intent launch = new Intent(Intent.ACTION_VIEW);
        launch.setClassName(this, "com.seleuco.mame4droid.MAME4droid");
        String cli = MameBootstrap.cliParamsFor(game);
        if (cdBios != null) {
            File driver = new File(rom.getParentFile(), "neocdz.zip");
            launch.setDataAndType(Uri.fromFile(driver), "application/zip");
            cli += " " + NeoCdSupport.cli(rom, cdBios);
        } else launch.setDataAndType(Uri.fromFile(rom), mimeFor(game));
        launch.putExtra("cli_params", cli);
        launch.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
        android.util.Log.i("TurboMame", cdBios == null ? "launch-route=cartridge-or-arcade" : "launch-route=neocdz-cdrom");
        startActivity(launch);
        finish();
    }

    private void prepareCd(final Uri importedBios) {
        if (preparing || isFinishing() || isDestroyed()) return;
        preparing = true;
        final int generation = ++preparationGeneration;
        progress = ProgressDialog.show(this, "Neo Geo CD", importedBios == null
                ? "Preparando o disco e a BIOS…" : "Conferindo a BIOS…", true, false);
        new Thread(() -> {
            File rom = null;
            String bios = null;
            Exception failure = null;
            try {
                rom = selectedGame();
                if (importedBios != null) {
                    try (InputStream input = getContentResolver().openInputStream(importedBios)) {
                        if (input == null) throw new IOException("Não foi possível ler a BIOS selecionada.");
                        NeoCdSupport.importBios(biosHome(), input);
                    }
                }
                bios = NeoCdSupport.prepare(rom, biosHome(), new File("/storage/emulated/0/EmulationStation/roms"));
            } catch (Exception error) { failure = error; }
            final File readyRom = rom;
            final String readyBios = bios;
            final Exception error = failure;
            runOnUiThread(() -> {
                if (generation != preparationGeneration || isFinishing() || isDestroyed()) return;
                preparing = false;
                dismissProgress();
                if (error != null) { showError(error); return; }
                try { launchGame(readyRom, readyBios); }
                catch (Exception launchFailure) { showError(launchFailure); }
            });
        }, "Station-CD-prepare").start();
    }

    private void showError(Exception error) {
        if (isFinishing() || isDestroyed()) return;
        String game = getIntent().getStringExtra("game");
        boolean cd = game != null && NeoCdSupport.isCd(new File(game));
        android.util.Log.w("TurboMame", "launch-failed kind=" + error.getClass().getSimpleName());
        AlertDialog.Builder dialog = new AlertDialog.Builder(this)
                .setTitle(cd ? "Neo Geo CD" : "Neo Geo / MAME")
                .setMessage(error.getMessage() == null ? "Não foi possível abrir o emulador." : error.getMessage())
                .setPositiveButton("VOLTAR", (d, which) -> MameBootstrap.returnToPlatforms(this))
                .setCancelable(false);
        if (cd) dialog.setNegativeButton("IMPORTAR BIOS", (d, which) -> {
            try {
                Intent pick = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                pick.addCategory(Intent.CATEGORY_OPENABLE);
                pick.setType("*/*");
                startActivityForResult(pick, IMPORT_BIOS);
            } catch (Exception failure) { showError(failure); }
        });
        dialog.show();
    }

    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request == SETTINGS && settingsLaunched) { MameBootstrap.returnToPlatforms(this); return; }
        if (request != IMPORT_BIOS) return;
        if (result != RESULT_OK || data == null || data.getData() == null) {
            showError(new IOException("A BIOS não foi selecionada. O jogo continua disponível no catálogo."));
        } else prepareCd(data.getData());
    }

    private void dismissProgress() {
        if (progress != null) { progress.dismiss(); progress = null; }
    }
    @Override protected void onDestroy() {
        ++preparationGeneration;
        dismissProgress();
        super.onDestroy();
    }
    @Override public void onBackPressed() { MameBootstrap.returnToPlatforms(this); }
    private static String mimeFor(String path) {
        String p = path.toLowerCase(Locale.US);
        if (p.endsWith(".chd") || p.endsWith(".iso") || p.endsWith(".bin")) return "application/octet-stream";
        if (p.endsWith(".cue") || p.endsWith(".m3u")) return "text/plain";
        return "application/zip";
    }
}
