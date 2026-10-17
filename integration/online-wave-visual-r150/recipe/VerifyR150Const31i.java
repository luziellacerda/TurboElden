import java.security.MessageDigest;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.Map;
import java.util.Set;

import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedMethod;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.dexlib2.iface.Method;
import com.android.tools.smali.dexlib2.iface.MethodImplementation;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction31i;

/**
 * Independently walk decoded DEX instructions at their real boundaries.
 * Reads one SHA-pinned DEX from stdin and prints only targeted methods and
 * actual const/31i instructions. No APK or class output is written.
 */
public final class VerifyR150Const31i {
    private static void need(boolean ok, String message) {
        if (!ok) throw new IllegalStateException(message);
    }

    private static int u32(byte[] data, int offset) {
        need(offset >= 0 && offset <= data.length - 4, "DEX u32 out of bounds");
        return (data[offset] & 255) | ((data[offset + 1] & 255) << 8) |
               ((data[offset + 2] & 255) << 16) | ((data[offset + 3] & 255) << 24);
    }

    private static String descriptor(Method method) {
        StringBuilder value = new StringBuilder(method.getName()).append('(');
        for (Object parameter : method.getParameterTypes()) value.append(parameter);
        return value.append(')').append(method.getReturnType()).toString();
    }

    private static void inspect(byte[] bytes, String identity, Method method) {
        need(method instanceof DexBackedMethod, "Method is not DEX backed: " + identity);
        DexBackedMethod direct = (DexBackedMethod) method;
        MethodImplementation implementation = method.getImplementation();
        need(implementation != null && direct.codeOffset > 0,
             "Target has no code item: " + identity);
        int codeOffset = direct.codeOffset;
        int end = codeOffset + 16 + 2 * u32(bytes, codeOffset + 12);
        need(end >= codeOffset + 16 && end <= bytes.length,
             "Code item outside DEX: " + identity);
        System.out.println("M\t" + identity + "\t" + codeOffset);
        int cursor = codeOffset + 16;
        for (Object instructionObject : implementation.getInstructions()) {
            Instruction instruction = (Instruction) instructionObject;
            int units = instruction.getCodeUnits();
            need(units > 0 && cursor + units * 2 <= end,
                 "Decoded instruction boundary outside code item: " + identity);
            if (instruction instanceof Instruction31i &&
                "const".equals(instruction.getOpcode().name)) {
                Instruction31i constant = (Instruction31i) instruction;
                need(units == 3 && cursor + 6 <= end &&
                     (bytes[cursor] & 255) == 0x14 &&
                     (bytes[cursor + 1] & 255) == constant.getRegisterA() &&
                     u32(bytes, cursor + 2) == constant.getNarrowLiteral(),
                     "Dexlib2 const/31i disagrees with raw bytes: " + identity);
                System.out.println("I\t" + identity + "\t" + cursor + "\t" +
                                   constant.getRegisterA() + "\t" +
                                   Integer.toUnsignedString(constant.getNarrowLiteral()));
            }
            cursor += units * 2;
        }
        need(cursor == end, "Dexlib2 did not consume the full code item: " + identity);
    }

    public static void main(String[] args) throws Exception {
        need(args.length >= 2 && args[0].matches("[0-9a-f]{64}"),
             "Expected DEX SHA-256 and target method identities");
        Set<String> targets = new HashSet<>();
        for (int index = 1; index < args.length; index++) {
            need(args[index].matches("L[^|]+;\\|[A-Za-z_$][A-Za-z0-9_$]*\\(.*\\).+") &&
                 targets.add(args[index]), "Invalid or duplicate target identity");
        }
        byte[] bytes = System.in.readAllBytes();
        need(bytes.length > 0 && bytes.length < 16 * 1024 * 1024 &&
             HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)).equals(args[0]),
             "Pinned DEX identity failed");
        DexBackedDexFile dex = new DexBackedDexFile(bytes, 0);
        Map<String, Integer> found = new HashMap<>();
        for (int index = 0; index < dex.classCount; index++) {
            ClassDef owner = (ClassDef) dex.classSection.get(index);
            for (Object methodObject : owner.getDirectMethods()) {
                Method method = (Method) methodObject;
                String identity = owner.getType() + "|" + descriptor(method);
                if (targets.contains(identity)) {
                    found.merge(identity, 1, Integer::sum);
                    inspect(bytes, identity, method);
                }
            }
            for (Object methodObject : owner.getVirtualMethods()) {
                Method method = (Method) methodObject;
                String identity = owner.getType() + "|" + descriptor(method);
                if (targets.contains(identity)) {
                    found.merge(identity, 1, Integer::sum);
                    inspect(bytes, identity, method);
                }
            }
        }
        need(found.keySet().equals(targets) && found.values().stream().allMatch(value -> value == 1),
             "Every target method must appear exactly once");
        System.out.println("DONE\t" + targets.size());
    }
}
