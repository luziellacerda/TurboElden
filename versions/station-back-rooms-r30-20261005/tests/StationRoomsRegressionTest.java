package org.emulationstation.frontend.netplay;
import org.json.*;
import java.io.*;
import java.nio.file.*;
import org.emulationstation.frontend.station.*;

public final class StationRoomsRegressionTest {
    static int checks;
    static void check(boolean value,String reason){checks++;if(!value)throw new AssertionError(reason);}
    interface Job{void run()throws Exception;}
    static void rejected(Job job,String text)throws Exception{try{job.run();throw new AssertionError("Accepted "+text);}catch(StationOnlineGame.Unavailable e){check(e.getMessage().contains(text),e.getMessage());}}
    static JSONObject room(int count,int ready)throws Exception {
        JSONArray members=new JSONArray(),confirmation=new JSONArray();
        for(int i=0;i<count;i++){members.put("p"+i);if((ready&(1<<i))!=0)confirmation.put("p"+i);}
        return new JSONObject().put("selfId","p0").put("transports",new JSONArray().put("relay-wss-v1"))
            .put("room",new JSONObject().put("hostId","p0").put("state","waiting").put("members",members).put("ready",confirmation));
    }
    public static void main(String[] args)throws Exception {
        for(int count=0;count<=3;count++)for(int ready=0;ready<8;ready++){
            JSONObject s=room(count,ready);boolean expected=count==2&&(ready&3)==3;
            check(StationRoomStartState.reason(s).isEmpty()==expected,"readiness "+count+" "+ready);
        }
        check(!StationRoomStartState.reason(null).isEmpty(),"null snapshot");
        JSONObject s=room(2,3);s.put("selfId","p1");check(!StationRoomStartState.reason(s).isEmpty(),"guest start");
        s=room(2,3);s.getJSONObject("room").put("state","starting");check(!StationRoomStartState.reason(s).isEmpty(),"already starting");
        s=room(2,3);s.put("transports",new JSONArray().put("direct"));check(!StationRoomStartState.reason(s).isEmpty(),"no relay");
        s=room(2,3);s.getJSONObject("room").put("members",new JSONArray().put("p0").put("p0"));check(!StationRoomStartState.reason(s).isEmpty(),"duplicate participant");
        s=room(2,3);s.getJSONObject("room").put("members",new JSONArray().put("p1").put("p2"));check(!StationRoomStartState.reason(s).isEmpty(),"host absent");
        StationRoomFeedback f=new StationRoomFeedback();
        f.fail("Baixe este jogo primeiro.");
        for(int i=0;i<10;i++)check(f.text(room(1,0),false).equals("Baixe este jogo primeiro."),"refresh erased error");
        f.begin();check(f.text(room(1,0),false).contains("outro jogador"),"single player explanation");
        check(f.text(room(2,0),false).contains("Marque"),"host not ready");
        check(f.text(room(2,1),false).contains("outro jogador marcar"),"guest not ready");
        check(f.text(room(2,3),false).contains("pode iniciar"),"all ready");
        check(f.text(room(2,3),true).contains("solicitação"),"busy feedback");
        StationFrontend.failure=new IOException("Baixe o jogo antes de criar ou entrar em uma sala");
        rejected(()->StationOnlineGame.installedRom("fixture"),"Baixe este jogo primeiro");
        StationFrontend.failure=new IOException("Catálogo não preparado");
        rejected(()->StationOnlineGame.installedRom("fixture"),"Volte ao catálogo");
        StationFrontend.failure=new IOException("private path /secret token hidden");
        rejected(()->StationOnlineGame.installedRom("fixture"),"Não foi possível acessar");
        StationFrontend.failure=null;StationFrontend.path=null;
        rejected(()->StationOnlineGame.installedRom("fixture"),"Baixe este jogo");
        Path fixture=Paths.get(args[0],"synthetic.sfc");Files.write(fixture,new byte[]{1,2,3,4});
        StationFrontend.path=fixture.toString();check(StationOnlineGame.installedRom("fixture").equals(fixture.toFile()),"installed ROM unchanged");
        check(StationOnlineGame.sha(fixture.toFile(),new StationApi.Cancellation()).equals("9f64a747e1b97f131fabb6b447296c9b6f0201e79fb3c5356e6c77e89b6a806a"),"ROM hash");
        StationFrontend.path=fixture.resolveSibling("absent.sfc").toString();
        rejected(()->StationOnlineGame.installedRom("fixture"),"arquivo do jogo");
        System.out.println(checks+" room readiness, feedback and actual game-path boundary checks passed");
    }
}
