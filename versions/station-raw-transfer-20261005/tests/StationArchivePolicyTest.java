package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
import java.nio.charset.StandardCharsets;

/** Calls the real JNI extractor in separate JVMs with original/CRC-free bridges. */
public final class StationArchivePolicyTest {
 static int checks;
 static void ok(boolean yes,String why){checks++;if(!yes)throw new AssertionError(why);}
 static final class MemorySink implements StationInstaller.Sink {
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();String name;long size;int entries;
  public void begin(byte[] name,long size,boolean dir)throws Exception{this.name=new String(name,StandardCharsets.UTF_8);this.size=size;entries++;ok(!dir,"Test is a regular member");}
  public void data(byte[] data,int length){bytes.write(data,0,length);}
  public void end(){ok(bytes.size()==size,"Decoded length matches the member");}
 }
 static byte[] archive(byte[] data)throws Exception {
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();CRC32 crc=new CRC32();crc.update(data);
  try(ZipOutputStream out=new ZipOutputStream(bytes)) {
   ZipEntry entry=new ZipEntry("games/ação.bin");entry.setMethod(ZipEntry.STORED);entry.setSize(data.length);entry.setCompressedSize(data.length);entry.setCrc(crc.getValue());
   out.putNextEntry(entry);out.write(data);out.closeEntry();
  }
  return bytes.toByteArray();
 }
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);boolean skip=args[1].equals("skip");
  byte[] payload=StationDownloadPerformanceTest.payload(),valid=archive(payload);
  Path file=root.resolve("valid.zip");Files.write(file,valid);MemorySink good=new MemorySink();
  new StationArchive().read(file,good,new StationApi.Cancellation());
  ok(good.entries==1&&good.name.equals("games/ação.bin")&&Arrays.equals(good.bytes.toByteArray(),payload),"Valid UTF8 ZIP extracts with the JNI implementation");
  byte[] altered=valid.clone();for(int i=14;i<18;i++)altered[i]^=0x55;
  for(int i=0;i<altered.length-20;i++)if(altered[i]==80&&altered[i+1]==75&&altered[i+2]==1&&altered[i+3]==2){for(int j=i+16;j<i+20;j++)altered[j]^=0x55;break;}
  Path crcOnly=root.resolve("crc-only.zip");Files.write(crcOnly,altered);MemorySink ignored=new MemorySink();
  try {
   new StationArchive().read(crcOnly,ignored,new StationApi.Cancellation());
   ok(skip,"Only the requested CRC-free bridge accepts a CRC mismatch");
   ok(Arrays.equals(ignored.bytes.toByteArray(),payload),"CRC-free extraction preserves all received bytes");
  }catch(IOException error){ok(!skip,"Original JNI rejects the same CRC-only mismatch");}
  Path invalid=root.resolve("not-an-archive");Files.write(invalid,new byte[]{1,2,3,4});
  try {new StationArchive().read(invalid,new MemorySink(),new StationApi.Cancellation());throw new AssertionError("Expected decoding failure");}
  catch(IOException expected){checks++;}
  System.out.println("PASS "+checks+" real JNI ZIP checks; policy="+args[1]);
 }
}
