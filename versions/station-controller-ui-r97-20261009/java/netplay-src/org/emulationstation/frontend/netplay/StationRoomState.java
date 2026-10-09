package org.emulationstation.frontend.netplay;
import org.json.*;
import java.io.IOException;
/** Prevent stale concurrent command/event replies from restoring an old room or password. */
final class StationRoomState {
    private JSONObject current;
    synchronized JSONObject get(){return current;}
    synchronized boolean accept(JSONObject next)throws IOException,JSONException {
        String instance=next.getString("instance");long revision=next.getLong("revision");
        if(!instance.matches("[0-9a-f]{32}")||revision<0)throw new IOException("Invalid room revision");
        if(current!=null && instance.equals(current.getString("instance")) && revision<current.getLong("revision"))return false;
        if(current!=null && !instance.equals(current.getString("instance")))throw new IOException("Online server restarted; enter again");
        current=next;return true;
    }
    synchronized void reset(){current=null;}
}
