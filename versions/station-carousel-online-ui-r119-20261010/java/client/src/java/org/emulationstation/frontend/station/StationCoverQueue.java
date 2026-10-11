package org.emulationstation.frontend.station;

import java.io.InterruptedIOException;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * One global cover IO worker. Visible requests always preempt the optional
 * post-publication cache completion pass. Game download workers are separate.
 */
public final class StationCoverQueue implements AutoCloseable {
 public static final int SUCCESS=0,CANCELLED=1,TRANSIENT=2,MISSING=3,RATE_LIMITED=4,AUTH_DENIED=5;
 private static final int MAX_PREFETCH_ITEMS=4096;
 private static final long MAX_RATE_DELAY_MS=86400000L;
 private static final long QUIESCE_TIMEOUT_MS=5000L;
 public interface Loader {Path load(String itemId,StationApi.Cancellation cancellation)throws Exception;}
 public interface Listener {void complete(String itemId,Path path,int result,long retryMillis);}
 public interface Work {
  /** Runs on the sole cover worker, after the exact path is available. */
  void process(Path path,StationApi.Cancellation cancellation)throws Exception;
  /** Runs on the cover worker for cancellation or failure. */
  default void failed(int result,long retryMillis){}
 }
 public interface Handle {void cancel();}
 /** One aggregate line per pass. It must never contain item IDs or paths. */
 public interface PassListener {void complete(String diagnostics);}

 private final Loader loader;private final Listener listener;private final PassListener passListener;
 private final ConcurrentHashMap<String,Task> requests=new ConcurrentHashMap<>();
 private final LinkedBlockingDeque<Runnable> workQueue=new LinkedBlockingDeque<Runnable>(9);
 private final ThreadPoolExecutor workers=new ThreadPoolExecutor(1,1,10,TimeUnit.SECONDS,
     workQueue,r->{Thread t=new Thread(r,"Station-covers");t.setDaemon(true);return t;});
 private final ScheduledExecutorService delays=Executors.newSingleThreadScheduledExecutor(r->{
  Thread t=new Thread(r,"Station-cover-delay");t.setDaemon(true);return t;
 });
 private volatile boolean foreground=true;
 private final Object publication=new Object();private volatile long generation;
 private final ArrayDeque<String> prefetchPending=new ArrayDeque<>();
 private final HashSet<String> prefetchMembers=new HashSet<>();
 private final ArrayDeque<Task> deferredNatives=new ArrayDeque<>();
 private final ArrayDeque<Task> deferredWorks=new ArrayDeque<>();
 private Task prefetchTask;private ScheduledFuture<?> prefetchWake;private int runningIo;
 private long passGeneration,passSerial;private int passPlanned,passStarted,passSucceeded,passCancelled;
 private int passTransient,passMissing,passRateLimited,passAuthDenied,passVisiblePreemptions;
 private boolean passOpen,rateLimitResumeUsed,catalogPreparing;
 private long rateLimitResumeAtNanos;
 private long workSequence;
 private Task highPriorityWork;

 public StationCoverQueue(Loader loader,Listener listener){this(loader,listener,diagnostics->{});}
 public StationCoverQueue(Loader loader,Listener listener,PassListener passListener){
  this.loader=Objects.requireNonNull(loader,"loader");
  this.listener=Objects.requireNonNull(listener,"listener");
  this.passListener=Objects.requireNonNull(passListener,"passListener");
  workers.allowCoreThreadTimeOut(true);
 }

 private final class Task implements Runnable {
  final String key,id;final boolean prefetch,notifyNative,highPriority;final Work work;
  final StationApi.Cancellation cancel=new StationApi.Cancellation();
  final AtomicBoolean completed=new AtomicBoolean();long startedGeneration;final long startedPass;
  Task(String key,String id,boolean prefetch,boolean notifyNative,Work work,boolean highPriority){
   this.key=key;this.id=id;this.prefetch=prefetch;this.notifyNative=notifyNative;this.work=work;this.highPriority=highPriority;
   this.startedGeneration=generation;this.startedPass=prefetch?passSerial:0;
  }
  void finish(Path path,int result,long delay){
   String passReport=null;
   synchronized(publication){
    if(!completed.compareAndSet(false,true))return;
    // Explicit online work is owned by its lifecycle Handle.  Carousel catalog
    // replacement must not invalidate a room cover that was requested while
    // ESActivity paused to open StationRoomsActivity.
    boolean stale=startedGeneration!=generation;
    if(prefetch){
     if(prefetchTask==this)prefetchTask=null;
     if(startedPass!=passSerial){schedulePrefetchLocked();}
     else passReport=completePrefetchLocked(this,stale?CANCELLED:result,stale?0:delay,stale);
    }else{
     requests.remove(key,this);
     if(highPriorityWork==this)highPriorityWork=null;
     int deliveredResult=stale?CANCELLED:result;long deliveredDelay=stale?0:delay;
     if(notifyNative)listener.complete(id,stale?null:path,deliveredResult,deliveredDelay);
     if(work!=null&&deliveredResult!=SUCCESS)try{work.failed(deliveredResult,deliveredDelay);}catch(RuntimeException ignored){}
     if(!stale){
      if(result==SUCCESS)removePendingLocked(id);
      schedulePrefetchLocked();
     }
    }
    publication.notifyAll();
   }
   notifyPass(passReport);
  }
  @Override public void run(){
   Path path=null;int result=SUCCESS;long delay=0;boolean enteredIo=false;
   try{
    cancel.check();if(!admitted())throw new InterruptedIOException("Cover queue is not available");
    synchronized(publication){
     cancel.check();if(completed.get()||startedGeneration!=generation||!admitted())throw new InterruptedIOException("Stale cover request");
     runningIo++;enteredIo=true;if(prefetch)passStarted++;
    }
    path=loader.load(id,cancel);if(!prefetch)cancel.check();if(path==null)throw new java.io.IOException("Missing cover path");
    if(work!=null)work.process(path,cancel);if(!prefetch)cancel.check();
   }catch(Exception error){
    path=null;
    boolean concreteRate=prefetch&&((error instanceof StationCoverStore.Deferred&&((StationCoverStore.Deferred)error).rateLimited)||
        (error instanceof StationApi.Failure&&((StationApi.Failure)error).status==429));
    if(!concreteRate&&(cancel.cancelled()||startedGeneration!=generation||(work==null&&!foreground)))result=CANCELLED;
    else{
     StationDiagnostics.record(StationDiagnostics.Event.COVER_FAILED,StationDiagnostics.status(error),1);
     if(error instanceof StationCoverStore.Deferred){StationCoverStore.Deferred deferred=(StationCoverStore.Deferred)error;
      result=deferred.rateLimited?RATE_LIMITED:MISSING;delay=deferred.retryMillis;
     }else if(error instanceof StationApi.Failure){StationApi.Failure failure=(StationApi.Failure)error;
      if(failure.status==429){result=RATE_LIMITED;delay=failure.retryAfterMillis>0?failure.retryAfterMillis:60000;}
      else if(failure.status==404){result=MISSING;delay=60000;}
      else if(failure.sessionDenied()){result=AUTH_DENIED;delay=5000;}
      else{result=TRANSIENT;delay=2000;}
     }else{result=TRANSIENT;delay=2000;}
    }
   }finally{
    if(enteredIo)synchronized(publication){runningIo--;publication.notifyAll();}
   }
   finish(path,result,delay);
  }
  private boolean admitted(){return !catalogPreparing&&(work!=null||foreground);}
 }

 /** Visible selection: atomically cancel/remove low-priority work first. */
 public void request(String id){
  Task visible;
  synchronized(publication){
   if(!foreground){listener.complete(id,null,CANCELLED,0);return;}
   String key="native:"+id;visible=new Task(key,id,false,true,null,false);if(requests.putIfAbsent(key,visible)!=null)return;
   if(prefetchTask!=null){passVisiblePreemptions++;cancelPrefetchTaskLocked(true);}
   // While the direct initial warm owner is active, retain one request per
   // identity without emitting per-frame CANCELLED results back to JNI.
   if(catalogPreparing){deferredNatives.addLast(visible);return;}
   if(!foreground){visible.cancel.cancel();visible.finish(null,CANCELLED,0);return;}
   submitNativeLocked(visible);
  }
 }

 private void submitNativeLocked(Task task){
  if(task.completed.get())return;
  if(!offerFrontLocked(task,true))task.finish(null,TRANSIENT,250);
 }

 /** Online/UI artwork uses the same worker for path IO and bitmap decode. */
 public Handle requestWork(String id,Work work){return requestWork(id,work,false);}
 /** A hero replaces an older hero and enters ahead of visible thumbnails. */
 public Handle requestWork(String id,Work work,boolean highPriority){
  Objects.requireNonNull(work,"work");final Task visible;
  synchronized(publication){
   String key="work:"+(++workSequence);visible=new Task(key,id,false,false,work,highPriority);
   if(highPriority&&highPriorityWork!=null&&!highPriorityWork.completed.get())cancelVisibleLocked(highPriorityWork);
   requests.put(key,visible);
   if(highPriority)highPriorityWork=visible;
   if(prefetchTask!=null){passVisiblePreemptions++;cancelPrefetchTaskLocked(true);}
   // The R115 synchronous warm pass runs off this executor.  Keep online work
   // pending during that short preparation window instead of starting a second
   // cover IO or returning a permanent blank.  replaceCatalog/endPreparation
   // submit it after the warm owner has released the lane.
   if(catalogPreparing){
    if(deferredWorks.size()>=9){
     Task displaced=highPriority?removeLastLowDeferredLocked():null;
     if(displaced!=null){displaced.cancel.cancel();displaced.finish(null,TRANSIENT,250);}
     if(deferredWorks.size()>=9)visible.finish(null,TRANSIENT,250);
     else if(highPriority)deferredWorks.addFirst(visible);else deferredWorks.addLast(visible);
    }else if(highPriority)deferredWorks.addFirst(visible);else deferredWorks.addLast(visible);
   }else submitWorkLocked(visible);
  }
  return ()->cancelVisible(visible);
 }

 private void cancelVisible(Task task){synchronized(publication){
  cancelVisibleLocked(task);
 }}
 private void cancelVisibleLocked(Task task){
  if(task==null||task.completed.get())return;task.cancel.cancel();
  if(deferredWorks.remove(task)||workers.remove(task))task.finish(null,CANCELLED,0);
 }

 private Task removeLastLowDeferredLocked(){
  for(Iterator<Task> iterator=deferredWorks.descendingIterator();iterator.hasNext();){Task candidate=iterator.next();if(!candidate.highPriority){iterator.remove();return candidate;}}
  return null;
 }

 private void submitWorkLocked(Task task){
  if(task.completed.get())return;
  if(!task.highPriority){try{workers.execute(task);}catch(RejectedExecutionException full){task.finish(null,TRANSIENT,250);}return;}
  if(!offerFrontLocked(task,false))task.finish(null,TRANSIENT,250);
 }
 private boolean offerFrontLocked(Task task,boolean nativePriority){
  if(workers.isShutdown())return false;
  if(!workQueue.offerFirst(task)){
   Task displaced=null;
   for(Iterator<Runnable> iterator=workQueue.descendingIterator();iterator.hasNext();){
    Runnable queued=iterator.next();if(!(queued instanceof StationCoverQueue.Task))continue;Task candidate=(Task)queued;
    if(candidate.highPriority)continue;
    // Native selection displaces only optional UI artwork. A hero may also
    // displace an older native reveal request if the surfaces ever overlap.
    if(nativePriority&&candidate.work==null)continue;
    iterator.remove();displaced=candidate;break;
   }
   if(displaced!=null){displaced.cancel.cancel();displaced.finish(null,TRANSIENT,250);}
   if(!workQueue.offerFirst(task))return false;
  }
  workers.prestartCoreThread();return true;
 }
 private void submitDeferredWorksLocked(){
  while(!catalogPreparing&&!deferredWorks.isEmpty()){
   Task task=deferredWorks.removeFirst();task.startedGeneration=generation;submitWorkLocked(task);
  }
 }
 private void submitDeferredNativesLocked(){
  while(!catalogPreparing&&foreground&&!deferredNatives.isEmpty()){
   Task task=deferredNatives.removeFirst();task.startedGeneration=generation;submitNativeLocked(task);
  }
 }

 /**
  * Starts one low-priority, catalog-generation-bound pass. Only one task is
  * admitted at a time, so the executor queue is never filled with thousands
  * of cache misses. Successes persist in StationCoverStore and restarts skip
  * them through the exact coverId+revision canonical key.
  */
 public void prefetchCatalog(Collection<String> itemIds){
  String oldReport;
  synchronized(publication){
   oldReport=finishPassLocked("replaced");cancelPrefetchLocked(false);clearPrefetchLocked();passSerial++;
   // Keep the cold plan even when catalog publication finishes while
   // ESActivity is paused for an online screen. Execution still waits for
   // foreground in schedulePrefetchLocked().
   if(itemIds!=null&&!catalogPreparing)for(String id:itemIds){
    if(id==null||id.isEmpty()||prefetchMembers.contains(id))continue;
    if(prefetchPending.size()>=MAX_PREFETCH_ITEMS)break;
    prefetchPending.addLast(id);prefetchMembers.add(id);
   }
   if(!prefetchPending.isEmpty()){
    passOpen=true;passGeneration=generation;passPlanned=prefetchPending.size();
    passStarted=passSucceeded=passCancelled=passTransient=passMissing=passRateLimited=passAuthDenied=passVisiblePreemptions=0;
    rateLimitResumeUsed=false;schedulePrefetchLocked();
   }
  }
  notifyPass(oldReport);
 }

 private void schedulePrefetchLocked(){
  if(!passOpen||!foreground||catalogPreparing||passGeneration!=generation||prefetchTask!=null||prefetchWake!=null||!requests.isEmpty())return;
  long rateWait=rateLimitResumeAtNanos-System.nanoTime();
  if(rateWait>0){scheduleRateWakeLocked(rateWait);return;}
  rateLimitResumeAtNanos=0;
  String id=prefetchPending.pollFirst();if(id==null){notifyPass(finishPassLocked("complete"));return;}
  prefetchMembers.remove(id);Task task=new Task("prefetch:"+passSerial+":"+passStarted,id,true,false,null,false);prefetchTask=task;
  try{workers.execute(task);}catch(RejectedExecutionException full){
   prefetchTask=null;prefetchPending.addFirst(id);prefetchMembers.add(id);
   notifyPass(finishPassLocked("executor-rejected"));
  }
 }

 /** Caller holds publication. Return an optional aggregate pass report. */
 private String completePrefetchLocked(Task task,int result,long retryMillis,boolean stale){
  if(!passOpen)return null;
  if(stale||passGeneration!=generation){passCancelled++;return finishPassLocked("cancelled");}
  if(result==RATE_LIMITED){
   passRateLimited++;
   if(rateLimitResumeUsed)return finishPassLocked("rate-limit-repeat");
   rateLimitResumeUsed=true;
   if(!prefetchMembers.contains(task.id)){prefetchPending.addFirst(task.id);prefetchMembers.add(task.id);}
   long wait=Math.max(1,Math.min(MAX_RATE_DELAY_MS,retryMillis>0?retryMillis:60000));
   rateLimitResumeAtNanos=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(wait);
   scheduleRateWakeLocked(TimeUnit.MILLISECONDS.toNanos(wait));
   return null;
  }
  if(!foreground||catalogPreparing){
   passCancelled++;if(!prefetchMembers.contains(task.id)){prefetchPending.addFirst(task.id);prefetchMembers.add(task.id);}return null;
  }
  if(result==SUCCESS){passSucceeded++;removePendingLocked(task.id);schedulePrefetchLocked();return null;}
  if(result==CANCELLED){
   passCancelled++;
   // A visible request preempts low priority work. Keep this identity at the
   // front and resume only after all visible work finishes.
   if(!prefetchMembers.contains(task.id)){prefetchPending.addFirst(task.id);prefetchMembers.add(task.id);}
   schedulePrefetchLocked();return null;
  }
  if(result==MISSING)passMissing++;
  else if(result==AUTH_DENIED)passAuthDenied++;
  else passTransient++;
  // Offline/network, 401/403 and 404 end this bounded pass. A later catalog
  // publication or app start constructs a fresh pass from the remaining cold
  // exact identities. There is no immediate retry loop.
  return finishPassLocked(result==MISSING?"missing":result==AUTH_DENIED?"auth":"offline-or-transient");
 }

 private void cancelPrefetchTaskLocked(boolean preserveIdentity){
  Task task=prefetchTask;if(task==null)return;task.cancel.cancel();
  if(preserveIdentity&&!prefetchMembers.contains(task.id)){prefetchPending.addFirst(task.id);prefetchMembers.add(task.id);}
  if(workers.remove(task)){prefetchTask=null;task.finish(null,CANCELLED,0);}
 }
 private void cancelPrefetchLocked(boolean preserveIdentity){
  if(prefetchWake!=null){prefetchWake.cancel(false);prefetchWake=null;}
  cancelPrefetchTaskLocked(preserveIdentity);
 }
 private void scheduleRateWakeLocked(long waitNanos){
  if(prefetchWake!=null||!foreground||catalogPreparing||!passOpen)return;
  final long expectedGeneration=generation;
  prefetchWake=delays.schedule(()->{
   synchronized(publication){
    prefetchWake=null;
    if(passOpen&&foreground&&!catalogPreparing&&passGeneration==generation&&generation==expectedGeneration)schedulePrefetchLocked();
   }
  },Math.max(1,waitNanos),TimeUnit.NANOSECONDS);
 }
 private void removePendingLocked(String id){
  if(!prefetchMembers.remove(id))return;
  for(Iterator<String> iterator=prefetchPending.iterator();iterator.hasNext();)if(iterator.next().equals(id)){iterator.remove();break;}
 }
 private void clearPrefetchLocked(){prefetchPending.clear();prefetchMembers.clear();rateLimitResumeUsed=false;rateLimitResumeAtNanos=0;}
 private String finishPassLocked(String reason){
  if(!passOpen)return null;passOpen=false;
  if(prefetchWake!=null){prefetchWake.cancel(false);prefetchWake=null;}
  clearPrefetchLocked();
  return "reason="+reason+" planned="+passPlanned+" started="+passStarted+
      " succeeded="+passSucceeded+" cancelled="+passCancelled+
      " transient="+passTransient+" missing="+passMissing+
      " rateLimited="+passRateLimited+" authDenied="+passAuthDenied+
      " visiblePreemptions="+passVisiblePreemptions;
 }
 private void notifyPass(String report){if(report!=null)try{passListener.complete(report);}catch(RuntimeException ignored){}}

 /**
  * Stops old-generation IO before the synchronous R115 preparation pass. This
  * is off the UI thread. The finite wait prevents a broken transport from
  * hanging catalog publication or overlapping a second cover IO.
  */
 public void quiesceForCatalog() throws InterruptedIOException {
  String report;long deadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(QUIESCE_TIMEOUT_MS);
  synchronized(publication){
   generation++;catalogPreparing=true;report=finishPassLocked("catalog-replaced");cancelPrefetchLocked(false);clearPrefetchLocked();
   Task[] visible=requests.values().toArray(new Task[0]);
   for(Task task:visible){task.cancel.cancel();if(workers.remove(task))task.finish(null,CANCELLED,0);}
   while(runningIo>0){
    long left=deadline-System.nanoTime();if(left<=0)throw new InterruptedIOException("Cover IO did not stop for catalog publication");
    try{TimeUnit.NANOSECONDS.timedWait(publication,left);}catch(InterruptedException interrupted){Thread.currentThread().interrupt();throw new InterruptedIOException("Catalog cover wait interrupted");}
   }
  }
  notifyPass(report);
 }

 /** Releases preparation admission if catalog preparation exits before publish. */
 public void endCatalogPreparation(){synchronized(publication){catalogPreparing=false;submitDeferredNativesLocked();submitDeferredWorksLocked();schedulePrefetchLocked();}}

 public void setForeground(boolean visible){
  String report=null;
  synchronized(publication){
   foreground=visible;
   if(!visible){
    if(prefetchWake!=null){prefetchWake.cancel(false);prefetchWake=null;}
    cancelPrefetchTaskLocked(true);
    Task[] active=requests.values().toArray(new Task[0]);
    for(Task task:active)if(task.notifyNative){
     // A native request retained behind the direct warm owner must remain
     // silent while ESActivity pauses; per-frame CANCELLED callbacks would
     // recreate the exact retry storm this admission gate prevents.
     if(catalogPreparing&&deferredNatives.contains(task))continue;
     task.cancel.cancel();if(deferredNatives.remove(task)||workers.remove(task))task.finish(null,CANCELLED,0);
    }
   }else{submitDeferredNativesLocked();submitDeferredWorksLocked();schedulePrefetchLocked();}
  }
  notifyPass(report);
 }

 /** Cancel results from a previous catalog before publishing its replacement. */
 public void invalidate(){replaceCatalog(()->{});}
 /**
  * Finish every old request before JNI clears its inbox. Active IO can unwind
  * later, but its atomic completion is already consumed by the generation.
  */
 public void replaceCatalog(Runnable publish){
  String report;
  synchronized(publication){
   generation++;report=finishPassLocked("catalog-replaced");cancelPrefetchLocked(false);clearPrefetchLocked();
   Task[] previous=requests.values().toArray(new Task[0]);
   for(Task task:previous)if(task.notifyNative&&!deferredNatives.contains(task)){
    task.cancel.cancel();workers.remove(task);task.finish(null,CANCELLED,0);
   }
   // Requests received behind the direct warm owner belong to the catalog
   // being published. Rebase them after the atomic publish. If ESActivity is
   // paused for an online screen, retain them silently until foreground=true.
   publish.run();catalogPreparing=false;submitDeferredNativesLocked();submitDeferredWorksLocked();
  }
  notifyPass(report);
 }
 /** Visible requests only; background completion must not starve catalog polling. */
 public int activeCount(){return requests.size();}
 @Override public void close(){
  synchronized(publication){
   foreground=false;catalogPreparing=false;
   cancelPrefetchLocked(false);finishPassLocked("closed");clearPrefetchLocked();
   Task[] active=requests.values().toArray(new Task[0]);
   for(Task task:active){task.cancel.cancel();deferredNatives.remove(task);deferredWorks.remove(task);if(workers.remove(task))task.finish(null,CANCELLED,0);}
  }
  workers.shutdownNow();delays.shutdownNow();
 }
}
