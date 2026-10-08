package org.emulationstation.frontend.netplay;

import android.content.Context;
import org.emulationstation.frontend.station.*;
import org.json.*;
import java.util.UUID;

/** Uses the existing pinned authority, Keystore identity and session lease. Never exposes bearer. */
final class StationOnlineClient {
    final StationAndroid app;volatile int page;
    volatile boolean multiplayerEnabled;private boolean multiplayerProbed;
    private JSONObject socialSnapshot,multiplayerSnapshot;private long combinedRevision;private String presentationKey="";
    JSONObject multiplayer(JSONObject request,StationApi.Cancellation cancel)throws Exception {
        StationApi.Session session=null;
        try(StationSessions.Lease lease=app.sessions.acquire(cancel)){
            session=lease.session;JSONObject result=app.api.multiplayer(session,request,cancel);
            JSONObject ticket=result.optJSONObject("ticket");
            if(ticket!=null)ticket.put("requestProof",app.api.multiplayerRelayRequestProof(session,ticket.getString("ticket")));
            acceptMultiplayer(result);multiplayerEnabled=true;return result;
        }catch(StationApi.Failure e){if(session!=null&&e.sessionDenied())app.sessions.denied(session);throw e;}
    }
    JSONObject profileSnapshot(String item,StationApi.Cancellation cancel)throws Exception {
        try{return multiplayer(command("capabilities").put("itemId",item),cancel);}
        catch(StationApi.Failure e){if(e.status==404||e.status==503)throw new StationOnlineGame.Unavailable("A classificação por jogo e as novas salas aguardam publicação no servidor.");throw e;}
    }
    private synchronized void acceptMultiplayer(JSONObject next)throws Exception {
        String instance=next.getString("instance");long revision=next.getLong("revision");
        if(!instance.matches("[0-9a-f]{32}")||revision<0)throw new java.io.IOException("Multiplayer revision");
        if(multiplayerSnapshot!=null){if(!instance.equals(multiplayerSnapshot.getString("instance")))throw new java.io.IOException("Multiplayer server restarted");if(revision<multiplayerSnapshot.getLong("revision"))return;}
        if(socialSnapshot!=null&&!socialSnapshot.getString("selfId").equals(next.getString("selfId")))throw new java.io.IOException("Multiplayer identity mismatch");
        multiplayerSnapshot=next;
    }
    synchronized JSONObject compose(JSONObject social)throws Exception {
        if(social!=null){
            if(socialSnapshot!=null){if(!social.getString("instance").equals(socialSnapshot.getString("instance")))throw new java.io.IOException("Online server restarted");if(social.getLong("revision")<socialSnapshot.getLong("revision"))social=null;}
            if(social!=null)socialSnapshot=social;
        }
        if(socialSnapshot==null)throw new java.io.IOException("Social snapshot unavailable");
        JSONObject out=new JSONObject(socialSnapshot.toString());
        if(multiplayerEnabled&&multiplayerSnapshot!=null){
            JSONObject mp=multiplayerSnapshot;if(!out.getString("selfId").equals(mp.getString("selfId")))throw new java.io.IOException("Multiplayer identity mismatch");String[] fields={"multiplayerVersion","capability","profiles","classification","profileCount"};
            for(String k:fields)if(mp.has(k))out.put(k,mp.get(k));
            // Legacy membership wins only while an already existing v2 room remains present.
            if(out.optJSONObject("room")==null||mp.optJSONObject("room")!=null){
                for(String k:new String[]{"room","rooms","totalRooms","messages","invites","joinRequests"})out.put(k,mp.has(k)?mp.get(k):k.equals("room")?JSONObject.NULL:k.equals("totalRooms")?0:new JSONArray());
                java.util.HashSet<String> members=new java.util.HashSet<>();JSONArray all=mp.optJSONArray("rooms");
                for(int i=0;all!=null&&i<all.length();i++){JSONObject room=all.optJSONObject(i);JSONArray roster=room==null?null:room.optJSONArray("members");for(int j=0;roster!=null&&j<roster.length();j++)members.add(roster.optString(j));}
                JSONObject mine=mp.optJSONObject("room");JSONArray ours=mine==null?null:mine.optJSONArray("members");for(int i=0;ours!=null&&i<ours.length();i++)members.add(ours.optString(i));
                JSONArray peers=out.optJSONArray("peers");for(int i=0;peers!=null&&i<peers.length();i++){JSONObject peer=peers.optJSONObject(i);if(peer!=null&&members.contains(peer.optString("peerId"))&&("online".equals(peer.optString("status"))||"in-room".equals(peer.optString("status"))))peer.put("status","in-room");}
                JSONObject own=mp.optJSONObject("room");out.put("messages",own==null?new JSONArray():own.optJSONArray("messages"));
                out.put("nextPage",JSONObject.NULL);
                out.put("transports",new JSONArray().put("relay-wss-v3"));
                JSONArray socialCaps=new JSONArray();JSONArray old=out.optJSONArray("socialCapabilities");
                for(int i=0;old!=null&&i<old.length();i++)if(!"join-request-v1".equals(old.optString(i)))socialCaps.put(old.get(i));
                out.put("socialCapabilities",socialCaps);out.put("roomCapabilities",new JSONArray());
            }
        }
        // A local presentation revision never becomes an authority/request proof.
        JSONObject visible=new JSONObject(out.toString());
        for(String k:new String[]{"revision","serverTimeMs","serverTime","serverUtc","requestId"})visible.remove(k);
        String key=visible.toString()+"/"+page;if(!key.equals(presentationKey)){presentationKey=key;combinedRevision++;}
        out.put("revision",combinedRevision).put("page",page);return out;
    }
    JSONObject pollMultiplayer(StationApi.Cancellation cancel)throws Exception {multiplayer(command("snapshot"),cancel);return compose(null);}
    synchronized JSONObject multiplayerRoom(String id)throws Exception {
        if(multiplayerSnapshot==null)return null;JSONObject own=multiplayerSnapshot.optJSONObject("room");
        if(own!=null&&(id.isEmpty()||id.equals(own.optString("roomId"))))return new JSONObject(own.toString());
        JSONArray rooms=multiplayerSnapshot.optJSONArray("rooms");for(int i=0;rooms!=null&&i<rooms.length();i++){JSONObject r=rooms.optJSONObject(i);if(r!=null&&id.equals(r.optString("roomId")))return new JSONObject(r.toString());}return null;
    }
    private synchronized boolean ownMultiplayer(){return multiplayerSnapshot!=null&&multiplayerSnapshot.optJSONObject("room")!=null;}
    private static boolean roomAction(String a){return java.util.Arrays.asList("create","join","ready","start","leave","relay-ticket","resume-relay","chat","request-join","accept-request","dismiss-request","invite","dismiss-invite").contains(a);}

    StationOnlineClient(Context context)throws Exception {app=StationAndroid.get(context);}
    static JSONObject command(String action)throws JSONException {
        return new JSONObject().put("action",action).put("requestId",UUID.randomUUID().toString());
    }
    JSONObject call(JSONObject request,boolean events,StationApi.Cancellation cancel)throws Exception {
        String action=request.optString("action");
        if(!events&&roomAction(action)&&(request.has("profileId")||ownMultiplayer())){
            if(java.util.Arrays.asList("request-join","accept-request","dismiss-request","invite","dismiss-invite").contains(action))throw new StationOnlineGame.Unavailable("Combine a partida pela conversa e entre pela lista de salas. Os convites desta modalidade ainda estão em preparação.");
            JSONObject clean=new JSONObject();
            String[] keys={"action","requestId","roomId","itemId","contentSha256","engineId","coreSha256","runtimeSha256","profileId","profileSha256","capacity","generation","linkId","value","nickname","text"};
            for(String key:keys)if(request.has(key))clean.put(key,request.get(key));
            if(action.equals("relay-ticket"))clean.put("action","ticket");if(action.equals("resume-relay"))clean.put("action","resume");
            if(!action.equals("create")&&!clean.has("generation")){
                JSONObject target=multiplayerRoom(clean.optString("roomId"));
                if(target==null)throw new StationOnlineGame.Unavailable("A sala mudou. Atualize a lista e confirme novamente.");
                clean.put("roomId",target.getString("roomId")).put("generation",target.getLong("generation"));
            }
            multiplayer(clean,cancel);return compose(null);
        }
        if(!events&&(action.equals("create")||action.equals("join")))throw StationMultiplayerProfile.unavailable();
        if(!events)request.put("page",page);
        StationApi.Session session=null;
        try(StationSessions.Lease lease=app.sessions.acquire(cancel)) {
            session=lease.session;JSONObject result=app.api.online(session,events,request,cancel);
            if(!events&&("relay-ticket".equals(request.optString("action"))||"resume-relay".equals(request.optString("action")))){
                JSONObject room=result.optJSONObject("room");
                JSONObject tunnel=room==null?null:room.optJSONObject("relay");
                if(tunnel!=null&&tunnel.has("ticket")){
                    String proof=app.api.relayRequestProof(session,tunnel.getString("ticket"));
                    if(proof!=null)tunnel.put("requestProof",proof);
                }
            }
            if(!events&&action.equals("enter")&&!multiplayerProbed){
                // Probe outside this lease below; acquiring nested leases can block renewal.
                multiplayerProbed=true;
            }
            return compose(result);
        }catch(StationApi.Failure e){if(session!=null&&e.sessionDenied())app.sessions.denied(session);throw e;}
    }
    void discoverMultiplayer(StationApi.Cancellation cancel)throws Exception {
        try{multiplayer(command("capabilities"),cancel);}catch(StationApi.Failure e){if(e.status!=404&&e.status!=503)throw e;}
    }
    JSONObject events(JSONObject snapshot,int page,StationApi.Cancellation cancel)throws Exception {
        synchronized(this){if(socialSnapshot!=null)snapshot=socialSnapshot;}
        JSONObject request=new JSONObject().put("requestId",UUID.randomUUID().toString()).put("page",page)
            .put("instance",snapshot.optString("instance","")).put("revision",snapshot.optLong("revision",0));
        return call(request,true,cancel);
    }
    StationCatalog.Item item(String id) {
        StationCoordinator.Library library=app.coordinator.current();return library==null?null:library.catalog.find(id);
    }
    String name(String id){StationCatalog.Item item=item(id);return item==null?"Jogo fora do catálogo carregado":item.name;}
    static String message(Throwable error) {
        if(error instanceof StationApi.Failure){String code=((StationApi.Failure)error).code;
            switch(code){
                case "STATION_MULTIPLAYER_GAME_UNCLASSIFIED":case "STATION_MULTIPLAYER_PROFILE_UNAPPROVED":case "STATION_MULTIPLAYER_CAPACITY_UNSUPPORTED":return "O jogo, o modo ou esta quantidade de jogadores ainda aguarda confirmação. Escolha uma opção aprovada.";
                case "STATION_MULTIPLAYER_GENERATION_MISMATCH":return "A sala mudou. Confira novamente os participantes antes de continuar.";
                case "STATION_MULTIPLAYER_ROOM_FULL":return "Esta sala já está completa.";
                case "STATION_MULTIPLAYER_NOT_READY":return "Todos os participantes precisam marcar Estou pronto.";
                case "STATION_MULTIPLAYER_DISABLED":return "As novas salas aguardam ativação no servidor.";
                case "STATION_MULTIPLAYER_PROFILE_UNAVAILABLE":case "STATION_MULTIPLAYER_PROFILE_INVALID":case "STATION_MULTIPLAYER_CAPACITY_INVALID":return "Este jogo ou quantidade de jogadores ainda não tem classificação confirmada para jogar online.";
                case "STATION_ONLINE_SOCIAL_DISABLED":return "As conversas privadas aguardam ativação do serviço.";
                case "STATION_ONLINE_REQUEST_EXISTS":return "Seu pedido já foi enviado. Aguarde a resposta do anfitrião.";
                case "STATION_ONLINE_JOIN_REQUEST_NOT_FOUND":return "Este pedido expirou ou já foi respondido.";
                case "STATION_ONLINE_TEXT_INVALID":return "Escreva uma mensagem de até 500 caracteres, sem quebras de linha.";
                case "STATION_ONLINE_CODE_INVALID":return "Confira os 8 caracteres do convite. Você pode colar o código completo.";
                case "STATION_ONLINE_CODE_NOT_FOUND":return "Este convite não está mais disponível. Peça um novo código da sala.";
                case "STATION_ONLINE_ROOM_NOT_FOUND":return "Esta sala foi encerrada. Peça um novo código ou convite.";
                case "STATION_ONLINE_PEER_NOT_FOUND":return "Este jogador não está mais disponível. Atualize a lista.";
                case "STATION_ONLINE_ALREADY_IN_ROOM":return "Você já está em uma sala. Saia dela antes de entrar em outra.";
                case "STATION_ONLINE_INVITE_EXISTS":return "Já existe um convite para este jogador. Aguarde a resposta ou a expiração.";
                case "STATION_ONLINE_INVITE_LIMIT":return "Há convites pendentes demais. Aguarde uma resposta antes de enviar outro.";
                case "STATION_ONLINE_HOST_REQUIRED":return "Somente quem criou a sala pode realizar esta ação.";
                case "STATION_ONLINE_ROOM_STARTED":return "Esta partida já começou. Volte ao lobby para encontrar outra sala.";
                case "STATION_ONLINE_INVITE_NOT_FOUND":return "Este convite expirou ou já foi usado.";
                case "STATION_ONLINE_ITEM_UNAVAILABLE":return "O jogo desta sala não está disponível no seu catálogo atual.";

                case "STATION_ONLINE_RELAY_DISABLED":return "A conexão pela internet aguarda ativação no servidor Station.";
                case "STATION_ONLINE_RELAY_FULL":return "Todas as conexões de partida estão ocupadas. Tente novamente em instantes.";
                case "STATION_ONLINE_RELAY_TICKET_INVALID":case "STATION_ONLINE_RELAY_ALREADY_ATTACHED":return "Esta conexão expirou ou já foi usada. Volte à sala e inicie outra partida.";
                case "STATION_ONLINE_DISABLED":return "As salas aguardam ativação no servidor. Seus jogos locais continuam disponíveis.";
                case "STATION_ONLINE_ENGINE_UNAVAILABLE":return "Este motor ainda não foi liberado para partidas no servidor.";
                case "STATION_ONLINE_BUILD_MISMATCH":return "Jogo, motor ou opções diferentes. Os dois aparelhos precisam da mesma edição.";
                case "STATION_ONLINE_ROOM_FULL":return "A sala já está cheia ou a partida começou.";
                case "STATION_ONLINE_NOT_READY":return "Os dois jogadores precisam marcar Pronto antes de iniciar.";
                case "STATION_ONLINE_BLOCKED":return "Não é possível entrar em contato com este jogador.";
                case "STATION_ONLINE_ENDPOINT_INVALID":return "Informe um endereço IP válido e uma porta entre 1024 e 65535.";
                case "STATION_ONLINE_ENTER_REQUIRED":return "Sua presença expirou. Toque em Reconectar.";
                case "STATION_ONLINE_CHAT_LIMIT":case "STATION_ONLINE_RATE_LIMITED":return "Muitas ações seguidas. Aguarde um instante e tente novamente.";
            }
            int status=((StationApi.Failure)error).status;
            if(status==404||status==503)return "O serviço de salas ainda não está disponível neste servidor.";
            if(status==401||status==403)return "Não foi possível validar seu acesso às salas. Volte às plataformas e confira sua conexão.";
        }
        if(error instanceof StationOnlineGame.Unavailable)return error.getMessage();
        return "Não foi possível concluir a conexão. Toque em Reconectar para tentar novamente.";
    }
}
