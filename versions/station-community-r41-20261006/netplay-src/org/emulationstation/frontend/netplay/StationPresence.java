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
    private static android.widget.PopupWindow notice;
    static void markRead(String messageId){remember("message:"+messageId);}
    private static void remember(String id){synchronized(shown){shown.add(id);while(shown.size()>128)shown.remove(shown.iterator().next());}}
    
    public static synchronized void install(Context context){
        if(installed||StationProcess.isNetplay())return;installed=true;
        ((Application)context.getApplicationContext()).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
            public void onActivityResumed(Activity a){current=new WeakReference<>(a);foreground(a,eligible(a));}
            public void onActivityPaused(Activity a){if(current.get()==a){current.clear();if(notice!=null){notice.dismiss();notice=null;}foreground(a,false);}}
            public void onActivityCreated(Activity a,Bundle b){}public void onActivityStarted(Activity a){}
            public void onActivityStopped(Activity a){}public void onActivitySaveInstanceState(Activity a,Bundle b){}public void onActivityDestroyed(Activity a){if(current.get()==a)current.clear();}
        });
    }
    private static boolean eligible(Activity a){return a!=null&&!(a instanceof StationRoomsActivity)&&!a.getClass().getName().contains(".auth.")&&!StationProcess.isNetplay();}
    public static synchronized void foreground(Context context,boolean visible){
        if(StationProcess.isNetplay())return;install(context);
        Activity shownActivity=current.get();if(shownActivity!=null){if(!eligible(shownActivity))visible=false;else if(!visible)visible=true;}
        if(active==visible&&future!=null&&!future.isDone())return;active=visible;generation++;
        if(cancellation!=null)cancellation.cancel();if(future!=null)future.cancel(true);
        if(!visible)return;
        final int mine=generation;Context app=context.getApplicationContext();StationApi.Cancellation cancel=new StationApi.Cancellation();cancellation=cancel;
        future=worker.submit(()->{
            int failures=0;
            while(active&&generation==mine&&!cancel.cancelled())try{
                StationOnlineClient c=new StationOnlineClient(app);if(c.app.coordinator.current()==null){Thread.sleep(1000);continue;}
                android.content.SharedPreferences profile=app.getSharedPreferences("station-online-profile",0);
                String nickname=profile.getString("nickname","Jogador");
                if("Jogador".equals(nickname)){String display=c.app.coordinator.current().displayName;if(display!=null&&!display.trim().isEmpty()){nickname=display.trim().replaceAll("[\\p{Cntrl}]", " ");if(nickname.length()>24)nickname=nickname.substring(0,24);profile.edit().putString("nickname",nickname).apply();}}
                JSONObject snapshot=c.call(StationOnlineClient.command("enter").put("nickname",nickname),false,cancel);
                if(profile.getBoolean("leaveOnCatalog",false)){snapshot=c.call(StationOnlineClient.command("leave"),false,cancel);profile.edit().remove("leaveOnCatalog").apply();}
                long heartbeat=SystemClock.elapsedRealtime();failures=0;
                while(active&&generation==mine&&!cancel.cancelled()){
                    invitations(app,snapshot,mine);
                    if(SystemClock.elapsedRealtime()-heartbeat>=20000){snapshot=c.call(StationOnlineClient.command("heartbeat"),false,cancel);heartbeat=SystemClock.elapsedRealtime();}
                    snapshot=c.events(snapshot,0,cancel);
                }
            }catch(Exception error){
                if(cancel.cancelled()||!active||mine!=generation||Thread.currentThread().isInterrupted())break;
                // Bounded reconnection only while this foreground owner is active. No five-minute dead state.
                try{Thread.sleep(Math.min(30000,1000L<<Math.min(++failures,5)));}catch(InterruptedException stop){break;}
            }
        });
    }
    private static void invitations(Context context,JSONObject snapshot,int epoch){
        Activity a=current.get();if(!eligible(a)||a.isFinishing()||a.isDestroyed())return;
        JSONArray invites=snapshot.optJSONArray("invites"),messages=snapshot.optJSONArray("directMessages");
        for(int type=0;type<2;type++){JSONArray rows=type==0?invites:messages;if(rows==null)continue;
            for(int i=0;i<rows.length();i++){JSONObject row=rows.optJSONObject(i);if(row==null)continue;
                if(type==1&&!snapshot.optString("selfId").equals(row.optString("toPeerId")))continue;
                final String id=(type==0?"invite:":"message:")+row.optString(type==0?"inviteId":"messageId");synchronized(shown){if(shown.contains(id))continue;}
                final String peer=type==1?row.optString("fromPeerId"):"";
                final String heading=type==0?"Convite para jogar":row.optString("nickname","Jogador")+" enviou uma mensagem";
                a.runOnUiThread(()->{
                    if(!active||generation!=epoch||current.get()!=a||a.isFinishing()||a.isDestroyed())return;
                    synchronized(shown){if(shown.contains(id))return;}
                    android.widget.TextView banner=new android.widget.TextView(a);banner.setText("LZ GAMES  •  "+heading+"   ›");banner.setTextColor(0xffeafff2);banner.setTextSize(14);banner.setPadding(24,20,24,20);
                    android.graphics.drawable.GradientDrawable bg=new android.graphics.drawable.GradientDrawable();bg.setColor(0xff164435);bg.setCornerRadius(14);banner.setBackground(bg);
                    android.widget.PopupWindow popup=new android.widget.PopupWindow(banner,Math.min(a.getResources().getDisplayMetrics().widthPixels-32,(int)(480*a.getResources().getDisplayMetrics().density)),android.view.ViewGroup.LayoutParams.WRAP_CONTENT,false);
                    popup.setElevation(12);popup.setOutsideTouchable(true);popup.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(android.graphics.Color.TRANSPARENT));
                    banner.setOnClickListener(v->{popup.dismiss();a.startActivity(new Intent(a,StationRoomsActivity.class).putExtra("station.peerId",peer));});
                    try{if(notice!=null)notice.dismiss();popup.showAtLocation(a.getWindow().getDecorView(),android.view.Gravity.TOP|android.view.Gravity.CENTER_HORIZONTAL,0,18);notice=popup;remember(id);banner.postDelayed(()->{popup.dismiss();if(notice==popup)notice=null;},6000);}catch(android.view.WindowManager.BadTokenException ignored){}
                });return;
            }
        }
    }
}
