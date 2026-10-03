package org.emulationstation.frontend.station;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.spec.X509EncodedKeySpec;
import java.lang.reflect.Constructor;
import org.json.JSONObject;

/** Isolated app_process test with generated public fixtures, never the installed app/session. */
public final class StationCapacityAndroidTest {
 public static void main(String[] args)throws Exception {
  Path dir=Paths.get(args[0]);KeyFactory factory=KeyFactory.getInstance("RSA");
  PublicKey authority=factory.generatePublic(new X509EncodedKeySpec(Files.readAllBytes(dir.resolve("authority.der"))));
  PublicKey device=factory.generatePublic(new X509EncodedKeySpec(Files.readAllBytes(dir.resolve("device-public.der"))));
  StationApi api=new StationApi((m,p,b,t,c)->{throw new AssertionError("No network in fixture");},new StationApi.Device(){
   public PublicKey publicKey(){return device;}public byte[] sign(byte[] payload){throw new AssertionError("No signing in fixture");}
   public String manufacturer(){return "fixture";}public String model(){return "capacity";}public int sdk(){return 34;}
  },()->0L,authority,"test-key");
  // Construct only a synthetic local session; production API still verifies the envelope signature and all owner fields.
  Constructor<StationApi.Session> constructor=StationApi.Session.class.getDeclaredConstructor(StationApi.class,String.class,String.class,String.class,String.class,long.class);
  constructor.setAccessible(true);StringBuilder id=new StringBuilder();for(int i=0;i<64;i++)id.append('2');
  StationApi.Session session=constructor.newInstance(api,"license_test_123",StationProtocol.deviceId(device.getEncoded()),id.toString(),"unused-test-token",Long.MAX_VALUE);
  byte[] envelope=Files.readAllBytes(dir.resolve("catalog-envelope.json"));long start=System.nanoTime();
  StationApi.CatalogSnapshot restored=api.restoreCatalog(envelope,session);long millis=(System.nanoTime()-start)/1000000;
  if(restored.catalog.items.size()!=40000||restored.catalog.find("capacity_139999")==null)throw new AssertionError("Truncated catalog");
  StationPublication publication=new StationPublication(restored.catalog);
  if(publication.rows.size()!=40000||publication.unsupportedCount!=0)throw new AssertionError("Wrong platform mapping");
  String highWater="unavailable";for(String line:Files.readAllLines(Paths.get("/proc/self/status"),StandardCharsets.UTF_8))if(line.startsWith("VmHWM:"))highWater=line.trim();
  JSONObject report=new JSONObject().put("synthetic",true).put("items",40000).put("envelopeBytes",envelope.length)
   .put("signatureParseMillis",millis).put("heapLimit",Runtime.getRuntime().maxMemory()).put("processHighWater",highWater)
   .put("fullApplicationUiTest",false).put("productionNetworkRequests",0);
  System.out.println("PASS Android 40000 signed rows: "+report.toString());
 }
}
