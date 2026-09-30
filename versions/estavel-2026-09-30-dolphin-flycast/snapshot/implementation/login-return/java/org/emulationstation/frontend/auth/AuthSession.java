package org.emulationstation.frontend.auth;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;
import android.util.Log;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.util.Arrays;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** Keep a successfully authenticated local session across frontend process recreation.
 * No password is stored. The encrypted record is private, excluded from Android backup,
 * and bound to this app's non-exportable Android Keystore key and password revision.
 */
public final class AuthSession {
    private static final String ALIAS="turborama.auth.session.v1";
    private static final byte[] MARKER="authenticated-v1:a73a0854a7696362b0011059927413b3580582952e7f6774b5edd4e33a7c0168".getBytes(StandardCharsets.UTF_8);
    private static volatile boolean authorized;
    private static Context context;
    private AuthSession() {}

    public static synchronized void attach(Context value) {
        if (context!=null) return;
        Context application=value.getApplicationContext();
        context=application!=null?application:value;
        // Only load a record created after successful password validation.
        authorized=restore();
    }
    public static boolean isAuthorized() { return authorized; }
    public static synchronized boolean authenticate(String value) {
        if (!LocalPassword.matches(value)) return false;
        authorized=true;
        persist();
        return true;
    }
    private static AtomicFile file() {
        return new AtomicFile(new File(context.getNoBackupFilesDir(),"authenticated-session-v1.bin"));
    }
    private static SecretKey key(boolean create) throws Exception {
        KeyStore store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
        if (store.containsAlias(ALIAS)) return (SecretKey)store.getKey(ALIAS,null);
        if (!create) return null;
        KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256).build());
        return generator.generateKey();
    }
    private static boolean restore() {
        if(context==null) return false;
        try {
            AtomicFile session=file();
            if(!session.getBaseFile().exists()||session.getBaseFile().length()>512) return false;
            byte[] bytes=session.readFully();
            if(bytes.length<30||bytes[0]!=1) return false;
            SecretKey secret=key(false);if(secret==null) return false;
            Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE,secret,new GCMParameterSpec(128,Arrays.copyOfRange(bytes,1,13)));
            cipher.updateAAD(context.getPackageName().getBytes(StandardCharsets.UTF_8));
            return MessageDigest.isEqual(MARKER,cipher.doFinal(bytes,13,bytes.length-13));
        } catch(Exception failure) {
            // Missing, invalid or undecryptable state always requires the original login.
            Log.i("TurboAuth","Stored session unavailable; authentication required");
            return false;
        }
    }
    private static void persist() {
        if(context==null) return;
        AtomicFile session=file();FileOutputStream output=null;
        try {
            Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.ENCRYPT_MODE,key(true));
            cipher.updateAAD(context.getPackageName().getBytes(StandardCharsets.UTF_8));
            byte[] iv=cipher.getIV();if(iv.length!=12) throw new IllegalStateException("Unexpected IV length");
            byte[] encrypted=cipher.doFinal(MARKER);
            output=session.startWrite();output.write(1);output.write(iv);output.write(encrypted);
            session.finishWrite(output);output=null;
        } catch(Exception failure) {
            if(output!=null)session.failWrite(output);
            Log.w("TurboAuth","Session could not be saved; login remains valid for this process");
        }
    }
}
