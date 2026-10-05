package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicInteger;
import org.json.JSONArray;

/** Actual signed responses: cached/renewed sessions avoid the catalog round trip. */
public final class StationDownloadStartTest {
 static int checks;
 static void ok(boolean yes,String why){checks++;if(!yes)throw new AssertionError(why);}
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  StationApiTest.Fake server=new StationApiTest.Fake();server.rotateSessions=true;
  AtomicInteger catalogs=new AtomicInteger(),profiles=new AtomicInteger(),grants=new AtomicInteger();
  StationApi.Transport transport=(method,path,body,bearer,cancel)->{
   if(path.startsWith("/v1/station/catalog"))catalogs.incrementAndGet();
   if(path.equals("/v1/station/me"))profiles.incrementAndGet();
   if(path.equals("/v1/station/downloads/authorize"))grants.incrementAndGet();
   return server.exchange(method,path,body,bearer,cancel);
  };
  StationApi api=new StationApi(transport,server,server,server.authority.getPublic(),"test-key");
  Path license=root.resolve("license");Files.write(license,server.license.getBytes(StandardCharsets.UTF_8));
  StationSessions sessions=new StationSessions(api,server,license);
  StationCoordinator owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),new StationCoverStore(root.resolve("covers"),api,sessions,server,n->{},bytes->{}),root,server);
  StationApi.Cancellation cancel=new StationApi.Cancellation();owner.login(null,cancel);
  ok(catalogs.get()==1&&profiles.get()==1,"Initial activation fetches its signed catalog and profile");
  owner.logout();ok(owner.login(null,cancel).cached,"Activated restart restores the signed offline catalog");
  int before=catalogs.get();server.time+=200000;
  server.failedRoute="/v1/station/catalog";server.status=500;server.errorCode="TEST_CATALOG_FAILURE";
  try(StationCoordinator.DownloadAccess access=owner.authorizeDownload("item_12345",cancel)) {
   ok(access.item.revision==access.grant.itemRevision,"Signed grant matches cached item revision");
   Path downloaded=root.resolve("first.bin");
   api.downloadToStaging(access.grant,downloaded,server.artifact.length,cancel,StationFiles.NO_PROGRESS);
   ok(Files.size(downloaded)==server.artifact.length,"The first cached download starts without a catalog response");
  }
  ok(catalogs.get()==before&&profiles.get()==1,"Reopening and renewing do not fetch the entire catalog/profile before download");
  ok(server.sessionCalls==2&&grants.get()==1&&server.artifactCalls==1,"Only a fresh session and one authorization/GET are needed");
  server.failedRoute="";server.itemRevision=2;server.catalogItems=new JSONArray().put(StationApiTest.item().put("revision",2));
  before=catalogs.get();int grantBefore=grants.get();
  try(StationCoordinator.DownloadAccess access=owner.authorizeDownload("item_12345",cancel)) {
   ok(access.item.revision==2&&access.grant.itemRevision==2,"A changed item reconciles before any artifact GET");
  }
  ok(catalogs.get()==before+1&&grants.get()==grantBefore+2&&profiles.get()==1,"Revision mismatch triggers exactly one catalog refresh and one new authorization");
  before=catalogs.get();grantBefore=grants.get();server.itemRevision=3;
  try {owner.authorizeDownload("item_12345",cancel);throw new AssertionError("Expected unstable item rejection");}
  catch(StationApi.ItemRevisionChanged expected){checks++;}
  ok(catalogs.get()==before+1&&grants.get()==grantBefore+2&&server.artifactCalls==1,"Repeated revision mismatch stops before GET without an authorization loop");
  server.failedRoute="/v1/station/downloads/authorize";server.status=403;server.errorCode="STATION_LICENSE_DENIED";
  try {owner.authorizeDownload("item_12345",cancel);throw new AssertionError("Expected license denial");}
  catch(StationApi.Failure expected){ok(expected.status==403,"The faster path still propagates server denial");}
  System.out.println("PASS "+checks+" cached start, session renewal, lazy catalog, bounded retry and denial checks");
 }
}
