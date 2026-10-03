package org.station.tests;

import android.content.Context;
import android.content.ContextWrapper;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import org.emulationstation.frontend.SnesBootstrap;
import org.emulationstation.frontend.MegaBootstrap;

/** Runs as shell in a unique /data/local/tmp fixture, never on app/user files. */
public final class StorageIsolationDeviceTest {
    private static int checks;
    private static void check(boolean value) { ++checks; if (!value) throw new AssertionError(checks); }
    private static final class App extends ContextWrapper {
        final File root;
        App(File root) { super(null); this.root=root; }
        @Override public Context getApplicationContext() { return this; }
        @Override public File getFilesDir() { return make("files"); }
        @Override public File getCacheDir() { return make("cache"); }
        @Override public File getExternalFilesDir(String type) { return make("external"); }
        File make(String name) { File f=new File(root,name); if(!f.isDirectory()&&!f.mkdirs())throw new AssertionError(); return f; }
    }
    private static final class NativeContext extends ContextWrapper {
        final boolean snes;
        NativeContext(App app,boolean snes) { super(app);this.snes=snes; }
        // Exactly the virtual-call arrangement used by NativeActivity.loadNativeCode.
        @Override public File getFilesDir() { return new File(snes?SnesBootstrap.filesDir(this):MegaBootstrap.filesDir(this)); }
        @Override public File getCacheDir() { return new File(snes?SnesBootstrap.cacheDir(this):MegaBootstrap.cacheDir(this)); }
        @Override public File getExternalFilesDir(String type) { return snes?SnesBootstrap.externalDirectory(this,type):MegaBootstrap.externalDirectory(this,type); }
    }
    private static void write(File f,String value) throws Exception { Files.write(f.toPath(),value.getBytes(StandardCharsets.UTF_8)); }
    private static String read(File f) throws Exception { return new String(Files.readAllBytes(f.toPath()),StandardCharsets.UTF_8); }
    private static void clean(File f,File root) throws Exception {
        String path=f.getCanonicalPath(),base=root.getCanonicalPath();
        if(!path.equals(base)&&!path.startsWith(base+File.separator))throw new AssertionError("outside fixture");
        if(f.isDirectory()) { File[] children=f.listFiles();if(children!=null)for(File c:children)clean(c,root); }
        if(!f.delete()&&f.exists())throw new AssertionError("fixture cleanup");
    }
    public static void main(String[] args) throws Exception {
        File root=new File("/data/local/tmp/station-explus-storage-"+System.nanoTime());
        if(!root.mkdir())throw new AssertionError();
        try {
            App app=new App(root); NativeContext snes=new NativeContext(app,true),mega=new NativeContext(app,false);
            File shared=new File(app.getFilesDir(),"config");write(shared,"legacy-do-not-import");
            File sf=snes.getFilesDir(),mf=mega.getFilesDir();
            check(sf.isDirectory());check(mf.isDirectory());check(!sf.equals(mf));
            check(sf.getName().equals("snes-explus"));check(mf.getName().equals("mega-explus"));
            check(sf.getParentFile().equals(app.getFilesDir()));check(mf.getParentFile().equals(app.getFilesDir()));
            check(!new File(sf,"config").exists());check(!new File(mf,"config").exists());
            write(new File(sf,"config"),"SNES-L-R-X-Y");write(new File(mf,"config"),"MEGA-A-B-C");
            check(snes.getFilesDir().equals(sf));check(mega.getFilesDir().equals(mf));
            check(read(new File(sf,"config")).equals("SNES-L-R-X-Y"));
            check(read(new File(mf,"config")).equals("MEGA-A-B-C"));
            check(read(shared).equals("legacy-do-not-import"));
            check(!snes.getCacheDir().equals(mega.getCacheDir()));
            check(!snes.getExternalFilesDir(null).equals(mega.getExternalFilesDir(null)));
            System.out.println("PASS "+checks+" Android NativeActivity storage-isolation regression checks");
        } finally { clean(root,root); }
    }
}
