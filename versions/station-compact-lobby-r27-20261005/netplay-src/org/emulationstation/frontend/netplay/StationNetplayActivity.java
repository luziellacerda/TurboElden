package org.emulationstation.frontend.netplay;
import android.app.Activity;
import android.content.Intent;
import android.os.*;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;
import java.io.File;
import java.lang.reflect.Method;
import java.util.*;
import java.util.concurrent.*;

/** Opens real emulator networking interfaces. This screen creates no Station lobby. */
public final class StationNetplayActivity extends Activity {
    private final ExecutorService worker=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-netplay-paths");t.setDaemon(true);return t;});
    private TextView status;private Button dolphin,psp,flycast;private boolean busy,visible;
    private File readySnapshot;private Throwable preparationError;
    private static boolean start(Activity activity,String itemId){
        if(activity.isFinishing()||activity.isDestroyed())return false;
        try{activity.startActivity(new Intent(activity,itemId==null?StationNetplayActivity.class:StationRoomsActivity.class).putExtra("station.itemId",itemId));return true;}
        catch(RuntimeException error){Log.e("StationNetplay","Networking menu dispatch failed: "+error.getClass().getSimpleName());return false;}
    }
    /** Returns success only after Android accepted startActivity, even from the SDL thread. */
    public static boolean launch(Activity activity){return launchGame(activity,null);}
    public static boolean launchGame(Activity activity,String itemId){
        if(activity==null||activity.isFinishing())return false;
        if(Looper.myLooper()==Looper.getMainLooper())return start(activity,itemId);
        final Object gate=new Object();final int[] result={0}; // pending/success/failure/cancelled
        synchronized(gate){
            new Handler(Looper.getMainLooper()).post(()->{synchronized(gate){if(result[0]!=0)return;result[0]=start(activity,itemId)?1:2;gate.notifyAll();}});
            long deadline=SystemClock.elapsedRealtime()+5000;
            while(result[0]==0){long remaining=deadline-SystemClock.elapsedRealtime();if(remaining<=0){result[0]=3;break;}try{gate.wait(remaining);}catch(InterruptedException e){result[0]=3;Thread.currentThread().interrupt();break;}}
            return result[0]==1;
        }
    }
    @Override public void onCreate(Bundle state){
        super.onCreate(state);NetplayUi ui=new NetplayUi(this,"Jogar em rede");
        ui.text("Use um jogo instalado e compatível. Cada participante precisa do mesmo jogo e de uma versão compatível do emulador.",15,0xffc5dacf);
        ui.action("Salas TurboStations • jogadores e convites",v->startActivity(new Intent(this,StationRoomsActivity.class)),true);
        ui.text("Mega Drive e Super Nintendo",17,0xff7ef2a0);
        ui.text("Abra um jogo e toque em Jogar online para conferir a disponibilidade do motor nas salas. A partida é direta entre aparelhos. Seus controles e saves locais são preservados.",14,0xffdec7b8);
        ui.text("Plataformas com opções de rede",17,0xffedf8f0);
        psp=ui.action("PSP • configurar multiplayer",v->openEngine("PspBootstrap"),true);
        ui.text("Em Configurações → Rede, ative WLAN e use o servidor ad hoc no aparelho anfitrião. A sala é aberta dentro do jogo. Não há relay público configurado pela Station.",14,0xffb9cfc1);
        dolphin=ui.action("GameCube / Wii • criar ou entrar em sala",v->openDolphin(),true);
        ui.text("Abre o NetPlay original do Dolphin e inclui os jogos instalados pela Station. Use Wi-Fi e a mesma versão do jogo. Alguns títulos e aparelhos podem perder sincronização.",14,0xffb9cfc1);
        flycast=ui.action("Dreamcast / Naomi • configurar rede",v->openEngine("FlycastBootstrap"),true);
        ui.text("Em Configurações → Rede, escolha GGPO para títulos compatíveis e informe o outro jogador. Native/DCNet usa as funções online próprias dos jogos Dreamcast; Naomi e Battle Cable têm opções específicas.",14,0xffb9cfc1);
        status=ui.text("Conexões e salas são gerenciadas pelo emulador selecionado.",14,0xff7ef2a0);ui.action("Voltar às plataformas",v->finish(),false);
    }
    private void setBusy(boolean value,String message){busy=value;psp.setEnabled(!value);dolphin.setEnabled(!value);flycast.setEnabled(!value);status.setText(message);}
    @Override protected void onStart(){super.onStart();visible=true;deliverPreparedSnapshot();}
    @Override protected void onStop(){visible=false;super.onStop();}
    private void deliverPreparedSnapshot(){
        if(!visible||isFinishing()||isDestroyed())return;
        if(preparationError!=null){Throwable error=preparationError;preparationError=null;showFailure(error);return;}
        File handoff=readySnapshot;if(handoff==null)return;readySnapshot=null;
        try{Intent intent=new Intent(this,StationDolphinNetplayActivity.class);intent.putExtra("station.netplay.paths",handoff.getName());startActivity(intent);finish();}
        catch(RuntimeException error){handoff.delete();showFailure(error);}
    }
    private void openEngine(String simpleName){
        if(busy)return;
        try{
            Class<?> bridge=Class.forName("org.emulationstation.frontend."+simpleName);
            boolean accepted=(Boolean)bridge.getMethod("launch",Activity.class,String.class,boolean.class).invoke(null,this,"",true);
            if(!accepted)throw new IllegalStateException("Engine launch declined");finish();
        }catch(ReflectiveOperationException|RuntimeException error){showFailure(error);}
    }
    private void openDolphin(){
        if(busy)return;setBusy(true,"Conferindo os jogos instalados de GameCube e Wii…");
        worker.execute(()->{
            File snapshot=null;
            try{
                Class<?> frontend=Class.forName("org.emulationstation.frontend.station.StationFrontend");
                Method installed=frontend.getMethod("installedPathsFor",String.class);
                LinkedHashSet<String> paths=new LinkedHashSet<>();Collections.addAll(paths,(String[])installed.invoke(null,"gamecube"));Collections.addAll(paths,(String[])installed.invoke(null,"wii"));
                if(Thread.currentThread().isInterrupted())throw new java.io.InterruptedIOException("Preparation cancelled");
                snapshot=NetplayPaths.writeSnapshot(getApplicationContext().getFilesDir(),paths.toArray(new String[0]));final File handoff=snapshot;
                runOnUiThread(()->{
                    if(isFinishing()||isDestroyed()){handoff.delete();return;}
                    readySnapshot=handoff;deliverPreparedSnapshot();
                });
            }catch(ReflectiveOperationException|java.io.IOException|RuntimeException error){if(snapshot!=null)snapshot.delete();runOnUiThread(()->{if(!isFinishing()&&!isDestroyed()){preparationError=error;deliverPreparedSnapshot();}});}
        });
    }
    private void showFailure(Throwable error){Log.e("StationNetplay","Networking entry failed: "+error.getClass().getSimpleName());setBusy(false,"Não foi possível preparar esta opção. Volte às plataformas, aguarde o catálogo carregar e tente novamente. Seus jogos e saves foram preservados.");}
    @Override protected void onDestroy(){worker.shutdownNow();if(readySnapshot!=null){readySnapshot.delete();readySnapshot=null;}super.onDestroy();}
}
