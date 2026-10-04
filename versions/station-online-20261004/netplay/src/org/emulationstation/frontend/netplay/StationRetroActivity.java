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
    private String roomId,engine;private ResultReceiver sessionEvents;private boolean host;private volatile boolean listening,visible;
    @Override public void onCreate(Bundle state){
        try{
            sessionEvents=getIntent().getParcelableExtra(StationGameSession.EXTRA);
            if(sessionEvents==null)throw new IllegalStateException("Session owner unavailable");
            JSONObject launch=StationRetroLaunch.consume(this,getIntent().getStringExtra("station.launch"));roomId=launch.getString("roomId");engine=launch.getString("engine");host="host".equals(launch.getString("role"));
            Intent i=getIntent();i.putExtra("ROM",launch.getString("rom"));i.putExtra("LIBRETRO",launch.getString("core"));i.putExtra("CONFIGFILE",launch.getString("config"));i.putExtra("USED","false");i.putExtra("APK",getApplicationInfo().sourceDir);i.putExtra("DATADIR",getFilesDir().toString());i.putExtra("SDCARD",getFilesDir().toString());i.putExtra("EXTERNAL",getFilesDir().toString());
            i.putExtra("STATION_NETPLAY_ROLE",launch.getString("role"));i.putExtra("STATION_NETPLAY_ADDRESS",launch.getString("address"));i.putExtra("STATION_NETPLAY_PORT",String.valueOf(launch.getInt("port")));
        }catch(Exception error){super.onCreate(state);Toast.makeText(this,"Não foi possível preparar a partida. Volte à sala e tente novamente.",Toast.LENGTH_LONG).show();finish();return;}
        super.onCreate(state);getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);getWindow().getDecorView().setSystemUiVisibility(5894);
    }
    @Override protected void onStart(){super.onStart();visible=true;if(sessionEvents!=null){Bundle data=new Bundle();data.putParcelable("reply",new ResultReceiver(new Handler(Looper.getMainLooper())){@Override protected void onReceiveResult(int code,Bundle value){if(visible&&code==100&&value!=null)notice(value.getString("message","Confira a conexão da sala."));}});sessionEvents.send(1,data);if(host&&listening)sessionEvents.send(3,null);}}
    public void onNetplayListening(){listening=true;if(host&&visible&&sessionEvents!=null)sessionEvents.send(3,null);}
    @Override protected void onStop(){visible=false;if(sessionEvents!=null)sessionEvents.send(2,null);super.onStop();}
    private boolean notified;private void notice(String text){if(!notified&&!isFinishing()){notified=true;new AlertDialog.Builder(this).setTitle("LZ GAMES • Conexão").setMessage(text).setPositiveButton("Entendi",null).show();}}
    public void onRetroArchExit(){StationRetroLaunch.clearSecret(this,roomId);runOnUiThread(this::finish);}
    @Override protected void onDestroy(){if(sessionEvents!=null)sessionEvents.send(4,null);StationRetroLaunch.clearSecret(this,roomId);super.onDestroy();}
    @Override public void onBackPressed(){new AlertDialog.Builder(this).setTitle("LZ GAMES • Partida online").setMessage("Sair encerra sua conexão e retorna às salas. O botão de menu dos controles abre as opções do emulador.").setNegativeButton("Continuar",null).setPositiveButton("Sair da partida",(d,w)->finish()).show();}
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
