package org.emulationstation.frontend.auth;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.json.JSONObject;

/** Async entry points for the native catalog and download bridge. */
public final class StationContent {
    private static final ExecutorService NETWORK = Executors.newSingleThreadExecutor();
    private static final Handler MAIN = new Handler(Looper.getMainLooper());

    public interface Callback {
        void finished(JSONObject result, String error);
    }

    private StationContent() {}

    public static void catalog(Context context, final String platform, final String cursor,
                               final Callback callback) {
        StationAuth.requireSession(context, new StationAuth.Callback() {
            @Override public void finished(boolean authorized, String message) {
                if (!authorized) { deliver(callback, null, message); return; }
                NETWORK.execute(new Runnable() {
                    @Override public void run() {
                        try {
                            String token = StationAuth.tokenForProtectedOperation();
                            String session = StationAuth.currentSessionId();
                            if (token == null || session == null) throw new SecurityException("Sessão expirada");
                            JSONObject result = StationApi.catalog(token, platform,
                                    cursor == null ? "" : cursor, currentDeviceId(), session);
                            deliver(callback, result, null);
                        } catch (Exception error) { deliver(callback, null, "Catálogo indisponível."); }
                    }
                });
            }
        });
    }

    public static void authorizeDownload(Context context, final String itemId,
                                         final Callback callback) {
        StationAuth.requireSession(context, new StationAuth.Callback() {
            @Override public void finished(boolean authorized, String message) {
                if (!authorized) { deliver(callback, null, message); return; }
                NETWORK.execute(new Runnable() {
                    @Override public void run() {
                        try {
                            String token = StationAuth.tokenForProtectedOperation();
                            String session = StationAuth.currentSessionId();
                            if (token == null || session == null) throw new SecurityException("Sessão expirada");
                            JSONObject result = StationApi.authorizeDownload(token, itemId,
                                    currentDeviceId(), session);
                            URL target = new URL(result.getString("downloadUrl"));
                            if (!"https".equals(target.getProtocol()) || target.getUserInfo() != null)
                                throw new SecurityException("Destino de download inválido");
                            if (result.optInt("expiresInSeconds", 0) < 1 ||
                                    result.optInt("expiresInSeconds", 0) > 3600)
                                throw new SecurityException("Concessão inválida");
                            deliver(callback, result, null);
                        } catch (Exception error) { deliver(callback, null, "Download não autorizado."); }
                    }
                });
            }
        });
    }

    private static String currentDeviceId() throws Exception {
        java.security.KeyPair key = StationCrypto.deviceKey(false);
        if (key == null) throw new SecurityException("Chave do aparelho ausente");
        return StationCrypto.deviceId(key.getPublic());
    }

    private static void deliver(final Callback callback, final JSONObject result, final String error) {
        if (callback != null) MAIN.post(new Runnable() {
            @Override public void run() { callback.finished(result, error); }
        });
    }
}
