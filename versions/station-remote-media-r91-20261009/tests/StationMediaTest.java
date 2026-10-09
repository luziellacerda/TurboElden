package org.emulationstation.frontend.station;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.json.*;
public final class StationMediaTest {
 static int checks;
 static void ok(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
 interface Op{void run()throws Exception;}
 static void fails(Op op)throws Exception{try{op.run();throw new AssertionError("Expected refusal");}catch(IOException|java.security.GeneralSecurityException|JSONException expected){checks++;}}
 static String hash(byte[] bytes)throws Exception{StringBuilder b=new StringBuilder();for(byte v:StationProtocol.sha256(bytes))b.append(String.format("%02x",v&255));return b.toString();}
 static JSONObject row(byte[] bytes)throws Exception{return new JSONObject().put("asset","turbo-system-videos/720-snes.mp4").put("sha256",hash(bytes)).put("sizeBytes",bytes.length).put("contentType","video/mp4").put("width",720).put("height",720).put("fps",30).put("audioTracks",0);}
 static JSONObject manifest(JSONObject...rows)throws Exception{JSONArray a=new JSONArray();for(JSONObject r:rows)a.put(r);return new JSONObject().put("revision",1).put("items",a);}
 static class Wire implements StationApi.Transport {
  final StationApiTest.Fake fake;final byte[] bytes;String tamper="";boolean badSignature;int mediaRequests;
  Wire(StationApiTest.Fake f,byte[] b){fake=f;bytes=b;}
  public StationApi.Response exchange(String m,String p,byte[] b,String token,StationApi.Cancellation c)throws IOException{
   if(!p.contains("/media/"))return fake.exchange(m,p,b,token,c);
   try{c.check();ok(token.equals(fake.activeToken),"authenticated media request");mediaRequests++;
    if(p.contains("/files/"))return fake.reply(200,"video/mp4",bytes,bytes.length);
    JSONObject body=manifest(row(bytes)).put("schemaVersion",1).put("domain",StationMediaCatalog.DOMAIN).put("productId",StationConfig.PRODUCT).put("applicationId",StationConfig.APPLICATION)
      .put("licenseId",fake.license).put("deviceId",fake.deviceId).put("sessionId",fake.activeSession).put("requestId",p.substring(p.indexOf('=')+1));
    if(!tamper.isEmpty())body.put(tamper,"wrong");byte[] payload=body.toString().getBytes(StandardCharsets.UTF_8);byte[] sig=StationApiTest.sign(fake.authority,payload);if(badSignature)sig[0]^=1;
    return fake.reply(200,"application/json",new JSONObject().put("keyId","test-key").put("payload",StationProtocol.base64Url(payload)).put("signature",StationProtocol.base64Url(sig)).toString().getBytes(StandardCharsets.UTF_8),-2);
   }catch(IOException e){throw e;}catch(Exception e){throw new IOException(e);}
  }
 }
 public static void main(String[] args)throws Exception {
  byte[] old=new byte[64],fresh=new byte[64];Arrays.fill(old,(byte)1);Arrays.fill(fresh,(byte)2);
  StationMediaCatalog.Entry e=StationMediaCatalog.entry(row(old)),n=StationMediaCatalog.entry(row(fresh));
  ok(new StationMediaCatalog(manifest(row(old))).items.size()==1,"manifest parses");
  for(String key:new String[]{"width","height","fps","audioTracks"})fails(()->new StationMediaCatalog(manifest(row(old).put(key,999))));
  for(String invalid:new String[]{"../../x.mp4","https://x/file.mp4","turbo-system-videos/720-../x.mp4","turbo-system-videos/720-X.mp4"})fails(()->new StationMediaCatalog(manifest(row(old).put("asset",invalid))));
  fails(()->new StationMediaCatalog(manifest(row(old),row(old))));fails(()->new StationMediaCatalog(manifest(row(old).put("sizeBytes",StationMediaCatalog.MAX_FILE+1))));
  Path dir=Paths.get(args[0]);StationMediaStore cache=new StationMediaStore(dir);StationApi.Cancellation c=new StationApi.Cancellation();
  cache.publish(e,new ByteArrayInputStream(old),c,p->{});ok(Arrays.equals(Files.readAllBytes(cache.cached(e.asset)),old),"initial complete file");
  fails(()->cache.publish(n,new ByteArrayInputStream(new byte[4]),c,p->{}));ok(Arrays.equals(Files.readAllBytes(cache.cached(e.asset)),old),"truncation retains old file");
  fails(()->cache.publish(n,new ByteArrayInputStream(old),c,p->{}));ok(cache.contains(e),"hash mismatch retains old file");
  fails(()->cache.publish(n,new ByteArrayInputStream(fresh),c,p->{throw new IOException("bad format");}));ok(cache.contains(e),"codec rejection retains old pointer");
  StationApi.Cancellation cancelled=new StationApi.Cancellation();cancelled.cancel();fails(()->cache.publish(n,new ByteArrayInputStream(fresh),cancelled,p->{}));ok(cache.contains(e),"cancellation retains old pointer");
  cache.publish(n,new ByteArrayInputStream(fresh),c,p->{});ok(cache.contains(n),"complete update published");
  StationMediaStore restored=new StationMediaStore(dir);ok(restored.contains(n),"offline restart retains cache");
  ok(Files.list(dir).filter(p->p.toString().endsWith(".mp4")).count()==1,"obsolete immutable file removed");
  StationApiTest.Fake fake=new StationApiTest.Fake();Wire wire=new Wire(fake,fresh);StationApi api=new StationApi(wire,fake,fake,fake.authority.getPublic(),"test-key");StationApi.Session session=api.openSession(fake.license,c);
  ok(api.mediaCatalog(session,c).items.size()==1,"signed media API");
  for(String field:new String[]{"requestId","sessionId","licenseId","deviceId","domain","applicationId","productId"}){wire.tamper=field;fails(()->api.mediaCatalog(session,c));}wire.tamper="";
  wire.badSignature=true;fails(()->api.mediaCatalog(session,c));wire.badSignature=false;
  try(StationApi.Response response=api.openMedia(session,n,c)){ok(response.body.read()==2,"authenticated immutable file");}
  int before=wire.mediaRequests;fails(()->api.mediaCatalog(session,cancelled));ok(wire.mediaRequests==before,"no network after cancellation");
  System.out.println("PASS "+checks+" media checks");
 }
}
