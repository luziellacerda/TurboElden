package org.emulationstation.frontend.netplay;

import org.json.JSONArray;
import org.json.JSONObject;

/** The actual R71 helper is compiled with this fixture; no Android or server is used. */
public final class StationRoomStartProtocolTest {
    private static int checks;
    private static final String HOST = "host-synthetic", GUEST = "guest-synthetic";
    private static void check(boolean value, String label) {
        checks++;
        if (!value) throw new AssertionError(label);
    }
    private static JSONObject snapshot(boolean v2, int count, int readyMask) throws Exception {
        JSONArray members = new JSONArray(), ready = new JSONArray();
        for (int i = 0; i < count; i++) members.put(i == 0 ? HOST : i == 1 ? GUEST : "extra-synthetic");
        if ((readyMask & 1) != 0) ready.put(HOST);
        if ((readyMask & 2) != 0) ready.put(GUEST);
        JSONObject room = new JSONObject().put("roomId", "room-synthetic").put("state", "waiting")
                .put("hostId", HOST).put("members", members).put("ready", ready);
        if (v2) room.put("recoveryProtocol", "station-stream.v2");
        return new JSONObject().put("selfId", HOST).put("room", room)
                .put("transports", new JSONArray().put(v2 ? "relay-wss-v2" : "relay-wss-v1"));
    }
    private static void blocked(JSONObject snapshot, String label) {
        check(!StationRoomStartState.reason(snapshot).isEmpty(), label);
    }
    public static void main(String[] args) throws Exception {
        blocked(null, "missing snapshot");
        blocked(new JSONObject(), "missing room");
        check(StationRoomStartState.transport(null).equals("relay-wss-v1"), "default transport is legacy");
        for (boolean v2 : new boolean[]{false, true}) {
            String selected = v2 ? "relay-wss-v2" : "relay-wss-v1";
            for (int count = 0; count <= 3; count++) {
                for (int mask = 0; mask < 4; mask++) {
                    JSONObject s = snapshot(v2, count, mask);
                    check(StationRoomStartState.reason(s).isEmpty() == (count == 2 && mask == 3),
                            selected + " requires exactly two members ready: " + count + "/" + mask);
                    check(StationRoomStartState.transport(s).equals(selected), "selected transport follows signed room");
                }
            }
            JSONObject s = snapshot(v2, 2, 3);
            check(StationRoomStartState.reason(s).isEmpty(), "one announced matching transport suffices");
            s.put("transports", new JSONArray().put("relay-wss-v1").put("relay-wss-v2"));
            check(StationRoomStartState.reason(s).isEmpty(), "both protocols announced");
            s.put("transports", new JSONArray().put(v2 ? "relay-wss-v1" : "relay-wss-v2"));
            blocked(s, "wrong protocol cannot authorize selected room");
            s.remove("transports");
            blocked(s, "missing transport cannot authorize start");
            s = snapshot(v2, 2, 3).put("selfId", GUEST);
            blocked(s, "guest cannot start");
            s.put("selfId", "");
            blocked(s, "missing self cannot start");
            s = snapshot(v2, 2, 3);
            s.getJSONObject("room").put("hostId", GUEST);
            blocked(s, "host flag follows ID");
            s = snapshot(v2, 2, 3);
            s.getJSONObject("room").put("members", new JSONArray().put(HOST).put(HOST));
            blocked(s, "duplicate member is not a pair");
            s = snapshot(v2, 2, 3);
            s.getJSONObject("room").put("members", new JSONArray().put(GUEST).put("third"));
            blocked(s, "host must belong to the room");
            s = snapshot(v2, 2, 3);
            s.getJSONObject("room").put("members", new JSONArray().put("").put(GUEST));
            blocked(s, "empty member is not a pair");
            s = snapshot(v2, 2, 3);
            s.getJSONObject("room").put("members", new JSONArray().put(GUEST).put(HOST));
            check(StationRoomStartState.reason(s).isEmpty(), "host can be the second member");
            s.getJSONObject("room").put("ready", new JSONArray().put(HOST).put("third"));
            blocked(s, "unrelated ready ID cannot replace guest confirmation");
            s.getJSONObject("room").remove("ready");
            blocked(s, "missing confirmations");
            for (String phase : new String[]{"starting", "connecting", "waiting-reconnect", "synchronizing", "playing", "unrecoverable", ""}) {
                s = snapshot(v2, 2, 3);
                s.getJSONObject("room").put("state", phase);
                blocked(s, "cannot start another match in phase " + phase);
            }
        }
        System.out.println("StationRoomStartProtocolTest: " + checks + " checks passed");
    }
}
