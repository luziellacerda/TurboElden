package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
public final class StationFilesTest {
 static int checks;
 interface Op {void run() throws Exception;}
 static void ok(boolean v,String m){checks++;if(!v)throw new AssertionError(m);}
 static void fails(Op op)throws Exception{try{op.run();throw new AssertionError("Expected rejection");}catch(IOException e){checks++;}}
 public static void main(String[]a)throws Exception{
  Path dir=Paths.get(a[0]);Files.createDirectories(dir);Path file=dir.resolve("cached.bin");
  byte[] before={4,5,6};byte[] after={1,2,3};Files.write(file,before);
  fails(()->StationFiles.replace(new ByteArrayInputStream(new byte[]{1,2}),file,3,10,()->false,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(file)),"Truncation destroyed cache");
  fails(()->StationFiles.replace(new ByteArrayInputStream(new byte[]{1,2,3,4}),file,3,10,()->false,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(file)),"Overrun destroyed cache");
  fails(()->StationFiles.replace(new ByteArrayInputStream(after),file,3,10,()->true,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(file)),"Cancel destroyed cache");
  InputStream broken=new InputStream(){public int read()throws IOException{throw new IOException("Lost connection");}};
  fails(()->StationFiles.replace(broken,file,3,10,()->false,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(file)),"Failure destroyed cache");
  fails(()->StationFiles.replace(new ByteArrayInputStream(after),file,3,10,()->false,(n,t)->{},"0".repeat(64)));
  ok(Arrays.equals(before,Files.readAllBytes(file)),"Bad digest destroyed cache");
  AtomicBoolean cancel=new AtomicBoolean();
  fails(()->StationFiles.replace(new ByteArrayInputStream(after),file,3,10,cancel::get,(n,t)->cancel.set(true)));
  ok(Arrays.equals(before,Files.readAllBytes(file)),"Late cancel destroyed cache");
  StationFiles.Receipt receipt=StationFiles.replace(new ByteArrayInputStream(after),file,3,10,()->false,(n,t)->{});
  ok(receipt.size==3&&receipt.sha256.equals("039058c6f2c0cb492c533b0a4d14ef77cc0f78abccced5287d84a1a2011cfb81"),"Receipt mismatch");
  ok(Arrays.equals(after,Files.readAllBytes(file)),"Success missing");
  try(java.util.stream.Stream<Path>s=Files.list(dir)){ok(s.noneMatch(p->p.toString().endsWith(".part")),"Partial leaked");}
  fails(()->StationFiles.imageExtension("<html>error</html>".getBytes()));
  ok(StationFiles.imageExtension(new byte[]{(byte)137,80,78,71,13,10,26,10}).equals("png"),"PNG");
  ok(StationFiles.archiveType(new byte[]{80,75,3,4}).equals("zip"),"ZIP");
  ok(StationFiles.archiveType(after).isEmpty(),"Raw misidentified");
  Path artifact=dir.resolve("artifact.bin");Files.write(artifact,before);
  fails(()->StationFiles.replaceArtifact(new ByteArrayInputStream(new byte[]{1,2}),artifact,3,3,()->false,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(artifact)),"Artifact truncation preserves existing bytes");
  fails(()->StationFiles.replaceArtifact(new ByteArrayInputStream(new byte[]{1,2,3,4}),artifact,3,3,()->false,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(artifact)),"Artifact overrun preserves existing bytes");
  fails(()->StationFiles.replaceArtifact(new ByteArrayInputStream(after),artifact,3,3,()->true,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(artifact)),"Artifact early cancellation preserves existing bytes");
  AtomicBoolean lateArtifactCancel=new AtomicBoolean();
  fails(()->StationFiles.replaceArtifact(new ByteArrayInputStream(after),artifact,3,3,lateArtifactCancel::get,(n,t)->lateArtifactCancel.set(true)));
  ok(Arrays.equals(before,Files.readAllBytes(artifact)),"Artifact late cancellation cannot publish buffered bytes");
  fails(()->StationFiles.replaceArtifact(new InputStream(){public int read()throws IOException{throw new IOException("Lost artifact connection");}},artifact,3,3,()->false,(n,t)->{}));
  ok(Arrays.equals(before,Files.readAllBytes(artifact)),"Artifact IO failure preserves existing bytes");
  byte[] large=new byte[3*256*1024+17];for(int i=0;i<large.length;i++)large[i]=(byte)(i*31+9);
  StationFiles.Receipt gameReceipt=StationFiles.replaceArtifact(new ByteArrayInputStream(large),artifact,large.length,large.length,()->false,(n,t)->{});
  ok(gameReceipt.size==large.length&&gameReceipt.sha256.isEmpty(),"Artifact receipt explicitly reports no calculated content hash");
  ok(Arrays.equals(large,Files.readAllBytes(artifact)),"Buffered artifact publication flushes the final incomplete output block");
  try(java.util.stream.Stream<Path>s=Files.list(dir)){ok(s.noneMatch(p->p.toString().endsWith(".part")),"Artifact transaction leaves no partials");}
  System.out.println("PASS "+checks+" file safety checks");
 }
}
