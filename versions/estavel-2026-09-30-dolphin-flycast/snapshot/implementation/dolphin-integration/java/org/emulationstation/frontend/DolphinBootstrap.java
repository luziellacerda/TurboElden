package org.emulationstation.frontend;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.Application;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Environment;
import android.util.Log;
import android.widget.Toast;
import java.io.*;
import java.util.List;

/** Integration only. Dolphin's engine, controls and emulation settings remain upstream. */
public final class DolphinBootstrap {
    public static volatile Throwable initializationError;
    private static final String TAG = "TurboDolphin";

    public static boolean initProcess(Application host) {
        String process = null;
        if (Build.VERSION.SDK_INT >= 28) process = Application.getProcessName();
        else {
            ActivityManager am = (ActivityManager) host.getSystemService(Context.ACTIVITY_SERVICE);
            List<ActivityManager.RunningAppProcessInfo> list = am.getRunningAppProcesses();
            if (list != null) for (ActivityManager.RunningAppProcessInfo p : list)
                if (p.pid == android.os.Process.myPid()) process = p.processName;
        }
        if (!(host.getPackageName() + ":dolphin").equals(process)) {
            if (host.getPackageName().equals(process)) removeLegacyEngineCopies(host);
            return false;
        }
        try {
            Class.forName("org.dolphinemu.dolphinemu.DolphinApplication")
                .getMethod("initEmbedded", Application.class).invoke(null, host);
            Log.i(TAG, "Official Dolphin 2609-7 initialized in its internal process");
        } catch (Throwable error) {
            initializationError = error;
            Log.e(TAG, "Dolphin initialization failed", error);
        }
        return true;
    }

    public static boolean launch(final Activity activity, final String path, final boolean settings) {
        if (activity == null || activity.isFinishing()) return false;
        if (!settings && (path == null || path.isEmpty())) return false;
        activity.runOnUiThread(() -> {
            try {
                Intent intent = new Intent(activity, DolphinEntryActivity.class);
                intent.putExtra("game", path);
                intent.putExtra("settings", settings);
                activity.startActivity(intent);
                Log.i(TAG, settings ? "Embedded settings requested" : "Embedded game requested");
            } catch (RuntimeException error) {
                Log.e(TAG, "Could not open embedded Dolphin", error);
                Toast.makeText(activity, "Não foi possível abrir o Dolphin. Tente novamente.", Toast.LENGTH_LONG).show();
            }
        });
        return true;
    }

    private static File folder(File root, String child) {
        if (root == null) throw new IllegalStateException("Armazenamento indisponível");
        File result = new File(root, child);
        if (!result.isDirectory() && !result.mkdirs()) throw new IllegalStateException("Não foi possível criar a pasta Dolphin");
        return result;
    }
    private static void removeLegacyEngineCopies(Context context) {
        File[] dirs = {new File(context.getFilesDir(), "cores"),
            new File(Environment.getExternalStorageDirectory(), "EmulationStation/.emulationstation/cores")};
        for (File dir : dirs) for (String name : new String[]{"dolphin_libretro_android.so", "libdolphin_libretro_android.so"}) {
            File file = new File(dir, name);
            if (file.isFile()) {
                if (file.delete()) Log.i(TAG, "Removed obsolete Dolphin Libretro binary");
                else Log.w(TAG, "Obsolete binary could not be removed; legacy route remains disabled");
            }
        }
    }
    public static File userDirectory(Context context) {
        return context == null ? null : folder(context.getExternalFilesDir(null), "Dolphin");
    }
    public static File internalDirectory(Context context) { return folder(context.getFilesDir(), "Dolphin"); }
    public static File cacheDirectory(Context context) {
        File root = context.getExternalCacheDir();
        return folder(root != null ? root : context.getCacheDir(), "Dolphin");
    }

    /** Copy native in-game saves only; old quick states/config/shaders stay untouched. */
    public static void migrateLegacySaves(Context context) {
        File dest = userDirectory(context);
        File marker = new File(dest, ".turborama-legacy-save-copy-v1");
        if (marker.exists()) return;
        File home = new File(Environment.getExternalStorageDirectory(), "EmulationStation");
        File[] sources = {
            new File(home, ".emulationstation/bios/dolphin-emu/User"),
            new File(home, ".emulationstation/saves/dolphin-emu/User"),
            new File(home, ".emulationstation/saves/User"),
            new File(context.getFilesDir(), ".emulationstation/bios/dolphin-emu/User")
        };
        try {
            for (File root : sources) if (root.isDirectory()) {
                for (String name : new String[]{"GC", "Wii", "GBA", "WFS", "Triforce"}) {
                    File from = new File(root, name);
                    if (from.isDirectory()) copyMissing(from, new File(dest, name), root.getCanonicalPath());
                }
            }
            try (FileOutputStream out = new FileOutputStream(marker)) { out.write("Saves preservados; configurações do Dolphin novo.\n".getBytes("UTF-8")); }
            Log.i(TAG, "Legacy native saves checked; originals retained");
        } catch (IOException error) {
            // Never discard a playable existing save or report migration success on failure.
            Log.e(TAG, "Legacy save copy incomplete; originals remain available", error);
            throw new IllegalStateException("Não foi possível preservar todos os saves do Dolphin antigo", error);
        }
    }
    private static void copyMissing(File from, File to, String root) throws IOException {
        if (!from.getCanonicalPath().startsWith(root + File.separator)) throw new IOException("Pasta fora da origem de saves");
        if (from.isDirectory()) {
            if (!to.isDirectory() && !to.mkdirs()) throw new IOException("Falha ao criar pasta de saves");
            File[] list = from.listFiles();
            if (list == null) throw new IOException("Falha ao ler saves");
            for (File item : list) copyMissing(item, new File(to, item.getName()), root);
        } else if (from.isFile() && !to.exists()) {
            File temp = new File(to.getParentFile(), to.getName() + ".td-copying");
            try (InputStream in = new FileInputStream(from); OutputStream out = new FileOutputStream(temp)) {
                byte[] buffer = new byte[65536]; int n;
                while ((n = in.read(buffer)) >= 0) out.write(buffer, 0, n);
            }
            if (!temp.renameTo(to)) throw new IOException("Falha ao concluir cópia de save");
        }
    }
}
