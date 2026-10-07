package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import org.json.*;

/** Synthetic signed authority in memory. No production, Android key store or files. */
public final class StationSecurityNegotiationTest {
    static int checks;
    static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
    interface Action {void run()throws Exception;}
    static void denied(Action action)throws Exception{
        try{action.run();throw new AssertionError("Expected refusal");}catch(IOException expected){checks++;}
    }
    static final class Wire implements StationApi.Transport {
        final StationApiTest.Fake fixture=new StationApiTest.Fake();
        final Set<String> nonces=new HashSet<>();
        boolean badChallenge,downgrade;int proofs;
        Wire()throws Exception{}
        @Override public boolean supportsRequestProof(){return true;}
        @Override public StationApi.Response exchange(String m,String p,byte[] b,String token,StationApi.Cancellation c)throws IOException{
            return exchange(m,p,b,token,null,c);
        }
        @Override public StationApi.Response exchange(String method,String path,byte[] body,String token,String proof,StationApi.Cancellation cancel)throws IOException{
            try{
                if(token!=null){check(proof!=null,"Authenticated request signed");verify(proof,method,path,body,token);proofs++;}
                else check(proof==null,"No bearer proof before session");
                StationApi.Response response=fixture.exchange(method,path,body,token,cancel);
                if(!path.equals("/v1/station/challenges")&&!path.equals("/v1/station/activations/challenge")&&!path.equals("/v1/station/sessions"))return response;
                byte[] bytes;try(StationApi.Response ignored=response){bytes=response.body.readAllBytes();}
                JSONObject envelope=new JSONObject(new String(bytes,StandardCharsets.UTF_8));
                JSONObject payload=new JSONObject(new String(StationProtocol.decode(envelope.getString("payload")),StandardCharsets.UTF_8));
                if(path.endsWith("/sessions"))payload.put("requestProof",downgrade?"none":"rsa-pss-v1").put("verifiedApp",false).put("serverTime",1791370000L);
                else payload.put("security",new JSONObject().put("requestProofVersion",1).put("keyAttestation",false).put("requireVerifiedApp",false)
                    .put("keyAttestationChallenge",StationProtocol.base64Url(badChallenge?new byte[32]:StationRequestProof.challenge(fixture.deviceId,"test-key"))));
                byte[] updated=payload.toString().getBytes(StandardCharsets.UTF_8);
                byte[] signed=new JSONObject().put("keyId","test-key").put("payload",StationProtocol.base64Url(updated))
                    .put("signature",StationProtocol.base64Url(StationApiTest.sign(fixture.authority,updated))).toString().getBytes(StandardCharsets.UTF_8);
                return new StationApi.Response(200,"application/json",signed.length,new ByteArrayInputStream(signed),()->{});
            }catch(IOException e){throw e;}catch(Exception e){throw new IOException(e);}
        }
        void verify(String proof,String method,String path,byte[] body,String token)throws Exception{
            String[] parts=proof.split("\\.");check(parts.length==4&&parts[0].equals("v1"),"Proof format");
            check(parts[2].matches("[A-Za-z0-9_-]{22}")&&nonces.add(parts[2]),"Fresh nonce");
            byte[] canonical=StationRequestProof.canonical(method,path,body,token,Long.parseLong(parts[1]),parts[2]);
            Signature signature=Signature.getInstance("RSASSA-PSS");signature.setParameter(StationApiTest.PSS);signature.initVerify(fixture.device.getPublic());signature.update(canonical);
            check(signature.verify(StationProtocol.decode(parts[3])),"Method/path/body/credential signature");
        }
        StationApi api()throws Exception{return new StationApi(this,fixture,fixture,fixture.authority.getPublic(),"test-key");}
    }
    public static void main(String[] args)throws Exception{
        Wire wire=new Wire();StationApi api=wire.api();StationApi.Cancellation cancel=new StationApi.Cancellation();
        check(api.activate(StationApiTest.token(9),cancel).equals(wire.fixture.license),"Existing identity activation");
        StationApi.Session session=api.openSession(wire.fixture.license,cancel);
        check(api.profile(session,cancel).equals("Comprador"),"Protected profile");
        check(api.catalog(session,cancel).items.size()==1,"Protected catalog");
        for(int i=0;i<4;i++)check(api.cover(session,"cover_12345",cancel).length==8,"Protected cover");
        api.authorize(session,"item_12345",1,cancel);
        check(wire.proofs==7,"Every authenticated request uses proof");
        String ticket=StationApiTest.token(5),proof=api.relayRequestProof(session,ticket);
        wire.verify(proof,"GET","/v1/station/online/relay",null,ticket);
        wire.fixture.time+=2000;
        String later=api.relayRequestProof(session,ticket);
        check(Long.parseLong(later.split("\\.")[1])-Long.parseLong(proof.split("\\.")[1])==2,"Monotonic server time");
        denied(()->api.relayRequestProof(wire.api().openSession(wire.fixture.license,cancel),ticket));
        wire.badChallenge=true;denied(()->api.openSession(wire.fixture.license,cancel));wire.badChallenge=false;
        wire.downgrade=true;denied(()->api.openSession(wire.fixture.license,cancel));
        Set<String> nonces=new HashSet<>();for(int i=0;i<64;i++)check(nonces.add(StationRequestProof.nonce()),"Nonce uniqueness");
        byte[] canonical=StationRequestProof.canonical("POST","/v1/station/online/command",new byte[]{1},ticket,1791370000,"abcdefghijklmnopqrstuv");
        check(!Arrays.equals(canonical,StationRequestProof.canonical("GET","/v1/station/online/command",new byte[]{1},ticket,1791370000,"abcdefghijklmnopqrstuv")),"Method bound");
        check(!Arrays.equals(canonical,StationRequestProof.canonical("POST","/v1/station/online/events",new byte[]{1},ticket,1791370000,"abcdefghijklmnopqrstuv")),"Route bound");
        check(!Arrays.equals(canonical,StationRequestProof.canonical("POST","/v1/station/online/command",new byte[]{2},ticket,1791370000,"abcdefghijklmnopqrstuv")),"Body bound");
        check(!Arrays.equals(canonical,StationRequestProof.canonical("POST","/v1/station/online/command",new byte[]{1},StationApiTest.token(6),1791370000,"abcdefghijklmnopqrstuv")),"Credential bound");
        System.out.println("PASS "+checks+" security negotiation checks; synthetic authority, no disk writes or production traffic");
    }
}
