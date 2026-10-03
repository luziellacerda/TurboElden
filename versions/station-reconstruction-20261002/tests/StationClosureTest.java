package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import org.json.*;

public final class StationClosureTest {
 static int checks;
 static void ok(boolean b,String reason){checks++;if(!b)throw new AssertionError(reason);}
 static final List<String> events=Collections.synchronizedList(new ArrayList<>());
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  String[][] aliases={{"megadrivebr","MegaDrive - BR"},{"arcade","Arcade"},{"atomiswave","Atomiswave"},{"dreamcast","Dreamcast"},{"mastersystem","Master System "},{"n64","Nintendo 64"},{"n64br","Nintendo 64 - BR"},{"nds","Nintendo DS"},{"neogeo","Neo Geo"},{"neogeocd","Neo Geo CD"},{"nes","Nintendinho"},{"o2em","Odyssey 2"},{"pcengine","Pc Engine"},{"pcenginecd","Pc Engine cd"},{"psx","Playstation 1"},{"switch","Switch"},{"gamecube","GameCube"},{"psp","PSP"},{"pspbr","Psp - BR"},{"ps2","Playstation 2"},{"ps2br","Playstation 2 - BR"},{"psvita","Psvita"}};
  for(String[] pair:aliases)ok(StationPlatforms.resolve(pair[0])==StationPlatforms.resolve(pair[1]),"Explicit alias "+pair[0]);
  for(String unknown:new String[]{"model2","sufami","invented"}){
   try{StationPlatforms.resolve(unknown);throw new AssertionError("Unknown route inferred");}
   catch(StationPlatforms.UnsupportedPlatform expected){ok(expected.platform.equals(unknown),"Unknown is explicit");}
  }
  StationCatalog mixed=StationCatalog.fromVerifiedPayload(StationApiTest.catalog(StationApiTest.item(),StationApiTest.item().put("itemId","item_unknown").put("platform","model2")));
  StationPublication publication=new StationPublication(mixed);
  ok(publication.rows.size()==1&&publication.rows.get(0).item.itemId.equals("item_12345"),"Unsupported platform cannot hide supported games");
  ok(mixed.items.size()==2&&publication.unsupported.get("model2")==1,"Entire signed catalog retained and exclusions counted");
  ok(publication.warning().contains("1 jogo")&&publication.warning().contains("model2"),"Unsupported entries have an explicit user notice");
  try{new StationPublication(StationCatalog.fromVerifiedPayload(StationApiTest.catalog(StationApiTest.item().put("platform","model2"))));throw new AssertionError("Unsupported-only catalog silently empty");}
  catch(StationPlatforms.UnsupportedPlatform expected){ok(true,"Unsupported-only catalog explains missing integration");}
  StationDiagnostics.observe((event,status,count)->events.add(event.name()+":"+status+":"+count));
  ok(StationDiagnostics.route("/v1/station/artifacts/SECRET")==StationDiagnostics.Event.ARTIFACT,"Grant never logged");
  ok(StationDiagnostics.route("/v1/station/covers/PRIVATE")==StationDiagnostics.Event.COVER,"Cover id never logged");
  List<String> traces=new ArrayList<>();
  StationDiagnostics.observeTrace((e,s,c,i,v,r)->traces.add(e+":"+s+":"+c+":"+i+":"+v+":"+r));
  try(StationDiagnostics.Scope trace=StationDiagnostics.selection("item_12345","cover_12345",7)){
   StationDiagnostics.trace(StationDiagnostics.Event.AUTHORIZE,404,"fixture-correlation-01");
   StationDiagnostics.trace(StationDiagnostics.Event.COVER,200,"unsafe\nheader");
  }
  StationDiagnostics.trace(StationDiagnostics.Event.PROFILE,200,"fixture-correlation-02");
  ok(traces.size()==2,"Unsafe correlation rejected and request scope cleared");
  ok(traces.get(0).contains(StationDiagnostics.tag("item_12345"))&&traces.get(0).endsWith(":7"),"Trace links exact selected item and revision by SHA256");
  ok(!traces.get(0).contains("item_12345")&&!traces.get(0).contains("cover_12345"),"Trace contains no raw identifiers");
  ok(traces.get(1).endsWith(":::0"),"Following request cannot inherit selected identities");
  StationDiagnostics.observeTrace((e,s,c,i,v,r)->{throw new IllegalStateException("observer");});
  StationDiagnostics.trace(StationDiagnostics.Event.ARTIFACT,200,"fixture-correlation-03");
  StationDiagnostics.observeTrace(null);
  StationDiagnostics.observe((e,s,c)->{throw new IllegalStateException("observer");});
  StationDiagnostics.record(StationDiagnostics.Event.CATALOG,200,1);ok(true,"Diagnostic failures cannot break requests");
  StationDiagnostics.observe((event,status,count)->events.add(event.name()+":"+status+":"+count));
  StationApiTest.Fake server=new StationApiTest.Fake();StationApi api=server.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  Path license=root.resolve("license");Files.write(license,server.license.getBytes(StandardCharsets.UTF_8));
  StationSessions sessions=new StationSessions(api,server,license);
  StationCoordinator owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),
   new StationCoverStore(root.resolve("covers"),api,sessions,server,n->server.time+=n,b->{}),root,server);
  JSONArray large=new JSONArray();String[] platforms={"snes","snesbr","megadrive","megadrivebr"};int[] counts={644,191,887,94};int index=0;
  for(int j=0;j<platforms.length;j++)for(int i=0;i<counts[j];i++)large.put(StationApiTest.item().put("itemId","fixture_"+(100000+index++)).put("platform",platforms[j]));
  server.catalogItems=large;StationCoordinator.Library library=owner.login(null,cancel);
  ok(library.catalog.items.size()==1816,"Entire signed candidate-sized catalog parsed");
  Map<String,Integer> totals=new HashMap<>();for(StationCatalog.Item item:library.catalog.items){StationPlatforms.resolve(item.platform);totals.merge(item.platform,1,Integer::sum);}
  for(int j=0;j<platforms.length;j++)ok(totals.get(platforms[j])==counts[j],"No truncation "+platforms[j]);
  ok(events.contains("CATALOG_NETWORK:200:1816"),"Network count diagnosed");
  server.failedRoute="/v1/station/catalog";server.status=503;server.errorCode="STATION_CATALOG_NOT_READY";
  ok(owner.refresh(cancel).cached,"Verified cache distinguished");ok(events.contains("CATALOG_CACHE:503:1816"),"Cache count diagnosed");
  server.failedRoute="";server.catalogItems=null;owner.refresh(cancel);
  StationCatalog.Item item=owner.current().catalog.items.get(0);
  Path roms=Files.createDirectories(root.resolve("roms"));Path old=Files.createDirectories(roms.resolve("master-system"));
  Path source=old.resolve("different-name.sms");Files.write(source,server.artifact);
  StationArtifact spec=StationArtifact.parse(StationApiTest.descriptor(server.artifact));
  ok(StationExistingArtifact.find(old,spec,cancel).equals(source),"Signed bytes match even with different name");
  Files.write(source,new byte[]{9,9,9});ok(StationExistingArtifact.find(old,spec,cancel)==null,"Same length is not identity");
  Files.write(source,server.artifact);StationApi.Cancellation stopped=new StationApi.Cancellation();stopped.cancel();
  try{StationExistingArtifact.find(old,spec,stopped);throw new AssertionError("Cancellation ignored");}catch(InterruptedIOException expected){ok(true,"Cancelled local scan");}
  ok(StationExistingArtifact.find(root.resolve("absent"),spec,cancel)==null,"Absent platform safe");
  StationInstaller installer=new StationInstaller(roms,root.resolve("records"),new StationInstallerTest.ZipReader());
  CountDownLatch done=new CountDownLatch(1);int[] result={0};String[] launch={""};
  try(StationDownloads downloads=new StationDownloads(api,owner,installer,roms.resolve(".station-v2/staging"),(id,active,n,t,message,path,code)->{
   if(code!=0){result[0]=code;launch[0]=path;done.countDown();}
  })){
   int requests=server.artifactCalls;ok(downloads.start(item.itemId),"Queue local verified install");
   ok(done.await(20,TimeUnit.SECONDS)&&result[0]==1,"Reused bytes installed transactionally");
   ok(server.artifactCalls==requests,"No artifact transfer when local bytes match");
   ok(Arrays.equals(Files.readAllBytes(Paths.get(launch[0])),server.artifact),"Installed bytes match");
   ok(Files.exists(source),"Original preserved");
   StationCatalog.Item aliased=StationCatalog.fromVerifiedPayload(StationApiTest.catalog(StationApiTest.item().put("platform","mastersystem"))).items.get(0);
   ok(installer.find(aliased)!=null,"Platform slug change preserves committed installation");
   installer.uninstall(item.itemId);ok(Files.exists(source),"Uninstall preserves original");
  }
  // With no matching local bytes, exercise the actual worker transfer/install path.
  Files.move(source,root.resolve("original-preserved.sms"));
  CountDownLatch downloaded=new CountDownLatch(1);int[] transferred={0};
  try(StationDownloads downloads=new StationDownloads(api,owner,installer,roms.resolve(".station-v2/staging"),(id,active,n,t,message,path,code)->{
   if(code!=0){transferred[0]=code;downloaded.countDown();}
  })){
   int requests=server.artifactCalls;ok(downloads.start(item.itemId),"Queue network install");
   ok(downloaded.await(20,TimeUnit.SECONDS)&&transferred[0]==1,"Transfer installs after signed verification");
   ok(server.artifactCalls==requests+1,"One artifact GET per grant");
   ok(installer.find(item)!=null,"Only complete network install becomes launchable");
  }
  server.omitDescriptor=true;
  try{owner.authorize(item.itemId,cancel);throw new AssertionError("Missing descriptor accepted");}
  catch(StationApi.ArtifactUnavailable expected){ok(StationDownloads.message(expected,cancel).contains("servidor"),"Clear descriptor message");}
  ok(events.stream().noneMatch(x->x.contains("SECRET")||x.contains("PRIVATE")||x.contains(server.license)),"No identifiers in diagnostics");
  StationDiagnostics.serverFailure(404,"STATION_ITEM_NOT_FOUND");
  ok(events.contains("SERVER_ITEM_NOT_FOUND:404:0"),"Known failure categorized");
  StationDiagnostics.serverFailure(404,"STATION_SECRET_PRIVATE");
  ok(events.contains("SERVER_OTHER_FAILURE:404:0"),"Unknown code not echoed");
  ok(events.stream().noneMatch(x->x.contains("SECRET")||x.contains("PRIVATE")),"Remote error codes cannot leak data");
  String missing=StationDownloads.message(new StationApi.Failure(404,"STATION_ITEM_NOT_FOUND"),cancel);
  ok(missing.contains("catálogo")&&!missing.contains("arquivo")&&!missing.contains("equipe"),"404 does not assert an unproven filesystem cause");
  ok(!StationDownloads.message(new java.net.SocketTimeoutException(),cancel).equals("Cancelado"),"Network timeout is not user cancellation");
  ok(!StationDownloads.message(new InterruptedIOException(),cancel).equals("Cancelado"),"Transport interruption is not user cancellation");
  ok(StationDownloads.message(new java.net.SocketTimeoutException(),stopped).equals("Cancelado"),"Explicit cancellation takes precedence");
  transferSessionRace(root.resolve("session-race"),true);
  transferSessionRace(root.resolve("session-streaming"),false);
  StationDiagnostics.observe(null);
  System.out.println("PASS "+checks+" server-closure checks (synthetic signed data, no production claim)");
 }
 static void transferSessionRace(Path root,boolean pendingHeaders)throws Exception {
  Files.createDirectories(root);
  StationApiTest.Fake server=new StationApiTest.Fake();server.rotateSessions=true;
  StationApi api=server.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  Path license=root.resolve("license");Files.write(license,server.license.getBytes(StandardCharsets.UTF_8));
  StationSessions sessions=new StationSessions(api,server,license);
  StationCoordinator owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),
   new StationCoverStore(root.resolve("covers"),api,sessions,server,n->server.time+=n,b->{}),root,server);
  owner.login(null,cancel);
  Path roms=Files.createDirectories(root.resolve("roms"));
  StationInstaller installer=new StationInstaller(roms,root.resolve("receipts"),new StationInstallerTest.ZipReader());
  CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);
  if(pendingHeaders){server.artifactEntered=entered;server.artifactRelease=release;}
  else{server.artifactBodyEntered=entered;server.artifactBodyRelease=release;}
  CountDownLatch installed=new CountDownLatch(1),coverStarted=new CountDownLatch(1),coverFinished=new CountDownLatch(1);
  int[] result={0};Throwable[] coverError={null};
  Thread cover=new Thread(()->{coverStarted.countDown();try{owner.cover("item_12345",cancel);}catch(Throwable e){coverError[0]=e;}finally{coverFinished.countDown();}},"fixture-cover");
  try(StationDownloads downloads=new StationDownloads(api,owner,installer,roms.resolve(".station-v2/staging"),(id,active,n,t,message,path,code)->{
   if(code!=0){result[0]=code;installed.countDown();}
  })){
   ok(downloads.start("item_12345"),"Start transfer under first session");
   ok(entered.await(10,TimeUnit.SECONDS),"GET entered before session renewal threshold");
   server.time+=165000;cover.start();
   ok(coverStarted.await(5,TimeUnit.SECONDS),"Independent cover worker started");
   try {
    if(pendingHeaders){
     ok(!coverFinished.await(200,TimeUnit.MILLISECONDS),"Cover cannot renew session before artifact headers arrive");
     ok(server.sessionCalls==1,"Artifact Bearer remains active until the server consumes the grant");
    }else{
     ok(coverFinished.await(5,TimeUnit.SECONDS)&&coverError[0]==null,"Streaming body cannot block cover/session renewal");
     ok(server.sessionCalls==2,"Session can renew after the accepted GET headers");
    }
   }finally{release.countDown();}
   ok(installed.await(10,TimeUnit.SECONDS)&&result[0]==1,"Pending grant completes despite cover renewal attempt");
   ok(coverFinished.await(10,TimeUnit.SECONDS)&&coverError[0]==null,"Cover resumes and renews session after GET");
   ok(server.sessionCalls==2&&owner.ready(),"New session authorizes refreshed catalog coherently");
   ok(installer.find(owner.current().catalog.find("item_12345"))!=null,"Concurrent operation leaves a verified installation");
  }finally{release.countDown();cover.join(10000);}
 }
}
