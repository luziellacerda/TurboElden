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
import android.util.AtomicFile;
import org.json.JSONObject;
import org.json.JSONException;
import java.nio.charset.StandardCharsets;
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
    private boolean settingsMode;
    private boolean settingsLeaving;
    private boolean settingsSaving;
    private int settingsCategory,settingsEpoch;
    private File settingsConfig;
    private LinearLayout settingsBody;
    private TextView settingsMessage;
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        if(!ApplicationName.expected(this)) {finish();return;}
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        requested=getIntent().getData();
        settingsMode="settings".equals(getIntent().getStringExtra("operation"))||requested==null;
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
        Button exit=new Button(this);exit.setText(settingsMode?"Voltar":"Sair");exit.setTextSize(12);exit.setAllCaps(false);
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
            File base=directory(new File(getFilesDir(),"ps4"));
            File cwd=directory(new File(base,"native-runtime")),storage=directory(new File(base,"storage"));
            directory(new File(storage,"xdg"));directory(new File(storage,"shader-cache/mesa"));
            File dataHome=directory(new File(storage,".local/share"));
            settingsConfig=new File(new File(dataHome,"shadPS4"),"config.json");
            // The native UserPaths table is initialized at dlopen. Bind the same private HOME
            // used by run before loading it, as the official config writer/native consumer require.
            android.system.Os.setenv("HOME",storage.getCanonicalPath(),true);
            android.system.Os.setenv("XDG_DATA_HOME",dataHome.getCanonicalPath(),true);
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
            if(settingsMode) {
                phase="settings";completed.set(true);
                runOnUiThread(this::showSettings);return;
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
                android.util.Log.e("StationPS4Owner","Internal owner failed in "+phase,failure);
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
        if(settingsMode) {
            if(completed.get())leaveSettings();else stopOwner();
            return;
        }
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
        if(touch!=null){if(connected)touch.clear();touch.setVisibility(running&&!connected&&getPreferences(MODE_PRIVATE).getBoolean("touch",true)?View.VISIBLE:View.GONE);}
    }
    @Override public void onInputDeviceAdded(int deviceId) {updatePhysical();}
    @Override public void onInputDeviceChanged(int deviceId) {updatePhysical();}
    @Override public void onInputDeviceRemoved(int deviceId) {Ps4Control pad=control;if(pad!=null)pad.removed(deviceId);updatePhysical();}
    @Override protected void onDestroy() {
        settingsLeaving=true;++settingsEpoch;
        if(input!=null)input.unregisterInputDeviceListener(this);
        // A lifecycle callback is not a user request to terminate the native game.
        worker.shutdown();stopper.shutdown();super.onDestroy();
    }
    private GradientDrawable settingsBackground(int color) {
        GradientDrawable bg=new GradientDrawable();bg.setColor(color);bg.setCornerRadius(dp(7));return bg;
    }
    private Button settingsButton(String label) {
        Button b=new Button(this);b.setText(label);b.setAllCaps(false);b.setTextSize(13);b.setTextColor(0xffe9eef9);
        b.setMinHeight(0);b.setMinimumHeight(0);b.setPadding(dp(12),0,dp(12),0);
        b.setBackground(settingsBackground(0xff182632));return b;
    }
    private TextView settingsText(String text,int size) {
        TextView v=new TextView(this);v.setText(text);v.setTextSize(size);v.setTextColor(0xffe9eef9);return v;
    }
    private boolean settingsActive() {
        return !settingsLeaving&&!stopping.get()&&!isFinishing()&&!isDestroyed()&&!worker.isShutdown();
    }
    private void showSettings() {
        if(!settingsActive())return;
        layout.removeAllViews();layout.setBackgroundColor(0xff081017);
        LinearLayout page=new LinearLayout(this);page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(dp(16),dp(10),dp(16),dp(10));layout.addView(page,new FrameLayout.LayoutParams(-1,-1));
        LinearLayout heading=new LinearLayout(this);heading.setGravity(Gravity.CENTER_VERTICAL);
        Button back=settingsButton("‹  Voltar");back.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        back.setOnClickListener(v->leaveSettings());heading.addView(back,new LinearLayout.LayoutParams(dp(94),dp(38)));
        TextView title=settingsText("PS4  /  Configurações",19);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        title.setPadding(dp(14),0,0,0);heading.addView(title,new LinearLayout.LayoutParams(0,-2,1));
        page.addView(heading,new LinearLayout.LayoutParams(-1,dp(44)));
        settingsMessage=settingsText("Opções do motor · alterações valem no próximo jogo",12);
        settingsMessage.setTextColor(0xff93a8ba);settingsMessage.setPadding(0,dp(3),0,dp(10));page.addView(settingsMessage);
        LinearLayout main=new LinearLayout(this);page.addView(main,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout tabs=new LinearLayout(this);tabs.setOrientation(LinearLayout.VERTICAL);
        main.addView(tabs,new LinearLayout.LayoutParams(dp(140),-1));
        String[] labels={"Imagem","Desempenho","Sistema","Áudio"};
        for(int i=0;i<labels.length;i++) {
            final int group=i;Button b=settingsButton(labels[i]);b.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);
            b.setTypeface(Typeface.DEFAULT,Typeface.BOLD);b.setOnClickListener(v->selectSettingsCategory(group));
            LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(-1,dp(39));size.setMargins(0,0,dp(12),dp(7));tabs.addView(b,size);
        }
        ScrollView scroll=new ScrollView(this);scroll.setVerticalScrollBarEnabled(false);main.addView(scroll,new LinearLayout.LayoutParams(0,-1,1));
        settingsBody=new LinearLayout(this);settingsBody.setOrientation(LinearLayout.VERTICAL);scroll.addView(settingsBody,new ScrollView.LayoutParams(-1,-2));
        selectSettingsCategory(settingsCategory);
    }
    private static final class Setting {
        final int group,kind;final String section,key,label;final Object documentedDefault;final String[] choices;
        Setting(int group,int kind,String section,String key,String label,Object documentedDefault,String...choices) {
            this.group=group;this.kind=kind;this.section=section;this.key=key;this.label=label;
            this.documentedDefault=documentedDefault;this.choices=choices;
        }
    }
    // Exact runtime-settings/shadps4.json keys/types/defaults from official 0.2.4.
    // Unknown/unbounded/backend/driver fields are never given invented writable controls.
    private static final Setting[] SETTINGS={
        new Setting(0,2,"GPU","display_mode","Enquadramento", "Fit","Fit","Stretch","Crop"),
        new Setting(0,1,"GPU","present_rb_swap","Corrigir canais de cor",Boolean.FALSE),
        new Setting(0,1,"GPU","hdr_allowed","Permitir HDR",Boolean.FALSE),
        new Setting(0,1,"GPU","fsr_enabled","Filtro FSR",Boolean.FALSE),
        new Setting(0,1,"GPU","rcas_enabled","Nitidez RCAS",Boolean.TRUE),
        new Setting(0,2,"GPU","present_mode","Apresentação dos quadros","Mailbox","Immediate","Mailbox","Fifo","FifoRelaxed"),
        new Setting(1,1,"General","big_core_affinity","Priorizar núcleos de alto desempenho",Boolean.FALSE),
        new Setting(1,1,"Vulkan","pipeline_cache_enabled","Cache de pipelines",Boolean.FALSE),
        new Setting(1,0,"GPU","vblank_frequency","Frequência VBlank",Integer.valueOf(60)),
        new Setting(2,0,"General","console_language","Idioma do sistema",Integer.valueOf(1)),
        new Setting(3,0,"Audio","audio_backend","Backend de áudio",null)
    };
    private JSONObject readNativeConfig() throws IOException,JSONException {
        if(settingsConfig==null)throw new IOException("Configuração PS4 indisponível");
        if(!settingsConfig.exists())return new JSONObject();
        if(!settingsConfig.isFile()||settingsConfig.length()>512*1024)throw new IOException("Arquivo de configuração PS4 inválido");
        try(InputStream input=new FileInputStream(settingsConfig);ByteArrayOutputStream output=new ByteArrayOutputStream()) {
            byte[] chunk=new byte[8192];int count;
            while((count=input.read(chunk))!=-1){if(output.size()+count>512*1024)throw new IOException("Configuração PS4 muito grande");output.write(chunk,0,count);}
            return new JSONObject(new String(output.toByteArray(),StandardCharsets.UTF_8));
        }
    }
    private Object currentSetting(JSONObject config,Setting setting) {
        JSONObject section=config.optJSONObject(setting.section);
        if(section!=null&&section.has(setting.key))return section.opt(setting.key);
        return setting.documentedDefault;
    }
    private void selectSettingsCategory(int group) {
        if(!settingsActive()||settingsBody==null)return;
        settingsCategory=group;final int epoch=++settingsEpoch;
        settingsBody.removeAllViews();settingsBody.addView(settingsText("Lendo configuração…",13));
        worker.execute(()->{
            try {
                JSONObject config=readNativeConfig();
                runOnUiThread(()->{
                    if(!settingsActive()||epoch!=settingsEpoch||settingsBody==null)return;
                    settingsBody.removeAllViews();
                    for(Setting setting:SETTINGS)if(setting.group==group)addSetting(config,setting);
                    if(group==2)addTouchSetting();
                });
            }catch(Exception error){settingsError("Não foi possível ler a configuração do PS4.");}
        });
    }
    private void addSetting(JSONObject config,Setting setting) {
        final Object current=currentSetting(config,setting);
        final boolean explicitlySet=config.optJSONObject(setting.section)!=null&&config.optJSONObject(setting.section).has(setting.key);
        String value=current==null||current==JSONObject.NULL?"Padrão do motor":current instanceof Boolean?((Boolean)current?"Ativado":"Desativado"):String.valueOf(current);
        if(!explicitlySet&&current!=null)value+=" · padrão";
        Button row=settingsButton(setting.label+"   ·   "+value);row.setSingleLine(true);
        row.setEllipsize(android.text.TextUtils.TruncateAt.END);row.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);
        LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(-1,dp(40));size.bottomMargin=dp(5);settingsBody.addView(row,size);
        if(setting.kind==0 || current==JSONObject.NULL || (setting.kind==1&&!(current instanceof Boolean)) || (setting.kind==2&&!(current instanceof String))) {
            row.setEnabled(false);row.setAlpha(.72f);return;
        }
        row.setOnClickListener(v->{
            if(!settingsActive()||settingsSaving)return;
            if(setting.kind==1)saveSettingsEntry(setting,Boolean.valueOf(!((Boolean)current)));
            else {
                int selected=-1;for(int i=0;i<setting.choices.length;i++)if(setting.choices[i].equals(current))selected=i;
                new AlertDialog.Builder(this).setTitle(setting.label).setSingleChoiceItems(setting.choices,selected,(dialog,index)->{
                    if(settingsActive())saveSettingsEntry(setting,setting.choices[index]);dialog.dismiss();
                }).setNegativeButton("Cancelar",null).show();
            }
        });
    }
    private void saveSettingsEntry(Setting setting,Object value) {
        if(!settingsActive()||settingsSaving||setting.kind==0)return;
        settingsSaving=true;
        settingsMessage.setText("Salvando configuração…");
        worker.execute(()->{
            try {
                JSONObject config=readNativeConfig();JSONObject section=config.optJSONObject(setting.section);
                if(config.has(setting.section)&&section==null)throw new IOException("Seção PS4 inválida");
                if(section==null){section=new JSONObject();config.put(setting.section,section);}
                section.put(setting.key,value);
                byte[] bytes=(config.toString(2)+"\n").getBytes(StandardCharsets.UTF_8);
                if(bytes.length>512*1024)throw new IOException("Configuração PS4 muito grande");
                directory(settingsConfig.getParentFile());AtomicFile atomic=new AtomicFile(settingsConfig);FileOutputStream output=null;
                try {output=atomic.startWrite();output.write(bytes);atomic.finishWrite(output);}
                catch(IOException error){if(output!=null)atomic.failWrite(output);throw error;}
                runOnUiThread(()->{
                    if(!settingsActive())return;
                    settingsSaving=false;
                    settingsMessage.setText("Salvo · alterações valem no próximo jogo");selectSettingsCategory(settingsCategory);
                });
            }catch(Exception error){runOnUiThread(()->{if(settingsActive())settingsSaving=false;});settingsError("Não foi possível salvar a configuração do PS4.");}
        });
    }
    private void addTouchSetting() {
        final boolean current=getPreferences(MODE_PRIVATE).getBoolean("touch",true);
        Button row=settingsButton("Controles de toque   ·   "+(current?"Ativados":"Desativados"));
        row.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);row.setOnClickListener(v->{
            if(!settingsActive()||settingsSaving)return;
            getPreferences(MODE_PRIVATE).edit().putBoolean("touch",!current).apply();selectSettingsCategory(settingsCategory);
        });settingsBody.addView(row,new LinearLayout.LayoutParams(-1,dp(40)));
    }
    private void settingsError(String message) {
        runOnUiThread(()->{if(settingsActive()&&settingsMessage!=null)settingsMessage.setText(message);});
    }
    private void leaveSettings() {
        if(!settingsActive())return;
        settingsLeaving=true;++settingsEpoch;
        // Save tasks already in this single FIFO worker complete before the human exit.
        worker.execute(this::finishOwner);
    }
    private static final class ApplicationName {
        static boolean expected(Activity context) {return (context.getPackageName()+":station_ps4").equals(android.app.Application.getProcessName());}
    }
}
