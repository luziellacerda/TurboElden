package org.emulationstation.frontend.station;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.json.*;

/** Isolated synthetic transport; never uses the production server or device identity. */
public final class StationCoverLoadTest {
 public static void main(String[] args)throws Exception {
  final int count=4096;
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  StationCoverConcurrencyTest.Server server=new StationCoverConcurrencyTest.Server();
  server.base.catalogItems=new JSONArray();
  for(int n=0;n<count;n++)server.base.catalogItems.put(new JSONObject()
   .put("itemId",StationCoverConcurrencyTest.id(n)).put("coverId",StationCoverConcurrencyTest.cover(n))
   .put("name","Synthetic fixture "+n).put("platform","snes").put("revision",1));
  StationApi api=server.api();Path license=root.resolve("synthetic-license");
  Files.write(license,server.base.license.getBytes(StandardCharsets.UTF_8));
  StationSessions sessions=new StationSessions(api,server,license);
  StationCoverStore store=new StationCoverStore(root.resolve("covers"),api,sessions,server,
   delay->{throw new AssertionError("Success pacing must never be invoked");},bytes->{});
  StationCoordinator owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),store,root,server);
  owner.login(null,new StationApi.Cancellation());
  server.entered=new CountDownLatch(4);server.release=new CountDownLatch(1);
  CountDownLatch done=new CountDownLatch(count);AtomicInteger next=new AtomicInteger(4);
  AtomicInteger success=new AtomicInteger(),errors=new AtomicInteger();
  AtomicReference<StationCoverQueue> ref=new AtomicReference<>();
  long start=System.nanoTime();
  try(StationCoverQueue queue=new StationCoverQueue(owner::cover,(id,path,status,delay)->{
    if(status==StationCoverQueue.SUCCESS)success.incrementAndGet();else errors.incrementAndGet();
    int n=next.getAndIncrement();if(n<count)ref.get().request(StationCoverConcurrencyTest.id(n));
    done.countDown();
   })) {
   ref.set(queue);for(int n=0;n<4;n++)queue.request(StationCoverConcurrencyTest.id(n));
   if(!server.entered.await(10,TimeUnit.SECONDS))throw new AssertionError("Four transfers failed to overlap");
   if(server.maximum.get()!=4)throw new AssertionError("Concurrency is not four");
   server.release.countDown();
   if(!done.await(120,TimeUnit.SECONDS))throw new AssertionError("Queue stalled: "+done.getCount()+" pending");
   if(errors.get()!=0||success.get()!=count||server.calls.get()!=count||server.maximum.get()!=4)
    throw new AssertionError("Unexpected completion/concurrency/count");
  }finally{server.release.countDown();}
  long cold=System.nanoTime()-start;
  StationCoverStore restored=new StationCoverStore(root.resolve("covers"),api,sessions,server,
   delay->{throw new AssertionError("Cache must never pace");},bytes->{});
  start=System.nanoTime();
  for(int n=0;n<count;n++)if(Files.size(restored.get(StationCoverConcurrencyTest.cover(n),1,new StationApi.Cancellation()))!=8)
   throw new AssertionError("Invalid synthetic cache file");
  long warm=System.nanoTime()-start;
  if(server.calls.get()!=count)throw new AssertionError("Warm cache performed HTTP");
  try(java.util.stream.Stream<Path> files=Files.list(root.resolve("covers"))){
   if(files.anyMatch(p->p.getFileName().toString().endsWith(".part")))throw new AssertionError("Partial files leaked");
  }
  long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);long workers;
  do{workers=Thread.getAllStackTraces().keySet().stream().filter(t->t.isAlive()&&t.getName().equals("Station-covers")).count();if(workers>0)Thread.sleep(10);}while(workers>0&&System.nanoTime()<deadline);
  if(workers!=0)throw new AssertionError("Queue worker leaked after close");
  JSONObject result=new JSONObject().put("items",count).put("coldCompleted",success.get()).put("errors",errors.get())
   .put("peakConcurrent",server.maximum.get()).put("warmCacheItems",count).put("warmExtraHttp",0)
   .put("workersAfterClose",workers).put("coldMilliseconds",cold/1000000.0).put("warmMilliseconds",warm/1000000.0)
   .put("transport","synthetic local signed fixture, eight-byte image headers; no real network or image decode")
   .put("androidPerformanceClaim",false);
  Files.write(root.resolve("load-result.json"),result.toString(2).getBytes(StandardCharsets.UTF_8));
  System.out.println("PASS "+result.toString());
 }
}
