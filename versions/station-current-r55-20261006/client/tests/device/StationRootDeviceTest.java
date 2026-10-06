package org.emulationstation.frontend.station;
import java.nio.file.*;
import java.io.IOException;
import java.nio.file.attribute.PosixFilePermissions;
public final class StationRootDeviceTest {
 public static void main(String[] args)throws Exception {
  Path root=Files.createTempDirectory(Paths.get(args[0]),"roots-");
  Path actual=Files.createDirectory(root.resolve("actual"));
  Path alias=root.resolve("android-alias");Files.createSymbolicLink(alias,actual);
  if(!alias.toRealPath().equals(actual.toRealPath()))throw new AssertionError("Canonical root");
  Path child=StationStorage.prepareRoot(alias.resolve("missing-home/games"));
  if(!Files.isDirectory(child))throw new AssertionError("Root descendants");
  if(!child.equals(actual.resolve("missing-home/games")))throw new AssertionError("Missing root under OS alias");
  if(StationStorage.usableBytes(child)<=0)throw new AssertionError("Android usable space query");
  Path save=child.resolve("save.srm");Files.write(save,new byte[]{42});
  if(!StationStorage.prepareRoot(alias.resolve("missing-home/games")).equals(child)||Files.readAllBytes(save)[0]!=42)throw new AssertionError("Repeated initialization preserves save");
  try(java.util.stream.Stream<Path> entries=Files.list(child)){if(entries.count()!=1)throw new AssertionError("Probe leaked");}
  Path outside=Files.createDirectory(root.resolve("outside"));
  Path unsafe=child.resolve("redirect");Files.createSymbolicLink(unsafe,outside);
  try{StationInstaller.directory(unsafe.resolve("unexpected"));throw new AssertionError("Child link accepted");}catch(IOException expected){}
  if(Files.exists(outside.resolve("unexpected")))throw new AssertionError("Outside write");
  Path locked=Files.createDirectory(root.resolve("locked"));
  Files.setPosixFilePermissions(locked,PosixFilePermissions.fromString("r-x------"));
  try{StationStorage.prepareRoot(locked.resolve("games"));throw new AssertionError("Missing permission accepted");}
  catch(StationStorage.Failure expected){if(!expected.reason.equals("STORAGE_ACCESS_DENIED"))throw new AssertionError("Wrong permission error");}
  finally{Files.setPosixFilePermissions(locked,PosixFilePermissions.fromString("rwx------"));}
  Path recovered=StationStorage.prepareRoot(locked.resolve("games"));
  if(!Files.isDirectory(recovered))throw new AssertionError("Retry after permission restored");
  Files.delete(recovered);Files.delete(locked);Files.delete(save);Files.delete(unsafe);Files.delete(child);Files.delete(child.getParent());Files.delete(alias);Files.delete(actual);Files.delete(outside);Files.delete(root);
  System.out.println("PASS 10 Android fresh-root, usable-space, alias, preservation, permission-retry and descendant-link checks");
 }
}
