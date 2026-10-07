package org.emulationstation.frontend.netplay;
import org.emulationstation.frontend.station.StationRecoveryProofTest;
import org.json.*;
import javax.net.ssl.*;
import java.io.*;
import java.net.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.cert.*;
import java.security.spec.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Actual Java bridge, two TCP endpoints, TLS/WSS, .NET production routes and proof verifier.
 * Native pause is a synthetic acknowledged hook here, not Android/core gameplay. */
public final class StationRecoveryTransportTest {
    static int checks;static long verifiedBytes;static Properties fixture;static SSLSocketFactory tls;static final ExecutorService io=Executors.newCachedThreadPool();
    static void check(boolean ok,String name){checks++;if(!ok)throw new AssertionError(name);}
    static void until(java.util.concurrent.Callable<Boolean> condition,String label)throws Exception{long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(25);while(!condition.call()){if(System.nanoTime()>end)throw new AssertionError(label);Thread.sleep(50);}check(true,label);}
    static byte[] read(InputStream in)throws Exception{ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))>=0)out.write(b,0,n);return out.toByteArray();}
    static HttpsURLConnection connection(String path)throws Exception{HttpsURLConnection c=(HttpsURLConnection)new URL(fixture.getProperty("url")+path).openConnection();c.setSSLSocketFactory(tls);c.setConnectTimeout(5000);c.setReadTimeout(15000);return c;}
    static JSONObject command(String role,PrivateKey key,String action)throws Exception{
        JSONObject body=new JSONObject().put("action",action).put("requestId",UUID.randomUUID().toString());
        if(action.endsWith("relay")||action.equals("relay-ticket")){
            body.put("roomId",fixture.getProperty("room")).put("generation",Long.parseLong(fixture.getProperty("generation"))).put("recoveryProtocol","station-stream.v2").put("engineId",fixture.getProperty("engine"));
            for(String field:new String[]{"contentSha256","optionsSha256","coreSha256","runtimeSha256"})body.put(field,fixture.getProperty("hash"));
        }else if(action.equals("host-listening"))body.put("roomId",fixture.getProperty("room"));
        String token=fixture.getProperty(role+".token"),path="/v1/station/online/command";byte[] bytes=body.toString().getBytes(StandardCharsets.UTF_8);
        HttpsURLConnection c=connection(path);c.setRequestMethod("POST");c.setDoOutput(true);c.setFixedLengthStreamingMode(bytes.length);c.setRequestProperty("Content-Type","application/json");c.setRequestProperty("Authorization","Bearer "+token);c.setRequestProperty("X-Station-Request-Proof",StationRecoveryProofTest.proof(key,token,"POST",path,bytes));
        try{c.getOutputStream().write(bytes);if(c.getResponseCode()!=200)throw new IOException("HTTP "+c.getResponseCode());JSONObject signed=new JSONObject(new String(read(c.getInputStream()),StandardCharsets.UTF_8));
            byte[] payload=Base64.getUrlDecoder().decode(signed.getString("payload"));
            PublicKey responseKey=KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(Base64.getUrlDecoder().decode(fixture.getProperty("responseSPKI"))));
            Signature verifier=Signature.getInstance("RSASSA-PSS");verifier.initVerify(responseKey);verifier.setParameter(new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1));verifier.update(payload);
            if(!verifier.verify(Base64.getUrlDecoder().decode(signed.getString("signature"))))throw new IOException("Response signature");
            JSONObject decoded=new JSONObject(new String(payload,StandardCharsets.UTF_8));if(!body.getString("requestId").equals(decoded.getString("requestId"))||!fixture.getProperty(role+".license").equals(decoded.getString("licenseId")))throw new IOException("Response context");
            return decoded.getJSONObject("snapshot");
        }finally{c.disconnect();}
    }
    static JSONObject state()throws Exception{HttpsURLConnection c=connection("/lab/state");c.setRequestProperty("X-Station-Lab",fixture.getProperty("lab"));try{return new JSONObject(new String(read(c.getInputStream()),StandardCharsets.UTF_8));}finally{c.disconnect();}}
    static void drop(String role)throws Exception{HttpsURLConnection c=connection("/lab/drop");c.setRequestMethod("POST");c.setDoOutput(true);c.setRequestProperty("X-Station-Lab",fixture.getProperty("lab"));byte[] bytes=role.getBytes(StandardCharsets.US_ASCII);c.setFixedLengthStreamingMode(bytes.length);try{c.getOutputStream().write(bytes);check(c.getResponseCode()==200,"isolated transport cut");}finally{c.disconnect();}}
    static final class Peer implements StationRecoveryTunnel.Listener {
        final String role;final PrivateKey key;final AtomicInteger pauses=new AtomicInteger(),credentials=new AtomicInteger();
        volatile long epoch;volatile boolean paused=true,connected,failed,stalled;StationRecoveryTunnel tunnel;
        Peer(String role)throws Exception{this.role=role;key=KeyFactory.getInstance("RSA").generatePrivate(new PKCS8EncodedKeySpec(Base64.getDecoder().decode(fixture.getProperty(role+".key"))));}
        JSONObject ticket(String action)throws Exception{credentials.incrementAndGet();return command(role,key,action).getJSONObject("room").getJSONObject("relay");}
        String proof(JSONObject descriptor)throws Exception{return StationRecoveryProofTest.proof(key,descriptor.getString("ticket"),"GET","/v1/station/online/relay",new byte[0]);}
        @Override public void ticket(){io.execute(()->{try{JSONObject t=ticket("resume-relay");tunnel.provide(t.getString("ticket"),proof(t),t.getInt("windowBytes"));}catch(Exception error){tunnel.unavailable();}});}
        @Override public void ready(){connected=true;if(role.equals("host"))io.execute(()->{try{command(role,key,"host-listening");}catch(Exception error){failed=true;}});}
        @Override public void state(boolean waiting,boolean synchronizing){}
        @Override public synchronized void nativeControl(long epoch,boolean pause,boolean visible){this.epoch=epoch;paused=pause;if(pause){pauses.incrementAndGet();stalled=false;}}
        @Override public synchronized long nativeStatus(){return(epoch<<3)|(paused?1:0)|(connected?2:0);}
        @Override public boolean nativeStalled(){return stalled;}
        @Override public void unrecoverable(String category){failed=true;System.err.println("Synthetic peer failed: "+role+" category="+category);}
    }
    static void transfer(Socket from,Socket to,int seed)throws Exception{
        byte[] bytes=new byte[180000];new Random(seed).nextBytes(bytes);
        Future<byte[]> received=io.submit(()->{byte[] result=new byte[bytes.length];DataInputStream input=new DataInputStream(to.getInputStream());input.readFully(result);return result;});
        from.getOutputStream().write(bytes);check(Arrays.equals(bytes,received.get(25,TimeUnit.SECONDS)),"ordered TCP bytes match exactly");verifiedBytes+=bytes.length;
    }
    public static void main(String[] args)throws Exception{
        fixture=new Properties();try(InputStream input=new FileInputStream(args[0])){fixture.load(input);}
        java.security.cert.Certificate cert=CertificateFactory.getInstance("X.509").generateCertificate(new ByteArrayInputStream(Base64.getDecoder().decode(fixture.getProperty("cert"))));
        KeyStore trust=KeyStore.getInstance(KeyStore.getDefaultType());trust.load(null,null);trust.setCertificateEntry("synthetic",cert);TrustManagerFactory tm=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());tm.init(trust);
        SSLContext context=SSLContext.getInstance("TLS");context.init(null,tm.getTrustManagers(),new SecureRandom());tls=context.getSocketFactory();
        for(int type=1;type<=13;type++){StationRecoveryWire f=new StationRecoveryWire(type,99,0,type==3?new byte[]{1,2,3}:new byte[0]);StationRecoveryWire decoded=StationRecoveryWire.decode(ByteBuffer.wrap(f.encode()));check(decoded.type==type&&decoded.offset==99&&Arrays.equals(decoded.data,f.data),"network-order frame");}
        Peer host=new Peer("host"),guest=new Peer("client");ServerSocket listener=new ServerSocket(0,1,InetAddress.getByName("127.0.0.1"));
        URI endpoint=new URI(fixture.getProperty("url").replace("https:","wss:")+"/v1/station/online/relay");
        JSONObject ht=host.ticket("relay-ticket"),gt=guest.ticket("relay-ticket");
        // Possession of the ticket without the device proof must not consume it.
        try(SSLSocket noProof=(SSLSocket)tls.createSocket("127.0.0.1",endpoint.getPort())){
            SSLParameters parameters=noProof.getSSLParameters();parameters.setEndpointIdentificationAlgorithm("HTTPS");noProof.setSSLParameters(parameters);noProof.setSoTimeout(5000);noProof.startHandshake();
            String request="GET /v1/station/online/relay HTTP/1.1\r\nHost: 127.0.0.1:"+endpoint.getPort()+"\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: "+Base64.getEncoder().encodeToString(new byte[16])+"\r\nSec-WebSocket-Protocol: station-stream.v2\r\nAuthorization: StationRelay "+ht.getString("ticket")+"\r\n\r\n";
            noProof.getOutputStream().write(request.getBytes(StandardCharsets.US_ASCII));String statusLine=new BufferedReader(new InputStreamReader(noProof.getInputStream(),StandardCharsets.US_ASCII)).readLine();check(statusLine!=null&&statusLine.startsWith("HTTP/1.1 401 "),"copied ticket without proof denied");
        }
        host.tunnel=new StationRecoveryTunnel(endpoint,ht.getString("ticket"),host.proof(ht),ht.getInt("windowBytes"),true,listener.getLocalPort(),tls,host);
        guest.tunnel=new StationRecoveryTunnel(endpoint,gt.getString("ticket"),guest.proof(gt),gt.getInt("windowBytes"),false,listener.getLocalPort(),tls,guest);
        Future<Socket> accepted=io.submit(listener::accept);host.tunnel.start();guest.tunnel.start();
        Socket guestNative=new Socket("127.0.0.1",guest.tunnel.localPort()),hostNative=accepted.get(10,TimeUnit.SECONDS);hostNative.setSoTimeout(30000);guestNative.setSoTimeout(30000);
        try{
            until(()->!host.paused&&!guest.paused,"both acknowledged transport barrier");
            transfer(hostNative,guestNative,1);transfer(guestNative,hostNative,2);
            for(String role:new String[]{"host","client","both"}){
                int before=host.credentials.get()+guest.credentials.get(),pauses=host.pauses.get()+guest.pauses.get();drop(role);
                until(()->host.credentials.get()+guest.credentials.get()>before&&host.pauses.get()+guest.pauses.get()>pauses,"fresh credential and pause after "+role);
                // Upload pending TCP bytes during recovery; delivery must remain exact with the same sockets.
                transfer(hostNative,guestNative,3+before);transfer(guestNative,hostNative,4+before);
                until(()->!host.paused&&!guest.paused,"coordinated return after "+role);
                JSONObject snapshot=state().getJSONObject("snapshot");check(snapshot.getJSONObject("room").getString("roomId").equals(fixture.getProperty("room")),"same logical match after "+role);
                check(!hostNative.isClosed()&&!guestNative.isClosed(),"native TCP preserved after "+role);
            }
            guest.tunnel.visible(false);until(()->host.paused,"background pauses peer");guest.tunnel.visible(true);until(()->!host.paused&&!guest.paused,"foreground resumes same stream");
            int pausedBefore=host.pauses.get();host.stalled=true;until(()->host.pauses.get()>pausedBefore,"native stall requests synchronized wait");
            transfer(hostNative,guestNative,99);until(()->!host.paused&&!guest.paused,"native stall synchronization returns");
            check(!host.failed&&!guest.failed,"no irrecoverable synthetic native state");
            until(()->{JSONObject status=state().getJSONObject("recovery");return status.getLong("pendingBytes")==0&&status.getInt("activeConnections")==2;},"bounded storage reclaimed after native delivery");
            System.out.println(new JSONObject().put("passed",true).put("checks",checks).put("tcpBytesVerified",verifiedBytes).put("scope","Actual Java/.NET TLS WSS and preserved TCP; synthetic native pause, not gameplay"));
        }finally{host.tunnel.close();guest.tunnel.close();hostNative.close();guestNative.close();listener.close();io.shutdownNow();}
    }
}
