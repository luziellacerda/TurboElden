import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import com.android.tools.smali.dexlib2.Opcodes;
import brut.androlib.smali.SmaliBuilder;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.dexlib2.iface.Field;
import com.android.tools.smali.dexlib2.iface.value.ArrayEncodedValue;
import com.android.tools.smali.dexlib2.iface.value.EncodedValue;
import com.android.tools.smali.dexlib2.immutable.value.ImmutableArrayEncodedValue;
import com.android.tools.smali.dexlib2.immutable.value.ImmutableEncodedValueFactory;
import com.android.tools.smali.dexlib2.util.EncodedValueUtils;
import com.android.tools.smali.dexlib2.writer.builder.*;
import com.android.tools.smali.dexlib2.writer.io.FileDataStore;
import com.android.tools.smali.util.ArraySortedSet;
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
        DexBackedDexFile dex = new DexBackedDexFile(bytes, 0);
        if (dex.hiddenApiRestrictionsOffset != 0) throw new IllegalStateException("Hidden API metadata");
        Map<String,ClassDef> result = new TreeMap<>();
        for (int i = 0; i < dex.classCount; i++) {
            ClassDef definition = new DexBackedClassDef(dex, dex.classStartOffset + i * 32, 0);
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
    // Verbatim restoration methods from the frozen R140 assembler.
    private static Object value(EncodedValue value) {
        return value == null ? null : ImmutableEncodedValueFactory.of(value);
    }

    private static boolean sameInitialValue(EncodedValue left, EncodedValue right) {
        if (Objects.equals(value(left), value(right))) return true;
        // A default before a later non-default entry is encoded in the donor
        // array but omitted from that field's smali directive. No value changes.
        return left == null ? right != null && EncodedValueUtils.isDefaultValue(right) :
                right == null && EncodedValueUtils.isDefaultValue(left);
    }

    private static List<Object> values(ArrayEncodedValue array) {
        List<Object> result = new ArrayList<>();
        if (array != null) for (Object value : array.getValue())
            result.add(value((EncodedValue) value));
        return result;
    }

    @SuppressWarnings("unchecked")
    private static <T> T interned(T value, Object existing) {
        return existing == null ? value : (T) existing;
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    private static boolean restore(DexBuilder dex, ClassDef original, BuilderClassDef parsed) {
        List<Field> before = new ArrayList<>();
        for (Object field : original.getStaticFields()) before.add((Field) field);
        List<Field> after = new ArrayList<>();
        for (Object field : parsed.staticFields) after.add((Field) field);
        if (before.size() != after.size()) throw new IllegalStateException("Static field set changed: " + original.getType());
        List<Object> exact = new ArrayList<>();
        boolean absent = false;
        for (int i = 0; i < before.size(); i++) {
            Field left = before.get(i), right = after.get(i);
            if (!left.getDefiningClass().equals(right.getDefiningClass()) ||
                    !left.getName().equals(right.getName()) || !left.getType().equals(right.getType()) ||
                    left.getAccessFlags() != right.getAccessFlags() ||
                    !sameInitialValue(left.getInitialValue(), right.getInitialValue()) ||
                    !left.getAnnotations().equals(right.getAnnotations()) ||
                    !left.getHiddenApiRestrictions().equals(right.getHiddenApiRestrictions()))
                throw new IllegalStateException("Static field changed: " + original.getType() + "->" + left.getName());
            if (left.getInitialValue() == null) absent = true;
            else {
                if (absent) throw new IllegalStateException("Non-contiguous donor static values");
                exact.add(value(left.getInitialValue()));
            }
        }
        List<Object> optimized = values(parsed.staticInitializers);
        if (exact.equals(optimized)) return false;
        if (optimized.size() >= exact.size() ||
                !exact.subList(0, optimized.size()).equals(optimized))
            throw new IllegalStateException("Unexpected initializer rewrite: " + original.getType());
        for (int i = optimized.size(); i < exact.size(); i++)
            if (!EncodedValueUtils.isDefaultValue((EncodedValue) exact.get(i)))
                throw new IllegalStateException("Non-default initializer trimmed: " + original.getType());

        var restored = dex.internArrayEncodedValue(new ImmutableArrayEncodedValue(exact));
        Object existing = dex.encodedArraySection.internedItems.putIfAbsent(restored, restored);
        restored = interned(restored, existing);
        ArrayList methods = new ArrayList();
        for (Object method : parsed.directMethods) methods.add(method);
        for (Object method : parsed.virtualMethods) methods.add(method);
        BuilderClassDef replacement = new BuilderClassDef(parsed.type, parsed.accessFlags,
                parsed.superclass, parsed.interfaces, parsed.sourceFile, parsed.annotations,
                ArraySortedSet.copyOf(new ArrayList(parsed.staticFields)),
                ArraySortedSet.copyOf(new ArrayList(parsed.instanceFields)), methods, restored);
        if (!dex.classSection.internedItems.replace(original.getType(), parsed, replacement))
            throw new IllegalStateException("Class replacement lost its exact owner");
        return true;
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
        // The pinned Windows APKtool exposes SmaliBuilder/DexBuilder rather than DexPool.
        // Decode only this selected partition into a fresh private directory, preserving debug.
        Path smali = output.getParent().resolve("selected-smali");
        Files.createDirectory(smali);
        SmaliBuilder assembler = new SmaliBuilder(28);
        DexBuilder dex = new DexBuilder(new Opcodes(28));
        for (var row : selected.entrySet()) {
            Path path = smali.resolve(row.getKey().substring(1, row.getKey().length() - 1) + ".smali");
            Files.createDirectories(path.getParent());
            Files.write(path, representation(row.getValue()), StandardOpenOption.CREATE_NEW);
            if (!assembler.buildFile(path.toFile(), dex)) throw new IllegalStateException("Invalid selected smali: " + row.getKey());
        }
        if (!dex.classSection.internedItems.keySet().equals(selected.keySet()))
            throw new IllegalStateException("Assembled closed class set differs");
        int restored = 0;
        for (var row : before.entrySet()) {
            if (MODIFIED.contains(row.getKey())) continue;
            BuilderClassDef parsed = (BuilderClassDef)dex.classSection.internedItems.get(row.getKey());
            if (parsed == null) throw new IllegalStateException("Unrelated donor class omitted");
            if (restore(dex, row.getValue(), parsed)) restored++;
        }
        dex.classSection.sortedClasses = null;
        FileDataStore store = new FileDataStore(output.toFile());
        try { dex.writeTo(store); } finally { store.raf.close(); }
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
            "\"staticInitializersPreserved\":true,\"restoredInitializerArrays\":" + restored + "," +
            "\"classProjectionFormat\":\"apktool-3.0.3-baksmali-locals-sequential-labels-debug-info\"," +
            "\"originalAllowedTypes\":" + array(MODIFIED) + ",\"finalAllowedTypes\":" + array(allowed) +
            ",\"addedTypes\":" + array(List.of(ORIGIN)) + ",\"removedTypes\":[],\"modifiedTypes\":" + array(changed) +
            ",\"baselineClassSha256\":" + object(oldHashes) + ",\"outputClassSha256\":" + object(newHashes) +
            ",\"unchangedClassSha256\":" + object(retained) + "}\n";
        Files.writeString(receipt, proof, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        System.out.println("partition=classes28.dex retainedClasses=266 outputClasses=272 responseBodyPreserved=true");
    }
}
