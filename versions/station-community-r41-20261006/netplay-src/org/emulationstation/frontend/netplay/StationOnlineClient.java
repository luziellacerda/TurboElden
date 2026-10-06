package org.emulationstation.frontend.netplay;

import android.content.Context;
import org.emulationstation.frontend.station.*;
import org.json.*;
import java.util.UUID;

/** Uses the existing pinned authority, Keystore identity and session lease. Never exposes bearer. */
final class StationOnlineClient {
    final StationAndroid app;volatile int page;
    StationOnlineClient(Context context)throws Exception {app=StationAndroid.get(context);}
    static JSONObject command(String action)throws JSONException {
        return new JSONObject().put("action",action).put("requestId",UUID.randomUUID().toString());
    }
    JSONObject call(JSONObject request,boolean events,StationApi.Cancellation cancel)throws Exception {
        if(!events)request.put("page",page);
        StationApi.Session session=null;
        try(StationSessions.Lease lease=app.sessions.acquire(cancel)) {
            session=lease.session;return app.api.online(session,events,request,cancel);
        }catch(StationApi.Failure e){if(session!=null&&e.sessionDenied())app.sessions.denied(session);throw e;}
    }
    JSONObject events(JSONObject snapshot,int page,StationApi.Cancellation cancel)throws Exception {
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
                case "STATION_ONLINE_SOCIAL_DISABLED":return "As conversas privadas aguardam ativação do serviço.";
                case "STATION_ONLINE_REQUEST_EXISTS":return "Seu pedido já foi enviado. Aguarde a resposta do anfitrião.";
                case "STATION_ONLINE_JOIN_REQUEST_NOT_FOUND":return "Este pedido expirou ou já foi respondido.";
                case "STATION_ONLINE_TEXT_INVALID":return "Escreva uma mensagem de até 500 caracteres, sem quebras de linha.";
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
