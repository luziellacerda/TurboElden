package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

/** Exercises real file ownership, rename, receipt commit and cancellation. */
public final class StationRawTransferTest {
 static int checks;
 interface Op {void run()throws Exception;}
 static void ok(boolean yes,String why){checks++;if(!yes)throw new AssertionError(why);}
 static void rejects(Op action)throws Exception{try{action.run();throw new AssertionError("Expected rejection");}catch(IOException expected){checks++;}}
 static Object key(Path p)throws Exception{return Files.readAttributes(p,BasicFileAttributes.class).fileKey();}
 static Path stage(Path roms,byte[] bytes)throws Exception {
  Path parent=StationInstaller.directory(roms.resolve(".station-v2/staging"));
  Path file=Files.createTempDirectory(parent,"transfer-").resolve("artifact");Files.write(file,bytes);return file;
 }
 static long generations(Path p)throws Exception{try(java.util.stream.Stream<Path> stream=Files.list(p)){return stream.count();}}
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  Path roms=root.resolve("roms"),records=root.resolve("records");
  StationApiTest.Fake server=new StationApiTest.Fake();server.artifact=StationDownloadPerformanceTest.payload();
  StationApi api=server.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  StationApi.Session session=api.openSession(server.license,cancel);
  StationApi.Grant grant=api.authorize(session,"item_12345",1,cancel);
  StationCatalog.Item item=StationInstallerTest.item();
  StationFiles.Receipt received=new StationFiles.Receipt(server.artifact.length,"");
  StationInstaller installer=new StationInstaller(roms,records,(a,s,c)->{throw new AssertionError("RAW does not use archive decoder");});
  Path source=stage(roms,server.artifact),receipt=records.resolve("item_12345.json");Object inode=key(source);
  AtomicInteger events=new AtomicInteger();
  StationInstaller.Installed first=installer.installStaged(item,grant,source,received,cancel,(n,total)->{
   events.incrementAndGet();ok(!Files.exists(receipt),"Receipt is unpublished while RAW changes directory");
   ok(n==total&&total==server.artifact.length,"RAW preparation has no byte copy loop");
  });
  ok(events.get()==1,"RAW emits one completed move event");
  ok(!Files.exists(source),"The queue-owned source is consumed");
  ok(inode!=null&&inode.equals(key(first.launchPath)),"Installed file keeps the original inode; no second body write");
  ok(Arrays.equals(Files.readAllBytes(first.launchPath),server.artifact),"The whole payload is preserved by rename");
  ok(installer.find(item).launchPath.equals(first.launchPath),"The private receipt publishes the moved entrypoint");
  Path save=first.launchPath.getParent().resolve("user.sav");Files.write(save,new byte[]{42});
  byte[] previous=Files.readAllBytes(receipt);Path owner=first.launchPath.getParent().getParent().getParent();long before=generations(owner);
  StationApi.Cancellation stopped=new StationApi.Cancellation();stopped.cancel();Path beforeMove=stage(roms,server.artifact);
  rejects(()->installer.installStaged(item,grant,beforeMove,received,stopped,StationFiles.NO_PROGRESS));
  ok(Files.exists(beforeMove)&&Arrays.equals(previous,Files.readAllBytes(receipt)),"Cancellation before rename preserves staging and the previous receipt");
  Path afterMove=stage(roms,server.artifact);StationApi.Cancellation late=new StationApi.Cancellation();
  rejects(()->installer.installStaged(item,grant,afterMove,received,late,(n,t)->late.cancel()));
  ok(!Files.exists(afterMove)&&generations(owner)==before,"Cancellation after rename removes only the uncommitted generation");
  ok(Arrays.equals(previous,Files.readAllBytes(receipt))&&Files.exists(first.launchPath)&&Files.exists(save),"Failed update preserves the previous game and save");
  Path outside=root.resolve("external.chd");Files.write(outside,server.artifact);
  rejects(()->installer.installStaged(item,grant,outside,received,cancel,StationFiles.NO_PROGRESS));
  ok(Files.exists(outside),"Files outside owned staging cannot be consumed");
  Path wrong=stage(roms,Arrays.copyOf(server.artifact,server.artifact.length-1));
  rejects(()->installer.installStaged(item,grant,wrong,new StationFiles.Receipt(server.artifact.length-1,""),cancel,StationFiles.NO_PROGRESS));
  ok(Files.exists(wrong)&&Arrays.equals(previous,Files.readAllBytes(receipt)),"Incomplete staging cannot replace a committed game");
  Path link=stage(roms,server.artifact);Files.delete(link);Files.createSymbolicLink(link,outside);
  rejects(()->installer.installStaged(item,grant,link,received,cancel,StationFiles.NO_PROGRESS));
  ok(Files.exists(outside),"Symbolic staging preserves external data");
  Path secondSource=stage(roms,server.artifact);StationInstaller.Installed second=installer.installStaged(item,grant,secondSource,received,cancel,StationFiles.NO_PROGRESS);
  ok(!second.launchPath.equals(first.launchPath)&&Files.exists(first.launchPath)&&Files.exists(save),"Replacement uses a fresh generation and retains old saves");
  installer.uninstall(item.itemId);
  ok(!Files.exists(second.launchPath)&&Files.exists(save)&&Files.exists(first.launchPath),"Uninstall removes only the current receipt's game");
  byte[] archive=StationInstallerTest.zip(new String[]{"game.bin"},new byte[][]{server.artifact});
  server.descriptorOverride=StationInstallerTest.zipSpec(archive,"game.bin",server.artifact.length,1);server.artifact=archive;
  StationApi.Grant zipped=api.authorize(session,"item_12345",1,cancel);Path zipSource=stage(roms,archive);
  AtomicInteger reads=new AtomicInteger();StationInstaller zipInstaller=new StationInstaller(roms,records,(a,s,c)->{reads.incrementAndGet();new StationInstallerTest.ZipReader().read(a,s,c);});
  StationInstaller.Installed extracted=zipInstaller.installStaged(item,zipped,zipSource,new StationFiles.Receipt(archive.length,""),cancel,StationFiles.NO_PROGRESS);
  ok(reads.get()==1&&Files.exists(zipSource),"ZIP still extracts transactionally and leaves staging for queue cleanup");
  ok(Arrays.equals(Files.readAllBytes(extracted.launchPath),StationDownloadPerformanceTest.payload()),"Archive companions and entrypoint retain their bytes");
  server.descriptorOverride=null;server.artifact=StationDownloadPerformanceTest.payload();
  StationApi.Grant opaque=api.authorize(session,"item_12345",1,cancel);
  byte[] altered=server.artifact.clone();altered[0]=80;altered[1]=75;altered[2]=3;altered[3]=4;
  Path opaqueSource=stage(roms,altered);StationInstaller.Installed accepted=installer.installStaged(item,opaque,opaqueSource,new StationFiles.Receipt(altered.length,""),cancel,StationFiles.NO_PROGRESS);
  ok(Arrays.equals(Files.readAllBytes(accepted.launchPath),altered),"Completed RAW payload is opaque: no header or integrity reread after download");
  System.out.println("PASS "+checks+" RAW rename, ownership, cancellation, receipt, saves and archive checks");
 }
}
