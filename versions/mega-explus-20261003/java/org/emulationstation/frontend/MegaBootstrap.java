package org.emulationstation.frontend;

import android.app.Activity;
import android.app.Application;
import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;
import android.os.Build;
import java.io.File;
import java.io.IOException;

/** Entry/storage bridge only. Controls, menus and emulation belong to upstream EX+. */
public final class MegaBootstrap {
    private static final String TAG = "StationMega";
    private static final String PATH = "station.mega.path";
    private static volatile String error = "Não foi possível abrir o MD.emu.";
    private MegaBootstrap() {}

    public static boolean initProcess(Application app) {
        // Called before any other engine initialization in the host Application.
        String process = null;
        if (Build.VERSION.SDK_INT >= 28) process = Application.getProcessName();
        else {
            ActivityManager manager = (ActivityManager) app.getSystemService(Context.ACTIVITY_SERVICE);
            java.util.List<ActivityManager.RunningAppProcessInfo> running = manager.getRunningAppProcesses();
            if (running != null) for (ActivityManager.RunningAppProcessInfo item : running)
                if (item.pid == android.os.Process.myPid()) process = item.processName;
        }
        if (!(app.getPackageName() + ":megadrive").equals(process)) return false;
        filesDir(app);
        cacheDir(app);
        Log.i(TAG, "Official EX+ process initialized; other engines skipped");
        return true;
    }

    private static String directory(File parent) {
        File dir = new File(parent, "mega-explus");
        if (!dir.isDirectory() && !dir.mkdirs())
            throw new IllegalStateException("Não foi possível preparar a pasta do Mega Drive.");
        return dir.getAbsolutePath();
    }
    public static String filesDir(Context context) { return directory(context.getApplicationContext().getFilesDir()); }
    public static String cacheDir(Context context) { return directory(context.getApplicationContext().getCacheDir()); }

    public static File externalDirectory(Context context, String type) {
        Context app = context.getApplicationContext();
        File parent = app.getExternalFilesDir(type);
        return new File(directory(parent != null ? parent : app.getFilesDir()));
    }

    public static boolean launch(Activity activity, String path, boolean settings) {
        if (activity == null || activity.isFinishing()) return false;
        final String game;
        try {
            filesDir(activity);
            cacheDir(activity);
            if (settings) game = null;
            else {
                if (path == null || path.isEmpty()) throw new IOException("Selecione um jogo instalado.");
                File file = new File(path).getCanonicalFile();
                if (!file.isFile() || !file.canRead() || file.length() == 0)
                    throw new IOException("Arquivo do jogo indisponível. Confira a instalação.");
                game = file.getAbsolutePath();
            }
        } catch (IOException | RuntimeException failure) {
            error = failure.getMessage();
            Log.w(TAG, "Launch preparation failed", failure);
            return false;
        }
        activity.runOnUiThread(() -> {
            try {
                Intent intent = new Intent();
                intent.setClassName(activity, "com.mdimagn.BaseActivity");
                if (game != null) intent.putExtra(PATH, game);
                activity.startActivity(intent);
                Log.i(TAG, settings ? "Official settings/menu requested" : "Official game requested");
            } catch (RuntimeException failure) {
                error = "Não foi possível abrir o MD.emu.";
                Log.e(TAG, "Launch failed", failure);
                Toast.makeText(activity, error, Toast.LENGTH_LONG).show();
            }
        });
        return true;
    }

    public static String getLastLaunchError() { return error; }

    public static String consumeGamePath(Activity activity) {
        Intent intent = activity.getIntent();
        if (intent == null || !intent.hasExtra(PATH)) return null;
        String path = intent.getStringExtra(PATH);
        intent.removeExtra(PATH);
        Log.i(TAG, "Game handed to upstream DocumentPickerEvent");
        return path;
    }

    public static void beforeDestroy(Activity activity) {
        // Upstream NativeActivity.onDestroy saves/destructs and exits only :megadrive.
        // Dispatch return before that native exit; never terminate the frontend.
        if (!activity.isFinishing() || activity.isChangingConfigurations()) return;
        Intent intent = new Intent();
        intent.setClassName(activity, "org.emulationstation.frontend.ESActivity");
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
        try {
            activity.startActivity(intent);
            Log.i(TAG, "Returning to existing platforms task");
        } catch (RuntimeException failure) {
            Log.e(TAG, "Could not bring platforms to foreground", failure);
        }
    }
}
