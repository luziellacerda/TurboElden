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

/** R141 scoped HTTP overlay. Every foreign type and the donor ResponseBody retain exact canonical bytes. */
public final class ScopedHttpDex {
    private static final String PIN = "6c9c2d6df00919ca4c927c3719b932ebfb1ef46b24f2de778120a84fd8d30225";
    private static final String PREFIX = "Lorg/emulationstation/frontend/station/";
    private static final String BODY = PREFIX + "StationHttp$ResponseBody;";
    private static final String ORIGIN = PREFIX + "StationDownloadOrigin;";
    private static final Set<String> ORIGINAL = Set.of(PREFIX + "StationHttp;", PREFIX + "StationHttp$1;", BODY,
        PREFIX + "StationHttp$$ExternalSyntheticLambda0;", PREFIX + "StationHttp$$ExternalSyntheticLambda1;",
        PREFIX + "StationHttp$$ExternalSyntheticLambda2;");
    private static final Set<String> MODIFIED = new TreeSet<>(ORIGINAL);
    private static final Set<String> FINAL = new TreeSet<>(ORIGINAL);
    static { MODIFIED.remove(BODY); FINAL.add(ORIGIN); }
    private static String sha(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }
    private static Map<String,ClassDef> classes(byte[] bytes) {
        if (bytes.length < 112 || !new String(bytes, 0, 4, StandardCharsets.US_ASCII).equals("dex\n"))
            throw new IllegalStateException("Standard DEX required");
        ByteBuffer map = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        int start = map.getInt(52), entries = map.getInt(start);
        for (int i = 0; i < entries; i++)
            if ((map.getShort(start + 4 + i * 12) & 0xffff) == 0xf000)
                throw new IllegalStateException("Hidden API metadata");
        DexBackedDexFile dex = new DexBackedDexFile(null, bytes);
        Map<String,ClassDef> result = new TreeMap<>();
        for (ClassDef definition : dex.getClasses())
            if (result.put(definition.getType(), definition) != null) throw new IllegalStateException("Duplicate class");
        return result;
    }
    private static byte[] representation(ClassDef definition) throws Exception {
        BaksmaliOptions options = new BaksmaliOptions();
        options.localsDirective = true; options.sequentialLabels = true; options.debugInfo = true;
        StringWriter text = new StringWriter();
        new ClassDefinition(options, definition).writeTo(new BaksmaliWriter(text));
        return text.toString().getBytes(StandardCharsets.UTF_8);
    }
    private static Map<String,String> hashes(Map<String,ClassDef> classes) throws Exception {
        Map<String,String> result = new TreeMap<>();
        for (var row : classes.entrySet()) result.put(row.getKey(), sha(representation(row.getValue())));
        return result;
    }
    private static String quote(String value) {
        if (value.indexOf('"') >= 0 || value.indexOf('\\') >= 0 || value.indexOf('\n') >= 0)
            throw new IllegalStateException("Unexpected descriptor text");
        return "\"" + value + "\"";
    }
    private static String array(Collection<String> values) {
        return "[" + String.join(",", values.stream().sorted().map(ScopedHttpDex::quote).toList()) + "]";
    }
    private static String object(Map<String,String> values) {
        List<String> rows = new ArrayList<>();
        for (var row : values.entrySet()) rows.add(quote(row.getKey()) + ":" + quote(row.getValue()));
        return "{" + String.join(",", rows) + "}";
    }
    public static void main(String[] args) throws Exception {
        if (args.length != 4) throw new IllegalArgumentException("DONOR_DEX CLOSED_OVERLAY_DEX OUTPUT_DEX FRESH_RECEIPT");
        Path donor = Path.of(args[0]), overlay = Path.of(args[1]), output = Path.of(args[2]), receipt = Path.of(args[3]);
        if (Files.exists(output) || Files.exists(receipt)) throw new IllegalStateException("Fresh outputs required");
        byte[] original = Files.readAllBytes(donor);
        if (!sha(original).equals(PIN)) throw new IllegalStateException("Exact R140 DEX28 required");
        Map<String,ClassDef> before = classes(original), replacement = classes(Files.readAllBytes(overlay));
        Set<String> donorFamily = new TreeSet<>();
        for (String type : before.keySet())
            if (type.equals(PREFIX + "StationHttp;") || type.startsWith(PREFIX + "StationHttp$")) donorFamily.add(type);
        if (before.size() != 271 || !donorFamily.equals(ORIGINAL) || before.containsKey(ORIGIN))
            throw new IllegalStateException("Exact six-type donor HTTP family required");
        if (!replacement.keySet().equals(FINAL))
            throw new IllegalStateException("Exactly the six HTTP types and one origin helper required");
        Map<String,ClassDef> selected = new TreeMap<>(before);
        selected.keySet().removeAll(MODIFIED);
        replacement.put(BODY, before.get(BODY));
        selected.putAll(replacement);
        if (selected.size() != 272) throw new IllegalStateException("Final class count differs");
        DexPool pool = new DexPool(Opcodes.forApi(28));
        for (ClassDef definition : selected.values()) pool.internClass(definition);
        FileDataStore store = new FileDataStore(output.toFile());
        try { pool.writeTo(store); } finally { store.close(); }
        Map<String,ClassDef> after = classes(Files.readAllBytes(output));
        if (!after.keySet().equals(selected.keySet())) throw new IllegalStateException("Unexpected class delta");
        Map<String,String> oldHashes = hashes(before), newHashes = hashes(after), retained = new TreeMap<>();
        for (String type : before.keySet()) {
            if (MODIFIED.contains(type)) continue;
            if (!Arrays.equals(representation(before.get(type)), representation(after.get(type))))
                throw new IllegalStateException("Unrelated class changed: " + type);
            retained.put(type, oldHashes.get(type));
        }
        if (retained.size() != 266 || !retained.containsKey(BODY)) throw new IllegalStateException("Retained count differs");
        Set<String> allowed = new TreeSet<>(MODIFIED); allowed.add(ORIGIN);
        List<String> changed = new ArrayList<>();
        for (String type : MODIFIED) if (!oldHashes.get(type).equals(newHashes.get(type))) changed.add(type);
        String proof = "{\"partition\":\"classes28.dex\",\"donorSha256\":\"" + PIN +
            "\",\"outputSha256\":\"" + sha(Files.readAllBytes(output)) +
            "\",\"originalClassCount\":271,\"finalClassCount\":272,\"unchangedClasses\":266," +
            "\"unrelatedClassesByteIdentical\":true,\"responseBodyPreserved\":true,\"testsPackaged\":false," +
            "\"classProjectionFormat\":\"apktool-3.0.3-baksmali-locals-sequential-labels-debug-info\"," +
            "\"originalAllowedTypes\":" + array(MODIFIED) + ",\"finalAllowedTypes\":" + array(allowed) +
            ",\"addedTypes\":" + array(List.of(ORIGIN)) + ",\"removedTypes\":[],\"modifiedTypes\":" + array(changed) +
            ",\"baselineClassSha256\":" + object(oldHashes) + ",\"outputClassSha256\":" + object(newHashes) +
            ",\"unchangedClassSha256\":" + object(retained) + "}\n";
        Files.writeString(receipt, proof, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        System.out.println("partition=classes28.dex retainedClasses=266 outputClasses=272 responseBodyPreserved=true");
    }
}
