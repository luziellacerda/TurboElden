package org.emulationstation.frontend.netplay;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import org.json.*;

/** Calls the real signed-profile parser with isolated JSON fixtures. Does not
 * authenticate a server, open a room, call emulator JNI, or prove gameplay. */
public final class StationDolphinProfileProbe {
    static int checks;
    static final String A=repeat('a'),B=repeat('b'),C=repeat('c');
    static String repeat(char c){StringBuilder out=new StringBuilder();for(int i=0;i<64;i++)out.append(c);return out.toString();}
    static void check(boolean value){if(!value)throw new AssertionError("check "+checks);checks++;}
    static JSONObject engine(String platform)throws Exception{return new JSONObject().put("platform",platform).put("engineId",platform+"-real-dolphin").put("coreSha256",A).put("runtimeSha256",B).put("backend",StationDolphinLaunch.BACKEND).put("options",StationDolphinLaunch.OPTIONS);}
    static String profileHash(String controller)throws Exception{return StationOnlineGame.hex(MessageDigest.getInstance("SHA-256").digest(StationMultiplayerProfile.canonical(controller,new int[]{1,1,1,1},StationDolphinLaunch.OPTIONS).getBytes(StandardCharsets.UTF_8)));}
    static JSONObject profile(JSONObject engine)throws Exception{
        String platform=engine.getString("platform"),controller=StationDolphinLaunch.profileFor(platform);
        return new JSONObject(engine.toString()).put("approved",true).put("itemId","isolated-game").put("contentSha256",C).put("profileId","isolated-mode").put("profileSha256",profileHash(controller)).put("controllerProfile",controller).put("mode","battle").put("modeTitle","Batalha").put("maximumPlayers",4).put("allowedPlayerCounts",new JSONArray(new int[]{2,3,4})).put("instructions",new JSONArray().put("Use um controle local por aparelho.")).put("sources",new JSONArray().put("https://dolphin-emu.org/docs/guides/netplay-guide/"));
    }
    static StationMultiplayerProfile parse(JSONObject profile,JSONObject engine)throws Exception{return StationMultiplayerProfile.find(new JSONObject().put("multiplayerVersion",3).put("capability","station-multiplayer.v3").put("profiles",new JSONArray().put(profile)),"isolated-game",engine);}
    static void reject(JSONObject profile,JSONObject engine)throws Exception{try{parse(profile,engine);throw new AssertionError("Invalid profile accepted");}catch(StationOnlineGame.Unavailable expected){checks++;}}
    public static void main(String[] args)throws Exception{
        for(String platform:new String[]{"gamecube","wii"}){
            JSONObject engine=engine(platform),profile=profile(engine);StationMultiplayerProfile parsed=parse(profile,engine);
            for(int count=0;count<=6;count++)check(parsed.permits(count)==(count>=2&&count<=4));
            for(int mask:new int[]{3,5,7,9,11,13,15})for(int slot=1;slot<=4;slot++)check(parsed.deviceForSlot(slot,mask)==((mask&(1<<(slot-1)))!=0?1:0));
            check(parsed.devices.length==4);check(parsed.options.equals(StationDolphinLaunch.OPTIONS));
            reject(new JSONObject(profile.toString()).put("maximumPlayers",5).put("allowedPlayerCounts",new JSONArray(new int[]{2,3,4,5})),engine);
            reject(new JSONObject(profile.toString()).put("allowedPlayerCounts",new JSONArray(new int[]{2,2,4})),engine);
            reject(new JSONObject(profile.toString()).put("allowedPlayerCounts",new JSONArray(new int[]{2,3})),engine);
            reject(new JSONObject(profile.toString()).put("approved",false),engine);
            reject(new JSONObject(profile.toString()).put("coreSha256",C),engine);
            reject(new JSONObject(profile.toString()).put("runtimeSha256",C),engine);
            reject(new JSONObject(profile.toString()).put("profileSha256",C),engine);
            reject(profile,new JSONObject(engine.toString()).put("backend","retroarch"));
            reject(profile,new JSONObject(engine.toString()).put("options",StationDolphinLaunch.OPTIONS+"changed=true\n"));
            String other=StationDolphinLaunch.profileFor("gamecube".equals(platform)?"wii":"gamecube");
            reject(new JSONObject(profile.toString()).put("controllerProfile",other).put("profileSha256",profileHash(other)),engine);
            reject(new JSONObject(profile.toString()).put("controllerProfile","direct-four-ports-v1").put("profileSha256",profileHash("direct-four-ports-v1")),engine);
            reject(new JSONObject(profile.toString()).put("sources",new JSONArray().put("http://example.org/")),engine);
        }
        System.out.println("{\"checks\":"+checks+",\"physicalGameplayValidated\":false}");
    }
}
