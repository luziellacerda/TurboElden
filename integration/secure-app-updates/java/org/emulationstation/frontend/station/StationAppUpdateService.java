package org.emulationstation.frontend.station;

import android.app.*;
import android.content.*;
import android.os.IBinder;

/** Foreground only after the user taps Update; no silent periodic APK download. */
public final class StationAppUpdateService extends Service {
    private static final String CHANNEL="station-app-updates";
    private static final int NOTICE=0x535550;
    private boolean started;
    private final Runnable refresh=()->getSystemService(NotificationManager.class).notify(NOTICE,notice());
    static void pendingNotice(Context context,Intent confirmation){
        NotificationManager manager=context.getSystemService(NotificationManager.class);
        manager.createNotificationChannel(new NotificationChannel(CHANNEL,"Atualizações do aplicativo",NotificationManager.IMPORTANCE_LOW));
        // The platform-supplied confirmation remains actionable even if the
        // app process is reclaimed after the download service has stopped.
        PendingIntent open=PendingIntent.getActivity(context,NOTICE,new Intent(confirmation).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        manager.notify(NOTICE,new Notification.Builder(context,CHANNEL).setSmallIcon(android.R.drawable.stat_sys_download_done)
            .setContentTitle("Concluir atualização do TurboStation").setContentText("Toque para confirmar a instalação no Android.")
            .setContentIntent(open).setAutoCancel(true).setOnlyAlertOnce(true).build());
    }
    static void clearNotice(Context context){context.getSystemService(NotificationManager.class).cancel(NOTICE);}
    private Notification notice(){
        PendingIntent open=PendingIntent.getActivity(this,NOTICE,new Intent(this,StationAppUpdateActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_SINGLE_TOP),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        long total=StationAppUpdater.total,done=StationAppUpdater.received;
        return new Notification.Builder(this,CHANNEL).setSmallIcon(android.R.drawable.stat_sys_download)
            .setContentTitle("Atualização do TurboStation").setContentText(StationAppUpdater.message)
            .setContentIntent(open).setOngoing(true).setOnlyAlertOnce(true)
            .setProgress(100,total>0?(int)Math.min(100,done*100/total):0,total<=0).build();
    }
    @Override public void onCreate(){super.onCreate();
        getSystemService(NotificationManager.class).createNotificationChannel(new NotificationChannel(CHANNEL,"Atualizações do aplicativo",NotificationManager.IMPORTANCE_LOW));
        startForeground(NOTICE,notice());StationAppUpdater.observe(refresh);
    }
    @Override public int onStartCommand(Intent intent,int flags,int id){
        if(!started){started=true;if(StationAppUpdater.busy)StationAppUpdater.run(this);else finishJob();}
        return START_NOT_STICKY;
    }
    void finishJob(){stopForeground(true);stopSelf();}
    @Override public void onDestroy(){StationAppUpdater.forget(refresh);super.onDestroy();}
    @Override public IBinder onBind(Intent intent){return null;}
}
