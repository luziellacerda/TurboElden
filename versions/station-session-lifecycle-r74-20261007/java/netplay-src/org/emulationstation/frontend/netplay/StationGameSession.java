package org.emulationstation.frontend.netplay;
import android.content.Context;
import android.content.Intent;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import android.app.Activity;
import org.emulationstation.frontend.auth.StationTaskNavigation;
import android.os.*;
import org.emulationstation.frontend.station.*;
import org.json.JSONObject;
import java.util.concurrent.*;

/** Main-process authority. v2 retains membership in background; only event 4 is human leave. */
final class StationGameSession {
    static final String EXTRA="station.sessionEvents",ANCHOR_EXTRA="station.sessionAnchor";
    private static final StationSessionRegistry<StationGameSession> anchors=new StationSessionRegistry<>();
    private final String anchorId=UUID.randomUUID().toString();
    private final AtomicBoolean ticketScheduled=new AtomicBoolean();
    private final Context app;private final int taskId;private final String room;private final JSONObject binding;
    private final boolean recovery;
    private final ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor();
    private volatile boolean visible,closed,listening,failed;private boolean acknowledged,humanLeft,lifecycleReleased;private ExecutorService departure;
    private volatile StationApi.Cancellation pending;private volatile ResultReceiver reply;
    private ScheduledFuture<?> heartbeat;
    private StationGameSession(Context app,String room,JSONObject binding){this.app=app.getApplicationContext();taskId=app instanceof Activity?((Activity)app).getTaskId():-1;this.room=room;this.binding=binding;recovery=binding!=null&&"station-stream.v2".equals(binding.optString("recoveryProtocol"));}
    static ResultReceiver create(Context context,String room){return createOwner(new StationGameSession(context,room,null));}
    static ResultReceiver create(Context context,JSONObject room){try{
        JSONObject bound=new JSONObject();for(String key:new String[]{"roomId","engineId","coreSha256","runtimeSha256","contentSha256","optionsSha256","recoveryProtocol","generation"})if(room.has(key))bound.put(key,room.get(key));
        return createOwner(new StationGameSession(context,room.getString("roomId"),bound));
    }catch(Exception error){throw new IllegalArgumentException("Invalid Station recovery binding",error);}}
    static Intent attach(Context context,JSONObject room,Intent intent){
        StationGameSession owner=null;
        try{JSONObject bound=new JSONObject();for(String key:new String[]{"roomId","engineId","coreSha256","runtimeSha256","contentSha256","optionsSha256","recoveryProtocol","generation"})if(room.has(key))bound.put(key,room.get(key));
            owner=new StationGameSession(context,room.getString("roomId"),bound);
            ResultReceiver callback=createOwner(owner);
            anchors.put(owner.anchorId,owner.room,owner.anchorGeneration(),owner);
            return intent.putExtra(EXTRA,callback).putExtra(ANCHOR_EXTRA,owner.anchorId);
        }catch(Exception error){if(owner!=null)owner.anchorEnded();throw new IllegalArgumentException("Invalid Station session binding",error);}
    }
    /** Result identity lives in the caller so an early native-process crash cannot strand a launch. */
    static final class LaunchReturn {
        private static final int FIRST_REQUEST=0x5354;
        private int nextRequest=FIRST_REQUEST,request=-1;private String key,room;private long generation=-1;
        boolean pending(){return key!=null;}
        int prepare(Intent intent,String room,long generation){
            if(pending()||nextRequest==Integer.MAX_VALUE)throw new IllegalStateException("Native result already pending");
            String key=intent==null?null:intent.getStringExtra(ANCHOR_EXTRA);
            if(anchorOwner(key,room,generation)==null)throw new IllegalArgumentException("Missing native result identity");
            this.key=key;this.room=room;this.generation=generation;request=nextRequest++;return request;
        }
        Bundle save(){Bundle saved=new Bundle();saved.putInt("next",nextRequest);if(pending()){saved.putInt("request",request);saved.putString("key",key);saved.putString("room",room);saved.putLong("generation",generation);}return saved;}
        void restore(Bundle saved){
            if(saved==null)return;int next=saved.getInt("next",FIRST_REQUEST);if(next>=FIRST_REQUEST)nextRequest=next;
            String candidate=saved.getString("key"),r=saved.getString("room");int code=saved.getInt("request",-1);long g=saved.getLong("generation",-1);
            if(candidate!=null&&candidate.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")&&r!=null&&r.matches("[0-9a-f]{32}")&&g>=0&&code>=FIRST_REQUEST&&code<nextRequest){key=candidate;room=r;generation=g;request=code;}
        }
        boolean completed(int requestCode){if(!pending()||requestCode!=request)return false;release();return true;}
        void abort(Intent intent){if(pending()&&intent!=null&&key.equals(intent.getStringExtra(ANCHOR_EXTRA)))release();}
        private void release(){try{StationGameSession owner=anchorOwner(key,room,generation);if(owner!=null)owner.anchorEnded();}finally{key=null;room=null;generation=-1;request=-1;}}
    }
    private long anchorGeneration(){return recovery?binding.optLong("generation",-1):0;}
    static StationGameSession anchorOwner(String key,String room,long generation){return anchors.find(key,room,generation);}
    static void discardLaunch(Intent intent,String room,long generation){if(intent==null)return;String key=intent.getStringExtra(ANCHOR_EXTRA);StationGameSession owner=anchors.find(key,room,generation);if(owner!=null){anchors.remove(key,owner);owner.closed=true;owner.pause();owner.worker.shutdown();}}
    // Binding loss is local lifecycle, never a remote leave/recovery-failed command.
    // Event 4 remains accepted after this cleanup so cross-Binder delivery order is harmless.
    synchronized void anchorEnded(){anchors.remove(anchorId,this);if(!closed){lifecycleReleased=true;closed=true;visible=false;StationTaskNavigation.gameEnded(this);pause();reply=null;worker.shutdown();}}
    private static ResultReceiver createOwner(StationGameSession owner){return StationSessionChannel.transport(new ResultReceiver(new Handler(Looper.getMainLooper())){
        @Override protected void onReceiveResult(int event,Bundle data){owner.event(event,data);}
    });}
    private synchronized void event(int event,Bundle data){
        // A terminal recovery panel can still emit one later human exit.
        if(event==4){
            if(humanLeft)return;humanLeft=true;anchors.remove(anchorId,this);StationTaskNavigation.gameEnded(this);closed=true;visible=false;pause();reply=null;worker.shutdown();
            departure=Executors.newSingleThreadExecutor();
            departure.execute(()->{try{StationOnlineClient c=new StationOnlineClient(app);JSONObject snapshot=c.call(StationOnlineClient.command("heartbeat"),false,new StationApi.Cancellation());JSONObject r=snapshot.optJSONObject("room");if(r!=null&&room.equals(r.optString("roomId")))c.call(StationOnlineClient.command("leave"),false,new StationApi.Cancellation());}catch(Exception ignored){}finally{departure.shutdown();}});
            return;
        }
        if(event==6&&recovery&&!failed&&!humanLeft&&(!closed||lifecycleReleased)){
            anchors.remove(anchorId,this);StationTaskNavigation.gameEnded(this);failed=true;visible=false;lifecycleReleased=false;pause();reply=null;
            ExecutorService terminal=worker.isShutdown()?Executors.newSingleThreadExecutor():worker;
            terminal.execute(()->{try{new StationOnlineClient(app).call(StationOnlineClient.command("recovery-failed").put("roomId",room).put("generation",binding.getLong("generation")),false,new StationApi.Cancellation());}catch(Exception ignored){}finally{terminal.shutdown();}});
            return;
        }
        if(closed||failed)return;
        if(event==1){StationTaskNavigation.gameVisible(this,taskId);visible=true;if(data!=null)reply=StationSessionChannel.read(data,"reply");
            if(heartbeat==null)heartbeat=worker.scheduleWithFixedDelay(this::sync,0,20,TimeUnit.SECONDS);
        }else if(event==2){visible=false;if(!recovery)pause();}
        else if(event==3){listening=true;if(visible)worker.execute(this::sync);}
        else if(event==5&&recovery&&!failed&&ticketScheduled.compareAndSet(false,true)){
            try{worker.execute(()->{try{ticket();}finally{ticketScheduled.set(false);}});}catch(RejectedExecutionException closedWorker){ticketScheduled.set(false);}
        }

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
    private synchronized void roomEnded(){anchors.remove(anchorId,this);StationTaskNavigation.gameEnded(this);closed=true;pause();reply=null;worker.shutdown();}
    private void send(int event,Bundle value){ResultReceiver target=reply;if(target!=null&&!closed)target.send(event,value);}
    private void notice(String message){if(visible){Bundle value=new Bundle();value.putString("message",message);send(100,value);}}
}
