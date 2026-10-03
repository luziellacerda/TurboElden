package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.json.*;
public final class StationCoverConcurrencyTest {
 static int checks;
 static void ok(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
 static final byte[] PNG={(byte)137,80,78,71,13,10,26,10};
 static class Server implements StationApi.Transport,StationApi.Clock {
  final StationApiTest.Fake base;final AtomicInteger calls=new AtomicInteger(),active=new AtomicInteger(),maximum=new AtomicInteger();
  volatile CountDownLatch entered,release;volatile int error;volatile long retry;volatile String errorCover="";
  Server()throws Exception{base=new StationApiTest.Fake();base.rotateSessions=true;base.catalogItems=new JSONArray();for(int i=0;i<12;i++)base.catalogItems.put(new JSONObject().put("itemId",id(i)).put("coverId",cover(i)).put("name","Game "+i).put("platform","snes").put("revision",1));}
  public long millis(){return base.time;}
  StationApi api()throws Exception{return new StationApi(this,base,this,base.authority.getPublic(),"test-key");}
  public StationApi.Response exchange(String method,String path,byte[] body,String token,StationApi.Cancellation cancel)throws IOException {
   if(!path.contains("/covers/")){synchronized(base){return base.exchange(method,path,body,token,cancel);}}
   calls.incrementAndGet();int n=active.incrementAndGet();maximum.accumulateAndGet(n,Math::max);
   try {
    CountDownLatch signal=entered,gate=release;if(signal!=null)signal.countDown();
    if(gate!=null)while(!gate.await(20,TimeUnit.MILLISECONDS))cancel.check();cancel.check();
    if(!token.equals(base.activeToken))throw new AssertionError("Rotated bearer used by cover");
    boolean failed=error!=0&&(errorCover.isEmpty()||path.endsWith(errorCover));
    byte[] bytes=failed?("{\"code\":\"STATION_RATE_LIMITED\"}").getBytes(StandardCharsets.UTF_8):PNG;
    return new StationApi.Response(failed?error:200,failed?"application/json":"image/png",bytes.length,new ByteArrayInputStream(bytes),()->active.decrementAndGet(),retry);
   }catch(InterruptedException interrupted){Thread.currentThread().interrupt();active.decrementAndGet();throw new InterruptedIOException();}
   catch(IOException|RuntimeException|Error failure){active.decrementAndGet();throw failure;}
  }
 }
 static String id(int i){return String.format("item_%04d",i);}static String cover(int i){return String.format("cover_%04d",i);}
 static class Fixture {
  final Server server;final StationApi api;final StationSessions sessions;final StationCoverStore store;final StationCoordinator owner;final Path root;
  Fixture(Path root)throws Exception{this.root=root;Files.createDirectories(root);server=new Server();api=server.api();Path license=root.resolve("license");Files.write(license,server.base.license.getBytes(StandardCharsets.UTF_8));sessions=new StationSessions(api,server,license);store=store(root.resolve("covers"));owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),store,root,server);owner.login(null,new StationApi.Cancellation());}
  StationCoverStore store(Path path)throws Exception{return new StationCoverStore(path,api,sessions,server,n->{throw new AssertionError("Artificial cover pacing was called");},b->{});}
 }
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  generation();parallel(root.resolve("parallel"));deduplicate(root.resolve("same-key"));renewal(root.resolve("renewal"));cancel(root.resolve("cancel"));backoff(root.resolve("backoff"));denialRace(root.resolve("denial"));
  ok(StationRetryAfter.parse("3",0)==3000,"Retry-After seconds");ok(StationRetryAfter.parse("Sat, 03 Oct 2026 12:00:05 GMT",1791028800000L)==5000,"Retry-After HTTP date");
  ok(StationRetryAfter.parse("nonsense",0)==0&&StationRetryAfter.parse(null,0)==0,"Absent/invalid header falls back");
  System.out.println("PASS "+checks+" cover concurrency, cache, session, lifecycle and backoff checks");
 }
 static void generation()throws Exception{
  CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1),done=new CountDownLatch(1);
  AtomicInteger calls=new AtomicInteger(),stale=new AtomicInteger();AtomicReference<StationCoverQueue> ref=new AtomicReference<>();AtomicReference<Path> result=new AtomicReference<>();
  try(StationCoverQueue queue=new StationCoverQueue((id,cancel)->{
   int call=calls.incrementAndGet();if(call==1){entered.countDown();if(!release.await(5,TimeUnit.SECONDS))throw new IOException("Fixture timeout");return Paths.get("old-revision.img");}
   return Paths.get("new-revision.img");
  },(id,path,status,delay)->{
   if(status==StationCoverQueue.CANCELLED){stale.incrementAndGet();ref.get().request(id);}
   if(status==StationCoverQueue.SUCCESS){result.set(path);done.countDown();}
  })){
   ref.set(queue);queue.request(id(0));ok(entered.await(5,TimeUnit.SECONDS),"Old catalog request entered");
   queue.invalidate();release.countDown();ok(done.await(5,TimeUnit.SECONDS),"Current catalog request refills automatically after obsolete completion");
   ok(stale.get()==1&&calls.get()==2&&Paths.get("new-revision.img").equals(result.get()),"Obsolete image can never overwrite the new catalog revision");
  }finally{release.countDown();}
 }
 static void parallel(Path root)throws Exception{
  Fixture f=new Fixture(root);f.server.entered=new CountDownLatch(4);f.server.release=new CountDownLatch(1);CountDownLatch done=new CountDownLatch(8);List<Integer>results=Collections.synchronizedList(new ArrayList<>());
  try(StationCoverQueue queue=new StationCoverQueue(f.owner::cover,(id,path,result,delay)->{results.add(result);done.countDown();})){
   for(int i=0;i<8;i++)queue.request(id(i));queue.request(id(0));
   ok(f.server.entered.await(5,TimeUnit.SECONDS),"Four HTTP cover transfers overlap");ok(f.server.calls.get()==4&&f.server.maximum.get()==4,"Actual maximum is four, fifth remains queued");
   f.server.release.countDown();ok(done.await(10,TimeUnit.SECONDS),"All eight refill and finish without another user action");
   ok(f.server.calls.get()==8&&results.stream().allMatch(v->v==StationCoverQueue.SUCCESS),"Queue deduplicates same item and completes all");
   ok(f.server.base.time==1000,"No success pacing or injected sleep");
  }finally{f.server.release.countDown();}
  int before=f.server.calls.get();StationCoverStore restarted=f.store(root.resolve("covers"));
  for(int i=0;i<8;i++)ok(Files.size(restarted.get(cover(i),1,new StationApi.Cancellation()))==8,"Persistent cover survives new store");
  ok(f.server.calls.get()==before,"Persistent cache adds zero HTTP requests");
  try(java.util.stream.Stream<Path> paths=Files.list(root.resolve("covers"))){ok(paths.noneMatch(p->p.getFileName().toString().endsWith(".part")),"No partial cache files leaked");}
 }
 static void deduplicate(Path root)throws Exception{
  Fixture f=new Fixture(root);f.server.entered=new CountDownLatch(1);f.server.release=new CountDownLatch(1);ExecutorService workers=Executors.newFixedThreadPool(2);
  try{Future<Path>a=workers.submit(()->f.store.get(cover(0),1,new StationApi.Cancellation()));ok(f.server.entered.await(5,TimeUnit.SECONDS),"First cache miss entered");Future<Path>b=workers.submit(()->f.store.get(cover(0),1,new StationApi.Cancellation()));
   f.server.release.countDown();ok(a.get(5,TimeUnit.SECONDS).equals(b.get(5,TimeUnit.SECONDS))&&f.server.calls.get()==1,"Per-key lock prevents duplicate same-image download");
  }finally{f.server.release.countDown();workers.shutdownNow();}
 }
 static void renewal(Path root)throws Exception{
  Fixture f=new Fixture(root);f.server.entered=new CountDownLatch(4);f.server.release=new CountDownLatch(1);ExecutorService workers=Executors.newFixedThreadPool(5);List<Future<Path>>covers=new ArrayList<>();
  try{for(int i=0;i<4;i++){final int n=i;covers.add(workers.submit(()->f.owner.cover(id(n),new StationApi.Cancellation())));}ok(f.server.entered.await(5,TimeUnit.SECONDS),"Four leases active before renewal");
   f.server.base.time+=165000;Future<?>refresh=workers.submit(()->{try{return f.owner.refresh(new StationApi.Cancellation());}catch(Exception e){throw new RuntimeException(e);}});
   Thread.sleep(100);ok(!refresh.isDone()&&f.server.base.sessionCalls==1,"Session does not rotate underneath four active cover requests");
   f.server.release.countDown();for(Future<Path>cover:covers)cover.get(5,TimeUnit.SECONDS);refresh.get(5,TimeUnit.SECONDS);
   ok(f.server.base.sessionCalls==2&&f.owner.ready(),"Renewal resumes after last lease, no deadlock");
  }finally{f.server.release.countDown();workers.shutdownNow();}
 }
 static void cancel(Path root)throws Exception{
  Fixture f=new Fixture(root);f.server.entered=new CountDownLatch(4);f.server.release=new CountDownLatch(1);CountDownLatch stopped=new CountDownLatch(8),resumed=new CountDownLatch(1);AtomicInteger cancelled=new AtomicInteger();
  try(StationCoverQueue queue=new StationCoverQueue(f.owner::cover,(id,path,result,delay)->{if(result==StationCoverQueue.CANCELLED){cancelled.incrementAndGet();stopped.countDown();}else if(result==StationCoverQueue.SUCCESS)resumed.countDown();})){
   for(int i=0;i<8;i++)queue.request(id(i));ok(f.server.entered.await(5,TimeUnit.SECONDS),"Four active before background");queue.setForeground(false);
   ok(stopped.await(5,TimeUnit.SECONDS)&&cancelled.get()==8,"Active and queued work report cancellation independently");ok(f.server.calls.get()==4&&queue.activeCount()==0,"Background starts no queued HTTP work");
   f.server.release.countDown();queue.setForeground(true);queue.request(id(0));ok(resumed.await(5,TimeUnit.SECONDS),"Resume retries cancelled image immediately, no 60-second ban");
  }finally{f.server.release.countDown();}
 }
 static void backoff(Path root)throws Exception{
  Fixture f=new Fixture(root);StationApi.Cancellation cancel=new StationApi.Cancellation();f.owner.cover(id(0),cancel);f.server.error=429;f.server.retry=3000;
  try{f.owner.cover(id(1),cancel);throw new AssertionError("429 accepted");}catch(StationApi.Failure failure){ok(failure.retryAfterMillis==3000,"429 carries server retry delay");}
  int count=f.server.calls.get();try{f.owner.cover(id(2),cancel);throw new AssertionError("Cooldown bypass");}catch(StationCoverStore.Deferred deferred){ok(deferred.rateLimited&&deferred.retryMillis==3000,"Rate limit returned as deferred, no busy wait");}
  f.owner.cover(id(0),cancel);ok(f.server.calls.get()==count,"Cached artwork remains immediate during rate backoff");f.server.base.time+=3000;f.server.error=0;f.owner.cover(id(2),cancel);ok(f.server.calls.get()==count+1,"Real backoff ends, next cover fetch starts");
  f.server.error=404;f.server.errorCover=cover(3);try{f.owner.cover(id(3),cancel);throw new AssertionError();}catch(StationApi.Failure expected){ok(expected.status==404,"Missing artwork classified");}
  f.server.error=0;f.owner.cover(id(4),cancel);ok(Files.exists(root.resolve("covers").resolve(cover(4)+"-1.img")),"404 does not stop another image");
  try{f.owner.cover(id(3),cancel);throw new AssertionError();}catch(StationCoverStore.Deferred deferred){ok(!deferred.rateLimited&&deferred.retryMillis==60000,"Missing cover alone has bounded retry");}
 }
 static void denialRace(Path root)throws Exception{
  Fixture f=new Fixture(root);StationApi.Cancellation cancel=new StationApi.Cancellation();f.server.error=401;StationApi.Session rejected=f.sessions.peek();
  try{f.owner.cover(id(0),cancel);throw new AssertionError();}catch(StationApi.Failure failure){ok(failure.sessionDenied()&&!f.owner.ready(),"401 invalidates active session without bypass");}
  f.server.error=0;f.owner.login(null,cancel);ok(f.owner.ready()&&f.server.base.sessionCalls==2,"Next authenticated login recovers after denial");f.owner.cover(id(0),cancel);ok(f.owner.ready(),"New session remains authorized after cover success");
  java.lang.reflect.Method invalidate=StationCoordinator.class.getDeclaredMethod("invalidate",StationApi.Session.class);invalidate.setAccessible(true);invalidate.invoke(f.owner,rejected);
  ok(f.owner.ready(),"Delayed rejection cannot clear a newer authorized session");
 }
}
