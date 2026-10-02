package org.emulationstation.frontend.auth;

import android.content.Context;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Production-start login. The typed value is the one-time activation code.
 * The local password marker is not a license. The bearer stays in memory.
 */
public final class StationAuth {
    public interface Callback {
        void ok(String displayName);
        void fail(String message);
    }

    private static final ExecutorService EXECUTOR = Executors.newSingleThreadExecutor();
    private static volatile String accessToken;

    private StationAuth() {}

    public static boolean wantsCommercial(Context context, String field) {
        if (!StationConfig.ready()) return false;
        String trimmed = field == null ? "" : field.trim();
        if (StationProtocol.activationCode(trimmed)) return true;
        return trimmed.isEmpty() && new File(context.getNoBackupFilesDir(), "station-license-id.txt").isFile();
    }

    public static void open(Context context, String field, Callback callback) {
        if (!StationConfig.ready()) {
            callback.fail("Acesso comercial indisponivel.");
            return;
        }
        EXECUTOR.execute(() -> {
            try {
                File licenseFile = new File(context.getNoBackupFilesDir(), "station-license-id.txt");
                String trimmed = field == null ? "" : field.trim();
                String licenseId;
                if (StationProtocol.activationCode(trimmed)) {
                    licenseId = StationClient.activate(context, trimmed);
                    writeLicense(licenseFile, licenseId);
                } else if (trimmed.isEmpty() && licenseFile.isFile()) {
                    licenseId = readLicense(licenseFile);
                    if (!StationProtocol.licenseId(licenseId)) {
                        callback.fail("Informe o codigo de acesso.");
                        return;
                    }
                } else if (!trimmed.isEmpty()) {
                    callback.fail("Codigo de acesso invalido.");
                    return;
                } else {
                    callback.fail("Informe o codigo de acesso.");
                    return;
                }
                accessToken = StationClient.openSession(context, licenseId);
                StationStore.publish(context);
                String name;
                try {
                    name = StationClient.profile(accessToken);
                } catch (RuntimeException failure) {
                    throw failure;
                } catch (Exception failure) {
                    name = "";
                }
                if (name == null || name.isEmpty()) name = savedName(context);
                if (!name.isEmpty()) writeName(context, name);
                try { StationLibrary.refresh(context, accessToken); } catch (Exception ignored) { }
                callback.ok(name);
            } catch (Exception failure) {
                accessToken = null;
                callback.fail("Nao foi possivel autorizar este aparelho.");
            }
        });
    }

    public static String savedName(Context context) {
        if (!StationConfig.ready()) return "";
        return readOptional(new File(context.getNoBackupFilesDir(), "station-display-name.txt"));
    }

    public static void pullName(Context context, Callback callback) {
        if (!wantsCommercial(context, "")) {
            callback.ok("");
            return;
        }
        EXECUTOR.execute(() -> {
            try {
                File licenseFile = new File(context.getNoBackupFilesDir(), "station-license-id.txt");
                String licenseId = readLicense(licenseFile);
                if (!StationProtocol.licenseId(licenseId)) {
                    callback.ok("");
                    return;
                }
                accessToken = StationClient.openSession(context, licenseId);
                StationStore.publish(context);
                String name = "";
                try {
                    name = StationClient.profile(accessToken);
                } catch (RuntimeException failure) {
                    throw failure;
                } catch (Exception failure) {
                    name = "";
                }
                if (name == null || name.isEmpty()) name = savedName(context);
                if (!name.isEmpty()) writeName(context, name);
                try { StationLibrary.refresh(context, accessToken); } catch (Exception ignored) { }
                callback.ok(name);
            } catch (Exception failure) {
                accessToken = null;
                callback.ok(savedName(context));
            }
        });
    }

    private static void writeName(Context context, String name) throws Exception {
        writeLicense(new File(context.getNoBackupFilesDir(), "station-display-name.txt"), name);
    }

    private static String readOptional(File file) {
        if (!file.isFile()) return "";
        try {
            return readLicense(file);
        } catch (Exception failure) {
            return "";
        }
    }

    private static void writeLicense(File file, String licenseId) throws Exception {
        try (FileOutputStream output = new FileOutputStream(file)) {
            output.write(licenseId.getBytes(StandardCharsets.UTF_8));
        }
    }

    private static String readLicense(File file) throws Exception {
        byte[] data = new byte[(int) file.length()];
        try (FileInputStream input = new FileInputStream(file)) {
            int offset = 0;
            while (offset < data.length) {
                int read = input.read(data, offset, data.length - offset);
                if (read < 0) break;
                offset += read;
            }
        }
        return new String(data, StandardCharsets.UTF_8).trim();
    }
}
