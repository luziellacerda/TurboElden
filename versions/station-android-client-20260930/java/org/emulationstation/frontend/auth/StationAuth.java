package org.emulationstation.frontend.auth;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.KeyStore;
import java.util.Arrays;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import org.json.JSONObject;

/** A single network worker owns activation, session renewal and the minimal profile cache. */
public final class StationAuth {
    private static final String STORAGE_ALIAS = "turborama.station.record.v1";
    private static final String RECORD = "station-activation-v1.bin";
    private static final ExecutorService NETWORK = Executors.newSingleThreadExecutor();
    private static final Handler MAIN = new Handler(Looper.getMainLooper());
    private static Context app;
    private static String licenseId;
    private static String deviceId;
    private static String displayName = "";
    private static String accessToken;
    private static String sessionId;
    private static long expiresElapsed;
    private static boolean busy;

    public interface Callback {
        void finished(boolean authorized, String message);
    }

    private StationAuth() {}

    public static synchronized void attach(Context context) {
        if (app != null) return;
        app = context.getApplicationContext();
        if (app == null) app = context;
        restore();
    }

    public static synchronized boolean isAuthorized() {
        return StationConfig.ready() && accessToken != null &&
                SystemClock.elapsedRealtime() < expiresElapsed;
    }

    public static synchronized boolean hasActivation() {
        return licenseId != null && deviceId != null;
    }

    public static synchronized String displayName() { return displayName; }

    public static synchronized String welcomeText() {
        return displayName.isEmpty() ? "Bem-vindo" : "Bem-vindo, " + displayName;
    }

    public static synchronized String tokenForProtectedOperation() {
        return isAuthorized() ? accessToken : null;
    }

    public static synchronized String currentSessionId() {
        return isAuthorized() ? sessionId : null;
    }

    public static void activate(Context context, final String code, final Callback callback) {
        attach(context);
        if (code == null || code.trim().isEmpty()) {
            dispatch(callback, false, "Digite o código de acesso.");
            return;
        }
        if (!begin(callback)) return;
        NETWORK.execute(new Runnable() {
            @Override public void run() {
                try {
                    KeyPair key = StationCrypto.deviceKey(true);
                    JSONObject challenge = StationApi.activationChallenge(code.trim(), key);
                    JSONObject grant = StationApi.activate(code.trim(), key, challenge);
                    String id = StationCrypto.deviceId(key.getPublic());
                    synchronized (StationAuth.class) {
                        licenseId = grant.getString("licenseId");
                        deviceId = id;
                        displayName = "";
                        save();
                    }
                    openSession(key);
                    end(callback, true, "Acesso liberado.");
                } catch (Exception error) {
                    end(callback, false, explain(error));
                }
            }
        });
    }

    public static void resume(Context context, final Callback callback) {
        attach(context);
        if (!StationConfig.ready()) {
            dispatch(callback, false, "A conexão com o servidor ainda não está configurada.");
            return;
        }
        if (isAuthorized()) {
            dispatch(callback, true, "Acesso liberado.");
            return;
        }
        if (!hasActivation()) {
            dispatch(callback, false, "Digite o código de acesso.");
            return;
        }
        if (!begin(callback)) return;
        NETWORK.execute(new Runnable() {
            @Override public void run() {
                try {
                    KeyPair key = StationCrypto.deviceKey(false);
                    if (key == null || !StationCrypto.deviceId(key.getPublic()).equals(deviceId))
                        throw new SecurityException("A chave deste aparelho não está disponível. Solicite transferência da licença.");
                    openSession(key);
                    end(callback, true, "Acesso liberado.");
                } catch (Exception error) {
                    end(callback, false, explain(error));
                }
            }
        });
    }

    /** Called before a protected operation; it never performs network I/O on the UI thread. */
    public static void requireSession(Context context, Callback callback) {
        resume(context, callback);
    }

    private static void openSession(KeyPair key) throws Exception {
        final String license;
        final String id;
        synchronized (StationAuth.class) { license = licenseId; id = deviceId; }
        JSONObject grant = StationApi.openSession(license, key);
        if (!id.equals(grant.optString("deviceId"))) throw new SecurityException("Sessão de outro aparelho");
        String token = grant.getString("accessToken");
        if (!token.matches("[A-Za-z0-9._~-]{16,4096}"))
            throw new SecurityException("Token inválido");
        int seconds = grant.getInt("expiresInSeconds");
        JSONObject profile = StationApi.profile(token, license, id, grant.getString("sessionId"));
        String name = profile.optString("displayName", "").trim();
        if (name.length() > 80) name = name.substring(0, 80);
        synchronized (StationAuth.class) {
            accessToken = token;
            sessionId = grant.getString("sessionId");
            expiresElapsed = SystemClock.elapsedRealtime() + (seconds - 5L) * 1000L;
            displayName = name;
            save();
        }
    }

    private static synchronized boolean begin(Callback callback) {
        if (busy) {
            dispatch(callback, false, "Aguarde a verificação em andamento.");
            return false;
        }
        busy = true;
        return true;
    }

    private static synchronized void end(Callback callback, boolean success, String message) {
        busy = false;
        dispatch(callback, success, message);
    }

    private static void dispatch(final Callback callback, final boolean success, final String message) {
        if (callback != null) MAIN.post(new Runnable() {
            @Override public void run() { callback.finished(success, message); }
        });
    }

    private static String explain(Exception error) {
        if (error instanceof StationApi.StationFailure) {
            int status = ((StationApi.StationFailure) error).status;
            if (status == 401 || status == 403) return "Acesso negado. Confira a licença ou solicite suporte.";
            if (status == 409) return "Licença vinculada a outro aparelho. Solicite transferência.";
            if (status == 410) return "Código expirado. Solicite outro código.";
        }
        if (error instanceof SecurityException) return error.getMessage();
        return "Não foi possível conectar ao servidor. Tente novamente.";
    }

    private static AtomicFile file() {
        return new AtomicFile(new File(app.getNoBackupFilesDir(), RECORD));
    }

    private static SecretKey storageKey(boolean create) throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (store.containsAlias(STORAGE_ALIAS)) return (SecretKey) store.getKey(STORAGE_ALIAS, null);
        if (!create) return null;
        KeyGenerator generator = KeyGenerator.getInstance("AES", "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(STORAGE_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256).build());
        return generator.generateKey();
    }

    private static void save() throws Exception {
        JSONObject value = new JSONObject();
        value.put("version", 1);
        value.put("licenseId", licenseId);
        value.put("deviceId", deviceId);
        value.put("displayName", displayName);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, storageKey(true));
        cipher.updateAAD(app.getPackageName().getBytes(StandardCharsets.UTF_8));
        byte[] iv = cipher.getIV();
        if (iv.length != 12) throw new SecurityException("IV inválido");
        byte[] encrypted = cipher.doFinal(StationCrypto.utf8(value.toString()));
        AtomicFile target = file();
        FileOutputStream output = null;
        try {
            output = target.startWrite();
            output.write(1); output.write(iv); output.write(encrypted);
            target.finishWrite(output);
        } catch (Exception error) {
            if (output != null) target.failWrite(output);
            throw error;
        }
    }

    private static void restore() {
        try {
            AtomicFile source = file();
            if (!source.getBaseFile().exists() || source.getBaseFile().length() > 4096) return;
            byte[] data = source.readFully();
            if (data.length < 30 || data[0] != 1) return;
            SecretKey key = storageKey(false);
            if (key == null) return;
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE, key,
                    new GCMParameterSpec(128, Arrays.copyOfRange(data, 1, 13)));
            cipher.updateAAD(app.getPackageName().getBytes(StandardCharsets.UTF_8));
            JSONObject value = new JSONObject(new String(
                    cipher.doFinal(data, 13, data.length - 13), StandardCharsets.UTF_8));
            if (value.optInt("version") != 1) return;
            String license = value.optString("licenseId");
            String device = value.optString("deviceId");
            if (!license.isEmpty() && !device.isEmpty()) {
                licenseId = license;
                deviceId = device;
                displayName = value.optString("displayName", "");
            }
        } catch (Exception ignored) {
            // Damaged or undecryptable state requires account recovery, never local authorization.
        }
    }
}
