package org.emulationstation.frontend.netplay;
import org.json.JSONObject;
/** Host starts only after both are ready; guest follows the server connecting state. */
final class StationLaunchPolicy {
 static boolean eligible(String state,boolean host){return "connecting".equals(state)||("starting".equals(state)&&host);}
 static boolean eligible(JSONObject room,boolean host){if("station-stream.v3".equals(room.optString("recoveryProtocol")))return "relay-wss-v3".equals(room.optString("transport"))&&!room.optBoolean("recoveryStarted",false)&&room.optLong("generation")>0&&("starting".equals(room.optString("state"))||"synchronizing".equals(room.optString("state"))||"waiting-reconnect".equals(room.optString("state")));if("station-stream.v2".equals(room.optString("recoveryProtocol"))&&"relay-wss-v2".equals(room.optString("transport"))){if(room.optBoolean("recoveryStarted",false)||"unrecoverable".equals(room.optString("state")))return false;return host||room.optBoolean("hostListening",false);}return eligible(room.optString("state"),host);}
 static String key(JSONObject room){return room.optString("roomId")+":"+room.optLong("generation");}
}
