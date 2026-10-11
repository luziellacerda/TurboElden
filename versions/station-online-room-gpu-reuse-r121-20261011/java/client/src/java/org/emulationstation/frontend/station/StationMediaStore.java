package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import org.json.*;

/** Persistent app-owned media, separate from evictable cache; old pointer survives every failed update. */
public final class StationMediaStore {
 public interface Validator {void validate(Path file)throws Exception;}
 private final Path directory,index;
 private final Map<String,StationMediaCatalog.Entry> current=new LinkedHashMap<>();
 private final Map<String,String> checked=new HashMap<>();
 public StationMediaStore(Path directory)throws Exception {
  StationInstaller.directory(directory);
  this.directory=directory.toRealPath();index=this.directory.resolve("installed.json");
  if(Files.isRegularFile(index,LinkOption.NOFOLLOW_LINKS))try{
   JSONArray rows=new JSONObject(new String(StationFiles.readBounded(index,StationMediaCatalog.MAX_BODY),StandardCharsets.UTF_8)).getJSONArray("items");
   if(rows.length()>StationMediaCatalog.MAX_ITEMS)throw new IOException("Invalid media cache count");
   for(int i=0;i<rows.length();i++){StationMediaCatalog.Entry e=StationMediaCatalog.entry(rows.getJSONObject(i));current.put(e.asset,e);}
  }catch(IOException|JSONException invalid){current.clear();}
 }
 private Path file(StationMediaCatalog.Entry e){return directory.resolve(e.sha256+".mp4");}
 private static String stamp(Path path)throws IOException{return Files.size(path)+":"+Files.getLastModifiedTime(path,LinkOption.NOFOLLOW_LINKS).toMillis();}
 public synchronized Path cached(String asset)throws Exception {
  if(!StationMediaCatalog.safeAsset(asset))return null;
  StationMediaCatalog.Entry e=current.get(asset);if(e==null)return null;Path p=file(e);
  if(!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)||Files.size(p)!=e.sizeBytes)return null;
  String stamp=stamp(p);if(!stamp.equals(checked.get(e.sha256))){
   MessageDigest digest=MessageDigest.getInstance("SHA-256");try(InputStream stream=Files.newInputStream(p)){byte[] b=new byte[65536];int n;while((n=stream.read(b))!=-1)digest.update(b,0,n);}
   StringBuilder hex=new StringBuilder();for(byte b:digest.digest())hex.append(String.format(java.util.Locale.ROOT,"%02x",b&255));
   if(!e.sha256.equals(hex.toString()))return null;checked.put(e.sha256,stamp);
  }return p;
 }
 public synchronized boolean contains(StationMediaCatalog.Entry e)throws Exception {
  StationMediaCatalog.Entry old=current.get(e.asset);return old!=null&&old.sha256.equals(e.sha256)&&cached(e.asset)!=null;
 }
 public void publish(StationMediaCatalog.Entry entry,InputStream source,StationApi.Cancellation cancel,Validator validator)throws Exception {
  Path target=file(entry);
  if(Files.getFileStore(directory).getUsableSpace()<entry.sizeBytes+32L*1024*1024)throw new IOException("Insufficient media storage");
  StationFiles.replace(source,target,entry.sizeBytes,StationMediaCatalog.MAX_FILE,cancel,StationFiles.NO_PROGRESS,entry.sha256);
  validator.validate(target);cancel.check();
  synchronized(this){
   Map<String,StationMediaCatalog.Entry> next=new LinkedHashMap<>(current);next.put(entry.asset,entry);
   if(next.size()>StationMediaCatalog.MAX_ITEMS)throw new IOException("Too many cached clips");
   JSONArray rows=new JSONArray();for(StationMediaCatalog.Entry e:next.values())rows.put(e.json());
   byte[] bytes=new JSONObject().put("items",rows).toString().getBytes(StandardCharsets.UTF_8);
   StationFiles.replace(new ByteArrayInputStream(bytes),index,bytes.length,StationMediaCatalog.MAX_BODY,cancel,StationFiles.NO_PROGRESS);
   current.clear();current.putAll(next);checked.put(entry.sha256,stamp(target));
   // Only immutable files owned by THIS media cache; open Android file descriptors remain valid.
   Set<String> retain=new HashSet<>();for(StationMediaCatalog.Entry e:current.values())retain.add(e.sha256+".mp4");
   try(DirectoryStream<Path> paths=Files.newDirectoryStream(directory,"*.mp4")){
    for(Path p:paths)if(p.getFileName().toString().matches("[0-9a-f]{64}\\.mp4")&&!retain.contains(p.getFileName().toString())&&Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS))try{Files.deleteIfExists(p);}catch(IOException inUse){}
   }
  }
 }
}
