package org.emulationstation.frontend.auth;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import java.util.concurrent.*;
import org.emulationstation.frontend.station.*;

/** Login UI adapter. The session and catalog are supplied by StationCoordinator only. */
public final class StationLogin {
    public interface Callback {void ok(String name);void fail(String message);}
    private static volatile StationCoordinator coordinator;
    private static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static final ThreadPoolExecutor WORK=new ThreadPoolExecutor(0,1,10,TimeUnit.SECONDS,
        new ArrayBlockingQueue<Runnable>(4),r->{Thread t=new Thread(r,"Station-login");t.setDaemon(true);return t;});
    private StationLogin() {}
    public static String displayName(){StationCoordinator owner=coordinator;StationCoordinator.Library current=owner==null?null:owner.current();return current==null?"":current.displayName;}
    public static boolean ready(){StationCoordinator current=coordinator;return current!=null&&current.ready();}
    public static boolean hasLicense(Context context){return new java.io.File(context.getNoBackupFilesDir(),"station-license-id.txt").isFile();}
    public static boolean rememberAccess(Context context){
        return context.getSharedPreferences("station-login-ui",Context.MODE_PRIVATE).getBoolean("rememberAccess",true);
    }
    public static void rememberAccess(Context context,boolean enabled){
        context.getSharedPreferences("station-login-ui",Context.MODE_PRIVATE).edit().putBoolean("rememberAccess",enabled).apply();
    }
    private static final java.util.WeakHashMap<Activity,StationApi.Cancellation> renewing=new java.util.WeakHashMap<>();
    public static void ensureAuthorized(Activity activity) {
        if(ready())return;
        if(coordinator!=null&&coordinator.current()!=null&&hasLicense(activity)) {
            synchronized(renewing){if(renewing.containsKey(activity))return;renewing.put(activity,new StationApi.Cancellation());}
            StationApi.Cancellation pending=begin(activity,null,new Callback(){
                public void ok(String name){synchronized(renewing){renewing.remove(activity);}activity.onWindowFocusChanged(activity.hasWindowFocus());}
                public void fail(String message){synchronized(renewing){renewing.remove(activity);}showLogin(activity);}
            });
            synchronized(renewing){renewing.put(activity,pending);}return;
        }
        showLogin(activity);
    }
    private static void showLogin(Activity activity) {
        if(activity.isFinishing()||activity.isDestroyed())return;
        Intent login=new Intent(activity,LoginActivity.class);
        login.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        activity.startActivity(login);
    }
    public static StationApi.Cancellation begin(Activity activity,String code,Callback callback) {
        StationApi.Cancellation cancel=new StationApi.Cancellation();
        Context app=activity.getApplicationContext();
        try {WORK.execute(()->{
            try {
                cancel.check();StationCoordinator owner=StationAndroid.get(app).coordinator;coordinator=owner;
                StationCoordinator.Library library=owner.login(code,cancel);
                MAIN.post(()->{if(!cancel.cancelled()&&!activity.isFinishing()&&!activity.isDestroyed())callback.ok(library.displayName);});
            }catch(Exception error){
                String message=message(error);
                MAIN.post(()->{if(!cancel.cancelled()&&!activity.isFinishing()&&!activity.isDestroyed())callback.fail(message);});
            }
        });}catch(RejectedExecutionException busy){MAIN.post(()->{if(!cancel.cancelled()&&!activity.isFinishing()&&!activity.isDestroyed())callback.fail("Aguarde a consulta de acesso terminar.");});}
        return cancel;
    }
    private static String message(Exception error) {
        if(error instanceof StationApi.Offline)return error.getMessage();
        if(error instanceof StationApi.Failure){
            StationApi.Failure failure=(StationApi.Failure)error;
            if(failure.status==403||failure.status==401)return "Acesso não autorizado. Confira seu código ou fale com o suporte.";
            if(failure.status==429)return "Muitas tentativas. Aguarde um minuto e tente novamente.";
            if(failure.status==503)return "O serviço está temporariamente indisponível. Tente novamente em instantes.";
        }
        if(error instanceof IllegalArgumentException)return "Informe o código de acesso recebido após a compra.";
        return "Não foi possível confirmar o acesso. Confira a conexão e tente novamente.";
    }
}
