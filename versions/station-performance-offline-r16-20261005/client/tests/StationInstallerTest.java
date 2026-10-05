package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.zip.*;
import org.json.*;

public final class StationInstallerTest {
 static int checks;
 interface Op{void run()throws Exception;}
 static void ok(boolean condition,String name){checks++;if(!condition)throw new AssertionError(name);}
 static void fails(Op op)throws Exception{try{op.run();throw new AssertionError("Expected rejection");}catch(IOException|JSONException|IllegalArgumentException e){checks++;}}
 static JSONObject copy(JSONObject object)throws Exception{return new JSONObject(object.toString());}
 static StationCatalog.Item item()throws Exception{return StationCatalog.fromVerifiedPayload(StationApiTest.catalog(StationApiTest.item())).items.get(0);}
 static byte[] zip(String[] names,byte[][] data)throws Exception{
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();try(ZipOutputStream out=new ZipOutputStream(bytes)){
   for(int i=0;i<names.length;i++){out.putNextEntry(new ZipEntry(names[i]));out.write(data[i]);out.closeEntry();}
  }return bytes.toByteArray();
 }
 static final class ZipReader implements StationInstaller.Reader {
  public void read(Path archive,StationInstaller.Sink sink,StationApi.Cancellation cancel)throws Exception{
   try(ZipFile input=new ZipFile(archive.toFile())){
    Enumeration<? extends ZipEntry> entries=input.entries();
    while(entries.hasMoreElements()){ZipEntry entry=entries.nextElement();sink.begin(entry.getName().getBytes(StandardCharsets.UTF_8),entry.getSize(),entry.isDirectory());
     if(!entry.isDirectory())try(InputStream in=input.getInputStream(entry)){byte[] buffer=new byte[1024];int n;while((n=in.read(buffer))!=-1)if(n>0)sink.data(buffer,n);}
     sink.end();
    }
   }
  }
 }
 static JSONObject zipSpec(byte[] bytes,String launch,long expanded,int count)throws Exception{
  return StationApiTest.descriptor(bytes).put("fileName","bundle.zip").put("format","zip").put("launchPath",launch).put("expandedSizeBytes",expanded).put("fileCount",count);
 }
 public static void main(String[] args)throws Exception{
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  StationApiTest.Fake server=new StationApiTest.Fake();StationApi api=server.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  StationApi.Session session=api.openSession(server.license,cancel);
  JSONObject raw=StationApiTest.descriptor(server.artifact);
  ok(StationArtifact.parse(raw).fileName.equals("game.bin"),"Typed descriptor");
  for(String key:new String[]{"fileName","sizeBytes","sha256","format","launchPath","expandedSizeBytes","fileCount"}){
   JSONObject invalid=copy(raw);invalid.remove(key);fails(()->StationArtifact.parse(invalid));
  }
  for(String path:new String[]{"../game.bin","/absolute","C:/file","a//b","a/./b","a/../b","a\\b","bad\nname"}){
   fails(()->StationArtifact.relativePath(path,512));
  }
  for(String key:new String[]{"sizeBytes","expandedSizeBytes","fileCount"}){
   for(Object value:new Object[]{0,-1,1.2,"3",Long.MAX_VALUE}){
    JSONObject invalid=copy(raw).put(key,value);fails(()->StationArtifact.parse(invalid));
   }
  }
  fails(()->StationArtifact.parse(copy(raw).put("sha256","f".repeat(63))));
  fails(()->StationArtifact.parse(copy(raw).put("sha256","A".repeat(64))));
  fails(()->StationArtifact.parse(copy(raw).put("launchPath","other.bin")));
  fails(()->StationArtifact.parse(copy(raw).put("format","exe")));
  server.omitDescriptor=true;fails(()->api.authorize(session,"item_12345",1,cancel));server.omitDescriptor=false;
  server.itemRevision=2;fails(()->api.authorize(session,"item_12345",1,cancel));server.itemRevision=1;
  server.descriptorOverride=copy(raw).put("fileName","../escape.bin");fails(()->api.authorize(session,"item_12345",1,cancel));server.descriptorOverride=null;
  Path staging=root.resolve("verified.bin");Files.write(staging,new byte[]{99});
  StationApi.Grant corrupted=api.authorize(session,"item_12345",1,cancel);server.artifact=new byte[]{9,9,9};
  api.downloadToStaging(corrupted,staging,100,cancel,StationFiles.NO_PROGRESS);
  ok(Arrays.equals(Files.readAllBytes(staging),new byte[]{9,9,9}),"Explicit no-content-hash policy accepts same-size game payload");
  int attempts=server.artifactCalls;fails(()->api.downloadToStaging(corrupted,staging,100,cancel,StationFiles.NO_PROGRESS));ok(server.artifactCalls==attempts,"Consumed transfer grant not retried");
  server.artifact=new byte[]{1,2,3};StationApi.Grant valid=api.authorize(session,"item_12345",1,cancel);
  attempts=server.artifactCalls;fails(()->api.downloadToStaging(valid,staging,2,cancel,StationFiles.NO_PROGRESS));ok(attempts==server.artifactCalls,"Local size limit before consuming grant");
  api.downloadToStaging(valid,staging,100,cancel,StationFiles.NO_PROGRESS);
  StationInstaller installer=new StationInstaller(root.resolve("roms"),root.resolve("records"),new ZipReader());
  ok(installer.find(item())==null,"No installation inferred from files");
  StationInstaller.Installed installed=installer.install(item(),valid,staging,cancel,StationFiles.NO_PROGRESS);
  ok(Files.readAllBytes(installed.launchPath).length==3,"Raw installed");
  ok(installer.find(item()).launchPath.equals(installed.launchPath),"Committed receipt resolves launch");
  Files.write(staging,new byte[]{5,5,5});installed=installer.install(item(),valid,staging,cancel,StationFiles.NO_PROGRESS);
  ok(Arrays.equals(Files.readAllBytes(installed.launchPath),new byte[]{5,5,5}),"Explicit no-content-hash policy accepts same-size RAW replacement");
  ok(installer.find(item()).launchPath.equals(installed.launchPath),"Replacement still requires a committed receipt");
  Files.write(staging,server.artifact);
  StationApi.Cancellation stopped=new StationApi.Cancellation();stopped.cancel();fails(()->installer.install(item(),valid,staging,stopped,StationFiles.NO_PROGRESS));
  ok(installer.find(item()).launchPath.equals(installed.launchPath),"Cancellation preserves previous installed game");
  Path saved=installed.launchPath.getParent().resolve("save-user.dat");Files.write(saved,new byte[]{42});
  Path receipt=root.resolve("records/item_12345.json");
  JSONObject tombstone=new JSONObject(new String(Files.readAllBytes(receipt),StandardCharsets.UTF_8)).put("removing",true);
  Files.write(receipt,tombstone.toString().getBytes(StandardCharsets.UTF_8));
  ok(installer.find(item())==null,"Interrupted uninstall stays hidden and retryable");
  installer.uninstall("item_12345");ok(!Files.exists(installed.launchPath)&&Files.exists(saved)&&installer.find(item())==null,"Uninstall preserves unknown saves");
  byte[] cue="FILE \"game.bin\" BINARY\n".getBytes(StandardCharsets.UTF_8);
  byte[] archive=zip(new String[]{"disc/game.cue","disc/game.bin"},new byte[][]{cue,new byte[]{1,2,3}});
  server.artifact=archive;server.descriptorOverride=zipSpec(archive,"disc/game.cue",cue.length+3,2);
  StationApi.Grant zipped=api.authorize(session,"item_12345",1,cancel);api.downloadToStaging(zipped,staging,10000,cancel,StationFiles.NO_PROGRESS);
  installed=installer.install(item(),zipped,staging,cancel,StationFiles.NO_PROGRESS);Path original=installed.launchPath;
  ok(installed.launchPath.getFileName().toString().equals("game.cue"),"Exact signed BIN CUE launch path");
  byte[] evil=zip(new String[]{"../escape.bin"},new byte[][]{{1,2,3}});server.artifact=evil;server.descriptorOverride=zipSpec(evil,"game.bin",3,1);
  StationApi.Grant traversal=api.authorize(session,"item_12345",1,cancel);api.downloadToStaging(traversal,staging,10000,cancel,StationFiles.NO_PROGRESS);
  fails(()->installer.install(item(),traversal,staging,cancel,StationFiles.NO_PROGRESS));
  ok(installer.find(item()).launchPath.equals(original),"Traversal failure preserves valid install");
  byte[] missing=zip(new String[]{"disc/game.cue"},new byte[][]{cue});server.artifact=missing;server.descriptorOverride=zipSpec(missing,"disc/game.cue",cue.length,1);
  StationApi.Grant missingBin=api.authorize(session,"item_12345",1,cancel);api.downloadToStaging(missingBin,staging,10000,cancel,StationFiles.NO_PROGRESS);
  fails(()->installer.install(item(),missingBin,staging,cancel,StationFiles.NO_PROGRESS));
  byte[] aliases=zip(new String[]{"Game.bin","game.bin"},new byte[][]{{1},{2}});server.artifact=aliases;server.descriptorOverride=zipSpec(aliases,"Game.bin",2,2);
  StationApi.Grant alias=api.authorize(session,"item_12345",1,cancel);api.downloadToStaging(alias,staging,10000,cancel,StationFiles.NO_PROGRESS);
  fails(()->installer.install(item(),alias,staging,cancel,StationFiles.NO_PROGRESS));
  ok(installer.find(item()).launchPath.equals(original),"Case aliases cannot overwrite previous game");
  Path owner=original.getParent().getParent().getParent().getParent();
  try(java.util.stream.Stream<Path> dirs=Files.list(owner)){ok(dirs.filter(p->p.getFileName().toString().startsWith("install-")).count()==3,"Failed transactions cleaned; committed and retained-save generations preserved");}
  Files.delete(original);ok(installer.find(item())==null,"Missing committed file is not installed");
  System.out.println("PASS "+checks+" descriptor and installation checks");
 }
}
