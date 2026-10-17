package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;
import org.json.*;

final class CatalogCapacityTransportFixture {
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
        volatile long time=1000;int requests,closed,artifactCalls;String tamper="",failedRoute="",errorCode="";int status=200;
        boolean reachable=true; Integer total; Boolean more; String lastCatalogPath;
        @Override public boolean available(){return reachable;}
        boolean rotateSessions;volatile int sessionCalls;
        volatile String activeToken=token(3),activeSession=sessionId;
        String displayName="Comprador";
        java.util.concurrent.CountDownLatch artifactEntered,artifactRelease;
        java.util.concurrent.CountDownLatch artifactBodyEntered,artifactBodyRelease;
        org.json.JSONObject descriptorOverride;org.json.JSONArray catalogItems;boolean omitDescriptor;long itemRevision=1;
        boolean badSignature,truncatedArtifact;byte[] artifact={1,2,3};long lengthOverride=-2;
        Fake()throws Exception {
            KeyPairGenerator gen=KeyPairGenerator.getInstance("RSA");gen.initialize(2048);
            authority=gen.generateKeyPair();device=gen.generateKeyPair();deviceId=StationProtocol.deviceId(device.getPublic().getEncoded());
        }
        public PublicKey publicKey(){return device.getPublic();}
        public byte[] sign(byte[] payload)throws Exception{return CatalogCapacityTransportFixture.sign(device,payload);}
        public String manufacturer(){return "test";}public String model(){return "host";}public int sdk(){return 34;}
        public long millis(){return time;}
        StationApi api()throws Exception{return new StationApi(this,this,this,authority.getPublic(),"test-key");}
        @Override public StationApi.Response exchange(String method,String path,byte[] request,String bearer,StationApi.Cancellation cancel)throws IOException {
            requests++;
            if(path.equals("/v1/station/catalog?metadata=1&maximumItems=20000")){lastCatalogPath=path;path="/v1/station/catalog";}
            try {
                cancel.check();
                if (path.equals(failedRoute))return reply(status,"application/json",new JSONObject().put("code",errorCode).toString().getBytes(StandardCharsets.UTF_8),-2);
                if(path.contains("/artifacts/")) {
                    artifactCalls++;
                    if(artifactEntered!=null){artifactEntered.countDown();if(!artifactRelease.await(10,java.util.concurrent.TimeUnit.SECONDS))throw new IOException("Fixture transfer barrier timed out");}
                    if(rotateSessions&&!bearer.equals(activeToken))return reply(401,"application/json",new JSONObject().put("code","STATION_SESSION_DENIED").toString().getBytes(StandardCharsets.UTF_8),-2);
                    ok(bearer.equals(activeToken),"Artifact bearer");
                    if(artifactBodyEntered!=null){
                        InputStream input=new FilterInputStream(new ByteArrayInputStream(artifact)){
                            boolean started;
                            @Override public int read(byte[] buffer,int offset,int length)throws IOException{
                                if(!started){started=true;artifactBodyEntered.countDown();try{if(!artifactBodyRelease.await(10,java.util.concurrent.TimeUnit.SECONDS))throw new IOException("Fixture body barrier timed out");}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}}
                                return super.read(buffer,offset,length);
                            }
                        };
                        return new StationApi.Response(200,"application/octet-stream",artifact.length,input,()->{input.close();closed++;});
                    }
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
                    sessionCalls++;
                    if(rotateSessions){activeToken=token(2+sessionCalls);activeSession=String.format("%064x",1+sessionCalls);}
                    response.put("licenseId",license).put("challengeId",challengeId).put("nonce",token(2))
                        .put("sessionId",activeSession).put("accessToken",activeToken).put("expiresInSeconds",180);
                }else {
                    ok(bearer.equals(activeToken),"Authenticated request");
                    response.put("licenseId",license).put("sessionId",activeSession);
                    if(operation.equals("catalog")){domain=StationProtocol.CATALOG;response.put("revision",1).put("items",catalogItems==null?new JSONArray().put(item()):catalogItems);}
                    else if(operation.equals("me")){domain=StationProtocol.PROFILE;response.put("displayName",displayName).put("profileVersion",1);}
                    else if(operation.equals("online/command")||operation.equals("online/events")){
                        domain="TurboRamaStationAndroid/online/v1";JSONObject body=new JSONObject(new String(request,StandardCharsets.UTF_8));
                        response.put("requestId",body.getString("requestId")).put("snapshot",new JSONObject().put("schemaVersion",1).put("instance","a".repeat(32)).put("revision",1));
                    }
                    else if(operation.equals("downloads/authorize")){
                        domain=StationProtocol.DOWNLOAD_GRANT;
                        JSONObject body=new JSONObject(new String(request,StandardCharsets.UTF_8));ok(body.getString("itemId").equals("item_12345"),"Authorize by ID");
                        response.put("itemId","item_12345").put("grantId",token(4)).put("expiresInSeconds",60).put("itemRevision",itemRevision);
                        if(!omitDescriptor)response.put("artifact",descriptorOverride==null?descriptor(artifact):descriptorOverride);
                    }else throw new AssertionError("Unexpected path "+path);
                }
                if (operation.equals("catalog")) {if(total!=null)response.put("totalItems",total);if(more!=null)response.put("hasMore",more);}
                response.put("domain",domain);
                if(!tamper.isEmpty())response.put(tamper,tamper.equals("schemaVersion")?2:"wrong_value");
                byte[] data=response.toString().getBytes(StandardCharsets.UTF_8),signature=CatalogCapacityTransportFixture.sign(authority,data);
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
}
