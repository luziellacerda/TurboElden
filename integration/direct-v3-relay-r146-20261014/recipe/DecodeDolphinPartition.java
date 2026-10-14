import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.zip.*;
import brut.androlib.smali.SmaliDecoder;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;

/** Decode one pinned DEX partition without extracting or decoding APK media. */
public final class DecodeDolphinPartition {
    public static void main(String[] args)throws Exception {
        if(args.length!=4)throw new IllegalArgumentException("APK, partition, expected SHA256, new output directory");
        if(!"classes35.dex".equals(args[1]) || !args[2].matches("[0-9a-f]{64}")) throw new IllegalArgumentException("Only reviewed R146 DEX35/checksum allowed");
        Path target=Paths.get(args[3]);if(Files.exists(target))throw new IllegalStateException("Output exists");
        byte[] bytes;
        try(ZipFile apk=new ZipFile(args[0])){
            ZipEntry entry=apk.getEntry(args[1]);if(entry==null||entry.getSize()<1||entry.getSize()>16*1024*1024)throw new IllegalStateException("Partition size");
            try(InputStream input=apk.getInputStream(entry)){bytes=input.readNBytes(16*1024*1024+1);}
        }
        String sha=java.util.HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        if(!sha.equals(args[2]))throw new IllegalStateException("Unexpected partition hash: "+sha);
        // The constructor retains the APK only for its container; decodeFile
        // receives the verified in-memory partition and reads no other assets.
        SmaliDecoder decoder=new SmaliDecoder(new File(args[0]),true);
        decoder.decodeFile(new DexBackedDexFile(bytes,0),target.toFile());
        System.out.println("Decoded "+args[1]+" SHA256 "+sha);
    }
}
