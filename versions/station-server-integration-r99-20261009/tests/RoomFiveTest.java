package org.emulationstation.frontend.netplay;
import org.json.*;
public final class RoomFiveTest {
 static int checks; static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
 static JSONObject room(int count)throws Exception{
  JSONArray roster=new JSONArray(),members=new JSONArray(),allowed=new JSONArray();
  for(int n=2;n<=count;n++)allowed.put(n);
  for(int n=1;n<=count;n++){roster.put(new JSONObject().put("peerId","p"+n).put("nickname","Jogador "+n).put("slot",n).put("ready",true));members.put("p"+n);}
  return new JSONObject().put("selfId","p1").put("transports",new JSONArray().put("relay-wss-v3")).put("room",new JSONObject().put("hostId","p1").put("state","waiting").put("recoveryProtocol","station-stream.v3").put("capacity",count).put("roster",roster).put("members",members).put("allowedPlayerCounts",allowed));
 }
 public static void main(String[]args)throws Exception{
  for(int count=2;count<=5;count++){
   JSONObject s=room(count),r=s.getJSONObject("room");check(StationRoomStartState.reason(s).isEmpty());
   check(new StationRoomRoster().rows(s).size()==count);
   for(int slot=1;slot<=count;slot++){
    r.getJSONArray("roster").getJSONObject(slot-1).put("ready",false);check(!StationRoomStartState.reason(s).isEmpty());
    r.getJSONArray("roster").getJSONObject(slot-1).put("ready",true);check(StationRoomStartState.reason(s).isEmpty());
   }
   s.put("selfId","p2");check(!StationRoomStartState.reason(s).isEmpty());s.put("selfId","p1");
   r.getJSONArray("roster").getJSONObject(count-1).put("slot",1);check(!StationRoomStartState.reason(s).isEmpty());
   check(new StationRoomRoster().rows(s).isEmpty());
  }
  JSONObject s=room(6);check(!StationRoomStartState.reason(s).isEmpty());check(new StationRoomRoster().rows(s).isEmpty());
  s=room(5);s.getJSONObject("room").put("allowedPlayerCounts",new JSONArray().put(2).put(3).put(4));check(!StationRoomStartState.reason(s).isEmpty());
  System.out.println("{\"passed\":true,\"checks\":"+checks+"}");
 }
}