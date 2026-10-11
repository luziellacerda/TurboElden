// Test fixture only. Never included in the application.
package org.json;import java.util.*;public class JSONArray{private final List<Object> v=new ArrayList<>();public JSONArray put(Object o){v.add(o);return this;}public int length(){return v.size();}public JSONObject getJSONObject(int i){return (JSONObject)v.get(i);} }
