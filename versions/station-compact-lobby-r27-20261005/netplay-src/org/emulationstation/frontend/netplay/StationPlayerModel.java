package org.emulationstation.frontend.netplay;

import org.json.*;

/** Only information actually published in the signed lobby snapshot. */
final class StationPlayerModel {
    final String id,name,status,roomItemId,inviteLabel,reason;
    final boolean present,self,available,canInvite,canShare;
    final JSONObject ownedRoom;
    private StationPlayerModel(String id,String name,String status,String item,String label,String reason,
            boolean present,boolean self,boolean available,boolean invite,boolean share,JSONObject room){
        this.id=id;this.name=name;this.status=status;roomItemId=item;inviteLabel=label;this.reason=reason;
        this.present=present;this.self=self;this.available=available;canInvite=invite;canShare=share;ownedRoom=room;
    }
    static JSONObject peer(JSONObject snapshot,String id){
        JSONArray all=snapshot==null?null:snapshot.optJSONArray("peers");
        if(all!=null)for(int i=0;i<all.length();i++){JSONObject p=all.optJSONObject(i);if(p!=null&&id.equals(p.optString("peerId")))return p;}
        return null;
    }
    static boolean member(JSONObject room,String id){
        JSONArray members=room==null?null:room.optJSONArray("members");
        if(members!=null)for(int i=0;i<members.length();i++)if(id.equals(members.optString(i)))return true;
        return false;
    }
    static boolean shareable(JSONObject snapshot){
        if(snapshot==null)return false;JSONObject room=snapshot.optJSONObject("room");
        JSONArray members=room==null?null:room.optJSONArray("members");
        return room!=null&&snapshot.optString("selfId").equals(room.optString("hostId"))&&"waiting".equals(room.optString("state"))&&members!=null&&members.length()<2;
    }
    static StationPlayerModel read(JSONObject snapshot,String id,String lastName,String selectedItem){
        JSONObject p=peer(snapshot,id),mine=snapshot==null?null:snapshot.optJSONObject("room");
        String name=p==null?lastName:p.optString("nickname","Jogador");
        boolean self=snapshot!=null&&id.equals(snapshot.optString("selfId"));
        boolean online=p!=null&&"online".equals(p.optString("status"));
        boolean inRoom=p!=null&&"in-room".equals(p.optString("status"));
        String status=p==null?"Presença não confirmada":self?(inRoom?"Você está em uma sala":"Você está online"):online?"Disponível para jogar":inRoom?"Em uma sala":"Status não informado";
        String item="";
        if(member(mine,id))item=mine.optString("itemId");
        else if(snapshot!=null){JSONArray rs=snapshot.optJSONArray("rooms");if(rs!=null)for(int i=0;i<rs.length();i++){JSONObject r=rs.optJSONObject(i);if(r!=null&&id.equals(r.optString("hostId"))){item=r.optString("itemId");break;}}}
        boolean share=shareable(snapshot),invite=false;
        String label=mine==null?"Criar sala e convidar":"Enviar convite",reason;
        if(p==null)reason="Este jogador não está na página atual. Volte à lista para atualizar a presença.";
        else if(self)reason="Seu perfil na comunidade. Compartilhe o código da sua sala para chamar alguém.";
        else if(!online)reason=inRoom?"Este jogador já está em uma sala.":"Aguarde a confirmação de disponibilidade deste jogador.";
        else if(mine==null){invite=selectedItem!=null&&!selectedItem.isEmpty();reason=invite?"Cria uma sala do jogo selecionado e envia o convite para este jogador.":"Abra um jogo e escolha Jogar online para criar a sala.";}
        else if(!snapshot.optString("selfId").equals(mine.optString("hostId")))reason="Somente quem criou sua sala pode enviar convites.";
        else if(!"waiting".equals(mine.optString("state")))reason="A partida já está em preparação. Aguarde para convidar outro jogador.";
        else if(!share)reason="Sua sala já está completa.";
        else {invite=true;reason="O convite aparece no aplicativo do jogador e expira em 60 segundos.";}
        return new StationPlayerModel(id,name,status,item,label,reason,p!=null,self,online,invite,share,mine);
    }
}
