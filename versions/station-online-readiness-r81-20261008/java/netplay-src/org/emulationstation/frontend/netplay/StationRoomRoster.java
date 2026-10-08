package org.emulationstation.frontend.netplay;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONObject;

/** Presentation only. Feed snapshots already accepted by StationRoomState after API verification. */
public final class StationRoomRoster {
    public static final int MAX_CACHED_NAMES = 256;
    public static final int ROOM_SLOTS = 2;
    public static final String NAME_UNAVAILABLE = "Nome indisponível";
    public static final String EMPTY_SLOT = "Aguardando jogador";

    /** position/label follow room.members, and do not identify controller ports or host order. */
    public static final class Row {
        public final int position;
        public final String peerId, name, label;
        public final boolean occupied, nameKnown, self, host, ready;

        private Row(int position, String peerId, String name, boolean nameKnown,
                    boolean self, boolean host, boolean ready) {
            this.position = position;
            this.peerId = peerId;
            this.name = name;
            this.label = "Jogador " + position;
            this.occupied = !peerId.isEmpty();
            this.nameKnown = nameKnown;
            this.self = self;
            this.host = host;
            this.ready = ready;
        }
    }

    private final LinkedHashMap<String, String> names =
            new LinkedHashMap<String, String>(32, 0.75f, true);
    private String instance = "";
    private long revision = -1;

    /** Call alongside StationRoomState.reset(), including reconnect/account/session changes. */
    public synchronized void reset() {
        names.clear();
        instance = "";
        revision = -1;
    }

    /** Observe every accepted page, even when that page is not painted. Cache names only. */
    public synchronized void observe(JSONObject snapshot) {
        if (snapshot == null) return;
        String nextInstance = string(snapshot.opt("instance"));
        long nextRevision = snapshot.optLong("revision", -1);
        if (!nextInstance.matches("[0-9a-f]{32}") || nextRevision < 0) {
            reset();
            return;
        }
        if (!nextInstance.equals(instance)) {
            reset();
            instance = nextInstance;
        }
        if (nextRevision < revision) return;
        revision = nextRevision;
        JSONArray peers = snapshot.optJSONArray("peers");
        for (int i = 0; peers != null && i < peers.length(); i++) {
            JSONObject peer = peers.optJSONObject(i);
            if (peer == null) continue;
            String id = string(peer.opt("peerId"));
            String name = nickname(peer);
            if (id.isEmpty() || name.isEmpty()) continue;
            names.put(id, name);
            while (names.size() > MAX_CACHED_NAMES)
                names.remove(names.keySet().iterator().next());
        }
        // This field belongs to our signed room and is independent of social pagination.
        JSONObject room = snapshot.optJSONObject("room");
        JSONArray profiles = ownProfiles(snapshot);
        JSONArray members = room == null ? null : room.optJSONArray("members");
        for (int i = 0; profiles != null && members != null && i < members.length(); i++) {
            String id = string(members.opt(i));
            String name = profileName(profiles, id);
            if (id.isEmpty() || name.isEmpty()) continue;
            names.put(id, name);
            while (names.size() > MAX_CACHED_NAMES)
                names.remove(names.keySet().iterator().next());
        }
    }

    /** Current signed page wins; cached names imply neither presence nor readiness. */
    public synchronized String resolveName(JSONObject snapshot, String peerId) {
        observe(snapshot);
        String name = knownName(snapshot, peerId);
        return name.isEmpty() ? NAME_UNAVAILABLE : name;
    }

    /** Real members plus empty visual places up to two. Unexpected extra members stay visible. */
    public synchronized List<Row> rows(JSONObject snapshot) {
        observe(snapshot);
        JSONObject room = snapshot == null ? null : snapshot.optJSONObject("room");
        if (room == null) return Collections.emptyList();
        if("station-stream.v3".equals(room.optString("recoveryProtocol"))){
            int capacity=room.optInt("capacity",0);if(capacity<2||capacity>4)return Collections.emptyList();
            JSONArray roster=room.optJSONArray("roster");ArrayList<Row> result=new ArrayList<Row>();String self=snapshot.optString("selfId");
            for(int slot=1;slot<=capacity;slot++){
                JSONObject player=null;for(int i=0;roster!=null&&i<roster.length();i++){JSONObject p=roster.optJSONObject(i);if(p!=null&&p.optInt("slot")==slot){if(player!=null)return Collections.emptyList();player=p;}}
                if(player==null){result.add(new Row(slot,"",EMPTY_SLOT,false,false,false,false));continue;}
                String id=player.optString("peerId"),name=player.optString("nickname");result.add(new Row(slot,id,name.isEmpty()?NAME_UNAVAILABLE:name,!name.isEmpty(),self.equals(id),slot==1,player.optBoolean("ready")));
            }
            return Collections.unmodifiableList(result);
        }
        JSONArray members = room.optJSONArray("members");
        JSONArray ready = room.optJSONArray("ready");
        String self = string(snapshot.opt("selfId")), host = string(room.opt("hostId"));
        int count = Math.max(ROOM_SLOTS, members == null ? 0 : members.length());
        ArrayList<Row> rows = new ArrayList<Row>(count);
        HashSet<String> seen = new HashSet<String>();
        for (int i = 0; i < count; i++) {
            String id = members == null ? "" : string(members.opt(i));
            if (!id.isEmpty() && !seen.add(id)) id = "";
            if (id.isEmpty()) {
                rows.add(new Row(i + 1, "", EMPTY_SLOT, false, false, false, false));
                continue;
            }
            String name = knownName(snapshot, id);
            rows.add(new Row(i + 1, id, name.isEmpty() ? NAME_UNAVAILABLE : name,
                    !name.isEmpty(), id.equals(self), id.equals(host), contains(ready, id)));
        }
        return Collections.unmodifiableList(rows);
    }

    private String knownName(JSONObject snapshot, String peerId) {
        if (snapshot == null || peerId == null || peerId.isEmpty()) return "";
        JSONObject room = snapshot.optJSONObject("room");
        if (room != null && contains(room.optJSONArray("members"), peerId)) {
            String profile = profileName(ownProfiles(snapshot), peerId);
            if (!profile.isEmpty()) return profile;
        }
        JSONArray peers = snapshot.optJSONArray("peers");
        String current = "";
        for (int i = 0; peers != null && i < peers.length(); i++) {
            JSONObject peer = peers.optJSONObject(i);
            if (peer != null && peerId.equals(string(peer.opt("peerId")))) {
                String name = nickname(peer);
                if (!name.isEmpty()) current = name;
            }
        }
        if (!current.isEmpty()) return current;
        if (!instance.equals(string(snapshot.opt("instance"))) || instance.isEmpty()) return "";
        String cached = names.get(peerId);
        return cached == null ? "" : cached;
    }

    private JSONArray ownProfiles(JSONObject snapshot) {
        if (snapshot == null || instance.isEmpty()
                || !instance.equals(string(snapshot.opt("instance")))
                || snapshot.optLong("revision", -1) < revision
                || !contains(snapshot.optJSONArray("roomCapabilities"), "own-room-member-profiles-v1"))
            return null;
        JSONObject room = snapshot.optJSONObject("room");
        String self = string(snapshot.opt("selfId"));
        if (room == null || self.isEmpty() || !contains(room.optJSONArray("members"), self)) return null;
        return room.optJSONArray("memberProfiles");
    }

    private static String profileName(JSONArray profiles, String id) {
        String result = "";
        boolean found = false;
        for (int i = 0; profiles != null && i < profiles.length(); i++) {
            JSONObject profile = profiles.optJSONObject(i);
            if (profile == null || !id.equals(string(profile.opt("peerId")))) continue;
            if (found) return ""; // An ambiguous record cannot replace another participant's name.
            found = true;
            result = nickname(profile);
        }
        return result;
    }

    private static String nickname(JSONObject peer) {
        String name = string(peer.opt("nickname"));
        return name.trim().isEmpty() ? "" : name;
    }

    private static String string(Object value) {
        return value instanceof String ? (String) value : "";
    }

    private static boolean contains(JSONArray values, String id) {
        for (int i = 0; values != null && i < values.length(); i++)
            if (id.equals(string(values.opt(i)))) return true;
        return false;
    }
}
