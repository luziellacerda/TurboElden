package org.emulationstation.frontend.netplay;
import org.json.*;
/** The signed snapshot is the authority; the server still validates every start. */
final class StationRoomStartState {
    static String reason(JSONObject snapshot) {
        JSONObject room=snapshot==null?null:snapshot.optJSONObject("room");
        if(room==null)return "Crie ou entre em uma sala primeiro.";
        String self=snapshot.optString("selfId");
        if(self.isEmpty()||!self.equals(room.optString("hostId")))return "Somente quem criou a sala pode iniciar.";
        if(!"waiting".equals(room.optString("state")))return "A partida já está em preparação.";
        if("station-stream.v3".equals(room.optString("recoveryProtocol"))){
            int capacity=room.optInt("capacity");JSONArray roster=room.optJSONArray("roster"),allowed=room.optJSONArray("allowedPlayerCounts");
            if(capacity<2||capacity>4||roster==null||roster.length()<2||roster.length()>capacity)return "Convide os jogadores para esta sala.";
            boolean countAllowed=false;for(int i=0;allowed!=null&&i<allowed.length();i++)if(allowed.optInt(i)==roster.length())countAllowed=true;
            if(!countAllowed)return "Este modo não aceita a quantidade atual de jogadores. Aguarde mais participantes.";
            java.util.HashSet<String> ids=new java.util.HashSet<>();java.util.HashSet<Integer> slots=new java.util.HashSet<>();
            for(int i=0;i<roster.length();i++){JSONObject p=roster.optJSONObject(i);if(p==null||p.optString("peerId").isEmpty()||!ids.add(p.optString("peerId"))||p.optInt("slot")<1||p.optInt("slot")>capacity||!slots.add(p.optInt("slot")))return "A lista de participantes precisa ser atualizada.";if(!p.optBoolean("ready"))return "Todos os participantes precisam marcar Estou pronto.";}
            if(!ids.contains(self)||!slots.contains(1))return "A lista de participantes precisa ser atualizada.";
            return has(snapshot.optJSONArray("transports"),"relay-wss-v3")?"":"A conexão da sala aguarda ativação.";
        }
        JSONArray members=room.optJSONArray("members"),ready=room.optJSONArray("ready");
        if(members==null||members.length()!=2||members.optString(0).isEmpty()||members.optString(0).equals(members.optString(1))||!has(members,self))return "Convide outro jogador ou compartilhe o código da sala.";
        if(!has(ready,self))return "Marque Estou pronto para confirmar sua participação.";
        if(!has(ready,members.optString(0))||!has(ready,members.optString(1)))return "Aguardando o outro jogador marcar Estou pronto.";
        if(!has(snapshot.optJSONArray("transports"),transport(snapshot)))return "A conexão pela internet aguarda ativação no servidor Station.";
        return "";
    }
    static String transport(JSONObject snapshot){
        JSONObject room=snapshot==null?null:snapshot.optJSONObject("room");
        if(room!=null&&"station-stream.v3".equals(room.optString("recoveryProtocol")))return "relay-wss-v3";
        return room!=null&&"station-stream.v2".equals(room.optString("recoveryProtocol"))?"relay-wss-v2":"relay-wss-v1";
    }
    static boolean has(JSONArray values,String value){if(values!=null)for(int i=0;i<values.length();i++)if(value.equals(values.optString(i)))return true;return false;}
}
