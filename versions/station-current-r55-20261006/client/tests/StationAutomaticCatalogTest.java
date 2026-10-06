package org.emulationstation.frontend.station;
import org.json.*;
import java.nio.charset.StandardCharsets;
public final class StationAutomaticCatalogTest {
 static void check(boolean result){if(!result)throw new AssertionError("Automatic catalog contract");}
 public static void main(String[] args)throws Exception{
  JSONObject row=new JSONObject().put("itemId","station_synthetic_n64").put("coverId","cover_synthetic_n64")
   .put("name","Jogo sintético").put("platform","n64").put("revision",5);
  StationCatalog plain=StationCatalog.fromVerifiedPayload(new JSONObject().put("revision",6).put("items",new JSONArray().put(row)));
  check(plain.items.get(0).description.isEmpty());
  row.put("metadata",new JSONObject().put("description","Sinopse do servidor.\nSegunda linha."));
  StationCatalog catalog=StationCatalog.fromVerifiedPayload(new JSONObject().put("revision",6).put("items",new JSONArray().put(row)));
  check(catalog.items.get(0).description.equals("Sinopse do servidor.\nSegunda linha."));
  check(StationPlatforms.resolve(catalog.items.get(0).platform).folder.equals("nintendo-64"));
  check(new StationPublication(catalog).rows.size()==1);
  StationCatalog cached=StationCatalog.fromVerifiedPayload(new JSONObject(new String(catalog.localPayload(),StandardCharsets.UTF_8)));
  check(cached.items.get(0).description.equals(catalog.items.get(0).description));
  row.put("metadata",new JSONObject().put("description","invalid\u0000text"));
  try{StationCatalog.fromVerifiedPayload(new JSONObject().put("revision",6).put("items",new JSONArray().put(row)));throw new AssertionError("NUL accepted");}catch(java.io.IOException expected){}
  System.out.println("PASS 6 N64, server synopsis, optional metadata, cache and malformed text checks");
 }
}
