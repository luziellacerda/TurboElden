package org.emulationstation.frontend.station;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;

/** No legacy file traversal or hashing before transfer. Installed receipts remain authoritative. */
public final class StationExistingArtifact {
 private StationExistingArtifact(){}
 interface Search {void walk(Path directory,SimpleFileVisitor<Path> visitor)throws IOException;}
 static Path find(Path platformDirectory,StationArtifact spec,StationApi.Cancellation cancel)throws Exception {
  cancel.check();
  return null;
 }
 static Path find(Path platformDirectory,StationArtifact spec,StationApi.Cancellation cancel,Search search)throws Exception {
  return find(platformDirectory,spec,cancel);
 }
}
