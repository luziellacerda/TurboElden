package org.emulationstation.frontend.netplay;
import org.json.*;
public final class StationCompactLobbyTest {
    static int checks;
    static void check(boolean v,String label){checks++;if(!v)throw new AssertionError(label);}
    static String repeat(String s,int n){StringBuilder b=new StringBuilder();while(n-->0)b.append(s);return b.toString();}
    static final String INSTANCE=repeat("a",32), ROOM=repeat("b",32), SELF=repeat("c",32), PEER=repeat("d",32), ITEM="station_"+repeat("e",32);
    static JSONObject snapshot(String status)throws Exception{return new JSONObject().put("instance",INSTANCE).put("revision",1).put("selfId",SELF).put("peers",new JSONArray().put(new JSONObject().put("peerId",SELF).put("nickname","Eu").put("status","online")).put(new JSONObject().put("peerId",PEER).put("nickname","Luíza 🎮").put("status",status))).put("rooms",new JSONArray());}
    static JSONObject room(String host,String phase,int count)throws Exception{JSONArray m=new JSONArray().put(SELF);if(count>1)m.put(PEER);return new JSONObject().put("roomId",ROOM).put("itemId",ITEM).put("hostId",host).put("state",phase).put("members",m);}
    static void reject(String value){try{StationInvitationCode.parse(value);throw new AssertionError("Accepted invalid code: "+value);}catch(IllegalArgumentException expected){checks++;}}
    public static void main(String[] args)throws Exception{
        String code=StationInvitationCode.encode(INSTANCE,ROOM,ITEM);StationInvitationCode parsed=StationInvitationCode.parse(code);
        check(parsed.instance.equals(INSTANCE)&&parsed.roomId.equals(ROOM)&&parsed.itemId.equals(ITEM),"exact code roundtrip");
        check(StationInvitationCode.parse("  "+code+"  ").itemId.equals(ITEM),"trim outer whitespace");
        check(code.length()<=160&&!code.contains("https")&&!code.contains("password"),"public locator, bounded");
        for(int n=8;n<=64;n++){String item=repeat("x",n);check(StationInvitationCode.parse(StationInvitationCode.encode(INSTANCE,ROOM,item)).itemId.equals(item),"allowed item length"+n);}
        reject(null);reject("");reject("TS2:"+INSTANCE+":"+ROOM+":"+ITEM);reject("TS1:"+INSTANCE+":"+ROOM);reject(code+":extra");reject(code+"\ninside");reject(code.replace(INSTANCE,repeat("A",32)));reject(code.replace(ROOM,"../"));reject("TS1:"+INSTANCE+":"+ROOM+":short");reject("TS1:"+INSTANCE+":"+ROOM+":"+repeat("x",65));reject("TS1:"+INSTANCE+":"+ROOM+":https://evil.test");reject(repeat("x",161));
        for(char c:new char[]{'/', '\\', ':', ' ', '\n', '\r', '\t', '\u0000', '.', '#', '?', 'ç'})reject("TS1:"+INSTANCE+":"+ROOM+":"+repeat("x",8)+c+"x");
        JSONObject s=snapshot("online");StationPlayerModel m=StationPlayerModel.read(s,PEER,"old",ITEM);
        check(m.present&&m.available&&m.canInvite&&!m.self&&!m.canShare,"available player can create and invite");check(m.name.equals("Luíza 🎮"),"actual Unicode nickname");check(m.inviteLabel.equals("Criar sala e convidar"),"create first label");
        check(!StationPlayerModel.read(s,PEER,"old",null).canInvite,"missing selected game");
        m=StationPlayerModel.read(s,SELF,"old",ITEM);check(m.self&&!m.canInvite,"cannot invite self");
        m=StationPlayerModel.read(s,repeat("f",32),"Missing",ITEM);check(!m.present&&!m.canInvite&&!m.status.toLowerCase().contains("offline"),"absence from paged snapshot not offline claim");
        m=StationPlayerModel.read(snapshot("in-room"),PEER,"old",ITEM);check(!m.available&&!m.canInvite&&m.status.equals("Em uma sala"),"busy peer");
        m=StationPlayerModel.read(snapshot("future-state"),PEER,"old",ITEM);check(!m.canInvite&&m.status.equals("Status não informado"),"unknown status");
        s=snapshot("online").put("room",room(SELF,"waiting",1));m=StationPlayerModel.read(s,PEER,"old",ITEM);check(m.canInvite&&m.canShare&&m.inviteLabel.equals("Enviar convite"),"host waiting free slot");
        check(StationPlayerModel.shareable(s),"host may share real room");
        s.put("room",room(SELF,"waiting",2));m=StationPlayerModel.read(s,PEER,"old",ITEM);check(!m.canInvite&&!m.canShare,"full room");
        for(String phase:new String[]{"starting","connecting","unknown"}){s.put("room",room(SELF,phase,1));m=StationPlayerModel.read(s,PEER,"old",ITEM);check(!m.canInvite&&!m.canShare,"not waiting: "+phase);}
        s.put("room",room(PEER,"waiting",1));check(!StationPlayerModel.read(s,PEER,"old",ITEM).canInvite&&!StationPlayerModel.shareable(s),"guest cannot invite/share");
        s=snapshot("in-room").put("room",room(SELF,"waiting",2));check(StationPlayerModel.read(s,PEER,"old",ITEM).roomItemId.equals(ITEM),"same-room game from actual members");
        s=snapshot("in-room");s.getJSONArray("rooms").put(room(PEER,"waiting",1));check(StationPlayerModel.read(s,PEER,"old",ITEM).roomItemId.equals(ITEM),"public host room game");
        s.getJSONArray("rooms").put(room(SELF,"waiting",2));check(!StationPlayerModel.read(snapshot("in-room"),PEER,"old",ITEM).roomItemId.equals(ITEM),"do not infer guest game");
        check(!StationPlayerModel.shareable(null),"null snapshot");check(!StationPlayerModel.shareable(snapshot("online").put("room",new JSONObject().put("hostId",SELF).put("state","waiting"))),"missing member list fail closed");
        StationRoomState state=new StationRoomState();check(state.accept(snapshot("online")),"accept current signed shape");check(!state.accept(snapshot("online").put("revision",0)),"stale reply rejected");
        try{state.accept(snapshot("online").put("instance",repeat("f",32)));throw new AssertionError("restart accepted");}catch(java.io.IOException expected){checks++;}
        System.out.println("PASS "+checks+" executable checks: compact player model, real room codes, stale presence, invite policy and snapshot ordering");
    }
}
