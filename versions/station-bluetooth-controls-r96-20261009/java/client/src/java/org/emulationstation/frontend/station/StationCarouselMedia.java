package org.emulationstation.frontend.station;

import android.app.*;
import android.os.*;
import android.media.*;
import java.io.*;
import java.nio.file.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Menu-only, one-at-a-time prefetch. Rendering consumes local files and never waits on HTTP. */
public final class StationCarouselMedia {
 private static final ExecutorService worker=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-menu-media");t.setDaemon(true);return t;});
 private static final AtomicBoolean queued=new AtomicBoolean();
 private static volatile boolean foreground=true,registered;
 private static volatile String preferred;
 private static volatile StationApi.Cancellation running;
 private static volatile StationMediaStore store;
 private static StationMediaCatalog catalog;
 private static long nextCatalog,nextAttempt;
 private StationCarouselMedia(){}
 private static synchronized StationMediaStore storage()throws Exception {
  if(store==null){StationAndroid app=StationAndroid.current();if(app==null)throw new IOException("Station not initialized");store=new StationMediaStore(app.privateFiles.resolve("station-v2/menu-media"));}
  return store;
 }
 public static void install(android.content.Context context){
  synchronized(StationCarouselMedia.class){if(registered)return;registered=true;}
  ((Application)context.getApplicationContext()).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   private boolean menu(Activity a){return a.getClass().getName().equals("org.emulationstation.frontend.ESActivity");}
   public void onActivityResumed(Activity a){setForeground(menu(a));}
   public void onActivityPaused(Activity a){if(menu(a))setForeground(false);}
   public void onActivityStopped(Activity a){}
   public void onActivityDestroyed(Activity a){}
   public void onActivityCreated(Activity a,Bundle b){}
   public void onActivityStarted(Activity a){}
   public void onActivitySaveInstanceState(Activity a,Bundle b){}
  });
 }
 public static void setForeground(boolean visible){foreground=visible;if(!visible)suspendTransfer();else tick();}
 public static void suspendTransfer(){StationApi.Cancellation cancel=running;if(cancel!=null)cancel.cancel();}
 /** Called only by the existing video worker, never the render/UI thread. */
 public static Path local(String asset)throws Exception {
  if(!StationMediaCatalog.safeAsset(asset))return null;preferred=asset;tick();return storage().cached(asset);
 }
 private static boolean allowed(){StationAndroid app=StationAndroid.current();return foreground&&app!=null&&app.coordinator.ready()&&app.api.available()&&StationFrontend.activeCount()==0;}
 public static void tick(){if(allowed()&&queued.compareAndSet(false,true))worker.execute(()->{try{sync();}finally{queued.set(false);}});}
 private static void sync(){
  if(!allowed()||SystemClock.elapsedRealtime()<nextAttempt)return;
  StationAndroid app=StationAndroid.current();StationApi.Cancellation cancel=new StationApi.Cancellation();running=cancel;
  try{
   StationMediaStore files=storage();
   if(catalog==null||SystemClock.elapsedRealtime()>=nextCatalog){
    StationMediaCatalog next;
    try(StationSessions.Lease lease=app.sessions.acquire(cancel)){next=app.api.mediaCatalog(lease.session,cancel);}
    if(catalog!=null&&next.revision<catalog.revision)throw new IOException("Media rollback refused");
    catalog=next;nextCatalog=SystemClock.elapsedRealtime()+300000;
   }
   while(allowed()){
    cancel.check();StationMediaCatalog.Entry wanted=catalog.items.get(preferred);preferred=null;
    if(wanted==null||files.contains(wanted)){wanted=null;for(StationMediaCatalog.Entry e:catalog.items.values())if(!files.contains(e)){wanted=e;break;}}
    if(wanted==null)return;
    final StationApi.Response response;
    // Release the session lease after authenticated headers, before streaming the body.
    try(StationSessions.Lease lease=app.sessions.acquire(cancel)){response=app.api.openMedia(lease.session,wanted,cancel);}
    try(StationApi.Response owned=response){files.publish(wanted,owned.body,cancel,StationCarouselMedia::validate);}
   }
  }catch(Exception unavailable){
   if(!cancel.cancelled()){
    nextAttempt=SystemClock.elapsedRealtime()+60000;
    if(unavailable instanceof StationApi.Failure){StationApi.Failure e=(StationApi.Failure)unavailable;
     if(e.retryAfterMillis>0)nextAttempt=SystemClock.elapsedRealtime()+Math.min(3600000,e.retryAfterMillis);
     if(e.status==404){catalog=null;nextCatalog=0;}
    }
    android.util.Log.i("StationMedia","Menu media update deferred; local media retained");
   }
  }finally{running=null;}
 }
 private static double frameRate(MediaFormat f){try{return f.getInteger(MediaFormat.KEY_FRAME_RATE);}catch(ClassCastException value){return f.getFloat(MediaFormat.KEY_FRAME_RATE);}}
 private static void validate(Path path)throws Exception {
  MediaExtractor extractor=new MediaExtractor();try{
   extractor.setDataSource(path.toString());if(extractor.getTrackCount()!=1)throw new IOException("Menu clip must have one video track and no audio");
   MediaFormat f=extractor.getTrackFormat(0);
   if(!"video/avc".equals(f.getString(MediaFormat.KEY_MIME))||f.getInteger(MediaFormat.KEY_WIDTH)!=720||f.getInteger(MediaFormat.KEY_HEIGHT)!=720
     ||!f.containsKey(MediaFormat.KEY_FRAME_RATE)||Math.abs(frameRate(f)-30)>0.01)
    throw new IOException("Menu clip must be H264 720x720 at 30 fps");
  }finally{extractor.release();}
 }
}
