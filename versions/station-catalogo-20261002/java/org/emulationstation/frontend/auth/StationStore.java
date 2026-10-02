package org.emulationstation.frontend.auth;

import android.content.Context;
import android.os.Environment;
import android.util.Log;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * The only catalog the carousel is allowed to read.
 * Cover and game addresses stay on station.invalid and never leave this device.
 */
public final class StationStore {
    private static final String TAG = "StationStore";
    private static final String HOST = "station.invalid";
    private static final String[] ORDER = {
        "snes", "snesbr", "megadrive", "megadrivebr", "gba", "gbc", "gb",
        "gamegear", "mastersystem", "sega32x"
    };

    private StationStore() {}

    public static boolean owned(String url) {
        return url != null && url.toLowerCase().contains(HOST);
    }

    public static String coverId(String url) {
        return kindId(url, "cover");
    }

    public static String gameId(String url) {
        return kindId(url, "game");
    }

    public static void publish(Context context) {
        try {
            byte[] body = body(context);
            int written = writeCaches(body);
            Log.i(TAG, "published bytes=" + body.length + " files=" + written);
        } catch (Exception failure) {
            Log.i(TAG, "kept");
        }
    }

    public static byte[] body(Context context) throws Exception {
        JSONArray items = readItems(context);
        Map<String, List<JSONObject>> grouped = new LinkedHashMap<String, List<JSONObject>>();
        for (int index = 0; index < ORDER.length; index++) {
            grouped.put(ORDER[index], new ArrayList<JSONObject>());
        }
        for (int index = 0; index < items.length(); index++) {
            JSONObject item = items.optJSONObject(index);
            if (item == null) continue;
            String itemId = item.optString("itemId", "");
            String coverId = item.optString("coverId", "");
            String name = item.optString("name", "").trim();
            String platform = item.optString("platform", "").trim();
            if (!StationProtocol.libraryId(itemId) || !StationProtocol.libraryId(coverId)) continue;
            if (name.length() == 0 || platform.length() == 0 || platform.length() > 32) continue;
            List<JSONObject> drawer = grouped.get(platform);
            if (drawer == null) {
                drawer = new ArrayList<JSONObject>();
                grouped.put(platform, drawer);
            }
            JSONObject file = new JSONObject();
            file.put("Id", itemId);
            file.put("DisplayName", name);
            file.put("Url", "https://" + HOST + "/game/" + itemId + ".zip");
            file.put("CoverImage", "https://" + HOST + "/cover/" + coverId + ".png");
            file.put("LaunchPath", "");
            file.put("SubDirectory", "");
            file.put("RequiredPackage", "");
            file.put("CreateDesktopShortcut", false);
            file.put("Extract", false);
            file.put("Order", drawer.size() + 1);
            file.put("Mensal", false);
            file.put("LockFiles", false);
            file.put("Oculto", false);
            drawer.add(file);
        }
        JSONArray drawers = new JSONArray();
        int order = 1;
        for (Map.Entry<String, List<JSONObject>> entry : grouped.entrySet()) {
            if (entry.getValue().isEmpty()) continue;
            Collections.sort(entry.getValue(), new java.util.Comparator<JSONObject>() {
                @Override public int compare(JSONObject left, JSONObject right) {
                    return left.optString("DisplayName", "").compareToIgnoreCase(right.optString("DisplayName", ""));
                }
            });
            for (int index = 0; index < entry.getValue().size(); index++) {
                entry.getValue().get(index).put("Order", index + 1);
            }
            JSONObject drawer = new JSONObject();
            drawer.put("Id", drawerId(entry.getKey()));
            drawer.put("Name", label(entry.getKey()));
            drawer.put("Description", "");
            drawer.put("Order", order++);
            drawer.put("DefaultSubPath", folder(entry.getKey()));
            drawer.put("R2Pasta", entry.getKey());
            drawer.put("RequiredPackage", "RETRO");
            drawer.put("CatalogLabel", "emulador");
            drawer.put("Demo", false);
            drawer.put("Mensal", false);
            drawer.put("Oculta", false);
            drawer.put("Android", true);
            drawer.put("AndroidPackage", "ULTIMATE");
            drawer.put("AndroidDemo", false);
            drawer.put("AndroidMensal", false);
            JSONArray files = new JSONArray();
            for (int index = 0; index < entry.getValue().size(); index++) files.put(entry.getValue().get(index));
            drawer.put("Files", files);
            drawers.put(drawer);
        }
        return drawers.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static JSONArray readItems(Context context) throws Exception {
        File catalog = new File(context.getNoBackupFilesDir(), "station-catalog.json");
        if (!catalog.isFile() || catalog.length() <= 0 || catalog.length() > 5L * 1024L * 1024L) return new JSONArray();
        byte[] data = new byte[(int) catalog.length()];
        try (FileInputStream input = new FileInputStream(catalog)) {
            int offset = 0;
            while (offset < data.length) {
                int count = input.read(data, offset, data.length - offset);
                if (count < 0) break;
                offset += count;
            }
            if (offset != data.length) return new JSONArray();
        }
        JSONArray items = new JSONObject(new String(data, StandardCharsets.UTF_8)).optJSONArray("items");
        return items == null ? new JSONArray() : items;
    }

    private static int writeCaches(byte[] body) throws Exception {
        List<File> homes = new ArrayList<File>();
        homes.add(new File("/storage/emulated/0/EmulationStation/.emulationstation"));
        homes.add(new File("/storage/emulated/0/.emulationstation"));
        File root = Environment.getExternalStorageDirectory();
        if (root != null) {
            homes.add(new File(root, "EmulationStation/.emulationstation"));
            homes.add(new File(root, ".emulationstation"));
        }
        int written = 0;
        for (int index = 0; index < homes.size(); index++) {
            File home = homes.get(index);
            if (!home.isDirectory()) continue;
            File destination = new File(new File(home, "store"), "catalog-cache.json");
            writeAtomic(destination, body);
            written++;
        }
        return written;
    }

    private static void writeAtomic(File destination, byte[] data) throws Exception {
        File parent = destination.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) {
            throw new IllegalStateException("store");
        }
        File partial = new File(parent, destination.getName() + ".part");
        try (FileOutputStream output = new FileOutputStream(partial)) { output.write(data); }
        if (destination.exists() && !destination.delete()) {
            partial.delete();
            throw new IllegalStateException("store");
        }
        if (!partial.renameTo(destination)) {
            partial.delete();
            throw new IllegalStateException("store");
        }
    }

    private static String kindId(String url, String kind) {
        if (url == null) return null;
        String path = url;
        int query = path.indexOf('?');
        if (query >= 0) path = path.substring(0, query);
        int hash = path.indexOf('#');
        if (hash >= 0) path = path.substring(0, hash);
        String marker = "/" + kind + "/";
        int at = path.toLowerCase().indexOf(marker);
        if (at < 0) return null;
        String value = path.substring(at + marker.length());
        int slash = value.indexOf('/');
        if (slash >= 0) value = value.substring(0, slash);
        int dot = value.lastIndexOf('.');
        if (dot > 0) value = value.substring(0, dot);
        return StationProtocol.libraryId(value) ? value : null;
    }

    private static String drawerId(String platform) {
        byte[] digest = StationProtocol.sha256(("station-drawer\n" + platform).getBytes(StandardCharsets.UTF_8));
        StringBuilder builder = new StringBuilder(32);
        for (int index = 0; index < 16; index++) {
            int value = digest[index] & 0xff;
            builder.append(Character.forDigit(value >>> 4, 16));
            builder.append(Character.forDigit(value & 0x0f, 16));
        }
        return builder.toString();
    }

    static String folder(String platform) {
        if ("snes".equals(platform)) return "super-nintendo";
        if ("snesbr".equals(platform)) return "super-nintendo-br";
        if ("megadrivebr".equals(platform)) return "megadrive-br";
        if ("gb".equals(platform)) return "gameboy";
        if ("gbc".equals(platform)) return "gameboy-color";
        if ("mastersystem".equals(platform)) return "master-system";
        return platform;
    }

    private static String label(String platform) {
        if ("snes".equals(platform)) return "Super Nintendo";
        if ("snesbr".equals(platform)) return "Super Nintendo - BR";
        if ("megadrive".equals(platform)) return "MegaDrive";
        if ("megadrivebr".equals(platform)) return "MegaDrive - BR";
        if ("gb".equals(platform)) return "Gameboy";
        if ("gba".equals(platform)) return "Gba";
        if ("gbc".equals(platform)) return "Gameboy Color";
        if ("gamegear".equals(platform)) return "gamegear";
        if ("mastersystem".equals(platform)) return "Master System";
        if ("sega32x".equals(platform)) return "sega32x";
        return platform;
    }
}
