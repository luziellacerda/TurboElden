package org.emulationstation.frontend.station;

import android.app.*;
import android.content.*;
import android.graphics.Color;
import android.net.Uri;
import android.os.*;
import android.provider.Settings;
import android.view.*;
import android.widget.*;

/** Private, user-initiated update screen; no password, browser or public APK URL. */
public final class StationAppUpdateActivity extends Activity {
    private TextView heading,description,status;
    private ProgressBar progress;
    private Button action;
    private boolean autoStart,askedPermission;
    private final Runnable refresh=this::render;
    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);if(getActionBar()!=null)getActionBar().hide();
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        LinearLayout column=new LinearLayout(this);column.setOrientation(LinearLayout.VERTICAL);column.setPadding(40,30,40,30);column.setBackgroundColor(Color.rgb(12,23,40));
        heading=label("Atualizar TurboStation",25);description=label("",16);status=label("",17);
        column.addView(heading);ScrollView notes=new ScrollView(this);notes.addView(description);column.addView(notes,new LinearLayout.LayoutParams(-1,0,1));column.addView(status);
        progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);progress.setMax(100);column.addView(progress);
        action=new Button(this);action.setOnClickListener(v->{
            if(StationAppUpdater.confirmationPending())StationAppUpdater.launchConfirmation();
            else if(StationAppUpdater.busy)StationAppUpdater.cancel();
            else if(StationAppUpdater.offer!=null){autoStart=true;askedPermission=false;proceed();}
            else StationAppUpdater.check(this::render);
        });column.addView(action);
        Button close=new Button(this);close.setText("Voltar");close.setOnClickListener(v->finish());column.addView(close);setContentView(column);
        try{StationAndroid.get(this);}
        catch(Exception unavailable){status.setText("Não foi possível preparar a atualização.");action.setEnabled(false);return;}
        autoStart=saved!=null?saved.getBoolean("start",false):getIntent().getBooleanExtra("start",false);
        askedPermission=saved!=null&&saved.getBoolean("permissionAsked",false);
        if(StationAppUpdater.offer==null)StationAppUpdater.check(()->{render();proceed();});
    }
    private TextView label(String value,int size){TextView view=new TextView(this);view.setText(value);view.setTextSize(size);view.setTextColor(Color.WHITE);view.setPadding(0,12,0,12);return view;}
    @Override protected void onResume(){super.onResume();StationAppUpdater.observe(refresh);StationAppUpdater.screen(this);render();proceed();}
    @Override protected void onPause(){StationAppUpdater.releaseScreen(this);StationAppUpdater.forget(refresh);super.onPause();}
    @Override public void onWindowFocusChanged(boolean focused){super.onWindowFocusChanged(focused);if(focused)StationAppUpdater.launchConfirmation();}
    @Override protected void onSaveInstanceState(Bundle out){out.putBoolean("start",autoStart);out.putBoolean("permissionAsked",askedPermission);super.onSaveInstanceState(out);}
    private void proceed(){
        if(!autoStart||StationAppUpdater.offer==null||StationAppUpdater.busy)return;
        if(Build.VERSION.SDK_INT>=26&&!getPackageManager().canRequestPackageInstalls()){
            status.setText("Permita que o TurboStation instale a atualização. Depois, volte a esta tela.");
            if(!askedPermission){
                askedPermission=true;
                try{startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+getPackageName())));}
                catch(RuntimeException restricted){autoStart=false;status.setText("Este aparelho não permitiu abrir a autorização de atualização. Confira as configurações do Android.");}
            }
            return;
        }
        autoStart=false;StationAppUpdater.begin(this);render();
    }
    private void render(){
        if(status==null)return;StationAppRelease release=StationAppUpdater.offer;
        description.setText(release==null?"As atualizações são obtidas do servidor protegido.":
            "Versão "+release.versionName+"\n\n"+release.notes+"\n\nA atualização preserva seus jogos, acesso e configurações. O aplicativo será reiniciado pelo Android.");
        long total=StationAppUpdater.total,received=StationAppUpdater.received;
        status.setText(StationAppUpdater.message+(StationAppUpdater.busy&&!StationAppUpdater.installing&&total>0?
            "\n"+Math.min(100,received*100/total)+"% · "+(received/1048576)+" / "+(total/1048576)+" MB":""));
        progress.setIndeterminate(StationAppUpdater.busy&&total<=0);
        progress.setProgress(total>0?(int)Math.min(100,received*100/total):0);
        action.setEnabled(!StationAppUpdater.checking&&(!StationAppUpdater.installing||StationAppUpdater.confirmationPending()));
        action.setText(StationAppUpdater.confirmationPending()?"Concluir atualização":StationAppUpdater.installing?"Aguardando Android…":StationAppUpdater.busy?"Cancelar download":release!=null?"Atualizar agora":"Verificar novamente");
    }
}
