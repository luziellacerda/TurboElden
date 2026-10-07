package org.emulationstation.frontend.netplay;
import android.content.Context;
import android.app.Activity;
import org.emulationstation.frontend.auth.StationTaskNavigation;
import android.os.*;
import org.emulationstation.frontend.station.*;
import org.json.JSONObject;
import java.util.concurrent.*;

/** Main-process authority. v2 retains membership in background; only event 4 is human leave. */
final class StationGameSession {
    static final String EXTRA="station.sessionEvents";
    private final Context app;private final int taskId;private final String room;private final JSONObject binding;
    private final boolean recovery;
    private final ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor();
    private volatile boolean visible,closed,listening,failed;private boolean acknowledged,humanLeft;private ExecutorService departure;
    private volatile StationApi.Cancellation pending;private volatile ResultReceiver reply;
    private ScheduledFuture<?> heartbeat;
    private StationGameSession(Context app,String room,JSONObject binding){this.app=app.getApplicationContext();taskId=app instanceof Activity?((Activity)app).getTaskId():-1;this.room=room;this.binding=binding;recovery=binding!=null&&"station-stream.v2".equals(binding.optString("recoveryProtocol"));}
    static ResultReceiver create(Context context,String room){return createOwner(new StationGameSession(context,room,null));}
    static ResultReceiver create(Context context,JSONObject room){try{
        JSONObject bound=new JSONObject();for(String key:new String[]{"roomId","engineId","coreSha256","runtimeSha256","contentSha256","optionsSha256","recoveryProtocol","generation"})if(room.has(key))bound.put(key,room.get(key));
        return createOwner(new StationGameSession(context,room.getString("roomId"),bound));
    }catch(Exception error){throw new IllegalArgumentException("Invalid Station recovery binding",error);}}
    private static ResultReceiver createOwner(StationGameSession owner){return StationSessionChannel.transport(new ResultReceiver(new Handler(Looper.getMainLooper())){
        @Override protected void onReceiveResult(int event,Bundle data){owner.event(event,data);}
    });}
    private synchronized void event(int event,Bundle data){
        // A terminal recovery panel can still emit one later human exit.
        if(event==4){
            if(humanLeft)return;humanLeft=true;StationTaskNavigation.gameEnded(this);closed=true;visible=false;pause();reply=null;worker.shutdown();
            departure=Executors.newSingleThreadExecutor();
            departure.execute(()->{try{StationOnlineClient c=new StationOnlineClient(app);JSONObject snapshot=c.call(StationOnlineClient.command("heartbeat"),false,new StationApi.Cancellation());JSONObject r=snapshot.optJSONObject("room");if(r!=null&&room.equals(r.optString("roomId")))c.call(StationOnlineClient.command("leave"),false,new StationApi.Cancellation());}catch(Exception ignored){}finally{departure.shutdown();}});
            return;
        }
        if(closed||failed)return;
        if(event==1){StationTaskNavigation.gameVisible(this,taskId);visible=true;if(data!=null)reply=StationSessionChannel.read(data,"reply");
            if(heartbeat==null)heartbeat=worker.scheduleWithFixedDelay(this::sync,0,20,TimeUnit.SECONDS);
        }else if(event==2){visible=false;if(!recovery)pause();}
        else if(event==3){listening=true;if(visible)worker.execute(this::sync);}
        else if(event==5&&recovery&&!failed)worker.execute(this::ticket);
        else if(event==6&&recovery&&!failed){StationTaskNavigation.gameEnded(this);failed=true;visible=false;pause();reply=null;worker.execute(()->{
            try{new StationOnlineClient(app).call(StationOnlineClient.command("recovery-failed").put("roomId",room).put("generation",binding.getLong("generation")),false,new StationApi.Cancellation());}catch(Exception ignored){}finally{worker.shutdown();}
        });}
    }
    private void pause(){if(heartbeat!=null){heartbeat.cancel(true);heartbeat=null;}if(pending!=null)pending.cancel();}
    private void ticket(){
        if(closed||failed||!visible)return;StationApi.Cancellation cancel=new StationApi.Cancellation();pending=cancel;
        try{
            JSONObject request=StationOnlineClient.command("resume-relay");
            for(String key:new String[]{"roomId","engineId","coreSha256","runtimeSha256","contentSha256","optionsSha256","recoveryProtocol","generation"})request.put(key,binding.get(key));
            JSONObject snapshot=new StationOnlineClient(app).call(request,false,cancel);
            JSONObject r=snapshot.getJSONObject("room");
            if(!room.equals(r.getString("roomId"))||r.getLong("generation")!=binding.getLong("generation"))throw new IllegalStateException("Generation changed");
            JSONObject descriptor=r.getJSONObject("relay");
            if(!"station-stream.v2".equals(descriptor.getString("protocol"))||descriptor.getInt("expiresInSeconds")<=0)throw new IllegalStateException("Invalid recovery descriptor");
            Bundle response=new Bundle();response.putString("ticket",descriptor.getString("ticket"));response.putString("proof",descriptor.getString("requestProof"));response.putInt("windowBytes",descriptor.getInt("windowBytes"));send(101,response);
        }catch(Exception error){Bundle response=new Bundle();boolean terminal=error instanceof StationApi.Failure&&
                (((StationApi.Failure)error).licenseDenied()||((StationApi.Failure)error).status==404||((StationApi.Failure)error).code.equals("STATION_RECOVERY_GENERATION_MISMATCH")||((StationApi.Failure)error).code.equals("STATION_RECOVERY_UNRECOVERABLE")||((StationApi.Failure)error).code.equals("STATION_ONLINE_BUILD_MISMATCH"));
            response.putBoolean("terminal",terminal);send(102,response);
        }finally{pending=null;}
    }
    private void sync(){
        if((!visible&&!recovery)||closed||failed)return;StationApi.Cancellation cancel=new StationApi.Cancellation();pending=cancel;
        long started=SystemClock.elapsedRealtime();
        try{StationOnlineClient c=new StationOnlineClient(app);
            if(listening&&!acknowledged){c.call(StationOnlineClient.command("host-listening").put("roomId",room),false,cancel);acknowledged=true;android.util.Log.i("StationRooms","game stage=host-listening-ack");}
            JSONObject snapshot=c.call(StationOnlineClient.command("heartbeat"),false,cancel);JSONObject r=snapshot.optJSONObject("room");
            android.util.Log.i("StationRooms","game stage=session-heartbeat elapsedMs="+(SystemClock.elapsedRealtime()-started)+" sameRoom="+(r!=null&&room.equals(r.optString("roomId"))));
            if(r==null||!room.equals(r.optString("roomId"))){if(recovery){Bundle value=new Bundle();value.putBoolean("terminal",true);send(102,value);roomEnded();}else notice("A sala foi encerrada. Você pode sair pelo menu do emulador.");}
            else if(recovery&&"unrecoverable".equals(r.optString("state"))){Bundle value=new Bundle();value.putBoolean("terminal",true);send(102,value);}
        }catch(Exception error){if(!cancel.cancelled())android.util.Log.w("StationRooms","game stage=session-sync type="+error.getClass().getSimpleName()+(error instanceof StationApi.Failure?" code="+((StationApi.Failure)error).code:""));
            if(recovery&&!cancel.cancelled()&&error instanceof StationApi.Failure&&((StationApi.Failure)error).licenseDenied()){Bundle value=new Bundle();value.putBoolean("terminal",true);send(102,value);}
            if(!recovery&&!cancel.cancelled()&&error instanceof StationApi.Failure&&((StationApi.Failure)error).sessionDenied())notice("O servidor não confirmou o acesso à sala. Encerre a partida e confira sua licença.");
        }finally{pending=null;}
    }
    private synchronized void roomEnded(){StationTaskNavigation.gameEnded(this);closed=true;pause();reply=null;worker.shutdown();}
    private void send(int event,Bundle value){ResultReceiver target=reply;if(target!=null&&!closed)target.send(event,value);}
    private void notice(String message){if(visible){Bundle value=new Bundle();value.putString("message",message);send(100,value);}}
}
