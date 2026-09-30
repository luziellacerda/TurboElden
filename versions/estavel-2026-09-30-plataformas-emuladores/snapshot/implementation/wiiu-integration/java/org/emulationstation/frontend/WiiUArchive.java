package org.emulationstation.frontend;

import android.content.Context;
import android.app.Activity;
import android.app.Application;
import android.os.Bundle;
import android.system.ErrnoException;
import android.system.Os;
import android.system.OsConstants;
import java.io.*;
import java.nio.channels.FileLock;
import java.nio.channels.OverlappingFileLockException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Locale;
import java.util.Properties;

/** One reusable, private, derived extraction; the downloaded archive is never modified. */
final class WiiUArchive {
    interface Progress {
        void onProgress(int percent, String message);
        boolean isCancelled();
    }

    private static final long MAX_BYTES = 32L * 1024 * 1024 * 1024;
    private static final int MAX_ENTRIES = 200000;
    private static final int MAX_DEPTH = 32;
    private static final String ROOT = "turbo-wiiu-prepared-v1";
    private static boolean loaded;
    private static boolean lifecycleRegistered, launchReserved;
    private static Activity playing;

    static synchronized void watchApplication(Application application) {
        if (!lifecycleRegistered) {
            application.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks() {
                @Override public void onActivityCreated(Activity a, Bundle b) {
                    if ("info.cemu.cemu.emulation.EmulationActivity".equals(a.getClass().getName())) {
                        synchronized (WiiUArchive.class) { playing = a; launchReserved = true; }
                    }
                }
                @Override public void onActivityDestroyed(Activity a) {
                    synchronized (WiiUArchive.class) {
                        if (playing == a && !a.isChangingConfigurations()) { playing = null; launchReserved = false; }
                    }
                }
                @Override public void onActivityStarted(Activity a) { }
                @Override public void onActivityResumed(Activity a) { }
                @Override public void onActivityPaused(Activity a) { }
                @Override public void onActivityStopped(Activity a) { }
                @Override public void onActivitySaveInstanceState(Activity a, Bundle b) { }
            });
            lifecycleRegistered = true;
        }
    }

    static synchronized boolean beginLaunch(Application application) {
        if (launchReserved) return false;
        watchApplication(application);
        launchReserved = true;
        return true;
    }

    static synchronized void abortLaunch() {
        if (playing == null) launchReserved = false;
    }

    private static synchronized void load() {
        if (!loaded) { System.loadLibrary("turbo_wiiu_archive"); loaded = true; }
    }

    private static native String extractRar(String source, String directory,
                                           long expectedSize, long expectedModified,
                                           Progress progress);

    static File prepare(Context context, File requested, Progress progress) throws Exception {
        checkCancelled(progress);
        File source = requested.getCanonicalFile();
        if (!isRar(source)) {
            // Preserve launch support for already extracted titles and direct images.
            File executable = WiiUBootstrap.executable(source, 0);
            if (executable != null) return executable;
            ArrayList<File> archives = new ArrayList<>();
            scanRars(source, source.getCanonicalPath(), 0, new int[]{0}, archives, progress);
            if (archives.size() != 1)
                throw new IOException(archives.isEmpty()
                    ? "Nenhum jogo Wii U compatível foi encontrado neste download."
                    : "Há mais de um RAR nesta pasta. Selecione o arquivo de um único jogo.");
            source = archives.get(0);
        }
        if (!source.isFile() || !source.canRead() || source.length() <= 0)
            throw new IOException("O download Wii U está vazio, incompleto ou indisponível.");

        long size = source.length(), modified = source.lastModified();
        String identity = source.getCanonicalPath() + "\n" + size + "\n" + modified;
        String key = sha256(identity);
        File root = new File(context.getNoBackupFilesDir(), ROOT);
        if (!root.isDirectory() && !root.mkdirs())
            throw new IOException("Não foi possível criar a pasta temporária Wii U.");
        root = root.getCanonicalFile();
        // Internal app storage only; no external path or archive entry can select this directory.
        requireChild(context.getNoBackupFilesDir().getCanonicalPath(), root);
        if (source.getCanonicalPath().startsWith(root.getCanonicalPath() + File.separator))
            throw new IOException("Um RAR dentro da preparação anterior não será extraído novamente. Selecione o download original.");

        try (RandomAccessFile lockFile = new RandomAccessFile(new File(root, ".lock"), "rw")) {
            FileLock lock;
            try { lock = lockFile.getChannel().tryLock(); }
            catch (OverlappingFileLockException busy) { lock = null; }
            if (lock == null) throw new IOException("Outro jogo Wii U está sendo preparado. Aguarde e tente novamente.");
            try {
                checkCancelled(progress);
                File ready = new File(root, "ready-" + key);
                File reused = cachedExecutable(ready, key);
                if (reused != null) {
                    progress.onProgress(100, "Jogo Wii U pronto");
                    return reused;
                }

                // There is at most one ready title or one incomplete extraction, never a growing cache.
                // Only our own derived folders are removed. The downloaded source and saves are elsewhere.
                File[] old = root.listFiles();
                if (old == null) throw new IOException("Não foi possível consultar a preparação anterior.");
                for (File item : old) {
                    String name = item.getName();
                    if (name.startsWith("ready-") || name.startsWith("stage-"))
                        removeDerived(root, item);
                }
                checkCancelled(progress);
                File stage = new File(root, "stage-" + key);
                if (!stage.mkdir()) throw new IOException("Não foi possível preparar a pasta do jogo.");
                boolean committed = false;
                try {
                    load();
                    progress.onProgress(0, "Preparando jogo Wii U");
                    String error = extractRar(source.getAbsolutePath(), stage.getAbsolutePath(),
                                              size, modified, progress);
                    if (error != null) throw new IOException(error);
                    checkCancelled(progress);
                    if (source.length() != size || source.lastModified() != modified)
                        throw new IOException("O download foi alterado durante a preparação. Aguarde terminar e tente novamente.");
                    File executable = findPreparedExecutable(stage, progress);
                    String relative = stage.toURI().relativize(executable.toURI()).getPath();
                    if (relative.isEmpty()) throw new IOException("Caminho Wii U inválido.");
                    Properties record = new Properties();
                    record.setProperty("version", "1");
                    record.setProperty("key", key);
                    record.setProperty("executable", relative);
                    record.setProperty("executable_size", Long.toString(executable.length()));
                    try (FileOutputStream out = new FileOutputStream(new File(stage, ".complete"))) {
                        record.store(out, "Turborama Wii U derived extraction");
                        out.getFD().sync();
                    }
                    checkCancelled(progress);
                    if (!stage.renameTo(ready)) throw new IOException("Não foi possível concluir a preparação Wii U.");
                    committed = true;
                    progress.onProgress(100, "Jogo Wii U pronto");
                    return new File(ready, relative);
                } finally {
                    if (!committed) removeDerived(root, stage);
                }
            } finally { lock.release(); }
        }
    }

    private static File cachedExecutable(File ready, String key) throws IOException {
        if (!ready.isDirectory()) return null;
        Properties p = new Properties();
        try (FileInputStream in = new FileInputStream(new File(ready, ".complete"))) {
            p.load(in);
            if (!"1".equals(p.getProperty("version")) || !key.equals(p.getProperty("key"))) return null;
            String relative = p.getProperty("executable", "");
            File file = new File(ready, relative).getCanonicalFile();
            requireChild(ready.getCanonicalPath(), file);
            long expected = Long.parseLong(p.getProperty("executable_size", "0"));
            return expected > 0 && file.isFile() && file.length() == expected && isPreparedExecutable(file)
                ? file : null;
        } catch (IOException | NumberFormatException invalid) { return null; }
    }

    private static File findPreparedExecutable(File stage, Progress progress) throws IOException {
        ArrayList<File> images = new ArrayList<>(), rpx = new ArrayList<>();
        scanPrepared(stage, stage.getCanonicalPath(), 0, new long[]{0, 0}, images, rpx, progress);
        // Reject ambiguous bundles rather than launching an update or an arbitrary second title.
        if (images.size() == 1 && rpx.isEmpty()) return images.get(0);
        if (images.isEmpty() && rpx.size() == 1) return rpx.get(0);
        if (images.isEmpty() && rpx.isEmpty())
            throw new IOException("O RAR não contém WUX, WUD, WUA ou RPX. Pacotes criptografados/NUS ou RAR dentro de RAR precisam ser preparados separadamente.");
        throw new IOException("O RAR contém mais de um executável Wii U. Separe o jogo base de atualizações e de outros títulos.");
    }

    private static void scanPrepared(File file, String root, int depth, long[] counts,
                                     ArrayList<File> images, ArrayList<File> rpx,
                                     Progress progress) throws IOException {
        checkCancelled(progress);
        if (depth > MAX_DEPTH || ++counts[0] > MAX_ENTRIES)
            throw new IOException("O pacote excede o limite de pastas ou arquivos.");
        if (depth > 0) requireChild(root, file);
        if (file.isFile()) {
            counts[1] += file.length();
            if (counts[1] > MAX_BYTES) throw new IOException("O pacote excede o limite de 32 GiB.");
            if (file.length() > 0 && isPreparedExecutable(file)) {
                if (file.getName().toLowerCase(Locale.ROOT).endsWith(".rpx")) rpx.add(file);
                else images.add(file);
            }
        } else if (file.isDirectory()) {
            File[] list = file.listFiles();
            if (list == null) throw new IOException("Não foi possível ler os arquivos preparados.");
            for (File child : list) scanPrepared(child, root, depth + 1, counts, images, rpx, progress);
        }
    }

    private static void scanRars(File file, String root, int depth, int[] count,
                                 ArrayList<File> output, Progress progress) throws IOException {
        checkCancelled(progress);
        if (depth > 8 || ++count[0] > MAX_ENTRIES || output.size() > 1) return;
        if (depth > 0) requireChild(root, file);
        if (isRar(file)) { output.add(file.getCanonicalFile()); return; }
        if (file.isDirectory()) {
            File[] list = file.listFiles();
            if (list != null) for (File child : list) scanRars(child, root, depth + 1, count, output, progress);
        }
    }

    private static boolean isRar(File file) {
        return file.isFile() && file.getName().toLowerCase(Locale.ROOT).endsWith(".rar");
    }

    private static boolean isPreparedExecutable(File file) {
        String name = file.getName().toLowerCase(Locale.ROOT);
        return name.endsWith(".wux") || name.endsWith(".wud") || name.endsWith(".wua") || name.endsWith(".rpx");
    }

    private static void checkCancelled(Progress progress) throws IOException {
        if (progress.isCancelled() || Thread.currentThread().isInterrupted())
            throw new IOException("Preparação cancelada. O download original foi preservado.");
    }

    private static void requireChild(String root, File file) throws IOException {
        if (!file.getCanonicalPath().startsWith(root + File.separator))
            throw new IOException("O pacote contém um caminho fora da pasta permitida.");
    }

    private static void removeDerived(File root, File item) throws IOException {
        String lexical = item.getAbsolutePath();
        if (!lexical.startsWith(root.getAbsolutePath() + File.separator))
            throw new IOException("A limpeza foi interrompida por caminho inválido.");
        // lstat avoids following a link if a previous interrupted preparation contained one.
        try {
            int mode = Os.lstat(lexical).st_mode;
            if (OsConstants.S_ISDIR(mode)) {
                requireChild(root.getCanonicalPath(), item);
                File[] children = item.listFiles();
                if (children == null) throw new IOException("Não foi possível limpar a preparação incompleta.");
                for (File child : children) removeDerived(root, child);
            }
            if (!item.delete()) throw new IOException("Não foi possível limpar a preparação anterior.");
        } catch (ErrnoException error) {
            if (error.errno != OsConstants.ENOENT) throw new IOException("Erro ao limpar a preparação anterior.", error);
        }
    }

    private static String sha256(String identity) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(identity.getBytes(StandardCharsets.UTF_8));
        StringBuilder out = new StringBuilder(64);
        for (byte b : digest) out.append(String.format(Locale.ROOT, "%02x", b & 255));
        return out.toString();
    }
}
