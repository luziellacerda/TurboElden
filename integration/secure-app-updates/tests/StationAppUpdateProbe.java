package org.emulationstation.frontend.station;

import java.io.*;
import java.lang.reflect.Constructor;
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;
import org.json.JSONObject;

/** Actual API signature validation and private staging, no Android UI or installer. */
public final class StationAppUpdateProbe {
    static int checks;
    static void check(boolean value,String name){checks++;if(!value)throw new AssertionError(name);}
    interface Action{void run()throws Exception;}
    static void reject(Action action,String name)throws Exception{try{action.run();throw new AssertionError("accepted "+name);}catch(IOException|GeneralSecurityException expected){checks++;}}
    static JSONObject descriptor(byte[] bytes)throws Exception{
        String hash=StationAppUpdateFiles.hex(MessageDigest.getInstance("SHA-256").digest(bytes));
        return new JSONObject().put("schemaVersion",1).put("packageName",StationAppRelease.PACKAGE)
            .put("versionCode",200L).put("versionName","Teste 200").put("releaseId",hash).put("sha256",hash)
            .put("sizeBytes",bytes.length).put("certificateSha256",repeat('c',64)).put("minimumSdk",28)
            .put("abi","arm64-v8a").put("notes","Apenas bytes sintéticos.");
    }
    static String repeat(char c,int count){char[] chars=new char[count];Arrays.fill(chars,c);return new String(chars);}
    public static void main(String[] args)throws Exception{
        byte[] bytes=new byte[600123];new Random(17).nextBytes(bytes);
        StationAppRelease release=StationAppRelease.parse(descriptor(bytes));
        check(release.eligible(100,35,repeat('c',64),true),"new compatible update");
        check(!release.eligible(200,35,repeat('c',64),true),"equal version rejected");
        check(!release.eligible(201,35,repeat('c',64),true),"downgrade rejected");
        check(!release.eligible(100,27,repeat('c',64),true),"SDK incompatible");
        check(!release.eligible(100,35,repeat('b',64),true),"certificate mismatch");
        check(!release.eligible(100,35,repeat('c',64),false),"ABI incompatible");
        for(String field:new String[]{"releaseId","sha256","certificateSha256","packageName","abi"}){
            JSONObject bad=descriptor(bytes).put(field,"../bad");reject(()->StationAppRelease.parse(bad),"bad "+field);
        }
        reject(()->StationAppRelease.parse(descriptor(bytes).put("versionCode",199.5)),"fractional version");
        reject(()->StationAppRelease.parse(descriptor(bytes).put("sizeBytes",StationAppRelease.MAXIMUM_BYTES+1)),"excess APK size");
        reject(()->StationAppRelease.parse(descriptor(bytes).put("minimumSdk",27)),"unsupported Android baseline");
        Path root=Files.createTempDirectory("station-app-update-jvm-");
        try{
            StationApi.Cancellation cancel=new StationApi.Cancellation();
            Path complete=StationAppUpdateFiles.receive(new ByteArrayInputStream(bytes),root,release,cancel,(done,total)->check(done<=total,"bounded progress"));
            check(Arrays.equals(Files.readAllBytes(complete),bytes),"complete bytes atomically published");
            check(Files.list(root).noneMatch(p->p.toString().endsWith(".part")),"no staging leak");
            check(StationAppUpdateFiles.cached(root,release,new StationApi.Cancellation())!=null,"verified cache recovery");
            byte[] corrupt=bytes.clone();corrupt[19]^=1;
            reject(()->StationAppUpdateFiles.receive(new ByteArrayInputStream(corrupt),root,release,new StationApi.Cancellation(),(a,b)->{}),"corruption denied");
            reject(()->StationAppUpdateFiles.receive(new ByteArrayInputStream(Arrays.copyOf(bytes,10)),root,release,new StationApi.Cancellation(),(a,b)->{}),"truncated transfer denied");
            reject(()->StationAppUpdateFiles.receive(new ByteArrayInputStream(Arrays.copyOf(bytes,bytes.length+1)),root,release,new StationApi.Cancellation(),(a,b)->{}),"oversized transfer denied");
            cancel.cancel();reject(()->StationAppUpdateFiles.receive(new ByteArrayInputStream(bytes),root,release,cancel,(a,b)->{}),"cancel cleans staging");
            Files.write(complete,corrupt);
            check(StationAppUpdateFiles.cached(root,release,new StationApi.Cancellation())==null,"bad retained APK discarded");
            Path outside=Files.createTempFile("station-update-outside-",".txt");Files.write(outside,new byte[]{17});
            try{
                Path link=root.resolve(release.sha256+".part");Files.createSymbolicLink(link,outside);
                reject(()->StationAppUpdateFiles.receive(new ByteArrayInputStream(bytes),root,release,new StationApi.Cancellation(),(a,b)->{}),"staging symlink denied");
                check(Files.readAllBytes(outside)[0]==17,"outside link target unchanged");Files.delete(link);
            }finally{Files.delete(outside);}
            Files.write(root.resolve("keep.txt"),new byte[]{1});Files.write(root.resolve(repeat('f',64)+".apk"),new byte[]{1});
            StationAppUpdateFiles.prune(root,"");check(Files.exists(root.resolve("keep.txt")),"prune confined to own APK names");
            check(!Files.exists(root.resolve(repeat('f',64)+".apk")),"old own APK pruned");
        }finally{try(java.util.stream.Stream<Path> files=Files.walk(root)){files.sorted(Comparator.reverseOrder()).forEach(p->{try{Files.deleteIfExists(p);}catch(IOException e){throw new UncheckedIOException(e);}});}}
        KeyPairGenerator generator=KeyPairGenerator.getInstance("RSA");generator.initialize(2048);
        KeyPair device=generator.generateKeyPair(),authority=generator.generateKeyPair();
        Fake server=new Fake(authority,bytes);
        StationApi.Device identity=new StationApi.Device(){
            public PublicKey publicKey(){return device.getPublic();}public byte[] sign(byte[] value)throws Exception{return new byte[256];}
            public String manufacturer(){return "lab";}public String model(){return "fixture";}public int sdk(){return 35;}
        };
        String keyId=StationAppUpdateFiles.hex(MessageDigest.getInstance("SHA-256").digest(authority.getPublic().getEncoded()));
        StationApi api=new StationApi(server,identity,()->1000,authority.getPublic(),keyId);server.api=api;server.keyId=keyId;
        Constructor<StationApi.Session> constructor=StationApi.Session.class.getDeclaredConstructor(StationApi.class,String.class,String.class,String.class,String.class,long.class);constructor.setAccessible(true);
        StationApi.Session session=constructor.newInstance(api,"12345678-1234-1234-1234-123456789abc",api.deviceId(),repeat('a',64),StationProtocol.base64Url(new byte[32]),180000L);server.session=session;
        JSONObject request=new JSONObject().put("requestId",repeat('b',32));
        check(api.appUpdates(session,false,request,new StationApi.Cancellation()).getBoolean("available"),"actual signed API check");
        server.wrongId=true;reject(()->api.appUpdates(session,false,request,new StationApi.Cancellation()),"replayed/different request denied");server.wrongId=false;
        server.wrongSession=true;reject(()->api.appUpdates(session,false,request,new StationApi.Cancellation()),"foreign session reply denied");server.wrongSession=false;
        server.badSignature=true;reject(()->api.appUpdates(session,false,request,new StationApi.Cancellation()),"bad authority signature denied");server.badSignature=false;
        JSONObject grant=api.appUpdates(session,true,request,new StationApi.Cancellation());
        try(StationApi.Response response=api.openAppUpdate(session,grant.getString("grantId"),bytes.length,new StationApi.Cancellation())){
            check(response.length==bytes.length,"APK headers accepted");
        }
        server.badMime=true;reject(()->api.openAppUpdate(session,grant.getString("grantId"),bytes.length,new StationApi.Cancellation()),"wrong APK MIME denied");server.badMime=false;
        reject(()->api.openAppUpdate(session,grant.getString("grantId"),bytes.length+1,new StationApi.Cancellation()),"wrong APK length denied");
        check(StationHttp.allowed("POST","/v1/station/updates/check"),"check allowlist");
        check(StationHttp.allowed("POST","/v1/station/updates/authorize"),"grant allowlist");
        check(StationHttp.allowed("GET","/v1/station/updates/artifacts/"+grant.getString("grantId")),"canonical GET allowlist");
        check(!StationHttp.allowed("GET","/v1/station/updates/artifacts/"+grant.getString("grantId")+"?extra=1"),"query forbidden");
        check(!StationHttp.allowed("GET","/v1/station/updates/artifacts/../../private"),"traversal forbidden");
        check(StationDownloadOrigin.applies("GET","/v1/station/artifacts/"+grant.getString("grantId")),"old direct game origin preserved");
        check(!StationDownloadOrigin.applies("GET","/v1/station/updates/artifacts/"+grant.getString("grantId")),"new route stays on pinned API origin until dedicated proxy is qualified");
        System.out.println("PASS StationAppUpdate checks="+checks+" actualApiSignatureAndFiles=true androidInstallerOrUi=false");
    }
    static final class Fake implements StationApi.Transport {
        final KeyPair authority;final byte[] bytes;StationApi api;StationApi.Session session;String keyId;
        boolean wrongId,wrongSession,badSignature,badMime;
        Fake(KeyPair authority,byte[] bytes){this.authority=authority;this.bytes=bytes;}
        public StationApi.Response exchange(String method,String path,byte[] body,String bearer,StationApi.Cancellation cancel)throws IOException{
            try{
                if(method.equals("GET"))return response(badMime?"text/html":"application/vnd.android.package-archive",bytes);
                JSONObject request=new JSONObject(new String(body,java.nio.charset.StandardCharsets.UTF_8));
                boolean grant=path.endsWith("/authorize");
                JSONObject payload=new JSONObject().put("schemaVersion",1).put("domain","TurboRamaStationAndroid/"+(grant?"app-update-grant":"app-update")+"/v1")
                    .put("productId",StationConfig.PRODUCT).put("applicationId",StationConfig.APPLICATION).put("deviceId",api.deviceId())
                    .put("licenseId",session.licenseId).put("sessionId",wrongSession?repeat('d',64):session.sessionId)
                    .put("requestId",wrongId?repeat('e',32):request.getString("requestId")).put("expiresInSeconds",60)
                    .put("release",descriptor(bytes)).put("available",true);
                if(grant)payload.put("grantId",StationProtocol.base64Url(new byte[32]));
                byte[] encoded=payload.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
                Signature signature=Signature.getInstance("RSASSA-PSS");signature.setParameter(new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1));signature.initSign(authority.getPrivate());signature.update(encoded);
                byte[] signed=signature.sign();if(badSignature)signed[0]^=1;
                byte[] envelope=new JSONObject().put("keyId",keyId).put("payload",StationProtocol.base64Url(encoded)).put("signature",StationProtocol.base64Url(signed)).toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
                return response("application/json",envelope);
            }catch(Exception e){throw new IOException("synthetic transport",e);}
        }
        StationApi.Response response(String mime,byte[] data){ByteArrayInputStream input=new ByteArrayInputStream(data);return new StationApi.Response(200,mime,data.length,input,input);}
    }
}
