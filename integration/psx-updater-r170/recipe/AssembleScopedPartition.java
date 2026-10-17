import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.ZipFile;
import brut.androlib.smali.SmaliBuilder;
import com.android.tools.smali.dexlib2.Opcodes;
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

/** Assemble one pinned partition without trimming unrelated explicit default initializers.
 *
 * Apktool 3.0.3's DexBuilder removes trailing null/false/zero entries from its
 * encoded static-value array. Reinsert only that array for unchanged classes;
 * fields, methods, annotations and every actual value retain the parsed objects.
 * VerifyScopedPartition must still byte-compare all other classes after writing.
 */
public final class AssembleScopedPartition {
    private static final int MAX_DEX_BYTES = 16 * 1024 * 1024;

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
        if (args.length != 6) throw new IllegalArgumentException("DONOR PARTITION SHA SMALI_DIR OUTPUT_DEX SCOPE_PROPERTIES");
        VerifyScopedPartition.Scope scope=VerifyScopedPartition.readScope(args[1],args[2],Path.of(args[5]));
        DexBackedDexFile donor=new DexBackedDexFile(VerifyScopedPartition.readDonor(args[0],args[1],args[2]),0);
        if (donor.hiddenApiRestrictionsOffset != 0) throw new IllegalStateException("HiddenAPI DEX");
        Path root=Path.of(args[3]),output=Path.of(args[4]);
        if (Files.exists(output)) throw new IllegalStateException("Destination exists");
        VerifyScopedPartition.main(new String[]{args[0],args[1],args[2],args[3],args[5]});
        Set<String> donorTypes=new TreeSet<>();
        for(int i=0;i<donor.classCount;i++) {
            ClassDef def=new DexBackedClassDef(donor,donor.classStartOffset+i*32,0);
            donorTypes.add(def.getType());
        }
        Set<String> expectedTypes=scope.finalTypes(donorTypes);
        List<Path> paths=new ArrayList<>();
        try(var files=Files.walk(root)) {
            files.filter(path->path.toString().endsWith(".smali")).forEach(paths::add);
        }
        paths.sort(Comparator.comparing(path->root.relativize(path).toString()));
        if(paths.size()!=expectedTypes.size()) throw new IllegalStateException("Explicit partition class count");
        SmaliBuilder assembler=new SmaliBuilder(28);
        DexBuilder dex=new DexBuilder(new Opcodes(28));
        for(Path path:paths)
            if(!assembler.buildFile(path.toFile(),dex)) throw new IllegalStateException("Invalid smali: "+root.relativize(path));
        if(!expectedTypes.equals(dex.classSection.internedItems.keySet())) throw new IllegalStateException("Assembled class delta");
        int restored=0;
        for(int i=0;i<donor.classCount;i++) {
            ClassDef original=new DexBackedClassDef(donor,donor.classStartOffset+i*32,0);
            if(scope.originalAllowed.contains(original.getType())) continue;
            BuilderClassDef parsed=(BuilderClassDef)dex.classSection.internedItems.get(original.getType());
            if(parsed==null) throw new IllegalStateException("Unrelated donor class omitted");
            if(restore(dex,original,parsed)) restored++;
        }
        dex.classSection.sortedClasses=null;
        FileDataStore store=new FileDataStore(output.toFile());
        try{dex.writeTo(store);}finally{store.raf.close();}
        System.out.println("assembledClasses="+expectedTypes.size()+" restoredInitializerArrays="+restored+
                " originalAllowed="+scope.originalAllowed.size()+" finalAllowed="+scope.finalAllowed.size()+" donorSHA="+args[2]);
    }
}
