package org.emulationstation.frontend.netplay;

import java.io.IOException;
import org.json.JSONObject;
import org.emulationstation.frontend.station.StationApi;

/** Only the explicit human event 4 calls this. Snapshot/transport/lifecycle
 * events cannot manufacture departure authority. No blind mutation retry. */
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
        try{confirmedAbsent(client.multiplayer(request(room,generation),cancel),room);return;}
        catch(StationApi.Failure rejected){
            // A rejected generation is evidence of no mutation. Network failures,
            // timeouts, license/profile rejection and generic 409 never reach here.
            if(rejected.status!=409||!"STATION_MULTIPLAYER_GENERATION_MISMATCH".equals(rejected.code)||cancel.cancelled())throw rejected;
        }
        // StationOnlineClient/API verifies authentication and the signed response.
        // 'room' denotes this session's OWN membership, not a room-list entry.
        JSONObject snapshot=client.multiplayer(StationOnlineClient.command("snapshot"),cancel);
        Object value=snapshot.get("room");
        if(value==JSONObject.NULL)return; // Already absent: never leave another room.
        if(!(value instanceof JSONObject))throw new IOException("HUMAN_DEPARTURE_SNAPSHOT");
        JSONObject current=(JSONObject)value;
        if(!room.equals(current.getString("roomId")))return;
        for(String key:IDENTITY){String original=binding.getString(key);
            if(original.isEmpty()||!original.equals(current.getString(key)))throw new IOException("HUMAN_DEPARTURE_IDENTITY");}
        long fresh=current.getLong("generation");
        if(fresh<=generation||cancel.cancelled())throw new IOException("HUMAN_DEPARTURE_STALE_SNAPSHOT");
        // Exactly one reissued mutation with a fresh idempotency key, still for
        // the same verified game/profile/runtime and same human departure target.
        confirmedAbsent(client.multiplayer(request(room,fresh),cancel),room);
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
