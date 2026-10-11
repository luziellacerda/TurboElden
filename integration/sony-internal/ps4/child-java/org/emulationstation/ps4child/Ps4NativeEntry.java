package org.emulationstation.ps4child;

import android.view.Surface;
import com.bachatas4.android.runtime.pkg.*;
import com.bachatas4.android.runtime.process.NativeRuntimeBridge;
import java.io.File;
import java.util.HashSet;
import java.util.Set;
import java.util.function.IntConsumer;
import java.util.function.BiConsumer;

/** The defining classloader owns both System.load and all registered native methods. */
public final class Ps4NativeEntry {
    private static final Set<String> loaded=new HashSet<>();
    private Ps4NativeEntry() {}
    public static synchronized void loadNative(String[] absolutePaths, String rsaMaterial) throws Exception {
        for (String path:absolutePaths) {
            File file=new File(path);
            if (!file.isAbsolute() || !file.isFile()) throw new IllegalArgumentException("Biblioteca PS4 inválida");
            if (loaded.add(file.getCanonicalPath())) {
                try { System.load(file.getCanonicalPath()); }
                catch (Throwable e) { loaded.remove(file.getCanonicalPath()); throw e; }
            }
        }
        PkgRsa.initialize(new File(rsaMaterial));
    }
    public static String[] probe(int fd) {
        PkgProbeResult p=PkgExtractor.nativeProbe(fd);
        if (p==null) throw new IllegalStateException("O pacote não retornou dados");
        return new String[]{p.contentId,p.titleHint,p.status.name(),Long.toString(p.packageSize),
                             Long.toString(p.pfsImageSize),p.message};
    }
    public static String[] extract(int fd, String directory, BiConsumer<Long,Long> progress) {
        PkgExtractResult result=PkgExtractor.nativeExtract(fd,directory,"00000000000000000000000000000000",new Progress(progress));
        if (result==null) throw new IllegalStateException("O pacote não retornou resultado");
        return new String[]{result.status.name(),result.contentId,result.message};
    }
    private static final class Progress implements PkgProgressListener {
        private final BiConsumer<Long,Long> target;
        Progress(BiConsumer<Long,Long> target) { this.target=target; }
        @Override public void onProgress(long completed,long total,String relativePath) {
            if (target!=null) target.accept(completed,total);
        }
    }
    public static int run(Surface surface,String[] argv,String[] environment,String cwd,IntConsumer exit) {
        NativeRuntimeBridge.setExitListener(exit);
        return NativeRuntimeBridge.run(surface,false,argv,environment,cwd,-1);
    }
    public static void stop() { NativeRuntimeBridge.stop(); }
    public static void cancelImport() { PkgExtractor.nativeCancel(); }
}
