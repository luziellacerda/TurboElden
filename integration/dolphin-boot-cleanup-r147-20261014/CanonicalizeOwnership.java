import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import brut.androlib.smali.SmaliBuilder;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.dexlib2.writer.builder.DexBuilder;
import com.android.tools.smali.baksmali.Adaptors.ClassDefinition;
import com.android.tools.smali.baksmali.BaksmaliOptions;
import com.android.tools.smali.baksmali.formatter.BaksmaliWriter;

/** Parse a single fixed class and emit canonical projection in memory only. */
public final class CanonicalizeOwnership {
    private static String sha(byte[] raw)throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(raw));
    }
    public static void main(String[] args)throws Exception {
        if (args.length != 3) throw new IllegalArgumentException("BASELINE/PROPOSED, pinned smali, new canonical output");
        String checksum = switch(args[0]) {
            case "BASELINE" -> "7dcbc2c67298d18e7ffe5b4839e73ca6967a0318e4628269598bef9a45ec2315";
            case "PROPOSED" -> "00869b191ffc794d32aaad2f787be11c80188395953ebd7f8a5c95bec69dd1de";
            default -> throw new IllegalArgumentException("Unreviewed ownership class");
        };
        if (!sha(Files.readAllBytes(Path.of(args[1]))).equals(checksum)) throw new IllegalStateException("Exact reviewed class required");
        Path output = Path.of(args[2]);
        if (Files.exists(output)) throw new IllegalStateException("Canonical output exists");
        DexBuilder dex = new DexBuilder(new Opcodes(28));
        if (!new SmaliBuilder(28).buildFile(Path.of(args[1]).toFile(), dex)) throw new IllegalStateException("Invalid reviewed class");
        if (!dex.classSection.internedItems.keySet().equals(Set.of("Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;")))
            throw new IllegalStateException("Class expansion refused");
        ClassDef type = (ClassDef) dex.classSection.internedItems.get("Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;");
        BaksmaliOptions options = new BaksmaliOptions();
        options.localsDirective = true; options.sequentialLabels = true; options.debugInfo = true;
        StringWriter text = new StringWriter();
        new ClassDefinition(options, type).writeTo(new BaksmaliWriter(text));
        byte[] projection = text.toString().getBytes(StandardCharsets.UTF_8);
        Files.createDirectories(output.getParent());
        Files.write(output, projection, StandardOpenOption.CREATE_NEW);
        System.out.println("parsedFixedClass=true canonicalSha256=" + sha(projection) + " dexWritten=false");
    }
}
