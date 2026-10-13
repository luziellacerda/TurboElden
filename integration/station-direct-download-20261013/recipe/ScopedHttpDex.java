import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.dexlib2.writer.pool.DexPool;
import com.android.tools.smali.dexlib2.writer.io.FileDataStore;
import com.android.tools.smali.baksmali.Adaptors.ClassDefinition;
import com.android.tools.smali.baksmali.BaksmaliOptions;
import com.android.tools.smali.baksmali.formatter.BaksmaliWriter;

/** Replace the HTTP family only and verify every other class's canonical smali byte for byte. */
public final class ScopedHttpDex {
    private static final String PIN = "6c9c2d6df00919ca4c927c3719b932ebfb1ef46b24f2de778120a84fd8d30225";
    private static final String PREFIX = "Lorg/emulationstation/frontend/station/";
    private static final String BODY = PREFIX + "StationHttp$ResponseBody;";
    private static boolean http(String type) {
        return type.equals(PREFIX + "StationHttp;") || type.startsWith(PREFIX + "StationHttp$");
    }
    private static boolean changed(String type) { return http(type) && !type.equals(BODY); }
    private static String sha(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }
    private static Map<String,ClassDef> classes(byte[] bytes) {
        ByteBuffer map = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        int start = map.getInt(52), entries = map.getInt(start);
        for (int i = 0; i < entries; i++)
            if ((map.getShort(start + 4 + i * 12) & 0xffff) == 0xf000)
                throw new IllegalStateException("Hidden API metadata");
        DexBackedDexFile dex = new DexBackedDexFile(null, bytes);
        Map<String,ClassDef> result = new TreeMap<>();
        for (ClassDef definition : dex.getClasses()) {
            if (result.put(definition.getType(), definition) != null) throw new IllegalStateException("Duplicate class");
        }
        return result;
    }
    private static byte[] representation(ClassDef definition) throws Exception {
        BaksmaliOptions options = new BaksmaliOptions();
        options.localsDirective = true; options.sequentialLabels = true; options.debugInfo = true;
        StringWriter text = new StringWriter();
        new ClassDefinition(options, definition).writeTo(new BaksmaliWriter(text));
        return text.toString().getBytes(StandardCharsets.UTF_8);
    }
    public static void main(String[] args) throws Exception {
        if (args.length != 4) throw new IllegalArgumentException("DONOR_DEX CLOSED_OVERLAY_DEX OUTPUT_DEX RECEIPT");
        Path donor = Path.of(args[0]), overlay = Path.of(args[1]), output = Path.of(args[2]);
        if (Files.exists(output)) throw new IllegalStateException("Fresh output required");
        byte[] original = Files.readAllBytes(donor);
        if (!sha(original).equals(PIN)) throw new IllegalStateException("Exact R139 DEX28 required");
        Map<String,ClassDef> before = classes(original), replacement = classes(Files.readAllBytes(overlay));
        if (before.size() != 271 || before.keySet().stream().filter(ScopedHttpDex::http).count() != 6)
            throw new IllegalStateException("Original HTTP family differs");
        if (!replacement.containsKey(PREFIX + "StationHttp;") ||
                !replacement.containsKey(PREFIX + "StationHttp$1;") ||
                !replacement.containsKey(PREFIX + "StationHttp$ResponseBody;") ||
                !replacement.containsKey(PREFIX + "StationDownloadOrigin;") ||
                replacement.keySet().stream().anyMatch(type -> !http(type) && !type.equals(PREFIX + "StationDownloadOrigin;")))
            throw new IllegalStateException("Only the closed HTTP family and download identity may be packaged");
        Map<String,ClassDef> selected = new TreeMap<>(before);
        selected.keySet().removeIf(ScopedHttpDex::changed);
        replacement.put(BODY, before.get(BODY));
        selected.putAll(replacement);
        DexPool pool = new DexPool(Opcodes.forApi(28));
        for (ClassDef definition : selected.values()) pool.internClass(definition);
        FileDataStore store = new FileDataStore(output.toFile());
        try { pool.writeTo(store); } finally { store.close(); }
        Map<String,ClassDef> after = classes(Files.readAllBytes(output));
        if (!after.keySet().equals(selected.keySet())) throw new IllegalStateException("Unexpected class delta");
        int unchanged = 0;
        Map<String,String> retained = new TreeMap<>();
        for (String type : before.keySet()) {
            if (changed(type)) continue;
            byte[] text = representation(before.get(type));
            if (!Arrays.equals(text, representation(after.get(type))))
                throw new IllegalStateException("Unrelated class changed: " + type);
            unchanged++; retained.put(type, sha(text));
        }
        List<String> lines = new ArrayList<>();
        lines.add("{\"partition\":\"classes28.dex\",\"donorSha256\":\"" + PIN + "\",\"outputSha256\":\"" +
                  sha(Files.readAllBytes(output)) + "\",\"unchangedClasses\":" + unchanged +
                  ",\"originalClasses\":" + before.size() + ",\"outputClasses\":" + after.size() +
                  ",\"testsPackaged\":false,\"retainedClassSha256\":{");
        for (Map.Entry<String,String> row : retained.entrySet())
            lines.add("\"" + row.getKey() + "\":\"" + row.getValue() + "\",");
        lines.set(lines.size()-1, lines.get(lines.size()-1).replace(",", ""));
        lines.add("}}");
        Files.write(Path.of(args[3]), lines, StandardCharsets.UTF_8);
        System.out.println("partition=classes28.dex retainedClasses=" + unchanged + " outputClasses=" + after.size());
    }
}
