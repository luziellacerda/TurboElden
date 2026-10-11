package org.emulationstation.frontend.station;

import java.io.IOException;
import java.util.*;
import org.json.*;

/** Signed catalogue of immutable menu clips. No server-supplied URLs or paths are followed. */
public final class StationMediaCatalog {
 public static final int MAX_ITEMS=128, MAX_BODY=262144;
 public static final long MAX_FILE=32L*1024*1024, MAX_TOTAL=256L*1024*1024;
 public static final String DOMAIN="TurboRamaStationAndroid/media-catalog/v1";
 public final long revision;
 public final Map<String,Entry> items;
 public static final class Entry {
  public final String asset,sha256;public final long sizeBytes;
  Entry(String asset,String hash,long size){this.asset=asset;sha256=hash;sizeBytes=size;}
  public JSONObject json()throws JSONException{return new JSONObject().put("asset",asset).put("sha256",sha256).put("sizeBytes",sizeBytes)
    .put("contentType","video/mp4").put("width",720).put("height",720).put("fps",30).put("audioTracks",0);}
 }
 public static boolean safeAsset(String value){return value!=null&&value.matches("turbo-system-videos/720-[a-z0-9][a-z0-9_-]{0,95}\\.mp4");}
 public static boolean safeHash(String value){return value!=null&&value.matches("[0-9a-f]{64}");}
 public static Entry entry(JSONObject row)throws IOException,JSONException {
  String asset=row.getString("asset"),hash=row.getString("sha256");long size=StationCatalog.integer(row,"sizeBytes");
  if(!safeAsset(asset)||!safeHash(hash)||size<16||size>MAX_FILE||!row.getString("contentType").equals("video/mp4")
    ||StationCatalog.integer(row,"width")!=720||StationCatalog.integer(row,"height")!=720||StationCatalog.integer(row,"fps")!=30||!zero(row.get("audioTracks")))
   throw new IOException("Invalid menu media entry");
  return new Entry(asset,hash,size);
 }
 private static boolean zero(Object value){return (value instanceof Integer||value instanceof Long)&&((Number)value).longValue()==0;}
 public StationMediaCatalog(JSONObject data)throws IOException,JSONException {
  revision=StationCatalog.integer(data,"revision");if(revision<1||revision>9007199254740991L)throw new IOException("Invalid media revision");
  JSONArray rows=data.getJSONArray("items");if(rows.length()<1||rows.length()>MAX_ITEMS)throw new IOException("Invalid media count");
  Map<String,Entry> result=new LinkedHashMap<>();long total=0;
  for(int i=0;i<rows.length();i++){Entry e=entry(rows.getJSONObject(i));if(result.put(e.asset,e)!=null||(total+=e.sizeBytes)>MAX_TOTAL)throw new IOException("Duplicate/oversize media catalogue");}
  items=Collections.unmodifiableMap(result);
 }
}
