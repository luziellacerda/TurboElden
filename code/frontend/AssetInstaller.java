package org.emulationstation.frontend;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.res.AssetManager;
import android.util.Log;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.Closeable;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public final class AssetInstaller {
    private static final String ASSET_ROOT = "resources";
    private static final String BIOS_ROOT = "bios";
    private static final String MARKER_NAME = ".installed-version";
    private static final String[][] PACKS = {new String[]{"packs/Dolphin.zip", ".pack-dolphin_libretro_android.so.ok"}};

    private AssetInstaller() {
    }

    public static void installIfNeeded(Context context, File homeDir) {
        installMissing(context.getAssets(), BIOS_ROOT, new File(homeDir, ".emulationstation/bios"));
        installPacks(context, new File(homeDir, ".emulationstation/bios"));
        File target = new File(homeDir, ".emulationstation/resources");
        File marker = new File(target, MARKER_NAME);
        long version = installStamp(context);
        if (version == readMarker(marker)) {
            return;
        }
        Log.i(ESActivity.TAG, "Installing resources into " + target);
        if (!target.exists() && !target.mkdirs()) {
            Log.e(ESActivity.TAG, "Could not create " + target + " - is storage access granted?");
            return;
        }
        try {
            copyAssetDir(context.getAssets(), ASSET_ROOT, target);
            writeMarker(marker, version);
            Log.i(ESActivity.TAG, "Resources installed.");
        } catch (IOException e) {
            Log.e(ESActivity.TAG, "Failed to install resources", e);
        }
    }

    private static void installPacks(Context context, final File systemDir) {
        final List<String[]> pending = new ArrayList<>();
        for (String[] pack : PACKS) {
            if (!new File(systemDir, pack[1]).exists()) {
                pending.add(pack);
            }
        }
        if (pending.isEmpty()) {
            return;
        }
        final AssetManager assets = context.getAssets();
        Thread worker = new Thread(new Runnable() {
            @Override
            public void run() {
                for (String[] pack2 : pending) {
                    File installing = new File(systemDir, pack2[1] + ".installing");
                    try {
                        try {
                            OutputStream flag = new FileOutputStream(installing);
                            try {
                                flag.write("1\n".getBytes());
                                flag.close();
                                long started = System.currentTimeMillis();
                                int files = AssetInstaller.extractPack(assets, pack2[0], systemDir);
                                OutputStream marker = new FileOutputStream(new File(systemDir, pack2[1]));
                                try {
                                    marker.write("ok\n".getBytes());
                                    marker.close();
                                    Log.i(ESActivity.TAG, "Installed " + pack2[0] + ": " + files + " files in " + (System.currentTimeMillis() - started) + " ms");
                                    installing.delete();
                                } catch (Throwable th) {
                                    marker.close();
                                    throw th;
                                }
                            } catch (Throwable th2) {
                                flag.close();
                                throw th2;
                            }
                        } catch (Exception e) {
                            Log.e(ESActivity.TAG, "Could not install " + pack2[0], e);
                        }
                    } catch (Throwable th3) {
                        installing.delete();
                        throw th3;
                    }
                }
            }
        }, "es-pack-installer");
        worker.setPriority(1);
        worker.start();
    }

    public static int extractPack(AssetManager assets, String assetPath, File destDir) throws IOException {
        if (!destDir.exists() && !destDir.mkdirs()) {
            throw new IOException("could not create " + destDir);
        }
        String rootPath = destDir.getCanonicalPath() + File.separator;
        ZipInputStream zip = new ZipInputStream(new BufferedInputStream(assets.open(assetPath)));
        int files = 0;
        try {
            byte[] buffer = new byte[65536];
            while (true) {
                ZipEntry entry = zip.getNextEntry();
                if (entry != null) {
                    File target = new File(destDir, entry.getName()).getCanonicalFile();
                    if (!target.getPath().startsWith(rootPath)) {
                        throw new IOException("zip entry escapes the folder: " + entry.getName());
                    }
                    if (entry.isDirectory()) {
                        target.mkdirs();
                    } else {
                        File parent = target.getParentFile();
                        if (parent != null && !parent.exists() && !parent.mkdirs()) {
                            throw new IOException("could not create " + parent);
                        }
                        OutputStream out = new FileOutputStream(target);
                        while (true) {
                            try {
                                int read = zip.read(buffer);
                                if (read <= 0) {
                                    break;
                                }
                                out.write(buffer, 0, read);
                            } catch (Throwable th) {
                                out.close();
                                throw th;
                            }
                        }
                        out.close();
                        files++;
                    }
                } else {
                    zip.close();
                    return files;
                }
            }
        } catch (Throwable th2) {
            zip.close();
            throw th2;
        }
    }

    private static void installMissing(AssetManager assets, String assetPath, File target) {
        try {
            String[] entries = assets.list(assetPath);
            if (entries != null && entries.length != 0) {
                for (String entry : entries) {
                    installMissing(assets, assetPath + "/" + entry, new File(target, entry));
                }
                return;
            }
            if (!target.exists()) {
                copyAssetFile(assets, assetPath, target);
                Log.i(ESActivity.TAG, "Installed " + target);
            }
        } catch (IOException e) {
            Log.e(ESActivity.TAG, "Failed to install " + target, e);
        }
    }

    private static void copyAssetDir(AssetManager assets, String assetPath, File target) throws IOException {
        String[] entries = assets.list(assetPath);
        if (entries == null || entries.length == 0) {
            copyAssetFile(assets, assetPath, target);
            return;
        }
        if (!target.exists() && !target.mkdirs()) {
            throw new IOException("could not create " + target);
        }
        for (String entry : entries) {
            copyAssetDir(assets, assetPath + "/" + entry, new File(target, entry));
        }
    }

    private static void copyAssetFile(AssetManager assets, String assetPath, File target) throws IOException {
        File parent = target.getParentFile();
        if (parent != null && !parent.exists() && !parent.mkdirs()) {
            throw new IOException("could not create " + parent);
        }
        InputStream in = null;
        OutputStream out = null;
        try {
            in = assets.open(assetPath);
            out = new FileOutputStream(target);
            byte[] buffer = new byte[16384];
            while (true) {
                int read = in.read(buffer);
                if (read > 0) {
                    out.write(buffer, 0, read);
                } else {
                    closeQuietly(in);
                    closeQuietly(out);
                    return;
                }
            }
        } catch (Throwable th) {
            closeQuietly(in);
            closeQuietly(out);
            throw th;
        }
    }

    private static long installStamp(Context context) {
        try {
            PackageInfo info = context.getPackageManager().getPackageInfo(context.getPackageName(), 0);
            return info.lastUpdateTime;
        } catch (Exception e) {
            return -1L;
        }
    }

    private static long readMarker(File marker) {
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader(marker));
            return Long.parseLong(reader.readLine().trim());
        } catch (Exception e) {
            return -1L;
        } finally {
            closeQuietly(reader);
        }
    }

    private static void writeMarker(File marker, long version) {
        FileWriter writer = null;
        try {
            try {
                writer = new FileWriter(marker);
                writer.write(String.valueOf(version));
            } catch (IOException e) {
                Log.w(ESActivity.TAG, "Could not write " + marker + " - resources will be reinstalled on every boot", e);
            }
        } finally {
            closeQuietly(writer);
        }
    }

    private static void closeQuietly(Closeable closeable) {
        if (closeable == null) {
            return;
        }
        try {
            closeable.close();
        } catch (IOException e) {
        }
    }
}
