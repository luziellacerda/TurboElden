package org.emulationstation.frontend.sony;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.hardware.input.InputManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;

/** Genuine in-APK PS3 owner. Only JNI/core is reused; no external application dispatch. */
public final class Ps3Activity extends Activity implements SurfaceHolder.Callback, InputManager.InputDeviceListener {
    private final ExecutorService worker = Executors.newSingleThreadExecutor(runnable -> new Thread(runnable, "StationPs3Owner"));
    private final Object submissions = new Object();
    private volatile boolean closed;
    private volatile boolean started;
    private volatile boolean gameConfigured;
    private volatile boolean prepared;
    private volatile boolean resumed;
    private boolean requestInFlight = true;
    private volatile Ps3Bootstrap.Ready owner;
    private volatile Ps3Input input;
    private FrameLayout root;
    private TextView progress;
    private SurfaceView surface;
    private Ps3TouchControls controls;
    private InputManager inputManager;
    private boolean exitDialog;
    private LinearLayout settingsBody;
    private TextView settingsMessage;
    private int settingsCategory;
    private int settingsEpoch;
    private boolean settingsLeaving;
    private boolean settingsSaving;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state); Ps3Bootstrap.requireProcess();
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        root = new FrameLayout(this); root.setBackgroundColor(Color.BLACK); setContentView(root);
        progress = text("Preparando PS3…", 18); progress.setGravity(Gravity.CENTER);
        root.addView(progress, new FrameLayout.LayoutParams(-1, -1));
        inputManager = (InputManager) getSystemService(INPUT_SERVICE);
        if (inputManager != null) inputManager.registerInputDeviceListener(this, null);
        Intent request = getIntent();
        String operation = request.getStringExtra("operation");
        if ("settings".equals(operation)) {
            Button loadingBack = settingsButton("‹  Voltar", false);
            loadingBack.setOnClickListener(view -> finish());
            FrameLayout.LayoutParams corner = new FrameLayout.LayoutParams(settingsDp(94), settingsDp(38), Gravity.TOP | Gravity.LEFT);
            corner.setMargins(settingsDp(16), settingsDp(10), 0, 0); root.addView(loadingBack, corner);
        }
        execute(() -> {
            try {
                owner = Ps3Bootstrap.prepare(this);
                if (closed) return;
                Ps3Firmware.ensure(owner, this::showProgress);
                if (closed) return;
                prepared = true;
                if ("settings".equals(operation)) { runOnUiThread(() -> { showSettings(); requestInFlight = false; }); return; }
                if ("prepare".equals(operation)) { runOnUiThread(() -> { if (!closed) { setResult(RESULT_OK); finish(); } }); return; }
                prepareGame(request);
                if (closed) return;
                input = new Ps3Input(owner.emulator);
                runOnUiThread(this::showGame);
            } catch (Throwable error) { failure(error); }
        });
    }

    /** One metadata descriptor is consumed by native; a new descriptor is used to play. */
    private void prepareGame(Intent request) throws Exception {
        showProgress("Preparando o jogo…");
        String path = request.getStringExtra("game_path");
        aenu.aps3e.Emulator.MetaInfo meta;
        if (path != null && new File(path).isDirectory()) {
            File directory = new File(path).getCanonicalFile();
            meta = owner.emulator.meta_info_from_dir(directory.getAbsolutePath());
            if (meta == null || meta.eboot_path == null || !new File(meta.eboot_path).isFile())
                throw new IOException("A pasta não contém um executável PS3 válido");
            validateMetadata(meta);
            gameConfigured = true;
            owner.emulator.setup_game_path(meta.eboot_path);
        } else {
            String supplied = request.getStringExtra("game_uri");
            Uri uri = supplied == null ? request.getData() : Uri.parse(supplied);
            if (uri == null && path != null) uri = Uri.fromFile(new File(path).getCanonicalFile());
            if (uri == null || !("content".equals(uri.getScheme()) || "file".equals(uri.getScheme())))
                throw new IOException("Selecione um ISO PS3 local");
            String keyText = request.getStringExtra("decryption_key_uri");
            Uri key = keyText == null ? null : Uri.parse(keyText);
            int[] metadata = detachPair(uri, key);
            // Both detached FDs are native-owned after this invocation.
            meta = owner.emulator.meta_info_from_iso(metadata[0], metadata[1], uri.toString());
            validateMetadata(meta);
            if (closed) return;
            int[] playback = detachPair(uri, key);
            gameConfigured = true;
            owner.emulator.setup_game_path(aenu.emulator.Emulator.Path.from(uri.toString(), playback[0], playback[1]));
        }
        owner.emulator.setup_game_id(meta.serial);
        File custom = new File(owner.userDirectory, "config/custom_cfg/" + meta.serial + ".yml");
        if (custom.isFile()) aenu.lang.System.setenv("APS3E_CUSTOM_CONFIG_YAML_PATH", custom.getAbsolutePath(), true);
    }
    private static void validateMetadata(aenu.aps3e.Emulator.MetaInfo meta) throws IOException {
        if (meta == null || meta.serial == null || !meta.serial.matches("[A-Za-z0-9_-]{1,32}"))
            throw new IOException("Não foi possível ler o jogo PS3. ISO criptografado exige a chave do próprio jogo");
    }
    private int detach(Uri uri) throws IOException {
        ParcelFileDescriptor descriptor;
        if ("file".equals(uri.getScheme())) descriptor = ParcelFileDescriptor.open(new File(uri.getPath()), ParcelFileDescriptor.MODE_READ_ONLY);
        else if ("content".equals(uri.getScheme())) descriptor = getContentResolver().openFileDescriptor(uri, "r");
        else throw new IOException("O arquivo precisa estar no armazenamento local");
        if (descriptor == null) throw new IOException("Não foi possível ler o arquivo PS3");
        if (descriptor.getStatSize() == 0) { descriptor.close(); throw new IOException("O arquivo PS3 está vazio"); }
        int fd = descriptor.detachFd(); descriptor.close(); return fd;
    }
    private int[] detachPair(Uri game, Uri key) throws IOException {
        int fd = detach(game);
        try { return new int[] {fd, key == null ? -1 : detach(key)}; }
        catch (IOException | RuntimeException error) { ParcelFileDescriptor.adoptFd(fd).close(); throw error; }
    }

    private void showGame() {
        if (closed || isFinishing()) return;
        root.removeAllViews();
        surface = new SurfaceView(this); surface.getHolder().addCallback(this);
        root.addView(surface, new FrameLayout.LayoutParams(-1, -1));
        controls = new Ps3TouchControls(this, input);
        root.addView(controls, new FrameLayout.LayoutParams(-1, -1));
        updateControls();
    }
    @Override public void surfaceCreated(SurfaceHolder holder) {
        if (closed) return;
        activateSurface(holder);
    }
    private void activateSurface(SurfaceHolder holder) {
        execute(() -> {
            if (closed || !resumed || owner == null || !holder.getSurface().isValid()) return;
            try {
                owner.emulator.setup_surface(holder.getSurface());
                if (!started) { started = true; owner.emulator.boot(); }
                else if (owner.emulator.is_paused()) owner.emulator.resume();
            } catch (Throwable error) { failure(error); }
        });
    }
    @Override public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {
        if (closed || width <= 0 || height <= 0) return;
        execute(() -> { if (!closed && started) owner.emulator.change_surface(width, height); });
    }
    @Override public void surfaceDestroyed(SurfaceHolder holder) {
        if (closed) return;
        if (input != null) input.releaseAll();
        execute(() -> { if (!closed && started) { owner.emulator.pause(); owner.emulator.setup_surface(null); } });
    }
    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        if (!closed && input != null && !exitDialog && input.key(event)) return true;
        return super.dispatchKeyEvent(event);
    }
    @Override public boolean onGenericMotionEvent(MotionEvent event) {
        if (!closed && input != null && !exitDialog && input.motion(event)) return true;
        return super.onGenericMotionEvent(event);
    }
    @Override public void onInputDeviceAdded(int id) { updateControls(); }
    @Override public void onInputDeviceChanged(int id) { updateControls(); }
    @Override public void onInputDeviceRemoved(int id) {
        if (input != null) input.releaseAll(); updateControls();
    }
    private void updateControls() {
        if (controls == null) return;
        boolean show = !Ps3Input.physicalControllerPresent() && getPreferences(MODE_PRIVATE).getBoolean("touch", true);
        if (!show) controls.release(); controls.setVisibility(show ? View.VISIBLE : View.GONE);
    }
    @Override protected void onPause() {
        resumed = false;
        if (input != null) input.releaseAll();
        if (started) execute(() -> { if (!closed) owner.emulator.pause(); });
        super.onPause();
    }
    @Override protected void onResume() {
        super.onResume(); resumed = true; updateControls();
        if (surface != null) activateSurface(surface.getHolder());
    }
    @Override public void onBackPressed() {
        if (!started) { if (settingsBody != null) leaveSettings(); else finish(); return; }
        if (exitDialog) return;
        exitDialog = true; if (input != null) input.releaseAll();
        new AlertDialog.Builder(this).setTitle("Sair do jogo?").setMessage("Voltar à TurboStations.")
            .setNegativeButton("Continuar", (dialog, which) -> exitDialog = false)
            .setPositiveButton("Sair", (dialog, which) -> finish())
            .setOnCancelListener(dialog -> exitDialog = false).show();
    }
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        // A private singleTask owner never replaces a running game with a new request.
        if (started || gameConfigured || requestInFlight || closed) return;
        setIntent(intent);
        if (owner == null || !prepared) return;
        if ("settings".equals(intent.getStringExtra("operation"))) { showSettings(); return; }
        requestInFlight = true;
        execute(() -> {
            try {
                Ps3Firmware.ensure(owner, this::showProgress);
                if (closed) return;
                if ("prepare".equals(intent.getStringExtra("operation"))) {
                    runOnUiThread(() -> { if (!closed) { setResult(RESULT_OK); finish(); } }); return;
                }
                prepareGame(intent); if (closed) return;
                input = new Ps3Input(owner.emulator); runOnUiThread(this::showGame);
            } catch (Throwable error) { failure(error); }
        });
    }
    @Override public void onDestroy() {
        synchronized (submissions) {
            if (!closed) {
                closed = true;
                if (inputManager != null) inputManager.unregisterInputDeviceListener(this);
                if (input != null) input.releaseAll();
                worker.execute(() -> {
                    try { if (owner != null && started) owner.emulator.quit(); }
                    finally {
                        if (started || gameConfigured) {
                            Ps3Bootstrap.requireProcess();
                            // Matches the upstream per-game lifetime, never Station's main process.
                            android.os.Process.killProcess(android.os.Process.myPid());
                        }
                    }
                });
                worker.shutdown();
            }
        }
        super.onDestroy();
    }
    private void execute(Runnable task) {
        synchronized (submissions) {
            if (closed) return;
            try {
                worker.execute(() -> { if (!closed) task.run(); });
            } catch (RejectedExecutionException error) {
                if (!closed) failure(error);
            }
        }
    }
    private void showProgress(String message) {
        runOnUiThread(() -> { if (!closed && progress != null) progress.setText(message); });
    }
    private void failure(Throwable error) {
        runOnUiThread(() -> {
            if (closed || isFinishing()) return;
            String message = error.getMessage();
            new AlertDialog.Builder(this).setTitle("PS3")
                .setMessage(message == null ? "Não foi possível preparar o motor PS3." : message)
                .setPositiveButton("Voltar", (dialog, which) -> finish())
                .setOnCancelListener(dialog -> finish()).show();
        });
    }
    private TextView text(String value, int size) {
        TextView view = new TextView(this); view.setText(value); view.setTextSize(size); view.setTextColor(0xffe9eef9); return view;
    }
    private int settingsDp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
    private GradientDrawable settingsBackground(int color, int radius) {
        GradientDrawable result = new GradientDrawable(); result.setColor(color);
        result.setCornerRadius(settingsDp(radius)); return result;
    }
    private Button settingsButton(String label, boolean accent) {
        Button button = new Button(this); button.setText(label); button.setAllCaps(false);
        button.setTextSize(13); button.setTextColor(accent ? 0xff06151d : 0xffe9eef9);
        button.setTypeface(Typeface.DEFAULT, Typeface.BOLD); button.setMinHeight(0); button.setMinimumHeight(0);
        button.setPadding(settingsDp(12), 0, settingsDp(12), 0);
        button.setBackground(settingsBackground(accent ? 0xff55d2ee : 0xff182632, 7));
        return button;
    }
    private void showSettings() {
        if (closed || isFinishing()) return;
        settingsLeaving = false; root.removeAllViews();
        root.setBackgroundColor(0xff081017);
        LinearLayout page = new LinearLayout(this); page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(settingsDp(16), settingsDp(10), settingsDp(16), settingsDp(10));
        root.addView(page, new FrameLayout.LayoutParams(-1,-1));
        LinearLayout heading = new LinearLayout(this); heading.setGravity(Gravity.CENTER_VERTICAL);
        Button back = settingsButton("‹  Voltar", false); back.setOnClickListener(view -> leaveSettings());
        heading.addView(back, new LinearLayout.LayoutParams(settingsDp(94), settingsDp(38)));
        TextView title = text("PS3  /  Configurações",19); title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        title.setPadding(settingsDp(14),0,0,0); heading.addView(title,new LinearLayout.LayoutParams(0,-2,1));
        page.addView(heading,new LinearLayout.LayoutParams(-1,settingsDp(44)));
        settingsMessage = text("Opções do motor · alterações valem no próximo jogo",12);
        settingsMessage.setTextColor(0xff93a8ba); settingsMessage.setPadding(0,settingsDp(3),0,settingsDp(10));
        page.addView(settingsMessage);
        LinearLayout main = new LinearLayout(this); main.setOrientation(LinearLayout.HORIZONTAL);
        page.addView(main,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout tabs = new LinearLayout(this); tabs.setOrientation(LinearLayout.VERTICAL);
        main.addView(tabs,new LinearLayout.LayoutParams(settingsDp(140),-1));
        String[] names={"Imagem","Áudio","Processamento","Sistema"};
        for (int i=0;i<names.length;i++) {
            final int category=i; Button tab=settingsButton(names[i],false);
            tab.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);
            tab.setOnClickListener(view -> selectSettingsCategory(category));
            LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(-1,settingsDp(39));
            size.setMargins(0,0,settingsDp(12),settingsDp(7));tabs.addView(tab,size);
        }
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(false);
        main.addView(scroll,new LinearLayout.LayoutParams(0,-1,1));
        settingsBody=new LinearLayout(this);settingsBody.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(settingsBody,new ScrollView.LayoutParams(-1,-2));
        selectSettingsCategory(settingsCategory);
    }
    private static final class Setting {
        final int category, kind, minimum, maximum;
        final String tag, label; final String[] values;
        Setting(int category,int kind,String tag,String label,int minimum,int maximum,String...values) {
            this.category=category;this.kind=kind;this.tag=tag;this.label=label;
            this.minimum=minimum;this.maximum=maximum;this.values=values;
        }
    }
    // Keys and bounds are the pinned official config/JNI contract, not frontend substitutes.
    // Shader enum labels differ between the published XML and official 2.43 native defaults;
    // show that current value without writing a guessed conversion.
    private static final Setting[] SETTINGS={
        new Setting(0,0,"Video|Renderer","Renderizador",0,0),
        new Setting(0,1,"Video|Resolution","Resolução",0,0,"1920x1080","1920x1080i","1280x720","720x480","720x480i","720x576","720x576i","1600x1080","1440x1080","1280x1080","960x1080"),
        new Setting(0,2,"Video|Resolution Scale","Escala de resolução",25,800),
        new Setting(0,1,"Video|Aspect ratio","Proporção da imagem",0,0,"4:3","16:9"),
        new Setting(0,1,"Video|Frame limit","Limite de quadros",0,0,"Off","30","50","60","120","Display","Auto","PS3 Native","Infinite"),
        new Setting(0,0,"Video|Shader Mode","Compilação de shaders",0,0),
        new Setting(0,3,"Video|Write Color Buffers","Gravar buffers de cor",0,0),
        new Setting(0,3,"Video|Strict Rendering Mode","Renderização estrita",0,0),
        new Setting(1,2,"Audio|Master Volume","Volume",0,200),
        new Setting(1,3,"Audio|Enable Buffering","Buffer de áudio",0,0),
        new Setting(1,3,"Audio|Enable Time Stretching","Ajuste de tempo do áudio",0,0),
        new Setting(2,1,"Core|PPU Decoder","Decodificador PPU",0,0,"Interpreter (static)","Recompiler (LLVM)"),
        new Setting(2,1,"Core|SPU Decoder","Decodificador SPU",0,0,"Interpreter (static)","Interpreter (dynamic)","Recompiler (ASMJIT)","Recompiler (LLVM)"),
        new Setting(2,2,"Core|PPU Threads","Threads PPU",1,8),
        new Setting(2,2,"Core|Preferred SPU Threads","Threads SPU preferidas",0,6),
        new Setting(2,2,"Core|Max LLVM Compile Threads","Threads de compilação LLVM",0,12),
        new Setting(2,3,"Core|LLVM Precompilation","Pré-compilação LLVM",0,0),
        new Setting(3,3,"Miscellaneous|Show trophy popups","Avisos de troféus",0,0)
    };
    private void selectSettingsCategory(int category) {
        if (closed || settingsLeaving || settingsBody==null) return;
        settingsCategory=category; final int epoch=++settingsEpoch;
        settingsBody.removeAllViews();settingsBody.addView(text("Lendo configuração…",13));
        execute(() -> {
            final String[] values=new String[SETTINGS.length];
            try (aenu.emulator.Emulator.Config config=aenu.emulator.Emulator.Config.openFile(owner.configFile.getAbsolutePath())) {
                for(int i=0;i<SETTINGS.length;i++)if(SETTINGS[i].category==category)values[i]=config.load(SETTINGS[i].tag);
                runOnUiThread(() -> {
                    if(closed || settingsLeaving || epoch!=settingsEpoch || settingsBody==null)return;
                    settingsBody.removeAllViews();
                    for(int i=0;i<SETTINGS.length;i++)if(SETTINGS[i].category==category)addSetting(SETTINGS[i],values[i]);
                    if(category==3)addTouchSetting();
                });
            } catch(Throwable error) {failure(error);}
        });
    }
    private void addSetting(Setting setting,String current) {
        Button row=settingsButton(setting.label+"   ·   "+displaySettingValue(setting,current),false);
        row.setTypeface(Typeface.DEFAULT,Typeface.NORMAL);row.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);
        row.setTextSize(13);row.setSingleLine(true);row.setEllipsize(android.text.TextUtils.TruncateAt.END);
        LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(-1,settingsDp(40));size.bottomMargin=settingsDp(5);
        settingsBody.addView(row,size);
        if(current==null || setting.kind==0) {row.setEnabled(false);row.setAlpha(.72f);return;}
        row.setOnClickListener(view -> {
            if(settingsLeaving || settingsSaving)return;
            if(setting.kind==3) {
                if(!"true".equals(current)&&!"false".equals(current))return;
                saveSettingsEntry(setting.tag,Boolean.toString(!Boolean.parseBoolean(current)));
            } else if(setting.kind==1) {
                int selected=-1;for(int i=0;i<setting.values.length;i++)if(setting.values[i].equals(current))selected=i;
                new AlertDialog.Builder(this).setTitle(setting.label)
                    .setSingleChoiceItems(setting.values,selected,(dialog,index)->{
                        if(!settingsLeaving)saveSettingsEntry(setting.tag,setting.values[index]);dialog.dismiss();
                    }).setNegativeButton("Cancelar",null).show();
            } else if(setting.kind==2)editSettingsNumber(setting,current);
        });
    }
    private String displaySettingValue(Setting setting,String current) {
        if(current==null)return "Indisponível nesta versão";
        if(setting.kind==3)return "true".equals(current)?"Ativado":"false".equals(current)?"Desativado":current;
        if(setting.tag.equals("Audio|Master Volume")||setting.tag.equals("Video|Resolution Scale"))return current+"%";
        return current;
    }
    private void editSettingsNumber(Setting setting,String current) {
        final int old;try{old=Integer.parseInt(current);}catch(NumberFormatException invalid){return;}
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(settingsDp(20),settingsDp(10),settingsDp(20),0);
        TextView value=text(Integer.toString(old),15);box.addView(value);
        SeekBar bar=new SeekBar(this);bar.setMax(setting.maximum-setting.minimum);
        bar.setProgress(Math.max(0,Math.min(setting.maximum-setting.minimum,old-setting.minimum)));box.addView(bar);
        bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar seek,int progress,boolean human){value.setText(Integer.toString(progress+setting.minimum));}
            public void onStartTrackingTouch(SeekBar seek){}
            public void onStopTrackingTouch(SeekBar seek){}
        });
        new AlertDialog.Builder(this).setTitle(setting.label).setView(box)
            .setNegativeButton("Cancelar",null).setPositiveButton("Salvar",(dialog,which)->{
                if(!settingsLeaving && !settingsSaving)saveSettingsEntry(setting.tag,Integer.toString(bar.getProgress()+setting.minimum));
            }).show();
    }
    private void addTouchSetting() {
        final boolean enabled=getPreferences(MODE_PRIVATE).getBoolean("touch",true);
        Button row=settingsButton("Controles de toque   ·   "+(enabled?"Ativados":"Desativados"),false);
        row.setTypeface(Typeface.DEFAULT,Typeface.NORMAL);row.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);
        row.setOnClickListener(view->{
            if(settingsLeaving || settingsSaving)return;
            getPreferences(MODE_PRIVATE).edit().putBoolean("touch",!enabled).apply();selectSettingsCategory(settingsCategory);
        });
        settingsBody.addView(row,new LinearLayout.LayoutParams(-1,settingsDp(40)));
    }
    private void saveSettingsEntry(String tag,String value) {
        if(settingsLeaving || settingsSaving || closed)return;
        settingsSaving=true;
        settingsMessage.setText("Salvando configuração…");
        execute(() -> {
            try(aenu.emulator.Emulator.Config config=aenu.emulator.Emulator.Config.openFile(owner.configFile.getAbsolutePath())) {
                config.save(tag,value);String yaml=config.closeText();
                if(yaml==null || yaml.length()==0)throw new IOException("O motor não retornou a configuração");
                Ps3Bootstrap.writeAtomic(owner.configFile,yaml.getBytes(StandardCharsets.UTF_8));
                runOnUiThread(()->{
                    settingsSaving=false;
                    if(closed || settingsLeaving)return;
                    settingsMessage.setText("Salvo · alterações valem no próximo jogo");selectSettingsCategory(settingsCategory);
                });
            }catch(Throwable error){runOnUiThread(()->settingsSaving=false);failure(error);}
        });
    }
    private void leaveSettings() {
        if(closed || settingsLeaving)return;
        settingsLeaving=true;++settingsEpoch;
        // Queue exit behind pending saves; do not drop a human change by closing the worker first.
        execute(()->runOnUiThread(()->{if(!closed && !isFinishing())finish();}));
    }
}
