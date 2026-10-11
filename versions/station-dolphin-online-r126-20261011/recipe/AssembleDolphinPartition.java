import java.io.File;
import java.nio.file.*;
import java.util.*;
import brut.androlib.smali.SmaliBuilder;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.writer.builder.DexBuilder;
import com.android.tools.smali.dexlib2.writer.io.FileDataStore;

/** Assemble only the explicitly supplied patched partition, preserving all other APK entries. */
public final class AssembleDolphinPartition {
    public static void main(String[] args)throws Exception {
        if(args.length!=2)throw new IllegalArgumentException("source directory, destination DEX");
        Path root=Paths.get(args[0]);List<Path> paths=new ArrayList<>();
        try(java.util.stream.Stream<Path> files=Files.walk(root)){files.filter(p->p.toString().endsWith(".smali")).forEach(paths::add);}
        paths.sort(Comparator.comparing(p->root.relativize(p).toString()));
        if(paths.isEmpty())throw new IllegalStateException("Missing partition source");
        SmaliBuilder assembler=new SmaliBuilder(28);DexBuilder dex=new DexBuilder(new Opcodes(28));
        for(Path path:paths)if(!assembler.buildFile(path.toFile(),dex))throw new IllegalStateException("Invalid smali: "+root.relativize(path));
        File output=new File(args[1]);if(output.exists())throw new IllegalStateException("Destination exists");
        FileDataStore store=new FileDataStore(output);try{dex.writeTo(store);}finally{store.raf.close();}
        System.out.println("Assembled partition files: "+paths.size());
    }
}
