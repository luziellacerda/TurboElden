package org.emulationstation.frontend.netplay;
import org.json.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** A display player count never grants an online seat. Only a signed, exact game profile does. */
final class StationMultiplayerProfile {
    final String itemId,contentSha256,platform,engineId,coreSha256,runtimeSha256,profileId,profileSha256,controllerProfile,mode,options;
    final int maximumPlayers;final int[] allowed,devices;
    final String modeTitle;final String[] instructions,sources;
    private StationMultiplayerProfile(JSONObject p,JSONObject engine)throws Exception {
        if(!Boolean.TRUE.equals(p.opt("approved")))throw unavailable();
        itemId=plain(p,"itemId",160);contentSha256=hash(p,"contentSha256");platform=plain(p,"platform",40);
        engineId=plain(p,"engineId",160);coreSha256=hash(p,"coreSha256");runtimeSha256=hash(p,"runtimeSha256");
        profileId=plain(p,"profileId",160);profileSha256=hash(p,"profileSha256");controllerProfile=plain(p,"controllerProfile",80);mode=plain(p,"mode",80);
        if(!engineId.equals(engine.getString("engineId"))||!platform.equals(engine.getString("platform"))||!coreSha256.equals(engine.getString("coreSha256"))||!runtimeSha256.equals(engine.getString("runtimeSha256")))throw unavailable();
        maximumPlayers=integer(p.get("maximumPlayers"));if(maximumPlayers<1||maximumPlayers>5)throw unavailable();
        if(maximumPlayers>StationOnlinePlatformPolicy.maximum(platform))throw unavailable();
        modeTitle=p.isNull("modeTitle")?"":plain(p,"modeTitle",80);
        instructions=help(p,"instructions",500,false);sources=help(p,"sources",512,true);
        JSONArray a=p.getJSONArray("allowedPlayerCounts");if(a.length()>4||(maximumPlayers==1?a.length()!=0:a.length()<1))throw unavailable();allowed=new int[a.length()];int last=1;
        for(int i=0;i<a.length();i++){int n=integer(a.get(i));if(n<=last||n>maximumPlayers)throw unavailable();allowed[i]=n;last=n;}if(last!=maximumPlayers)throw unavailable();
        String base=engine.getString("options");int[] configured;String opts=base;
        switch(controllerProfile){
            case "standard-2p-v1":if(maximumPlayers>2)throw unavailable();configured=new int[]{1,1};break;
            case "direct-four-ports-v1":if(maximumPlayers>4||!StationOnlinePlatformPolicy.directFourPads(platform))throw unavailable();configured=new int[]{1,1,1,1};break;
            case "psx-dualshock-2p-v1":if(maximumPlayers>2||!"psx".equals(platform))throw unavailable();configured=new int[]{517,517};break;
            case "snes-multitap-port2-v1":if(!"snes".equals(platform))throw unavailable();configured=new int[]{1,257,1,1,1};break;
            case "megadrive-sega-teamplayer-v1":if(maximumPlayers>4||!"megadrive".equals(platform)||!base.isEmpty())throw unavailable();configured=new int[]{1,1,1,1,1,1,1,1};opts="clownmdemu_input_protocol = \"sega\"\n";break;
            case "megadrive-ea-4way-v1":if(maximumPlayers>4||!"megadrive".equals(platform)||!base.isEmpty())throw unavailable();configured=new int[]{1,1,1,1};opts="clownmdemu_input_protocol = \"ea\"\n";break;
            default:throw unavailable();
        }
        devices=configured;options=opts;
        String expected=StationOnlineGame.hex(MessageDigest.getInstance("SHA-256").digest(canonical(controllerProfile,devices,options).getBytes(StandardCharsets.UTF_8)));
        if(!expected.equals(profileSha256))throw unavailable();
    }
    static StationMultiplayerProfile find(JSONObject snapshot,String item,JSONObject engine)throws Exception {return find(snapshot,item,engine,"");}
    static java.util.List<StationMultiplayerProfile> choices(JSONObject snapshot,String item,JSONObject engine)throws Exception {
        java.util.List<StationMultiplayerProfile> result=new java.util.ArrayList<>();
        for(StationMultiplayerProfile p:classifications(snapshot,item,engine))if(p.maximumPlayers>=2)result.add(p);
        boolean hasDocumentedModes=false;
        for(StationMultiplayerProfile p:result)if(!"two-player".equals(p.mode)&&!p.modeTitle.isEmpty()&&p.sources.length>0){hasDocumentedModes=true;break;}
        if(hasDocumentedModes){
            java.util.Iterator<StationMultiplayerProfile> iterator=result.iterator();
            while(iterator.hasNext())if("two-player".equals(iterator.next().mode))iterator.remove();
        }
        return java.util.Collections.unmodifiableList(result);
    }
    /** Exact verified classifications may describe a single-player mode, which grants no room seats. */
    static java.util.List<StationMultiplayerProfile> classifications(JSONObject snapshot,String item,JSONObject engine)throws Exception {
        if(snapshot==null||snapshot.optInt("multiplayerVersion")!=3||!"station-multiplayer.v3".equals(snapshot.optString("capability")))throw unavailable();
        java.util.List<StationMultiplayerProfile> result=new java.util.ArrayList<>();JSONArray all=snapshot.getJSONArray("profiles");
        for(int i=0;i<all.length();i++){JSONObject p=all.getJSONObject(i);if(Boolean.TRUE.equals(p.opt("approved"))&&item.equals(p.optString("itemId"))&&engine.optString("engineId").equals(p.optString("engineId"))){result.add(new StationMultiplayerProfile(p,engine));}}
        return java.util.Collections.unmodifiableList(result);
    }
    static StationMultiplayerProfile find(JSONObject snapshot,String item,JSONObject engine,String profileId)throws Exception {
        StationMultiplayerProfile found=null;
        for(StationMultiplayerProfile p:choices(snapshot,item,engine))if(profileId.isEmpty()||profileId.equals(p.profileId)){if(found!=null)throw unavailable();found=p;}
        if(found==null)throw unavailable();return found;
    }
    static String canonical(String name,int[] devices,String options){
        StringBuilder out=new StringBuilder("{\"schemaVersion\":1,\"controllerProfile\":").append(JSONObject.quote(name)).append(",\"devices\":[");
        for(int i=0;i<devices.length;i++){if(i>0)out.append(',');out.append(devices[i]);}
        return out.append("],\"coreOptions\":").append(JSONObject.quote(options)).append('}').toString();
    }
    boolean permits(int count){for(int n:allowed)if(n==count)return true;return false;}
    int deviceForSlot(int slot,int activeMask)throws IOException {
        if(slot<1||slot>16||activeMask<1||activeMask>31)throw unavailable();
        if("direct-four-ports-v1".equals(controllerProfile)&&(activeMask&(1<<(slot-1)))==0)return 0;
        return slot<=devices.length?devices[slot-1]:0;
    }
    JSONObject fields(JSONObject c)throws JSONException{return c.put("itemId",itemId).put("contentSha256",contentSha256).put("engineId",engineId).put("coreSha256",coreSha256).put("runtimeSha256",runtimeSha256).put("profileId",profileId).put("profileSha256",profileSha256);}
    void verify(JSONObject room)throws Exception {
        if(!"station-stream.v3".equals(room.optString("recoveryProtocol"))||!"relay-wss-v3".equals(room.optString("transport")))throw unavailable();
        JSONObject expected=fields(new JSONObject());Iterator<String> keys=expected.keys();while(keys.hasNext()){String k=keys.next();if(!expected.getString(k).equals(room.optString(k)))throw unavailable();}
        if(!platform.equals(room.optString("platform"))||!mode.equals(room.optString("mode"))||!controllerProfile.equals(room.optString("controllerProfile"))||maximumPlayers!=room.optInt("maximumPlayers"))throw unavailable();
        JSONArray a=room.optJSONArray("allowedPlayerCounts");if(a==null||a.length()!=allowed.length)throw unavailable();for(int i=0;i<allowed.length;i++)if(a.optInt(i)!=allowed[i])throw unavailable();
        int capacity=room.getInt("capacity");if(!permits(capacity))throw unavailable();
        JSONArray roster=room.getJSONArray("roster");if(roster.length()<1||roster.length()>capacity)throw unavailable();
        HashSet<String> people=new HashSet<>();HashSet<Integer> slots=new HashSet<>();
        for(int i=0;i<roster.length();i++){JSONObject row=roster.getJSONObject(i);String id=row.getString("peerId");int slot=row.getInt("slot");if(id.isEmpty()||!people.add(id)||slot<1||slot>capacity||!slots.add(slot))throw unavailable();if(slot==1&&!id.equals(room.getString("hostId")))throw unavailable();}
        if(!slots.contains(1))throw unavailable();
        if(!"waiting".equals(room.optString("state"))&&!permits(roster.length()))throw unavailable();
    }
    static int slot(JSONObject room,String peer)throws Exception {JSONArray a=room.getJSONArray("roster");for(int i=0;i<a.length();i++){JSONObject p=a.getJSONObject(i);if(peer.equals(p.getString("peerId")))return p.getInt("slot");}throw unavailable();}
    static int mask(JSONObject room)throws Exception {JSONArray a=room.getJSONArray("roster");int mask=0;for(int i=0;i<a.length();i++){int slot=a.getJSONObject(i).getInt("slot");if(slot<1||slot>5||(mask&(1<<(slot-1)))!=0)throw unavailable();mask|=1<<(slot-1);}return mask;}
    static String[] help(JSONObject value,String key,int maximum,boolean links)throws Exception {
        if(value.isNull(key))return new String[0];JSONArray array=value.getJSONArray(key);if(array.length()>8)throw unavailable();String[] out=new String[array.length()];
        for(int i=0;i<out.length;i++){Object raw=array.get(i);if(!(raw instanceof String))throw unavailable();String s=(String)raw;if(s.isEmpty()||s.length()>maximum)throw unavailable();for(int c=0;c<s.length();c++)if(Character.isISOControl(s.charAt(c)))throw unavailable();if(links){java.net.URI uri=new java.net.URI(s);if(!"https".equals(uri.getScheme())||uri.getHost()==null||uri.getUserInfo()!=null)throw unavailable();}out[i]=s;}return out;
    }
    static String plain(JSONObject p,String k,int max)throws Exception {String v=p.getString(k);if(v.isEmpty()||v.length()>max||v.indexOf('\n')>=0||v.indexOf('\r')>=0)throw unavailable();return v;}
    static String hash(JSONObject p,String k)throws Exception {String v=p.getString(k);if(!v.matches("[0-9a-f]{64}"))throw unavailable();return v;}
    private static int integer(Object value)throws Exception {if(!(value instanceof Integer)&&!(value instanceof Long))throw unavailable();long n=((Number)value).longValue();if(n<Integer.MIN_VALUE||n>Integer.MAX_VALUE)throw unavailable();return (int)n;}
    static StationOnlineGame.Unavailable unavailable(){return new StationOnlineGame.Unavailable("O modo online deste jogo ainda não tem uma classificação de jogadores e controles confirmada. Escolha um jogo já aprovado.");}
}
