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
import org.json.JSONTokener;

/** The signed Station catalog. Remote addresses are never part of this model. */
public final class StationCatalog {
    public static final int MAX_ITEMS = 40000;
    public static final class Item {
        public final String itemId;
        public final String name;
        public final String platform;
        public final long revision;
        public final String coverId;

        private Item(String itemId, String name, String platform, long revision, String coverId) {
            this.itemId = itemId; this.name = name; this.platform = platform;
            this.revision = revision; this.coverId = coverId;
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

    /** Only called after signature verification; retain typed rows, not a 40,000-object JSON tree. */
    static final class Parsed {
        final JSONObject identity; final StationCatalog catalog;
        Parsed(JSONObject identity,StationCatalog catalog){this.identity=identity;this.catalog=catalog;}
    }
    static Parsed fromVerifiedText(String text) throws IOException {
        try {
            JSONTokener input=new JSONTokener(text);
            if(input.nextClean()!='{')throw new IOException("Catalog object required");
            JSONObject identity=new JSONObject();java.util.Set<String> keys=new java.util.HashSet<>();
            List<Item> items=new ArrayList<>();Map<String,Item> byId=new LinkedHashMap<>();boolean hasItems=false;
            if(input.nextClean()=='}')throw new IOException("Incomplete catalog");input.back();
            while(true){
                Object key=input.nextValue();if(!(key instanceof String)||!keys.add((String)key))throw new IOException("Invalid catalog field");
                if(input.nextClean()!=':')throw new IOException("Catalog separator required");
                if(key.equals("items")){
                    hasItems=true;if(input.nextClean()!='[')throw new IOException("Catalog items required");
                    char next=input.nextClean();
                    if(next!=']'){
                        input.back();
                        while(true){
                            if(items.size()>=MAX_ITEMS)throw new IOException("Catalog exceeds supported item count");
                            Object value=input.nextValue();if(!(value instanceof JSONObject))throw new IOException("Invalid catalog row");
                            addRow((JSONObject)value,items,byId);
                            next=input.nextClean();if(next==']')break;
                            if(next!=',')throw new IOException("Catalog row separator required");
                        }
                    }
                }else{
                    Object value=input.nextValue();
                    if(value instanceof JSONObject||value instanceof JSONArray)throw new IOException("Unexpected catalog metadata object");
                    identity.put((String)key,value);
                }
                char next=input.nextClean();if(next=='}')break;
                if(next!=',')throw new IOException("Catalog field separator required");
            }
            if(!hasItems||input.nextClean()!=0)throw new IOException("Incomplete catalog or trailing data");
            return new Parsed(identity,new StationCatalog(integer(identity,"revision"),items,byId));
        }catch(JSONException invalid){throw new IOException("Incomplete Station catalog",invalid);}
    }
    private static void addRow(JSONObject row,List<Item> items,Map<String,Item> byId)throws IOException,JSONException {
        String itemId=libraryId(StationApi.string(row,"itemId")),coverId=libraryId(StationApi.string(row,"coverId"));
        Item item=new Item(itemId,plainText(StationApi.string(row,"name"),120),plainText(StationApi.string(row,"platform"),120),integer(row,"revision"),coverId);
        if(byId.put(itemId,item)!=null)throw new IOException("Duplicate catalog item");
        items.add(item);
    }

    /** Call only after StationClient has verified the envelope signature and domain. */
    public static StationCatalog fromVerifiedPayload(JSONObject payload) throws IOException {
        try {
            long revision = integer(payload, "revision");
            JSONArray rows = payload.getJSONArray("items");
            if (rows.length() > MAX_ITEMS) throw new IOException("Catalog exceeds supported item count");
            List<Item> items = new ArrayList<>();
            Map<String, Item> byId = new LinkedHashMap<>();
            for (int i = 0; i < rows.length(); i++) {
                addRow(rows.getJSONObject(i),items,byId);
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
                rows.put(row);
            }
            root.put("items", rows);
            return root.toString().getBytes(StandardCharsets.UTF_8);
        } catch (JSONException impossible) {
            throw new IOException("Unable to store Station catalog", impossible);
        }
    }

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
