package org.emulationstation.frontend.station;

import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.spec.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.json.*;

/** Actual candidate backend integration, with temporary software keys and fixture media only. */
public final class StationSecurityHttpTest {
    static final class Http implements StationApi.Transport {
        final String origin;final AtomicInteger protectedRequests=new AtomicInteger();
        final Set<String> nonces=ConcurrentHashMap.newKeySet();
        Http(String origin)throws Exception {
            URI uri=new URI(origin);
            if(!uri.getScheme().equals("http")||!uri.getHost().equals("127.0.0.1")||uri.getPort()==5192)
                throw new IOException("Temporary loopback fixture required");this.origin=origin;
        }
        public boolean supportsRequestProof(){return true;}
        public StationApi.Response exchange(String method,String path,byte[] body,String token,StationApi.Cancellation cancel)throws IOException {
            return exchange(method,path,body,token,null,cancel);
        }
        public StationApi.Response exchange(String method,String path,byte[] body,String token,String proof,StationApi.Cancellation cancel)throws IOException {
            cancel.check();HttpURLConnection connection=(HttpURLConnection)new URL(origin+path).openConnection();
            connection.setInstanceFollowRedirects(false);connection.setRequestMethod(method);connection.setConnectTimeout(10000);connection.setReadTimeout(10000);
            if(token!=null){if(proof==null)throw new AssertionError("New client omitted request proof");
                connection.setRequestProperty("Authorization","Bearer "+token);connection.setRequestProperty("X-Station-Request-Proof",proof);
                if(!nonces.add(proof.split("\\.")[2]))throw new AssertionError("Request nonce reused");protectedRequests.incrementAndGet();}
            if(body!=null){connection.setDoOutput(true);connection.setRequestProperty("Content-Type","application/json");
                connection.setFixedLengthStreamingMode(body.length);try(OutputStream out=connection.getOutputStream()){out.write(body);}}
            int status=connection.getResponseCode();InputStream stream=status>=400?connection.getErrorStream():connection.getInputStream();
            if(stream==null)stream=new ByteArrayInputStream(new byte[0]);final InputStream owned=stream;
            return new StationApi.Response(status,connection.getContentType(),connection.getContentLengthLong(),owned,()->{owned.close();connection.disconnect();});
        }
    }
    static byte[] decode(String text){return Base64.getUrlDecoder().decode(text);}
    static String hash(byte[] bytes)throws Exception {StringBuilder out=new StringBuilder();
        for(byte b:MessageDigest.getInstance("SHA-256").digest(bytes))out.append(String.format(Locale.ROOT,"%02x",b&255));return out.toString();}
    public static void main(String[] args)throws Exception {
        JSONObject config=new JSONObject(new String(Files.readAllBytes(Paths.get(args[0])),StandardCharsets.UTF_8));
        KeyFactory factory=KeyFactory.getInstance("RSA");PublicKey primary=factory.generatePublic(new X509EncodedKeySpec(decode(config.getString("deviceSpki"))));
        PrivateKey privateKey=factory.generatePrivate(new PKCS8EncodedKeySpec(decode(config.getString("devicePrivate"))));
        PublicKey authority=factory.generatePublic(new X509EncodedKeySpec(decode(config.getString("authoritySpki"))));
        StationApi.Device device=new StationApi.Device(){
            public PublicKey publicKey(){return primary;}
            public byte[] sign(byte[] bytes)throws Exception {Signature signature=Signature.getInstance("RSASSA-PSS");
                signature.setParameter(new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1));
                signature.initSign(privateKey);signature.update(bytes);return signature.sign();}
            public String manufacturer(){return "Synthetic";}public String model(){return "JVM";}public int sdk(){return 35;}
        };
        Http transport=new Http(config.getString("origin"));StationApi api=new StationApi(transport,device,
            ()->System.nanoTime()/1000000L,authority,hash(authority.getEncoded()));
        StationApi.Cancellation cancel=new StationApi.Cancellation();
        String license=api.activate(config.getString("code"),cancel);
        if(!license.equals(config.getString("license")))throw new AssertionError("Activation license changed");
        StationApi.Session session=api.openSession(license,cancel);
        if(!api.profile(session,cancel).equals("Security fixture"))throw new AssertionError("Buyer profile changed");
        api.catalog(session,cancel);
        ExecutorService executor=Executors.newFixedThreadPool(4);
        try{
            List<Callable<Integer>> jobs=new ArrayList<>();
            for(int i=0;i<16;i++)jobs.add(()->api.cover(session,"cover-synthetic-01",new StationApi.Cancellation()).length);
            for(Future<Integer> result:executor.invokeAll(jobs))if(result.get()!=config.getInt("coverBytes"))throw new AssertionError("Cover bytes changed");
        }finally{executor.shutdownNow();}
        StationApi.Grant grant=api.authorize(session,"item-synthetic-01",3,cancel);
        Path target=Paths.get(args[0]).getParent().resolve("jvm-game.bin");
        api.downloadToStaging(grant,target,8*1024*1024,cancel,StationFiles.NO_PROGRESS);
        if(Files.size(target)!=4*1024*1024)throw new AssertionError("Download bytes changed");Files.delete(target);
        String relayProof=api.relayRequestProof(session,StationProtocol.base64Url(new byte[32]));
        if(relayProof==null||!relayProof.startsWith("v1."))throw new AssertionError("Relay proof absent");
        StationApi.Session renewed=api.openSession(license,cancel);api.profile(renewed,cancel);
        System.out.println("PASS actual Java/candidate HTTP activation, protected session/renewal, profile/catalog, four covers concurrently, exact download and relay signing; protected requests="+transport.protectedRequests.get());
    }
}
