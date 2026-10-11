package org.emulationstation.frontend.sony;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import java.io.IOException;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Validates a Station game, then dispatches to an owner inside this APK. */
public final class StationSonyLaunchActivity extends Activity {
    private ExecutorService preparation;
    private volatile boolean closed;
    private boolean dispatched;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        if (saved != null && saved.getBoolean("station.offline.dispatched", false)) {
            dispatched = true;
            finish();
            return;
        }
        Intent incoming = getIntent();
        String system = incoming.getStringExtra("station.platform");
        if (!"ps3".equals(system) && !"ps4".equals(system)) {
            failure("Sistema não reconhecido.");
            return;
        }
        if (Build.VERSION.SDK_INT < ("ps4".equals(system) ? 31 : 28) || !arm64()) {
            failure("ps4".equals(system) ? "PS4 requer Android 12 ou mais recente, de 64 bits." :
                "PS3 requer Android 9 ou mais recente, de 64 bits.");
            return;
        }
        preparation = Executors.newSingleThreadExecutor(runnable -> {
            Thread worker = new Thread(runnable, "StationSonyDispatch");
            worker.setDaemon(true);
            return worker;
        });
        preparation.execute(() -> {
            try {
                boolean settings = "settings".equals(incoming.getStringExtra("station.operation"));
                Uri source = settings ? null : incoming.getData();
                if (!settings) {
                    validateSource(source, system);
                    if (org.emulationstation.frontend.station.StationLocalSonyDemos.isMarkedDemo(this, source, system)) {
                        postFailure("Este arquivo DEMO é somente uma amostra visual. Para jogar, use o arquivo do seu jogo.");
                        return;
                    }
                }
                Intent target = new Intent(Intent.ACTION_VIEW);
                target.setClassName(getPackageName(), "org.emulationstation.frontend.sony." +
                    ("ps3".equals(system) ? "Ps3Activity" : "Ps4Activity"));
                target.putExtra("operation", settings ? "settings" : "play");
                if (source != null) {
                    target.setData(source);
                    target.putExtra("game_uri", source.toString());
                    target.setClipData(ClipData.newRawUri("Jogo", source));
                    target.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                }
                runOnUiThread(() -> dispatch(target));
            } catch (Exception cause) {
                postFailure(cause.getMessage() == null ? "Não foi possível preparar o jogo." : cause.getMessage());
            }
        });
    }

    public static boolean openSettings(Activity activity, String system) {
        if (activity == null || activity.isFinishing() || activity.isDestroyed() ||
            (!"ps3".equals(system) && !"ps4".equals(system))) return false;
        activity.runOnUiThread(() -> {
            if (activity.isFinishing() || activity.isDestroyed()) return;
            Intent request = new Intent().setClassName(activity.getPackageName(),
                "org.emulationstation.frontend.offline.StationSonyOfflineActivity");
            request.putExtra("station.platform", system);
            request.putExtra("station.operation", "settings");
            activity.startActivity(request);
        });
        return true;
    }

    private static boolean arm64() {
        for (String abi : Build.SUPPORTED_ABIS) if ("arm64-v8a".equals(abi)) return true;
        return false;
    }

    private void validateSource(Uri source, String system) throws IOException {
        if (source == null || !"content".equals(source.getScheme()) ||
            !(getPackageName() + ".turboeden.provider").equals(source.getAuthority())) {
            throw new IOException("O arquivo precisa estar na pasta de jogos da TurboStations.");
        }
        String name = null;
        try (Cursor row = getContentResolver().query(source, new String[] {OpenableColumns.DISPLAY_NAME}, null, null, null)) {
            if (row != null && row.moveToFirst()) name = row.getString(0);
        }
        String extension = name == null || name.lastIndexOf('.') < 0 ? "" :
            name.substring(name.lastIndexOf('.')).toLowerCase(Locale.ROOT);
        if (!("ps3".equals(system) ? ".iso".equals(extension) : ".pkg".equals(extension))) {
            throw new IOException("ps3".equals(system) ? "A abertura direta de PS3 aceita um arquivo ISO." :
                "A abertura direta de PS4 aceita um pacote PKG.");
        }
        try (ParcelFileDescriptor descriptor = getContentResolver().openFileDescriptor(source, "r")) {
            if (descriptor == null || descriptor.getStatSize() <= 83) {
                throw new IOException("O arquivo não contém um jogo completo.");
            }
        }
    }

    private void dispatch(Intent target) {
        if (closed || isFinishing() || dispatched) return;
        try {
            dispatched = true;
            startActivity(target);
            finish();
        } catch (RuntimeException cause) {
            dispatched = false;
            failure("Não foi possível abrir o motor interno. Seus jogos e saves foram preservados.");
        }
    }

    private void postFailure(String text) {
        runOnUiThread(() -> { if (!closed && !isFinishing()) failure(text); });
    }

    private void failure(String text) {
        if (closed || isFinishing()) return;
        new AlertDialog.Builder(this).setTitle("Jogar offline").setMessage(text)
            .setPositiveButton("Voltar", (dialog, which) -> finish()).setOnCancelListener(dialog -> finish()).show();
    }

    @Override public void onSaveInstanceState(Bundle saved) {
        saved.putBoolean("station.offline.dispatched", dispatched);
        super.onSaveInstanceState(saved);
    }

    @Override public void onDestroy() {
        closed = true;
        if (preparation != null) preparation.shutdownNow();
        super.onDestroy();
    }
}
