package org.emulationstation.frontend.netplay;
import org.emulationstation.frontend.station.StationRecoveryProofTest;
import org.json.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;
public final class StationRecoveryVectorsTest {
    static int checks;
    static void check(boolean ok){checks++;if(!ok)throw new AssertionError("Public vector "+checks);}
    static byte[] decode(String value){return Base64.getUrlDecoder().decode(value);}
    static byte[] hex(String value){byte[] data=new byte[value.length()/2];for(int i=0;i<data.length;i++)data[i]=(byte)Integer.parseInt(value.substring(2*i,2*i+2),16);return data;}
    public static void main(String[] args)throws Exception{
        JSONObject vectors=new JSONObject(new String(Files.readAllBytes(Paths.get(args[0])),StandardCharsets.UTF_8));
        PublicKey key=KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(decode(vectors.getString("publicKeySpkiBase64Url"))));
        JSONArray proofs=vectors.getJSONArray("requestProof");
        for(int i=0;i<proofs.length();i++){
            JSONObject v=proofs.getJSONObject(i);byte[] data=StationRecoveryProofTest.canonical(v.getString("method"),v.getString("target"),decode(v.getString("bodyBase64Url")),v.getString("syntheticCredential"),v.getLong("timestamp"),v.getString("nonce"));
            check(new String(data,StandardCharsets.UTF_8).equals(v.getString("canonicalUTF8")));
            Signature signature=Signature.getInstance("RSASSA-PSS");signature.initVerify(key);signature.setParameter(new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1));signature.update(data);check(signature.verify(decode(v.getString("signatureBase64Url"))));
        }
        JSONArray wire=vectors.getJSONArray("wire");
        for(int i=0;i<wire.length();i++){
            JSONObject v=wire.getJSONObject(i);byte[] bytes=hex(v.getString("frameHex"));StationRecoveryWire frame=StationRecoveryWire.decode(ByteBuffer.wrap(bytes));
            check(frame.type==v.getInt("type")&&frame.offset==v.getLong("offset")&&frame.value==v.getLong("value"));
            check(Arrays.equals(bytes,frame.encode()));
        }
        System.out.println("{\"passed\":true,\"checks\":"+checks+",\"scope\":\"Public Python/.NET/Java binary and RSA-PSS vectors, no Android execution\"}");
    }
}
