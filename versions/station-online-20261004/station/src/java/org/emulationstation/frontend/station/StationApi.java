package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.*;
import java.nio.charset.*;
import java.nio.file.Path;
import java.security.*;
import java.security.spec.*;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;
import org.json.*;

/** Direct, typed implementation of Servidor-pix StationService at 1bfb619. */
public final class StationApi {
    public interface Device {
        PublicKey publicKey() throws Exception;
        byte[] sign(byte[] payload) throws Exception;
        String manufacturer(); String model(); int sdk();
    }
    public interface Clock { long millis(); }
    public interface Transport {
        Response exchange(String method, String path, byte[] body, String bearer, Cancellation cancel) throws IOException;
    }
    public static final class Response implements AutoCloseable {
        final int status; final String type; final long length; final InputStream body;
        private final Closeable owner;
        final long retryAfterMillis;
        public Response(int status, String type, long length, InputStream body, Closeable owner) {
            this(status,type,length,body,owner,0);
        }
        public Response(int status,String type,long length,InputStream body,Closeable owner,long retryAfterMillis) {
            this.status=status; this.type=type; this.length=length; this.body=body; this.owner=owner;this.retryAfterMillis=retryAfterMillis;
        }
        @Override public void close() throws IOException { owner.close(); }
    }
    public static final class Cancellation implements StationFiles.Cancellation {
        private volatile boolean cancelled;
        private Runnable abort;
        public synchronized void cancel() { cancelled=true; if (abort != null) abort.run(); }
        @Override public boolean cancelled() { return cancelled || Thread.currentThread().isInterrupted(); }
        public void check() throws InterruptedIOException {
            if (cancelled()) throw new InterruptedIOException("Station operation cancelled");
        }
        synchronized void attach(Runnable action) throws InterruptedIOException {
            check(); if (abort != null) throw new IllegalStateException("Cancellation already in use"); abort=action;
        }
        synchronized void detach(Runnable action) { if (abort == action) abort=null; }
    }
    public static final class Failure extends IOException {
        public final int status;
        public final String code;
        public final long retryAfterMillis;
        Failure(int status,String code){this(status,code,0);}
        Failure(int status,String code,long retryAfterMillis){super("Station " + status + " " + code);this.status=status;this.code=code;this.retryAfterMillis=retryAfterMillis;}
        public boolean sessionDenied() { return status == 401 || status == 403; }
    }
    public static final class Session {
        public final String licenseId, deviceId, sessionId;
        private final String token;
        private final long expires;
        private final StationApi owner;
        private Session(StationApi owner,String licenseId,String deviceId,String sessionId,String token,long expires) {
            this.owner=owner;this.licenseId=licenseId;this.deviceId=deviceId;this.sessionId=sessionId;this.token=token;this.expires=expires;
        }
        public boolean needsRenewal(long monotonicMillis) { return monotonicMillis >= expires - 15000; }
    }
    public static final class Grant {
        public final String itemId;
        public final long itemRevision;
        public final StationArtifact artifact;
        private final String grantId;
        private final long expires;
        private final Session session;
        private final AtomicBoolean consumed = new AtomicBoolean();
        private Grant(String itemId,long revision,StationArtifact artifact,String grantId,long expires,Session session) {
            this.itemId=itemId;this.itemRevision=revision;this.artifact=artifact;this.grantId=grantId;this.expires=expires;this.session=session;
        }
    }
    public static final class CatalogSnapshot {
        public final StationCatalog catalog;
        private final byte[] signedEnvelope;
        private CatalogSnapshot(StationCatalog catalog,byte[] signedEnvelope) {
            this.catalog=catalog;this.signedEnvelope=signedEnvelope;
        }
        public byte[] encoded() { return signedEnvelope.clone(); }
    }
    private static final class SignedReply {
        final JSONObject payload; final byte[] envelope;
        SignedReply(JSONObject payload,byte[] envelope) {this.payload=payload;this.envelope=envelope;}
    }
    private static final String ROOT="/v1/station/";
    private static final PSSParameterSpec PSS=new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1);
    private final Transport transport;
    private final Device device;
    private final Clock clock;
    private final PublicKey authority;
    private final String authorityId;
    private final String deviceId;

    public StationApi(Transport transport, Device device, Clock clock, PublicKey authority, String authorityId) throws Exception {
        this.transport=transport;this.device=device;this.clock=clock;this.authority=authority;this.authorityId=authorityId;
        this.deviceId=StationProtocol.deviceId(device.publicKey().getEncoded());
    }

    public String activate(String code, Cancellation cancel) throws Exception {
        token(code);
        String key=StationProtocol.base64Url(device.publicKey().getEncoded());
        String extra=field("activationCode",code)+","+field("devicePublicKey",key);
        long started=clock.millis();
        JSONObject challenge=signed("POST","activations/challenge",identity(StationProtocol.REQUEST_ACTIVATION,extra),null,
            StationProtocol.ACTIVATION_CHALLENGE,StationProtocol.MAXIMUM_BODY_BYTES,cancel);
        lifetime(challenge,60); String challengeId=hexId(string(challenge,"challengeId")); String nonce=token(string(challenge,"nonce"));
        notExpired(started+60000);
        byte[] proof=identity(StationProtocol.ACTIVATE,extra+","+field("challengeId",challengeId)+","+field("nonce",nonce));
        JSONObject result=signed("POST","activations/complete",envelope(proof),null,StationProtocol.ACTIVATED,
            StationProtocol.MAXIMUM_BODY_BYTES,cancel);
        equal(result,"challengeId",challengeId); equal(result,"nonce",nonce);
        String license=string(result,"licenseId");
        if (!StationProtocol.licenseId(license)) throw new IOException("Invalid license identifier");
        return license;
    }

    public Session openSession(String licenseId,Cancellation cancel) throws Exception {
        if (!StationProtocol.licenseId(licenseId)) throw new IOException("Invalid license identifier");
        long started=clock.millis();
        JSONObject challenge=signed("POST","challenges",identity(StationProtocol.REQUEST_SESSION,field("licenseId",licenseId)),
            null,StationProtocol.SESSION_CHALLENGE,StationProtocol.MAXIMUM_BODY_BYTES,cancel);
        equal(challenge,"licenseId",licenseId); lifetime(challenge,60);
        String challengeId=hexId(string(challenge,"challengeId")),nonce=token(string(challenge,"nonce"));
        notExpired(started+60000);
        byte[] proof=identity(StationProtocol.OPEN_SESSION,field("licenseId",licenseId)+","+field("challengeId",challengeId)+","+field("nonce",nonce));
        long sessionStart=clock.millis();
        JSONObject result=signed("POST","sessions",envelope(proof),null,StationProtocol.SESSION,StationProtocol.MAXIMUM_BODY_BYTES,cancel);
        equal(result,"licenseId",licenseId);equal(result,"challengeId",challengeId);equal(result,"nonce",nonce);lifetime(result,180);
        String id=string(result,"sessionId");
        if (!id.matches("[0-9a-f]{64}")) throw new IOException("Invalid session identifier");
        notExpired(sessionStart+180000);
        return new Session(this,licenseId,deviceId,id,token(string(result,"accessToken")),sessionStart+180000);
    }

    /** Signed, request-bound response; credentials remain private to this transport. */
    public JSONObject online(Session session,boolean events,JSONObject request,Cancellation cancel)throws Exception {
        String requestId=string(request,"requestId");
        if(!requestId.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))throw new IOException("Invalid online request ID");
        byte[] body=request.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
        if(body.length>8192)throw new IOException("Online request too large");
        JSONObject result=signed("POST",events?"online/events":"online/command",body,session,
            "TurboRamaStationAndroid/online/v1",524288,cancel);
        equal(result,"requestId",requestId);
        JSONObject snapshot=result.getJSONObject("snapshot");
        if(snapshot.getInt("schemaVersion")!=1)throw new IOException("Unsupported online snapshot");
        return snapshot;
    }

    public String profile(Session session,Cancellation cancel) throws Exception {
        JSONObject profile=signed("GET","me",null,session,StationProtocol.PROFILE,StationProtocol.MAXIMUM_BODY_BYTES,cancel);
        StationCatalog.integer(profile,"profileVersion");
        return StationCatalog.plainText(string(profile,"displayName"),80);
    }

    public StationCatalog catalog(Session session,Cancellation cancel) throws Exception {
        return catalogSnapshot(session,cancel).catalog;
    }
    public CatalogSnapshot catalogSnapshot(Session session,Cancellation cancel) throws Exception {
        SignedReply reply=signedReply("GET","catalog",null,session,StationProtocol.CATALOG,
            StationProtocol.CATALOG_BODY_BYTES,cancel);
        return new CatalogSnapshot(StationCatalog.fromVerifiedPayload(reply.payload),reply.envelope);
    }
    /** Cached catalog is display data only; caller must already hold a valid session. */
    public CatalogSnapshot restoreCatalog(byte[] envelope,Session session) throws Exception {
        valid(session);
        if (envelope.length > StationProtocol.CATALOG_BODY_BYTES) throw new IOException("Catalog cache too large");
        JSONObject payload=verify(envelope,StationProtocol.CATALOG,session,true);
        return new CatalogSnapshot(StationCatalog.fromVerifiedPayload(payload),envelope.clone());
    }

    public byte[] cover(Session session,String coverId,Cancellation cancel) throws Exception {
        StationCatalog.libraryId(coverId); valid(session);
        try (Response response=transport.exchange("GET",ROOT+"covers/"+coverId,null,session.token,cancel)) {
            success(response,cancel);
            byte[] bytes=read(response,StationProtocol.COVER_BODY_BYTES,cancel);
            String ext=StationFiles.imageExtension(bytes),type=mime(response.type);
            String expected=ext.equals("jpg")?"image/jpeg":"image/"+ext;
            if (!type.equals(expected) && !(ext.equals("jpg") && type.equals("image/jpg")))
                throw new IOException("Cover MIME and bytes disagree");
            return bytes;
        }
    }

    public static final class ArtifactUnavailable extends IOException {
        ArtifactUnavailable(){super("Signed artifact descriptor unavailable");}
    }
    public Grant authorize(Session session,String itemId,long expectedRevision,Cancellation cancel) throws Exception {
        StationCatalog.libraryId(itemId);
        if(expectedRevision<1)throw new IOException("Missing catalog item revision");
        long started=clock.millis();
        JSONObject result=signed("POST","downloads/authorize",identity(StationProtocol.REQUEST_DOWNLOAD,field("itemId",itemId)),
            session,StationProtocol.DOWNLOAD_GRANT,StationProtocol.MAXIMUM_BODY_BYTES,cancel);
        equal(result,"itemId",itemId);lifetime(result,60);notExpired(started+60000);
        if(!result.has("itemRevision")||!(result.opt("artifact") instanceof JSONObject))throw new ArtifactUnavailable();
        long revision=StationCatalog.integer(result,"itemRevision");
        if(revision!=expectedRevision)throw new IOException("Authorized item revision changed; refresh catalog");
        StationArtifact artifact=StationArtifact.parse(result.getJSONObject("artifact"));
        return new Grant(itemId,revision,artifact,token(string(result,"grantId")),started+60000,session);
    }

    /** Publishes staging only after size and signed digest match. Installation is a separate transaction. */
    public StationFiles.Receipt downloadToStaging(Grant grant,Path stagingFile,long maximumBytes,
            Cancellation cancel,StationFiles.Progress progress) throws Exception {
        try(ArtifactTransfer transfer=openArtifact(grant,maximumBytes,cancel)) {
            return transfer.copyToStaging(stagingFile,cancel,progress);
        }
    }

    /** The server consumes the grant before returning these validated transfer headers. */
    public ArtifactTransfer openArtifact(Grant grant,long maximumBytes,Cancellation cancel) throws Exception {
        valid(grant.session);notExpired(grant.expires);cancel.check();
        if(maximumBytes<grant.artifact.sizeBytes)throw new IOException("Artifact exceeds local transfer limit");
        if (!grant.consumed.compareAndSet(false,true)) throw new IOException("Grant has already been used");
        // Never retry this GET: the server consumes the grant even if the connection later fails.
        Response response=transport.exchange("GET",ROOT+"artifacts/"+grant.grantId,null,grant.session.token,cancel);
        boolean accepted=false;
        try {
            success(response,cancel);
            if (!mime(response.type).equals("application/octet-stream") || response.length != grant.artifact.sizeBytes)
                throw new IOException("Artifact headers invalid");
            ArtifactTransfer transfer=new ArtifactTransfer(response,grant.artifact,maximumBytes);accepted=true;return transfer;
        }finally{if(!accepted)response.close();}
    }
    public static final class ArtifactTransfer implements AutoCloseable {
        private final Response response;private final StationArtifact artifact;private final long maximum;
        private final AtomicBoolean copied=new AtomicBoolean(),closed=new AtomicBoolean();
        private ArtifactTransfer(Response response,StationArtifact artifact,long maximum){this.response=response;this.artifact=artifact;this.maximum=maximum;}
        public StationFiles.Receipt copyToStaging(Path file,Cancellation cancel,StationFiles.Progress progress)throws Exception {
            if(closed.get()||!copied.compareAndSet(false,true))throw new IOException("Transfer has already been used");
            return StationFiles.replace(response.body,file,artifact.sizeBytes,maximum,cancel,progress,artifact.sha256);
        }
        public void close()throws IOException{if(closed.compareAndSet(false,true))response.close();}
    }

    private JSONObject signed(String method,String path,byte[] request,Session session,String domain,int maximum,
            Cancellation cancel) throws Exception {
        return signedReply(method,path,request,session,domain,maximum,cancel).payload;
    }
    private SignedReply signedReply(String method,String path,byte[] request,Session session,String domain,int maximum,
            Cancellation cancel) throws Exception {
        cancel.check();if (session != null) valid(session);
        try (Response response=transport.exchange(method,ROOT+path,request,session == null ? null:session.token,cancel)) {
            success(response,cancel);
            if (!mime(response.type).equals("application/json")) throw new IOException("Unexpected JSON MIME");
            byte[] envelope=read(response,maximum,cancel);
            JSONObject payload=verify(envelope,domain,session,false);
            cancel.check();return new SignedReply(payload,envelope);
        }
    }
    private JSONObject verify(byte[] encoded,String domain,Session session,boolean previousSession) throws Exception {
        JSONObject envelope=new JSONObject(utf8(encoded));
        equal(envelope,"keyId",authorityId);
        byte[] payload=StationProtocol.decode(string(envelope,"payload"));
        byte[] signature=StationProtocol.decode(string(envelope,"signature"));
        Signature verifier;
        try { verifier=Signature.getInstance("RSASSA-PSS"); }
        catch (NoSuchAlgorithmException android) { verifier=Signature.getInstance("SHA256withRSA/PSS"); }
        verifier.setParameter(PSS);verifier.initVerify(authority);verifier.update(payload);
        if (!verifier.verify(signature)) throw new GeneralSecurityException("Station signature rejected");
        JSONObject body=new JSONObject(utf8(payload));
        if (StationCatalog.integer(body,"schemaVersion") != 1) throw new IOException("Unsupported Station schema");
        equal(body,"domain",domain);equal(body,"productId",StationConfig.PRODUCT);
        equal(body,"applicationId",StationConfig.APPLICATION);equal(body,"deviceId",deviceId);
        if (session != null) {
            equal(body,"licenseId",session.licenseId);
            if (previousSession) hexId(string(body,"sessionId"));
            else equal(body,"sessionId",session.sessionId);
        }
        return body;
    }

    private byte[] identity(String domain,String extra) {
        return StationProtocol.identity(domain,deviceId,device.manufacturer(),device.model(),device.sdk(),extra);
    }
    private byte[] envelope(byte[] payload) throws Exception {
        return ("{"+field("payload",StationProtocol.base64Url(payload))+","+
            field("signature",StationProtocol.base64Url(device.sign(payload)))+"}").getBytes(StandardCharsets.UTF_8);
    }
    private void valid(Session session) throws IOException {
        if (session == null || session.owner != this) throw new IOException("Missing Station session"); notExpired(session.expires);
    }
    private void notExpired(long deadline) throws IOException { if (clock.millis() >= deadline) throw new IOException("Station authorization expired"); }
    private static String hexId(String value) throws IOException {
        if (!value.matches("[0-9a-f]{64}")) throw new IOException("Invalid Station identifier");return value;
    }
    private static String token(String token) throws IOException {
        if (!StationProtocol.activationCode(token)) throw new IOException("Invalid Station token");return token;
    }
    private static void lifetime(JSONObject body,int seconds) throws Exception {
        if (StationCatalog.integer(body,"expiresInSeconds") != seconds) throw new IOException("Unexpected authorization lifetime");
    }
    static String string(JSONObject body,String key) throws JSONException,IOException {
        Object value=body.get(key);if (!(value instanceof String)) throw new IOException("Invalid string field: "+key);return (String)value;
    }
    private static void equal(JSONObject body,String key,String expected) throws JSONException,IOException {
        if (!expected.equals(string(body,key))) throw new IOException("Station context mismatch: "+key);
    }
    private static String field(String key,String value) {return StationProtocol.field(key,value);}
    private static String mime(String type) {return type == null?"":type.split(";",2)[0].trim().toLowerCase(Locale.ROOT);}
    private static String utf8(byte[] bytes) throws CharacterCodingException {
        return StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString();
    }
    private static void success(Response response,Cancellation cancel) throws Exception {
        if (response.status == 200) return;
        String code="HTTP_ERROR";
        try {
            JSONObject error=new JSONObject(utf8(read(response,StationProtocol.MAXIMUM_BODY_BYTES,cancel)));
            String candidate=string(error,"code");
            if (candidate.matches("STATION_[A-Z0-9_]{1,80}")) code=candidate;
        } catch (InterruptedIOException e) {throw e;} catch (Exception ignored) { /* Never expose response bodies. */ }
        StationDiagnostics.serverFailure(response.status,code);
        throw new Failure(response.status,code,response.retryAfterMillis);
    }
    private static byte[] read(Response response,int maximum,Cancellation cancel) throws IOException {
        if (response.length > maximum) throw new IOException("Station response too large");
        ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int count;
        while (true) {cancel.check();count=response.body.read(buffer);if(count<0)break;if(count==0)continue;
            if(count>maximum-out.size())throw new IOException("Station response too large");out.write(buffer,0,count);}
        if (response.length >= 0 && out.size() != response.length) throw new IOException("Truncated Station response");
        cancel.check();return out.toByteArray();
    }
}
