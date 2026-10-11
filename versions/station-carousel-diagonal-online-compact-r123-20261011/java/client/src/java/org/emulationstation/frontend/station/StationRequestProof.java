package org.emulationstation.frontend.station;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;

/** Binds a credential to one control/GET request. Game files are never hashed here. */
final class StationRequestProof {
    private static final SecureRandom RANDOM=new SecureRandom();
    private StationRequestProof(){}
    static byte[] challenge(String deviceId,String authorityId)throws Exception {
        return MessageDigest.getInstance("SHA-256").digest(("TurboRamaStationAndroid/key-attestation/v1\n"+
            deviceId+"\n"+authorityId+"\n").getBytes(StandardCharsets.UTF_8));
    }
    static byte[] canonical(String method,String target,byte[] body,String credential,long timestamp,String nonce)throws Exception {
        return ("TurboRamaStationAndroid/request/v1\n"+method+"\n"+target+"\n"+
            hash(body==null?new byte[0]:body)+"\n"+hash(credential.getBytes(StandardCharsets.US_ASCII))+"\n"+
            Long.toString(timestamp)+"\n"+nonce+"\n").getBytes(StandardCharsets.UTF_8);
    }
    static String nonce(){byte[] bytes=new byte[16];RANDOM.nextBytes(bytes);return StationProtocol.base64Url(bytes);}
    private static String hash(byte[] value)throws Exception {
        byte[] bytes=MessageDigest.getInstance("SHA-256").digest(value);StringBuilder out=new StringBuilder(64);
        char[] digits="0123456789abcdef".toCharArray();
        for(byte b:bytes){out.append(digits[(b&255)>>>4]);out.append(digits[b&15]);}return out.toString();
    }
}
