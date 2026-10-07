package org.emulationstation.frontend.netplay;
import org.json.*;
import java.util.List;

public final class StationOwnRoomProfilesTest {
    static int checks;
    static final String HOST="11111111111111111111111111111111",GUEST="22222222222222222222222222222222",OTHER="33333333333333333333333333333333";
    static void check(boolean ok,String text){checks++;if(!ok)throw new AssertionError(text);}
    static JSONArray ids(String... xs){return new JSONArray(java.util.Arrays.asList(xs));}
    static JSONObject profile(String id,Object name)throws Exception{return new JSONObject().put("peerId",id).put("nickname",name);}
    static JSONObject fixture()throws Exception {
        JSONArray social=new JSONArray();
        for(int i=0;i<100;i++)social.put(profile("unrelated"+i,"Pessoa "+i));
        return new JSONObject().put("instance","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").put("revision",1).put("selfId",HOST)
          .put("page",40).put("roomCapabilities",ids("short-invite-v1","own-room-member-profiles-v1")).put("peers",social)
          .put("room",new JSONObject().put("members",ids(HOST,GUEST)).put("ready",ids(GUEST)).put("hostId",HOST)
            .put("memberProfiles",new JSONArray().put(profile(GUEST,"Convidado 🎮")).put(profile(HOST,"Anfitrião"))));
    }
    public static void main(String[] args)throws Exception {
        StationRoomRoster model=new StationRoomRoster(); JSONObject s=fixture();
        List<StationRoomRoster.Row> rows=model.rows(s);
        check(rows.size()==2,"profiles must not add participants");check(rows.get(0).name.equals("Anfitrião"),"host outside social page");
        check(rows.get(1).name.equals("Convidado 🎮"),"guest outside social page");check(rows.get(0).host,"host by ID");
        check(rows.get(0).self&&!rows.get(1).self,"self by ID");check(!rows.get(0).ready&&rows.get(1).ready,"ready by IDs only");
        check(model.resolveName(s,GUEST).equals("Convidado 🎮"),"same resolver for card/dialog");
        s.put("peers",new JSONArray().put(profile(GUEST,"Old page name")));check(model.rows(s).get(1).name.equals("Convidado 🎮"),"own room wins social page");
        s.getJSONObject("room").getJSONArray("memberProfiles").put(profile(OTHER,"Intruso"));
        check(model.rows(s).size()==2,"unlisted profile ignored");check(model.resolveName(s,OTHER).equals(StationRoomRoster.NAME_UNAVAILABLE),"unlisted name not cached");
        s.put("revision",2);s.getJSONObject("room").put("memberProfiles",new JSONArray().put(profile(HOST,"Novo anfitrião")).put(profile(GUEST,"Novo convidado")));
        check(model.rows(s).get(0).name.equals("Novo anfitrião"),"name changes at new revision");
        s.getJSONObject("room").put("memberProfiles",JSONObject.NULL);s.put("peers",new JSONArray());check(model.rows(s).get(1).name.equals("Novo convidado"),"bounded name fallback remains");
        check(!model.rows(s).get(0).ready,"name fallback never ready");
        model.reset();s=fixture();s.put("roomCapabilities",ids("short-invite-v1"));check(!model.rows(s).get(0).nameKnown,"capability required");
        s.put("peers",new JSONArray().put(profile(HOST,"Legado")));check(model.rows(s).get(0).name.equals("Legado"),"legacy server social names preserved");
        model.reset();s=fixture();s.put("selfId",OTHER);check(!model.rows(s).get(1).nameKnown,"own-room identity required");
        model.reset();s=fixture();s.put("selfId",JSONObject.NULL);check(!model.rows(s).get(1).nameKnown,"missing self rejected");
        model.reset();s=fixture();s.getJSONObject("room").put("memberProfiles",new JSONArray().put(profile(HOST,"one")).put(profile(HOST,"two")));
        check(!model.rows(s).get(0).nameKnown,"ambiguous duplicate ID ignored");check(!model.rows(s).get(1).nameKnown,"missing guest does not borrow host");
        model.reset();s=fixture();s.getJSONObject("room").put("memberProfiles",new JSONArray().put(profile(HOST,42)).put(profile(GUEST,"  ")));
        check(!model.rows(s).get(0).nameKnown&&!model.rows(s).get(1).nameKnown,"malformed names ignored");
        model.reset();s=fixture();s.getJSONObject("room").put("memberProfiles",new JSONArray().put(JSONObject.NULL).put(17).put(profile(GUEST,"Válido")));
        check(model.rows(s).get(1).name.equals("Válido"),"malformed unrelated entries ignored");
        model.reset();s=fixture();s.getJSONObject("room").put("memberProfiles",new JSONArray().put(profile(HOST,"Igual")).put(profile(GUEST,"Igual")));
        rows=model.rows(s);check(!rows.get(0).peerId.equals(rows.get(1).peerId)&&rows.get(0).name.equals(rows.get(1).name),"duplicate nickname preserves distinct users");
        model.reset();s=fixture();s.put("revision",5);model.observe(s);JSONObject stale=fixture();stale.getJSONObject("room").getJSONArray("memberProfiles").getJSONObject(0).put("nickname","Stale");
        check(model.rows(stale).get(1).name.equals("Convidado 🎮"),"stale profile cannot replace cache");
        s=fixture();s.put("instance","bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb");s.getJSONObject("room").remove("memberProfiles");check(!model.rows(s).get(0).nameKnown,"instance clears profile cache");
        model.reset();s=fixture();s.put("instance","invalid");check(!model.rows(s).get(0).nameKnown,"invalid instance rejects profiles");
        model.reset();s=fixture();s.put("room",JSONObject.NULL);check(model.rows(s).isEmpty(),"no room creates no roster");
        model.reset();s=fixture();s.getJSONObject("room").put("members",ids(HOST));rows=model.rows(s);
        check(rows.size()==2&&!rows.get(1).occupied,"unlisted guest becomes empty slot");check(!rows.get(1).ready,"unlisted ready ignored");
        check(model.resolveName(s,GUEST).equals(StationRoomRoster.NAME_UNAVAILABLE),"unlisted profile not retained");
        System.out.println("StationOwnRoomProfilesTest: "+checks+" checks passed");
    }
}
