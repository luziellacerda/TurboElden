package org.emulationstation.frontend.netplay;

import java.io.IOException;
import java.io.EOFException;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import org.json.JSONObject;
import org.emulationstation.frontend.station.StationApi;

/** Only the explicit human event 4 calls this. Snapshot/transport/lifecycle
 * events cannot manufacture departure authority. One exact idempotent replay
 * requires an authenticated snapshot of the same room, identity and generation. */
final class StationHumanDeparture {
    private static final String[] IDENTITY={"roomId","recoveryProtocol","itemId",
        "engineId","coreSha256","runtimeSha256","contentSha256","profileId","profileSha256"};
    private StationHumanDeparture(){}
    static void leave(StationOnlineClient client,JSONObject binding,StationApi.Cancellation cancel)throws Exception {
        if(binding==null||!"station-stream.v3".equals(binding.getString("recoveryProtocol")))throw new IOException("HUMAN_DEPARTURE_BINDING");
        long generation=binding.getLong("generation");
        if(generation<1)throw new IOException("HUMAN_DEPARTURE_GENERATION");
        String room=binding.getString("roomId");
        if(!room.matches("[0-9a-f]{32}"))throw new IOException("HUMAN_DEPARTURE_ROOM");
        // Keep this JSONObject: multiplayer() adds its fixed paging fields. Reusing
        // the object preserves both requestId and request body on an uncertain send.
        JSONObject original=request(room,generation);
        try{confirmedAbsent(client.multiplayer(original,cancel),room);return;}
        catch(StationApi.Failure rejected){
            // A rejected generation is evidence of no mutation. Network failures,
            // timeouts, license/profile rejection and generic 409 never reach here.
            if(rejected.status!=409||!"STATION_MULTIPLAYER_GENERATION_MISMATCH".equals(rejected.code)||cancel.cancelled())throw rejected;
            // A definite generation rejection cannot have mutated membership.
            JSONObject current=ownRoom(client,room,cancel);
            if(current==null)return;
            sameIdentity(binding,current);
            long fresh=current.getLong("generation");
            if(fresh<=generation||cancel.cancelled())throw new IOException("HUMAN_DEPARTURE_STALE_SNAPSHOT");
            // Only this proven rejection permits a new generation/requestId.
            confirmedAbsent(client.multiplayer(request(room,fresh),cancel),room);
            return;
        }
        catch(Exception uncertain){
            if(cancel.cancelled()||!n64(binding)||!transportUncertain(uncertain))throw uncertain;
            JSONObject current=ownRoom(client,room,cancel);
            if(current==null)return; // Own membership no longer contains the target.
            sameIdentity(binding,current);
            if(current.getLong("generation")!=generation||cancel.cancelled())
                throw new IOException("HUMAN_DEPARTURE_CHANGED_GENERATION");
            // One replay only, of the exact operation already sent. The server's
            // requestId receipt makes a lost response safe to repeat.
            confirmedAbsent(client.multiplayer(original,cancel),room);
            return;
        }
    }
    private static boolean transportUncertain(Exception failure){
        return failure instanceof StationApi.Offline||failure instanceof SocketTimeoutException
            ||failure instanceof SocketException||failure instanceof EOFException
            ||failure instanceof UnknownHostException;
    }
    private static boolean n64(JSONObject binding){
        // Engine identity comes from the signed launch binding, never a game title.
        return binding.optString("engineId").matches("mupen64plus-ae-[0-9a-f]{8}-n64-v3-[0-9a-f]{12}");
    }
    // StationOnlineClient/API verifies authentication and the signed response.
    // 'room' denotes this session's OWN membership, not a room-list entry.
    private static JSONObject ownRoom(StationOnlineClient client,String room,StationApi.Cancellation cancel)throws Exception {
        JSONObject snapshot=client.multiplayer(StationOnlineClient.command("snapshot"),cancel);
        Object value=snapshot.get("room");
        if(value==JSONObject.NULL)return null;
        if(!(value instanceof JSONObject))throw new IOException("HUMAN_DEPARTURE_SNAPSHOT");
        JSONObject current=(JSONObject)value;
        return room.equals(current.getString("roomId"))?current:null;
    }
    private static void sameIdentity(JSONObject binding,JSONObject current)throws Exception {
        for(String key:IDENTITY){String original=binding.getString(key);
            if(original.isEmpty()||!original.equals(current.getString(key)))throw new IOException("HUMAN_DEPARTURE_IDENTITY");}
    }
    private static JSONObject request(String room,long generation)throws Exception {
        return StationOnlineClient.command("leave").put("roomId",room).put("generation",generation);
    }
    private static void confirmedAbsent(JSONObject snapshot,String target)throws Exception {
        Object value=snapshot.get("room");
        if(value==JSONObject.NULL)return;
        if(!(value instanceof JSONObject)||target.equals(((JSONObject)value).getString("roomId")))throw new IOException("HUMAN_DEPARTURE_UNCONFIRMED");
    }
}
