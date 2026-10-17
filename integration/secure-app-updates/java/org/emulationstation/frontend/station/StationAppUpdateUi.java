package org.emulationstation.frontend.station;

import android.app.*;
import android.content.*;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.lang.ref.WeakReference;

/** Uses the same exact carousel Activity as the existing download notices. */
public final class StationAppUpdateUi {
    private static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static boolean installed;
    private static WeakReference<Activity> menu=new WeakReference<>(null);
    private static PopupWindow banner;
    private static String shownId;
    private static long nextCheck;
    private static long nextNotice;
    private static final Runnable POLL=StationAppUpdateUi::poll;
    private StationAppUpdateUi(){}
    static synchronized void install(StationAndroid app,Context context){
        if(!Application.getProcessName().equals(context.getPackageName()))return;
        StationAppUpdater.initialize(app);
        if(!installed){
            installed=true;
            ((Application)app.context).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
                public void onActivityResumed(Activity a){
                    if(!isMenu(a))return;
                    menu=new WeakReference<>(a);MAIN.removeCallbacks(POLL);MAIN.postDelayed(POLL,5000);
                }
                public void onActivityPaused(Activity a){release(a);}
                public void onActivityStopped(Activity a){release(a);}
                public void onActivityDestroyed(Activity a){release(a);}
                public void onActivityCreated(Activity a,Bundle b){}
                public void onActivityStarted(Activity a){}
                public void onActivitySaveInstanceState(Activity a,Bundle b){}
            });
        }
        if(context instanceof Activity&&isMenu((Activity)context)){
            Activity a=(Activity)context;MAIN.post(()->{menu=new WeakReference<>(a);MAIN.removeCallbacks(POLL);MAIN.postDelayed(POLL,5000);});
        }
    }
    private static boolean isMenu(Activity a){return a.getClass().getName().equals("org.emulationstation.frontend.ESActivity");}
    private static void release(Activity a){if(menu.get()!=a)return;menu.clear();MAIN.removeCallbacks(POLL);dismiss();}
    private static void dismiss(){if(banner!=null){banner.dismiss();banner=null;}shownId=null;}
    private static void poll(){
        Activity a=menu.get();if(a==null||a.isFinishing()||a.isDestroyed())return;
        if(StationFrontend.authorized()&&StationFrontend.activeCount()==0&&a.hasWindowFocus()&&!StationDownloadPanel.isOpen()){
            long now=SystemClock.elapsedRealtime();
            if(now>=nextCheck){nextCheck=now+15*60*1000;StationAppUpdater.check(StationAppUpdateUi::show);}
            else show();
        }
        MAIN.postDelayed(POLL,30000);
    }
    private static void show(){
        Activity a=menu.get();StationAppRelease release=StationAppUpdater.offer;
        if(release==null){dismiss();return;}
        if(banner!=null&&!release.id.equals(shownId))dismiss();
        if(a==null||banner!=null||SystemClock.elapsedRealtime()<nextNotice||a.isFinishing()||a.isDestroyed()||!a.hasWindowFocus()||(StationAppUpdater.busy&&!StationAppUpdater.confirmationPending())||StationDownloadPanel.isOpen())return;
        LinearLayout row=new LinearLayout(a);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(a,16),dp(a,8),dp(a,8),dp(a,8));
        GradientDrawable background=new GradientDrawable();background.setColor(Color.rgb(19,34,55));background.setCornerRadius(dp(a,12));row.setBackground(background);
        TextView text=new TextView(a);text.setText("Atualização disponível · "+release.versionName);text.setTextColor(Color.WHITE);text.setTextSize(15);
        row.addView(text,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        Button update=new Button(a);update.setText("Atualizar");update.setOnClickListener(v->{dismiss();a.startActivity(new Intent(a,StationAppUpdateActivity.class).putExtra("start",true));});row.addView(update);
        Button later=new Button(a);later.setText("Depois");later.setOnClickListener(v->{nextNotice=SystemClock.elapsedRealtime()+60*60*1000;dismiss();});row.addView(later);
        banner=new PopupWindow(row,Math.min(a.getResources().getDisplayMetrics().widthPixels-dp(a,24),dp(a,650)),ViewGroup.LayoutParams.WRAP_CONTENT,false);
        shownId=release.id;
        banner.setElevation(dp(a,8));banner.setOutsideTouchable(false);
        try{banner.showAtLocation(a.getWindow().getDecorView(),Gravity.TOP|Gravity.CENTER_HORIZONTAL,0,dp(a,32));}
        catch(RuntimeException unavailable){dismiss();}
    }
    private static int dp(Context context,int value){return Math.round(value*context.getResources().getDisplayMetrics().density);}
}
