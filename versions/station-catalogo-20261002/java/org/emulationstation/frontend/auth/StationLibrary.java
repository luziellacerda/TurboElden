package org.emulationstation.frontend.auth;

import android.content.Context;
import android.os.Environment;
import android.util.Log;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.HashSet;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.json.JSONArray;
import org.json.JSONObject;

/** Private Station list and covers. Game bytes are fetched only by ensureGame. */
public final class StationLibrary {
    private static final String TAG = "StationLibrary";
    private static final ExecutorService COVERS = Executors.newSingleThreadExecutor();
    private static volatile boolean coverRun;

    private StationLibrary() {}

    public static void refresh(Context context, String accessToken) {
        if (accessToken == null || accessToken.isEmpty()) return;
        try {
            JSONObject catalog = StationClient.catalog(accessToken);
            if (catalog == null) {
                Log.i(TAG, "catalog kept status=503");
                return;
            }
            JSONArray source = catalog.optJSONArray("items");
            JSONArray clean = new JSONArray();
            StringBuilder table = new StringBuilder();
            if (source != null) {
                for (int index = 0; index < source.length(); index++) {
                    JSONObject item = source.optJSONObject(index);
                    if (item == null) continue;
                    String itemId = item.optString("itemId", "");
                    String coverId = item.optString("coverId", "");
                    String name = item.optString("name", "").trim();
                    String platform = item.optString("platform", "").trim();
                    if (!StationProtocol.libraryId(itemId) || !StationProtocol.libraryId(coverId)) continue;
                    if (!plain(name, 120) || !platformOk(platform)) continue;
                    JSONObject row = new JSONObject();
                    row.put("itemId", itemId);
                    row.put("name", name);
                    row.put("platform", platform);
                    row.put("revision", item.optLong("revision", 1));
                    row.put("coverId", coverId);
                    clean.put(row);
                    table.append(itemId).append('\t').append(platform).append('\t')
                        .append(name.replace('\t', ' ').replace('\n', ' ').replace('\r', ' '))
                        .append('\t').append(StationStore.folder(platform)).append("/station/").append(itemId).append('\n');
                }
            }
            JSONObject saved = new JSONObject();
            saved.put("revision", catalog.optLong("revision", 1));
            saved.put("items", clean);
            writeAtomic(new File(context.getNoBackupFilesDir(), "station-catalog.json"),
                saved.toString().getBytes(StandardCharsets.UTF_8));
            writeAtomic(new File(context.getNoBackupFilesDir(), "station-items.tsv"),
                table.toString().getBytes(StandardCharsets.UTF_8));
            Log.i(TAG, "catalog items=" + clean.length());
            noteRevisions(context, clean);
            StationStore.publish(context);
            merge(context);
        } catch (Exception failure) {
            Log.i(TAG, "catalog kept");
        }
    }

    public static void covers(final Context context, final String accessToken) {
        if (accessToken == null || accessToken.isEmpty() || coverRun) return;
        final Context app = context.getApplicationContext();
        COVERS.execute(new Runnable() {
            @Override public void run() {
                coverRun = true;
                int fetched = 0;
                try {
                    File catalogFile = new File(app.getNoBackupFilesDir(), "station-catalog.json");
                    if (!catalogFile.isFile()) return;
                    JSONObject catalog = new JSONObject(readText(catalogFile));
                    JSONArray items = catalog.optJSONArray("items");
                    if (items == null) return;
                    File directory = new File(app.getNoBackupFilesDir(), "station-covers");
                    if (!directory.isDirectory() && !directory.mkdirs()) return;
                    HashSet<String> present = new HashSet<String>();
                    File[] files = directory.listFiles();
                    if (files != null) {
                        for (int index = 0; index < files.length; index++) {
                            String filename = files[index].getName();
                            int dot = filename.lastIndexOf('.');
                            if (dot > 0) present.add(filename.substring(0, dot));
                        }
                    }
                    for (int index = 0; index < items.length(); index++) {
                        JSONObject item = items.optJSONObject(index);
                        if (item == null) continue;
                        String coverId = item.optString("coverId", "");
                        if (!StationProtocol.libraryId(coverId) || present.contains(coverId)) continue;
                        File destination = new File(directory, coverId + ".bin");
                        try {
                            String extension = StationClient.saveCover(accessToken, coverId, destination);
                            File named = new File(directory, coverId + "." + extension);
                            if (!destination.renameTo(named)) destination.delete();
                            else present.add(coverId);
                            fetched++;
                        } catch (SecurityException failure) {
                            destination.delete();
                            if ("Station rate limited.".equals(failure.getMessage())) break;
                        } catch (Exception failure) {
                            destination.delete();
                        }
                        try { Thread.sleep(2100L); }
                        catch (InterruptedException interrupted) { break; }
                    }
                    merge(app);
                } catch (Exception failure) {
                    Log.i(TAG, "covers kept");
                } finally {
                    Log.i(TAG, "covers fetched=" + fetched);
                    coverRun = false;
                }
            }
        });
    }

    public static File ensureGame(Context context, String itemId) throws Exception {
        if (!StationProtocol.libraryId(itemId)) throw new IllegalArgumentException("Station item was rejected.");
        File directory = new File(context.getNoBackupFilesDir(), "station-games");
        if (!directory.isDirectory() && !directory.mkdirs()) throw new SecurityException("Station file was not stored.");
        File destination = new File(directory, itemId);
        if (destination.isFile() && destination.length() > 0) return destination;
        File license = new File(context.getNoBackupFilesDir(), "station-license-id.txt");
        String licenseId = readText(license).trim();
        if (!StationProtocol.licenseId(licenseId)) throw new SecurityException("Station session is missing.");
        String token = StationClient.openSession(context, licenseId);
        String grantId = StationClient.authorize(context, token, itemId);
        StationClient.saveGame(token, grantId, destination);
        Log.i(TAG, "game stored");
        return destination;
    }

    private static void merge(Context context) {
        try {
            File catalogFile = new File(context.getNoBackupFilesDir(), "station-catalog.json");
            if (!catalogFile.isFile()) return;
            JSONObject catalog = new JSONObject(readText(catalogFile));
            JSONArray items = catalog.optJSONArray("items");
            if (items == null) return;
            File roms = roms();
            if (roms == null) return;
            for (int index = 0; index < items.length(); index++) {
                JSONObject item = items.optJSONObject(index);
                if (item == null) continue;
                place(roms, item, coverFile(context, item.optString("coverId", "")));
            }
        } catch (Exception failure) {
            Log.i(TAG, "library kept");
        }
    }

    private static void place(File roms, JSONObject item, File cover) throws Exception {
        String itemId = item.getString("itemId");
        String name = item.getString("name");
        String platform = item.getString("platform");
        if (!platformOk(platform)) return;
        File system = new File(roms, StationStore.folder(platform));
        if (!system.isDirectory() && !system.mkdirs()) return;
        File gamelist = new File(system, "gamelist.xml");
        String text = gamelist.isFile() ? readText(gamelist) : "<gameList>\n</gameList>";
        if (text.indexOf("http://") >= 0 || text.indexOf("https://") >= 0) return;
        String marker = "./station/" + itemId;
        int close = text.lastIndexOf("</gameList>");
        if (close < 0) return;
        if (text.indexOf(marker) >= 0) {
            writeImage(system, text, marker, cover, gamelist);
            return;
        }
        int found = blockWithName(text, name);
        if (found >= 0) {
            writeImage(system, text, name, cover, gamelist);
            return;
        }
        String image = "";
        if (cover != null && cover.isFile()) {
            File copied = new File(new File(system, "station"), cover.getName());
            if (copied.getParentFile() != null) copied.getParentFile().mkdirs();
            copy(cover, copied);
            image = "\n    <image>./station/" + xml(cover.getName()) + "</image>";
        }
        String entry = "  <game>\n    <path>" + marker + "</path>\n    <name>"
            + xml(name) + "</name>" + image + "\n  </game>\n";
        String updated = text.substring(0, close) + entry + text.substring(close);
        writeAtomic(gamelist, updated.getBytes(StandardCharsets.UTF_8));
    }

    private static void writeImage(File system, String text, String needle, File cover, File gamelist) throws Exception {
        if (cover == null || !cover.isFile()) return;
        int start = text.indexOf("<game");
        while (start >= 0) {
            int end = text.indexOf("</game>", start);
            if (end < 0) return;
            String block = text.substring(start, end);
            if (block.indexOf(needle) >= 0) {
                int imageStart = block.indexOf("<image>");
                int imageEnd = block.indexOf("</image>");
                if (imageStart >= 0 && imageEnd > imageStart) {
                    String relative = block.substring(imageStart + 7, imageEnd).trim();
                    if (relative.indexOf("http") < 0 && relative.indexOf("..") < 0 && !relative.startsWith("/")) {
                        File image = new File(system, relative.startsWith("./") ? relative.substring(2) : relative);
                        if (image.getParentFile() != null) image.getParentFile().mkdirs();
                        copy(cover, image);
                    }
                }
                return;
            }
            start = text.indexOf("<game", end);
        }
    }

    private static int blockWithName(String text, String name) {
        String encoded = "<name>" + xml(name) + "</name>";
        return text.indexOf(encoded);
    }

    private static void noteRevisions(Context context, JSONArray items) {
        try {
            File directory = new File(context.getNoBackupFilesDir(), "station-covers");
            if (!directory.isDirectory() && !directory.mkdirs()) return;
            File table = new File(directory, "revisions.tsv");
            HashMap<String, String> previous = new HashMap<String, String>();
            if (table.isFile()) {
                String[] lines = readText(table).split("\n");
                for (int index = 0; index < lines.length; index++) {
                    int tab = lines[index].indexOf('\t');
                    if (tab <= 0) continue;
                    previous.put(lines[index].substring(0, tab), lines[index].substring(tab + 1).trim());
                }
            }
            StringBuilder next = new StringBuilder();
            for (int index = 0; index < items.length(); index++) {
                JSONObject item = items.optJSONObject(index);
                if (item == null) continue;
                String coverId = item.optString("coverId", "");
                if (!StationProtocol.libraryId(coverId)) continue;
                String revision = Long.toString(item.optLong("revision", 1));
                String old = previous.get(coverId);
                if (old != null && !old.equals(revision)) deleteCover(directory, coverId);
                next.append(coverId).append('\t').append(revision).append('\n');
            }
            writeAtomic(table, next.toString().getBytes(StandardCharsets.UTF_8));
        } catch (Exception failure) {
            Log.i(TAG, "covers kept");
        }
    }

    private static void deleteCover(File directory, String coverId) {
        File[] files = directory.listFiles();
        if (files == null) return;
        String prefix = coverId + ".";
        for (int index = 0; index < files.length; index++) {
            if (files[index].getName().startsWith(prefix)) files[index].delete();
        }
    }

    private static File coverFile(Context context, String coverId) {
        if (!StationProtocol.libraryId(coverId)) return null;
        File directory = new File(context.getNoBackupFilesDir(), "station-covers");
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

    private static File roms() {
        File primary = new File(Environment.getExternalStorageDirectory(), "EmulationStation/roms");
        if (primary.isDirectory()) return primary;
        File direct = new File("/storage/emulated/0/EmulationStation/roms");
        if (direct.isDirectory()) return direct;
        return null;
    }

    private static boolean plain(String value, int maximum) {
        if (value == null || value.isEmpty() || value.length() > maximum) return false;
        for (int index = 0; index < value.length(); index++) {
            if (value.charAt(index) < 0x20) return false;
        }
        return true;
    }

    private static boolean platformOk(String value) {
        if (value == null || value.isEmpty() || value.length() > 32) return false;
        for (int index = 0; index < value.length(); index++) {
            char item = value.charAt(index);
            if (!((item >= 'a' && item <= 'z') || (item >= '0' && item <= '9'))) return false;
        }
        return true;
    }

    private static String xml(String value) {
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;");
    }

    private static void copy(File source, File destination) throws Exception {
        if (destination.getParentFile() != null) destination.getParentFile().mkdirs();
        try (FileInputStream input = new FileInputStream(source); FileOutputStream output = new FileOutputStream(destination)) {
            byte[] buffer = new byte[8192];
            int read;
            while ((read = input.read(buffer)) >= 0) output.write(buffer, 0, read);
        }
    }

    private static void writeAtomic(File destination, byte[] data) throws Exception {
        File partial = new File(destination.getParentFile(), destination.getName() + ".part");
        if (partial.getParentFile() != null) partial.getParentFile().mkdirs();
        try (FileOutputStream output = new FileOutputStream(partial)) { output.write(data); }
        if (destination.exists() && !destination.delete()) throw new SecurityException("Station list was not stored.");
        if (!partial.renameTo(destination)) throw new SecurityException("Station list was not stored.");
    }

    private static String readText(File file) throws Exception {
        byte[] data = new byte[(int) file.length()];
        try (FileInputStream input = new FileInputStream(file)) {
            int offset = 0;
            while (offset < data.length) {
                int read = input.read(data, offset, data.length - offset);
                if (read < 0) break;
                offset += read;
            }
        }
        return new String(data, StandardCharsets.UTF_8);
    }
}
