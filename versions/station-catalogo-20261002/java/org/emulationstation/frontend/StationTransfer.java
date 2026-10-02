package org.emulationstation.frontend;

import android.content.Context;
import android.util.Log;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import org.emulationstation.frontend.auth.StationClient;
import org.emulationstation.frontend.auth.StationLibrary;
import org.emulationstation.frontend.auth.StationProtocol;
import org.emulationstation.frontend.auth.StationStore;
import org.libsdl.app.SDL;

/**
 * Answers every carousel request that used to leave the device.
 * The visible list is the Station catalog only. The baked asset catalog is not served.
 */
public final class StationTransfer {
    private static final String TAG = "StationTransfer";
    private static final Object LOCK = new Object();
    private static String token;
    private static long tokenAt;
    private static long lastCover;
    private static volatile byte[] mergedCache;
    private static volatile long mergedStamp;

    private StationTransfer() {}

    public static boolean blocked(String url) {
        return foreign(url);
    }

    private static boolean foreign(String url) {
        if (url == null) return false;
        String lower = url.toLowerCase();
        return lower.contains("miami") || lower.contains("sambox") || lower.contains("squareweb")
            || lower.contains("?e=") || lower.contains("?s=") || lower.contains("&e=") || lower.contains("&s=");
    }

    public static boolean take(String url, String destPath, HttpBridge.Request request) {
        boolean oldHost = foreign(url);
        boolean local = StationStore.owned(url);
        if (!oldHost && !local) return false;
        if (oldHost && !catalog(url)) {
            if (request != null) fail(request);
            return true;
        }
        if (request == null) return true;
        if (request.cancelled) {
            fail(request);
            return true;
        }
        try {
            Context context = SDL.getContext();
            if (context == null) throw new IllegalStateException("missing context");
            if (oldHost && catalog(url)) {
                byte[] body = catalogResponse(context);
                deliver(request, destPath, body);
                Log.i(TAG, "catalog");
                return true;
            }
            String coverId = StationStore.coverId(url);
            if (coverId != null) {
                byte[] bytes = cover(context, coverId);
                deliver(request, destPath, bytes);
                Log.i(TAG, "cover");
                return true;
            }
            String itemId = StationStore.gameId(url);
            if (itemId != null) {
                File game = StationLibrary.ensureGame(context, itemId);
                if (destPath == null || destPath.length() == 0) throw new IllegalStateException("game has no destination");
                copy(game, new File(destPath));
                request.total = game.length();
                if (request.downloadedBytes != null) request.downloadedBytes.set(game.length());
                request.downloadOk = true;
                request.isFile = true;
                request.status = 1;
                Log.i(TAG, "game");
                return true;
            }
            throw new IllegalStateException("not a station file");
        } catch (Exception failure) {
            Log.i(TAG, "miss " + reason(failure));
            fail(request);
        }
        return true;
    }

    private static String reason(Exception failure) {
        String message = failure.getMessage();
        String status = statusToken(message);
        if (status.length() > 0) return status;
        if ("Station file length was rejected.".equals(message)) return "length";
        if ("Station cover type was rejected.".equals(message)) return "type";
        if ("Station file was denied.".equals(message)) return "status";
        if ("Station rate limited.".equals(message)) return "rate";
        if ("Station file redirect was rejected.".equals(message)) return "redirect";
        if ("Station request was denied.".equals(message)) return "session";
        if ("missing context".equals(message)) return "context";
        if ("catalog".equals(message)) return "catalog";
        if ("not a station file".equals(message)) return "file";
        if ("license".equals(message)) return "license";
        if ("cover".equals(message)) return "read";
        String name = failure.getClass().getSimpleName();
        if (name == null || name.length() == 0 || name.indexOf(' ') >= 0) return "error";
        return name;
    }

    private static String statusToken(String message) {
        if (message == null || message.length() < 4 || message.charAt(0) != 's') return "";
        int end = 1;
        while (end < message.length() && message.charAt(end) >= '0' && message.charAt(end) <= '9') end++;
        if (end != 4) return "";
        if (end == message.length()) return message;
        if (message.charAt(end) != ' ') return "";
        String code = message.substring(end + 1);
        if (code.length() < 9 || code.length() > 40 || !code.startsWith("STATION_")) return "";
        for (int index = 0; index < code.length(); index++) {
            char item = code.charAt(index);
            if (!((item >= 'A' && item <= 'Z') || item == '_')) return "";
        }
        return message;
    }

    private static byte[] catalogResponse(Context context) throws Exception {
        File stored = new File(context.getNoBackupFilesDir(), "station-catalog.json");
        if (!stored.isFile() || stored.length() <= 2) throw new IllegalStateException("catalog");
        long stamp = stored.length() ^ stored.lastModified();
        byte[] cached = mergedCache;
        if (cached != null && stamp == mergedStamp) return cached;
        byte[] station = StationStore.body(context);
        if (station.length < 3) throw new IllegalStateException("catalog");
        mergedCache = station;
        mergedStamp = stamp;
        return station;
    }

    private static boolean catalog(String url) {
        String path = url.toLowerCase();
        int query = path.indexOf('?');
        if (query >= 0) path = path.substring(0, query);
        return path.contains("/drawers.json");
    }

    private static void deliver(HttpBridge.Request request, String destPath, byte[] bytes) throws Exception {
        if (destPath != null && destPath.length() > 0) {
            File dest = new File(destPath);
            if (dest.getParentFile() != null) dest.getParentFile().mkdirs();
            try (FileOutputStream output = new FileOutputStream(dest)) { output.write(bytes); }
            request.isFile = true;
        }
        request.content = bytes;
        request.total = bytes.length;
        if (request.downloadedBytes != null) request.downloadedBytes.set(bytes.length);
        request.downloadOk = true;
        request.status = 1;
    }

    private static void fail(HttpBridge.Request request) {
        request.downloadOk = false;
        request.status = 2;
        request.error = "Conteudo indisponivel.";
    }

    private static byte[] cover(Context context, String coverId) throws Exception {
        if (!StationProtocol.libraryId(coverId)) throw new IllegalArgumentException("cover");
        File directory = new File(context.getNoBackupFilesDir(), "station-covers");
        if (!directory.isDirectory() && !directory.mkdirs()) throw new IllegalStateException("covers");
        File existing = stored(directory, coverId);
        if (existing == null) {
            synchronized (LOCK) {
                existing = stored(directory, coverId);
                if (existing == null) {
                    long wait = 2100L - (System.currentTimeMillis() - lastCover);
                    if (wait > 0) Thread.sleep(wait);
                    lastCover = System.currentTimeMillis();
                    existing = fetch(context, directory, coverId);
                }
            }
        }
        return read(existing);
    }

    private static File fetch(Context context, File directory, String coverId) throws Exception {
        File partial = new File(directory, coverId + ".bin");
        String extension;
        try {
            extension = StationClient.saveCover(session(context), coverId, partial);
        } catch (SecurityException failure) {
            partial.delete();
            if (failure.getMessage() == null || !failure.getMessage().startsWith("s401")) throw failure;
            token = null;
            tokenAt = 0L;
            extension = StationClient.saveCover(session(context), coverId, partial);
        }
        File named = new File(directory, coverId + "." + extension);
        if (!partial.renameTo(named)) {
            partial.delete();
            throw new IllegalStateException("cover");
        }
        return named;
    }

    private static String session(Context context) throws Exception {
        synchronized (LOCK) {
            long now = System.currentTimeMillis();
            if (token != null && now - tokenAt < 150000L) return token;
            File license = new File(context.getNoBackupFilesDir(), "station-license-id.txt");
            String licenseId = readText(license).trim();
            if (!StationProtocol.licenseId(licenseId)) throw new IllegalStateException("license");
            token = StationClient.openSession(context, licenseId);
            tokenAt = now;
            return token;
        }
    }

    private static File stored(File directory, String coverId) {
        File[] files = directory.listFiles();
        if (files == null) return null;
        for (int index = 0; index < files.length; index++) {
            String filename = files[index].getName();
            if (filename.startsWith(coverId + ".") && !filename.endsWith(".part") && !filename.endsWith(".bin")) {
                return files[index];
            }
        }
        return null;
    }

    private static void copy(File source, File destination) throws Exception {
        if (destination.getParentFile() != null) destination.getParentFile().mkdirs();
        File partial = new File(destination.getParentFile(), destination.getName() + ".part");
        try (FileInputStream input = new FileInputStream(source); FileOutputStream output = new FileOutputStream(partial)) {
            byte[] buffer = new byte[8192];
            int read;
            while ((read = input.read(buffer)) >= 0) output.write(buffer, 0, read);
        }
        Files.move(partial.toPath(), destination.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
    }

    private static byte[] read(File file) throws Exception {
        if (file.length() <= 0 || file.length() > 5L * 1024L * 1024L) throw new IllegalStateException("cover");
        byte[] data = new byte[(int) file.length()];
        try (FileInputStream input = new FileInputStream(file)) {
            int offset = 0;
            while (offset < data.length) {
                int count = input.read(data, offset, data.length - offset);
                if (count < 0) break;
                offset += count;
            }
            if (offset != data.length) throw new IllegalStateException("cover");
        }
        return data;
    }

    private static String readText(File file) throws Exception {
        return new String(read(file), StandardCharsets.UTF_8);
    }
}
