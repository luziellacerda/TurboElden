package org.emulationstation.frontend.station;
import java.nio.file.*;
import java.util.*;
import org.json.*;
public final class StationArcadePackageTest {
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  byte[] game=StationInstallerTest.zip(new String[]{"chip-p1.bin","chip-c1.bin"},new byte[][]{{1,2,3},{4,5,6}});
  byte[] bios=StationInstallerTest.zip(new String[]{"synthetic-bios.bin"},new byte[][]{{7,8,9}});
  byte[] outer=StationInstallerTest.zip(new String[]{"synthetic.zip","neogeo.zip"},new byte[][]{game,bios});
  StationApiTest.Fake server=new StationApiTest.Fake();server.artifact=outer;
  server.descriptorOverride=StationInstallerTest.zipSpec(outer,"synthetic.zip",game.length+bios.length,2);
  StationApi api=server.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  StationApi.Session session=api.openSession(server.license,cancel);
  StationApi.Grant grant=api.authorize(session,"item_12345",1,cancel);
  Path staging=root.resolve("delivery.zip");api.downloadToStaging(grant,staging,100000,cancel,StationFiles.NO_PROGRESS);
  JSONObject data=StationApiTest.item().put("platform","neogeo");
  StationCatalog.Item item=StationCatalog.fromVerifiedPayload(StationApiTest.catalog(data)).items.get(0);
  StationInstaller installer=new StationInstaller(root.resolve("roms"),root.resolve("receipts"),new StationInstallerTest.ZipReader());
  StationInstaller.Installed result=installer.install(item,grant,staging,cancel,StationFiles.NO_PROGRESS);
  if(!result.launchPath.getFileName().toString().equals("synthetic.zip"))throw new AssertionError("ZIP launch");
  if(!Arrays.equals(Files.readAllBytes(result.launchPath),game))throw new AssertionError("Game ZIP changed");
  if(!Arrays.equals(Files.readAllBytes(result.launchPath.getParent().resolve("neogeo.zip")),bios))throw new AssertionError("BIOS ZIP changed");
  if(Files.exists(result.launchPath.getParent().resolve("chip-p1.bin")))throw new AssertionError("Nested ZIP extracted");
  if(!installer.find(item).launchPath.equals(result.launchPath))throw new AssertionError("Receipt lost");
  System.out.println("PASS 5 Neo Geo nested ZIP and BIOS installer checks");
 }
}
