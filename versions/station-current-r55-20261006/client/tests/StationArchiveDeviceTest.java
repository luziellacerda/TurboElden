package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
public final class StationArchiveDeviceTest {
 static final class Sink implements StationInstaller.Sink {
  int files;long bytes,current,expected;boolean directory;Set<String> names=new HashSet<>();
  public void begin(byte[] data,long size,boolean dir)throws Exception{
   String name=new String(data,StandardCharsets.UTF_8);if(dir&&name.endsWith("/"))name=name.substring(0,name.length()-1);
   StationArtifact.relativePath(name,4096);if(!names.add(name.toLowerCase(Locale.ROOT)))throw new IOException("Duplicate");
   current=0;expected=size;directory=dir;if(!dir)files++;
  }
  public void data(byte[] data,int length)throws Exception{if(directory||length>expected-current)throw new IOException("Size mismatch");current+=length;bytes+=length;}
  public void end()throws Exception{if(!directory&&current!=expected)throw new IOException("Truncated");}
 }
 public static void main(String[] args)throws Exception{
  Path root=Paths.get(args[0]);StationArchive reader=new StationArchive();int checks=0;
  for(String name:new String[]{"valid.zip","valid.7z","stored.rar"}){
   Sink sink=new Sink();reader.read(root.resolve(name),sink,new StationApi.Cancellation());
   if(sink.files<1||sink.bytes<1)throw new AssertionError("Empty "+name);checks++;
   System.out.println("PASS native "+name+" files="+sink.files+" bytes="+sink.bytes);
  }
  for(String name:new String[]{"traversal.zip","symlink.zip","duplicate.zip","truncated.zip"}){
   try{reader.read(root.resolve(name),new Sink(),new StationApi.Cancellation());throw new AssertionError("Accepted "+name);}
   catch(IOException e){checks++;System.out.println("PASS native rejected "+name);}
  }
  StationApi.Cancellation cancel=new StationApi.Cancellation();cancel.cancel();
  try{reader.read(root.resolve("valid.7z"),new Sink(),cancel);throw new AssertionError("Ignored cancellation");}catch(InterruptedIOException expected){checks++;}
  System.out.println("PASS "+checks+" native Android archive checks");
 }
}
