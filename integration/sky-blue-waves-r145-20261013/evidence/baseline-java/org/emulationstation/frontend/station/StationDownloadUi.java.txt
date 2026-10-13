package org.emulationstation.frontend.station;

import android.app.Activity;
import android.app.Application;
import android.app.Dialog;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewTreeObserver;
import android.view.Window;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.lang.ref.WeakReference;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/** Event-driven notices owned only by the foreground carousel, never an emulator. */
public final class StationDownloadUi {
    private static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static final SignalGate signals=new SignalGate();
    private static WeakReference<Activity> owner=new WeakReference<>(null);
    private static WeakReference<View> focusView=new WeakReference<>(null);
    private static ViewTreeObserver focusObserver;
    private static Dialog warning;
    private static boolean installed;
    private static final ViewTreeObserver.OnWindowFocusChangeListener FOCUS=focused->{if(focused)showNext();};

    private StationDownloadUi(){}
    static final class Notice {
        final String id,name,message;
        final long order;final AtomicBoolean shown=new AtomicBoolean();
        Notice(String id,String name,String message,long order){this.id=id;this.name=name==null||name.isEmpty()?"Jogo":name;this.message=message;this.order=order;}
    }
    /** Producers never acquire a UI-owned lock or enqueue ordinary progress. */
    static final class SignalGate {
        final ConcurrentHashMap<String,Notice> known=new ConcurrentHashMap<>();
        final AtomicInteger slots=new AtomicInteger();
        final AtomicLong sequence=new AtomicLong();
        boolean offer(String id,String name,String message,int result,boolean active){
            if(id==null||id.isEmpty())return false;
            if(active||result==1||result==2||"Cancelado".equals(message)){
                if(known.remove(id)==null)return false;slots.decrementAndGet();return true;
            }
            if(result!=3||message==null||message.isEmpty())return false;
            for(;;){
                Notice old=known.get(id);if(old!=null&&message.equals(old.message))return false;
                Notice notice=new Notice(id,name,message,sequence.incrementAndGet());
                if(old!=null){if(known.replace(id,old,notice))return true;continue;}
                // One source owns admission, deduplication and pending presentation.
                int count=slots.get();
                if(count>=48){
                    Notice oldest=null;for(Notice entry:known.values())if(oldest==null||entry.order<oldest.order)oldest=entry;
                    if(oldest!=null&&known.remove(oldest.id,oldest))slots.decrementAndGet();
                    count=slots.get();
                }
                while(count<48&&!slots.compareAndSet(count,count+1))count=slots.get();
                if(count>=48)return false;
                old=known.putIfAbsent(id,notice);
                if(old==null)return true;
                slots.decrementAndGet();
            }
        }
        Notice next(){Notice next=null;for(Notice entry:known.values())if(!entry.shown.get()&&(next==null||entry.order<next.order))next=entry;return next;}
        boolean current(Notice notice){return notice!=null&&known.get(notice.id)==notice;}
        void shown(Notice notice){if(current(notice))notice.shown.set(true);}
    }

    public static synchronized void install(Application application){
        if(installed)return;installed=true;
        application.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
            public void onActivityResumed(Activity a){
                if(!menu(a))return;detachFocus();owner=new WeakReference<>(a);
                View decor=a.getWindow().getDecorView();focusView=new WeakReference<>(decor);focusObserver=decor.getViewTreeObserver();
                focusObserver.addOnWindowFocusChangeListener(FOCUS);a.getWindow().getDecorView().post(StationDownloadUi::showNext);
            }
            public void onActivityPaused(Activity a){release(a);}
            public void onActivityStopped(Activity a){release(a);}
            public void onActivityDestroyed(Activity a){release(a);}
            public void onActivityCreated(Activity a,Bundle b){}
            public void onActivityStarted(Activity a){}
            public void onActivitySaveInstanceState(Activity a,Bundle b){}
        });
    }
    private static boolean menu(Activity a){return a!=null&&a.getClass().getName().equals("org.emulationstation.frontend.ESActivity");}
    private static void detachFocus(){
        View decor=focusView.get();ViewTreeObserver current=decor==null?null:decor.getViewTreeObserver();
        if(focusObserver!=null&&focusObserver.isAlive())focusObserver.removeOnWindowFocusChangeListener(FOCUS);
        if(current!=null&&current!=focusObserver&&current.isAlive())current.removeOnWindowFocusChangeListener(FOCUS);
        focusObserver=null;focusView.clear();
    }
    private static void release(Activity a){
        if(owner.get()!=a)return;owner.clear();detachFocus();
        if(warning!=null){Dialog old=warning;warning=null;old.dismiss();}
    }
    public static void changed(String id,String name,String message,int result,boolean active){
        if(!signals.offer(id,name,message,result,active))return;
        MAIN.post(StationDownloadUi::showNext);
    }
    static void resumeNotices(){MAIN.post(StationDownloadUi::showNext);}
    static boolean mayPresent(boolean menu,boolean finishing,boolean destroyed,boolean focused,boolean panelOpen,boolean warningOpen){
        return menu&&!finishing&&!destroyed&&focused&&!panelOpen&&!warningOpen;
    }
    private static void showNext(){
        Notice notice=signals.next();if(notice==null)return;
        Activity a=owner.get();if(a==null||!mayPresent(menu(a),a.isFinishing(),a.isDestroyed(),a.hasWindowFocus(),StationDownloadPanel.isOpen(),warning!=null))return;
        Dialog dialog=messageDialog(a,"Não foi possível concluir",notice.name,notice.message,"ENTENDI",null,null,null);
        warning=dialog;dialog.setOnDismissListener(d->{if(warning==dialog)warning=null;MAIN.post(StationDownloadUi::showNext);});
        try{if(!signals.current(notice)){warning=null;return;}dialog.show();sizeDialog(a,dialog);signals.shown(notice);}
        catch(android.view.WindowManager.BadTokenException destroyed){warning=null;}
    }
    static int dp(Activity a,float value){return Math.round(value*a.getResources().getDisplayMetrics().density);}
    static GradientDrawable surface(Activity a,int color,int edge,float radius){
        GradientDrawable shape=new GradientDrawable();shape.setColor(color);shape.setCornerRadius(dp(a,radius));
        if(edge!=0)shape.setStroke(dp(a,1),edge);return shape;
    }
    static TextView label(Activity a,String value,int size,int color){
        TextView text=new TextView(a);text.setText(value);text.setTextSize(size);text.setTextColor(color);text.setGravity(Gravity.CENTER_VERTICAL);return text;
    }
    static TextView action(Activity a,String value,boolean destructive){
        TextView button=label(a,value,13,destructive?0xffffc5cb:0xffdffaff);button.setGravity(Gravity.CENTER);button.setTypeface(null,Typeface.BOLD);
        button.setBackground(new android.graphics.drawable.InsetDrawable(surface(a,destructive?0xff36202b:0xff123345,destructive?0xff734151:0xff306277,8),0,dp(a,5),0,dp(a,5)));
        button.setMinHeight(dp(a,48));button.setFocusable(true);button.setPadding(dp(a,10),0,dp(a,10),0);return button;
    }
    static Dialog messageDialog(Activity a,String title,String name,String message,String primary,Runnable accepted,String secondary,Runnable rejected){
        Dialog dialog=new Dialog(a);dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        LinearLayout page=new LinearLayout(a){@Override protected void onMeasure(int widthSpec,int heightSpec){int available=Math.max(dp(a,160),a.getResources().getDisplayMetrics().heightPixels-dp(a,48));int specified=View.MeasureSpec.getSize(heightSpec);if(View.MeasureSpec.getMode(heightSpec)!=View.MeasureSpec.UNSPECIFIED)available=Math.min(available,specified);super.onMeasure(widthSpec,View.MeasureSpec.makeMeasureSpec(available,View.MeasureSpec.AT_MOST));}};
        page.setOrientation(LinearLayout.VERTICAL);page.setPadding(dp(a,20),dp(a,16),dp(a,20),dp(a,16));
        page.setBackground(surface(a,0xff0d1a2a,0xff315167,14));
        TextView heading=label(a,title,16,0xffeffaff);heading.setTypeface(null,Typeface.BOLD);heading.setMaxLines(2);page.addView(heading,new LinearLayout.LayoutParams(-1,-2));
        android.widget.ScrollView scroll=new android.widget.ScrollView(a);scroll.setFillViewport(false);LinearLayout bodyArea=new LinearLayout(a);bodyArea.setOrientation(LinearLayout.VERTICAL);
        TextView game=label(a,name,14,0xff79dcec);LinearLayout.LayoutParams gp=new LinearLayout.LayoutParams(-1,-2);gp.topMargin=dp(a,8);bodyArea.addView(game,gp);
        TextView body=label(a,message,13,0xffb3c8d8);LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(-1,-2);bp.topMargin=dp(a,8);bp.bottomMargin=dp(a,16);bodyArea.addView(body,bp);
        scroll.addView(bodyArea,new android.widget.ScrollView.LayoutParams(-1,-2));page.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout actions=new LinearLayout(a);actions.setOrientation(LinearLayout.HORIZONTAL);
        if(secondary!=null){TextView keep=action(a,secondary,false);keep.setOnClickListener(v->{dialog.dismiss();if(rejected!=null)rejected.run();});LinearLayout.LayoutParams kp=new LinearLayout.LayoutParams(0,dp(a,48),1);kp.rightMargin=dp(a,8);actions.addView(keep,kp);}
        TextView accept=action(a,primary,accepted!=null);accept.setOnClickListener(v->{dialog.dismiss();if(accepted!=null)accepted.run();});actions.addView(accept,new LinearLayout.LayoutParams(0,dp(a,48),1));
        page.addView(actions,new LinearLayout.LayoutParams(-1,-2));dialog.setContentView(page);Window window=dialog.getWindow();
        if(window!=null){window.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));window.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);android.view.WindowManager.LayoutParams attrs=window.getAttributes();attrs.dimAmount=.64f;window.setAttributes(attrs);}
        return dialog;
    }
    static void sizeDialog(Activity a,Dialog dialog){Window window=dialog.getWindow();if(window!=null)window.setLayout(Math.min(dp(a,420),Math.max(dp(a,240),a.getResources().getDisplayMetrics().widthPixels-dp(a,32))),-2);}
}
