"""Prescribed navigation/lifecycle edits over the frozen incoming recovery source."""

def one(source,before,after):
    if source.count(before)!=1:raise ValueError('Navigation source boundary changed: '+before[:60])
    return source.replace(before,after)

def expected_session(source):
    source=one(source,'import android.content.Context;','import android.content.Context;\nimport android.app.Activity;\nimport org.emulationstation.frontend.auth.StationTaskNavigation;')
    source=one(source,'private final Context app;private final String room;','private final Context app;private final int taskId;private final String room;')
    source=one(source,'private volatile boolean visible,closed,listening,failed;private boolean acknowledged;','private volatile boolean visible,closed,listening,failed;private boolean acknowledged,humanLeft;private ExecutorService departure;')
    source=one(source,'this.app=app;this.room=room;','this.app=app.getApplicationContext();taskId=app instanceof Activity?((Activity)app).getTaskId():-1;this.room=room;')
    if source.count('new StationGameSession(context.getApplicationContext(),')!=2:raise ValueError('Session creation boundary changed')
    source=source.replace('new StationGameSession(context.getApplicationContext(),','new StationGameSession(context,')
    source=one(source,'if(event==1){visible=true;','if(event==1){StationTaskNavigation.gameVisible(this,taskId);visible=true;')
    source=one(source,'else if(event==6&&recovery&&!failed){failed=true;worker.execute(()->{','else if(event==6&&recovery&&!failed){StationTaskNavigation.gameEnded(this);failed=true;visible=false;pause();reply=null;worker.execute(()->{')
    source=one(source,'false,new StationApi.Cancellation());}catch(Exception ignored){}\n        });}', 'false,new StationApi.Cancellation());}catch(Exception ignored){}finally{worker.shutdown();}\n        });}')
    old_exit='''        else if(event==4){closed=true;visible=false;pause();reply=null;
            worker.execute(()->{try{StationOnlineClient c=new StationOnlineClient(app);JSONObject snapshot=c.call(StationOnlineClient.command("heartbeat"),false,new StationApi.Cancellation());JSONObject r=snapshot.optJSONObject("room");if(r!=null&&room.equals(r.optString("roomId")))c.call(StationOnlineClient.command("leave"),false,new StationApi.Cancellation());}catch(Exception ignored){}finally{worker.shutdown();}});
        }
'''
    source=one(source,old_exit,'')
    entry='''    private void event(int event,Bundle data){
        // A terminal recovery panel can still emit one later human exit.
        if(event==4){
            if(humanLeft)return;humanLeft=true;StationTaskNavigation.gameEnded(this);closed=true;visible=false;pause();reply=null;worker.shutdown();
            departure=Executors.newSingleThreadExecutor();
            departure.execute(()->{try{StationOnlineClient c=new StationOnlineClient(app);JSONObject snapshot=c.call(StationOnlineClient.command("heartbeat"),false,new StationApi.Cancellation());JSONObject r=snapshot.optJSONObject("room");if(r!=null&&room.equals(r.optString("roomId")))c.call(StationOnlineClient.command("leave"),false,new StationApi.Cancellation());}catch(Exception ignored){}finally{departure.shutdown();}});
            return;
        }
        if(closed||failed)return;'''
    source=one(source,'    private void event(int event,Bundle data){\n        if(closed)return;',entry)
    source=one(source,'if((!visible&&!recovery)||closed)return;','if((!visible&&!recovery)||closed||failed)return;')
    source=one(source,'send(102,value);closed=true;pause();reply=null;worker.shutdown();','send(102,value);roomEnded();')
    source=one(source,'    private void send(int event,Bundle value){','    private synchronized void roomEnded(){StationTaskNavigation.gameEnded(this);closed=true;pause();reply=null;worker.shutdown();}\n    private void send(int event,Bundle value){')
    source=one(source,'private void event(int event,Bundle data){','private synchronized void event(int event,Bundle data){')
    return source

def expected_presence(source):
    source=one(source,'import android.content.*;','import android.content.*;\nimport org.emulationstation.frontend.auth.StationTaskNavigation;')
    return one(source,'a.startActivity(new Intent(a,StationRoomsActivity.class).putExtra("station.peerId",peer));','StationTaskNavigation.open(a,new Intent(a,StationRoomsActivity.class).putExtra("station.peerId",peer));')
