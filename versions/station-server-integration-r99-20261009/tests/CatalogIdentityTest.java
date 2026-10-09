import org.emulationstation.frontend.station.StationCatalog;import org.json.*;
public class CatalogIdentityTest {
 static int checks;static void check(boolean x){checks++;if(!x)throw new AssertionError("check "+checks);}
 static JSONObject payload(String scheme)throws Exception {JSONObject row=new JSONObject().put("itemId","testgame").put("coverId","testgame").put("name","Jogo").put("platform","psx").put("revision",1).put("contentSha256",new String(new char[64]).replace('\0','a'));if(scheme!=null)row.put("contentIdentityScheme",scheme);return new JSONObject().put("revision",1).put("items",new JSONArray().put(row));}
 public static void main(String[] args)throws Exception{
  for(String scheme:new String[]{null,"cue-set-v1","wiiu-set-v1"}){StationCatalog c=StationCatalog.fromVerifiedPayload(payload(scheme));check(c.items.get(0).contentIdentityScheme.equals(scheme==null?"":scheme));StationCatalog copy=StationCatalog.fromVerifiedPayload(new JSONObject(new String(c.localPayload(),"UTF-8")));check(copy.items.get(0).contentIdentityScheme.equals(c.items.get(0).contentIdentityScheme));}
  for(String scheme:new String[]{"", "unknown"}){boolean rejected=false;try{StationCatalog.fromVerifiedPayload(payload(scheme));}catch(java.io.IOException ex){rejected=true;}check(rejected);}
  JSONObject broken=payload("cue-set-v1");broken.getJSONArray("items").getJSONObject(0).remove("contentSha256");boolean rejected=false;try{StationCatalog.fromVerifiedPayload(broken);}catch(java.io.IOException ex){rejected=true;}check(rejected);
  System.out.println("{\"passed\":true,\"checks\":"+checks+"}");
 }
}