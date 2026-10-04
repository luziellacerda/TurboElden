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

/** Device identity. RSA 2048, non-exportable, Android Keystore. Not a Suite TPM key. */
public final class StationCrypto {
    public static final String ALIAS = "turborama.station.device.v1";
    private static final PSSParameterSpec PSS = new PSSParameterSpec("SHA-256", "MGF1", MGF1ParameterSpec.SHA256, 32, 1);

    private StationCrypto() {}

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
