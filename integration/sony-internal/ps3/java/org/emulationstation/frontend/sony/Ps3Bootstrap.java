package org.emulationstation.frontend.sony;

import android.app.Application;
import android.content.Context;
import android.os.Build;
import android.os.Looper;
import android.util.AtomicFile;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

/** One native owner per :station_ps3 process; no foreign Application or UI. */
public final class Ps3Bootstrap {
    public static final class Ready {
        public final File userDirectory;
        public final File configFile;
        public final aenu.aps3e.Emulator emulator;
        final StationSonyAssets.Prepared assets;
        Ready(File directory, File config, aenu.aps3e.Emulator emulator,
                StationSonyAssets.Prepared assets) {
            this.userDirectory = directory; this.configFile = config; this.emulator = emulator;
            this.assets = assets;
        }
    }
    private static Ready ready;
    private static Throwable failed;
    private Ps3Bootstrap() {}
    static void requireProcess() {
        if (Build.VERSION.SDK_INT < 28 || !Application.getProcessName().endsWith(":station_ps3"))
            throw new IllegalStateException("PS3 requires its private Android 9+ process");
        boolean arm64 = false;
        for (String abi : Build.SUPPORTED_ABIS) if ("arm64-v8a".equals(abi)) arm64 = true;
        if (!arm64 || !android.os.Process.is64Bit())
            throw new IllegalStateException("PS3 requires ARM64");
    }
    public static synchronized Ready prepare(Context context) throws Exception {
        requireProcess();
        if (Looper.myLooper() == Looper.getMainLooper())
            throw new IllegalStateException("PS3 preparation must run on a worker");
        if (ready != null) return ready;
        if (failed != null) throw new IOException("PS3 native initialization failed", failed);
        try {
            StationSonyAssets.Prepared assets = StationSonyAssets.prepare(context, "ps3",
                    StationSonyAssetPins.PS3_MANIFEST_SHA256);
            File directory = new File(context.getNoBackupFilesDir(), "station-sony/ps3/userdata");
            String[] folders = {"config", "config/dev_flash", "config/dev_flash2", "config/dev_flash3",
                "config/dev_bdvd", "config/dev_hdd0/game", "config/dev_hdd0/home/00000001/exdata",
                "config/dev_hdd1", "config/games", "config/Icons/ui", "config/custom_cfg",
                "logs", "font", "cache", "drivers", "firmware"};
            for (String folder : folders) mkdir(new File(directory, folder));
            File config = new File(directory, "config/config.yml");
            if (!config.isFile()) copyAtomic(assets.assetFile("config/config.yml"), config);
            if (config.length() == 0) throw new IOException("Empty PS3 configuration");
            for (String relative : Ps3AssetPaths.ICONS) {
                File target = new File(directory, "config/" + relative);
                if (!target.isFile()) copyAtomic(assets.assetFile(relative), target);
            }
            StationSonyAssets.loadNative(assets, "liblang_System.so");
            StationSonyAssets.loadNative(assets, "libhardware_ProcessorInfo.so");
            String gpu = aenu.hardware.ProcessorInfo.gpu_get_physical_device_name_vk();
            if (gpu == null || gpu.length() == 0) throw new IOException("Vulkan is unavailable for PS3");
            env("APS3E_DATA_DIR", directory.getAbsolutePath());
            env("APS3E_LOG_DIR", new File(directory, "logs").getAbsolutePath());
            env("APS3E_NATIVE_LIB_DIR", assets.nativeDirectory().getAbsolutePath());
            env("APS3E_ANDROID_API_VERSION", Integer.toString(Build.VERSION.SDK_INT));
            env("APS3E_GLOBAL_CONFIG_YAML_PATH", config.getAbsolutePath());
            env("APS3E_ENABLE_LOG", "false");
            Ps3LocalizedStrings.installEnvironment();
            // Default upstream config selects system Vulkan, not a custom hook/driver.
            StationSonyAssets.loadNative(assets, "libe.so");
            aenu.aps3e.Emulator emulator = new aenu.aps3e.Emulator();
            // Publish only after JNI registration succeeds. Reentry returns the same owner.
            aenu.aps3e.Emulator.get = emulator;
            ready = new Ready(directory, config, emulator, assets);
            return ready;
        } catch (Throwable error) {
            failed = error;
            if (error instanceof Exception) throw (Exception) error;
            throw new IOException("PS3 native initialization failed", error);
        }
    }
    private static void env(String key, String value) {
        aenu.lang.System.setenv(key, value, true);
    }
    static void mkdir(File folder) throws IOException {
        if (!folder.isDirectory() && !folder.mkdirs()) throw new IOException("Could not create PS3 storage");
    }
    static void copyAtomic(File input, File output) throws IOException {
        mkdir(output.getParentFile());
        AtomicFile atomic = new AtomicFile(output);
        FileOutputStream target = null;
        try (FileInputStream source = new FileInputStream(input)) {
            target = atomic.startWrite();
            byte[] buffer = new byte[65536]; int count;
            while ((count = source.read(buffer)) != -1) target.write(buffer, 0, count);
            atomic.finishWrite(target);
        } catch (IOException error) {
            if (target != null) atomic.failWrite(target);
            throw error;
        }
    }
    static void writeAtomic(File file, byte[] bytes) throws IOException {
        mkdir(file.getParentFile()); AtomicFile atomic = new AtomicFile(file);
        FileOutputStream output = null;
        try { output = atomic.startWrite(); output.write(bytes); atomic.finishWrite(output); }
        catch (IOException error) { if (output != null) atomic.failWrite(output); throw error; }
    }
}
