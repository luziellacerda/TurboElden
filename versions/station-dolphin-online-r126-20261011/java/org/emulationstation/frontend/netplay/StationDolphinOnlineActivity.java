package org.emulationstation.frontend.netplay;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.*;
import org.json.JSONObject;
import java.util.concurrent.*;

/** Private :dolphin entry. The official EmulationActivity remains the actual
 * renderer/controller owner; this entry owns only the Station launch/result. */
public final class StationDolphinOnlineActivity extends Activity {
    private final ExecutorService worker=Executors.newSingleThreadExecutor();
    private String launchName;private boolean childStarted,sessionStarted,closing;private TextView status;
    @Override protected void onCreate(Bundle saved){
        super.onCreate(saved);launchName=getIntent().getStringExtra(StationDolphinSelector.EXTRA);
        getWindow().setBackgroundDrawableResource(android.R.color.black);
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setGravity(Gravity.CENTER);panel.setPadding(32,24,32,24);panel.setBackgroundColor(0xff080d17);
        status=new TextView(this);status.setText("Conectando os jogadores…");status.setTextColor(0xffeaf2ff);status.setTextSize(17);status.setGravity(Gravity.CENTER);panel.addView(status);
        Button back=new Button(this);back.setText("Voltar");back.setOnClickListener(v->onBackPressed());panel.addView(back);setContentView(panel);
        if(saved!=null)childStarted=saved.getBoolean("childStarted");
        if(!StationDolphinSelector.selected(launchName)){
            try{StationDolphinSelector.requestIdleRestart(this);}catch(Exception failure){status.setText("O Dolphin está em uso. Saia da partida atual antes de entrar nesta sala.");}
            return;
        }
        worker.execute(()->{try{
            awaitDirectories();
            JSONObject launch;
            try{launch=StationDolphinLaunch.consume(this,launchName);}
            catch(java.io.FileNotFoundException consumed){if(saved==null)throw consumed;launch=StationDolphinSelector.descriptor();}
            if(launch==null)throw new IllegalStateException("DOLPHIN_SELECTED_DESCRIPTOR_MISSING");
            final JSONObject selectedLaunch=launch;
            runOnUiThread(()->{
                if(closing||isFinishing()||isDestroyed())return;
                try{StationDolphinSession.start(this,launchName,selectedLaunch);sessionStarted=true;if(!childStarted)StationDolphinSession.entryVisible(this,true);}
                catch(Exception failure){status.setText("Não foi possível conectar esta partida. Volte à sala para tentar novamente.");}
            });
        }catch(Exception failure){runOnUiThread(()->{if(!isFinishing())status.setText("Esta preparação expirou. Volte à sala e inicie novamente.");});}});
    }
    private void awaitDirectories()throws Exception {
        Class<?> bootstrap=Class.forName("org.emulationstation.frontend.DolphinBootstrap");
        java.lang.reflect.Method ready=Class.forName("org.dolphinemu.dolphinemu.utils.DirectoryInitialization").getMethod("areDolphinDirectoriesReady");
        long limit=android.os.SystemClock.elapsedRealtime()+45000;
        for(;;){
            if(Thread.currentThread().isInterrupted())throw new java.io.InterruptedIOException("DOLPHIN_DIRECTORY_CANCELLED");
            Object error=bootstrap.getField("initializationError").get(null);if(error!=null)throw new java.io.IOException("DOLPHIN_DIRECTORY_FAILED",(Throwable)error);
            if((Boolean)ready.invoke(null))return;
            if(android.os.SystemClock.elapsedRealtime()>=limit)throw new java.io.IOException("DOLPHIN_DIRECTORY_NOT_READY");
            Thread.sleep(100);
        }
    }
    @Override public void startActivityForResult(Intent intent,int request){
        if(request==64){
            if(childStarted)throw new IllegalStateException("DOLPHIN_GAME_ALREADY_LAUNCHED");
            if(intent.getComponent()==null||!"org.dolphinemu.dolphinemu.activities.EmulationActivity".equals(intent.getComponent().getClassName()))throw new IllegalArgumentException("DOLPHIN_GAME_ACTIVITY");
            childStarted=true;
            try{super.startActivityForResult(intent,request);}catch(RuntimeException failure){childStarted=false;throw failure;}return;
        }
        super.startActivityForResult(intent,request);
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(request!=64)return;childStarted=false;
        // An emulator error or native return is not permission to leave the room.
        if(StationDolphinSession.gameReturned(this,result)){
            closing=true;StationDolphinSession.humanClose(this,()->StationDolphinSelector.finishOnlineProcess(this));
        }else if(!isFinishing()){
            status.setText("A partida precisa de atenção. Aguarde a conexão ou saia para criar uma nova sala.");StationDolphinSession.entryVisible(this,true);
        }
    }
    @Override protected void onResume(){super.onResume();if(sessionStarted&&!childStarted&&!closing)StationDolphinSession.entryVisible(this,true);}
    @Override protected void onPause(){if(sessionStarted&&!childStarted&&!closing)StationDolphinSession.entryVisible(this,false);super.onPause();}
    @Override public void onBackPressed(){if(!closing)StationDolphinSession.confirmExit(this);}
    @Override protected void onSaveInstanceState(Bundle saved){saved.putBoolean("childStarted",childStarted);super.onSaveInstanceState(saved);}
    @Override protected void onDestroy(){worker.shutdownNow();super.onDestroy();}
}
