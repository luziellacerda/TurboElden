package org.emulationstation.frontend.netplay;
import org.json.*;
public class StationSocialTest {
 static int n;static void check(boolean b){n++;if(!b)throw new AssertionError("check "+n);}
 public static void main(String[] a)throws Exception{
 JSONObject s=new JSONObject().put("selfId","self");check(!StationSocial.supports(s,"direct-chat-v1"));check(!StationSocial.supports(null,"direct-chat-v1"));
 s.put("socialCapabilities",new JSONArray().put("direct-chat-v1").put("join-request-v1"));check(StationSocial.supports(s,"direct-chat-v1"));check(!StationSocial.supports(s,"whatsapp"));
 JSONArray all=new JSONArray();for(int i=0;i<100;i++){all.put(new JSONObject().put("messageId","id"+i).put("fromPeerId",i%2==0?"self":"other").put("toPeerId",i%2==0?"other":"self").put("text","Message "+i));}
 all.put(new JSONObject().put("messageId","private").put("fromPeerId","third").put("toPeerId","self"));s.put("directMessages",all);
 JSONArray selected=StationSocial.messages(s,"other");check(selected.length()==100);check(StationSocial.last(selected).equals("id99"));for(int i=0;i<selected.length();i++)check(!selected.getJSONObject(i).optString("messageId").equals("private"));
 check(StationSocial.messages(s,"unknown").length()==0);check(StationSocial.messages(null,"other").length()==0);check(!StationSocial.requested(s,"room"));s.put("sentJoinRequests",new JSONArray().put(new JSONObject().put("roomId","room")));check(StationSocial.requested(s,"room"));check(!StationSocial.requested(s,"else"));
 check(StationSocial.last(null).isEmpty());check(!StationSocial.conversation(null,"a","b"));
 System.out.println("PASS "+n+" social client checks");
 }
}
