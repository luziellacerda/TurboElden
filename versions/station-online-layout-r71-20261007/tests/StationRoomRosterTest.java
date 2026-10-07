package org.emulationstation.frontend.netplay;

import java.util.List;
import org.json.JSONArray;
import org.json.JSONObject;

/** Offline fixtures use the existing snapshot fields; no Android or network is required. */
public final class StationRoomRosterTest {
    private static int checks;
    private static final String INSTANCE = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    private static final String OTHER_INSTANCE = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
    private static final String SELF = "11111111111111111111111111111111";
    private static final String GUEST = "22222222222222222222222222222222";
    private static final String OTHER = "33333333333333333333333333333333";

    private static void check(boolean result, String message) {
        checks++;
        if (!result) throw new AssertionError(message);
    }
    private static JSONObject peer(String id, String name) throws Exception {
        return new JSONObject().put("peerId", id).put("nickname", name);
    }
    private static JSONArray ids(String... ids) { return new JSONArray(java.util.Arrays.asList(ids)); }
    private static JSONObject room(String host, JSONArray members, JSONArray ready) throws Exception {
        return new JSONObject().put("roomId", "test-room").put("hostId", host)
                .put("state", "waiting").put("members", members).put("ready", ready);
    }
    private static JSONObject snapshot(long revision, JSONArray peers, JSONObject room) throws Exception {
        return new JSONObject().put("instance", INSTANCE).put("revision", revision).put("page", 0)
                .put("selfId", SELF).put("peers", peers).put("room", room == null ? JSONObject.NULL : room);
    }
    private static JSONArray people() throws Exception {
        // Deliberately opposite to room order, with an unrelated peer first.
        return new JSONArray().put(peer(OTHER, "Extra")).put(peer(GUEST, "Luíza 🎮")).put(peer(SELF, "João"));
    }
    private static JSONObject pair(long revision, JSONArray peers) throws Exception {
        return snapshot(revision, peers, room(SELF, ids(SELF, GUEST), ids(SELF, GUEST)));
    }
    private static void testBinding() throws Exception {
        StationRoomRoster model = new StationRoomRoster();
        JSONObject s = pair(1, people());
        List<StationRoomRoster.Row> rows = model.rows(s);
        check(rows.size() == 2, "two room members, unrelated peer not added");
        check(rows.get(0).peerId.equals(SELF), "member order, not peers order");
        check(rows.get(1).peerId.equals(GUEST), "second ID binding");
        check(rows.get(0).name.equals("João"), "first actual name");
        check(rows.get(1).name.equals("Luíza 🎮"), "second actual Unicode name");
        check(rows.get(0).label.equals("Jogador 1"), "room position first label");
        check(rows.get(1).label.equals("Jogador 2"), "room position second label");
        check(rows.get(0).occupied && rows.get(1).occupied, "both real rows occupied");
        check(rows.get(0).nameKnown && rows.get(1).nameKnown, "both names observed");
        check(rows.get(0).self && !rows.get(1).self, "self by ID only");
        check(rows.get(0).host && !rows.get(1).host, "host by ID only");
        check(rows.get(0).ready && rows.get(1).ready, "ready by membership");
        check(model.resolveName(s, GUEST).equals(rows.get(1).name), "shared name resolution");
        List<StationRoomRoster.Row> confirmation = model.rows(s);
        check(confirmation.get(0).name.equals(rows.get(0).name)
                && confirmation.get(1).name.equals(rows.get(1).name), "card and confirmation model agree");
        s.put("room", room(SELF, ids(GUEST, SELF), ids(GUEST)));
        rows = model.rows(s);
        check(rows.get(0).peerId.equals(GUEST) && !rows.get(0).host, "guest can occupy first room position");
        check(rows.get(1).host && rows.get(1).position == 2, "host never forced into first position");
        check(rows.get(0).ready && !rows.get(1).ready, "ready not copied by index");
        s.put("selfId", GUEST);
        rows = model.rows(s);
        check(rows.get(0).self && !rows.get(1).self, "guest view marks actual self");
        check(!rows.get(0).host && rows.get(1).host, "guest view retains real host");
        try { rows.clear(); throw new AssertionError("mutable rows"); }
        catch (UnsupportedOperationException expected) { checks++; }
        s.put("room", room(OTHER, ids(SELF, GUEST), ids(OTHER)));
        rows = model.rows(s);
        check(!rows.get(0).host && !rows.get(1).host, "unlisted host not assigned to another member");
        check(!rows.get(0).ready && !rows.get(1).ready, "unrelated ready ID cannot mark room members");
        for (int mask = 0; mask < 4; mask++) {
            JSONArray ready = new JSONArray();
            if ((mask & 1) != 0) ready.put(SELF);
            if ((mask & 2) != 0) ready.put(GUEST);
            s.put("room", room(SELF, ids(SELF, GUEST), ready));
            rows = model.rows(s);
            check(rows.get(0).ready == ((mask & 1) != 0), "first readiness combination " + mask);
            check(rows.get(1).ready == ((mask & 2) != 0), "second readiness combination " + mask);
        }
    }
    private static void testPaginationAndScope() throws Exception {
        StationRoomRoster model = new StationRoomRoster();
        JSONObject page0 = pair(1, people());
        model.observe(page0);
        JSONObject page1 = pair(2, new JSONArray().put(peer(OTHER, "Outra página"))).put("page", 1);
        List<StationRoomRoster.Row> rows = model.rows(page1);
        check(rows.get(0).name.equals("João"), "first name survives paginated absence");
        check(rows.get(1).name.equals("Luíza 🎮"), "second name survives paginated absence");
        check(rows.get(0).nameKnown && rows.get(1).nameKnown, "cache names remain identified");
        page1.put("room", room(SELF, ids(SELF, GUEST), new JSONArray()));
        rows = model.rows(page1);
        check(!rows.get(0).ready && !rows.get(1).ready, "cache never preserves readiness");
        JSONObject renamed = pair(3, new JSONArray().put(peer(GUEST, "Nome novo")));
        check(model.rows(renamed).get(1).name.equals("Nome novo"), "current observed name supersedes cache");
        model.observe(page0); // Defensive protection; Activity normally rejects this first.
        check(model.rows(pair(4, new JSONArray())).get(1).name.equals("Nome novo"), "older revision does not overwrite cached name");
        model.observe(pair(4, new JSONArray().put(peer(SELF, "Mesmo revision outra página"))));
        check(model.rows(pair(4, new JSONArray())).get(0).name.equals("Mesmo revision outra página"), "same revision page accepted");
        JSONObject restarted = pair(1, new JSONArray()).put("instance", OTHER_INSTANCE);
        rows = model.rows(restarted);
        check(rows.get(0).name.equals(StationRoomRoster.NAME_UNAVAILABLE), "instance clears first cached name");
        check(!rows.get(1).nameKnown, "instance clears second cached name");
        check(rows.get(1).occupied, "unknown name remains a real participant");
        model.observe(pair(2, people()).put("instance", OTHER_INSTANCE));
        model.reset();
        check(!model.rows(restarted).get(0).nameKnown, "explicit session reset clears cache");
        model.observe(page0);
        model.observe(pair(10, new JSONArray()).put("instance", "invalid"));
        check(!model.rows(pair(11, new JSONArray())).get(1).nameKnown, "invalid scope cannot leak old names");
        check(model.resolveName(null, SELF).equals(StationRoomRoster.NAME_UNAVAILABLE), "null snapshot cannot expose cached names");
        check(model.resolveName(page0, null).equals(StationRoomRoster.NAME_UNAVAILABLE), "null ID explicit fallback");
    }
    private static void testNamesAndSlots() throws Exception {
        StationRoomRoster model = new StationRoomRoster();
        List<StationRoomRoster.Row> rows = model.rows(pair(1, new JSONArray()));
        check(rows.get(0).name.equals("Nome indisponível"), "missing name explicit");
        check(rows.get(1).name.equals("Nome indisponível"), "both missing names explicit");
        check(rows.get(0).occupied && rows.get(1).occupied, "missing names do not remove members");
        check(rows.get(0).host && rows.get(0).self && rows.get(0).ready, "flags independent of nickname");
        check(!rows.get(0).nameKnown && !rows.get(1).nameKnown, "unknown markers independent of flags");
        JSONArray sameNames = new JSONArray().put(peer(SELF, "Mesmo nome")).put(peer(GUEST, "Mesmo nome"));
        rows = model.rows(pair(2, sameNames));
        check(rows.size() == 2 && !rows.get(0).peerId.equals(rows.get(1).peerId), "same nickname keeps two distinct IDs");
        check(rows.get(0).name.equals(rows.get(1).name), "real duplicate nickname preserved");
        StringBuilder longName = new StringBuilder();
        for (int i = 0; i < 100; i++) longName.append("Á🎮");
        rows = model.rows(pair(3, new JSONArray().put(peer(GUEST, longName.toString()))));
        check(rows.get(1).name.equals(longName.toString()), "long Unicode name retained for layout binding");
        model.reset();
        JSONObject solo = snapshot(1, people(), room(SELF, ids(SELF), ids(SELF)));
        rows = model.rows(solo);
        check(rows.size() == 2 && rows.get(0).occupied, "solo room has two visual slots");
        check(!rows.get(1).occupied && rows.get(1).peerId.isEmpty(), "empty slot is not a participant");
        check(rows.get(1).name.equals("Aguardando jogador"), "empty slot waiting label");
        check(!rows.get(1).nameKnown && !rows.get(1).ready && !rows.get(1).host && !rows.get(1).self, "empty slot carries no participant status");
        check(rows.get(1).label.equals("Jogador 2"), "second empty room position label");
        check(model.rows(snapshot(2, people(), null)).isEmpty(), "no room has no invented roster");
        check(model.rows(null).isEmpty(), "null snapshot has no roster");
        rows = model.rows(snapshot(3, people(), room(SELF, new JSONArray(), ids(SELF))));
        check(rows.size() == 2 && !rows.get(0).occupied && !rows.get(1).occupied, "empty room uses placeholders only");
        rows = model.rows(snapshot(4, people(), room(SELF, ids(SELF, SELF), ids(SELF))));
        check(rows.get(0).occupied && !rows.get(1).occupied, "duplicate member cannot invent second participant");
        rows = model.rows(snapshot(5, people(), room(SELF, new JSONArray().put(27).put(JSONObject.NULL), ids(SELF))));
        check(!rows.get(0).occupied && !rows.get(1).occupied, "non-string members are not names or IDs");
        model.reset();
        rows = model.rows(pair(6, new JSONArray().put(peer(SELF, "   ")).put(new JSONObject().put("peerId", GUEST).put("nickname", 42))));
        check(!rows.get(0).nameKnown && !rows.get(1).nameKnown, "blank and non-string names remain unknown");
        rows = model.rows(snapshot(7, people(), room(SELF, ids(SELF, GUEST, OTHER), ids(SELF))));
        check(rows.size() == 3 && rows.get(2).peerId.equals(OTHER), "unexpected extra members stay visible without changing start policy");
        check(rows.get(2).label.equals("Jogador 3"), "extra member uses actual room position");
    }
    private static void testBound() throws Exception {
        StationRoomRoster model = new StationRoomRoster();
        JSONArray full = new JSONArray();
        for (int i = 0; i < 256; i++) full.put(peer("p" + i, "Nome " + i));
        JSONObject s = snapshot(1, full, null);
        model.observe(s);
        JSONObject empty = snapshot(2, new JSONArray(), null);
        check(model.resolveName(empty, "p0").equals("Nome 0"), "oldest entry available at capacity");
        model.observe(snapshot(3, new JSONArray().put(peer("new", "Novo")), null));
        JSONObject next = snapshot(4, new JSONArray(), null);
        check(model.resolveName(next, "p0").equals("Nome 0"), "recently resolved member survives eviction");
        check(model.resolveName(next, "p1").equals(StationRoomRoster.NAME_UNAVAILABLE), "least recently used entry evicted above 256");
        check(model.resolveName(next, "new").equals("Novo"), "new name cached");
        int available = 0;
        for (int i = 0; i < 256; i++)
            if (!model.resolveName(next, "p" + i).equals(StationRoomRoster.NAME_UNAVAILABLE)) available++;
        check(available == 255, "exactly 256 names including newcomer retained");
        JSONArray oversized = new JSONArray();
        for (int i = 0; i < 270; i++) oversized.put(peer("many" + i, "N" + i));
        JSONObject roomPage = snapshot(5, oversized, room("many0", ids("many0", "many269"), new JSONArray()));
        List<StationRoomRoster.Row> rows = model.rows(roomPage);
        check(rows.get(0).name.equals("N0"), "current page name wins even if cache capacity evicts it");
        check(rows.get(1).name.equals("N269"), "last current page name bound by ID");
        check(model.resolveName(snapshot(6, new JSONArray(), null), "many0").equals(StationRoomRoster.NAME_UNAVAILABLE), "capacity remains bounded after oversized page");
    }
    public static void main(String[] args) throws Exception {
        testBinding();
        testPaginationAndScope();
        testNamesAndSlots();
        testBound();
        System.out.println("StationRoomRosterTest: " + checks + " checks passed");
    }
}
