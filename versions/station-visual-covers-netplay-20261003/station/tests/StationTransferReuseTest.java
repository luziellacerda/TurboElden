package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
public final class StationTransferReuseTest {
 static int checks;
 static void ok(boolean value,String reason){checks++;if(!value)throw new AssertionError(reason);}
 static final byte[] DATA={1,2,3};
 static final class Input extends ByteArrayInputStream {
  final AtomicInteger disconnects;boolean closed;int reads;boolean failClose;
  Input(byte[] bytes,AtomicInteger disconnects){super(bytes);this.disconnects=disconnects;}
  @Override public synchronized int read(byte[] b,int o,int n){reads++;return super.read(b,o,n);}
  @Override public void close()throws IOException{closed=true;if(failClose)throw new IOException("Synthetic close failure");}
 }
 static void tls()throws Exception{
  AtomicInteger disconnects=new AtomicInteger();Input input=new Input(DATA,disconnects);
  StationHttp.ResponseBody body=new StationHttp.ResponseBody(input,DATA.length);StationApi.Cancellation cancel=new StationApi.Cancellation();
  ok(!body.finished,"Unread body not poolable");byte[] bytes=new byte[8];ok(body.read(bytes)==3&&!body.finished,"Length alone is not EOF proof");ok(body.read(bytes)==-1&&body.finished,"Complete EOF with exact length is poolable");
  StationHttp.closeResponse(body,cancel,disconnects::incrementAndGet);ok(disconnects.get()==0&&input.closed,"Completed response closes stream without destroying pooled TLS socket");
  disconnects.set(0);input=new Input(DATA,disconnects);body=new StationHttp.ResponseBody(input,3);body.read();int before=input.reads;
  StationHttp.closeResponse(body,new StationApi.Cancellation(),disconnects::incrementAndGet);ok(disconnects.get()==1&&input.closed&&input.reads==before,"Partial body disconnects and never drains extra bytes");
  disconnects.set(0);input=new Input(DATA,disconnects);body=new StationHttp.ResponseBody(input,4);while(body.read(bytes)>=0){}
  ok(!body.finished,"Truncated declared content cannot be pooled even after EOF");StationHttp.closeResponse(body,new StationApi.Cancellation(),disconnects::incrementAndGet);ok(disconnects.get()==1,"Truncated response disconnects");
  disconnects.set(0);input=new Input(DATA,disconnects);body=new StationHttp.ResponseBody(input,-1);while(body.read(bytes)>=0){}
  cancel=new StationApi.Cancellation();cancel.cancel();StationHttp.closeResponse(body,cancel,disconnects::incrementAndGet);ok(disconnects.get()==1,"Cancellation overrides completed-body reuse");
  disconnects.set(0);input=new Input(DATA,disconnects);input.failClose=true;body=new StationHttp.ResponseBody(input,3);while(body.read(bytes)>=0){}
  try{StationHttp.closeResponse(body,new StationApi.Cancellation(),disconnects::incrementAndGet);throw new AssertionError("Close error swallowed");}catch(IOException expected){ok(disconnects.get()==1,"Close failure disconnects pooled candidate");}
  disconnects.set(0);body=new StationHttp.ResponseBody(new InputStream(){public int read()throws IOException{throw new IOException("Synthetic read failure");}},3);
  try{body.read();throw new AssertionError();}catch(IOException expected){StationHttp.closeResponse(body,new StationApi.Cancellation(),disconnects::incrementAndGet);ok(disconnects.get()==1,"Read failure disconnects");}
 }
 static StationArtifact spec()throws Exception{return StationArtifact.parse(StationApiTest.descriptor(DATA));}
 static void exact(Path root)throws Exception{
  Files.createDirectories(root);StationArtifact spec=spec();Path exact=root.resolve(spec.fileName);Files.write(exact,DATA);AtomicInteger walks=new AtomicInteger();
  Path found=StationExistingArtifact.find(root,spec,new StationApi.Cancellation(),(directory,visitor)->{walks.incrementAndGet();throw new AssertionError("Exact artifact must precede tree scan");});
  ok(found.equals(exact)&&walks.get()==0,"Matching exact file returns without any directory traversal");
  StationApi.Cancellation stopped=new StationApi.Cancellation();stopped.cancel();try{StationExistingArtifact.find(root,spec,stopped,(directory,visitor)->walks.incrementAndGet());throw new AssertionError();}catch(InterruptedIOException expected){ok(walks.get()==0,"Cancelled lookup performs no scan");}
  Files.write(exact,new byte[]{3,2,1});Path other=root.resolve("other.bin");Files.write(other,DATA);
  found=StationExistingArtifact.find(root,spec,new StationApi.Cancellation(),(directory,visitor)->{walks.incrementAndGet();visitor.visitFile(other,Files.readAttributes(other,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS));});
  ok(found.equals(other)&&walks.get()==1,"Same name and size but wrong SHA cannot bypass identity check");
  List<Path> ordered=new ArrayList<>();for(int i=0;i<8;i++){Path file=root.resolve("candidate-"+i);Files.write(file,i==7?DATA:new byte[]{7,7,7});ordered.add(file);}
  StationExistingArtifact.Search traversal=(directory,visitor)->{for(Path file:ordered)if(visitor.visitFile(file,Files.readAttributes(file,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS))==FileVisitResult.TERMINATE)break;};
  ok(StationExistingArtifact.find(root,spec,new StationApi.Cancellation(),traversal)==null,"Already-hashed exact file counts toward eight-candidate budget");
  Files.delete(exact);ok(StationExistingArtifact.find(root,spec,new StationApi.Cancellation(),traversal).equals(ordered.get(7)),"Without exact candidate all eight fallback hashes remain available");
  Files.write(exact,new byte[]{1});ok(StationExistingArtifact.find(root,spec,new StationApi.Cancellation(),traversal).equals(ordered.get(7)),"Wrong-size exact file does not consume hashing budget");
 }
 public static void main(String[] args)throws Exception{tls();exact(Paths.get(args[0]));System.out.println("PASS "+checks+" TLS response reuse and exact-artifact-first checks");}
}
