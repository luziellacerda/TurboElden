package org.emulationstation.frontend.station;
import java.nio.file.*;
import java.io.IOException;
public final class StationRootDeviceTest {
 public static void main(String[] args)throws Exception {
  Path root=Files.createTempDirectory(Paths.get(args[0]),"roots-");
  Path actual=Files.createDirectory(root.resolve("actual"));
  Path alias=root.resolve("android-alias");Files.createSymbolicLink(alias,actual);
  if(!alias.toRealPath().equals(actual.toRealPath()))throw new AssertionError("Canonical root");
  Path child=StationInstaller.directory(alias.toRealPath().resolve("games"));
  if(!Files.isDirectory(child))throw new AssertionError("Root descendants");
  Path outside=Files.createDirectory(root.resolve("outside"));
  Path unsafe=child.resolve("redirect");Files.createSymbolicLink(unsafe,outside);
  try{StationInstaller.directory(unsafe.resolve("unexpected"));throw new AssertionError("Child link accepted");}catch(IOException expected){}
  if(Files.exists(outside.resolve("unexpected")))throw new AssertionError("Outside write");
  Files.delete(unsafe);Files.delete(child);Files.delete(alias);Files.delete(actual);Files.delete(outside);Files.delete(root);
  System.out.println("PASS 4 Android canonical-root and descendant-link checks");
 }
}
