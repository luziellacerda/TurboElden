import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.dexlib2.iface.Method;
import com.android.tools.smali.dexlib2.iface.MethodImplementation;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.ReferenceInstruction;
import com.android.tools.smali.dexlib2.iface.reference.MethodReference;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.Set;
import java.util.Objects;
import java.util.zip.ZipFile;

/** Reads the actual assembled DEX; no Android or gameplay is simulated. */
public final class DolphinDexHookProbe {
    private static int checks;
    private static void check(boolean value, String label) {
        if (!value) throw new AssertionError(label);
        checks++;
    }
    private static String key(MethodReference method) {
        StringBuilder result = new StringBuilder(method.getDefiningClass())
                .append("->").append(method.getName()).append('(');
        for (Object type : method.getParameterTypes()) result.append(type);
        return result.append(')').append(method.getReturnType()).toString();
    }
    private static ArrayList<Method> methods(ClassDef type) {
        ArrayList<Method> result = new ArrayList<>();
        for (Object method : type.getDirectMethods()) result.add((Method) method);
        for (Object method : type.getVirtualMethods()) result.add((Method) method);
        return result;
    }
    private static DexBackedDexFile read(String path) throws Exception {
        return new DexBackedDexFile(Files.readAllBytes(Path.of(path)), 0);
    }
    private static Map<String,ClassDef> types(DexBackedDexFile file) {
        Map<String,ClassDef> result = new TreeMap<>();
        for (int i=0;i<file.classSection.size();i++) {
            ClassDef type=(ClassDef)file.classSection.get(i); result.put(type.getType(),type);
        }
        return result;
    }
    private static Set<String> signatures(ClassDef type) {
        Set<String> result=new TreeSet<>();
        for(Method method:methods(type)) result.add(key(method)+" "+method.getAccessFlags());
        return result;
    }
    public static void main(String[] args) throws Exception {
        if (args.length != 4) throw new IllegalArgumentException("DEX10 DEX12 DEX35 baseAPK");
        Map<String,Method> exported = new HashMap<>();
        DexBackedDexFile java = read(args[2]);
        for (int i=0;i<java.classSection.size();i++) {
            ClassDef type = (ClassDef) java.classSection.get(i);
            for (Method method : methods(type)) exported.put(key(method), method);
        }
        Map<String,Integer> calls = new TreeMap<>();
        int partitions[] = {4991, 5};
        try(ZipFile apk=new ZipFile(args[3])) { for (int p=0;p<2;p++) {
            DexBackedDexFile donor = read(args[p]);
            check(donor.classSection.size()==partitions[p], "complete donor class count");
            String partition="classes"+(p==0?10:12)+".dex";
            DexBackedDexFile original=new DexBackedDexFile(apk.getInputStream(apk.getEntry(partition)).readAllBytes(),0);
            Map<String,ClassDef> before=types(original),after=types(donor);
            check(before.keySet().equals(after.keySet()),"identical donor namespace/class set");
            for(String name:before.keySet()) {
                ClassDef old=before.get(name),now=after.get(name);
                check(old.getAccessFlags()==now.getAccessFlags(),"original class flags retained");
                check(Objects.equals(old.getSuperclass(),now.getSuperclass())&&old.getInterfaces().equals(now.getInterfaces()),"original inheritance retained");
                Set<String> expected=signatures(old);
                if(name.equals("Lorg/dolphinemu/dolphinemu/activities/EmulationActivity;")) expected.add(name+"->onPause()V 4");
                check(expected.equals(signatures(now)),"all original method signatures retained");
            }
            for (int i=0;i<donor.classSection.size();i++) {
                ClassDef type = (ClassDef) donor.classSection.get(i);
                for (Method method : methods(type)) {
                    MethodImplementation implementation = method.getImplementation();
                    if (implementation==null) continue;
                    for (Object raw : implementation.getInstructions()) {
                        Instruction instruction = (Instruction) raw;
                        if (!(instruction instanceof ReferenceInstruction)) continue;
                        Object reference = ((ReferenceInstruction) instruction).getReference();
                        if (!(reference instanceof MethodReference)) continue;
                        MethodReference target = (MethodReference) reference;
                        if (!target.getDefiningClass().equals("Lorg/emulationstation/frontend/netplay/StationDolphinSession;")
                            && !target.getDefiningClass().equals("Lorg/emulationstation/frontend/netplay/StationDolphinSelector;")) continue;
                        check(instruction.getOpcode().name.startsWith("invoke-static"), "hook static opcode");
                        String call = key(target);
                        Method exportedMethod = exported.get(call);
                        check(exportedMethod!=null, "actual DEX35 has exact hook descriptor: "+call);
                        check((exportedMethod.getAccessFlags() & 9)==9, "hook public static: "+call);
                        calls.put(call, calls.getOrDefault(call,0)+1);
                    }
                }
            }
        } }
        check(calls.size()==16, "sixteen distinct hooks");
        check(calls.values().stream().mapToInt(Integer::intValue).sum()==20, "twenty actual hook call sites");
        System.out.println("{\"checks\":"+checks+",\"distinctHookDescriptors\":"+calls.size()+",\"callSites\":20,\"physicalGameplayValidated\":false}");
        for (Map.Entry<String,Integer> call : calls.entrySet()) System.out.println(call.getValue()+" "+call.getKey());
    }
}
