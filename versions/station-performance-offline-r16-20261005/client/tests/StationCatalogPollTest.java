package org.emulationstation.frontend.station;
import java.io.IOException;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.json.*;

public final class StationCatalogPollTest {
 static int checks;
 static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
 static JSONObject payload(Object metadata)throws Exception {
  return new JSONObject().put("revision",8).put("items",new JSONArray().put(new JSONObject()
   .put("itemId","synthetic_n64").put("coverId","synthetic_cover").put("name","N64")
   .put("platform","n64").put("revision",1).put("metadata",metadata)));
 }
 static void reject(Object metadata)throws Exception {
  try{StationCatalog.fromVerifiedPayload(payload(metadata));throw new AssertionError("invalid metadata accepted");}
  catch(IOException expected){checks++;}
 }
 public static void main(String[] args)throws Exception {
  StationCatalogPoll gate=new StationCatalogPoll();check(gate.begin()==null);
  gate.resume();StationCatalogPoll.Ticket a=gate.begin();check(a!=null);check(gate.current(a));check(gate.begin()==null);
  gate.resume();check(gate.current(a));
  AtomicInteger aborts=new AtomicInteger();a.cancel.attach(aborts::incrementAndGet);
  gate.pause();check(a.cancel.cancelled());check(aborts.get()==1);check(!gate.current(a));check(gate.begin()==null);
  gate.resume();check(!gate.current(a));check(gate.begin()==null);gate.finish(a);
  StationCatalogPoll.Ticket b=gate.begin();check(gate.current(b));gate.finish(a);check(gate.current(b));gate.finish(b);
  check(gate.begin()!=null);gate.pause();
  check(!StationCatalogPoll.changed(8,"Cliente",8,"Cliente"));
  check(StationCatalogPoll.changed(8,"Cliente",9,"Cliente"));
  check(StationCatalogPoll.changed(8,"Cliente",8,"Nome novo"));
  check(StationDiagnostics.route("/v1/station/catalog?metadata=1")==StationDiagnostics.Event.CATALOG);
  check(StationDiagnostics.route("/v1/station/catalog")==StationDiagnostics.Event.CATALOG);
  check(StationDiagnostics.route("/v1/station/catalog?metadata=2")==StationDiagnostics.Event.REQUEST_FAILED);
  reject("text");reject(JSONObject.NULL);reject(new JSONArray());
  reject(new JSONObject().put("description",12));reject(new JSONObject().put("description","x".repeat(2001)));
  reject(new JSONObject().put("description","\ud800"));reject(new JSONObject().put("description","bad\fpage"));
  check(StationCatalog.fromVerifiedPayload(payload(new JSONObject().put("description","x".repeat(2000)))).items.get(0).description.length()==2000);
  check(StationCatalog.fromVerifiedPayload(payload(new JSONObject())).items.get(0).description.isEmpty());
  // Exercise a request already running when the activity is hidden.
  StationCatalogPoll race=new StationCatalogPoll();race.resume();StationCatalogPoll.Ticket t=race.begin();
  CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);AtomicInteger published=new AtomicInteger();
  ExecutorService worker=Executors.newSingleThreadExecutor();
  try {
   Future<?> run=worker.submit(()->{entered.countDown();try{release.await();if(race.current(t))published.incrementAndGet();}catch(InterruptedException e){Thread.currentThread().interrupt();}finally{race.finish(t);}});
   check(entered.await(2,TimeUnit.SECONDS));race.pause();race.resume();release.countDown();run.get(2,TimeUnit.SECONDS);
   check(published.get()==0);check(t.cancel.cancelled());check(race.begin()!=null);
  }finally{worker.shutdownNow();}
  System.out.println("PASS "+checks+" foreground cancellation, generation, revision, diagnostics and metadata checks");
 }
}
