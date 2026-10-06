package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Structural and progress regressions for the explicitly requested game-file policy. */
public final class StationDownloadPerformanceTest {
 static int checks;
 interface Op{void run()throws Exception;}
 static void ok(boolean value,String reason){checks++;if(!value)throw new AssertionError(reason);}
 static void rejects(Op action)throws Exception{try{action.run();throw new AssertionError("Expected rejection");}catch(IOException expected){checks++;}}
 static byte[] payload(){byte[] result=new byte[3*65536+17];for(int i=0;i<result.length;i++)result[i]=(byte)(i*31+7);return result;}
 static long generations(Path owner)throws IOException{try(java.util.stream.Stream<Path> paths=Files.list(owner)){return paths.filter(p->p.getFileName().toString().startsWith("install-")).count();}}
 static void rawBounds(Path root)throws Exception {
  Files.createDirectories(root);StationApiTest.Fake server=new StationApiTest.Fake();server.artifact=payload();StationApi api=server.api();
  StationApi.Cancellation cancel=new StationApi.Cancellation();StationApi.Grant grant=api.authorize(api.openSession(server.license,cancel),"item_12345",1,cancel);
  Path source=root.resolve("staging.bin"),records=root.resolve("records");Files.write(source,server.artifact);
  StationInstaller installer=new StationInstaller(root.resolve("roms"),records,(archive,sink,stopped)->{throw new AssertionError("RAW must not enter decoder");});
  AtomicInteger progress=new AtomicInteger();Path receipt=records.resolve("item_12345.json");
  StationInstaller.Installed installed=installer.install(StationInstallerTest.item(),grant,source,cancel,(n,total)->{
   progress.incrementAndGet();ok(!Files.exists(receipt),"RAW is unpublished while copying");ok(n<=total&&total==server.artifact.length,"Progress respects signed RAW length");
  });
  ok(progress.get()>1&&Arrays.equals(Files.readAllBytes(installed.launchPath),server.artifact),"Multi-chunk RAW copy preserves bytes");
  byte[] committed=Files.readAllBytes(receipt);Path owner=installed.launchPath.getParent().getParent().getParent();long before=generations(owner);
  StationApi.Cancellation stopped=new StationApi.Cancellation();
  rejects(()->installer.install(StationInstallerTest.item(),grant,source,stopped,(n,total)->stopped.cancel()));
  ok(Arrays.equals(Files.readAllBytes(receipt),committed)&&generations(owner)==before,"Mid-copy cancellation preserves prior commit and removes partial generation");
  AtomicBoolean grew=new AtomicBoolean();
  rejects(()->installer.install(StationInstallerTest.item(),grant,source,new StationApi.Cancellation(),(n,total)->{
   if(grew.compareAndSet(false,true))try{Files.write(source,new byte[]{1},StandardOpenOption.APPEND);}catch(IOException e){throw new UncheckedIOException(e);}
  }));
  ok(grew.get()&&Arrays.equals(Files.readAllBytes(receipt),committed)&&generations(owner)==before,"RAW growing during copy cannot exceed signed size or commit");
  Files.write(source,Arrays.copyOf(server.artifact,server.artifact.length-1));
  rejects(()->installer.install(StationInstallerTest.item(),grant,source,new StationApi.Cancellation(),StationFiles.NO_PROGRESS));
  byte[] wrongFormat=server.artifact.clone();wrongFormat[0]=80;wrongFormat[1]=75;wrongFormat[2]=3;wrongFormat[3]=4;Files.write(source,wrongFormat);
  rejects(()->installer.install(StationInstallerTest.item(),grant,source,new StationApi.Cancellation(),StationFiles.NO_PROGRESS));
  ok(Arrays.equals(Files.readAllBytes(receipt),committed)&&generations(owner)==before,"Truncated and wrong-format RAW preserve prior receipt");
  ok(Arrays.equals(Files.readAllBytes(installed.launchPath),server.artifact),"Failed replacements preserve installed bytes");
 }
 static void receiptLookup(Path root)throws Exception {
  Files.createDirectories(root);StationApiTest.Fake server=new StationApiTest.Fake();byte[] launch={1,2,3},companion={4,5};
  server.artifact=StationInstallerTest.zip(new String[]{"game.bin","data/companion.bin"},new byte[][]{launch,companion});
  server.descriptorOverride=StationInstallerTest.zipSpec(server.artifact,"game.bin",5,2);StationApi api=server.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  StationApi.Grant grant=api.authorize(api.openSession(server.license,cancel),"item_12345",1,cancel);Path source=root.resolve("bundle.zip");Files.write(source,server.artifact);
  StationInstaller installer=new StationInstaller(root.resolve("roms"),root.resolve("records"),new StationInstallerTest.ZipReader());
  StationInstaller.Installed installed=installer.install(StationInstallerTest.item(),grant,source,cancel,StationFiles.NO_PROGRESS);
  Path extra=installed.launchPath.getParent().resolve("data/companion.bin");Files.delete(extra);
  ok(installer.find(StationInstallerTest.item()).launchPath.equals(installed.launchPath),"Collection lookup uses committed entrypoint without scanning companion files");
  Files.write(installed.launchPath,new byte[]{1});ok(installer.find(StationInstallerTest.item())==null,"Wrong-size entrypoint is unavailable");
  Files.write(installed.launchPath,launch);ok(installer.find(StationInstallerTest.item())!=null,"Restored entrypoint resolves existing receipt");
  Files.delete(installed.launchPath);ok(installer.find(StationInstallerTest.item())==null,"Missing entrypoint is unavailable");
  Files.write(extra,companion);Files.write(installed.launchPath,launch);Path save=installed.launchPath.getParent().resolve("user.sav");Files.write(save,new byte[]{9});
  installer.uninstall("item_12345");ok(!Files.exists(extra)&&!Files.exists(installed.launchPath)&&Files.exists(save),"Uninstall still owns all recorded files and preserves user saves");
 }
 static final class Metric {final StationDiagnostics.Event event;final long count;Metric(StationDiagnostics.Event event,long count){this.event=event;this.count=count;}}
 static long metricCount(List<Metric> metrics,StationDiagnostics.Event event){return metrics.stream().filter(m->m.event==event).count();}
 static long metricValue(List<Metric> metrics,StationDiagnostics.Event event){return metrics.stream().filter(m->m.event==event).findFirst().orElseThrow(()->new AssertionError("Missing metric "+event)).count;}
 static final class Change {final String phase;final long n,total;final int result;Change(String phase,long n,long total,int result){this.phase=phase;this.n=n;this.total=total;this.result=result;}}
 static void phases(Path root,boolean archive,boolean legacy)throws Exception {
  Files.createDirectories(root);StationApiTest.Fake server=new StationApiTest.Fake();byte[] data=payload();server.artifact=archive?StationInstallerTest.zip(new String[]{"game.bin"},new byte[][]{data}):data;
  if(archive)server.descriptorOverride=StationInstallerTest.zipSpec(server.artifact,"game.bin",data.length,1);
  server.artifactBodyEntered=new CountDownLatch(1);server.artifactBodyRelease=new CountDownLatch(1);
  StationApi api=server.api();Path license=root.resolve("license.txt");Files.write(license,server.license.getBytes(StandardCharsets.UTF_8));
  StationSessions sessions=new StationSessions(api,server,license);StationCoordinator owner=new StationCoordinator(api,sessions,new StationCatalogStore(root.resolve("catalog")),new StationCoverStore(root.resolve("covers"),api,sessions,server,n->{},bytes->{}),root,server);
  owner.login(null,new StationApi.Cancellation());Path roms=root.resolve("roms");
  if(legacy){Path platform=roms.resolve(StationPlatforms.resolve(StationInstallerTest.item().platform).folder);Files.createDirectories(platform);Files.write(platform.resolve(archive?"bundle.zip":"game.bin"),server.artifact);}
  StationInstaller installer=new StationInstaller(roms,root.resolve("records"),new StationInstallerTest.ZipReader());
  List<Change> changes=Collections.synchronizedList(new ArrayList<>());List<Metric> metrics=Collections.synchronizedList(new ArrayList<>());CountDownLatch terminal=new CountDownLatch(1);
  StationDiagnostics.observe((event,status,n)->metrics.add(new Metric(event,n)));
  try(StationDownloads downloads=new StationDownloads(api,owner,installer,roms.resolve(".station-v2/staging"),(id,active,n,total,message,path,result)->{changes.add(new Change(message,n,total,result));if(!active)terminal.countDown();})) {
   ok(downloads.start("item_12345"),"Queue accepts fixture");
   try {
    ok(server.artifactBodyEntered.await(10,TimeUnit.SECONDS),"Headers accepted before fixture body is consumed");
    ok(metricCount(metrics,StationDiagnostics.Event.AUTHORIZE_ELAPSED_MS)==1&&metricValue(metrics,StationDiagnostics.Event.AUTHORIZE_ELAPSED_MS)>=0,"Authorization duration includes acquired access and finishes before body");
    ok(metricCount(metrics,StationDiagnostics.Event.ARTIFACT_HEADERS_ELAPSED_MS)==1&&metricValue(metrics,StationDiagnostics.Event.ARTIFACT_HEADERS_ELAPSED_MS)>=0,"Header duration emitted before blocked body is consumed");
    ok(metricCount(metrics,StationDiagnostics.Event.DOWNLOAD_ELAPSED_MS)==0&&metricCount(metrics,StationDiagnostics.Event.INSTALL_ELAPSED_MS)==0,"Body and install completion metrics cannot be emitted before body transfer");
   }finally{server.artifactBodyRelease.countDown();}
   ok(terminal.await(10,TimeUnit.SECONDS),"Fixture finishes");
   List<Change> snapshot=new ArrayList<>(changes);ok(snapshot.get(snapshot.size()-1).result==1,"Fixture installs successfully");
   int prepared=-1,lastDownload=-1;for(int i=0;i<snapshot.size();i++){Change change=snapshot.get(i);if(change.phase.equals("Baixando"))lastDownload=i;if(prepared<0&&change.phase.equals("Preparando"))prepared=i;}
   ok(prepared>lastDownload&&lastDownload>=0,"Preparation explicitly follows network phase");Change transition=snapshot.get(prepared);
   ok(transition.n==server.artifact.length&&transition.total==(long)server.artifact.length+data.length,"Phase transition preserves existing ABI global counts");
   ok(snapshot.stream().noneMatch(p->p.phase.equals("Verificando integridade")),"No nonexistent content-verification phase is announced");
   ok(snapshot.stream().noneMatch(p->p.phase.equals("Conferindo arquivo já baixado")),"No removed legacy-scan phase is announced");
   ok(metricCount(metrics,StationDiagnostics.Event.INSTALL_ELAPSED_MS)==1&&metricValue(metrics,StationDiagnostics.Event.INSTALL_ELAPSED_MS)>=0,"One nonnegative duration per completed installation");
   ok(metricCount(metrics,StationDiagnostics.Event.DOWNLOAD_ELAPSED_MS)==1&&metricValue(metrics,StationDiagnostics.Event.DOWNLOAD_ELAPSED_MS)>=0,"One nonnegative duration per completed transfer");
   ok(metricCount(metrics,StationDiagnostics.Event.DOWNLOAD_BYTES)==1&&metricValue(metrics,StationDiagnostics.Event.DOWNLOAD_BYTES)==server.artifact.length,"Downloaded bytes metric counts artifact only once");
   ok(metricCount(metrics,StationDiagnostics.Event.AUTHORIZE_ELAPSED_MS)==1&&metricCount(metrics,StationDiagnostics.Event.ARTIFACT_HEADERS_ELAPSED_MS)==1,"Authorization and header durations remain single events after completion");
   ok(server.artifactCalls==1,"One authenticated GET even if a legacy file matches name and size");
  }finally{StationDiagnostics.observe(null);}
 }
 public static void main(String[] args)throws Exception {
  ok(StationDownloads.message(new StationApi.Offline(),new StationApi.Cancellation()).equals("Conecte-se à internet para baixar o jogo."),"Offline download explains Internet requirement without blocking installed games");
  Path root=Paths.get(args[0]);rawBounds(root.resolve("raw-bounds"));receiptLookup(root.resolve("receipt"));
  phases(root.resolve("raw"),false,false);phases(root.resolve("zip"),true,false);phases(root.resolve("legacy"),false,true);
  System.out.println("PASS "+checks+" size, format, rollback, entrypoint, phase and metric checks");
 }
}
