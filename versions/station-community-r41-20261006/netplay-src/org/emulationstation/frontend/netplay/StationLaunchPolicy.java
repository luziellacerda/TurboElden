package org.emulationstation.frontend.netplay;
import org.json.JSONObject;
/** Host starts only after both are ready; guest follows the server connecting state. */
final class StationLaunchPolicy {
 static boolean eligible(String state,boolean host){return "connecting".equals(state)||("starting".equals(state)&&host);}
 static String key(JSONObject room){return room.optString("roomId")+":"+room.optLong("generation");}
}
