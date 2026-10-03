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
  String[][] aliases={{"megadrivebr","MegaDrive - BR"},{"arcade","Arcade"},{"atomiswave","Atomiswave"},{"dreamcast","Dreamcast"},{"mastersystem","Master System "},{"n64","Nintendo 64"},{"n64br","Nintendo 64 - BR"},{"nds","Nintendo DS"},{"neogeo","Neo Geo"},{"neogeocd","Neo Geo CD"},{"nes","Nintendinho"},{"o2em","Odyssey 2"},{"pcengine","Pc Engine"},{"pcenginecd","Pc Engine cd"},{"psx","Playstation 1"},{"switch","Switch"}};
  for(String[] pair:aliases)ok(StationPlatforms.resolve(pair[0])==StationPlatforms.resolve(pair[1]),"Explicit alias "+pair[0]);
  for(String unknown:new String[]{"model2","sufami","invented"}){
   try{StationPlatforms.resolve(unknown);throw new AssertionError("Unknown route inferred");}
   catch(StationPlatforms.UnsupportedPlatform expected){ok(expected.platform.equals(unknown),"Unknown is explicit");}
  }
  StationDiagnostics.observe((event,status,count)->events.add(event.name()+":"+status+":"+count));
  ok(StationDiagnostics.route("/v1/station/artifacts/SECRET")==StationDiagnostics.Event.ARTIFACT,"Grant never logged");
  ok(StationDiagnostics.route("/v1/station/covers/PRIVATE")==StationDiagnostics.Event.COVER,"Cover id never logged");
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
  ok(StationDownloads.message(new StationApi.Failure(404,"STATION_ITEM_NOT_FOUND"),cancel).contains("catálogo"),"Missing game requires server correction, not repeated retry");
  StationDiagnostics.observe(null);
  System.out.println("PASS "+checks+" server-closure checks (synthetic signed data, no production claim)");
 }
}
