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

/** Exact R173 donor projection; only the GameCube room presentation family. */
public final class VerifyScopedPartition {
    static final int MAX_DEX_BYTES = 16 * 1024 * 1024;
    static final class Scope {
        final String partition, checksum;
        final Set<String> families, originalAllowed, finalAllowed;
        Scope(String partition, String checksum, Set<String> families,
              Set<String> originalAllowed, Set<String> finalAllowed) {
            this.partition=partition; this.checksum=checksum; this.families=families;
            this.originalAllowed=originalAllowed; this.finalAllowed=finalAllowed;
        }
        boolean belongs(String type) {
            if (type.equals("Lorg/emulationstation/frontend/station/StationHttp$ResponseBody;")) return false;
            for (String family : families)
                if (type.equals(family) || type.startsWith(family.substring(0,family.length()-1)+"$")) return true;
            return false;
        }
        Set<String> finalTypes(Set<String> donor) {
            Set<String> result=new HashSet<>(donor);
            result.removeAll(originalAllowed); result.addAll(finalAllowed); return result;
        }
    }
    static Set<String> list(String raw) {
        Set<String> result=new TreeSet<>();
        if (raw == null || raw.isEmpty()) throw new IllegalArgumentException("Nonempty explicit class set required");
        for (String type : raw.split("\\|",-1))
            if (!type.matches("Lorg/emulationstation/frontend/[A-Za-z0-9_/$]+;") || !result.add(type))
                throw new IllegalArgumentException("Invalid or duplicate online lifecycle class");
        return result;
    }
    static Scope readScope(String partition, String checksum, Path path) throws Exception {
        Properties properties=new Properties();
        List<String> lines=Files.readAllLines(path,StandardCharsets.UTF_8);
        if (lines.size()!=6) throw new IllegalArgumentException("Exactly six scope fields required");
        for (String line : lines) {
            int separator=line.indexOf('=');
            if(separator<1 || properties.put(line.substring(0,separator),line.substring(separator+1))!=null)
                throw new IllegalArgumentException("Duplicate or malformed scope field");
        }
        if (!properties.stringPropertyNames().equals(Set.of("schema","partition","donorSha256","families","originalAllowed","finalAllowed")) ||
                !"station.gamecube-cpu.scoped-types.r174.v1".equals(properties.getProperty("schema")) ||
                !partition.equals(properties.getProperty("partition")) ||
                !checksum.equals(properties.getProperty("donorSha256")) || !checksum.matches("[0-9a-f]{64}"))
            throw new IllegalStateException("Scope identity");
        Set<String> families=list(properties.getProperty("families"));
        Set<String> expected=Set.of("Lorg/emulationstation/frontend/netplay/StationDolphinSession;","Lorg/emulationstation/frontend/netplay/StationDolphinCpuPolicy;");
        if (!partition.equals("classes35.dex") || !families.equals(expected))
            throw new IllegalStateException("R174 CPU-session-family scope");
        Scope scope=new Scope(partition,checksum,families,list(properties.getProperty("originalAllowed")),list(properties.getProperty("finalAllowed")));
        if (!scope.originalAllowed.equals(Set.of("Lorg/emulationstation/frontend/netplay/StationDolphinSession$Session;")) ||
                !scope.finalAllowed.equals(Set.of("Lorg/emulationstation/frontend/netplay/StationDolphinSession$Session;","Lorg/emulationstation/frontend/netplay/StationDolphinCpuPolicy;"))) throw new IllegalStateException("R174 owner root");
        for (String type : scope.originalAllowed) if (!scope.belongs(type)) throw new IllegalStateException("Foreign original allowed type");
        for (String type : scope.finalAllowed) if (!scope.belongs(type)) throw new IllegalStateException("Foreign final allowed type");
        return scope;
    }
    static byte[] readDonor(String apk, String partition, String checksum) throws Exception {
        byte[] raw;
        try (ZipFile zip=new ZipFile(apk)) {
            var entry=zip.getEntry(partition);
            if (entry==null || entry.getSize()<1 || entry.getSize()>MAX_DEX_BYTES) throw new IllegalStateException("Donor partition size");
            try (var stream=zip.getInputStream(entry)) { raw=stream.readNBytes(MAX_DEX_BYTES+1); }
        }
        if (raw.length>MAX_DEX_BYTES || !HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(raw)).equals(checksum))
            throw new IllegalStateException("Donor DEX identity");
        return raw;
    }
    static Set<String> types(Path directory) throws Exception {
        Set<String> result=new TreeSet<>();
        try (var paths=Files.walk(directory)) {
            for (Path path : paths.filter(p->p.toString().endsWith(".smali")).toList()) {
                if (Files.isSymbolicLink(path)) throw new IllegalStateException("Symbolic smali");
                String relative=directory.relativize(path).toString().replace('\\','/');
                if (!result.add("L"+relative.substring(0,relative.length()-6)+";")) throw new IllegalStateException("Duplicate smali type");
            }
        }
        return result;
    }
    public static void main(String[] args) throws Exception {
        if (args.length!=5) throw new IllegalArgumentException("DONOR PARTITION SHA SMALI_DIR SCOPE_PROPERTIES");
        Scope scope=readScope(args[1],args[2],Path.of(args[4]));
        DexBackedDexFile dex=new DexBackedDexFile(readDonor(args[0],args[1],args[2]),0);
        if (dex.hiddenApiRestrictionsOffset!=0) throw new IllegalStateException("HiddenAPI DEX");
        Set<String> donorTypes=new TreeSet<>(), donorAllowed=new TreeSet<>();
        int unchanged=0;
        for (int i=0;i<dex.classCount;i++) {
            ClassDef def=new DexBackedClassDef(dex,dex.classStartOffset+i*32,0);
            donorTypes.add(def.getType());
            if (scope.belongs(def.getType())) { donorAllowed.add(def.getType()); continue; }
            var options=new BaksmaliOptions();
            options.localsDirective=true; options.sequentialLabels=true; options.debugInfo=true;
            StringWriter text=new StringWriter();
            new ClassDefinition(options,def).writeTo(new BaksmaliWriter(text));
            Path decoded=Path.of(args[3]).resolve(def.getType().substring(1,def.getType().length()-1)+".smali");
            if (!Arrays.equals(text.toString().getBytes(StandardCharsets.UTF_8),Files.readAllBytes(decoded)))
                throw new IllegalStateException("Unrelated class changed: "+def.getType());
            unchanged++;
        }
        if (!donorAllowed.equals(scope.originalAllowed)) throw new IllegalStateException("Original family set differs from pinned scope");
        Set<String> finalTypes=types(Path.of(args[3]));
        if (!finalTypes.equals(scope.finalTypes(donorTypes))) throw new IllegalStateException("Class delta differs from explicit family scope");
        System.out.println("verifiedClasses="+dex.classCount+" finalClasses="+finalTypes.size()+" unchanged="+unchanged+
                " originalAllowed="+scope.originalAllowed.size()+" finalAllowed="+scope.finalAllowed.size()+" donorSHA="+args[2]);
    }
}
