package org.emulationstation.frontend.station;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** The signed Station catalog. Remote addresses are never part of this model. */
public final class StationCatalog {
    public static final int MAX_ITEMS = 4096;
    public static final class Item {
        public final String itemId;
        public final String name;
        public final String platform;
        public final long revision;
        public final String coverId;
        public final List<String> folderPath;
        public final String description, developer, publisher, genre, players, releaseDate;

        private Item(String itemId, String name, String platform, long revision, String coverId, String description, JSONObject row) throws IOException, JSONException {
            this.itemId = itemId; this.name = name; this.platform = platform;
            this.revision = revision; this.coverId = coverId; this.description = description;this.folderPath=readFolderPath(row);
            developer=metadataText(row,"developer",80);publisher=metadataText(row,"publisher",80);
            genre=metadataText(row,"genre",80);players=metadataText(row,"players",40);releaseDate=metadataText(row,"releaseDate",40);
        }
    }

    public final long revision;
    public final List<Item> items;
    private final Map<String, Item> byId;

    private StationCatalog(long revision, List<Item> items, Map<String, Item> byId) {
        this.revision = revision;
        this.items = Collections.unmodifiableList(items);
        this.byId = Collections.unmodifiableMap(byId);
    }

    public Item find(String itemId) { return byId.get(itemId); }

    /** Call only after StationClient has verified the envelope signature and domain. */
    public static StationCatalog fromVerifiedPayload(JSONObject payload) throws IOException {
        try {
            long revision = integer(payload, "revision");
            JSONArray rows = payload.getJSONArray("items");
            if (rows.length() > MAX_ITEMS) throw new IOException("Catalog exceeds supported item count");
            List<Item> items = new ArrayList<>();
            Map<String, Item> byId = new LinkedHashMap<>();
            for (int i = 0; i < rows.length(); i++) {
                JSONObject row = rows.getJSONObject(i);
                String itemId = libraryId(StationApi.string(row, "itemId"));
                String coverId = libraryId(StationApi.string(row, "coverId"));
                String name = plainText(StationApi.string(row, "name"), 120);
                String platform = plainText(StationApi.string(row, "platform"), 120);
                Item item = new Item(itemId, name, platform, integer(row, "revision"), coverId, description(row), row);
                if (byId.put(itemId, item) != null) throw new IOException("Duplicate catalog item");
                items.add(item);
            }
            return new StationCatalog(revision, items, byId);
        } catch (JSONException invalid) {
            throw new IOException("Incomplete Station catalog", invalid);
        }
    }

    public byte[] localPayload() throws IOException {
        try {
            JSONObject root = new JSONObject();
            root.put("revision", revision);
            JSONArray rows = new JSONArray();
            for (Item item : items) {
                JSONObject row = new JSONObject();
                row.put("itemId", item.itemId); row.put("name", item.name);
                row.put("platform", item.platform); row.put("revision", item.revision);
                row.put("coverId", item.coverId);
                row.put("metadata", new JSONObject().put("description", item.description).put("developer",item.developer).put("publisher",item.publisher).put("genre",item.genre).put("players",item.players).put("releaseDate",item.releaseDate));
                if(!item.folderPath.isEmpty())row.put("folderPath",new JSONArray(item.folderPath));
                rows.put(row);
            }
            root.put("items", rows);
            return root.toString().getBytes(StandardCharsets.UTF_8);
        } catch (JSONException impossible) {
            throw new IOException("Unable to store Station catalog", impossible);
        }
    }

    private static String metadataText(JSONObject row,String key,int limit)throws IOException,JSONException {
        JSONObject metadata=row.optJSONObject("metadata");
        if(metadata==null||!metadata.has(key))return "";
        String value=StationApi.string(metadata,key);return value.isEmpty()?"":plainText(value,limit);
    }
    private static String description(JSONObject row) throws IOException, JSONException {
        JSONObject metadata = row.optJSONObject("metadata");
        if (metadata == null || !metadata.has("description")) return "";
        String value = StationApi.string(metadata, "description");
        if (value.length() > 2000) throw new IOException("Catalog description too long");
        for (int i=0; i<value.length(); i++) {
            char c=value.charAt(i);
            if (c == 0 || Character.isISOControl(c) && c != '\n' && c != '\t')
                throw new IOException("Invalid catalog description");
            if (Character.isSurrogate(c) && (i+1>=value.length() ||
                !Character.isSurrogatePair(c,value.charAt(++i)))) throw new IOException("Invalid catalog description");
        }
        return value;
    }

    private static List<String> readFolderPath(JSONObject row)throws JSONException,IOException {
        if(!row.has("folderPath"))return Collections.emptyList();
        Object value=row.get("folderPath");if(!(value instanceof JSONArray))throw new IOException("Invalid catalog folder path");
        JSONArray path=(JSONArray)value;if(path.length()>8)throw new IOException("Catalog folder depth exceeds limit");
        ArrayList<String> segments=new ArrayList<>();
        for(int i=0;i<path.length();i++){
            Object part=path.get(i);if(!(part instanceof String))throw new IOException("Invalid catalog folder name");
            String text=plainText((String)part,80);
            if(text.trim().isEmpty()||text.equals(".")||text.equals("..")||text.indexOf('/')>=0||text.indexOf('\\')>=0)
                throw new IOException("Invalid catalog folder name");
            segments.add(text);
        }
        return Collections.unmodifiableList(segments);
    }

    public static String folderKey(Item item){return String.join("/",item.folderPath);}

    public static String libraryId(String value) throws IOException {
        if (value == null || !value.matches("[A-Za-z0-9_-]{8,64}"))
            throw new IOException("Invalid Station content identifier");
        return value;
    }

    public static String plainText(String value, int limit) throws IOException {
        if (value == null || value.length() < 1 || value.length() > limit)
            throw new IOException("Invalid catalog text");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (Character.isISOControl(c) || Character.isSurrogate(c) &&
                    (i + 1 >= value.length() || !Character.isSurrogatePair(c, value.charAt(++i))))
                throw new IOException("Invalid catalog text");
        }
        return value;
    }

    static long integer(JSONObject row, String key) throws JSONException, IOException {
        Object value = row.get(key);
        if (!(value instanceof Integer) && !(value instanceof Long))
            throw new IOException("Invalid catalog revision");
        long result = ((Number)value).longValue();
        if (result < 1) throw new IOException("Invalid catalog revision");
        return result;
    }
}
