package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.BooleanSupplier;
import org.json.*;

/** Real queue/API/installer, generated signed fixtures only; no phone or production. */
public final class StationDownloadCenterTest {
 static int checks;
 static void ok(boolean value,String name){checks++;if(!value)throw new AssertionError(name);}
 static void await(BooleanSupplier predicate,String name)throws Exception{long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(12);while(!predicate.getAsBoolean()&&System.nanoTime()<end)Thread.sleep(10);ok(predicate.getAsBoolean(),name);}
 static final class Wire implements StationApi.Transport {
  final StationApiTest.Fake server;volatile boolean online=true,stall;volatile int breakBodies,authorizations,gets,completed;volatile boolean rejected;
  Wire(StationApiTest.Fake s){server=s;}
  public boolean available(){return online;}
  public StationApi.Response exchange(String m,String p,byte[] b,String token,StationApi.Cancellation c)throws IOException{
   if(p.contains("/downloads/authorize")){authorizations++;if(rejected)return new StationApi.Response(403,"application/json",-1,new ByteArrayInputStream("{\"code\":\"STATION_LICENSE_DENIED\"}".getBytes()),()->{});}
   StationApi.Response reply=server.exchange(m,p,b,token,c);
   if(!p.contains("/artifacts/"))return reply;gets++;boolean fail=breakBodies-->0;
   InputStream stream=new FilterInputStream(reply.body){boolean broken;
    @Override public int read(byte[] bytes,int at,int size)throws IOException{
     while(stall){c.check();try{Thread.sleep(10);}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}}
     c.check();if(fail&&!broken){broken=true;throw new java.net.SocketException("fixture network loss");}
     int n=in.read(bytes,at,Math.min(8192,size));if(n<0)completed++;return n;
    }
   };
   return new StationApi.Response(reply.status,reply.type,reply.length,stream,reply::close);
  }
 }
 static StationDownloads.State state(StationDownloads d,String id){for(StationDownloads.Entry e:d.entries())if(e.id.equals(id))return e.state;return null;}
 public static void main(String[] args)throws Exception{
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  for(int i=0;i<600;i++){long delay=StationDownloadRetry.delayMillis(i,0);ok(delay>=2000&&delay<=30000,"bounded retry");}
  for(int status:new int[]{400,401,403,404,409,422})ok(!StationDownloadRetry.transientFailure(new StationApi.Failure(status,"fixture")),"permanent HTTP "+status);
  for(int status:new int[]{408,429,500,502,503,504})ok(StationDownloadRetry.transientFailure(new StationApi.Failure(status,"fixture")),"temporary HTTP "+status);
  ok(!StationDownloadRetry.transientFailure(new IOException("disk full")),"local IO is not network");
  ok(!StationDownloadRetry.transientFailure(new StationApi.ArtifactNetworkFailure(new javax.net.ssl.SSLHandshakeException("fixture"))),"TLS checks not retried as offline");
  ok(StationDownloadRetry.delayMillis(1,60000)==60000,"Retry-After retained");
  StationApiTest.Fake server=new StationApiTest.Fake();Wire wire=new Wire(server);
  StationApi api=new StationApi(wire,server,server,server.authority.getPublic(),"test-key");
  Path license=root.resolve("license");Files.write(license,server.license.getBytes(java.nio.charset.StandardCharsets.UTF_8));
  StationSessions sessions=new StationSessions(api,server,license);
  StationCoordinator owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),new StationCoverStore(root.resolve("covers"),api,sessions,server,n->{},b->{}),root,server);
  owner.login(null,new StationApi.Cancellation());Path staging=root.resolve("roms/.station-v2/staging");
  StationInstaller installer=new StationInstaller(root.resolve("roms"),root.resolve("receipts"),new StationInstallerTest.ZipReader());
  List<Integer> results=Collections.synchronizedList(new ArrayList<>());String id="item_12345";
  final StationDownloads d=new StationDownloads(api,owner,installer,staging,(key,active,n,total,message,path,result)->{if(result!=0)results.add(result);});
  try{
   wire.breakBodies=1;ok(d.start(id),"start");ok(!d.start(id),"no duplicate active job");
   await(()->state(d,id)==StationDownloads.State.WAITING,"network cut waits");ok(results.isEmpty(),"network cut does not emit failed/cancelled");
   await(()->state(d,id)==StationDownloads.State.COMPLETE,"recovers without user restart");ok(wire.authorizations==2&&wire.gets==2,"new authorization for every attempt");ok(installer.find(owner.current().catalog.find(id))!=null,"only completed transfer installed");
   wire.stall=true;ok(d.start(id),"new requested transfer");await(()->state(d,id)==StationDownloads.State.DOWNLOADING,"transfer started");d.pause(id);
   await(()->state(d,id)==StationDownloads.State.PAUSED,"pause transfer");int requests=wire.gets;Thread.sleep(250);ok(wire.gets==requests,"no retry while paused");
   await(()->Files.exists(staging.resolve("pending-downloads-v1")),"queue journal saved");
   wire.stall=false;d.resume(id);await(()->state(d,id)==StationDownloads.State.COMPLETE,"resume transfer");ok(wire.gets==requests+1,"resume gets fresh authorization");
   wire.online=false;ok(d.start(id),"queue offline");await(()->state(d,id)==StationDownloads.State.WAITING,"offline remains waiting");d.cancel(id);
   await(()->state(d,id)==null,"cancel removes row while waiting");ok(d.entryCount()==0,"cancel clears badge");requests=wire.gets;wire.online=true;d.connectionChanged();Thread.sleep(200);ok(wire.gets==requests,"cancelled cannot auto restart");
   wire.stall=true;ok(d.start(id),"start for in-flight cancellation");await(()->state(d,id)==StationDownloads.State.DOWNLOADING,"in-flight started");d.cancel(id);ok(state(d,id)==null&&d.entryCount()==0,"in-flight row hidden immediately");Thread.sleep(250);wire.stall=false;
   wire.rejected=true;ok(d.start(id),"permission rejection attempt");await(()->state(d,id)==StationDownloads.State.ERROR,"auth failure remains explicit error");requests=wire.authorizations;Thread.sleep(250);ok(wire.authorizations==requests,"no authorization bypass loop");wire.rejected=false;
   owner.login(null,new StationApi.Cancellation());
   // Restore a user-paused job after a new manager instance, without a network request.
   wire.online=false;d.resume(id);await(()->state(d,id)==StationDownloads.State.WAITING,"wait before journal pause");d.pause(id);
   await(()->{try{return Files.readString(staging.resolve("pending-downloads-v1")).contains("\tP");}catch(IOException e){return false;}},"paused choice persisted");
   d.close();requests=wire.authorizations;
   try(StationDownloads restored=new StationDownloads(api,owner,installer,staging,(key,active,n,total,message,path,result)->{})){restored.restorePending();ok(state(restored,id)==StationDownloads.State.PAUSED,"restored paused");ok(wire.authorizations==requests,"restoring pause does not start network");restored.cancel(id);}
   ok(installer.find(owner.current().catalog.find(id))!=null,"previous install preserved after later failure and cancel");
  }finally{d.close();}
  System.out.println("PASS "+checks+" download center checks with signed fixtures");
 }
}
