package org.emulationstation.frontend.netplay;

import android.app.*;
import android.content.*;
import android.os.*;
import android.view.Gravity;
import android.widget.*;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.*;

/** Main-process result anchor. Dolphin renders and reads input in :dolphin. */
public final class StationDolphinActivity extends Activity {
    private static final int CHILD=64;
    private final ExecutorService worker=Executors.newSingleThreadExecutor();
    private final Handler main=new Handler(Looper.getMainLooper());
    private String launchName;private boolean childStarted,waitingRestart,cancelled;private int restarts,restartPid;
    private TextView status;
    @Override protected void onCreate(Bundle saved){
        super.onCreate(saved);launchName=getIntent().getStringExtra("station.launch");
        getWindow().setBackgroundDrawableResource(android.R.color.black);
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setGravity(Gravity.CENTER);panel.setPadding(32,24,32,24);panel.setBackgroundColor(0xff080d17);
        status=new TextView(this);status.setText("Preparando a partida…");status.setTextColor(0xffeaf2ff);status.setTextSize(17);status.setGravity(Gravity.CENTER);panel.addView(status);
        Button cancel=new Button(this);cancel.setText("Voltar");cancel.setOnClickListener(v->onBackPressed());panel.addView(cancel);setContentView(panel);
        if(saved!=null){childStarted=saved.getBoolean("childStarted");waitingRestart=saved.getBoolean("waitingRestart");restarts=saved.getInt("restarts");restartPid=saved.getInt("restartPid");}
        if(waitingRestart)waitForIdleRestart();else if(!childStarted)launchChild();
    }
    private void launchChild(){
        worker.execute(()->{try{
            if(Thread.currentThread().isInterrupted())return;
            StationDolphinLaunch.peek(this,launchName);StationDolphinLaunch.publishPending(this,launchName);
            runOnUiThread(()->{
                if(cancelled||isFinishing()||isDestroyed())return;
                Intent child=new Intent(this,StationDolphinOnlineActivity.class);child.putExtras(getIntent());child.putExtra(StationDolphinSelector.EXTRA,launchName);
                try{childStarted=true;startActivityForResult(child,CHILD);}
                catch(RuntimeException failure){childStarted=false;failed();}
            });
        }catch(Exception failure){runOnUiThread(this::failed);}});
    }
    private void waitForIdleRestart(){
        worker.execute(()->{try{
            // The idle child sends its own PID before finishing. An elapsed
            // delay alone does not prove the old Dolphin globals were released.
            Thread.sleep(800);long limit=SystemClock.elapsedRealtime()+10000;
            while(alive(restartPid)){
                if(cancelled||Thread.currentThread().isInterrupted())return;
                if(SystemClock.elapsedRealtime()>=limit)throw new IOException("DOLPHIN_IDLE_PROCESS_NOT_RELEASED");
                Thread.sleep(100);
            }
            StationDolphinLaunch.peek(this,launchName);
            runOnUiThread(()->{if(cancelled||isFinishing()||isDestroyed())return;waitingRestart=false;launchChild();});
        }catch(Exception failure){runOnUiThread(this::failed);}});
    }
    private boolean alive(int pid)throws IOException {
        if(pid<=0||pid==android.os.Process.myPid())throw new IOException("DOLPHIN_IDLE_PROCESS_ID");
        ActivityManager manager=(ActivityManager)getSystemService(ACTIVITY_SERVICE);
        List<ActivityManager.RunningAppProcessInfo> processes=manager==null?null:manager.getRunningAppProcesses();
        if(processes==null)throw new IOException("DOLPHIN_PROCESS_STATE_UNAVAILABLE");
        for(ActivityManager.RunningAppProcessInfo process:processes)if(process.pid==pid){
            if(!(getPackageName()+":dolphin").equals(process.processName))throw new IOException("DOLPHIN_PROCESS_IDENTITY");return true;
        }
        return false;
    }
    private void failed(){
        if(cancelled||isFinishing()||isDestroyed())return;
        waitingRestart=false;childStarted=false;StationDolphinLaunch.discard(this,launchName);
        status.setText("Não foi possível preparar esta partida. Volte à sala e tente novamente.");
        // Preparation failure is not a human leave command and does not kill a
        // process or clear the authenticated room automatically.
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(request!=CHILD)return;childStarted=false;
        if(result==StationDolphinSelector.RESTART_IDLE_PROCESS){
            if(restarts++!=0){failed();return;}restartPid=data==null?0:data.getIntExtra("station.dolphin.pid",0);waitingRestart=true;waitForIdleRestart();return;
        }
        setResult(result,data);finish();
    }
    @Override public void onBackPressed(){
        if(cancelled||isFinishing())return;
        new AlertDialog.Builder(this).setTitle("Sair da preparação?").setMessage("Você voltará à sala.")
            .setNegativeButton("Continuar",null).setPositiveButton("Sair",(dialog,which)->{
                cancelled=true;worker.shutdownNow();main.removeCallbacksAndMessages(null);StationDolphinLaunch.discard(this,launchName);
                ResultReceiver events=StationSessionChannel.read(getIntent().getExtras(),StationGameSession.EXTRA);
                if(events!=null)events.send(4,null);setResult(RESULT_CANCELED);finish();
            }).show();
    }
    @Override protected void onSaveInstanceState(Bundle saved){saved.putBoolean("childStarted",childStarted);saved.putBoolean("waitingRestart",waitingRestart);saved.putInt("restarts",restarts);saved.putInt("restartPid",restartPid);super.onSaveInstanceState(saved);}
    @Override protected void onDestroy(){worker.shutdownNow();main.removeCallbacksAndMessages(null);if(isFinishing()&&!childStarted)StationDolphinLaunch.discard(this,launchName);super.onDestroy();}
}
