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
        JSONArray members=room.optJSONArray("members"),ready=room.optJSONArray("ready");
        if(members==null||members.length()!=2||members.optString(0).isEmpty()||members.optString(0).equals(members.optString(1))||!has(members,self))return "Convide outro jogador ou compartilhe o código da sala.";
        if(!has(ready,self))return "Marque Estou pronto para confirmar sua participação.";
        if(!has(ready,members.optString(0))||!has(ready,members.optString(1)))return "Aguardando o outro jogador marcar Estou pronto.";
        if(!has(snapshot.optJSONArray("transports"),"relay-wss-v1"))return "A conexão pela internet aguarda ativação no servidor Station.";
        return "";
    }
    static boolean has(JSONArray values,String value){if(values!=null)for(int i=0;i<values.length();i++)if(value.equals(values.optString(i)))return true;return false;}
}
