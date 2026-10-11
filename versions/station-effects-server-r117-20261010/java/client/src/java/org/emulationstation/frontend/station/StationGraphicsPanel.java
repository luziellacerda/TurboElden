package org.emulationstation.frontend.station;

import android.app.Activity;
import android.app.Application;
import android.app.Dialog;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import java.util.ArrayList;

/** Opaque graphics settings page, usable as a settings tab or as a dialog. */
public final class StationGraphicsPanel extends Dialog {
    private static StationGraphicsPanel visible;
    private final Activity owner;
    private Content content;
    private boolean lifecycleRegistered;
    private final Application.ActivityLifecycleCallbacks lifecycle = new Application.ActivityLifecycleCallbacks() {
        public void onActivityStopped(Activity activity) { if (activity == owner) dismiss(); }
        public void onActivityDestroyed(Activity activity) { if (activity == owner) dismiss(); }
        public void onActivityCreated(Activity activity, Bundle state) {}
        public void onActivityStarted(Activity activity) {}
        public void onActivityResumed(Activity activity) {}
        public void onActivityPaused(Activity activity) {}
        public void onActivitySaveInstanceState(Activity activity, Bundle state) {}
    };

    private StationGraphicsPanel(Activity owner) {
        super(owner, android.R.style.Theme_Material_NoActionBar_Fullscreen);
        this.owner = owner;
    }
    public static boolean open(Activity owner) {
        if (owner == null || owner.isFinishing() || owner.isDestroyed()) return false;
        owner.runOnUiThread(() -> {
            if (owner.isFinishing() || owner.isDestroyed() || visible != null) return;
            StationGraphicsPanel panel = new StationGraphicsPanel(owner);
            visible = panel;
            panel.show();
        });
        return true;
    }
    public static View createContent(Activity owner, Runnable close) {
        return new Content(owner, close);
    }
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setBackgroundDrawable(new ColorDrawable(0xff080c13));
        getWindow().setLayout(-1, -1);
        getWindow().getDecorView().setSystemUiVisibility(5894);
        content = new Content(owner, this::dismiss);
        setContentView(content);
        owner.getApplication().registerActivityLifecycleCallbacks(lifecycle);
        lifecycleRegistered = true;
    }
    @Override public void dismiss() {
        if (content != null) content.disconnect();
        if (lifecycleRegistered) {
            owner.getApplication().unregisterActivityLifecycleCallbacks(lifecycle);
            lifecycleRegistered = false;
        }
        if (visible == this) visible = null;
        super.dismiss();
    }

    private static final class Option {
        final int effect; final Switch toggle;
        Option(int effect, Switch toggle) { this.effect = effect; this.toggle = toggle; }
    }
    private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener {
        private final Activity owner;
        private final StationGraphicsPreferences preferences;
        private final ArrayList<Option> options = new ArrayList<>();
        private final Switch master;
        private final TextView status;
        private final RadioGroup backgrounds;
        private boolean connected, updating;

        Content(Activity owner, Runnable close) {
            super(owner);
            this.owner = owner;
            preferences = StationGraphicsPreferences.get(owner);
            setOrientation(VERTICAL);
            setPadding(dp(24), dp(16), dp(24), dp(14));
            setBackgroundColor(0xff080c13);
            LinearLayout header = new LinearLayout(owner);
            header.setGravity(Gravity.CENTER_VERTICAL);
            TextView back = text("‹  VOLTAR", 13, 0xffdbe9f8);
            back.setTypeface(null, Typeface.BOLD);
            back.setPadding(dp(16), 0, dp(16), 0);
            back.setGravity(Gravity.CENTER);
            back.setBackground(surface(0xff172431, 8));
            back.setFocusable(true);
            back.setOnClickListener(v -> { if (close != null) close.run(); });
            header.addView(back, new LinearLayout.LayoutParams(-2, dp(38)));
            TextView title = text("EFEITOS GRÁFICOS", 22, 0xfff3f8ff);
            title.setTypeface(null, Typeface.BOLD);
            title.setPadding(dp(20), 0, 0, 0);
            header.addView(title, new LinearLayout.LayoutParams(0, dp(42), 1));
            addView(header);

            ScrollView scroll = new ScrollView(owner);
            scroll.setFillViewport(true);
            scroll.setOverScrollMode(View.OVER_SCROLL_NEVER);
            LinearLayout list = new LinearLayout(owner);
            list.setOrientation(VERTICAL);
            list.setPadding(0, dp(10), 0, dp(8));
            scroll.addView(list, new ScrollView.LayoutParams(-1, -2));
            addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

            master = toggle("Efeitos gerais");
            master.setTextOn("Ativo"); master.setTextOff("Desativado");
            status = text("", 12, 0xff9cb6c9);
            LinearLayout masterRow = new LinearLayout(owner);
            masterRow.setOrientation(VERTICAL);
            masterRow.setPadding(dp(14), dp(7), dp(14), dp(7));
            masterRow.setBackground(surface(0xff132330, 9));
            masterRow.addView(master, new LinearLayout.LayoutParams(-1, dp(40)));
            masterRow.addView(status, new LinearLayout.LayoutParams(-1, -2));
            list.addView(masterRow);
            master.setOnCheckedChangeListener((button, checked) -> {
                if (!updating) preferences.setMasterDisabled(!checked);
            });

            addOption(list, StationGraphicsPreferences.LED, "LEDs das capas", "Luzes e rastros das capas de sistemas e jogos.");
            addOption(list, StationGraphicsPreferences.VIDEO, "Vídeos do carrossel", "Reprodução dos vídeos de sistemas e coleções.");
            addOption(list, StationGraphicsPreferences.CLOUDS, "Fundo animado", "Movimento das nuvens ou das ondas escolhidas abaixo.");
            addOption(list, StationGraphicsPreferences.ICONS, "Ícones e Lotties", "Movimento do robô, estrelas e demais ícones.");
            addOption(list, StationGraphicsPreferences.CELL_EFFECTS, "Efeitos das células", "Brilhos e animações decorativas dos botões e capas.");
            addOption(list, StationGraphicsPreferences.UI_TRANSITIONS, "Transições visuais", "Animações de entrada e troca de itens do menu.");

            TextView backgroundTitle = text("FUNDO", 12, 0xff79c8ff);
            backgroundTitle.setTypeface(null, Typeface.BOLD);
            backgroundTitle.setPadding(dp(4), dp(12), 0, dp(5));
            list.addView(backgroundTitle);
            backgrounds = new RadioGroup(owner);
            backgrounds.setOrientation(LinearLayout.HORIZONTAL);
            String[] labels = {"Céu", "Ondas", "Sem fundo"};
            for (int mode = 0; mode < labels.length; mode++) {
                RadioButton button = new RadioButton(owner);
                button.setId(0x117100 + mode);
                button.setText(labels[mode]); button.setTextSize(14); button.setTextColor(0xffe3edf8);
                backgrounds.addView(button, new RadioGroup.LayoutParams(0, dp(42), 1));
            }
            backgrounds.setOnCheckedChangeListener((group, id) -> {
                if (!updating && id >= 0x117100 && id <= 0x117102) preferences.setBackgroundMode(id - 0x117100);
            });
            list.addView(backgrounds);
            TextView foot = text("As escolhas ficam salvas. O botão de economia interrompe todos os efeitos; ao reativar, suas escolhas voltam.", 12, 0xff9cb6c9);
            foot.setPadding(dp(4), dp(8), dp(4), 0);
            list.addView(foot);
            render(preferences.snapshot());
        }

        private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
        private TextView text(String value, int size, int color) {
            TextView text = new TextView(owner); text.setText(value); text.setTextSize(size); text.setTextColor(color);
            text.setGravity(Gravity.CENTER_VERTICAL); return text;
        }
        private GradientDrawable surface(int color, int radius) {
            GradientDrawable drawable = new GradientDrawable(); drawable.setColor(color); drawable.setCornerRadius(dp(radius)); return drawable;
        }
        private Switch toggle(String label) {
            Switch toggle = new Switch(owner); toggle.setText(label); toggle.setTextSize(15); toggle.setTextColor(0xffedf5ff);
            toggle.setShowText(true); toggle.setTextOn("Ativo"); toggle.setTextOff("Desativado"); toggle.setSwitchPadding(dp(18));
            return toggle;
        }
        private void addOption(LinearLayout list, int effect, String label, String detail) {
            LinearLayout row = new LinearLayout(owner); row.setOrientation(VERTICAL);
            row.setPadding(dp(14), dp(3), dp(14), dp(7)); row.setBackground(surface(0xff101821, 8));
            Switch toggle = toggle(label); row.addView(toggle, new LinearLayout.LayoutParams(-1, dp(37)));
            TextView hint = text(detail, 11, 0xff9cb0c2); row.addView(hint, new LinearLayout.LayoutParams(-1, -2));
            LinearLayout.LayoutParams layout = new LinearLayout.LayoutParams(-1, -2); layout.topMargin = dp(7); list.addView(row, layout);
            options.add(new Option(effect, toggle));
            toggle.setOnCheckedChangeListener((button, checked) -> { if (!updating) preferences.setEnabled(effect, checked); });
        }
        private void render(StationGraphicsPreferences.State state) {
            updating = true;
            try {
                master.setChecked(!state.masterDisabled);
                status.setText(state.masterDisabled ? "Economia ativa · todas as animações paradas" : "Ative somente os efeitos que deseja usar");
                for (Option option : options) {
                    option.toggle.setChecked((state.individualMask & option.effect) != 0);
                    option.toggle.setEnabled(!state.masterDisabled);
                    option.toggle.setAlpha(state.masterDisabled ? .45f : 1f);
                }
                backgrounds.check(0x117100 + state.backgroundMode);
                backgrounds.setAlpha(state.masterDisabled ? .45f : 1f);
                for (int i = 0; i < backgrounds.getChildCount(); i++) backgrounds.getChildAt(i).setEnabled(!state.masterDisabled);
            } finally { updating = false; }
        }
        @Override protected void onAttachedToWindow() {
            super.onAttachedToWindow();
            if (!connected) { connected = true; preferences.addListener(this); }
            render(preferences.snapshot());
        }
        @Override protected void onDetachedFromWindow() { disconnect(); super.onDetachedFromWindow(); }
        void disconnect() { if (connected) { preferences.removeListener(this); connected = false; } }
        @Override public void onGraphicsChanged(StationGraphicsPreferences.State state) {
            owner.runOnUiThread(() -> { if (connected && !owner.isFinishing()) render(preferences.snapshot()); });
        }
    }
}
