package org.emulationstation.frontend.sony;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.SurfaceTexture;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.hardware.input.InputManager;
import android.net.Uri;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BiConsumer;
import java.util.function.IntConsumer;

/** Internal offline PS4 owner. Every extraction, import and native run stays outside the UI thread. */
public final class Ps4Activity extends Activity implements TextureView.SurfaceTextureListener,InputManager.InputDeviceListener {
    private final ExecutorService worker=Executors.newSingleThreadExecutor(r->new Thread(r,"StationPS4-Owner"));
    private final ExecutorService stopper=Executors.newSingleThreadExecutor(r->new Thread(r,"StationPS4-Stop"));
    private final Object surfaceLock=new Object();
    private final AtomicBoolean stopping=new AtomicBoolean(),started=new AtomicBoolean(),completed=new AtomicBoolean();
    private volatile Surface surface;
    private SurfaceTexture retainedTexture;
    private TextureView display;
    private volatile Class<?> entry;
    private volatile Ps4Control control;
    private volatile Ps4Audio audio;
    private volatile boolean running;
    private volatile String phase="prepare";
    private File session;
    private Uri requested;
    private TextView title,status;
    private LinearLayout notice;
    private FrameLayout layout;
    private Ps4Touch touch;
    private InputManager input;
    private long lastProgress;
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        if(!ApplicationName.expected(this)) {finish();return;}
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        requested=getIntent().getData();
        layout=new FrameLayout(this);layout.setBackgroundColor(Color.BLACK);setContentView(layout);
        display=new TextureView(this);display.setSurfaceTextureListener(this);
        layout.addView(display,new FrameLayout.LayoutParams(-1,-1));
        touch=new Ps4Touch(this,new Ps4Touch.Target() {
            @Override public void snapshot(long buttons,int lx,int ly,int rx,int ry) {
                Ps4Control current=control;if(current!=null)current.touchSnapshot(buttons,lx,ly,rx,ry);
            }
            @Override public void clear() {Ps4Control current=control;if(current!=null)current.clearTouch();}
        });
        touch.setVisibility(View.GONE);layout.addView(touch,new FrameLayout.LayoutParams(-1,-1));
        buildNotice();
        Button exit=new Button(this);exit.setText("Sair");exit.setTextSize(12);exit.setAllCaps(false);
        exit.setOnClickListener(v->confirmExit());
        FrameLayout.LayoutParams corner=new FrameLayout.LayoutParams(dp(66),dp(40),Gravity.TOP|Gravity.RIGHT);
        corner.setMargins(0,dp(8),dp(8),0);layout.addView(exit,corner);
        input=(InputManager)getSystemService(INPUT_SERVICE);input.registerInputDeviceListener(this,new Handler(Looper.getMainLooper()));
        if(started.compareAndSet(false,true))worker.execute(this::prepareAndRun);
    }
    private void buildNotice() {
        notice=new LinearLayout(this);notice.setOrientation(LinearLayout.VERTICAL);notice.setPadding(dp(28),dp(22),dp(28),dp(22));
        GradientDrawable background=new GradientDrawable();background.setColor(0xee0e1623);background.setCornerRadius(dp(18));notice.setBackground(background);
        title=new TextView(this);title.setText("PlayStation 4");title.setTextColor(Color.WHITE);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);title.setTextSize(23);
        status=new TextView(this);status.setText("Preparando o motor…");status.setTextColor(0xffb6c9df);status.setTextSize(15);status.setPadding(0,dp(12),0,0);
        notice.addView(title);notice.addView(status);
        FrameLayout.LayoutParams place=new FrameLayout.LayoutParams(dp(400),-2,Gravity.CENTER);layout.addView(notice,place);
    }
    private void prepareAndRun() {
        try {
            if(Build.VERSION.SDK_INT<31)throw new IOException("O motor PS4 requer Android 12 ou mais recente");
            StationSonyAssets.Prepared assets=StationSonyAssets.prepare(this,"ps4",StationSonyAssetPins.PS4_MANIFEST_SHA256,
                (path,done,total)->progress("Preparando o motor",done,total));
            checkStopped();
            File owner=assets.assetFile("derived/owner.dex");
            if(!owner.setReadOnly())throw new IOException("Não foi possível proteger o motor PS4");
            File optimized=directory(new File(getCodeCacheDir(),"ps4-owner"));
            Ps4ClassLoader loader=new Ps4ClassLoader(owner.getAbsolutePath(),optimized.getAbsolutePath(),
                assets.nativeDirectory().getAbsolutePath(),getClassLoader());
            Class<?> preparedEntry=loader.loadClass("org.emulationstation.ps4child.Ps4NativeEntry");
            LinkedHashSet<String> nativePaths=new LinkedHashSet<>();
            for(String name:new String[]{"libbachata_native_runtime.so","libbachata_pkg.so"})
                for(File file:StationSonyAssets.nativeLoadPlan(assets,name))nativePaths.add(file.getCanonicalPath());
            Ps4Game.invoke(preparedEntry,"loadNative",new Class<?>[]{String[].class,String.class},
                nativePaths.toArray(new String[0]),assets.assetFile("derived/pkg-rsa.bin").getCanonicalPath());
            // Publish only after JNI registration and private material initialization.
            // A concurrent human cancel cannot call unregistered native methods.
            entry=preparedEntry;
            checkStopped();
            Ps4Runtime.prepare(assets,directory(new File(getNoBackupFilesDir(),"ps4-runtime")));
            File base=directory(new File(getFilesDir(),"ps4"));
            File cwd=directory(new File(base,"native-runtime")),storage=directory(new File(base,"storage"));
            directory(new File(storage,"xdg"));directory(new File(storage,"shader-cache/mesa"));
            if(requested==null) {
                phase="settings";completed.set(true);
                show("PlayStation 4","Motor e arquivos internos preparados. Escolha um jogo na lista para jogar.");return;
            }
            phase="import";show("PlayStation 4","Preparando o jogo…");
            Ps4Game game=Ps4Game.prepare(this,requested,directory(new File(base,"games")),entry,
                (done,total)->progress("Preparando o jogo",done,total));
            checkStopped();
            session=directory(new File(storage,"s/"+UUID.randomUUID().toString().replace("-","").substring(0,10)));
            File inputPath=new File(session,"c"),audioPath=new File(session,"a");
            control=new Ps4Control(inputPath,this::nativeEvent);audio=new Ps4Audio(audioPath,message->{if(running)warning(message);});
            String[] arguments={"libbachata_native_runtime.so","--override-root",game.root.getCanonicalPath(),
                "--bachata-storage-root",storage.getCanonicalPath(),"--bachata-socket",inputPath.getCanonicalPath()};
            String[] environment={"HOME="+storage.getCanonicalPath(),"TMPDIR="+session.getCanonicalPath(),
                "XDG_CACHE_HOME="+new File(storage,"xdg").getCanonicalPath(),
                "MESA_SHADER_CACHE_DIR="+new File(storage,"shader-cache/mesa").getCanonicalPath(),
                "BACHATA_ALSA_SOCKET="+audioPath.getCanonicalPath()};
            Surface target;
            synchronized(surfaceLock) {
                while(!stopping.get()&&(surface==null||!surface.isValid()))surfaceLock.wait();
                checkStopped();target=surface;
            }
            show(game.title,"Iniciando o jogo…");phase="game";running=true;
            runOnUiThread(this::updatePhysical);
            Object result=Ps4Game.invoke(entry,"run",new Class<?>[]{Surface.class,String[].class,String[].class,String.class,IntConsumer.class},
                target,arguments,environment,cwd.getCanonicalPath(),(IntConsumer)code->{});
            running=false;completed.set(true);
            if(stopping.get())finishOwner();
            else show(game.title,((Integer)result)==0?"Partida encerrada.":"O motor não conseguiu iniciar ou manter este jogo.");
        } catch(InterruptedException cancelled) {
            Thread.currentThread().interrupt();completed.set(true);finishOwner();
        } catch(Throwable failure) {
            completed.set(true);running=false;
            if(stopping.get())finishOwner();else {
                String message=failure instanceof IOException?failure.getMessage():"Não foi possível iniciar o motor PS4 interno.";
                show("PlayStation 4",message==null?"O jogo não pôde ser preparado.":message);
                android.util.Log.e("StationPS4Owner","Internal owner failed in "+phase+": "+failure.getClass().getSimpleName());
            }
        } finally {closeSession();}
    }
    private void progress(String message,long done,long total) {
        long now=SystemClock.elapsedRealtime();if(now-lastProgress<250&&done!=total)return;lastProgress=now;
        show("PlayStation 4",message+(total>0?" · "+Math.min(100,(100*done)/total)+"%":"…"));
    }
    private void nativeEvent(String event) {
        if("BACHATA/1 EVENT Frame".equals(event)||"BACHATA/1 EVENT Running".equals(event)) {
            if("BACHATA/1 EVENT Running".equals(event))runOnUiThread(()->{notice.setVisibility(View.GONE);updatePhysical();});
        } else if(event.startsWith("BACHATA/1 ERROR code="))warning("O motor PS4 informou uma falha de execução.");
    }
    private void warning(String message) {runOnUiThread(()->{if(!isFinishing())Toast.makeText(this,message,Toast.LENGTH_SHORT).show();});}
    private void show(String heading,String message) {
        runOnUiThread(()->{if(!isFinishing()){title.setText(heading);status.setText(message);notice.setVisibility(View.VISIBLE);}});
    }
    private void checkStopped() throws InterruptedException {if(stopping.get())throw new InterruptedException("Owner stopped");}
    private static File directory(File file) throws IOException {if(!file.isDirectory()&&!file.mkdirs())throw new IOException("Sem espaço para preparar PS4");return file.getCanonicalFile();}
    private int dp(int value) {return Math.round(value*getResources().getDisplayMetrics().density);}
    private void confirmExit() {
        if(!running&&completed.get()){finishOwner();return;}
        new AlertDialog.Builder(this).setTitle("Sair do PS4?").setMessage("Encerrar esta partida e voltar à lista de jogos?")
            .setNegativeButton("Continuar",null).setPositiveButton("Sair",(dialog,which)->stopOwner()).show();
    }
    private void stopOwner() {
        if(!stopping.compareAndSet(false,true))return;
        if(touch!=null)touch.clear();Ps4Control current=control;if(current!=null)current.neutral();
        synchronized(surfaceLock){surfaceLock.notifyAll();}
        show("PlayStation 4","Encerrando…");
        if(completed.get()){finishOwner();return;}
        stopper.execute(()-> {
            Class<?> currentEntry=entry;if(currentEntry==null)return;
            try {Ps4Game.invoke(currentEntry,"cancelImport",new Class<?>[0]);}catch(Exception ignored){}
            try {Ps4Game.invoke(currentEntry,"stop",new Class<?>[0]);}catch(Exception ignored){}
        });
    }
    private void closeSession() {
        Ps4Control pad=control;control=null;if(pad!=null)try{pad.close();}catch(IOException ignored){}
        Ps4Audio sound=audio;audio=null;if(sound!=null)try{sound.close();}catch(IOException ignored){}
        if(session!=null)session.delete();
        runOnUiThread(()->{
            if(touch!=null){touch.clear();touch.setVisibility(View.GONE);}
            if(display!=null)display.setVisibility(View.GONE);
            // Native run has returned before this method is called: release only our retained pair.
            synchronized(surfaceLock){if(surface!=null){surface.release();surface=null;}}
            if(retainedTexture!=null){retainedTexture.release();retainedTexture=null;}
        });
    }
    private void finishOwner() {
        runOnUiThread(()-> {
            finish();
            // Native libraries cannot be unloaded/reassigned to a new loader in the same process.
            new Handler(Looper.getMainLooper()).postDelayed(()->{if(ApplicationName.expected(this))android.os.Process.killProcess(android.os.Process.myPid());},200);
        });
    }
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        warning(running?"A partida atual continua aberta. Saia dela para trocar de jogo.":"O PS4 já está aberto. Volte à lista para escolher o jogo.");
    }
    @Override public void onBackPressed() {confirmExit();}
    @Override public boolean dispatchKeyEvent(KeyEvent event) {Ps4Control pad=control;if(pad!=null&&pad.key(event))return true;return super.dispatchKeyEvent(event);}
    @Override public boolean dispatchGenericMotionEvent(MotionEvent event) {Ps4Control pad=control;if(pad!=null&&pad.motion(event))return true;return super.dispatchGenericMotionEvent(event);}
    @Override public void onSurfaceTextureAvailable(SurfaceTexture texture,int width,int height) {
        if(completed.get())return;
        if(retainedTexture==null)retainedTexture=texture;
        else if(retainedTexture!=texture)display.setSurfaceTexture(retainedTexture);
        synchronized(surfaceLock){if(surface==null)surface=new Surface(retainedTexture);surfaceLock.notifyAll();}
    }
    @Override public void onSurfaceTextureSizeChanged(SurfaceTexture texture,int width,int height) { }
    @Override public boolean onSurfaceTextureDestroyed(SurfaceTexture texture) {
        // Bridge 0.2.4 has no pause/rebind API. Keep the same producer surface on detach;
        // TextureView reuses it on return, without fabricating an SDL pause or ending the game.
        return completed.get()||retainedTexture!=texture;
    }
    @Override public void onSurfaceTextureUpdated(SurfaceTexture texture) { }
    @Override protected void onPause() {super.onPause();if(touch!=null)touch.clear();Ps4Control pad=control;if(pad!=null)pad.neutral();}
    @Override public void onConfigurationChanged(Configuration config) {super.onConfigurationChanged(config);updatePhysical();}
    private void updatePhysical() {
        boolean connected=false;for(int id:InputDevice.getDeviceIds()){InputDevice device=InputDevice.getDevice(id);if(device!=null&&Ps4Control.gamepad(device.getSources())){connected=true;break;}}
        if(touch!=null){if(connected)touch.clear();touch.setVisibility(running&&!connected?View.VISIBLE:View.GONE);}
    }
    @Override public void onInputDeviceAdded(int deviceId) {updatePhysical();}
    @Override public void onInputDeviceChanged(int deviceId) {updatePhysical();}
    @Override public void onInputDeviceRemoved(int deviceId) {Ps4Control pad=control;if(pad!=null)pad.removed(deviceId);updatePhysical();}
    @Override protected void onDestroy() {
        if(input!=null)input.unregisterInputDeviceListener(this);
        // A lifecycle callback is not a user request to terminate the native game.
        worker.shutdown();stopper.shutdown();super.onDestroy();
    }
    private static final class ApplicationName {
        static boolean expected(Activity context) {return (context.getPackageName()+":station_ps4").equals(android.app.Application.getProcessName());}
    }
}
