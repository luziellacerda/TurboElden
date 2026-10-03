package org.emulationstation.frontend.station;
import java.nio.file.Path;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
/** Four actual IO workers, immediate refill and cancellation separate from unavailable artwork. */
public final class StationCoverQueue implements AutoCloseable {
 public static final int SUCCESS=0,CANCELLED=1,TRANSIENT=2,MISSING=3,RATE_LIMITED=4,AUTH_DENIED=5;
 public interface Loader {Path load(String itemId,StationApi.Cancellation cancellation)throws Exception;}
 public interface Listener {void complete(String itemId,Path path,int result,long retryMillis);}
 private final Loader loader;private final Listener listener;
 private final ConcurrentHashMap<String,Task> requests=new ConcurrentHashMap<>();
 private final ThreadPoolExecutor workers=new ThreadPoolExecutor(4,4,10,TimeUnit.SECONDS,new ArrayBlockingQueue<Runnable>(32),r->{Thread t=new Thread(r,"Station-covers");t.setDaemon(true);return t;});
 private volatile boolean foreground=true;
 private final Object publication=new Object();private volatile long generation;
 public StationCoverQueue(Loader loader,Listener listener){this.loader=loader;this.listener=listener;workers.allowCoreThreadTimeOut(true);}
 private final class Task implements Runnable {
  final String id;final StationApi.Cancellation cancel=new StationApi.Cancellation();final AtomicBoolean completed=new AtomicBoolean();
  final long startedGeneration;
  Task(String id){this.id=id;this.startedGeneration=generation;}
  void finish(Path path,int result,long delay){if(completed.compareAndSet(false,true)){synchronized(publication){
   requests.remove(id,this);boolean stale=startedGeneration!=generation;listener.complete(id,stale?null:path,stale?CANCELLED:result,stale?0:delay);
  }}}
  @Override public void run(){
   try{cancel.check();if(!foreground)throw new java.io.InterruptedIOException();Path path=loader.load(id,cancel);cancel.check();if(path==null)throw new java.io.IOException("Missing cover path");finish(path,SUCCESS,0);}
   catch(Exception error){
    if(cancel.cancelled()||!foreground){finish(null,CANCELLED,0);return;}
    StationDiagnostics.record(StationDiagnostics.Event.COVER_FAILED,StationDiagnostics.status(error),1);
    if(error instanceof StationCoverStore.Deferred){StationCoverStore.Deferred delayed=(StationCoverStore.Deferred)error;finish(null,delayed.rateLimited?RATE_LIMITED:MISSING,delayed.retryMillis);}
    else if(error instanceof StationApi.Failure){StationApi.Failure failure=(StationApi.Failure)error;
     if(failure.status==429)finish(null,RATE_LIMITED,failure.retryAfterMillis>0?failure.retryAfterMillis:60000);
     else if(failure.status==404)finish(null,MISSING,60000);
     else if(failure.sessionDenied())finish(null,AUTH_DENIED,5000);
     else finish(null,TRANSIENT,2000);
    }else finish(null,TRANSIENT,2000);
   }
  }
 }
 public void request(String id){synchronized(publication){
  if(!foreground){listener.complete(id,null,CANCELLED,0);return;}
  Task task=new Task(id);if(requests.putIfAbsent(id,task)!=null)return;
  if(!foreground){task.cancel.cancel();task.finish(null,CANCELLED,0);return;}
  try{workers.execute(task);}catch(RejectedExecutionException full){task.finish(null,TRANSIENT,250);}
 }}
 public void setForeground(boolean visible){foreground=visible;if(!visible)for(Task task:requests.values()){
  task.cancel.cancel();if(workers.remove(task))task.finish(null,CANCELLED,0);
 }}
 /** Cancel results from a previous catalog before publishing its replacement. */
 public void invalidate(){synchronized(publication){generation++;}for(Task task:requests.values()){
  task.cancel.cancel();if(workers.remove(task))task.finish(null,CANCELLED,0);
 }}
 public int activeCount(){return requests.size();}
 @Override public void close(){setForeground(false);workers.shutdown();}
}
