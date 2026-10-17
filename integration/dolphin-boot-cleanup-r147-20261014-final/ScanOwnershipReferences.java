import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedClassDef;
import com.android.tools.smali.dexlib2.iface.instruction.ReferenceInstruction;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.Method;
import com.android.tools.smali.dexlib2.iface.reference.FieldReference;

/** Read all real DEX10 field instructions; no assembly or APK mutation. */
public final class ScanOwnershipReferences {
    public static void main(String[] args)throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("Pinned R145 APK only");
        byte[] raw;
        try (ZipFile apk = new ZipFile(args[0])) {
            try (var stream = apk.getInputStream(apk.getEntry("classes10.dex"))) { raw = stream.readAllBytes(); }
        }
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(raw));
        if (!sha.equals("09ed47c40c4a6f5194bcb9ace23f85392b99c19c84cd654e61716de37b32e01c"))
            throw new IllegalStateException("Exact donor DEX10 required");
        DexBackedDexFile dex = new DexBackedDexFile(raw, 0);
        int classes = 0, references = 0;
        for (int index = 0; index < dex.classCount; index++) {
            var type = new DexBackedClassDef(dex, dex.classStartOffset + index * 32, 0);
            classes++;
            List<Method> methods = new ArrayList<>();
            for (Object method : type.getDirectMethods()) methods.add((Method) method);
            for (Object method : type.getVirtualMethods()) methods.add((Method) method);
            for (var method : methods) {
                if (method.getImplementation() == null) continue;
                for (Object value : method.getImplementation().getInstructions()) {
                    Instruction instruction = (Instruction) value;
                    if (instruction instanceof ReferenceInstruction ref && ref.getReference() instanceof FieldReference field &&
                        field.getDefiningClass().equals("Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;") &&
                        Set.of("bootSessionDataPointer", "isClosed").contains(field.getName())) {
                        references++;
                        System.out.println(type.getType() + "\t" + method.getName() + method.getParameterTypes() + method.getReturnType() +
                                "\t" + instruction.getOpcode() + "\t" + field.getName());
                    }
                }
            }
        }
        System.out.println("scannedClasses=" + classes + " references=" + references + " dexSHA=" + sha);
    }
}
