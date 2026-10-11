package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Deterministic host proof for the one-lane visible/background cover queue. */
public final class StationCoverPrefetchTest {
 private static int checks;
 private static void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
 private static void await(CountDownLatch latch,String message)throws Exception{check(latch.await(5,TimeUnit.SECONDS),message);}

 public static void main(String[] args)throws Exception{
  visiblePreemptsWithoutParallelIo();
  terminalFailuresStopPass();
  retryAfterIsBounded();
  successfulPrefetchAfterLateCancelIsNotRepeated();
  heroReplacesStaleHeroAndJumpsThumbnails();
  nativeSelectionJumpsOptionalArtwork();
  lifecyclePreservesRetryAfter();
  lifecyclePausesAndResumes();
  backgroundPublicationRetainsColdPlan();
  catalogPreparationOwnsTheLane();
  onlineWaitsForCatalogOwnerAcrossCarouselPause();
  catalogReplaceRetainsPausedDeferredNative();
  onlineDecodeUsesTheSameLane();
  System.out.println("PASS "+checks+" one-lane cover prefetch checks");
 }

 private static void visiblePreemptsWithoutParallelIo()throws Exception{
  AtomicInteger active=new AtomicInteger(),maximum=new AtomicInteger(),bgAttempts=new AtomicInteger(),nativeEvents=new AtomicInteger();
  List<String> order=Collections.synchronizedList(new ArrayList<>());
  CountDownLatch firstBg=new CountDownLatch(1),visibleDone=new CountDownLatch(1),passDone=new CountDownLatch(1);
  AtomicReference<String> report=new AtomicReference<>();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   int concurrent=active.incrementAndGet();maximum.accumulateAndGet(concurrent,Math::max);order.add(id);
   try{
    if(id.equals("background1")&&bgAttempts.incrementAndGet()==1){firstBg.countDown();for(;;){cancel.check();Thread.sleep(5);}}
    return Paths.get(id+".img");
   }finally{active.decrementAndGet();}
  },(id,path,result,delay)->{nativeEvents.incrementAndGet();if(id.equals("visible01")&&result==StationCoverQueue.SUCCESS)visibleDone.countDown();},text->{report.set(text);passDone.countDown();})){
   queue.prefetchCatalog(Arrays.asList("background1","background2"));await(firstBg,"Background pass entered");
   queue.request("visible01");await(visibleDone,"Visible request completed after preemption");await(passDone,"Background pass resumed and completed");
   check(maximum.get()==1,"Cover loader never overlaps IO");
   check(order.equals(Arrays.asList("background1","visible01","background1","background2")),"Visible request runs before resumed background work: "+order);
   check(nativeEvents.get()==1,"Background results stay out of the native visible inbox");
   check(report.get().contains("reason=complete")&&report.get().contains("visiblePreemptions=1"),"Aggregate pass report records preemption only");
  }
 }

 private static void terminalFailuresStopPass()throws Exception{
  assertStops(404,"missing");assertStops(401,"auth");assertStops(0,"offline-or-transient");
 }
 private static void assertStops(int status,String reason)throws Exception{
  AtomicInteger calls=new AtomicInteger();CountDownLatch stopped=new CountDownLatch(1);AtomicReference<String> report=new AtomicReference<>();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   calls.incrementAndGet();if(status==0)throw new StationApi.Offline();throw new StationApi.Failure(status,"TEST");
  },(id,path,result,delay)->{},text->{report.set(text);stopped.countDown();})){
   queue.prefetchCatalog(Arrays.asList("failure01","mustNotRun"));await(stopped,"Terminal background failure reported");Thread.sleep(80);
   check(calls.get()==1,"Status "+status+" ends this pass without looping");
   check(report.get().contains("reason="+reason),"Failure reason is aggregate and classified");
   check(!report.get().contains("failure01")&&!report.get().contains("mustNotRun"),"Diagnostics contain no item identities");
  }
 }

 private static void retryAfterIsBounded()throws Exception{
  AtomicInteger calls=new AtomicInteger();CountDownLatch done=new CountDownLatch(1);long started=System.nanoTime();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   if(calls.incrementAndGet()==1)throw new StationApi.Failure(429,"RATE",120);return Paths.get("rate.img");
  },(id,path,result,delay)->{},text->done.countDown())){
   queue.prefetchCatalog(Collections.singletonList("rate0001"));
   Thread.sleep(50);check(calls.get()==1,"429 has no immediate retry");await(done,"One delayed 429 retry completed pass");
   check(calls.get()==2,"429 performs exactly one delayed retry");
   check(TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-started)>=100,"Retry-After delay is respected");
  }
  AtomicInteger repeated=new AtomicInteger();CountDownLatch stopped=new CountDownLatch(1);AtomicReference<String> report=new AtomicReference<>();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{repeated.incrementAndGet();throw new StationApi.Failure(429,"RATE",20);},
      (id,path,result,delay)->{},text->{report.set(text);stopped.countDown();})){
   queue.prefetchCatalog(Collections.singletonList("rate0002"));await(stopped,"Repeated 429 stops pass");Thread.sleep(80);
   check(repeated.get()==2,"Repeated 429 cannot create an unbounded loop");
   check(report.get().contains("reason=rate-limit-repeat"),"Repeated rate limit is diagnosed aggregately");
  }
 }

 private static void lifecyclePausesAndResumes()throws Exception{
  AtomicInteger attempts=new AtomicInteger();CountDownLatch entered=new CountDownLatch(1),cancelled=new CountDownLatch(1),done=new CountDownLatch(1);
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   if(attempts.incrementAndGet()==1){entered.countDown();try{for(;;){cancel.check();Thread.sleep(5);}}finally{cancelled.countDown();}}
   return Paths.get(id+".img");
  },(id,path,result,delay)->{},text->{if(text.contains("reason=complete"))done.countDown();})){
   queue.prefetchCatalog(Arrays.asList("paused01","paused02"));await(entered,"Lifecycle fixture entered");
   queue.setForeground(false);await(cancelled,"Background cancels active cover IO");Thread.sleep(30);
   check(attempts.get()==1,"No cover starts while backgrounded");queue.setForeground(true);await(done,"Foreground resumes retained cold plan");
   check(attempts.get()==3,"Cancelled identity and following identity complete once after resume");
  }
 }

 private static void backgroundPublicationRetainsColdPlan()throws Exception{
  AtomicInteger calls=new AtomicInteger();CountDownLatch complete=new CountDownLatch(1);
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{calls.incrementAndGet();return Paths.get(id+".img");},
      (id,path,result,delay)->{},text->{if(text.contains("reason=complete"))complete.countDown();})){
   queue.setForeground(false);queue.prefetchCatalog(Arrays.asList("coldWhileOnline1","coldWhileOnline2"));Thread.sleep(60);
   check(calls.get()==0,"A catalog published in background retains cold covers without starting IO");
   queue.setForeground(true);await(complete,"Foreground resumes the cold plan retained by background publication");
   check(calls.get()==2,"Each retained cold identity is fetched exactly once after resume");
  }
 }

 private static void successfulPrefetchAfterLateCancelIsNotRepeated()throws Exception{
  AtomicInteger backgroundCalls=new AtomicInteger();CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1),visibleDone=new CountDownLatch(1),passDone=new CountDownLatch(1);
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   if(id.equals("lateCancel")){backgroundCalls.incrementAndGet();entered.countDown();release.await(5,TimeUnit.SECONDS);return Paths.get("late.img");}
   return Paths.get("visible.img");
  },(id,path,result,delay)->{if(id.equals("visibleLate")&&result==StationCoverQueue.SUCCESS)visibleDone.countDown();},text->{if(text.contains("reason=complete"))passDone.countDown();})){
   queue.prefetchCatalog(Collections.singletonList("lateCancel"));await(entered,"Late-cancel fixture entered");
   queue.request("visibleLate");release.countDown();await(visibleDone,"Visible request follows completed late-cancel load");await(passDone,"Late-cancel pass completes");
   check(backgroundCalls.get()==1,"Successful loader completion removes any identity preserved by preemption");
  }
 }

 private static void heroReplacesStaleHeroAndJumpsThumbnails()throws Exception{
  List<String> processed=Collections.synchronizedList(new ArrayList<>());CountDownLatch firstEntered=new CountDownLatch(1),release=new CountDownLatch(1),newHeroDone=new CountDownLatch(1),oldHeroCancelled=new CountDownLatch(1);
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->Paths.get(id+".img"),(id,path,result,delay)->{})){
   queue.requestWork("thumb0",new StationCoverQueue.Work(){public void process(Path path,StationApi.Cancellation cancel)throws Exception{processed.add("thumb0");firstEntered.countDown();release.await(5,TimeUnit.SECONDS);}});
   await(firstEntered,"First thumbnail owns lane");
   for(int i=1;i<8;i++){final String id="thumb"+i;queue.requestWork(id,new StationCoverQueue.Work(){public void process(Path path,StationApi.Cancellation cancel){processed.add(id);}});}
   queue.requestWork("oldHero",new StationCoverQueue.Work(){public void process(Path path,StationApi.Cancellation cancel){processed.add("oldHero");}public void failed(int result,long retry){if(result==StationCoverQueue.CANCELLED)oldHeroCancelled.countDown();}},true);
   queue.requestWork("newHero",new StationCoverQueue.Work(){public void process(Path path,StationApi.Cancellation cancel){processed.add("newHero");newHeroDone.countDown();}},true);
   await(oldHeroCancelled,"New hero cancels queued stale hero");release.countDown();await(newHeroDone,"New hero runs as next cover after active thumbnail");
   check(processed.size()>=2&&processed.get(0).equals("thumb0")&&processed.get(1).equals("newHero"),"Hero enters ahead of queued thumbnails: "+processed);
   check(!processed.contains("oldHero"),"Stale hero is never decoded");
  }
 }

 private static void lifecyclePreservesRetryAfter()throws Exception{
  AtomicInteger calls=new AtomicInteger();CountDownLatch entered=new CountDownLatch(1),release429=new CountDownLatch(1),done=new CountDownLatch(1);long[] resumedAt={0};
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   int call=calls.incrementAndGet();if(call==1){entered.countDown();release429.await(5,TimeUnit.SECONDS);throw new StationApi.Failure(429,"RATE",220);}
   resumedAt[0]=System.nanoTime();return Paths.get("rate-resume.img");
  },(id,path,result,delay)->{},text->{if(text.contains("reason=complete"))done.countDown();})){
   long start=System.nanoTime();queue.prefetchCatalog(Collections.singletonList("rateLifecycle"));await(entered,"Rate lifecycle fixture entered");
   queue.setForeground(false);release429.countDown();Thread.sleep(50);queue.setForeground(true);Thread.sleep(80);
   check(calls.get()==1,"Foreground resume cannot bypass preserved Retry-After");await(done,"Prefetch resumes once Retry-After expires");
   check(calls.get()==2&&TimeUnit.NANOSECONDS.toMillis(resumedAt[0]-start)>=190,"Retry-After survives lifecycle cancellation race");
  }
 }

 private static void nativeSelectionJumpsOptionalArtwork()throws Exception{
  List<String> loaded=Collections.synchronizedList(new ArrayList<>());CountDownLatch blockerEntered=new CountDownLatch(1),release=new CountDownLatch(1),nativeDone=new CountDownLatch(1);AtomicInteger displaced=new AtomicInteger();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{loaded.add(id);return Paths.get(id+".img");},
      (id,path,result,delay)->{if(id.equals("selectedNative")&&result==StationCoverQueue.SUCCESS)nativeDone.countDown();})){
   queue.requestWork("panelBlock",new StationCoverQueue.Work(){public void process(Path path,StationApi.Cancellation cancel)throws Exception{blockerEntered.countDown();release.await(5,TimeUnit.SECONDS);}});
   await(blockerEntered,"Download-panel fixture owns lane");
   for(int i=0;i<9;i++){final String id="panel"+i;queue.requestWork(id,new StationCoverQueue.Work(){public void process(Path path,StationApi.Cancellation cancel){}public void failed(int result,long retry){if(result==StationCoverQueue.TRANSIENT)displaced.incrementAndGet();}});}
   queue.request("selectedNative");release.countDown();await(nativeDone,"Selected native cover enters ahead of optional panel artwork");
   check(loaded.size()>=2&&loaded.get(0).equals("panelBlock")&&loaded.get(1).equals("selectedNative"),"Native selected cover runs next: "+loaded);
   check(displaced.get()>=1,"Full queue displaces optional artwork rather than selected native cover");
  }
 }

 private static void catalogPreparationOwnsTheLane()throws Exception{
  AtomicInteger active=new AtomicInteger(),maximum=new AtomicInteger(),attempts=new AtomicInteger();CountDownLatch entered=new CountDownLatch(1),allowed=new CountDownLatch(1);
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   maximum.accumulateAndGet(active.incrementAndGet(),Math::max);attempts.incrementAndGet();
   try{if(id.equals("oldpass1")){entered.countDown();for(;;){cancel.check();Thread.sleep(5);}}return Paths.get(id+".img");}
   finally{active.decrementAndGet();}
  },(id,path,result,delay)->{if(id.equals("allowed1")&&result==StationCoverQueue.SUCCESS)allowed.countDown();})){
   queue.prefetchCatalog(Collections.singletonList("oldpass1"));await(entered,"Old pass entered before catalog preparation");
   queue.quiesceForCatalog();queue.request("blocked1");Thread.sleep(30);
   check(attempts.get()==1,"Preparation admission rejects old-catalog visible IO");
   queue.endCatalogPreparation();queue.request("allowed1");await(allowed,"Same queue remains usable after preparation admission releases");
   check(maximum.get()==1,"Quiesce never overlaps old cover IO");
  }
 }

 private static void onlineDecodeUsesTheSameLane()throws Exception{
  AtomicInteger active=new AtomicInteger(),maximum=new AtomicInteger();CountDownLatch bgEntered=new CountDownLatch(1),decoded=new CountDownLatch(1),workEntered=new CountDownLatch(1),workCancelled=new CountDownLatch(1),passDone=new CountDownLatch(1);
  AtomicInteger bgAttempts=new AtomicInteger();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   maximum.accumulateAndGet(active.incrementAndGet(),Math::max);
   try{if(id.equals("onlineBg")&&bgAttempts.incrementAndGet()==1){bgEntered.countDown();for(;;){cancel.check();Thread.sleep(5);}}return Paths.get(id+".img");}
   finally{active.decrementAndGet();}
  },(id,path,result,delay)->{},text->{if(text.contains("reason=complete"))passDone.countDown();})){
   queue.prefetchCatalog(Collections.singletonList("onlineBg"));await(bgEntered,"Online fixture background entered");
   queue.setForeground(false);Thread.sleep(30);
   queue.requestWork("hero0001",new StationCoverQueue.Work(){@Override public void process(Path path,StationApi.Cancellation cancel)throws Exception{
    maximum.accumulateAndGet(active.incrementAndGet(),Math::max);try{Thread.sleep(20);cancel.check();}finally{active.decrementAndGet();}decoded.countDown();
   }});
   await(decoded,"Online bitmap decode remains admitted after carousel onStop");
   StationCoverQueue.Handle handle=queue.requestWork("hero0002",new StationCoverQueue.Work(){@Override public void process(Path path,StationApi.Cancellation cancel)throws Exception{
    workEntered.countDown();for(;;){cancel.check();Thread.sleep(5);}
   }@Override public void failed(int result,long retry){if(result==StationCoverQueue.CANCELLED)workCancelled.countDown();}});
   await(workEntered,"Second online work entered");handle.cancel();await(workCancelled,"Online stop handle cancels explicit work");Thread.sleep(30);
   check(bgAttempts.get()==1&&passDone.getCount()==1,"Carousel prefetch stays paused throughout online screen");
   queue.setForeground(true);await(passDone,"Carousel resume continues retained background plan");
   check(maximum.get()==1,"Path IO and online decode share exactly one lane");
  }
 }

 private static void catalogReplaceRetainsPausedDeferredNative()throws Exception{
  AtomicInteger attempts=new AtomicInteger(),events=new AtomicInteger(),published=new AtomicInteger();CountDownLatch done=new CountDownLatch(1);
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{attempts.incrementAndGet();return Paths.get(id+".img");},
      (id,path,result,delay)->{events.incrementAndGet();if(id.equals("nativeAfterReplace")&&result==StationCoverQueue.SUCCESS)done.countDown();})){
   queue.quiesceForCatalog();queue.request("nativeAfterReplace");queue.setForeground(false);
   queue.replaceCatalog(published::incrementAndGet);Thread.sleep(60);
   check(published.get()==1,"Catalog replacement publishes once while carousel is paused");
   check(attempts.get()==0&&events.get()==0&&queue.activeCount()==1,"Deferred native survives replacement without premature CANCELLED callback");
   queue.setForeground(true);await(done,"Deferred native is rebased and submitted on foreground after replacement");
   check(attempts.get()==1&&events.get()==1&&queue.activeCount()==0,"Rebased native performs one exact load and clears request state");
  }
 }

 private static void onlineWaitsForCatalogOwnerAcrossCarouselPause()throws Exception{
  AtomicInteger attempts=new AtomicInteger(),nativeEvents=new AtomicInteger();CountDownLatch decoded=new CountDownLatch(1),nativeDone=new CountDownLatch(1);
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{attempts.incrementAndGet();return Paths.get(id+".img");},
      (id,path,result,delay)->{nativeEvents.incrementAndGet();if(id.equals("nativeDeferred")&&result==StationCoverQueue.SUCCESS)nativeDone.countDown();})){
   queue.quiesceForCatalog();
   for(int i=0;i<32;i++)queue.request("nativeDeferred");
   // ESActivity pauses while the direct catalog warm owner is still unwinding.
   // That pause must neither release preparation nor cancel room artwork.
   queue.setForeground(false);
   queue.requestWork("onlineDeferred",new StationCoverQueue.Work(){@Override public void process(Path path,StationApi.Cancellation cancel){decoded.countDown();}});
   Thread.sleep(60);
   check(attempts.get()==0&&decoded.getCount()==1,"Online work waits while the catalog warm owner still owns cover IO");
   check(nativeEvents.get()==0,"Repeated native requests are deduplicated without CANCELLED callback loops during preparation");
   queue.endCatalogPreparation();await(decoded,"Online work resumes after catalog owner releases lane while carousel stays paused");
   check(nativeEvents.get()==0,"Deferred native stays silent until carousel foreground resumes");
   queue.setForeground(true);await(nativeDone,"One deferred native request resumes on foreground after preparation ended");
   check(attempts.get()==2&&nativeEvents.get()==1&&queue.activeCount()==0,"Deferred native and online covers perform one exact load each and leave no stuck request");
  }
 }
}
