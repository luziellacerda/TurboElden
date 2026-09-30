package org.emulationstation.frontend;

import android.content.Intent;
import android.content.ComponentName;
import android.content.res.ColorStateList;
import android.os.Bundle;
import android.os.Handler;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import java.lang.reflect.Method;

/** Wait for real Dolphin initialization, then use the upstream launch checks and UI. */
public final class DolphinEntryActivity extends tdolphin.appcompat.app.AppCompatActivity {
    private final Handler handler = new Handler();
    private TextView status;
    private ProgressBar progress;
    private boolean dispatched;
    private final Runnable ready = () -> prepare();

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(0xff07110b);
        getWindow().setNavigationBarColor(0xff07110b);
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setGravity(Gravity.CENTER);
        panel.setPadding(36, 24, 36, 24);
        panel.setBackgroundColor(0xff07110b);
        TextView title = new TextView(this);
        title.setText("TURBORAMA  •  DOLPHIN");
        title.setTextColor(0xff53f887); title.setTextSize(25);
        panel.addView(title);
        status = new TextView(this);
        status.setText("Preparando o Dolphin…");
        status.setTextColor(0xffdeeee3); status.setTextSize(17); status.setPadding(0, 20, 0, 20);
        panel.addView(status);
        progress = new ProgressBar(this);
        progress.setIndeterminateTintList(ColorStateList.valueOf(0xff53f887));
        panel.addView(progress, new LinearLayout.LayoutParams(56, 56));
        Button back = new Button(this); back.setText("Voltar"); back.setOnClickListener(v -> finish());
        panel.addView(back);
        setContentView(panel);
        handler.post(ready);
    }

    private void prepare() {
        if (isFinishing() || dispatched) return;
        try {
            if (DolphinBootstrap.initializationError != null) throw DolphinBootstrap.initializationError;
            Class<?> init = Class.forName("org.dolphinemu.dolphinemu.utils.DirectoryInitialization");
            boolean done = (Boolean) init.getMethod("areDolphinDirectoriesReady").invoke(null);
            if (!done) { handler.postDelayed(ready, 120); return; }
            dispatched = true;
            if (getIntent().getBooleanExtra("settings", false)) {
                Class<?> menu = Class.forName("org.dolphinemu.dolphinemu.features.settings.ui.MenuTag");
                Object root = menu.getField("SETTINGS").get(null);
                Class.forName("tdolphin.tracing.Trace").getMethod("launch", android.content.Context.class, menu).invoke(null, this, root);
            } else {
                String game = getIntent().getStringExtra("game");
                Class<?> fragment = Class.forName("tdolphin.fragment.app.FragmentActivity");
                Method launch = Class.forName("tdolphin.shaded.okio.Path$Companion")
                    .getMethod("launch", fragment, String[].class, boolean.class, boolean.class);
                launch.invoke(null, this, new String[]{game}, false, false);
            }
        } catch (Throwable error) {
            android.util.Log.e("TurboDolphin", "Embedded launch failed", error);
            progress.setVisibility(View.GONE);
            status.setText("Não foi possível preparar o Dolphin. Volte e tente novamente.");
        }
    }

    @Override public void startActivity(Intent intent) {
        super.startActivity(intent);
        ComponentName target = intent.getComponent();
        if (target != null && (target.getClassName().endsWith("EmulationActivity") || target.getClassName().endsWith("SettingsActivity"))) finish();
    }
    @Override protected void onDestroy() { handler.removeCallbacksAndMessages(null); super.onDestroy(); }
}
