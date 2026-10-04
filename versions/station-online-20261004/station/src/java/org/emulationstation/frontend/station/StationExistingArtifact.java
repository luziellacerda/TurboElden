package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;

/** User-requested reuse only. File names never establish game identity; signed size/hash do. */
public final class StationExistingArtifact {
 private StationExistingArtifact(){}
 interface Search {void walk(Path directory,SimpleFileVisitor<Path> visitor)throws IOException;}
 static Path find(Path platformDirectory,StationArtifact spec,StationApi.Cancellation cancel)throws Exception {
  return find(platformDirectory,spec,cancel,(directory,visitor)->Files.walkFileTree(directory,EnumSet.noneOf(FileVisitOption.class),6,visitor));
 }
 static Path find(Path platformDirectory,StationArtifact spec,StationApi.Cancellation cancel,Search search)throws Exception {
  cancel.check();StationInstaller.checkParents(platformDirectory);
  if(!Files.isDirectory(platformDirectory,LinkOption.NOFOLLOW_LINKS))return null;
  List<Path> candidates=new ArrayList<>();
  // Check the exact server file name first; scanning is bounded and never follows links.
  Path exact=platformDirectory.resolve(spec.fileName);
  // Upstream 1dc8c381: prove the exact file before traversing thousands of unrelated files.
  boolean checkedExact=Files.isRegularFile(exact,LinkOption.NOFOLLOW_LINKS)&&Files.size(exact)==spec.sizeBytes;
  if(checkedExact){StationInstaller.checkParents(exact);if(StationInstaller.digest(exact,cancel).equals(spec.sha256))return exact;}
  final int maximumCandidates=checkedExact?7:8;
  final int[] visited={0};
  search.walk(platformDirectory,new SimpleFileVisitor<Path>(){
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes attrs)throws IOException{
    cancel.check();return ++visited[0]>4096?FileVisitResult.TERMINATE:FileVisitResult.CONTINUE;
   }
   public FileVisitResult visitFile(Path file,BasicFileAttributes attrs)throws IOException{
    cancel.check();if(++visited[0]>4096||candidates.size()>=maximumCandidates)return FileVisitResult.TERMINATE;
    if(attrs.isRegularFile()&&!attrs.isSymbolicLink()&&attrs.size()==spec.sizeBytes&&!file.equals(exact))candidates.add(file);
    return FileVisitResult.CONTINUE;
   }
   public FileVisitResult visitFileFailed(Path file,IOException error)throws IOException{cancel.check();return FileVisitResult.CONTINUE;}
  });
  long remaining=Math.max(spec.sizeBytes,512L*1024*1024)-(checkedExact?spec.sizeBytes:0);
  for(Path file:candidates){
   cancel.check();if(spec.sizeBytes>remaining)break;remaining-=spec.sizeBytes;
   StationInstaller.checkParents(file);
   if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)!=spec.sizeBytes)continue;
   if(StationInstaller.digest(file,cancel).equals(spec.sha256))return file;
  }
  return null;
 }
}
