package org.emulationstation.frontend.netplay;
import org.json.*;
/** Optional additions to the existing verified snapshot, never guessed from HTTP success. */
final class StationSocial {
 static boolean supports(JSONObject s,String name){JSONArray a=s==null?null:s.optJSONArray("socialCapabilities");if(a!=null)for(int i=0;i<a.length();i++)if(name.equals(a.optString(i)))return true;return false;}
 static boolean conversation(JSONObject m,String self,String other){return m!=null&&((self.equals(m.optString("fromPeerId"))&&other.equals(m.optString("toPeerId")))||(other.equals(m.optString("fromPeerId"))&&self.equals(m.optString("toPeerId"))));}
 static JSONArray messages(JSONObject s,String other){JSONArray result=new JSONArray(),a=s==null?null:s.optJSONArray("directMessages");String self=s==null?"":s.optString("selfId");if(a!=null)for(int i=0;i<a.length();i++){JSONObject m=a.optJSONObject(i);if(conversation(m,self,other))result.put(m);}return result;}
 static boolean requested(JSONObject s,String room){JSONArray a=s==null?null:s.optJSONArray("sentJoinRequests");if(a!=null)for(int i=0;i<a.length();i++){JSONObject r=a.optJSONObject(i);if(r!=null&&room.equals(r.optString("roomId")))return true;}return false;}
 static String last(JSONArray a){JSONObject m=a==null||a.length()==0?null:a.optJSONObject(a.length()-1);return m==null?"":m.optString("messageId");}
}
