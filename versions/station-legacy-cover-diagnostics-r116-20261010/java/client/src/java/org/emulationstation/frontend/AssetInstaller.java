package org.emulationstation.frontend;

import android.content.Context;
import android.content.res.AssetManager;
import android.util.Log;
import java.io.*;
import java.nio.file.*;
import org.emulationstation.frontend.station.StationBundledFiles;
import org.emulationstation.frontend.station.StationResourceBundle;
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
            int copied=StationResourceBundle.install(source,resources);
            Log.i(TAG,"Packaged resources ready: restored="+copied+" bios="+bios);
        }catch(Exception failed){Log.e(TAG,"Could not prepare packaged resources: "+failed.getClass().getSimpleName());}
    }
}
