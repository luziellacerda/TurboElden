package org.emulationstation.frontend.station;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
/** Reproduces the old split invalidate/publish flow when testing the frozen R3 source. */
public final class StationCoverPublicationTest {
 static int checks;
 static void ok(boolean value,String text){checks++;if(!value)throw new AssertionError(text);}
 static void replace(StationCoverQueue queue,Runnable publish)throws Exception {
  try {queue.getClass().getMethod("replaceCatalog",Runnable.class).invoke(queue,publish);}
  catch(NoSuchMethodException oldImplementation){queue.invalidate();publish.run();}
  catch(InvocationTargetException failure){Throwable cause=failure.getCause();if(cause instanceof Error)throw (Error)cause;throw new RuntimeException(cause);}
 }
 static void round()throws Exception {
  CountDownLatch oldEntered=new CountDownLatch(4),releaseOld=new CountDownLatch(1),newDone=new CountDownLatch(1);
  ConcurrentHashMap<String,Path> inbox=new ConcurrentHashMap<>();AtomicInteger calls=new AtomicInteger(),cancels=new AtomicInteger(),success=new AtomicInteger();
  AtomicBoolean published=new AtomicBoolean(),postPublicationOld=new AtomicBoolean();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   int call=calls.incrementAndGet();
   if(call<=4){oldEntered.countDown();if(!releaseOld.await(5,TimeUnit.SECONDS))throw new IllegalStateException("Fixture timeout");return Paths.get("old.img");}
   return Paths.get("new.img");
  },(id,path,result,delay)->{
   if(result==StationCoverQueue.CANCELLED){cancels.incrementAndGet();if(published.get())postPublicationOld.set(true);}
   if(result==StationCoverQueue.SUCCESS){success.incrementAndGet();inbox.put(id,path);newDone.countDown();}
  })) {
   for(int i=0;i<8;i++)queue.request("item000"+i);
   ok(oldEntered.await(5,TimeUnit.SECONDS),"Four old cover bodies started");
   inbox.put("completed-before-refresh",Paths.get("stale.img"));
   replace(queue,()->{
    ok(queue.activeCount()==0,"Every old request must finish before JNI publishes a catalog");
    ok(cancels.get()==8,"Active and queued old requests each report cancellation once");
    inbox.clear();published.set(true);
   });
   ok(inbox.isEmpty(),"Native inbox starts empty for new publication");
   queue.request("item0000");releaseOld.countDown();
   ok(newDone.await(5,TimeUnit.SECONDS),"Same item refills after publication without another UI action");
   ok(calls.get()==5,"Cancelled queued requests never reach network loader");
   ok(Paths.get("new.img").equals(inbox.get("item0000")),"Only current publication image attaches");
   ok(success.get()==1&&!postPublicationOld.get(),"Old completion cannot free or overwrite a new native slot");
   ok(cancels.get()==8,"Old IO unwinding does not deliver a second completion");
  }finally{releaseOld.countDown();}
 }
 public static void main(String[] args)throws Exception {
  for(int i=0;i<20;i++)round();
  System.out.println("PASS "+checks+" atomic catalog publication checks (20 races)");
 }
}
