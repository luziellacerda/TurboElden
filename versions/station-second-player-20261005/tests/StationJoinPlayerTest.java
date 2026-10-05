package org.emulationstation.frontend.netplay;

import org.json.*;

/** Real signed-snapshot shapes for the two separate one-player rooms reported by the operator. */
public final class StationJoinPlayerTest {
    private static int checks;
    private static final String SELF="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",OTHER="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
    private static final String OWN="cccccccccccccccccccccccccccccccc",TARGET="dddddddddddddddddddddddddddddddd";
    private static final String ITEM="station_eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";
    private static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    private static JSONObject publicRoom(String phase,int players)throws Exception{
        return new JSONObject().put("roomId",TARGET).put("itemId",ITEM).put("hostId",OTHER)
            .put("state",phase).put("players",players).put("maximumPlayers",2);
    }
    private static JSONObject own(String phase,boolean guest)throws Exception{
        JSONArray members=new JSONArray().put(SELF);if(guest)members.put(OTHER);
        return new JSONObject().put("roomId",OWN).put("itemId",ITEM).put("hostId",SELF)
            .put("state",phase).put("members",members);
    }
    private static JSONObject lobby(JSONObject target)throws Exception{
        return new JSONObject().put("instance",OWN).put("revision",12).put("selfId",SELF)
            .put("peers",new JSONArray().put(new JSONObject().put("peerId",SELF).put("nickname","Eu").put("status","online"))
                .put(new JSONObject().put("peerId",OTHER).put("nickname","Primeiro telefone").put("status","in-room")))
            .put("rooms",new JSONArray().put(target));
    }
    private static StationPlayerModel model(JSONObject s){return StationPlayerModel.read(s,OTHER,"Anterior",null);}
    public static void main(String[] args)throws Exception{
        JSONObject s=lobby(publicRoom("waiting",1));StationPlayerModel m=model(s);
        check(m.canJoin&&!m.canInvite,"guest can enter the existing host room without creating another room");
        check(m.joinRoomId.equals(TARGET)&&m.joinItemId.equals(ITEM),"join uses the actual published room and game");
        s.put("room",own("waiting",false));m=model(s);
        check(StationPlayerModel.soloWaitingRoom(s)&&m.canJoin,"separate solo room offers entry with user confirmation");
        check(m.ownedRoom.optString("roomId").equals(OWN),"current room retained for confirmation");
        check(!StationPlayerModel.read(s,SELF,"Eu",ITEM).canJoin,"no self join");
        s.put("room",own("waiting",true));check(!model(s).canJoin,"do not offer an automatic departure with another participant");
        for(String phase:new String[]{"starting","connecting","unknown"}){
            s.put("room",own(phase,false));check(!StationPlayerModel.soloWaitingRoom(s)&&!model(s).canJoin,"do not switch a running or unknown room: "+phase);
        }
        s=lobby(publicRoom("waiting",2));check(!model(s).canJoin,"full destination");
        for(String phase:new String[]{"starting","connecting","unknown"})check(!model(lobby(publicRoom(phase,1))).canJoin,"destination unavailable: "+phase);
        for(String key:new String[]{"players","maximumPlayers","roomId","itemId"}){
            JSONObject r=publicRoom("waiting",1);r.remove(key);check(!model(lobby(r)).canJoin,"missing authoritative field: "+key);
        }
        s=lobby(publicRoom("waiting",1));s.put("peers",new JSONArray());check(!model(s).canJoin,"absence from the page is not fabricated presence");
        s=lobby(publicRoom("waiting",1));s.getJSONArray("peers").getJSONObject(1).put("status","future");check(!model(s).canJoin,"unknown peer state");
        s=lobby(publicRoom("waiting",1));JSONObject joined=own("waiting",true).put("roomId",TARGET).put("hostId",OTHER);s.put("room",joined);
        m=model(s);check(!m.canJoin&&!m.canInvite&&m.roomItemId.equals(ITEM),"already sharing the same room");
        System.out.println("PASS "+checks+" checks: guest entry, two solo rooms, shared membership and unavailable destinations");
    }
}
