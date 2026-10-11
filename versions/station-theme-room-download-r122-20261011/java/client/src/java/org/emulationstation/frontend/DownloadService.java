package org.emulationstation.frontend;
import android.app.*;
import android.content.*;
import android.os.*;
import java.util.*;
import org.emulationstation.frontend.auth.LoginActivity;
/** A foreground service exists only while a Station job is active. No idle polling or Wi-Fi performance lock. */
public final class DownloadService extends Service {
 private static final String CHANNEL="downloads";
 private static final int NOTICE=7001;
 private static final Handler MAIN=new Handler(Looper.getMainLooper());
 private static final Map<String,Job> ACTIVE=new LinkedHashMap<>();
 private static DownloadService instance;
 private static boolean requested;
 private PowerManager.WakeLock wake;
 private long lastUpdate;
 private static final class Job {String name,message;long done,total;Job(String name,long done,long total,String message){this.name=name;this.done=done;this.total=total;this.message=message;}}
 public static void changed(Context context,String id,String name,boolean active,long done,long total,String message,int result){
  MAIN.post(()->{
   if(active)ACTIVE.put(id,new Job(name,done,total,message));else ACTIVE.remove(id);
   if(ACTIVE.isEmpty()){
    if(instance!=null)instance.stopSelf();requested=false;
   }else if(instance!=null){instance.updateWake();instance.update(false);}
   else if(!requested){requested=true;try{context.startForegroundService(new Intent(context,DownloadService.class));}catch(RuntimeException denied){requested=false;}}
  });
 }
 @Override public void onCreate(){
  super.onCreate();instance=this;requested=false;
  NotificationManager manager=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);
  if(manager!=null)manager.createNotificationChannel(new NotificationChannel(CHANNEL,"Downloads",NotificationManager.IMPORTANCE_LOW));
  PowerManager power=(PowerManager)getSystemService(POWER_SERVICE);
  if(power!=null){wake=power.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"TurboStations:download");wake.setReferenceCounted(false);}
 }
 @Override public int onStartCommand(Intent intent,int flags,int startId){
  updateWake();Notification notice=notification();if(Build.VERSION.SDK_INT>=29)startForeground(NOTICE,notice,1);else startForeground(NOTICE,notice);
  if(ACTIVE.isEmpty())stopSelf();return START_NOT_STICKY;
 }
 private void updateWake(){
  if(wake==null)return;boolean busy=false;
  for(Job j:ACTIVE.values())if(j.message.equals("Baixando")||j.message.equals("Preparando")||j.message.equals("Aguardando autorização")){busy=true;break;}
  if(busy&&!wake.isHeld())wake.acquire(6*60*60*1000L);else if(!busy&&wake.isHeld())wake.release();
 }
 private void update(boolean force){long now=SystemClock.elapsedRealtime();if(!force&&now-lastUpdate<1000)return;lastUpdate=now;
  NotificationManager manager=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);if(manager!=null)manager.notify(NOTICE,notification());
 }
 private Notification notification(){
  long done=0,total=0;boolean known=true;String name="Preparando download",message="Aguarde";
  for(Job job:ACTIVE.values()){done+=job.done;if(job.total<1)known=false;else total+=job.total;name=job.name;message=job.message;}
  int percent=known&&total>0?(int)Math.min(100,(done*100)/total):0;
  Intent open=new Intent(this,LoginActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
  PendingIntent pending=PendingIntent.getActivity(this,0,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
  return new Notification.Builder(this,CHANNEL).setSmallIcon(android.R.drawable.stat_sys_download)
   .setContentTitle(ACTIVE.size()>1?ACTIVE.size()+" jogos":name).setContentText(message+(known?" "+percent+"%":""))
   .setProgress(100,percent,!known).setOnlyAlertOnce(true).setOngoing(true).setContentIntent(pending).build();
 }
 @Override public void onDestroy(){if(wake!=null&&wake.isHeld())wake.release();if(instance==this)instance=null;requested=false;super.onDestroy();}
 @Override public IBinder onBind(Intent intent){return null;}
}
