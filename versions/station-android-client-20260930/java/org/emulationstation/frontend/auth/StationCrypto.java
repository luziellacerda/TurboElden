package org.emulationstation.frontend.auth;

import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.MGF1ParameterSpec;
import java.security.spec.PSSParameterSpec;
import java.security.spec.X509EncodedKeySpec;

/** Device proof and server grant verification use RSA-PSS SHA-256, MGF1-SHA-256, salt 32. */
final class StationCrypto {
    private static final String ALIAS = "turborama.station.device.v1";
    private static final PSSParameterSpec PSS = new PSSParameterSpec(
            "SHA-256", "MGF1", MGF1ParameterSpec.SHA256, 32, 1);

    private StationCrypto() {}

    static String b64(byte[] value) {
        return Base64.encodeToString(value, Base64.URL_SAFE | Base64.NO_PADDING | Base64.NO_WRAP);
    }

    static byte[] unb64(String value) {
        return Base64.decode(value, Base64.URL_SAFE | Base64.NO_PADDING | Base64.NO_WRAP);
    }

    static byte[] utf8(String value) { return value.getBytes(StandardCharsets.UTF_8); }

    static KeyPair deviceKey(boolean create) throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (store.containsAlias(ALIAS)) {
            return new KeyPair(store.getCertificate(ALIAS).getPublicKey(), (PrivateKey) store.getKey(ALIAS, null));
        }
        if (!create) return null;
        KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA", "AndroidKeyStore");
        generator.initialize(new KeyGenParameterSpec.Builder(ALIAS, KeyProperties.PURPOSE_SIGN)
                .setKeySize(2048)
                .setDigests(KeyProperties.DIGEST_SHA256)
                .setSignaturePaddings(KeyProperties.SIGNATURE_PADDING_RSA_PSS)
                .build());
        return generator.generateKeyPair();
    }

    static String deviceId(PublicKey key) throws Exception {
        return b64(MessageDigest.getInstance("SHA-256").digest(key.getEncoded()));
    }

    static String sign(PrivateKey key, byte[] bytes) throws Exception {
        Signature signature = Signature.getInstance("SHA256withRSA/PSS");
        signature.setParameter(PSS);
        signature.initSign(key);
        signature.update(bytes);
        return b64(signature.sign());
    }

    static void verifyServer(byte[] bytes, String signatureText, String keyId) throws Exception {
        if (!StationConfig.ready() || !StationConfig.SERVER_KEY_ID.equals(keyId))
            throw new SecurityException("Autoridade do servidor indisponível");
        PublicKey key = KeyFactory.getInstance("RSA").generatePublic(
                new X509EncodedKeySpec(unb64(StationConfig.SERVER_PUBLIC_KEY_SPKI_BASE64URL)));
        Signature signature = Signature.getInstance("SHA256withRSA/PSS");
        signature.setParameter(PSS);
        signature.initVerify(key);
        signature.update(bytes);
        if (!signature.verify(unb64(signatureText)))
            throw new SecurityException("Resposta do servidor inválida");
    }
}
