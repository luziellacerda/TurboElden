package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.json.*;

/** Synthetic signed fixtures only. No production API or private identity is used. */
public final class StationCapacityTest {
 static int checks;
 interface Op {void run()throws Exception;}
 static void ok(boolean result,String message){checks++;if(!result)throw new AssertionError(message);}
 static void reject(Op op)throws Exception {try{op.run();throw new AssertionError("Expected rejection");}catch(IOException|java.security.GeneralSecurityException|JSONException expected){checks++;}}
 public static void main(String[] args)throws Exception {
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  String[] platforms={"snes","snesbr","megadrive","megadrivebr"};
  JSONArray rows=new JSONArray();StringBuilder name=new StringBuilder();for(int i=0;i<120;i++)name.append('\u6f22');
  for(int i=0;i<40000;i++)rows.put(StationApiTest.item().put("itemId","capacity_"+(100000+i)).put("coverId","artwork_"+(100000+i)).put("name",name.toString()).put("platform",platforms[i%4]));
  StationApiTest.Fake fake=new StationApiTest.Fake();fake.catalogItems=rows;fake.escapeCatalogUnicode=true;
  StationApi api=fake.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
  StationApi.Session session=api.openSession(fake.license,cancel);
  long start=System.nanoTime();StationApi.CatalogSnapshot snapshot=api.catalogSnapshot(session,cancel);
  long parseMs=(System.nanoTime()-start)/1000000;
  ok(snapshot.catalog.items.size()==40000,"40,000 signed rows preserved");
  Files.write(root.resolve("catalog-envelope.json"),snapshot.encoded());
  Files.write(root.resolve("authority.der"),fake.authority.getPublic().getEncoded());
  Files.write(root.resolve("device-public.der"),fake.device.getPublic().getEncoded());
  ok(snapshot.encoded().length>12*1024*1024,"Fixture exceeds previous envelope limit");
  ok(snapshot.catalog.find("capacity_139999").name.equals(name.toString()),"Last item and Unicode name preserved");
  StationPublication publication=new StationPublication(snapshot.catalog);
  ok(publication.rows.size()==40000&&publication.unsupportedCount==0,"All rows map to exact supported platforms");
  int[] counts=new int[4];for(StationCatalog.Item item:snapshot.catalog.items)for(int i=0;i<4;i++)if(item.platform.equals(platforms[i]))counts[i]++;
  for(int count:counts)ok(count==10000,"Each platform has 10,000 entries");
  StationCatalogStore store=new StationCatalogStore(root.resolve("cache"));
  StationApi.CatalogSnapshot persisted=store.refresh(api,session,cancel);
  ok(store.read(api,session).catalog.find("capacity_139999")!=null,"Signed disk cache preserves last row");
  fake.catalogItems=null;
  fake.badSignature=true;reject(()->api.catalogSnapshot(session,cancel));fake.badSignature=false;
  fake.tamper="deviceId";reject(()->api.catalogSnapshot(session,cancel));fake.tamper="";
  rows.put(StationApiTest.item().put("itemId","capacity_140000"));reject(()->StationCatalog.fromVerifiedPayload(new JSONObject().put("revision",1).put("items",rows)));
  StringBuilder overflow=new StringBuilder("{\"revision\":1,\"items\":[");
  for(int i=0;i<40001;i++){if(i>0)overflow.append(',');overflow.append(StationApiTest.item().put("itemId","overflow_"+(100000+i)).toString());}
  overflow.append("]}");reject(()->StationCatalog.fromVerifiedText(overflow.toString()));
  String row=StationApiTest.item().toString();
  for(String bad:new String[]{"{}","{\"revision\":1,\"items\":["+row+","+row+"]}","{\"revision\":1,\"items\":[],\"items\":[]}","{\"revision\":1,\"items\":[null]}","{\"revision\":1,\"items\":[],}","{\"revision\":1,\"items\":[]} trailing","{\"revision\":1,\"items\":["+row+",]}","{\"revision\":1,\"items\":[],\"x\":{}}"})reject(()->StationCatalog.fromVerifiedText(bad));
  ok(StationCatalog.fromVerifiedText("{\"items\":[],\"revision\":1}").catalog.items.isEmpty(),"Order-independent empty catalog");
  ok(StationCatalog.fromVerifiedText("{\"revision\":1,\"items\":["+row+"]}").catalog.items.size()==1,"Stable-size contract unchanged");
  StationInstaller installer=new StationInstaller(root.resolve("roms"),root.resolve("records"),new StationInstallerTest.ZipReader());
  ok(installer.recordedIds().isEmpty(),"No per-item filesystem search for empty install set");
  Files.write(root.resolve("records/item_12345.json"),"invalid receipt".getBytes(StandardCharsets.UTF_8));
  Files.write(root.resolve("records/bad.json"),new byte[]{1});
  ok(installer.recordedIds().equals(Collections.singleton("item_12345")),"Only valid receipt names considered");
  reject(()->installer.find(StationCatalog.fromVerifiedText("{\"revision\":1,\"items\":["+row+"]}").catalog.items.get(0)));
  JSONObject report=new JSONObject().put("checks",checks).put("synthetic",true).put("items",40000).put("perPlatform",10000)
   .put("envelopeBytes",persisted.encoded().length).put("parseAndSignatureMillis",parseMs)
   .put("usedHeapAtEnd",Runtime.getRuntime().totalMemory()-Runtime.getRuntime().freeMemory()).put("heapLimit",Runtime.getRuntime().maxMemory())
   .put("note","Heap value is an end sample, not peak; duration is this isolated process, not full UI performance.");
  Files.write(root.resolve("capacity-results.json"),report.toString(2).getBytes(StandardCharsets.UTF_8));
  System.out.println("PASS "+checks+" capacity checks: 40000 signed rows, "+persisted.encoded().length+" envelope bytes, parse/signature "+parseMs+" ms");
 }
}
