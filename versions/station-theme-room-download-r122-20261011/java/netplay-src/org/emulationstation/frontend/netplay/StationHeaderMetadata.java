package org.emulationstation.frontend.netplay;

import org.json.*;

/** Same exact item-ID metadata table used by the native carousel. Unknown stays unknown. */
final class StationHeaderMetadata {
    final String players;final int rating;
    StationHeaderMetadata(String players,int rating){this.players=players;this.rating=rating;}
    static StationHeaderMetadata lookup(JSONObject data,String itemId,String serverPlayers){
        JSONArray row=data.optJSONArray(itemId);String players=row==null?serverPlayers:row.optString(0,"");
        if(players.isEmpty())players=serverPlayers;
        int rating=row==null?-1:row.optInt(1,-1);if(rating<0||rating>1000)rating=-1;
        return new StationHeaderMetadata(playerCount(players),rating);
    }
    static String playerCount(String value){
        if(value==null||!value.matches("[0-9]+(?:-[0-9]+|\\+)?"))return "—";
        String count=value.substring(value.lastIndexOf('-')+1);
        return count.equals("1")?"1 jogador":count+" jogadores";
    }
}
