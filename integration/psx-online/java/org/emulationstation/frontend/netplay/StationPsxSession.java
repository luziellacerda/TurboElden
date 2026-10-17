package org.emulationstation.frontend.netplay;

import android.app.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.json.*;

/** Java controls the authenticated room/links. Only the original SDL owner may
 * apply state, sample inputs or advance the loaded normal PCSX core. */
public final class StationPsxSession {
    private static volatile Session current;
    private StationPsxSession(){}
    public static synchronized void attach(Activity activity,String name) {
        if(current!=null){current.fatal("PSX_SECOND_OWNER");return;}
        current=new Session(activity,name);current.initialize();
    }
    public static boolean authorizedToStart(){Session s=current;return s!=null&&s.descriptorValid&&s.ownerReady&&s.visible&&!s.failed&&!s.human;}
    public static void visibility(boolean shown){Session s=current;if(s!=null)s.visibility(shown);}
    public static void onRendererReady(){Session s=current;if(s!=null)s.rendererReady=true;/* Never a core pause ACK. */}
    public static void onCoreReady(int stateBytes){Session s=current;if(s!=null&&!s.human&&!s.closed)try{s.worker.execute(()->s.coreReady(stateBytes));}catch(RejectedExecutionException ignored){}}
    public static void onLocalPause(boolean paused){Session s=current;if(s!=null&&!s.human&&!s.closed)try{s.worker.execute(()->s.localPause(paused));}catch(RejectedExecutionException ignored){}}
    public static void onPreparationFailed(String category){Session s=current;if(s!=null)s.fatal("PSX_PREPARATION_FAILED");}
    public static void onOwnerReturned(String error){Session s=current;if(s!=null){s.ownerReturned=true;if(!s.human)s.fatal("PSX_UNEXPECTED_OWNER_RETURN");}}
    public static void onHumanExitRequested(){Session s=current;if(s!=null)s.activity.runOnUiThread(()->confirmExit(s.activity));}
    public static boolean humanCleanupComplete(){Session s=current;return s!=null&&s.human&&s.humanCleanupComplete;}
    public static void onOwnerThreadStarted(){Session s=current;if(s!=null&&s.activity instanceof StationPsxOnlineActivity)((StationPsxOnlineActivity)s.activity).recordOwnerThread();}
    public static boolean humanExitAuthorized(){Session s=current;return s!=null&&s.human;}
    public static void confirmExit(Activity activity){Session s=current;if(s==null||activity!=s.activity)return;
        activity.runOnUiThread(()->{if(s.exitDialog||s.human||activity.isFinishing())return;s.exitDialog=true;
            new AlertDialog.Builder(activity).setTitle("Sair da partida?").setMessage("A partida ser\u00e1 encerrada neste aparelho.")
                .setNegativeButton("Continuar",(d,w)->s.exitDialog=false)
                .setPositiveButton("Sair",(d,w)->{s.exitDialog=false;s.humanExit();})
                .setOnCancelListener(d->s.exitDialog=false).show();});
    }
    public static void unexpectedDestroy(){Session s=current;if(s!=null&&!s.human){s.visibility(false);s.fatal("PSX_ACTIVITY_DESTROYED");}}
    private static final class Control {
        final long epoch,serial;final boolean pause,visible;
        Control(long e,long s,boolean p,boolean v){epoch=e;serial=s;pause=p;visible=v;}
    }
    private static final class Session implements StationMultiplayerSession.Listener {
        final Activity activity;final String name;final StationPsxWifiLatency wifiLatency;
        final ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"Station-PSX-session");t.setDaemon(true);return t;});
        final AtomicReference<Control> desired=new AtomicReference<>(new Control(1,1,true,false));
        volatile JSONObject launch;volatile ResultReceiver events;volatile StationSessionLink owner;volatile StationMultiplayerSession transport;
        volatile boolean descriptorValid,ownerReady,visible,rendererReady,configured,loaded,failed,human,closed,ownerReturned,localPaused,exitDialog,started,humanCleanupComplete;
        volatile long reportedStatus=-8;private ScheduledFuture<?> updates;private Dialog waiting;private TextView waitingText;
        Session(Activity activity,String name){this.activity=activity;this.name=name;this.wifiLatency=new StationPsxWifiLatency(activity);}
        private void refreshWifiLatency(){activity.runOnUiThread(()->wifiLatency.setActive(
            descriptorValid&&visible&&!localPaused&&!failed&&!human&&!closed));}
        void initialize(){worker.execute(()->{try {
            launch=StationPsxLaunch.consume(activity,name);
            events=StationSessionChannel.read(activity.getIntent().getExtras(),StationGameSession.EXTRA);
            String anchor=activity.getIntent().getStringExtra(StationGameSession.ANCHOR_EXTRA);
            if(events==null||anchor==null||anchor.isEmpty())throw new IOException("PSX_ROOM_AUTHORITY");
            if(!StationPsxBridge.nativePrepare(new File(activity.getApplicationInfo().nativeLibraryDir,"libpcsx_rearmed_libretro_android.so").getCanonicalPath(),
                launch.getString("rom"),launch.getString("privateHome"),StationPsxLaunch.unhex(launch.getString("bindingSha256")),launch.getInt("localSlot"),3))throw new IOException("PSX_NATIVE_PREPARE");
            configured=true;descriptorValid=true;refreshWifiLatency();
            Control c=desired.get();StationPsxBridge.nativeControl(c.epoch,c.serial,true,c.visible);
            if(human){StationPsxBridge.nativeAuthorizeHumanExit();return;}
            owner=new StationSessionLink(activity,anchor,launch.getString("roomId"),launch.getLong("generation"),new StationSessionLink.Listener(){
                public void ready(){if(closed||human)return;ownerReady=true;refreshSdlGate();if(loaded&&visible&&!localPaused)startOwner();}
                public void unavailable(String category){if(closed||human)return;ownerReady=false;pauseLocally();StationMultiplayerSession t=transport;if(t!=null)t.visible(false);showWaiting("Aguardando a conex\u00e3o da sala\u2026");}
            });activity.runOnUiThread(()->{if(!closed&&!human)owner.bind();});
            updates=worker.scheduleWithFixedDelay(this::update,0,50,TimeUnit.MILLISECONDS);
        }catch(Exception failure){fatal("PSX_INITIALIZATION");StationPsxBridge.nativePreparationFailed("PSX_INITIALIZATION");}});}
        void refreshSdlGate(){activity.runOnUiThread(()->{if(!closed&&!human)activity.onWindowFocusChanged(activity.hasWindowFocus());});}
        void coreReady(int bytes){if(closed||human||loaded)return;try {
            if(!descriptorValid||bytes<1||bytes>16*1024*1024)throw new IOException("PSX_REAL_STATE_SIZE");
            loaded=true;transport=new StationMultiplayerSession(new JSONObject(launch.toString()).put("port",0),this,StationPsxEndpoint.factory());
            transport.listening();if(visible&&ownerReady&&!localPaused)startOwner();
        }catch(Exception failure){fatal("PSX_CORE_BINDING");}}
        void visibility(boolean shown){if(closed||human)return;visible=shown;refreshWifiLatency();
            if(!shown){pauseLocally();StationMultiplayerSession t=transport;if(t!=null)t.visible(false);ResultReceiver e=events;if(e!=null)e.send(2,null);hideWaiting();}
            else if(ownerReady){refreshSdlGate();if(loaded&&!localPaused)startOwner();}
            else showWaiting("Preparando a partida\u2026");
        }
        void localPause(boolean paused){if(closed||human)return;localPaused=paused;refreshWifiLatency();
            if(paused){pauseLocally();if(transport!=null)transport.visible(false);if(events!=null)events.send(2,null);}
            else if(visible&&ownerReady&&loaded&&!failed)startOwner();
        }
        private void pauseLocally(){nativeControl(desired.get().epoch,true,false);}
        private void startOwner(){StationMultiplayerSession t=transport;if(t==null||closed||human||failed||!visible||!ownerReady||localPaused)return;
            Bundle b=new Bundle();b.putParcelable("reply",StationSessionChannel.transport(new ResultReceiver(new Handler(Looper.getMainLooper())){
                protected void onReceiveResult(int code,Bundle value){StationMultiplayerSession target=transport;if(closed||human||value==null||target==null)return;
                    if(code==103)try{target.provide(value.getString("linkId"),value.getLong("serial"),new JSONObject(value.getString("descriptor")));}
                        catch(Exception failure){target.unavailable(value.getString("linkId"),value.getLong("serial"),true);}
                    else if(code==104)target.unavailable(value.getString("linkId"),value.getLong("serial"),value.getBoolean("terminal"));
                    else if(code==102&&value.getBoolean("terminal"))fatal("PSX_AUTHORITY_REJECTED");
                }
            }));events.send(1,b);if(!started){started=true;t.start();}t.visible(true);
        }
        public synchronized void nativeControl(long epoch,boolean pause,boolean shown){if(closed||human||epoch<1)return;
            boolean effective=pause||failed||!shown||!visible||!ownerReady||localPaused;Control old,next;
            do{old=desired.get();if(epoch<old.epoch||epoch==old.epoch&&effective==old.pause&&shown==old.visible)return;
                if(old.serial==Long.MAX_VALUE||epoch>Long.MAX_VALUE/8){fatal("PSX_CONTROL_EXHAUSTED");return;}
                next=new Control(epoch,old.serial+1,effective,shown);
            }while(!desired.compareAndSet(old,next));
            reportedStatus=-8;
            // Every new permission first establishes a CPU pause at its exact
            // local serial; update resumes only after that genuine checkpoint.
            if(configured)StationPsxBridge.nativeControl(next.epoch,next.serial,next.pause,next.visible);
        }
        public long nativeStatus(){
            if(!configured||!loaded||closed||human||failed)return -8;
            Control c=desired.get();long[] s=StationPsxBridge.nativeStatus();
            if(s==null||s.length!=StationPsxBridge.STATUS_FIELDS||c!=desired.get()||
                s[StationPsxBridge.EPOCH]!=c.epoch||s[StationPsxBridge.CONTROL_SERIAL]!=c.serial)return -8;
            boolean ack=s[StationPsxBridge.ACK_VALID]!=0&&s[StationPsxBridge.ACK_EPOCH]==c.epoch&&s[StationPsxBridge.ACK_SERIAL]==c.serial;
            boolean ready=ack&&s[StationPsxBridge.INITIAL_STATE_SYNCED]!=0&&s[StationPsxBridge.DRAINED]!=0&&
                s[StationPsxBridge.FAILED]==0&&s[StationPsxBridge.CORE_READY]!=0&&
                s[StationPsxBridge.CLOSED]==0&&s[StationPsxBridge.LOCAL_PAUSED]==0&&
                s[StationPsxBridge.IN_FRAME]==0&&s[StationPsxBridge.APPLYING_STATE]==0&&!localPaused;
            return c.epoch*8|(ack?1:0)|(ready?2:0);
        }
        public boolean nativeStalled(){return false;/* Waiting for inputs is ordinary lockstep, not NeedSync. */}
        public boolean bind(int port,int remote){return false;}
        public void unbind(int port,int remote){}
        public void ticket(String id,long serial){if(!closed&&!human&&events!=null){Bundle b=new Bundle();b.putString("linkId",id);b.putLong("serial",serial);events.send(5,b);}}
        public void ready(){if(!closed&&!human&&!failed&&visible&&ownerReady&&events!=null)events.send(3,null);}
        public void state(boolean waiting,boolean sync){if(waiting)showWaiting(sync?"Sincronizando os jogadores\u2026":"Aguardando a conex\u00e3o da sala\u2026");else hideWaiting();}
        public void trace(String event){android.util.Log.i("StationPsx",event);}
        public synchronized void fatal(String category){if(closed||human||failed)return;failed=true;reportedStatus=-8;refreshWifiLatency();
            Control old=desired.get();desired.set(new Control(old.epoch,old.serial==Long.MAX_VALUE?Long.MAX_VALUE:old.serial+1,true,false));
            if(configured)StationPsxBridge.nativeFail(category);if(events!=null)events.send(6,null);
            showWaiting("A partida precisa de aten\u00e7\u00e3o. Aguarde a conex\u00e3o ou saia pelo menu para criar uma nova sala.");
            android.util.Log.w("StationPsx",category);
        }
        private synchronized void update(){if(closed||human||!configured||!loaded)return;try {
            Control c=desired.get();long[] status=StationPsxBridge.nativeStatus();
            if(status==null||status.length!=StationPsxBridge.STATUS_FIELDS)throw new IOException("PSX_NATIVE_STATUS");
            if(status[StationPsxBridge.FAILED]!=0){fatal("PSX_NATIVE_OWNER_FAILED");return;}
            boolean ack=status[StationPsxBridge.EPOCH]==c.epoch&&status[StationPsxBridge.CONTROL_SERIAL]==c.serial&&
                status[StationPsxBridge.ACK_VALID]!=0&&status[StationPsxBridge.ACK_EPOCH]==c.epoch&&status[StationPsxBridge.ACK_SERIAL]==c.serial;
            // READY still requires drained queues in nativeStatus(). After the
            // relay grants PLAYING, the faster peer may already have sent valid
            // gameplay. Requiring an empty inbox here would prevent the owner
            // from resuming to consume that very inbox. Native resume rechecks
            // the exact epoch/serial ACK and the applied snapshot atomically.
            boolean synced=status[StationPsxBridge.INITIAL_STATE_SYNCED]!=0&&
                status[StationPsxBridge.CORE_READY]!=0&&status[StationPsxBridge.CLOSED]==0&&
                status[StationPsxBridge.LOCAL_PAUSED]==0&&status[StationPsxBridge.IN_FRAME]==0&&
                status[StationPsxBridge.APPLYING_STATE]==0;
            if(!c.pause&&ack&&synced&&visible&&ownerReady&&!localPaused&&!failed)StationPsxBridge.nativeResume(c.epoch,c.serial);
            if(c==desired.get())reportedStatus=c.epoch*8|(ack?1:0)|(ack&&synced&&status[StationPsxBridge.DRAINED]!=0&&!failed&&!localPaused?2:0);
            // Gameplay commits are deliberately distinct from v3 byte ACKs.
            // Bound their diagnostic queue without logging inputs or identities.
            for(int i=0;i<64&&StationPsxBridge.nativeTakeCommit()!=null;i++){}
        }catch(Exception failure){fatal("PSX_CONTROL_STATUS");}}
        void humanExit(){synchronized(this){if(closed||human)return;human=true;reportedStatus=-8;}refreshWifiLatency();
            activity.runOnUiThread(()->activity.setResult(Activity.RESULT_OK));
            if(events!=null)events.send(4,null);hideWaiting();StationPsxLaunch.discard(activity,name);
            worker.execute(()->{StationMultiplayerSession t=transport;if(t!=null)t.close();if(updates!=null)updates.cancel(false);
                StationSessionLink link=owner;CountDownLatch binderClosed=new CountDownLatch(link==null?0:1);
                if(link!=null)activity.runOnUiThread(()->{try{link.close();}finally{binderClosed.countDown();}});
                StationPsxBridge.nativeAuthorizeHumanExit();
                finishHumanCleanup(t,binderClosed);});
        }
        private void finishHumanCleanup(StationMultiplayerSession transport,CountDownLatch binderClosed){
            // Join IO only on this private worker. A blocked callback or IO thread
            // keeps cleanup incomplete; no timeout is authority to kill a game.
            try{
                if(binderClosed.getCount()!=0||transport!=null&&!transport.awaitClosed(250)){
                    worker.schedule(()->finishHumanCleanup(transport,binderClosed),50,TimeUnit.MILLISECONDS);return;
                }
                humanCleanupComplete=true;closed=true;worker.shutdown();
                activity.runOnUiThread(()->{if(activity instanceof StationPsxOnlineActivity)((StationPsxOnlineActivity)activity).finishRetiredOwner();});
            }catch(InterruptedException interrupted){Thread.currentThread().interrupt();/* no false cleanup/automatic exit */}
        }
        private void showWaiting(String message){activity.runOnUiThread(()->{if(closed||human||!visible||activity.isFinishing())return;
            if(waiting==null){LinearLayout panel=new LinearLayout(activity);panel.setPadding(24,16,24,16);panel.setBackgroundColor(0xff10151c);
                waitingText=new TextView(activity);waitingText.setTextColor(0xffeaf2ff);waitingText.setTextSize(15);panel.addView(waitingText);
                waiting=new Dialog(activity);waiting.requestWindowFeature(Window.FEATURE_NO_TITLE);waiting.setContentView(panel);waiting.setCancelable(false);waiting.show();
                Window w=waiting.getWindow();if(w!=null){w.setDimAmount(0);w.addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE);w.setGravity(Gravity.TOP);}}
            waitingText.setText(message);});}
        private void hideWaiting(){activity.runOnUiThread(()->{if(waiting!=null){waiting.dismiss();waiting=null;waitingText=null;}});}
    }
}
