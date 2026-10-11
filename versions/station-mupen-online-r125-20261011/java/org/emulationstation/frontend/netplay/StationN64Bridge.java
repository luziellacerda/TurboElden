package org.emulationstation.frontend.netplay;

import android.app.*;
import android.content.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.lang.reflect.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

/** Conditional hooks for the integrated Mupen64Plus AE. No upstream preferences
 * or controllers are rewritten. A consumed, verified launch is required. */
public final class StationN64Bridge {
    static final String EXTRA="station.n64.launch";
    private static volatile Session current;
    public static boolean isStation(Intent intent){return current!=null&&intent!=null&&current.name.equals(intent.getStringExtra(EXTRA));}
    public static boolean isStationContext(Context context){Session s=current;return s!=null&&(context==s.activity||s.contexts.contains(context));}
    public static String coreName(){return current==null?"mupen64plus-core":"station_mupen64plus_core";}
    public static void onCreate(Activity activity){
        String name=activity.getIntent().getStringExtra(EXTRA);if(name==null){if(current!=null)throw new IllegalStateException("N64_PROCESS_RESTART_REQUIRED");return;}
        if(current!=null){if(current.closed||!name.equals(current.name))throw new IllegalStateException("N64_SESSION_CONFLICT");current.replaceActivity(activity);return;}
        try {JSONObject launch=StationN64Launch.consume(activity,name);Session session=new Session(activity,name,launch);current=session;
            // The Station adapter owns the host role, not the upstream manual lobby.
            activity.getIntent().putExtra(StationN64Launch.key("NETPLAY_ENABLED"),true).putExtra(StationN64Launch.key("NETPLAY_SERVER"),false);
        }catch(Exception e){throw new IllegalStateException("N64_LAUNCH_INVALID",e);}
    }
    public static void propagate(Context context,Intent service){Session s=current;if(s!=null&&isStationContext(context)){service.putExtra(EXTRA,s.name);
        try{service.putExtra(StationN64Launch.key("USE_RAPHNET_DEVICES"),false);}catch(Exception e){throw new IllegalStateException("N64_INPUT_PROFILE",e);}}}
    public static void onServiceStart(Context context,Intent intent){Session s=current;if(intent!=null&&intent.hasExtra(EXTRA)){if(s==null||!isStation(intent))throw new IllegalStateException("N64_OWNER_MISMATCH");s.contexts.add(context);}else if(s!=null)throw new IllegalStateException("N64_OWNER_MISSING");}
    public static void onGamePrefs(Object prefs,Intent intent){Session s=current;if(s!=null&&isStation(intent))s.prefs(prefs);}
    public static void onServicePrefs(Context context,Object prefs){Session s=current;if(s!=null&&isStationContext(context))s.prefs(prefs);}
    public static boolean skipAutoSave(Context context){return isStationContext(context);}
    public static boolean skipLoadAutoSave(Context context){return isStationContext(context);}
    public static boolean skipExternalStorage(Context context){return isStationContext(context);}
    public static boolean onReady(Activity activity,Object fragment){Session s=current;if(s==null||!isStation(activity.getIntent()))return false;s.ready(fragment);return true;}
    public static void onResume(Activity activity){Session s=current;if(s!=null&&activity==s.activity)s.resume();}
    public static void onPause(Activity activity){Session s=current;if(s!=null&&activity==s.activity)s.pause();}
    public static String gameDataDir(Object prefs){Session s=current;return s!=null&&s.preferences.contains(prefs)?s.dir.toString():null;}
    public static void onNewIntent(Activity activity,Intent intent){Session s=current;if(s==null||activity!=s.activity)return;
        try {String name=intent.getStringExtra(EXTRA);if(name!=null&&!s.name.equals(name))throw new IOException("N64_OWNER_MISMATCH");
            String exit=StationN64Launch.key("EXIT_GAME"),force=StationN64Launch.key("FORCE_EXIT_GAME");
            if(s.name.equals(name)&&intent.getBooleanExtra(exit,false)){s.humanAuthorized=true;s.humanExit();}
            else {intent.removeExtra(exit);intent.removeExtra(force);}
            intent.putExtra(EXTRA,s.name).putExtra(StationN64Launch.key("NETPLAY_ENABLED"),true).putExtra(StationN64Launch.key("NETPLAY_SERVER"),false);
        }catch(Exception e){throw new IllegalStateException("N64_NEW_INTENT",e);}}
    public static void authorizeHumanExit(Activity activity){Session s=current;if(s!=null&&isStationContext(activity))s.humanAuthorized=true;}
    public static boolean allowShutdown(Context context){Session s=current;if(s==null||!isStationContext(context))return true;
        if(s.humanAuthorized||s.human)return true;s.fatal("N64_UNAUTHORIZED_SHUTDOWN");return false;}
    public static void requestHumanExit(Context context){Session s=current;if(s!=null&&isStationContext(context)&&s.humanAuthorized)s.humanExit();}
    public static boolean onExit(Activity activity){Session s=current;if(s==null||!isStationContext(activity))return false;
        if(!s.humanAuthorized&&!s.human){s.fatal("N64_UNEXPECTED_EXIT");return true;}s.humanExit();s.close();activity.setResult(Activity.RESULT_OK);activity.finish();return true;}
    public static void onDestroy(Activity activity){Session s=current;if(s!=null&&isStationContext(activity)&&activity.isFinishing())s.close();}
    private static Object field(Object object,String name)throws Exception {Field f=findField(object.getClass(),name);f.setAccessible(true);return f.get(object);}
    private static Field findField(Class<?> type,String name)throws NoSuchFieldException{for(Class<?> c=type;c!=null;c=c.getSuperclass())try{return c.getDeclaredField(name);}catch(NoSuchFieldException ignored){}throw new NoSuchFieldException(name);}
    private static void set(Object object,String name,Object value)throws Exception {Field f=findField(object.getClass(),name);f.setAccessible(true);f.set(object,value);}
    private static final class Core {
        final Object library;final Method getFunction,invoke;
        Core()throws Exception {Class<?> l=Class.forName("com.sun.jna.NativeLibrary"),f=Class.forName("com.sun.jna.Function");library=l.getMethod("getInstance",String.class).invoke(null,"station_mupen64plus_core");getFunction=l.getMethod("getFunction",String.class);invoke=f.getMethod("invoke",Class.class,Object[].class);}
        Object call(String name,Class<?> result,Object...args)throws Exception {Object fn=getFunction.invoke(library,name);return invoke.invoke(fn,result,args);}
        long status(){try{return ((Number)call("StationMupenStatus",Long.TYPE)).longValue();}catch(Exception e){return -1;}}
        void control(long epoch,boolean pause,boolean visible)throws Exception {call("StationMupenControl",Void.TYPE,epoch,pause?1:0,visible?1:0);}
        boolean stalled(){try{return ((Number)call("StationMupenStalled",Integer.TYPE)).intValue()!=0;}catch(Exception e){return true;}}
        void quit(){try{call("StationMupenRequestQuit",Void.TYPE);}catch(Exception ignored){}}
    }
    private static final class Session implements StationMultiplayerSession.Listener {
        Activity activity;final String name;final JSONObject launch;final boolean host;final int slot;final File dir;
        final ResultReceiver events;final StationSessionLink owner;final StationN64Mux mux;final StationMultiplayerSession transport;final Core core;
        final Set<Context> contexts=Collections.synchronizedSet(Collections.newSetFromMap(new IdentityHashMap<Context,Boolean>()));
        final Set<Object> preferences=Collections.synchronizedSet(Collections.newSetFromMap(new IdentityHashMap<Object,Boolean>()));
        final ExecutorService worker=Executors.newSingleThreadExecutor();
        volatile boolean closed,visible,ownerReady,started,connecting,human,humanAuthorized,failed;private Dialog waiting;private TextView waitingText;
        Session(Activity activity,String name,JSONObject launch)throws Exception {
            this.activity=activity;this.name=name;this.launch=launch;host="host".equals(launch.getString("role"));slot=launch.getInt("localSlot");
            events=StationSessionChannel.read(activity.getIntent().getExtras(),StationGameSession.EXTRA);if(events==null)throw new IOException("N64_OWNER_MISSING");
            dir=new File(activity.getNoBackupFilesDir(),"station-online/n64/"+launch.getString("roomId")+"/"+launch.getLong("generation"));
            if(!dir.isDirectory()&&!dir.mkdirs())throw new IOException("N64_SAVE_DIRECTORY");
            core=new Core();if(((Number)core.call("StationMupenConfigure",Integer.TYPE,slot-1,launch.getInt("expectedDeviceMask"))).intValue()!=1)throw new IOException("N64_CORE_ROSTER");
            mux=new StationN64Mux(host,slot-1,launch.getInt("expectedDeviceMask"),this::fatal);
            try {transport=new StationMultiplayerSession(new JSONObject(launch.toString()).put("port",mux.hubPort()),this);}
            catch(Exception e){mux.close();throw e;}
            owner=new StationSessionLink(activity,activity.getIntent().getStringExtra(StationGameSession.ANCHOR_EXTRA),launch.getString("roomId"),launch.getLong("generation"),new StationSessionLink.Listener(){
                public void ready(){if(closed)return;ownerReady=true;if(visible)startOwner();}
                public void unavailable(String category){if(closed)return;ownerReady=false;transport.visible(false);showWaiting("Aguardando a conexão da sala…");}
            });owner.bind();
        }
        void replaceActivity(Activity next){if(activity!=next){hideWaiting();activity=next;}}
        void prefs(Object prefs){try {preferences.add(prefs);
            File root=dir.getCanonicalFile();
            for(String n:new String[]{"autoSaveDir","coreUserConfigDir","sramDataDir","slotSaveDir","userSaveDir"}){File f=new File(root,n);if(!f.isDirectory()&&!f.mkdirs())throw new IOException("N64_SAVE_DIRECTORY");set(prefs,n,f.toString());}
            set(prefs,"mupen64plus_cfg",new File(new File(root,"coreUserConfigDir"),"mupen64plus.cfg").toString());
            // No per-phone JIT or raw USB input differences may change deterministic state.
            set(prefs,"r4300Emulator","1");set(prefs,"rspHleVideo",true);set(prefs,"randomizeInterrupts",false);
            set(prefs,"disableExpansionPak",false);set(prefs,"countPerOp",0);set(prefs,"countPerOpDen",0);set(prefs,"forceAlignmentOfPiDma",0);
            set(prefs,"videoPluginLib",Class.forName("paulscode.android.mupen64plusae.persistent.AppData$VideoPlugin").getField("GLIDE64MK2").get(null));
            set(prefs,"rspPluginLib",Class.forName("paulscode.android.mupen64plusae.persistent.AppData$RspPlugin").getField("HLE").get(null));
            // The launch uses a separate empty preferences namespace, including cheats.
            set(prefs,"mPreferences",activity.getSharedPreferences("station-n64-"+launch.getString("roomId")+"-"+launch.getLong("generation"),0));
        }catch(Exception e){throw new IllegalStateException("N64_SESSION_STORAGE",e);}}
        void ready(Object fragment){if(connecting||closed)return;connecting=true;
            worker.execute(()->{try {
                mux.start(transport.localPort());transport.listening();
                int reg;do{reg=new java.security.SecureRandom().nextInt();}while(reg==0);
                Method connect=activity.getClass().getMethod("connect",Integer.TYPE,Integer.TYPE,String.class,String.class,InetAddress.class,Integer.TYPE);
                connect.invoke(activity,reg,slot,"mupen64plus-video-glide64mk2","mupen64plus-rsp-hle",InetAddress.getByName("127.0.0.1"),mux.corePort());
                Object service=field(fragment,"mCoreService");if(service==null||!Boolean.TRUE.equals(field(service,"mNetplayInitSuccess")))throw new IOException("N64_REGISTRATION_REJECTED");
                mux.awaitRegistered();if(closed)return;activity.getClass().getMethod("start").invoke(activity);
            }catch(Exception e){if(!closed)fatal("N64_INITIALIZATION");}});
        }
        void resume(){visible=true;if(ownerReady)startOwner();else showWaiting("Aguardando a conexão da sala…");}
        void pause(){visible=false;transport.visible(false);events.send(2,null);hideWaiting();}
        private void startOwner(){if(closed||!ownerReady||!visible)return;
            Bundle b=new Bundle();b.putParcelable("reply",StationSessionChannel.transport(new ResultReceiver(new Handler(Looper.getMainLooper())){
                protected void onReceiveResult(int code,Bundle value){if(closed||value==null)return;
                    if(code==103)try{transport.provide(value.getString("linkId"),value.getLong("serial"),new JSONObject(value.getString("descriptor")));}catch(Exception e){transport.unavailable(value.getString("linkId"),value.getLong("serial"),true);}
                    else if(code==104)transport.unavailable(value.getString("linkId"),value.getLong("serial"),value.getBoolean("terminal"));
                    else if(code==102&&value.getBoolean("terminal"))fatal("N64_AUTHORITY");
                }}));events.send(1,b);if(!started){started=true;transport.start();}transport.visible(!failed);
        }
        public void nativeControl(long epoch,boolean pause,boolean shown){try{core.control(epoch,pause||failed,shown&&visible);}catch(Exception e){fatal("N64_RECOVERY_HOOK");}}
        public long nativeStatus(){return core.status();}
        public boolean nativeStalled(){return core.stalled();}
        public boolean bind(int port,int remote){return mux.bind(port,remote);}
        public void unbind(int port,int remote){mux.unbind(port,remote);}
        public void ticket(String link,long serial){if(!closed){Bundle b=new Bundle();b.putString("linkId",link);b.putLong("serial",serial);events.send(5,b);}}
        public void ready(){if(!closed&&visible)events.send(3,null);}
        public void state(boolean waiting,boolean sync){if(waiting)showWaiting(sync?"Sincronizando os jogadores…":"Aguardando a conexão da sala…");else hideWaiting();}
        public void fatal(String category){if(closed||failed)return;failed=true;long status=core.status();try{core.control(status<0?0:status>>>3,true,false);}catch(Exception ignored){}
            events.send(6,null);showWaiting("A partida precisa de atenção. Aguarde a conexão ou saia pelo menu para criar uma nova sala.");android.util.Log.w("StationN64",category);}
        public void trace(String event){android.util.Log.i("StationN64",event);}
        private void showWaiting(String message){activity.runOnUiThread(()->{if(closed||!visible||activity.isFinishing())return;if(waiting==null){
            LinearLayout panel=new LinearLayout(activity);panel.setOrientation(LinearLayout.VERTICAL);panel.setPadding(24,16,24,16);panel.setBackgroundColor(0xff10151c);
            waitingText=new TextView(activity);waitingText.setTextColor(0xffeaf2ff);waitingText.setTextSize(15);panel.addView(waitingText);waiting=new Dialog(activity);waiting.requestWindowFeature(Window.FEATURE_NO_TITLE);waiting.setContentView(panel);waiting.setCancelable(false);waiting.show();Window w=waiting.getWindow();if(w!=null){w.setDimAmount(0);w.addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE);w.setGravity(Gravity.TOP);}}
            waitingText.setText(message);
        });}
        private void hideWaiting(){Activity ownerActivity=activity;ownerActivity.runOnUiThread(()->{if(waiting!=null){waiting.dismiss();waiting=null;waitingText=null;}});}
        void humanExit(){if(closed||human)return;human=true;events.send(4,null);core.quit();}
        synchronized void close(){if(closed)return;closed=true;visible=false;core.quit();transport.close();mux.close();owner.close();worker.shutdownNow();hideWaiting();if(!human)events.send(6,null);}
    }
}
