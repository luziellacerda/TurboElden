import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.ZipFile;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.baksmali.Adaptors.ClassDefinition;
import com.android.tools.smali.baksmali.BaksmaliOptions;
import com.android.tools.smali.baksmali.formatter.BaksmaliWriter;

/** Byte-check every unchanged class and the complete class set of one pinned DEX. */
public final class VerifyScopedPartition {
    public static void main(String[] args) throws Exception {
        if (args.length < 5) throw new IllegalArgumentException("Exact allowed types required");
        Set<String> allowed = new HashSet<>();
        for (int i = 4; i < args.length; i++) {
            if (!args[i].matches("Lorg/emulationstation/frontend/[A-Za-z0-9_/$]+;") || !allowed.add(args[i]))
                throw new IllegalArgumentException("Invalid or duplicated allowed type");
        }
        byte[] bytes;
        try (ZipFile apk = new ZipFile(args[0]); var in = apk.getInputStream(apk.getEntry(args[1]))) {
            bytes = in.readNBytes(16 * 1024 * 1024);
        }
        String checksum = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        if (!checksum.equals(args[2])) throw new IllegalStateException("DEX identity");
        DexBackedDexFile dex = new DexBackedDexFile(bytes, 0);
        if (dex.hiddenApiRestrictionsOffset != 0) throw new IllegalStateException("HiddenAPI DEX");
        Set<String> seenAllowed = new HashSet<>();
        int unchanged = 0;
        for (int i = 0; i < dex.classCount; i++) {
            ClassDef def = new DexBackedClassDef(dex, dex.classStartOffset + i * 32, 0);
            if (allowed.contains(def.getType())) { seenAllowed.add(def.getType()); continue; }
            var options = new BaksmaliOptions();
            options.localsDirective = true; options.sequentialLabels = true; options.debugInfo = true;
            StringWriter text = new StringWriter();
            new ClassDefinition(options, def).writeTo(new BaksmaliWriter(text));
            Path decoded = Path.of(args[3]).resolve(def.getType().substring(1, def.getType().length()-1) + ".smali");
            if (!Arrays.equals(text.toString().getBytes(StandardCharsets.UTF_8), Files.readAllBytes(decoded)))
                throw new IllegalStateException("Unrelated class changed: " + def.getType());
            unchanged++;
        }
        long count;
        try (var files = Files.walk(Path.of(args[3]))) {
            count = files.filter(path -> path.toString().endsWith(".smali")).count();
        }
        if (count != dex.classCount || !seenAllowed.equals(allowed)) throw new IllegalStateException("Class set changed");
        System.out.println("verifiedClasses=" + dex.classCount + " unchanged=" + unchanged + " changed=" + allowed.size() + " donorSHA=" + checksum);
    }
}
