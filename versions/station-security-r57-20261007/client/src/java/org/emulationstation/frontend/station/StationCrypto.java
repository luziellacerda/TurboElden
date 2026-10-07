package org.emulationstation.frontend.station;

import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.MGF1ParameterSpec;
import java.security.spec.PSSParameterSpec;
import java.security.MessageDigest;
import java.security.cert.X509Certificate;
import java.security.spec.ECGenParameterSpec;
import java.util.Enumeration;
import java.util.Arrays;

/** Device identity. RSA 2048, non-exportable, Android Keystore. Not a Suite TPM key. */
public final class StationCrypto {
    public static final String ALIAS = "turborama.station.device.v1";
    private static final PSSParameterSpec PSS = new PSSParameterSpec("SHA-256", "MGF1", MGF1ParameterSpec.SHA256, 32, 1);

    private StationCrypto() {}
    private static StationApi.RequestKey cachedRequestKey;
    private static byte[] cachedChallenge;
    private static long retryAfter;

    /** Secondary key only. The existing RSA alias and license binding survive upgrades. */
    public static synchronized StationApi.RequestKey requestKey(byte[] challenge)throws Exception {
        if(challenge==null||challenge.length!=32)throw new java.security.GeneralSecurityException("Invalid attestation challenge");
        if(cachedRequestKey!=null&&Arrays.equals(cachedChallenge,challenge)&&usable(cachedRequestKey.certificates()))
            return cachedRequestKey;
        long now=android.os.SystemClock.elapsedRealtime();
        if(now<retryAfter)return null;
        String generatedAlias=null;
        try{
            KeyStore store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
            String prefix="turborama.station.request.v1."+StationProtocol.base64Url(MessageDigest.getInstance("SHA-256").digest(challenge)).substring(0,16)+".";
            String alias=null;Enumeration<String> names=store.aliases();
            while(names.hasMoreElements()){
                String candidate=names.nextElement();
                if(candidate.startsWith(prefix)&&usable(encoded(store,candidate))){alias=candidate;break;}
            }
            if(alias==null){
                alias=prefix+java.util.UUID.randomUUID().toString();
                generatedAlias=alias;
                KeyPairGenerator generator=KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC,"AndroidKeyStore");
                generator.initialize(new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_SIGN)
                    .setAlgorithmParameterSpec(new ECGenParameterSpec("secp256r1"))
                    .setDigests(KeyProperties.DIGEST_SHA256).setAttestationChallenge(challenge)
                    .setUserAuthenticationRequired(false).build());
                generator.generateKeyPair();
            }
            final PublicKey publicKey=store.getCertificate(alias).getPublicKey();
            final PrivateKey privateKey=(PrivateKey)store.getKey(alias,null);final byte[][] certificates=encoded(store,alias);
            if(!usable(certificates))throw new java.security.GeneralSecurityException("Attestation unavailable");
            cachedRequestKey=new StationApi.RequestKey(){
                public PublicKey publicKey(){return publicKey;}
                public byte[] sign(byte[] payload)throws Exception {
                    Signature signature=Signature.getInstance("SHA256withECDSA");signature.initSign(privateKey);
                    signature.update(payload);return signature.sign();
                }
                public byte[][] certificates(){byte[][] copy=new byte[certificates.length][];
                    for(int i=0;i<copy.length;i++)copy[i]=certificates[i].clone();return copy;}
            };
            cachedChallenge=challenge.clone();return cachedRequestKey;
        }catch(Exception unavailable){
            // Only discard a new secondary key that was never returned to a session.
            // Older request keys and the principal RSA alias stay intact.
            if(generatedAlias!=null)try{
                KeyStore cleanup=KeyStore.getInstance("AndroidKeyStore");cleanup.load(null);
                cleanup.deleteEntry(generatedAlias);
            }catch(Exception ignored){}
            retryAfter=now+3600000;return null;
        }
    }
    private static byte[][] encoded(KeyStore store,String alias)throws Exception {
        java.security.cert.Certificate[] chain=store.getCertificateChain(alias);
        if(chain==null||chain.length<2||chain.length>6)throw new java.security.GeneralSecurityException("Missing attestation chain");
        byte[][] out=new byte[chain.length][];for(int i=0;i<chain.length;i++)out[i]=chain[i].getEncoded();return out;
    }
    private static boolean usable(byte[][] chain){
        try{
            java.security.cert.CertificateFactory factory=java.security.cert.CertificateFactory.getInstance("X.509");
            for(int i=0;i<chain.length-1;i++){
                X509Certificate certificate=(X509Certificate)factory.generateCertificate(new java.io.ByteArrayInputStream(chain[i]));
                certificate.checkValidity(new java.util.Date(System.currentTimeMillis()+60000));
            }
            return true;
        }catch(Exception unavailable){return false;}
    }

    public static synchronized PublicKey publicKey() throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (!store.containsAlias(ALIAS)) {
            KeyPairGenerator generator = KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_RSA, "AndroidKeyStore");
            generator.initialize(new KeyGenParameterSpec.Builder(ALIAS, KeyProperties.PURPOSE_SIGN)
                .setKeySize(2048)
                .setDigests(KeyProperties.DIGEST_SHA256)
                .setSignaturePaddings(KeyProperties.SIGNATURE_PADDING_RSA_PSS)
                .build());
            generator.generateKeyPair();
        }
        return store.getCertificate(ALIAS).getPublicKey();
    }

    public static byte[] sign(byte[] message) throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        PrivateKey key = (PrivateKey) store.getKey(ALIAS, null);
        Signature signature = Signature.getInstance("SHA256withRSA/PSS");
        signature.setParameter(PSS);
        signature.initSign(key);
        signature.update(message);
        return signature.sign();
    }
}
