package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;
import org.json.*;

public final class StationApiTest {
    static int checks;
    interface Op { void run() throws Exception; }
    static void ok(boolean yes,String name) {checks++;if(!yes)throw new AssertionError(name);}
    static void fails(Op action) throws Exception {
        try { action.run();throw new AssertionError("Expected failure"); }
        catch (IOException|GeneralSecurityException|JSONException|IllegalArgumentException expected) {checks++;}
    }
    static final PSSParameterSpec PSS=new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1);
    static byte[] sign(KeyPair pair,byte[] data)throws Exception {
        Signature s=Signature.getInstance("RSASSA-PSS");s.setParameter(PSS);s.initSign(pair.getPrivate());s.update(data);return s.sign();
    }
    static String token(int b) { byte[] bytes=new byte[32];Arrays.fill(bytes,(byte)b);return StationProtocol.base64Url(bytes); }
    static final class Fake implements StationApi.Transport, StationApi.Device, StationApi.Clock {
        final KeyPair authority,device;
        final String deviceId,license="license_test_123",sessionId="2".repeat(64),challengeId="1".repeat(64);
        long time=1000;int requests,closed,artifactCalls;String tamper="",failedRoute="",errorCode="";int status=200;
        org.json.JSONObject descriptorOverride;boolean omitDescriptor;long itemRevision=1;
        boolean badSignature,truncatedArtifact;byte[] artifact={1,2,3};long lengthOverride=-2;
        Fake()throws Exception {
            KeyPairGenerator gen=KeyPairGenerator.getInstance("RSA");gen.initialize(2048);
            authority=gen.generateKeyPair();device=gen.generateKeyPair();deviceId=StationProtocol.deviceId(device.getPublic().getEncoded());
        }
        public PublicKey publicKey(){return device.getPublic();}
        public byte[] sign(byte[] payload)throws Exception{return StationApiTest.sign(device,payload);}
        public String manufacturer(){return "test";}public String model(){return "host";}public int sdk(){return 34;}
        public long millis(){return time;}
        StationApi api()throws Exception{return new StationApi(this,this,this,authority.getPublic(),"test-key");}
        @Override public StationApi.Response exchange(String method,String path,byte[] request,String bearer,StationApi.Cancellation cancel)throws IOException {
            requests++;
            try {
                cancel.check();
                if (path.equals(failedRoute))return reply(status,"application/json",new JSONObject().put("code",errorCode).toString().getBytes(StandardCharsets.UTF_8),-2);
                if(path.contains("/artifacts/")) {
                    artifactCalls++;ok(bearer.equals(token(3)),"Artifact bearer");
                    return reply(200,"application/octet-stream",artifact,truncatedArtifact?10:artifact.length);
                }
                if(path.contains("/covers/"))return reply(200,"image/png",new byte[]{(byte)137,80,78,71,13,10,26,10},-2);
                JSONObject response=new JSONObject().put("schemaVersion",1).put("productId",StationConfig.PRODUCT)
                    .put("applicationId",StationConfig.APPLICATION).put("deviceId",deviceId);
                String operation=path.substring("/v1/station/".length());String domain;
                if(operation.equals("activations/challenge")){
                    domain=StationProtocol.ACTIVATION_CHALLENGE;
                    JSONObject body=new JSONObject(new String(request,StandardCharsets.UTF_8));ok(body.getString("activationCode").equals(token(9)),"Activation code");
                    response.put("challengeId",challengeId).put("nonce",token(2)).put("expiresInSeconds",60);
                }else if(operation.equals("activations/complete")){
                    verifyDevice(request);domain=StationProtocol.ACTIVATED;
                    response.put("licenseId",license).put("challengeId",challengeId).put("nonce",token(2));
                }else if(operation.equals("challenges")){
                    domain=StationProtocol.SESSION_CHALLENGE;response.put("licenseId",license).put("challengeId",challengeId).put("nonce",token(2)).put("expiresInSeconds",60);
                }else if(operation.equals("sessions")){
                    verifyDevice(request);domain=StationProtocol.SESSION;
                    response.put("licenseId",license).put("challengeId",challengeId).put("nonce",token(2))
                        .put("sessionId",sessionId).put("accessToken",token(3)).put("expiresInSeconds",180);
                }else {
                    ok(bearer.equals(token(3)),"Authenticated request");
                    response.put("licenseId",license).put("sessionId",sessionId);
                    if(operation.equals("catalog")){domain=StationProtocol.CATALOG;response.put("revision",1).put("items",new JSONArray().put(item()));}
                    else if(operation.equals("me")){domain=StationProtocol.PROFILE;response.put("displayName","Comprador").put("profileVersion",1);}
                    else if(operation.equals("downloads/authorize")){
                        domain=StationProtocol.DOWNLOAD_GRANT;
                        JSONObject body=new JSONObject(new String(request,StandardCharsets.UTF_8));ok(body.getString("itemId").equals("item_12345"),"Authorize by ID");
                        response.put("itemId","item_12345").put("grantId",token(4)).put("expiresInSeconds",60).put("itemRevision",itemRevision);
                        if(!omitDescriptor)response.put("artifact",descriptorOverride==null?descriptor(artifact):descriptorOverride);
                    }else throw new AssertionError("Unexpected path "+path);
                }
                response.put("domain",domain);
                if(!tamper.isEmpty())response.put(tamper,tamper.equals("schemaVersion")?2:"wrong_value");
                byte[] data=response.toString().getBytes(StandardCharsets.UTF_8),signature=StationApiTest.sign(authority,data);
                if(badSignature)signature[0]^=1;
                byte[] bytes=new JSONObject().put("keyId","test-key").put("payload",StationProtocol.base64Url(data))
                    .put("signature",StationProtocol.base64Url(signature)).toString().getBytes(StandardCharsets.UTF_8);
                return reply(200,"application/json; charset=utf-8",bytes,lengthOverride);
            }catch(IOException e){throw e;}catch(Exception e){throw new IOException(e);}
        }
        void verifyDevice(byte[] bytes)throws Exception {
            JSONObject env=new JSONObject(new String(bytes,StandardCharsets.UTF_8));byte[] payload=StationProtocol.decode(env.getString("payload"));
            Signature v=Signature.getInstance("RSASSA-PSS");v.setParameter(PSS);v.initVerify(device.getPublic());v.update(payload);
            ok(v.verify(StationProtocol.decode(env.getString("signature"))),"Device proof signature");
        }
        StationApi.Response reply(int status,String type,byte[] data,long length){
            return new StationApi.Response(status,type,length == -2?data.length:length,new ByteArrayInputStream(data),()->closed++);
        }
    }
    static JSONObject descriptor(byte[] bytes)throws Exception {
        StringBuilder hash=new StringBuilder();for(byte b:StationProtocol.sha256(bytes))hash.append(String.format("%02x",b&255));
        return new JSONObject().put("fileName","game.bin").put("sizeBytes",bytes.length).put("sha256",hash.toString())
            .put("format","raw").put("launchPath","game.bin").put("expandedSizeBytes",bytes.length).put("fileCount",1);
    }
    static JSONObject item()throws Exception {return new JSONObject().put("itemId","item_12345").put("name","Game")
        .put("platform","Master System ").put("revision",1).put("coverId","cover_12345");}
    static JSONObject catalog(JSONObject...rows)throws Exception {JSONArray items=new JSONArray();for(JSONObject row:rows)items.put(row);return new JSONObject().put("revision",1).put("items",items);}
    public static void main(String[] args)throws Exception {
        Fake fake=new Fake();StationApi api=fake.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
        ok(api.activate(token(9),cancel).equals(fake.license),"Activation");
        StationApi.Session session=api.openSession(fake.license,cancel);
        ok(!session.needsRenewal(fake.time),"Fresh session");
        ok(api.profile(session,cancel).equals("Comprador"),"Profile");
        StationCatalog list=api.catalog(session,cancel);
        ok(list.items.size()==1&&list.find("item_12345")!=null,"Catalog");
        ok(list.items.get(0).platform.equals("Master System "),"Preserve exact platform label");
        ok(api.cover(session,"cover_12345",cancel).length==8,"Cover transfer");
        ok(fake.closed==fake.requests,"Connections closed on success");
        for(String field:new String[]{"licenseId","deviceId","sessionId","productId","applicationId","domain","schemaVersion"}){
            fake.tamper=field;fails(()->api.catalog(session,cancel));fake.tamper="";
        }
        fake.badSignature=true;fails(()->api.catalog(session,cancel));fake.badSignature=false;
        fake.lengthOverride=10;fails(()->api.catalog(session,cancel));fake.lengthOverride=-2;
        fake.failedRoute="/v1/station/catalog";fake.status=403;fake.errorCode="STATION_LICENSE_DENIED";
        try{api.catalog(session,cancel);throw new AssertionError("403 ignored");}catch(StationApi.Failure e){ok(e.sessionDenied()&&e.code.equals("STATION_LICENSE_DENIED"),"Typed denial");}
        fake.failedRoute="";ok(fake.closed==fake.requests,"Connections closed on errors");
        StationApi.Cancellation stopped=new StationApi.Cancellation();stopped.cancel();int before=fake.requests;
        fails(()->api.catalog(session,stopped));ok(fake.requests==before,"No request after cancellation");
        fails(()->api.catalog(fake.api().openSession(fake.license,cancel),cancel));
        fake.tamper="nonce";fails(()->api.openSession(fake.license,cancel));fake.tamper="";
        fake.tamper="itemId";fails(()->api.authorize(session,"item_12345",1,cancel));fake.tamper="";
        Path target=Paths.get(args[0]).resolve("staged.artifact");Files.createDirectories(target.getParent());Files.write(target,new byte[]{9});
        StationApi.Grant grant=api.authorize(session,"item_12345",1,cancel);fake.truncatedArtifact=true;
        fails(()->api.downloadToStaging(grant,target,100,cancel,(n,t)->{}));
        ok(Arrays.equals(Files.readAllBytes(target),new byte[]{9}),"Preserve previous artifact");
        before=fake.artifactCalls;fails(()->api.downloadToStaging(grant,target,100,cancel,(n,t)->{}));ok(fake.artifactCalls==before,"Never reuse grant");
        fake.truncatedArtifact=false;StationApi.Grant secondGrant=api.authorize(session,"item_12345",1,cancel);
        ok(api.downloadToStaging(secondGrant,target,100,cancel,(n,t)->{}).size==3,"Artifact complete");
        final StationApi.Grant expired=api.authorize(session,"item_12345",1,cancel);fake.time+=60000;
        fails(()->api.downloadToStaging(expired,target,100,cancel,(n,t)->{}));
        fake.time+=120000;before=fake.requests;fails(()->api.catalog(session,cancel));ok(before==fake.requests,"Expired session not sent");
        fails(()->StationCatalog.fromVerifiedPayload(catalog(item(),item())));
        fails(()->StationCatalog.fromVerifiedPayload(catalog(item().put("revision",1.5))));
        fails(()->StationCatalog.fromVerifiedPayload(catalog(item().put("itemId","../../escape"))));
        fails(()->StationCatalog.fromVerifiedPayload(catalog(item().put("name",123))));
        fails(()->StationCatalog.fromVerifiedPayload(catalog(item().put("name","bad\nname"))));
        ok(StationCatalog.fromVerifiedPayload(catalog()).items.isEmpty(),"Empty catalog valid");
        try{list.items.clear();throw new AssertionError("Mutable catalog");}catch(UnsupportedOperationException good){checks++;}
        ok(!new String(list.localPayload(),StandardCharsets.UTF_8).contains("https:"),"No fabricated URLs");
        ok(!StationHttp.allowed("GET","https://another.example/file"),"No remote address path");
        ok(!StationHttp.allowed("GET","/v1/station/covers/../../file"),"No traversal route");
        ok(StationHttp.allowed("GET","/v1/station/covers/cover_12345"),"Cover ID route");
        ok(fake.closed==fake.requests,"All responses closed");
        System.out.println("PASS "+checks+" protocol and catalog checks");
    }
}
