package org.emulationstation.frontend.netplay;
import android.content.Context;
import android.os.*;
import org.emulationstation.frontend.station.*;
import org.json.JSONObject;
import java.util.concurrent.*;

/** Main-process session owner. Native process reports lifecycle/listen events over private Binder. */
final class StationGameSession {
    static final String EXTRA="station.sessionEvents";
    private final Context app;private final String room;
    private final ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor();
    private volatile boolean visible,closed,listening;private boolean acknowledged;
    private volatile StationApi.Cancellation pending;private volatile ResultReceiver reply;
    private ScheduledFuture<?> heartbeat;
    private StationGameSession(Context app,String room){this.app=app;this.room=room;}
    static ResultReceiver create(Context context,String room){
        StationGameSession owner=new StationGameSession(context.getApplicationContext(),room);
        return new ResultReceiver(new Handler(Looper.getMainLooper())){
            @Override protected void onReceiveResult(int event,Bundle data){owner.event(event,data);}
        };
    }
    private void event(int event,Bundle data){
        if(closed)return;
        if(event==1){visible=true;if(data!=null)reply=data.getParcelable("reply");
            if(heartbeat==null)heartbeat=worker.scheduleWithFixedDelay(this::sync,0,20,TimeUnit.SECONDS);
        }else if(event==2){visible=false;pause();}
        else if(event==3){listening=true;if(visible)worker.execute(this::sync);}
        else if(event==4){closed=true;visible=false;pause();reply=null;
            worker.execute(()->{try{StationOnlineClient c=new StationOnlineClient(app);JSONObject s=c.call(StationOnlineClient.command("heartbeat"),false,new StationApi.Cancellation());JSONObject r=s.optJSONObject("room");if(r!=null&&room.equals(r.optString("roomId")))c.call(StationOnlineClient.command("leave"),false,new StationApi.Cancellation());}catch(Exception ignored){}finally{worker.shutdown();}});
        }
    }
    private void pause(){if(heartbeat!=null){heartbeat.cancel(true);heartbeat=null;}if(pending!=null)pending.cancel();}
    private void sync(){
        if(!visible||closed)return;StationApi.Cancellation cancel=new StationApi.Cancellation();pending=cancel;
        try{StationOnlineClient c=new StationOnlineClient(app);
            if(listening&&!acknowledged){c.call(StationOnlineClient.command("host-listening").put("roomId",room),false,cancel);acknowledged=true;android.util.Log.i("StationRooms","game stage=host-listening-ack");}
            JSONObject snapshot=c.call(StationOnlineClient.command("heartbeat"),false,cancel);JSONObject r=snapshot.optJSONObject("room");
            if(r==null||!room.equals(r.optString("roomId")))notice("A sala foi encerrada. Você pode sair pelo menu do emulador.");
        }catch(Exception error){if(!cancel.cancelled())android.util.Log.w("StationRooms","game stage=session-sync type="+error.getClass().getSimpleName()+(error instanceof StationApi.Failure?" code="+((StationApi.Failure)error).code:""));if(!cancel.cancelled()&&error instanceof StationApi.Failure&&((StationApi.Failure)error).sessionDenied())notice("O servidor não confirmou o acesso à sala. Encerre a partida e confira sua licença.");}
        finally{pending=null;}
    }
    private void notice(String message){ResultReceiver target=reply;if(target!=null&&visible&&!closed){Bundle value=new Bundle();value.putString("message",message);target.send(100,value);}}
}
