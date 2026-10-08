package org.emulationstation.frontend.netplay;
import android.app.*;
import android.content.*;
import android.content.pm.ActivityInfo;
import android.os.*;
import android.view.*;
import android.view.accessibility.AccessibilityManager;
import android.widget.Toast;
import org.emulationstation.frontend.station.*;
import org.json.*;
import java.io.File;
import java.util.Locale;
import java.util.concurrent.*;

/** Dedicated :station_netplay process: upstream RetroArch owns video, audio, touch and gamepads. */
public final class StationRetroActivity extends NativeActivity {
    private StationRelayTunnel relay;private boolean relayPaused;
    private StationSessionLink sessionLink;private boolean ownerReady,transportStarted,quitRequested;
    private String ownerFailure;
    public native boolean stationRequestQuit();
    private StationRecoveryTunnel recovery;private boolean humanExit,recoveryWaiting=true,recoverySynchronizing,recoveryLost;private volatile boolean nativeLoaded;
    private Dialog recoveryDialog;private android.widget.LinearLayout recoveryPanel;private android.widget.TextView recoveryText;private android.widget.ProgressBar recoveryProgress;
    public static native void stationRecoveryControl(long epoch,boolean pause,boolean visible);
    public static native long stationRecoveryStatus();
    public static native boolean stationRecoveryStalled();
    private Object backRegistration;private AlertDialog exitDialog;
    private String roomId,engine,pendingNotice,recoveryReason;private ResultReceiver sessionEvents;private boolean host;private volatile boolean listening,visible;
    @Override public void onCreate(Bundle state){
        try{
            sessionEvents=StationSessionChannel.read(getIntent().getExtras(),StationGameSession.EXTRA);
            if(sessionEvents==null)throw new IllegalStateException("Session owner unavailable");
            JSONObject launch=StationRetroLaunch.consume(this,getIntent().getStringExtra("station.launch"));roomId=launch.getString("roomId");engine=launch.getString("engine");host="host".equals(launch.getString("role"));
            if("station-stream.v2".equals(launch.optString("recoveryProtocol"))){
                recovery=new StationRecoveryTunnel(StationRelayTls.endpoint(),launch.getString("relayTicket"),launch.getString("relayRequestProof"),launch.getInt("windowBytes"),host,launch.getInt("port"),StationRelayTls.create(),new StationRecoveryTunnel.Listener(){
                    @Override public void trace(String event){android.util.Log.i("StationRecovery","correlation="+launch.optString("relayCorrelation","")+" generation="+launch.optLong("generation")+" role="+(host?"host":"client")+" "+event);}
                    @Override public void ticket(){if(sessionEvents!=null&&!sessionFinished)sessionEvents.send(5,null);}
                    @Override public void ready(){runOnUiThread(()->{if(sessionFinished||isDestroyed())return;listening=true;if(host&&visible&&sessionEvents!=null)sessionEvents.send(3,null);});}
                    @Override public void state(boolean wait,boolean synchronizing){runOnUiThread(()->{recoveryWaiting=wait;recoverySynchronizing=synchronizing;drawRecovery();});}
                    @Override public void nativeControl(long epoch,boolean pause,boolean shown){runOnUiThread(()->{if(!sessionFinished&&nativeLoaded)try{stationRecoveryControl(epoch,pause,shown);}catch(LinkageError error){android.util.Log.e("StationRooms","game stage=native-hook-failed type="+error.getClass().getSimpleName());unrecoverable("NATIVE_HOOK");}});}
                    @Override public long nativeStatus(){if(!nativeLoaded)return -1;try{return stationRecoveryStatus();}catch(LinkageError error){return -1;}}
                    @Override public boolean nativeStalled(){if(!nativeLoaded)return false;try{return stationRecoveryStalled();}catch(LinkageError error){return false;}}
                    @Override public void unrecoverable(String category){runOnUiThread(()->{if(sessionFinished||recoveryLost)return;recoveryLost=true;recoveryReason=category;recoveryWaiting=true;android.util.Log.w("StationRooms","game stage=recovery-unrecoverable category="+category);if(sessionEvents!=null)sessionEvents.send(6,null);drawRecovery();});}
                });
                launch.put("address","127.0.0.1").put("port",recovery.localPort());
            }else if(launch.has("relayTicket")){
                relay=new StationRelayTunnel(StationRelayTls.endpoint(),launch.getString("relayTicket"),launch.optString("relayRequestProof",null),host,launch.getInt("port"),StationRelayTls.create(),new StationRelayTunnel.Listener(){
                    @Override public void ready(){runOnUiThread(()->{
                        if(sessionFinished||relayPaused||isFinishing()||isDestroyed()||relay==null||!relay.available())return;
                        android.util.Log.i("StationRooms","game stage=local-stream-ready role="+(host?"host":"client"));
                        listening=true;if(host&&visible&&sessionEvents!=null)sessionEvents.send(3,null);
                    });}
                    @Override public void trace(String event){android.util.Log.i("StationRelay",event);}
                    @Override public void failed(){failed(StationRelayTunnel.Failure.RELAY);}
                    @Override public void failed(StationRelayTunnel.Failure reason){runOnUiThread(()->{
                        listening=false;if(sessionFinished||isFinishing()||isDestroyed())return;
                        android.util.Log.w("StationRooms","game stage=relay-failed reason="+reason.name()+" role="+(host?"host":"client"));
                        pendingNotice=reason==StationRelayTunnel.Failure.NATIVE_LISTENER?
                            "O motor do jogo não abriu a conexão online neste aparelho. Volte às salas para tentar novamente. A outra pessoa ainda não entrou na partida.":
                            "A conexão da partida foi encerrada. Saia para voltar às salas e iniciar uma nova partida.";
                        if(visible)notice(pendingNotice);
                    });}
                });
                launch.put("address","127.0.0.1").put("port",relay.localPort());
            }
            sessionLink=new StationSessionLink(this,getIntent().getStringExtra(StationGameSession.ANCHOR_EXTRA),roomId,launch.optLong("generation",0),new StationSessionLink.Listener(){
                @Override public void ready(){if(sessionFinished||isFinishing()||isDestroyed())return;ownerReady=true;ownerFailure=null;android.util.Log.i("StationRooms","game stage=session-owner-bound");if(visible)startSessionOwner();}
                @Override public void unavailable(String category){if(sessionFinished||isFinishing()||isDestroyed())return;ownerReady=false;ownerFailure=category;recoveryWaiting=true;android.util.Log.w("StationRooms","game stage=session-owner-wait category="+category);if(recovery!=null&&transportStarted)recovery.visible(false);drawRecovery();}
            });
            Intent i=getIntent();i.putExtra("ROM",launch.getString("rom"));i.putExtra("LIBRETRO",launch.getString("core"));i.putExtra("CONFIGFILE",launch.getString("config"));i.putExtra("USED","false");i.putExtra("APK",getApplicationInfo().sourceDir);i.putExtra("DATADIR",getFilesDir().toString());i.putExtra("SDCARD",getFilesDir().toString());i.putExtra("EXTERNAL",getFilesDir().toString());
            i.putExtra("STATION_NETPLAY_ROLE",launch.getString("role"));i.putExtra("STATION_NETPLAY_ADDRESS",launch.getString("address"));i.putExtra("STATION_NETPLAY_PORT",String.valueOf(launch.getInt("port")));
            i.putExtra("STATION_RECOVERY_PROTOCOL",launch.optString("recoveryProtocol",""));
        }catch(Exception error){android.util.Log.e("StationRooms","game stage=launch-failed type="+error.getClass().getSimpleName());if(recovery!=null)recovery.close();if(relay!=null)relay.close();super.onCreate(state);Toast.makeText(this,"Não foi possível preparar a partida. Volte à sala e tente novamente.",Toast.LENGTH_LONG).show();finish();return;}
        try{super.onCreate(state);if(recovery!=null){System.loadLibrary("station_retroarch");stationRecoveryStatus();stationRecoveryStalled();android.util.Log.i("StationRooms","game stage=native-hooks-loaded");}}catch(RuntimeException|LinkageError error){android.util.Log.e("StationRooms","game stage=native-start-failed type="+error.getClass().getSimpleName());if(recovery!=null)recovery.close();if(relay!=null)relay.close();Toast.makeText(this,"O motor do jogo não iniciou. Volte às salas para tentar novamente.",Toast.LENGTH_LONG).show();finish();return;}
        nativeLoaded=true;if(recovery!=null)installRecoveryPanel();if(sessionLink!=null)sessionLink.bind();
        if(Build.VERSION.SDK_INT>=33)backRegistration=Back33.register(this);getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);getWindow().getDecorView().setSystemUiVisibility(5894);installOnlineMenuButton();
    }
    @Override protected void onStart(){super.onStart();if(sessionFinished)return;visible=true;if(relayPaused){notice("A partida online foi encerrada ao sair do aplicativo. Volte às salas para jogar novamente.");}if(pendingNotice!=null)notice(pendingNotice);if(ownerReady)startSessionOwner();else drawRecovery();}
    private void startSessionOwner(){
        if(!ownerReady||!visible||sessionFinished)return;
        if(sessionEvents!=null){Bundle data=new Bundle();data.putParcelable("reply",StationSessionChannel.transport(new ResultReceiver(new Handler(Looper.getMainLooper())){@Override protected void onReceiveResult(int code,Bundle value){
            if(sessionFinished||value==null)return;
            if(recovery!=null&&code==101){try{recovery.provide(value.getString("ticket"),value.getString("proof"),value.getInt("windowBytes"));}catch(Exception error){recovery.reject();}}
            else if(recovery!=null&&code==102){if(value.getBoolean("terminal"))recovery.reject();else recovery.unavailable();}
            else if(visible&&code==100)notice(value.getString("message","Confira a conexão da sala."));
        }}));sessionEvents.send(1,data);if(host&&listening&&(relay==null||relay.available()))sessionEvents.send(3,null);}
        if(!transportStarted){transportStarted=true;if(recovery!=null)recovery.start();if(relay!=null)relay.start();}
        if(recovery!=null){recovery.visible(true);drawRecovery();}
    }
    public void onNetplayListening(){android.util.Log.i("StationRooms","game stage=native-listening role="+(host?"host":"client"));if(recovery!=null){recovery.listening();return;}if(relay!=null){relay.listening();return;}if(sessionFinished)return;listening=true;if(host&&visible&&sessionEvents!=null)sessionEvents.send(3,null);}
    @Override protected void onStop(){android.util.Log.i("StationRooms","game stage=activity-stop finishing="+isFinishing());visible=false;if(recovery!=null){if(transportStarted)recovery.visible(false);drawRecovery();}if(relay!=null){relayPaused=true;relay.close();}if(sessionEvents!=null)sessionEvents.send(2,null);super.onStop();}
    private boolean notified;private void notice(String text){if(!notified&&!isFinishing()){notified=true;new AlertDialog.Builder(this).setTitle("LZ GAMES • Conexão").setMessage(text).setPositiveButton("Entendi",null).show();}}
    public void onRetroArchExit(){StationRetroLaunch.clearSecret(this,roomId);runOnUiThread(this::finish);}
    private volatile boolean sessionFinished;
    private synchronized void closeSession(){
        if(sessionFinished)return;sessionFinished=true;visible=false;listening=false;
        if(recovery!=null)recovery.close();if(relay!=null)relay.close();
        if(recovery!=null)recovery.close();
        if(sessionEvents!=null)sessionEvents.send(recovery!=null&&!humanExit?6:4,null);
        StationRetroLaunch.clearSecret(this,roomId);
        android.util.Log.i("StationRooms","game stage=session-ended");
    }
    @Override public void finish(){closeSession();super.finish();}
    @Override protected void onDestroy(){dismissRecoveryPanel();if(sessionLink!=null){sessionLink.close();sessionLink=null;}if(Build.VERSION.SDK_INT>=33&&backRegistration!=null)Back33.unregister(this,backRegistration);if(exitDialog!=null)exitDialog.dismiss();closeSession();super.onDestroy();}
    @Override public void onBackPressed(){showExitMenu();}
    @Override public boolean dispatchKeyEvent(KeyEvent event){
        if(event.getKeyCode()==KeyEvent.KEYCODE_BACK){
            if(event.getAction()==KeyEvent.ACTION_UP&&!event.isCanceled())showExitMenu();
            return true;
        }
        return super.dispatchKeyEvent(event);
    }
    private void installOnlineMenuButton(){
        // Only this small view handles its own touch target. Game touches stay native.
        android.widget.TextView menu=new android.widget.TextView(this);
        menu.setText("⋮");menu.setTextSize(30);menu.setTextColor(0xb3ffffff);
        menu.setGravity(Gravity.CENTER);menu.setContentDescription("Menu da partida online");
        menu.setClickable(true);menu.setFocusable(true);menu.setBackgroundColor(0x00000000);
        menu.setOnClickListener(v->showExitMenu());
        float density=getResources().getDisplayMetrics().density;
        android.widget.FrameLayout.LayoutParams p=new android.widget.FrameLayout.LayoutParams((int)(48*density),(int)(48*density),Gravity.TOP|Gravity.RIGHT);
        p.topMargin=(int)(8*density);p.rightMargin=(int)(12*density);addContentView(menu,p);
    }
    private void showExitMenu(){
        if(isFinishing()||isDestroyed()||(exitDialog!=null&&exitDialog.isShowing()))return;
        exitDialog=StationExitPanel.create(this,this::confirmExit);
        exitDialog.setOnDismissListener(d->{exitDialog=null;if(!isFinishing())getWindow().getDecorView().setSystemUiVisibility(5894);});
        exitDialog.show();android.util.Log.i("StationRooms","game stage=exit-menu");
    }
    private void confirmExit(){new AlertDialog.Builder(this).setTitle("Sair da partida?").setMessage("Isso encerra sua participação e avisa o outro jogador.").setNegativeButton("Continuar",null).setPositiveButton("Sair da partida",(dialog,which)->requestHumanExit()).show();}
    private void requestHumanExit(){
        if(quitRequested)return;quitRequested=true;humanExit=true;
        // Notify the main authority before native teardown, which may end this private process.
        closeSession();
        if(nativeLoaded)try{if(stationRequestQuit())return;}catch(LinkageError error){android.util.Log.e("StationRooms","game stage=quit-hook-failed");}
        finish();
    }
    private void installRecoveryPanel(){
        // NativeActivity renders EGL into its own window. Waiting needs a separate application
        // window; adding a View to the native window can leave it invisible below the EGL frame.
        drawRecovery();
    }
    private void createRecoveryPanel(){
        recoveryDialog=new Dialog(this);recoveryDialog.setOwnerActivity(this);
        recoveryDialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        recoveryDialog.setCancelable(false);recoveryDialog.setCanceledOnTouchOutside(false);
        recoveryPanel=new android.widget.LinearLayout(this);recoveryPanel.setOrientation(1);recoveryPanel.setGravity(Gravity.CENTER);recoveryPanel.setBackgroundColor(0xe610171f);
        recoveryText=new android.widget.TextView(this);recoveryText.setTextColor(0xffefffff);recoveryText.setTextSize(20);recoveryText.setGravity(Gravity.CENTER);recoveryPanel.addView(recoveryText);
        recoveryProgress=new android.widget.ProgressBar(this);recoveryProgress.setIndeterminate(true);recoveryPanel.addView(recoveryProgress);
        android.widget.Button exit=new android.widget.Button(this);exit.setText("Sair da partida");exit.setOnClickListener(v->confirmExit());recoveryPanel.addView(exit);
        recoveryDialog.setContentView(recoveryPanel);
        Window window=recoveryDialog.getWindow();
        if(window!=null){
            // Keep native input/focus ownership. This window still receives its button touches;
            // hardware Back continues through the Activity's existing human exit confirmation.
            window.addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE);
            window.clearFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            window.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(0x00000000));
        }
    }
    private void drawRecovery(){
        if(!visible||!recoveryWaiting||sessionFinished||isFinishing()||isDestroyed()){dismissRecoveryPanel();return;}
        if(recoveryDialog==null)createRecoveryPanel();
        recoveryText.setText(!ownerReady?(ownerFailure==null?"Preparando a conexão da partida…":"Aguardando o serviço da partida…"):recoveryLost?("AUTHORITY".equals(recoveryReason)?"O servidor não autorizou a retomada. Confira seu acesso; você pode sair da partida.":"Não foi possível recuperar o estado desta partida. Você pode sair e iniciar outra sala."):recoverySynchronizing?"Sincronizando a partida…":"Aguardando conexão…");
        recoveryProgress.setVisibility(recoveryLost?View.GONE:View.VISIBLE);
        if(!recoveryDialog.isShowing()){
            recoveryDialog.show();Window window=recoveryDialog.getWindow();
            if(window!=null){window.setLayout(-1,-1);window.getDecorView().setSystemUiVisibility(5894);}
        }
    }
    private void dismissRecoveryPanel(){
        Dialog dialog=recoveryDialog;recoveryDialog=null;recoveryPanel=null;recoveryText=null;recoveryProgress=null;
        if(dialog!=null)dialog.dismiss();
    }
    private static final class Back33 {
        static Object register(StationRetroActivity activity){
            android.window.OnBackInvokedCallback callback=activity::showExitMenu;
            activity.getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,callback);
            return callback;
        }
        static void unregister(StationRetroActivity activity,Object callback){activity.getOnBackInvokedDispatcher().unregisterOnBackInvokedCallback((android.window.OnBackInvokedCallback)callback);}
    }
    public boolean isAndroidTV(){return ((UiModeManager)getSystemService(UI_MODE_SERVICE)).getCurrentModeType()==4;}
    public int getBatteryLevel(){BatteryManager b=(BatteryManager)getSystemService(BATTERY_SERVICE);return b.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);}
    public int getPowerstate(){Intent s=registerReceiver(null,new IntentFilter(Intent.ACTION_BATTERY_CHANGED));if(s==null)return 0;int status=s.getIntExtra(BatteryManager.EXTRA_STATUS,-1);return status==BatteryManager.BATTERY_STATUS_FULL?3:status==BatteryManager.BATTERY_STATUS_CHARGING?2:1;}
    public void setSustainedPerformanceMode(boolean on){runOnUiThread(()->getWindow().setSustainedPerformanceMode(on));}
    public void setScreenOrientation(int orientation){runOnUiThread(()->setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_USER_LANDSCAPE));}
    public String getUserLanguageString(){return Locale.getDefault().toLanguageTag();}
    public boolean isPlayStoreBuild(){return false;}
    public String[] getAvailableCores(){return getInstalledCores();}
    public String[] getInstalledCores(){return new String[]{"station_bsnes","station_clownmdemu","station_geolith"};}
    public void downloadCore(String name){runOnUiThread(()->Toast.makeText(this,"Os motores são atualizados junto com a TurboStations.",Toast.LENGTH_LONG).show());}
    public void deleteCore(String name){runOnUiThread(()->Toast.makeText(this,"Este motor faz parte do aplicativo e não pode ser removido durante a partida.",Toast.LENGTH_LONG).show());}
    public int getVolumeCount(){return 1;}
    public String getVolumePath(String index){return "0".equals(index)?getFilesDir().toString():"";}
    public void inputGrabMouse(boolean grab){runOnUiThread(()->{View v=getWindow().getDecorView();if(grab)v.requestPointerCapture();else v.releasePointerCapture();});}
    public boolean isScreenReaderEnabled(){return ((AccessibilityManager)getSystemService(ACCESSIBILITY_SERVICE)).isEnabled();}
    public void accessibilitySpeak(String text){runOnUiThread(()->getWindow().getDecorView().announceForAccessibility(text));}
    public void doHapticFeedback(int effect){runOnUiThread(()->getWindow().getDecorView().performHapticFeedback(effect));}
    public void doVibrate(int id,int effect,int strength,int oneShot){Vibrator v=null;InputDevice d=id<0?null:InputDevice.getDevice(id);v=d==null?(Vibrator)getSystemService(VIBRATOR_SERVICE):d.getVibrator();if(v==null||!v.hasVibrator())return;if(strength<=0){v.cancel();return;}v.vibrate(VibrationEffect.createOneShot(oneShot>0?Math.min(oneShot,1000):16,Math.min(255,strength)));}
}
