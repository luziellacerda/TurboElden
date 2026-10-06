package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;

/** Real RSA signatures from the fixture; all offline network calls are counted. */
public final class StationOfflineTest {
 static int checks;
 interface Op {void run()throws Exception;}
 static void ok(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
 static void fails(Op op)throws Exception{try{op.run();throw new AssertionError("Expected rejection");}catch(IOException|java.security.GeneralSecurityException|org.json.JSONException expected){checks++;}}
 static final class Client {
  final Path root; final StationApi api;final StationSessions sessions;final StationCatalogStore catalogs;
  final StationCoordinator owner;
  Client(Path root,StationApiTest.Fake server)throws Exception{this(root,server,server.api());}
  Client(Path root,StationApiTest.Fake server,StationApi api)throws Exception{
   this.root=root;this.api=api;Files.createDirectories(root);
   sessions=new StationSessions(api,server,root.resolve("license"));
   catalogs=new StationCatalogStore(root.resolve("catalog"));
   StationCoverStore covers=new StationCoverStore(root.resolve("covers"),api,sessions,server,n->{},b->{});
   owner=new StationCoordinator(api,sessions,catalogs,covers,root,server);
  }
  Path catalogFile()throws Exception{try(java.util.stream.Stream<Path> paths=Files.list(root.resolve("catalog"))){return paths.filter(p->p.toString().endsWith(".json")).findFirst().get();}}
 }
 static StationApi.Cancellation cancel(){return new StationApi.Cancellation();}
 static void online(Client c,StationApiTest.Fake server)throws Exception{server.reachable=true;c.owner.login(StationApiTest.token(9),cancel());}
 public static void main(String[] args)throws Exception{
  Path root=Paths.get(args[0]);Files.createDirectories(root);StationApiTest.Fake server=new StationApiTest.Fake();
  Client first=new Client(root.resolve("main"),server);server.reachable=false;
  fails(()->first.owner.login(StationApiTest.token(9),cancel()));ok(!first.owner.ready()&&server.requests==0,"First activation requires network, no fake local grant");
  online(first,server);ok(first.owner.ready(),"Online activation and library accepted");
  Path cover=first.owner.cover("item_12345",cancel());
  Path roms=Files.createDirectories(first.root.resolve("roms"));
  StationInstaller installer=new StationInstaller(roms,first.root.resolve("records"),new StationInstallerTest.ZipReader());
  Path staging=first.root.resolve("fixture.bin");Files.write(staging,server.artifact);
  StationApi.Grant spec=first.owner.authorize("item_12345",cancel());
  StationInstaller.Installed installed=installer.install(first.owner.current().catalog.find("item_12345"),spec,staging,cancel(),StationFiles.NO_PROGRESS);
  byte[] good=Files.readAllBytes(first.catalogFile());
  String disk=Files.readString(first.catalogFile());ok(!disk.contains(server.activeToken)&&!disk.contains("accessToken"),"No bearer persisted in signed catalog");
  int before=server.requests;server.reachable=false;server.time+=365L*24*60*60*1000;
  ok(first.owner.ready(),"A year offline does not expire local entry");
  ok(first.owner.cover("item_12345",cancel()).equals(cover)&&server.requests==before,"Saved cover independent of expired session");
  fails(()->first.owner.refresh(cancel()));ok(first.owner.ready(),"Offline refresh cannot close local library");
  fails(()->first.owner.authorize("item_12345",cancel()));ok(first.owner.ready()&&server.requests==before,"Offline download creates no grant, library retained");
  Client reboot=new Client(first.root,server);server.time=1;
  StationCoordinator.Library library=reboot.owner.login(null,cancel());
  ok(library.cached&&library.displayName.equals("Comprador")&&library.catalog.items.size()==1,"Cold boot restores name and signed catalog");
  ok(reboot.sessions.peek()==null&&server.requests==before,"Cold boot makes zero requests and invents no online session");
  StationInstaller reopenedInstaller=new StationInstaller(roms,first.root.resolve("records"),new StationInstallerTest.ZipReader());
  StationInstaller.Installed localGame=reopenedInstaller.find(library.catalog.find("item_12345"));
  ok(localGame!=null&&localGame.launchPath.equals(installed.launchPath)&&Files.size(localGame.launchPath)==3&&server.requests==before,"Installed game resolves after offline restart without transfer");
  StationApi.Transport unreachable=(method,path,body,bearer,cancellation)->{throw new java.net.ConnectException("Fixture server offline");};
  StationApi unavailableApi=new StationApi(unreachable,server,server,server.authority.getPublic(),"test-key");
  Client outage=new Client(first.root,server,unavailableApi);
  ok(outage.owner.login(null,cancel()).catalog.items.size()==1,"Connected Wi-Fi with server down still opens locally");
  fails(()->outage.owner.refresh(cancel()));ok(outage.owner.ready(),"Server connection failure preserves local access");
  ok(reboot.owner.cover("item_12345",cancel()).equals(cover)&&server.requests==before,"Cold boot reads persistent cover without session");
  java.util.concurrent.CountDownLatch entered=new java.util.concurrent.CountDownLatch(1),release=new java.util.concurrent.CountDownLatch(1);
  server.reachable=true;
  StationApi.Transport slow=(method,path,body,bearer,cancellation)->{
   if(path.equals("/v1/station/me")){entered.countDown();try{if(!release.await(5,java.util.concurrent.TimeUnit.SECONDS))throw new IOException("Test barrier timed out");}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}}
   return server.exchange(method,path,body,bearer,cancellation);
  };
  Client polling=new Client(first.root,server,new StationApi(slow,server,server,server.authority.getPublic(),"test-key"));
  polling.owner.login(null,cancel());
  java.util.concurrent.ExecutorService workers=java.util.concurrent.Executors.newFixedThreadPool(2);
  try{
   java.util.concurrent.Future<?> network=workers.submit(()->{try{polling.owner.refresh(cancel());}catch(Exception e){throw new RuntimeException(e);}});
   ok(entered.await(2,java.util.concurrent.TimeUnit.SECONDS),"Background profile request is deliberately stalled");
   java.util.concurrent.Future<Boolean> local=workers.submit(()->polling.owner.ready() && polling.owner.cover("item_12345",cancel()).equals(cover) && reopenedInstaller.find(polling.owner.current().catalog.find("item_12345"))!=null);
   ok(local.get(2,java.util.concurrent.TimeUnit.SECONDS),"Slow server does not lock ready/current/cache/installed-game reads");
   release.countDown();network.get(2,java.util.concurrent.TimeUnit.SECONDS);
  }finally{release.countDown();workers.shutdownNow();}
  before=server.requests;server.reachable=false;
  Files.delete(cover);fails(()->reboot.owner.cover("item_12345",cancel()));ok(reboot.owner.ready()&&server.requests==before,"Missing offline cover does not lock app or start network");
  reboot.owner.logout();ok(!reboot.owner.ready(),"Logout clears running access");reboot.owner.login(null,cancel());ok(reboot.owner.ready(),"Explicit re-entry restores registered installation");
  StationApi.Cancellation stopped=cancel();stopped.cancel();fails(()->reboot.owner.login(null,stopped));ok(!reboot.owner.ready()&&server.requests==before,"Cancelled restore does not authorize");
  reboot.owner.login(null,cancel());server.reachable=true;server.failedRoute="/v1/station/me";server.status=503;server.errorCode="STATION_UNAVAILABLE";
  fails(()->reboot.owner.refresh(cancel()));ok(reboot.owner.ready(),"Server outage preserves local library");
  server.status=401;server.errorCode="STATION_SESSION_INVALID";fails(()->reboot.owner.refresh(cancel()));ok(reboot.owner.ready()&&reboot.sessions.peek()==null,"401 expires bearer, not purchased local access");
  server.failedRoute="";reboot.owner.refresh(cancel());ok(reboot.sessions.peek()!=null,"Reconnection obtains real online session");
  server.failedRoute="/v1/station/me";server.status=403;server.errorCode="STATION_LICENSE_DENIED";
  fails(()->reboot.owner.refresh(cancel()));ok(!reboot.owner.ready(),"Explicit license denial closes local access");
  server.reachable=false;Client denied=new Client(first.root,server);before=server.requests;
  fails(()->denied.owner.login(null,cancel()));ok(!denied.owner.ready()&&server.requests==before,"Known denial survives offline restart");
  server.reachable=true;server.failedRoute="";denied.owner.login(null,cancel());ok(denied.owner.ready(),"Server reapproval restores access with saved license");
  server.time+=200000;server.failedRoute="/v1/station/challenges";server.status=403;server.errorCode="STATION_DEVICE_DENIED";
  fails(()->denied.owner.authorize("item_12345",cancel()));ok(!denied.owner.ready(),"Device denial before session creation persists too");
  server.reachable=false;fails(()->new Client(first.root,server).owner.login(null,cancel()));
  server.reachable=true;server.failedRoute="";denied.owner.login(null,cancel());server.reachable=false;
  Path cat=denied.catalogFile();before=server.requests;
  // Persisted data may only be accepted for the exact server, product, app, device and license.
  fails(()->denied.api.restoreLocalCatalog(good,"license_other_123"));
  StationApiTest.Fake other=new StationApiTest.Fake();
  StationApi otherDevice=new StationApi(server,other,server,server.authority.getPublic(),"test-key");
  fails(()->otherDevice.restoreLocalCatalog(good,server.license));
  fails(()->new StationApi(server,server,server,other.authority.getPublic(),"test-key").restoreLocalCatalog(good,server.license));
  fails(()->new StationApi(server,server,server,server.authority.getPublic(),"wrong-key").restoreLocalCatalog(good,server.license));
  JSONObject envelope=new JSONObject(new String(good,StandardCharsets.UTF_8));
  byte[] signature=StationProtocol.decode(envelope.getString("signature"));signature[0]^=1;
  byte[] corrupt=envelope.put("signature",StationProtocol.base64Url(signature)).toString().getBytes(StandardCharsets.UTF_8);
  Files.write(cat,corrupt);fails(()->new Client(first.root,server).owner.login(null,cancel()));
  Files.write(cat,"{}".getBytes(StandardCharsets.UTF_8));fails(()->new Client(first.root,server).owner.login(null,cancel()));
  Files.write(cat,good);Files.writeString(first.root.resolve("license"),"license_other_123");fails(()->new Client(first.root,server).owner.login(null,cancel()));
  Files.delete(first.root.resolve("license"));fails(()->new Client(first.root,server).owner.login(null,cancel()));
  ok(server.requests==before,"Malformed/copied cache cannot bypass auth or make offline network requests");
  ok(server.closed==server.requests,"All actual online responses closed");
  System.out.println("PASS "+checks+" offline activation/cache/reboot/denial checks");
 }
}
