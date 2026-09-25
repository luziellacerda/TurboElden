package org.emulationstation.frontend;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.util.Log;
import androidx.core.app.NotificationCompat;
import androidx.core.app.ServiceCompat;
import androidx.core.content.ContextCompat;
import java.util.Locale;
import org.apache.commons.compress.compressors.bzip2.BZip2Constants;
import org.apache.commons.p013io.FileUtils;

public final class DownloadService extends Service {
    private static final String CHANNEL_DONE = "downloads_done";
    private static final String CHANNEL_PROGRESS = "downloads";
    private static final int NOTIFICATION_ID = 7001;
    private static final long REFRESH_MS = 1000;
    private static volatile boolean sRunning;
    private long mLastTime;
    private double mSpeed;
    private PowerManager.WakeLock mWakeLock;
    private WifiManager.WifiLock mWifiLock;
    private final Handler mHandler = new Handler(Looper.getMainLooper());
    private long mLastBytes = -1;
    private final Runnable mRefresh = new Runnable() {
        @Override
        public void run() {
            int i = HttpBridge.activeFileDownloads().count;
            DownloadService downloadService = DownloadService.this;
            if (i == 0) {
                downloadService.stopSelf();
                return;
            }
            NotificationManager manager = (NotificationManager) downloadService.getSystemService("notification");
            if (manager != null) {
                manager.notify(DownloadService.NOTIFICATION_ID, DownloadService.this.buildProgress());
            }
            DownloadService.this.mHandler.postDelayed(this, 1000L);
        }
    };

    static void ensureRunning() {
        Context context = ESActivity.getAppContext();
        if (context == null || sRunning) {
            return;
        }
        ESActivity.requestNotificationPermission();
        try {
            ContextCompat.startForegroundService(context, new Intent(context, (Class<?>) DownloadService.class));
        } catch (Exception e) {
            Log.w(ESActivity.TAG, "Could not start the download service", e);
        }
    }

    static void notifyFinished(String title, boolean succeeded, String error) {
        Context context = ESActivity.getAppContext();
        if (context == null) {
            return;
        }
        createChannels(context);
        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_DONE).setSmallIcon(succeeded ? android.R.drawable.stat_sys_download_done : android.R.drawable.stat_notify_error).setContentTitle(succeeded ? "Download concluído" : "Falha no download").setContentText(succeeded ? title : title + " - " + error).setContentIntent(openAppIntent(context)).setAutoCancel(true);
        NotificationManager manager = (NotificationManager) context.getSystemService("notification");
        if (manager != null) {
            manager.notify(Math.abs(title.hashCode() % BZip2Constants.BASEBLOCKSIZE) + 7002, builder.build());
        }
    }

    @Override
    public void onCreate() {
        int mode;
        super.onCreate();
        sRunning = true;
        createChannels(this);
        PowerManager power = (PowerManager) getSystemService("power");
        if (power != null) {
            this.mWakeLock = power.newWakeLock(1, "EmulationStation:download");
            this.mWakeLock.setReferenceCounted(false);
            this.mWakeLock.acquire(21600000L);
        }
        WifiManager wifi = (WifiManager) getApplicationContext().getSystemService("wifi");
        if (wifi != null) {
            if (Build.VERSION.SDK_INT >= 29) {
                mode = 4;
            } else {
                mode = 3;
            }
            this.mWifiLock = wifi.createWifiLock(mode, "EmulationStation:download");
            this.mWifiLock.setReferenceCounted(false);
            this.mWifiLock.acquire();
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        int type = Build.VERSION.SDK_INT >= 29 ? 1 : 0;
        ServiceCompat.startForeground(this, NOTIFICATION_ID, buildProgress(), type);
        this.mHandler.removeCallbacks(this.mRefresh);
        this.mHandler.post(this.mRefresh);
        return 2;
    }

    public Notification buildProgress() {
        String title;
        HttpBridge.DownloadSnapshot snapshot = HttpBridge.activeFileDownloads();
        long now = System.currentTimeMillis();
        if (this.mLastBytes >= 0 && now > this.mLastTime && snapshot.downloaded >= this.mLastBytes) {
            double instant = ((snapshot.downloaded - this.mLastBytes) * 1000.0d) / (now - this.mLastTime);
            this.mSpeed = this.mSpeed <= 0.0d ? instant : (this.mSpeed * 0.6d) + (0.4d * instant);
        }
        this.mLastBytes = snapshot.downloaded;
        this.mLastTime = now;
        if (snapshot.count <= 1) {
            title = "Baixando " + (snapshot.firstTitle != null ? snapshot.firstTitle : "");
        } else {
            title = "Baixando " + snapshot.count + " jogos";
        }
        StringBuilder text = new StringBuilder();
        int percent = -1;
        if (snapshot.total > 0) {
            percent = (int) Math.min(100L, (snapshot.downloaded * 100) / snapshot.total);
            text.append(percent).append("%  ·  ").append(size(snapshot.downloaded)).append(" de ").append(size(snapshot.total));
        } else {
            text.append(size(snapshot.downloaded));
        }
        if (this.mSpeed > 0.0d) {
            text.append("  ·  ").append(size((long) this.mSpeed)).append("/s");
        }
        return new NotificationCompat.Builder(this, CHANNEL_PROGRESS).setSmallIcon(android.R.drawable.stat_sys_download).setContentTitle(title).setContentText(text.toString()).setProgress(100, Math.max(percent, 0), percent < 0).setOngoing(true).setOnlyAlertOnce(true).setSilent(true).setContentIntent(openAppIntent(this)).setForegroundServiceBehavior(1).build();
    }

    @Override
    public void onDestroy() {
        this.mHandler.removeCallbacks(this.mRefresh);
        if (this.mWakeLock != null && this.mWakeLock.isHeld()) {
            this.mWakeLock.release();
        }
        if (this.mWifiLock != null && this.mWifiLock.isHeld()) {
            this.mWifiLock.release();
        }
        sRunning = false;
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private static PendingIntent openAppIntent(Context context) {
        Intent open = new Intent(context, (Class<?>) ESActivity.class).setAction("android.intent.action.MAIN").addCategory("android.intent.category.LAUNCHER").addFlags(270532608);
        return PendingIntent.getActivity(context, 0, open, 201326592);
    }

    private static void createChannels(Context context) {
        NotificationManager manager = (NotificationManager) context.getSystemService("notification");
        if (manager == null) {
            return;
        }
        NotificationChannel progress = new NotificationChannel(CHANNEL_PROGRESS, "Downloads em andamento", 2);
        progress.setShowBadge(false);
        manager.createNotificationChannel(progress);
        manager.createNotificationChannel(new NotificationChannel(CHANNEL_DONE, "Downloads concluídos", 3));
    }

    private static String size(long bytes) {
        if (bytes >= FileUtils.ONE_GB) {
            return String.format(Locale.US, "%.2f GB", Double.valueOf(bytes / 1.073741824E9d));
        }
        if (bytes >= FileUtils.ONE_MB) {
            return String.format(Locale.US, "%.1f MB", Double.valueOf(bytes / 1048576.0d));
        }
        return String.format(Locale.US, "%d KB", Long.valueOf(bytes / FileUtils.ONE_KB));
    }
}
