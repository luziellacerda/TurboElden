package com.bachatas4.android.runtime.pkg;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.math.BigInteger;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.spec.RSAPrivateCrtKeySpec;
import java.util.Arrays;
import javax.crypto.Cipher;

/** PKG callback reconstructed from the pinned APK contract; material stays in private build inputs. */
public final class PkgRsa {
    private static PrivateKey primary, secondary;
    private PkgRsa() {}
    public static synchronized void initialize(File material) throws Exception {
        if (primary != null) return;
        byte[][] values = new byte[16][];
        try (DataInputStream in = new DataInputStream(new FileInputStream(material))) {
            if (in.readInt() != 0x50345231 || in.readInt() != 16)
                throw new IOException("Material PKG inválido");
            for (int i=0;i<16;i++) {
                int n=in.readInt();
                if (n < 1 || n > 256) throw new IOException("Material PKG inválido");
                values[i]=new byte[n]; in.readFully(values[i]);
            }
            if (in.read()!=-1) throw new IOException("Material PKG excedente");
        }
        primary=key(values,0); secondary=key(values,8);
        for (byte[] value:values) Arrays.fill(value,(byte)0);
    }
    private static BigInteger integer(byte[] value) { return new BigInteger(1,value); }
    private static PrivateKey key(byte[][] v, int i) throws Exception {
        // Original PkgRsa.a: modulus, publicExponent(last), privateExponent, p,q,dp,dq,coefficient.
        return KeyFactory.getInstance("RSA").generatePrivate(new RSAPrivateCrtKeySpec(
            integer(v[i]),integer(v[i+7]),integer(v[i+1]),integer(v[i+2]),integer(v[i+3]),
            integer(v[i+4]),integer(v[i+5]),integer(v[i+6])));
    }
    public static byte[] decrypt(byte[] ciphertext, boolean second) throws Exception {
        if (ciphertext == null || ciphertext.length != 256 || primary == null)
            throw new IOException("PKG RSA não preparado");
        Cipher cipher=Cipher.getInstance("RSA/ECB/PKCS1Padding");
        cipher.init(Cipher.DECRYPT_MODE,second?secondary:primary);
        byte[] plain=cipher.doFinal(ciphertext);
        if (plain.length==0) throw new IOException("PKG RSA vazio");
        if (plain.length>=32) return Arrays.copyOfRange(plain,0,32);
        byte[] padded=new byte[32];
        System.arraycopy(plain,0,padded,32-plain.length,plain.length);
        return padded;
    }
}
