"""Apply after refine_information_ui.py: durable human v3 departure, no implicit leave."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'java/netplay-src/org/emulationstation/frontend/netplay'
BASE = ROOT.parent / 'station-online-layout-r71-20261007/java/netplay-src/org/emulationstation/frontend/netplay/StationPresence.java'
PREVIOUS = ROOT.parent / 'station-pump-wakeup-r76-20261008/evidence/java-dex-build.json'

def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('Expected unique source anchor: ' + before[:80])
    return text.replace(before, after)

HELPER = r'''package org.emulationstation.frontend.netplay;

import java.util.UUID;

/** A human's exact departure target. Network/lifecycle events never create this intent. */
final class StationRoomLeaveIntent {
    static final String KEY="leaveMultiplayerIntent";
    enum Decision { LEAVE, ACKNOWLEDGED_ABSENT, HOLD_DIFFERENT_GENERATION }
    final String encoded,roomId,protocol,requestId;final long generation;
    private StationRoomLeaveIntent(String room,long generation,String protocol,String request){
        this.roomId=room;this.generation=generation;this.protocol=protocol;this.requestId=request;
        encoded=protocol+"|"+room+"|"+generation+"|"+request;
    }
    static StationRoomLeaveIntent human(String room,long generation,String protocol){
        StationRoomLeaveIntent value=parse(protocol+"|"+room+"|"+generation+"|"+UUID.randomUUID());
        if(value==null)throw new IllegalArgumentException("Invalid room departure");return value;
    }
    static StationRoomLeaveIntent parse(String text){
        if(text==null||text.length()>160)return null;String[] parts=text.split("\\|",-1);
        if(parts.length!=4||!"station-stream.v3".equals(parts[0])||!parts[1].matches("[0-9a-f]{32}")
                ||!parts[2].matches("[1-9][0-9]{0,18}")||!parts[3].matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))return null;
        try{long generation=Long.parseLong(parts[2]);return new StationRoomLeaveIntent(parts[1],generation,parts[0],parts[3]);}catch(NumberFormatException invalid){return null;}
    }
    /** Call only with own-room fields from an authenticated, verified snapshot. */
    Decision decide(String currentRoom,long currentGeneration,String currentProtocol){
        if(currentRoom==null||currentRoom.isEmpty()||!roomId.equals(currentRoom))return Decision.ACKNOWLEDGED_ABSENT;
        return generation==currentGeneration&&protocol.equals(currentProtocol)?Decision.LEAVE:Decision.HOLD_DIFFERENT_GENERATION;
    }
    /** A failed request, or an older completion racing a newer human intent, cannot clear it. */
    String afterResult(String currentlyStored,boolean verifiedSnapshot,String currentRoom,long currentGeneration,String currentProtocol){
        if(!encoded.equals(currentlyStored)||!verifiedSnapshot)return currentlyStored;
        return decide(currentRoom,currentGeneration,currentProtocol)==Decision.ACKNOWLEDGED_ABSENT?"":currentlyStored;
    }
}
'''

DEPARTURE = '''    private static JSONObject departureRoom(JSONObject snapshot)throws Exception {
        Object value=snapshot.get("room");if(value==JSONObject.NULL)return null;
        if(!(value instanceof JSONObject))throw new java.io.IOException("Invalid departure snapshot");
        JSONObject room=(JSONObject)value;
        if(!room.getString("roomId").matches("[0-9a-f]{32}")||room.getLong("generation")<1||!"station-stream.v3".equals(room.getString("recoveryProtocol")))throw new java.io.IOException("Invalid departure binding");
        return room;
    }
    private static void leaveMultiplayer(StationOnlineClient client,android.content.SharedPreferences profile,StationApi.Cancellation cancel)throws Exception {
        final String saved; synchronized(StationRoomLeaveIntent.class){saved=profile.getString(StationRoomLeaveIntent.KEY,"");}
        StationRoomLeaveIntent intent=StationRoomLeaveIntent.parse(saved);if(intent==null)return;
        JSONObject snapshot=client.multiplayer(StationOnlineClient.command("snapshot"),cancel);
        JSONObject room=departureRoom(snapshot);
        StationRoomLeaveIntent.Decision decision=intent.decide(room==null?null:room.optString("roomId"),room==null?0:room.optLong("generation"),room==null?"":room.optString("recoveryProtocol"));
        if(decision==StationRoomLeaveIntent.Decision.LEAVE){
            snapshot=client.multiplayer(StationOnlineClient.command("leave").put("requestId",intent.requestId).put("roomId",intent.roomId).put("generation",intent.generation),cancel);
            room=departureRoom(snapshot);
        }
        // Clear only on a fresh signed absence, never merely because a request was sent.
        synchronized(StationRoomLeaveIntent.class){
            String current=profile.getString(StationRoomLeaveIntent.KEY,"");
            String next=intent.afterResult(current,true,room==null?null:room.optString("roomId"),room==null?0:room.optLong("generation"),room==null?"":room.optString("recoveryProtocol"));
            if(!current.isEmpty()&&next.isEmpty())profile.edit().remove(StationRoomLeaveIntent.KEY).apply();
        }
    }
'''

def main():
    old = json.loads(PREVIOUS.read_text('utf8'))['sourceHashes']['netplay-src/org/emulationstation/frontend/netplay/StationPresence.java']
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != old:
        raise ValueError('The inherited StationPresence source is not the frozen R76 composition')
    presence = BASE.read_text('utf8')
    presence = replace_once(presence, '                long heartbeat=SystemClock.elapsedRealtime();failures=0;',
        '                leaveMultiplayer(c,profile,cancel);snapshot=c.compose(null);\n                long heartbeat=SystemClock.elapsedRealtime();failures=0;')
    presence = replace_once(presence,
        'if(SystemClock.elapsedRealtime()-heartbeat>=20000){snapshot=c.call(StationOnlineClient.command("heartbeat"),false,cancel);heartbeat=SystemClock.elapsedRealtime();}',
        'if(SystemClock.elapsedRealtime()-heartbeat>=20000){leaveMultiplayer(c,profile,cancel);snapshot=c.call(StationOnlineClient.command("heartbeat"),false,cancel);heartbeat=SystemClock.elapsedRealtime();}')
    presence = replace_once(presence, '    private static void invitations(Context context,JSONObject snapshot,int epoch){',
        DEPARTURE + '    private static void invitations(Context context,JSONObject snapshot,int epoch){')
    rooms_path = OUT / 'StationRoomsActivity.java'
    rooms = rooms_path.read_text('utf8')
    before = '        if(room()!=null)getSharedPreferences("station-online-profile",0).edit().putBoolean("leaveOnCatalog",true).apply();'
    after = '''        JSONObject leaving=room();
        if(leaving!=null){
            android.content.SharedPreferences profile=getSharedPreferences("station-online-profile",0);
            if("station-stream.v3".equals(leaving.optString("recoveryProtocol"))){
                StationRoomLeaveIntent intent=StationRoomLeaveIntent.human(leaving.optString("roomId"),leaving.optLong("generation"),leaving.optString("recoveryProtocol"));
                synchronized(StationRoomLeaveIntent.class){if(!profile.edit().putString(StationRoomLeaveIntent.KEY,intent.encoded).remove("leaveOnCatalog").commit()){status.setText("Não foi possível registrar a saída. Tente novamente.");return;}}
            }else profile.edit().putBoolean("leaveOnCatalog",true).apply();
        }'''
    if before in rooms:
        rooms = replace_once(rooms, before, after)
    elif after not in rooms:
        prior = after.replace('if(!profile.edit().putString(StationRoomLeaveIntent.KEY,intent.encoded).remove("leaveOnCatalog").commit()){status.setText("Não foi possível registrar a saída. Tente novamente.");return;}', 'profile.edit().putString(StationRoomLeaveIntent.KEY,intent.encoded).remove("leaveOnCatalog").apply();')
        if prior in rooms: rooms = replace_once(rooms, prior, after)
        else: raise ValueError('Unknown exitRooms implementation; review before applying')
    (OUT / 'StationRoomLeaveIntent.java').write_text(HELPER, encoding='utf8', newline='\n')
    (OUT / 'StationPresence.java').write_text(presence, encoding='utf8', newline='\n')
    rooms_path.write_text(rooms, encoding='utf8', newline='\n')
    print('Durable exact-generation v3 human departure applied; legacy flow preserved.')

if __name__ == '__main__': main()
