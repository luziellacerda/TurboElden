package org.emulationstation.frontend;

import android.content.Context;
import android.content.res.AssetManager;
import android.util.Log;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import org.emulationstation.frontend.station.StationBundledFiles;
import org.emulationstation.frontend.station.StationStorage;

/** The APK supplies its resources; a prior phone installation is never a prerequisite. */
public final class AssetInstaller {
    private static final String TAG="EmulationStation";
    private AssetInstaller() {}
    public static synchronized void installIfNeeded(Context context,File homeDir) {
        try{
            Path home=StationStorage.prepareRoot(homeDir.toPath());
            AssetManager assets=context.getAssets();
            StationBundledFiles.Source source=new StationBundledFiles.Source(){
                public String[] list(String path)throws IOException{return assets.list(path);}
                public InputStream open(String path)throws IOException{return assets.open(path);}
            };
            // Integrated Dolphin has its own runtime. The retired packs/Dolphin.zip is
            // absent from this APK and must not be installed as a libretro dependency.
            int bios=StationBundledFiles.install(source,"bios",home.resolve(".emulationstation/bios"),false);
            Path resources=home.resolve(".emulationstation/resources");
            Path marker=resources.resolve(".installed-version");
            long stamp=context.getPackageManager().getPackageInfo(context.getPackageName(),0).lastUpdateTime;
            String version=Long.toString(stamp);
            boolean current=Files.isRegularFile(marker,LinkOption.NOFOLLOW_LINKS)&&
                version.equals(new String(Files.readAllBytes(marker),StandardCharsets.UTF_8).trim());
            // Even with a current marker, repair missing or empty packaged resources.
            int copied=StationBundledFiles.install(source,"resources",resources,!current);
            Files.write(marker,version.getBytes(StandardCharsets.UTF_8),StandardOpenOption.CREATE,
                StandardOpenOption.WRITE,StandardOpenOption.TRUNCATE_EXISTING,LinkOption.NOFOLLOW_LINKS);
            Log.i(TAG,"Packaged resources ready: restored="+copied+" bios="+bios);
        }catch(Exception failed){Log.e(TAG,"Could not prepare packaged resources: "+failed.getClass().getSimpleName());}
    }
}
