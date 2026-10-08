package org.emulationstation.frontend.netplay;
import android.app.Activity;
import android.content.Intent;
import android.os.*;
import android.util.Log;
import android.widget.TextView;
import java.util.Arrays;
import java.util.concurrent.*;

/** Uses the existing :dolphin Application bootstrap, then the upstream cache and NetPlay UI. */
public final class StationDolphinNetplayActivity extends Activity {
    private static final String CACHE="org.dolphinemu.dolphinemu.services.GameFileCacheManager";
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final ExecutorService worker=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-dolphin-paths");t.setDaemon(true);return t;});
    private final Runnable tick=this::prepare;private TextView status;private long waitStarted;
    private boolean active,scanning,pathsStarted,failed,dispatched;private volatile String[] folders;private volatile Throwable pathError;
    @Override public void onCreate(Bundle state){
        super.onCreate(state);NetplayUi ui=new NetplayUi(this,"Preparando NetPlay");
        status=ui.text("Preparando o Dolphin e conferindo os jogos instalados…",17,0xffc5dacf);
        ui.text("O tempo depende da leitura real dos jogos. A biblioteca e as configurações existentes são preservadas.",14,0xffb9cfc1);ui.action("Voltar",v->finish(),false);
    }
    @Override protected void onStart(){super.onStart();active=true;waitStarted=SystemClock.elapsedRealtime();handler.post(tick);}
    @Override protected void onStop(){active=false;handler.removeCallbacks(tick);super.onStop();}
    @Override protected void onDestroy(){
        handler.removeCallbacksAndMessages(null);worker.shutdownNow();
        if(isFinishing())try{NetplayPaths.deleteSnapshot(getApplicationContext().getFilesDir(),getIntent().getStringExtra("station.netplay.paths"));}catch(java.io.IOException ignored){}
        super.onDestroy();
    }
    private void prepare(){
        if(!active||failed||dispatched||isFinishing())return;
        try{
            Class<?> bootstrap=Class.forName("org.emulationstation.frontend.DolphinBootstrap");
            if(bootstrap.getField("initializationError").get(null)!=null)throw new IllegalStateException("Dolphin process initialization failed");
            Class<?> directory=Class.forName("org.dolphinemu.dolphinemu.utils.DirectoryInitialization");
            boolean ready=(Boolean)directory.getMethod("areDolphinDirectoriesReady").invoke(null);
            if(!ready){if(SystemClock.elapsedRealtime()-waitStarted>45000)throw new IllegalStateException("Directory initialization timed out");handler.postDelayed(tick,150);return;}
            if(!pathsStarted){pathsStarted=true;worker.execute(()->{
                try{String[] paths=NetplayPaths.readSnapshot(getApplicationContext().getFilesDir(),getIntent().getStringExtra("station.netplay.paths"));folders=NetplayPaths.installedFolders(paths);}
                catch(Throwable error){pathError=error;}
            });}
            if(pathError!=null)throw new IllegalStateException("Installed game handoff failed",pathError);
            if(folders==null){handler.postDelayed(tick,150);return;}
            Class<?> manager=Class.forName(CACHE);
            if(!scanning){
                Class<?> cache=Class.forName("org.dolphinemu.dolphinemu.model.GameFileCache");
                String[] original=(String[])cache.getMethod("getIsoPaths").invoke(null);
                String[] merged=NetplayPaths.mergeFolders(original,folders);
                if(!Arrays.equals(original,merged)){
                    cache.getMethod("setIsoPaths",String[].class).invoke(null,(Object)merged);
                    Class.forName("org.dolphinemu.dolphinemu.features.settings.model.NativeConfig").getMethod("save",int.class).invoke(null,1); // Upstream LAYER_BASE.
                }
                manager.getMethod("startLoad").invoke(null);manager.getMethod("startRescan").invoke(null);scanning=true;
                status.setText(folders.length==0?"Conferindo a biblioteca Dolphin. Nenhum jogo de GameCube/Wii instalado pela Station foi encontrado.":"Atualizando a biblioteca Dolphin com os jogos instalados…");
                handler.postDelayed(tick,150);return;
            }
            if((Boolean)manager.getMethod("isLoadingOrRescanning").invoke(null)){handler.postDelayed(tick,150);return;}
            dispatched=true;Intent intent=new Intent();intent.setClassName(this,"org.dolphinemu.dolphinemu.features.netplay.ui.NetplaySetupActivity");startActivity(intent);finish();
        }catch(ReflectiveOperationException|RuntimeException error){
            failed=true;handler.removeCallbacks(tick);Log.e("StationNetplay","Dolphin NetPlay preparation failed: "+error.getClass().getSimpleName());
            status.setText("Não foi possível preparar o NetPlay do Dolphin. Volte e abra as configurações do Dolphin para conferir a inicialização. Seus jogos e saves foram preservados.");
        }
    }
}
