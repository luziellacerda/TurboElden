package org.emulationstation.frontend.netplay;
import org.json.*;

public final class StationRoomCreationTest {
    private static int checks;
    private static void check(boolean value,String detail){checks++;if(!value)throw new AssertionError(detail);}
    private static JSONObject room()throws Exception{return new JSONObject("{\"selfId\":\"host-a\",\"room\":{\"roomId\":\"r-a\",\"itemId\":\"game-a\",\"hostId\":\"host-a\",\"members\":[\"host-a\"]}}");}
    public static void main(String[] args)throws Exception{
        check(StationRoomCreation.confirmed(room(),"game-a"),"Acknowledged matching room can open");
        check(!StationRoomCreation.confirmed(null,"game-a"),"No snapshot cannot open empty lobby");
        check(!StationRoomCreation.confirmed(new JSONObject(),"game-a"),"Empty response rejected");
        check(!StationRoomCreation.confirmed(room(),null),"Missing selection rejected");
        check(!StationRoomCreation.confirmed(room(),""),"Empty selection rejected");
        check(!StationRoomCreation.confirmed(room(),"game-b"),"Old game's room cannot acknowledge new selection");
        JSONObject s=room();s.put("room",JSONObject.NULL);check(!StationRoomCreation.confirmed(s,"game-a"),"Empty room rejected");
        s=room();s.put("selfId","");check(!StationRoomCreation.confirmed(s,"game-a"),"Missing host identity rejected");
        s=room();s.getJSONObject("room").put("roomId","");check(!StationRoomCreation.confirmed(s,"game-a"),"Missing room id rejected");
        s=room();s.getJSONObject("room").put("hostId","other");check(!StationRoomCreation.confirmed(s,"game-a"),"Different host rejected");
        s=room();s.getJSONObject("room").put("members",new JSONArray());check(!StationRoomCreation.confirmed(s,"game-a"),"Not a member rejected");
        s=room();s.getJSONObject("room").put("members",new JSONArray().put("other"));check(!StationRoomCreation.confirmed(s,"game-a"),"Another member alone rejected");
        s=room();s.getJSONObject("room").getJSONArray("members").put("guest-b");check(StationRoomCreation.confirmed(s,"game-a"),"Acknowledgment remains valid after guest joins");
        check(!StationRoomCreation.confirmed(room(),"game-a "),"Exact item id required");
        System.out.println("PASS "+checks+" room creation acknowledgment checks");
    }
}
