package org.emulationstation.frontend.netplay;
import android.app.*;
import android.content.*;
import android.os.*;
import java.lang.ref.WeakReference;
import java.util.*;
import java.util.concurrent.*;
import org.emulationstation.frontend.station.*;
import org.json.*;

/** Main catalogue presence only. Rooms and gameplay take over when the catalogue is hidden. */
public final class StationPresence {
    private static final ExecutorService worker=Executors.newSingleThreadExecutor();
    private static WeakReference<Activity> current=new WeakReference<>(null);
    private static volatile boolean active,installed;private static volatile int generation;
    private static volatile StationApi.Cancellation cancellation;private static Future<?> future;
    private static final Set<String> shown=new LinkedHashSet<>();
    private static long retryAfter;
    public static synchronized void install(Context context){
        if(installed||StationProcess.isNetplay())return;installed=true;
        ((Application)context.getApplicationContext()).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
            public void onActivityResumed(Activity a){current=new WeakReference<>(a);}
            public void onActivityPaused(Activity a){if(current.get()==a)current.clear();}
            public void onActivityCreated(Activity a,Bundle b){}public void onActivityStarted(Activity a){}
            public void onActivityStopped(Activity a){}public void onActivitySaveInstanceState(Activity a,Bundle b){}public void onActivityDestroyed(Activity a){if(current.get()==a)current.clear();}
        });
    }
    public static synchronized void foreground(Context context,boolean visible){
        if(StationProcess.isNetplay())return;install(context);
        if(active==visible)return;active=visible;generation++;
        if(cancellation!=null)cancellation.cancel();if(future!=null)future.cancel(true);
        if(!visible||SystemClock.elapsedRealtime()<retryAfter)return;
        final int mine=generation;Context app=context.getApplicationContext();StationApi.Cancellation cancel=new StationApi.Cancellation();cancellation=cancel;
        future=worker.submit(()->{
            try{
                StationOnlineClient c=new StationOnlineClient(app);if(c.app.coordinator.current()==null)return;
                String nickname=app.getSharedPreferences("station-online-profile",0).getString("nickname","Jogador");
                JSONObject snapshot=c.call(StationOnlineClient.command("enter").put("nickname",nickname),false,cancel);long heartbeat=SystemClock.elapsedRealtime();
                while(active&&generation==mine&&!cancel.cancelled()){
                    invitations(app,snapshot,mine);
                    if(SystemClock.elapsedRealtime()-heartbeat>=20000){snapshot=c.call(StationOnlineClient.command("heartbeat"),false,cancel);heartbeat=SystemClock.elapsedRealtime();}
                    snapshot=c.events(snapshot,0,cancel);
                }
            }catch(Exception error){
                if(!cancel.cancelled())retryAfter=SystemClock.elapsedRealtime()+300000;
                // Optional presence failure never blocks catalogue, covers, login or downloads.
            }
        });
    }
    private static void invitations(Context context,JSONObject snapshot,int epoch){
        JSONArray invites=snapshot.optJSONArray("invites");if(invites==null)return;
        for(int i=0;i<invites.length();i++){JSONObject invitation=invites.optJSONObject(i);if(invitation==null)continue;String id=invitation.optString("inviteId");synchronized(shown){if(shown.contains(id))continue;shown.add(id);while(shown.size()>64)shown.remove(shown.iterator().next());}
            Activity a=current.get();if(a==null||a.isFinishing()||a.isDestroyed())continue;
            a.runOnUiThread(()->{if(!active||generation!=epoch||a.isFinishing())return;new AlertDialog.Builder(a).setTitle("LZ GAMES • Convite recebido").setMessage("Um jogador convidou você para uma partida. Abra as salas para conferir o jogo e aceitar.").setNegativeButton("Agora não",null).setPositiveButton("Ver convite",(d,w)->a.startActivity(new Intent(a,StationRoomsActivity.class))).show();});break;
        }
    }
}
