package org.emulationstation.frontend.netplay;
import org.json.JSONArray;
import org.json.JSONObject;

/** A visible room must be the acknowledged room for this host and selected item. */
final class StationRoomCreation {
    static boolean confirmed(JSONObject snapshot,String itemId){
        if(snapshot==null||itemId==null||itemId.isEmpty())return false;
        JSONObject room=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");
        if(room==null||self.isEmpty()||room.optString("roomId").isEmpty()||
                !itemId.equals(room.optString("itemId"))||!self.equals(room.optString("hostId")))return false;
        JSONArray members=room.optJSONArray("members");
        for(int i=0;members!=null&&i<members.length();i++)if(self.equals(members.optString(i)))return true;
        return false;
    }
}
