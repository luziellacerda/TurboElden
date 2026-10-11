package org.emulationstation.frontend.sony;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
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
        if (!started) { finish(); return; }
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
    private void showSettings() {
        if (closed || isFinishing()) return;
        root.removeAllViews(); LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL); int pad = (int)(24*getResources().getDisplayMetrics().density);
        panel.setPadding(pad,pad,pad,pad); root.addView(panel, new FrameLayout.LayoutParams(-1,-1));
        panel.addView(text("PS3 · Configurações", 21));
        panel.addView(text("Sistema preparado · Vulkan · configuração original do motor", 14));
        Switch touch = new Switch(this); touch.setText("Controles de toque"); touch.setTextColor(0xffe9eef9);
        touch.setChecked(getPreferences(MODE_PRIVATE).getBoolean("touch", true));
        touch.setOnCheckedChangeListener((button, checked) -> getPreferences(MODE_PRIVATE).edit().putBoolean("touch", checked).apply());
        panel.addView(touch);
        Switch trophies = new Switch(this); trophies.setText("Avisos de troféus"); trophies.setTextColor(0xffe9eef9);
        panel.addView(trophies);
        TextView volumeText = text("Volume",14); panel.addView(volumeText);
        SeekBar volume = new SeekBar(this); volume.setMax(100); panel.addView(volume);
        execute(() -> {
            try (aenu.emulator.Emulator.Config config = aenu.emulator.Emulator.Config.openFile(owner.configFile.getAbsolutePath())) {
                boolean show = "true".equals(config.load("Miscellaneous|Show trophy popups"));
                int level = Integer.parseInt(config.load("Audio|Master Volume"));
                runOnUiThread(() -> {
                    if (closed) return;
                    trophies.setChecked(show); volume.setProgress(Math.max(0,Math.min(100,level)));
                    trophies.setOnCheckedChangeListener((button, checked) -> saveConfig("Miscellaneous|Show trophy popups", Boolean.toString(checked)));
                    volume.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                        public void onProgressChanged(SeekBar bar,int value,boolean human) { volumeText.setText("Volume · " + value + "%"); }
                        public void onStartTrackingTouch(SeekBar bar) {}
                        public void onStopTrackingTouch(SeekBar bar) { saveConfig("Audio|Master Volume", Integer.toString(bar.getProgress())); }
                    });
                });
            } catch (Throwable error) { failure(error); }
        });
        Button back = new Button(this); back.setText("Voltar"); back.setOnClickListener(view -> finish()); panel.addView(back);
    }
    private void saveConfig(String tag, String value) {
        execute(() -> {
            if (closed) return;
            try (aenu.emulator.Emulator.Config config = aenu.emulator.Emulator.Config.openFile(owner.configFile.getAbsolutePath())) {
                config.save(tag,value); String yaml = config.closeText();
                Ps3Bootstrap.writeAtomic(owner.configFile, yaml.getBytes(StandardCharsets.UTF_8));
            } catch (Throwable error) { failure(error); }
        });
    }
}
