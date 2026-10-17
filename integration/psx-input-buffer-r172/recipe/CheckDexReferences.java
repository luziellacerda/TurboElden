import java.nio.file.*;
import java.util.*;
import java.util.zip.ZipFile;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.ReferenceInstruction;
import com.android.tools.smali.dexlib2.iface.reference.MethodReference;

/** Check the actual final 40-partition view, including synthetic CAS targets. */
public final class CheckDexReferences {
    static String signature(MethodReference m) {
        return m.getName()+"("+String.join("",m.getParameterTypes())+")"+m.getReturnType();
    }
    static List<Method> methods(ClassDef def) {
        List<Method> result=new ArrayList<>();
        for(Object m:def.getDirectMethods())result.add((Method)m);
        for(Object m:def.getVirtualMethods())result.add((Method)m);
        return result;
    }
    static boolean has(ClassDef def,String signature,Map<String,ClassDef> all,Set<String> seen,boolean exact) {
        if(def==null || !seen.add(def.getType())) return false;
        for(Method m:methods(def)) if(signature(m).equals(signature))return true;
        if(exact)return false;
        if(has(all.get(def.getSuperclass()),signature,all,seen,false))return true;
        for(Object i:def.getInterfaces())if(has(all.get(i),signature,all,seen,false))return true;
        return false;
    }
    static boolean externalParent(ClassDef def,Map<String,ClassDef> all,Set<String> seen) {
        if(def==null || !seen.add(def.getType()))return false;
        String p=def.getSuperclass();
        if(p!=null && !all.containsKey(p) && !p.equals("Ljava/lang/Object;"))return true;
        if(externalParent(all.get(p),all,seen))return true;
        for(Object i:def.getInterfaces())if(!all.containsKey(i)||externalParent(all.get(i),all,seen))return true;
        return false;
    }
    static boolean changed(String t) {
        String n=t.substring(t.lastIndexOf('/')+1).split("\\$",2)[0].replace(";", "");
        return Set.of("StationPsxLaunch","StationPsxPolicy").contains(n);
    }
    public static void main(String[] a)throws Exception {
        if(a.length!=2)throw new IllegalArgumentException("BASE_APK COMPILED_PARTITION_DIRECTORY");
        Map<String,ClassDef> all=new HashMap<>();
        int partitions=0;
        try(ZipFile z=new ZipFile(a[0])) {
            var entries=z.entries();
            while(entries.hasMoreElements()) {
                var e=entries.nextElement();if(!e.getName().matches("classes(?:[0-9]+)?\\.dex"))continue;
                Path candidate=Path.of(a[1],e.getName());byte[] raw;
                if(Files.isRegularFile(candidate))raw=Files.readAllBytes(candidate);
                else try(var in=z.getInputStream(e)){raw=in.readAllBytes();}
                var d=new DexBackedDexFile(raw,0);partitions++;
                for(int i=0;i<d.classCount;i++){
                    ClassDef def=new DexBackedClassDef(d,d.classStartOffset+i*32,0);
                    if(all.putIfAbsent(def.getType(),def)!=null)throw new IllegalStateException("Duplicate type: "+def.getType());
                }
            }
        }
        if(partitions!=40)throw new IllegalStateException("Forty partitions required");
        int checked=0;
        for(ClassDef def:all.values())if(changed(def.getType()))for(Method method:methods(def)){
            if(method.getImplementation()==null)continue;
            for(Object entry:method.getImplementation().getInstructions()){
                Instruction instruction=(Instruction)entry;
                if(!(instruction instanceof ReferenceInstruction r) || !(r.getReference() instanceof MethodReference ref))continue;
                String owner=ref.getDefiningClass();ClassDef target=all.get(owner);
                if(target==null){
                    if(owner.startsWith("Lorg/emulationstation/frontend/"))throw new IllegalStateException("Missing app owner: "+owner);
                    continue;
                }
                boolean exact=ref.getName().equals("<init>") || instruction.getOpcode().name().startsWith("INVOKE_STATIC");
                boolean found=has(target,signature(ref),all,new HashSet<>(),exact);
                if(!found && (exact || !externalParent(target,all,new HashSet<>())))
                    throw new IllegalStateException("Unresolved app method: "+def.getType()+" -> "+owner+"->"+signature(ref));
                checked++;
            }
        }
        System.out.println("PASS finalPartitions="+partitions+" uniqueClasses="+all.size()+" changedOwnerAppReferences="+checked);
    }
}
