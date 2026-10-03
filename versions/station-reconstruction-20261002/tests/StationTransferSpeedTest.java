package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.json.*;

/** Exercise actual overlap, cache publication, cancellation and session boundaries. */
public final class StationTransferSpeedTest {
 static int checks;
 static final byte[] PNG={(byte)137,80,78,71,13,10,26,10};
 static void ok(boolean condition,String reason){checks++;if(!condition)throw new AssertionError(reason);}
 static final class Remote implements StationApi.Transport {
  final StationApiTest.Fake signed;
  final AtomicInteger calls=new AtomicInteger(),active=new AtomicInteger(),maximum=new AtomicInteger();
  volatile CountDownLatch entered=new CountDownLatch(0),release=new CountDownLatch(0);
  volatile int status=200;
  Remote(StationApiTest.Fake signed){this.signed=signed;}
  void hold(int count){entered=new CountDownLatch(count);release=new CountDownLatch(1);}
  public StationApi.Response exchange(String method,String route,byte[] bytes,String token,StationApi.Cancellation cancel)throws IOException {
   if(!route.startsWith("/v1/station/covers/")){synchronized(signed){return signed.exchange(method,route,bytes,token,cancel);}}
   calls.incrementAndGet();int running=active.incrementAndGet();maximum.accumulateAndGet(running,Math::max);
   CountDownLatch barrier=release;entered.countDown();
   try {
    while(!barrier.await(50,TimeUnit.MILLISECONDS))cancel.check();cancel.check();
    int result=status;
    byte[] body=result==200?PNG:new JSONObject().put("code",result==429?"STATION_RATE_LIMITED":"STATION_SESSION_INVALID").toString().getBytes(StandardCharsets.UTF_8);
    return new StationApi.Response(result,result==200?"image/png":"application/json",body.length,new ByteArrayInputStream(body),()->{});
   }catch(InterruptedException stopped){Thread.currentThread().interrupt();throw new InterruptedIOException();}
   finally{active.decrementAndGet();}
  }
 }
 static JSONArray catalog(int revision)throws Exception {
  JSONArray rows=new JSONArray();
  for(int i=0;i<8;i++)rows.put(StationApiTest.item().put("itemId",i==0?"item_12345":"item_fast_"+i)
   .put("coverId","cover_fast_"+i).put("revision",revision));
  return rows;
 }
 static void fails(Future<?> task,String reason)throws Exception {
  try{task.get(2,TimeUnit.SECONDS);throw new AssertionError(reason);}
  catch(ExecutionException failure){ok(failure.getCause() instanceof IOException,reason);}
 }
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  StationApiTest.Fake signed=new StationApiTest.Fake();signed.catalogItems=catalog(1);signed.rotateSessions=true;
  Remote remote=new Remote(signed);
  StationApi api=new StationApi(remote,signed,signed,signed.authority.getPublic(),"test-key");
  Path license=root.resolve("license");Files.write(license,signed.license.getBytes(StandardCharsets.UTF_8));
  StationSessions sessions=new StationSessions(api,signed,license);
  AtomicInteger waits=new AtomicInteger();
  StationCoverStore store=new StationCoverStore(root.resolve("covers"),api,sessions,signed,n->waits.incrementAndGet(),b->{});
  StationCoordinator owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),store,root,signed);
  StationApi.Cancellation login=new StationApi.Cancellation();owner.login(null,login);
  ExecutorService workers=Executors.newFixedThreadPool(4);
  try {
   remote.hold(4);List<Future<Path>> batch=new ArrayList<>();
   for(int i=0;i<4;i++){final String id=i==0?"item_12345":"item_fast_"+i;batch.add(workers.submit(()->owner.cover(id,new StationApi.Cancellation())));}
   try{ok(remote.entered.await(2,TimeUnit.SECONDS),"Four independent covers enter transport together");}
   finally{remote.release.countDown();}
   for(Future<Path> cover:batch)ok(Arrays.equals(Files.readAllBytes(cover.get(2,TimeUnit.SECONDS)),PNG),"Parallel cover preserves exact bytes");
   ok(remote.maximum.get()==4&&waits.get()==0,"Four requests overlap without artificial pacing");

   remote.hold(1);Future<Path> holding=workers.submit(()->owner.cover("item_fast_4",new StationApi.Cancellation()));
   try {
    ok(remote.entered.await(2,TimeUnit.SECONDS),"Uncached cover is held in transport");
    int requests=remote.calls.get();
    Future<Path> cached=workers.submit(()->owner.cover("item_12345",new StationApi.Cancellation()));
    ok(Files.exists(cached.get(500,TimeUnit.MILLISECONDS))&&remote.calls.get()==requests,"Cache hit does not wait for an unrelated cover");
    Future<StationApi.Grant> grant=workers.submit(()->owner.authorize("item_12345",new StationApi.Cancellation()));
    ok(grant.get(1,TimeUnit.SECONDS)!=null,"Cover transfer cannot delay download authorization");
   }finally{remote.release.countDown();}
   holding.get(2,TimeUnit.SECONDS);

   remote.hold(1);int before=remote.calls.get();List<Future<Path>> same=new ArrayList<>();
   for(int i=0;i<4;i++)same.add(workers.submit(()->store.get(sessions.peek(),"cover_duplicate",1,new StationApi.Cancellation())));
   try{ok(remote.entered.await(2,TimeUnit.SECONDS),"First duplicate enters transport");}
   finally{remote.release.countDown();}
   for(Future<Path> cover:same)cover.get(2,TimeUnit.SECONDS);
   ok(remote.calls.get()==before+1,"Concurrent duplicate cover has one HTTP request and one cache file");

   remote.hold(1);holding=workers.submit(()->store.get(sessions.peek(),"cover_cancelled",1,new StationApi.Cancellation()));
   try {
    ok(remote.entered.await(2,TimeUnit.SECONDS),"First cover owns cache publication");
    StationApi.Cancellation stop=new StationApi.Cancellation();
    Future<Path> waiting=workers.submit(()->store.get(sessions.peek(),"cover_cancelled",1,stop));stop.cancel();
    fails(waiting,"Cancelled duplicate exits promptly without another request");
   }finally{remote.release.countDown();}
   holding.get(2,TimeUnit.SECONDS);

   remote.hold(1);Future<Path> stale=workers.submit(()->owner.cover("item_fast_5",new StationApi.Cancellation()));
   try {
    ok(remote.entered.await(2,TimeUnit.SECONDS),"Old revision is held in transport");
    signed.catalogItems=catalog(2);owner.refresh(new StationApi.Cancellation());
   }finally{remote.release.countDown();}
   fails(stale,"Old cover completion cannot publish into the new revision");
   ok(owner.cover("item_fast_5",new StationApi.Cancellation()).getFileName().toString().endsWith("-2.img"),"New revision uses its own cache file");

   remote.status=429;before=remote.calls.get();
   try{store.get(sessions.peek(),"cover_limited",2,new StationApi.Cancellation());throw new AssertionError("Rate limit ignored");}
   catch(StationApi.Failure limit){ok(limit.status==429,"Server 429 is retained");}
   try{store.get(sessions.peek(),"cover_other",2,new StationApi.Cancellation());throw new AssertionError("Cooldown ignored");}
   catch(IOException limited){ok(remote.calls.get()==before+1,"429 stops new network requests without sleeping");}
   ok(Files.exists(store.get(sessions.peek(),"cover_fast_5",2,new StationApi.Cancellation())),"Cached covers remain available during rate cooldown");
   signed.time+=60001;remote.status=200;
   ok(Files.exists(store.get(sessions.peek(),"cover_other",2,new StationApi.Cancellation())),"Cover requests recover after cooldown");

   remote.hold(1);stale=workers.submit(()->owner.cover("item_fast_6",new StationApi.Cancellation()));
   try {
    ok(remote.entered.await(2,TimeUnit.SECONDS),"Old session cover is held in transport");
    signed.time+=165000;owner.refresh(new StationApi.Cancellation());remote.status=401;
   }finally{remote.release.countDown();}
   fails(stale,"Late old session denial propagates");remote.status=200;
   ok(owner.ready(),"Late denial cannot clear the newer authorized catalog/session");

   StationHttp.ResponseBody body=new StationHttp.ResponseBody(new ByteArrayInputStream(PNG));
   ok(!body.finished,"Unread HTTP body cannot be reused");byte[] buffer=new byte[16];
   ok(body.read(buffer)>0&&!body.finished,"Partial response cannot return socket to pool");
   ok(body.read(buffer)==-1&&body.finished,"Only consumed HTTP response permits connection reuse");body.close();
   ok(waits.get()==0,"No fixed delay was introduced by retry or cache logic");
  }finally{remote.release.countDown();workers.shutdownNow();workers.awaitTermination(5,TimeUnit.SECONDS);}
  System.out.println("PASS "+checks+" transfer speed checks (parallel covers, exact cache, cancellation, grants, revisions, rate recovery, late denial)");
 }
}
