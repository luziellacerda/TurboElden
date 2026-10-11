package org.emulationstation.frontend.station;

import android.app.Activity;
import android.app.Application;
import android.app.Dialog;
import android.content.res.ColorStateList;
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

/** Opaque settings page. Decoration is static; no additional frame loop or worker. */
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
    public static View createContent(Activity owner, Runnable close) { return new Content(owner, close); }
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setBackgroundDrawable(new ColorDrawable(0xff050a15));
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
        final int effect; final Switch toggle; final TextView value;
        Option(int effect, Switch toggle, TextView value) { this.effect = effect; this.toggle = toggle; this.value = value; }
    }
    private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener {
        private static final int WHITE = 0xffedf6ff, MUTED = 0xff9baec4, ACCENT = 0xff76d7f5, ACTIVE = 0xff66dbad;
        private static final int MODE_ID = 0x118100;
        private final Activity owner;
        private final StationGraphicsPreferences preferences;
        private final ArrayList<Option> options = new ArrayList<>();
        private final Switch master;
        private final TextView status, masterValue;
        private final RadioGroup backgrounds;
        private final boolean wide;
        private boolean connected, updating;

        Content(Activity owner, Runnable close) {
            super(owner);
            this.owner = owner;
            preferences = StationGraphicsPreferences.get(owner);
            android.util.DisplayMetrics display = getResources().getDisplayMetrics();
            wide = display.widthPixels > display.heightPixels && display.widthPixels / display.density >= 520;
            setOrientation(VERTICAL);
            setPadding(dp(wide ? 24 : 18), dp(14), dp(wide ? 24 : 18), dp(10));
            GradientDrawable backdrop = new GradientDrawable(GradientDrawable.Orientation.TL_BR, new int[]{0xff050a15, 0xff0b1728});
            setBackground(backdrop);

            LinearLayout header = new LinearLayout(owner); header.setGravity(Gravity.CENTER_VERTICAL);
            LinearLayout titles = vertical();
            TextView eyebrow = text("PERSONALIZAR A EXPERIÊNCIA", 10, ACCENT); eyebrow.setLetterSpacing(.10f);
            titles.addView(eyebrow);
            TextView title = text("Efeitos gráficos", 22, WHITE); title.setTypeface(null, Typeface.BOLD); titles.addView(title);
            header.addView(titles, new LinearLayout.LayoutParams(0, dp(48), 1));
            TextView back = text("‹  VOLTAR", 12, WHITE); back.setTypeface(null, Typeface.BOLD); back.setGravity(Gravity.CENTER);
            back.setPadding(dp(16), 0, dp(16), 0); back.setBackground(surface(0xff15243a, 0xff30455e, 10));
            back.setFocusable(true); back.setContentDescription("Voltar às configurações");
            back.setOnClickListener(v -> { if (close != null) close.run(); });
            header.addView(back, new LinearLayout.LayoutParams(-2, dp(38))); addView(header);
            View rule = new View(owner); rule.setBackgroundColor(0xff254154);
            LinearLayout.LayoutParams ruleLayout = new LinearLayout.LayoutParams(-1, dp(1)); ruleLayout.topMargin = dp(8); addView(rule, ruleLayout);

            ScrollView scroll = new ScrollView(owner); scroll.setFillViewport(true); scroll.setOverScrollMode(View.OVER_SCROLL_NEVER);
            scroll.setClipToPadding(false);
            LinearLayout list = vertical(); list.setPadding(0, dp(10), 0, dp(6));
            scroll.addView(list, new ScrollView.LayoutParams(-1, -2)); addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

            LinearLayout masterRow = rowSurface(0xff122639, 0xff36566c);
            LinearLayout masterCopy = vertical();
            TextView masterTitle = text("Efeitos gerais", 15, WHITE); masterTitle.setTypeface(null, Typeface.BOLD); masterCopy.addView(masterTitle);
            status = text("", 11, MUTED); status.setMaxLines(2); masterCopy.addView(status);
            masterRow.addView(masterCopy, new LinearLayout.LayoutParams(0, -2, 1));
            masterValue = text("", 11, ACTIVE); masterValue.setPadding(dp(8), 0, dp(8), 0); masterRow.addView(masterValue);
            master = toggle("Efeitos gerais"); masterRow.addView(master, new LinearLayout.LayoutParams(dp(48), dp(42)));
            list.addView(masterRow, new LinearLayout.LayoutParams(-1, -2));
            master.setOnCheckedChangeListener((button, checked) -> { if (!updating) preferences.setMasterDisabled(!checked); });

            section(list, "FUNDO DO MENU", "Ondas suaves, céu ou tela sem fundo");
            backgrounds = new RadioGroup(owner); backgrounds.setOrientation(HORIZONTAL);
            backgrounds.setPadding(dp(4), dp(3), dp(4), dp(3)); backgrounds.setBackground(surface(0xff101c2d, 0xff253c54, 10));
            int[] modes = { StationGraphicsPreferences.WAVES, StationGraphicsPreferences.SKY, StationGraphicsPreferences.OFF };
            String[] names = { "Ondas", "Céu", "Sem fundo" };
            for (int i = 0; i < modes.length; i++) {
                RadioButton button = new RadioButton(owner); button.setId(MODE_ID + modes[i]); button.setText(names[i]);
                button.setTextSize(13); button.setTextColor(WHITE); button.setGravity(Gravity.CENTER_VERTICAL);
                button.setButtonTintList(tint(ACTIVE)); button.setPadding(dp(7), 0, dp(3), 0);
                backgrounds.addView(button, new RadioGroup.LayoutParams(0, dp(40), 1));
            }
            backgrounds.setOnCheckedChangeListener((group, id) -> {
                if (!updating && id >= MODE_ID && id <= MODE_ID + 2) preferences.setBackgroundMode(id - MODE_ID);
            });
            list.addView(backgrounds, new LinearLayout.LayoutParams(-1, -2));

            section(list, "ANIMAÇÕES E ILUMINAÇÃO", "Escolha exatamente o que fica ativo");
            int[] effects = {StationGraphicsPreferences.LED, StationGraphicsPreferences.VIDEO, StationGraphicsPreferences.CLOUDS,
                    StationGraphicsPreferences.ICONS, StationGraphicsPreferences.CELL_EFFECTS, StationGraphicsPreferences.UI_TRANSITIONS};
            String[] labels = {"LEDs das capas", "Vídeos do carrossel", "Fundo animado", "Ícones e Lotties", "Efeitos das células", "Transições visuais"};
            String[] hints = {"Luzes e rastros de sistemas e jogos", "Vídeos de sistemas e coleções", "Movimento do céu ou das ondas", "Robô, estrelas e demais ícones", "Brilhos decorativos dos menus", "Entrada e troca de itens"};
            LinearLayout pair = null;
            for (int i = 0; i < effects.length; i++) {
                if (!wide || i % 2 == 0) { pair = new LinearLayout(owner); pair.setOrientation(HORIZONTAL); list.addView(pair, new LinearLayout.LayoutParams(-1, -2)); }
                LinearLayout option = option(effects[i], labels[i], hints[i]);
                LinearLayout.LayoutParams optionLayout = new LinearLayout.LayoutParams(wide ? 0 : -1, -2, wide ? 1 : 0);
                optionLayout.bottomMargin = dp(7); if (wide && i % 2 == 0) optionLayout.rightMargin = dp(8); pair.addView(option, optionLayout);
            }
            TextView foot = text("Desative os efeitos gerais para usar o mínimo gráfico. Ao reativar, suas escolhas individuais são restauradas.", 11, MUTED);
            foot.setPadding(dp(3), dp(2), dp(3), dp(3)); list.addView(foot);
            render(preferences.snapshot());
        }

        private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
        private LinearLayout vertical() { LinearLayout view = new LinearLayout(owner); view.setOrientation(VERTICAL); return view; }
        private TextView text(String value, int size, int color) {
            TextView text = new TextView(owner); text.setText(value); text.setTextSize(size); text.setTextColor(color);
            text.setGravity(Gravity.CENTER_VERTICAL); return text;
        }
        private GradientDrawable surface(int color, int stroke, int radius) {
            GradientDrawable drawable = new GradientDrawable(); drawable.setColor(color); drawable.setCornerRadius(dp(radius));
            drawable.setStroke(dp(1), stroke); return drawable;
        }
        private ColorStateList tint(int color) {
            return new ColorStateList(new int[][]{{android.R.attr.state_checked}, {}}, new int[]{color, 0xff577089});
        }
        private Switch toggle(String description) {
            Switch toggle = new Switch(owner); toggle.setShowText(false); toggle.setContentDescription(description);
            toggle.setThumbTintList(tint(ACTIVE)); toggle.setTrackTintList(tint(0xff2d806d)); toggle.setPadding(0, 0, 0, 0);
            return toggle;
        }
        private LinearLayout rowSurface(int color, int rim) {
            LinearLayout row = new LinearLayout(owner); row.setOrientation(HORIZONTAL); row.setGravity(Gravity.CENTER_VERTICAL);
            row.setPadding(dp(12), dp(8), dp(10), dp(8)); row.setBackground(surface(color, rim, 10)); return row;
        }
        private void section(LinearLayout list, String title, String hint) {
            LinearLayout row = new LinearLayout(owner); row.setGravity(Gravity.CENTER_VERTICAL); row.setPadding(dp(3), dp(11), dp(3), dp(6));
            TextView label = text(title, 10, ACCENT); label.setTypeface(null, Typeface.BOLD); label.setLetterSpacing(.08f); row.addView(label);
            if (wide) { TextView detail = text(hint, 11, MUTED); detail.setPadding(dp(12), 0, 0, 0); row.addView(detail); }
            list.addView(row);
        }
        private LinearLayout option(int effect, String label, String detail) {
            LinearLayout card = vertical(); card.setPadding(dp(12), dp(6), dp(10), dp(7)); card.setBackground(surface(0xff0f1d2d, 0xff253d51, 10));
            LinearLayout top = new LinearLayout(owner); top.setGravity(Gravity.CENTER_VERTICAL);
            TextView title = text(label, 13, WHITE); title.setTypeface(null, Typeface.BOLD); title.setMaxLines(2);
            top.addView(title, new LinearLayout.LayoutParams(0, dp(38), 1));
            Switch toggle = toggle(label); top.addView(toggle, new LinearLayout.LayoutParams(dp(44), dp(38))); card.addView(top);
            LinearLayout bottom = new LinearLayout(owner); bottom.setGravity(Gravity.CENTER_VERTICAL);
            TextView hint = text(detail, 10, MUTED); hint.setMaxLines(2); bottom.addView(hint, new LinearLayout.LayoutParams(0, -2, 1));
            TextView value = text("", 10, ACTIVE); value.setPadding(dp(5), 0, 0, 0); bottom.addView(value); card.addView(bottom);
            options.add(new Option(effect, toggle, value));
            toggle.setOnCheckedChangeListener((button, checked) -> { if (!updating) preferences.setEnabled(effect, checked); });
            card.setOnClickListener(v -> { if (toggle.isEnabled()) toggle.setChecked(!toggle.isChecked()); });
            return card;
        }
        private void render(StationGraphicsPreferences.State state) {
            updating = true;
            try {
                master.setChecked(!state.masterDisabled); masterValue.setText(state.masterDisabled ? "Desativado" : "Ativo");
                masterValue.setTextColor(state.masterDisabled ? MUTED : ACTIVE);
                int active = Integer.bitCount(state.effectiveMask());
                status.setText(state.masterDisabled ? "Modo de economia · animações interrompidas" : active + " de 6 opções ativas · escolhas salvas");
                for (Option option : options) {
                    boolean selected = (state.individualMask & option.effect) != 0;
                    option.toggle.setChecked(selected); option.toggle.setEnabled(!state.masterDisabled);
                    option.toggle.setAlpha(state.masterDisabled ? .4f : 1f);
                    option.value.setText(selected && !state.masterDisabled ? "Ativo" : "Desativado");
                    option.value.setTextColor(selected && !state.masterDisabled ? ACTIVE : MUTED);
                }
                backgrounds.check(MODE_ID + state.backgroundMode); backgrounds.setAlpha(state.masterDisabled ? .45f : 1f);
                for (int i = 0; i < backgrounds.getChildCount(); i++) {
                    RadioButton button = (RadioButton) backgrounds.getChildAt(i); button.setEnabled(!state.masterDisabled);
                    button.setTextColor(button.isChecked() ? ACTIVE : WHITE);
                }
            } finally { updating = false; }
        }
        @Override protected void onAttachedToWindow() {
            super.onAttachedToWindow(); if (!connected) { connected = true; preferences.addListener(this); } render(preferences.snapshot());
        }
        @Override protected void onDetachedFromWindow() { disconnect(); super.onDetachedFromWindow(); }
        void disconnect() { if (connected) { preferences.removeListener(this); connected = false; } }
        @Override public void onGraphicsChanged(StationGraphicsPreferences.State state) {
            owner.runOnUiThread(() -> { if (connected && !owner.isFinishing() && !owner.isDestroyed()) render(preferences.snapshot()); });
        }
    }
}