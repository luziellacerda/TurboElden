package org.emulationstation.frontend.station;
import java.security.*;
import java.security.spec.*;
import java.util.Base64;
public final class StationRecoveryProofTest {
    public static byte[] canonical(String method,String path,byte[] body,String credential,long timestamp,String nonce)throws Exception{
        return StationRequestProof.canonical(method,path,body,credential,timestamp,nonce);
    }
    public static String proof(PrivateKey key,String credential,String method,String path,byte[] body)throws Exception{
        long timestamp=System.currentTimeMillis()/1000;String nonce=StationRequestProof.nonce();
        Signature signature=Signature.getInstance("RSASSA-PSS");signature.initSign(key);
        signature.setParameter(new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1));
        signature.update(StationRequestProof.canonical(method,path,body,credential,timestamp,nonce));
        return "v1."+timestamp+"."+nonce+"."+Base64.getUrlEncoder().withoutPadding().encodeToString(signature.sign());
    }
}
