package org.emulationstation.frontend.netplay;
import org.json.*;
/** A presence refresh must never erase the explanation for a failed user action. */
final class StationRoomFeedback {
    private String error="";
    void begin(){error="";}
    void fail(String value){error=value==null?"":value;}
    String text(JSONObject snapshot,boolean busy){
        if(!error.isEmpty())return error;
        if(busy)return "Concluindo sua solicitação…";
        JSONObject room=snapshot==null?null:snapshot.optJSONObject("room");
        if(room==null)return "Convide um jogador ou entre em uma sala para começar.";
        if(!"waiting".equals(room.optString("state")))return "Conectando os jogadores…";
        if(!snapshot.optString("selfId").equals(room.optString("hostId")))return "Marque Estou pronto e aguarde quem criou a sala iniciar.";
        String reason=StationRoomStartState.reason(snapshot);
        return reason.isEmpty()?"Os dois jogadores estão prontos. Você pode iniciar.":reason;
    }
}
