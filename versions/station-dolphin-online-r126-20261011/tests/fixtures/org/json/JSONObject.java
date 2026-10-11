package org.json;
import java.util.*;
/** Minimal typed fixture builder, not an application JSON parser. */
public final class JSONObject {
    private final Map<String,Object> values=new HashMap<>();
    public JSONObject put(String key,Object value){values.put(key,value);return this;}
    private Object value(String key){if(!values.containsKey(key))throw new IllegalArgumentException("Missing fixture field");return values.get(key);}
    public String getString(String key){return (String)value(key);}
    public int getInt(String key){return ((Number)value(key)).intValue();}
    public boolean getBoolean(String key){return (Boolean)value(key);}
    public JSONObject getJSONObject(String key){return (JSONObject)value(key);}
    public JSONArray getJSONArray(String key){return (JSONArray)value(key);}
}
