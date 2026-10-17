package org.emulationstation.frontend.netplay;

import android.app.*;
import android.content.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.lang.reflect.*;
import java.net.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.json.*;

/** Owns the real Dolphin NetplaySession and real EmulationActivity. Room HTTP
 * authority remains in StationGameSession; DATA uses the existing signed v3
 * links. Native pointers are released only by the serialized session worker. */
public final class StationDolphinSession {
    private static volatile Session current;
    private StationDolphinSession(){}
    public static synchronized void start(Activity entry,String name,JSONObject launch)throws Exception {
        Session s=current;
        if(s!=null){if(s.closed||!s.name.equals(name))throw new IOException("DOLPHIN_OWNER_CONFLICT");s.replaceEntry(entry);return;}
        if(!StationDolphinSelector.selected(name))throw new IOException("DOLPHIN_PROCESS_VARIANT");
        current=new Session(entry,name,launch);current.initialize();
    }
    public static void entryVisible(Activity entry,boolean shown){Session s=current;if(s!=null&&entry==s.entry&&(!s.bootDispatched||shown&&!s.childActive))s.visible(shown);}
    public static boolean gameReturned(Activity entry,int code){Session s=current;if(s==null||entry!=s.entry)return false;s.childActive=false;
        if(s.human)return true;s.game=null;s.visible(true);s.fatal("DOLPHIN_UNEXPECTED_RETURN");return false;}
    public static void confirmExit(Activity entry){Session s=current;if(s==null){
        String name=entry.getIntent().getStringExtra(StationDolphinSelector.EXTRA);
        ResultReceiver events=StationSessionChannel.read(entry.getIntent().getExtras(),StationGameSession.EXTRA);if(events!=null)events.send(4,null);
        StationDolphinLaunch.discard(entry,name);
        if(StationDolphinSelector.selected(name))StationDolphinSelector.finishOnlineProcess(entry);
        else{entry.setResult(Activity.RESULT_CANCELED);entry.finish();}
        return;}
        new AlertDialog.Builder(entry).setTitle("Sair da partida?").setMessage("A partida será encerrada neste aparelho.")
            .setNegativeButton("Continuar",null).setPositiveButton("Sair",(d,w)->humanClose(entry,()->StationDolphinSelector.finishOnlineProcess(entry))).show();}
    public static void humanClose(Activity entry,Runnable done){Session s=current;if(s==null||entry!=s.entry)throw new IllegalStateException("DOLPHIN_OWNER");s.closeByHuman(done);}
    public static void onGameCreate(Activity activity){Session s=current;String name=activity.getIntent().getStringExtra(StationDolphinSelector.EXTRA);
        if(s==null){if(name!=null)throw new IllegalStateException("DOLPHIN_OWNER_MISSING");return;}
        if(!s.name.equals(name))throw new IllegalStateException("DOLPHIN_OWNER_MISMATCH");
        String[] paths=activity.getIntent().getStringArrayExtra("SelectedGames");
        if(paths==null||paths.length!=1||!s.rom.equals(paths[0]))throw new IllegalStateException("DOLPHIN_GAME_MISMATCH");
        s.hideWaiting();s.game=activity;s.childActive=true;
    }
    public static void onGameResume(Activity activity){Session s=current;if(s!=null&&s.game==activity)s.visible(true);}
    public static void onGamePause(Activity activity){Session s=current;if(s!=null&&s.game==activity)s.visible(false);}
    public static void onGameDestroy(Activity activity){Session s=current;if(s!=null&&s.game==activity&&activity.isFinishing()){
        if(s.human)activity.setResult(Activity.RESULT_OK);else s.fatal("DOLPHIN_UNEXPECTED_EXIT");}}
    public static void onMenuAction(Activity activity,int action){Session s=current;if(s!=null&&s.game==activity&&action==22)s.authorizeHuman();}
    public static boolean allowMenuAction(Activity activity,int action){Session s=current;
        if(s==null||s.game!=activity||action<6||action>21)return true;
        android.widget.Toast.makeText(activity,"Estados rápidos ficam indisponíveis durante a partida online.",android.widget.Toast.LENGTH_SHORT).show();return false;}
    public static boolean allowSaveState(Activity activity){Session s=current;return s==null||s.game!=activity;}
    public static boolean onBootGame(Object official,String path){Session s=current;if(s==null||s.official!=official)return false;s.boot(path);return true;}
    public static boolean onNativeStop(Object official){Session s=current;if(s==null||s.official!=official)return false;if(!s.human)s.fatal("DOLPHIN_NATIVE_STOP");return !s.human;}
    public static boolean onConnectionLost(Object official){Session s=current;if(s==null||s.official!=official)return false;if(!s.human)s.fatal("DOLPHIN_NATIVE_CONNECTION");return true;}
    public static boolean onConnectionError(Object official,String message){Session s=current;if(s==null||s.official!=official)return false;s.fatal("DOLPHIN_NATIVE_CONNECT");return true;}
    public static boolean allowClose(Object official){Session s=current;return s==null||s.official!=official||s.human;}
    private static Class<?> type(String name)throws ClassNotFoundException{return Class.forName(name);}
    private static Object field(Object object,String name)throws Exception{Field f=object instanceof Class?((Class<?>)object).getDeclaredField(name):object.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(object instanceof Class?null:object);}
    private static void put(Object object,String name,Object value)throws Exception{Field f=object instanceof Class?((Class<?>)object).getDeclaredField(name):object.getClass().getDeclaredField(name);f.setAccessible(true);f.set(object instanceof Class?null:object,value);}
    private static Object callStatic(String name,String method,Class<?>[] types,Object...args)throws Exception{return type(name).getMethod(method,types).invoke(null,args);}

    private static final class Session implements StationMultiplayerSession.Listener {
        volatile Activity entry,game;final String name,rom,platform;final JSONObject launch;final boolean host;final int slot,mask;
        final ResultReceiver events;final StationSessionLink owner;final StationMultiplayerSession transport;
        final ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"Station-Dolphin-session");t.setDaemon(true);return t;});
        volatile Object official;volatile boolean visible,ownerReady,started,closed,closing,human,failed,bootDispatched,childActive,connected,configured;
        private static final class Control {final long epoch,serial;final boolean pause;Control(long epoch,long serial,boolean pause){this.epoch=epoch;this.serial=serial;this.pause=pause;}}
        final AtomicReference<Control> desired=new AtomicReference<>(new Control(1,1,true));
        volatile long reportedStatus=-8;
        private long appliedEpoch=-1;private boolean appliedPause=true,gameStartRequested,coreBarrierEstablished;private Dialog waiting;private TextView waitingText;
        private ScheduledFuture<?> updates;
        Session(Activity entry,String name,JSONObject launch)throws Exception{
            this.entry=entry;this.name=name;this.launch=launch;rom=launch.getString("rom");platform=launch.getString("platform");
            host="host".equals(launch.getString("role"));slot=launch.getInt("localSlot");mask=launch.getInt("expectedDeviceMask");
            events=StationSessionChannel.read(entry.getIntent().getExtras(),StationGameSession.EXTRA);if(events==null)throw new IOException("DOLPHIN_OWNER_MISSING");
            transport=new StationMultiplayerSession(new JSONObject(launch.toString()).put("port",0),this,StationDolphinEndpoint.factory());
            owner=new StationSessionLink(entry,entry.getIntent().getStringExtra(StationGameSession.ANCHOR_EXTRA),launch.getString("roomId"),launch.getLong("generation"),new StationSessionLink.Listener(){
                public void ready(){if(closed||closing)return;ownerReady=true;if(visible)startOwner();}
                public void unavailable(String category){if(closed||closing)return;ownerReady=false;transport.visible(false);showWaiting("Aguardando a conexão da sala…");}
            });owner.bind();
        }
        void replaceEntry(Activity next){hideWaiting();entry=next;}
        void initialize(){worker.execute(()->{try{
            // Parsing an ISO/cache entry can be expensive; it never runs on UI.
            Class<?> fileType=type("org.dolphinemu.dolphinemu.model.GameFile");
            Object file=fileType.getMethod("parse",String.class).invoke(null,rom);if(file==null)throw new IOException("DOLPHIN_GAME_FILE");
            // Pinned DiscIO::Platform: GameCubeDisc=0, Triforce=1, WiiDisc=2.
            int detected=(Integer)fileType.getMethod("getPlatform").invoke(file);
            if(detected!=("gamecube".equals(platform)?0:2))throw new IOException("DOLPHIN_GAME_PLATFORM");
            CountDownLatch made=new CountDownLatch(1);AtomicReference<Throwable> error=new AtomicReference<>();
            entry.runOnUiThread(()->{try{
                if(closing)throw new IOException("DOLPHIN_CANCELED");
                Object games=Array.newInstance(fileType,1);Array.set(games,0,file);
                Object data=field(type("org.dolphinemu.dolphinemu.services.GameFileCacheManager"),"gameFiles");
                data.getClass().getMethod("setValue",Object.class).invoke(data,games);
                Class<?> callback=type("org.dolphinemu.dolphinemu.model.TaskViewModel$$ExternalSyntheticLambda0");
                Object onClosed=callback.getConstructor(Integer.TYPE).newInstance(2);
                official=type("org.dolphinemu.dolphinemu.features.netplay.NetplaySession").getConstructor(callback).newInstance(onClosed);
                put(type("org.dolphinemu.dolphinemu.features.netplay.NetplayManager"),"activeSession",official);
            }catch(Throwable failure){error.set(failure);}finally{made.countDown();}});
            made.await();if(error.get()!=null)throw new IOException("DOLPHIN_OFFICIAL_SESSION",error.get());if(closing)return;
            int port;try(DatagramSocket reservation=new DatagramSocket(0,InetAddress.getByName("127.0.0.1"))){port=reservation.getLocalPort();}
            if(closing)return;
            if(!StationDolphinBridge.nativeConfigure(host,slot,mask<<1,port,1,"Player "+slot))throw new IOException("DOLPHIN_NATIVE_CONFIG");
            configured=true;
            StationDolphinCpuPolicy.configure(platform);
            if(closing){StationDolphinBridge.nativeAuthorizeHumanExit(official);StationDolphinBridge.nativeCloseTransport();return;}
            // STATE may have arrived during parsing. Hold native clocks before
            // Join; DATA still flows, and CPU idle is acknowledged separately.
            StationDolphinBridge.nativeSuspendTransport(desired.get().epoch);
            Control pending=desired.get();StationDolphinBridge.nativeControl(pending.epoch,pending.serial,pending.pause||failed||!visible);
            if(failed){StationDolphinBridge.nativeFail("DOLPHIN_PREPARATION_FAILED");return;}
            transport.listening();
            if(!StationDolphinBridge.nativeConnect(official,host))throw new IOException("DOLPHIN_NATIVE_CONNECT");
            connected=true;if(closing)return;
            if(host)StationDolphinBridge.nativeSelectGame(official,file);
            updates=worker.scheduleWithFixedDelay(this::update,0,50,TimeUnit.MILLISECONDS);
        }catch(Exception failure){if(!closing&&!closed)fatal("DOLPHIN_INITIALIZATION");}});}
        void visible(boolean shown){if(closed||closing)return;visible=shown;if(!shown){nativeControl(desired.get().epoch,true,false);transport.visible(false);events.send(2,null);hideWaiting();}else if(ownerReady)startOwner();else showWaiting("Aguardando a conexão da sala…");}
        private void startOwner(){if(closed||closing||!visible||!ownerReady)return;
            Bundle b=new Bundle();b.putParcelable("reply",StationSessionChannel.transport(new ResultReceiver(new Handler(Looper.getMainLooper())){
                protected void onReceiveResult(int code,Bundle value){if(closed||closing||value==null)return;
                    if(code==103)try{transport.provide(value.getString("linkId"),value.getLong("serial"),new JSONObject(value.getString("descriptor")));}catch(Exception e){transport.unavailable(value.getString("linkId"),value.getLong("serial"),true);}
                    else if(code==104)transport.unavailable(value.getString("linkId"),value.getLong("serial"),value.getBoolean("terminal"));
                    else if(code==102&&value.getBoolean("terminal"))fatal("DOLPHIN_AUTHORITY");
                }}));events.send(1,b);if(!started){started=true;transport.start();}transport.visible(!failed);
        }
        public void nativeControl(long epoch,boolean pause,boolean shown){if(closed||closing||epoch<1)return;
            Control next,previous;
            boolean paused=pause||failed||!shown;
            do{previous=desired.get();if(epoch<previous.epoch||epoch==previous.epoch&&paused==previous.pause)return;next=new Control(epoch,previous.serial+1,paused);}while(!desired.compareAndSet(previous,next));
            // This freezes ENet immediately, even while official Connect is
            // holding its operations lock. It is deliberately NOT a CPU ACK.
            if(configured)StationDolphinBridge.nativeControl(next.epoch,next.serial,next.pause);
        }
        public long nativeStatus(){long status=reportedStatus;return status>=0&&(status&2)!=0&&!StationDolphinBridge.nativeDrained()?status&~2L:status;}
        public boolean nativeStalled(){return false;}
        public boolean bind(int port,int remote){return false;}
        public void unbind(int port,int remote){}
        public void ticket(String id,long serial){if(!closed&&!closing){Bundle b=new Bundle();b.putString("linkId",id);b.putLong("serial",serial);events.send(5,b);}}
        public void ready(){if(!closed&&!closing&&visible)events.send(3,null);}
        public void state(boolean waiting,boolean sync){if(waiting)showWaiting(sync?"Sincronizando os jogadores…":"Aguardando a conexão da sala…");else hideWaiting();}
        public void trace(String event){android.util.Log.i("StationDolphin",event);}
        public synchronized void fatal(String category){if(closed||closing||failed)return;failed=true;
            desired.updateAndGet(control->new Control(control.epoch,control.serial+1,true));
            if(configured)StationDolphinBridge.nativeFail(category);events.send(6,null);
            showWaiting("A partida precisa de atenção. Aguarde a conexão ou saia pelo menu para criar uma nova sala.");android.util.Log.w("StationDolphin",category);}
        private void update(){if(closed||closing)return;try{
            Control control=desired.get();long epoch=control.epoch;
            // Even when the first fresh STATE already grants resume, establish
            // the actual local epoch/boot barrier before using that permission.
            boolean pause=control.pause||failed||!visible||!coreBarrierEstablished||appliedEpoch!=epoch;
            if(epoch>0&&(epoch!=appliedEpoch||pause!=appliedPause)){
                boolean ok=pause?StationDolphinBridge.nativePauseAtEpoch(official,epoch):StationDolphinBridge.nativeResumeAtEpoch(epoch,control.serial);
                if(control!=desired.get()||closing)return;
                if(!ok){if(!StationDolphinBridge.nativeFailure().isEmpty())fatal("DOLPHIN_CPU_BARRIER");return;}appliedEpoch=epoch;appliedPause=pause;
            }
            int flags=StationDolphinBridge.nativeStatus(official);
            if((flags&StationDolphinBridge.FAILED)!=0){reportedStatus=Math.max(1,epoch)*8|4;fatal("DOLPHIN_NATIVE_FAILURE");return;}
            if((flags&StationDolphinBridge.CORE_RUNNING)!=0&&!coreBarrierEstablished){
                // The pre-boot idle ACK holds the gate, but is not evidence that
                // the subsequently created CPU thread has reached its barrier.
                boolean idle=StationDolphinBridge.nativePauseAtEpoch(official,epoch);
                if(control!=desired.get()||closing)return;
                if(!idle)return;coreBarrierEstablished=true;
                flags=StationDolphinBridge.nativeStatus(official);
            }
            boolean roster=(flags&StationDolphinBridge.CLIENT_CONNECTED)!=0&&(!host||(flags&StationDolphinBridge.EXACT_HOST_ROSTER)!=0);
            if(host&&roster&&!gameStartRequested){int[] ports=new int[4];for(int i=0;i<4;i++)if((mask&(1<<i))!=0)ports[i]=i+1;
                if(!StationDolphinBridge.nativeMapControllers(official,"gamecube".equals(platform)?ports:new int[4],"wii".equals(platform)?ports:new int[4]))throw new IOException("DOLPHIN_NATIVE_MAPPING");
                gameStartRequested=StationDolphinBridge.nativeStartGame(official);
            }
            long acknowledged=StationDolphinBridge.nativeAcknowledgedEpoch();boolean paused=appliedPause&&acknowledged==epoch&&epoch>0;
            boolean ready=roster&&coreBarrierEstablished&&(flags&StationDolphinBridge.CORE_RUNNING)!=0&&(flags&StationDolphinBridge.LOCAL_DRAINED)!=0;
            if(control==desired.get()&&!closing)reportedStatus=epoch<1?-8:epoch*8|(paused?1:0)|(ready?2:0);
        }catch(Exception failure){fatal("DOLPHIN_SESSION_CONTROL");}}
        void boot(String path){if(closed||closing||bootDispatched)return;
            if(!rom.equals(path)){fatal("DOLPHIN_BOOT_GAME_MISMATCH");return;}bootDispatched=true;
            entry.runOnUiThread(()->{if(closed||closing)return;try{
                Intent intent=new Intent(entry,type("org.dolphinemu.dolphinemu.activities.EmulationActivity"));
                intent.putExtra("SelectedGames",new String[]{rom}).putExtra("Riivolution",false).putExtra("SystemMenu",false).putExtra(StationDolphinSelector.EXTRA,name);
                childActive=true;entry.startActivityForResult(intent,64);
            }catch(Exception failure){childActive=false;fatal("DOLPHIN_ACTIVITY_LAUNCH");}});
        }
        synchronized void authorizeHuman(){if(human||closed)return;if(configured&&!StationDolphinBridge.nativeAuthorizeHumanExit(official))throw new IllegalStateException("DOLPHIN_EXIT_AUTHORITY");human=true;events.send(4,null);}
        void closeByHuman(Runnable done){
            // Native callbacks take transport -> Session. Never retain Session
            // while canceling/closing transport, or explicit Exit can deadlock UI.
            synchronized(this){if(closed||closing)return;authorizeHuman();closing=true;visible=false;}
            if(configured)StationDolphinBridge.nativeCloseTransport();transport.close();if(updates!=null)updates.cancel(false);
            worker.execute(()->{try{
                if(configured)callStatic("org.dolphinemu.dolphinemu.NativeLibrary","StopEmulation",new Class<?>[0]);
                if(official!=null)official.getClass().getMethod("closeBlocking").invoke(official);
                owner.close();closed=true;hideWaiting();entry.runOnUiThread(done);
            }catch(Exception failure){closing=false;visible=true;showWaiting("Não foi possível concluir a saída. Tente novamente pelo menu.");android.util.Log.w("StationDolphin","DOLPHIN_EXIT_CLEANUP");}
            finally{if(closed)worker.shutdown();}});
        }
        private void showWaiting(String message){Activity target=game!=null?game:entry;target.runOnUiThread(()->{if(closed||!visible||target.isFinishing())return;if(waiting==null){
            LinearLayout panel=new LinearLayout(target);panel.setPadding(24,16,24,16);panel.setBackgroundColor(0xff10151c);waitingText=new TextView(target);waitingText.setTextColor(0xffeaf2ff);waitingText.setTextSize(15);panel.addView(waitingText);
            waiting=new Dialog(target);waiting.requestWindowFeature(Window.FEATURE_NO_TITLE);waiting.setContentView(panel);waiting.setCancelable(false);waiting.show();Window w=waiting.getWindow();if(w!=null){w.setDimAmount(0);w.addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE);w.setGravity(Gravity.TOP);}}
            waitingText.setText(message);});}
        private void hideWaiting(){Activity target=game!=null?game:entry;target.runOnUiThread(()->{if(waiting!=null){waiting.dismiss();waiting=null;waitingText=null;}});}
    }
}
