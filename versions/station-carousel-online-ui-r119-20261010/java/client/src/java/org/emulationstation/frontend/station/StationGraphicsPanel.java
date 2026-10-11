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
        final int effect; final String label; final Switch toggle; final TextView value;
        Option(int effect, String label, Switch toggle, TextView value) { this.effect = effect; this.label = label; this.toggle = toggle; this.value = value; }
    }
    private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener {
        private static final int WHITE = 0xffeef6ff, MUTED = 0xff9bb0c5, ACCENT = 0xff78d7ed, ACTIVE = 0xff8bdedc;
        private static final int MODE_ID = 0x118100;
        private final Activity owner;
        private final StationGraphicsPreferences preferences;
        private final ArrayList<Option> options = new ArrayList<>();
        private final Switch master;
        private final TextView status, masterValue, backgroundHint;
        private final RadioGroup backgrounds;
        private final boolean wide;
        private boolean connected, updating;

        Content(Activity owner, Runnable close) {
            super(owner);
            this.owner = owner;
            preferences = StationGraphicsPreferences.get(owner);
            android.util.DisplayMetrics display = getResources().getDisplayMetrics();
            wide = display.widthPixels > display.heightPixels && display.widthPixels / display.density >= 620;
            setOrientation(VERTICAL);
            setPadding(dp(wide ? 24 : 16), dp(12), dp(wide ? 24 : 16), dp(8));
            setBackground(new GradientDrawable(GradientDrawable.Orientation.TL_BR, new int[]{0xff060d19, 0xff102338}));

            LinearLayout header = new LinearLayout(owner); header.setGravity(Gravity.CENTER_VERTICAL);
            LinearLayout titles = vertical();
            TextView eyebrow = text("CONFIGURAÇÕES  /  VISUAL", 10, ACCENT); eyebrow.setLetterSpacing(.08f); titles.addView(eyebrow);
            TextView title = text("Efeitos gráficos", 22, WHITE); title.setTypeface(null, Typeface.BOLD); titles.addView(title);
            header.addView(titles, new LinearLayout.LayoutParams(0, dp(48), 1));
            TextView back = text("‹  VOLTAR", 12, WHITE); back.setTypeface(null, Typeface.BOLD); back.setGravity(Gravity.CENTER);
            back.setPadding(dp(16), 0, dp(16), 0); back.setMinWidth(dp(96)); back.setBackground(surface(0xff172b41, 0xff355168, 10));
            back.setFocusable(true); back.setContentDescription("Voltar às configurações");
            back.setOnClickListener(v -> { if (close != null) close.run(); });
            header.addView(back, new LinearLayout.LayoutParams(-2, dp(48))); addView(header);
            View rule = new View(owner); rule.setBackgroundColor(0xff2b475e);
            LinearLayout.LayoutParams ruleLayout = new LinearLayout.LayoutParams(-1, dp(1)); ruleLayout.topMargin = dp(8); addView(rule, ruleLayout);

            ScrollView scroll = new ScrollView(owner); scroll.setFillViewport(true); scroll.setOverScrollMode(View.OVER_SCROLL_NEVER);
            scroll.setClipToPadding(false);
            LinearLayout body = new LinearLayout(owner); body.setOrientation(wide ? HORIZONTAL : VERTICAL); body.setPadding(0, dp(8), 0, dp(4));
            scroll.addView(body, new ScrollView.LayoutParams(-1, -2)); addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
            LinearLayout left = vertical(), right = vertical();
            if (wide) {
                LinearLayout.LayoutParams side = new LinearLayout.LayoutParams(0, -2, .42f); side.rightMargin = dp(12); body.addView(left, side);
                body.addView(right, new LinearLayout.LayoutParams(0, -2, .58f));
            } else { body.addView(left, new LinearLayout.LayoutParams(-1, -2)); body.addView(right, new LinearLayout.LayoutParams(-1, -2)); }

            section(left, "CONTROLE GERAL");
            LinearLayout masterRow = rowSurface(0xff153246, 0xff3d7180);
            LinearLayout masterCopy = vertical();
            TextView masterTitle = text("Efeitos gerais", 15, WHITE); masterTitle.setTypeface(null, Typeface.BOLD); masterCopy.addView(masterTitle);
            status = text("", 11, MUTED); status.setMaxLines(2); masterCopy.addView(status);
            masterRow.addView(masterCopy, new LinearLayout.LayoutParams(0, -2, 1));
            masterValue = text("", 11, ACTIVE); masterValue.setSingleLine(true); masterValue.setPadding(dp(6), 0, dp(6), 0); masterRow.addView(masterValue);
            master = toggle("Efeitos gerais"); masterRow.addView(master, new LinearLayout.LayoutParams(dp(52), dp(48))); left.addView(masterRow);
            master.setOnCheckedChangeListener((button, checked) -> { if (!updating) preferences.setMasterDisabled(!checked); });
            masterRow.setOnClickListener(v -> master.setChecked(!master.isChecked()));

            section(left, "FUNDO");
            LinearLayout backgroundCard = vertical(); backgroundCard.setPadding(dp(6), dp(6), dp(6), dp(4)); backgroundCard.setBackground(surface(0xff10263a, 0xff2d4d63, 10));
            backgrounds = new RadioGroup(owner); backgrounds.setOrientation(HORIZONTAL);
            int[] modes = {StationGraphicsPreferences.WAVES, StationGraphicsPreferences.SKY, StationGraphicsPreferences.OFF};
            String[] names = {"Ondas", "Céu", "Sem fundo"};
            for (int i = 0; i < modes.length; i++) {
                RadioButton button = new RadioButton(owner); button.setId(MODE_ID + modes[i]); button.setText(names[i]);
                button.setTextSize(12); button.setTextColor(WHITE); button.setGravity(Gravity.CENTER); button.setButtonDrawable(new ColorDrawable(android.graphics.Color.TRANSPARENT));
                button.setPadding(dp(2), 0, dp(2), 0); button.setSingleLine(true); button.setContentDescription("Fundo " + names[i]);
                RadioGroup.LayoutParams itemLayout = new RadioGroup.LayoutParams(0, dp(48), 1); itemLayout.setMargins(dp(2), 0, dp(2), 0);
                backgrounds.addView(button, itemLayout);
            }
            backgrounds.setOnCheckedChangeListener((group, id) -> { if (!updating && id >= MODE_ID && id <= MODE_ID + 2) preferences.setBackgroundMode(id - MODE_ID); });
            backgroundCard.addView(backgrounds, new LinearLayout.LayoutParams(-1, -2));
            backgroundCard.addView(option(StationGraphicsPreferences.CLOUDS, "Animar o fundo", "Movimento do céu ou das ondas", false));
            backgroundHint = text("", 11, MUTED); backgroundHint.setPadding(dp(6), dp(2), dp(6), dp(4)); backgroundHint.setMaxLines(2); backgroundCard.addView(backgroundHint);
            left.addView(backgroundCard);
            TextView economy = text("Ao desligar os efeitos gerais, tudo fica parado. Suas escolhas voltam quando você reativar.", 11, MUTED);
            economy.setPadding(dp(3), dp(9), dp(3), 0); left.addView(economy);

            section(right, "CAPAS E MÍDIA");
            addOption(right, StationGraphicsPreferences.LED, "LEDs das capas", "Luzes e rastros de sistemas e jogos");
            addOption(right, StationGraphicsPreferences.VIDEO, "Vídeos do carrossel", "Vídeos de sistemas e coleções");
            section(right, "INTERFACE");
            addOption(right, StationGraphicsPreferences.ICONS, "Ícones e Lotties", "Robô, estrelas e demais ícones");
            addOption(right, StationGraphicsPreferences.CELL_EFFECTS, "Efeitos das células", "Brilhos decorativos dos menus");
            addOption(right, StationGraphicsPreferences.UI_TRANSITIONS, "Transições visuais", "Entrada e troca de itens");
            TextView foot = text("Escolhas salvas automaticamente", 10, MUTED); foot.setGravity(Gravity.RIGHT); foot.setPadding(0, dp(4), 0, 0); addView(foot);
            render(preferences.snapshot());
        }

        private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
        private LinearLayout vertical() { LinearLayout view = new LinearLayout(owner); view.setOrientation(VERTICAL); return view; }
        private TextView text(String value, int size, int color) {
            TextView text = new TextView(owner); text.setText(value); text.setTextSize(size); text.setTextColor(color); text.setGravity(Gravity.CENTER_VERTICAL); return text;
        }
        private GradientDrawable surface(int color, int stroke, int radius) {
            GradientDrawable drawable = new GradientDrawable(); drawable.setColor(color); drawable.setCornerRadius(dp(radius)); drawable.setStroke(dp(1), stroke); return drawable;
        }
        private ColorStateList tint(int color) { return new ColorStateList(new int[][]{{android.R.attr.state_checked}, {}}, new int[]{color, 0xff58758e}); }
        private Switch toggle(String description) {
            Switch toggle = new Switch(owner); toggle.setShowText(false); toggle.setContentDescription(description);
            toggle.setThumbTintList(tint(ACTIVE)); toggle.setTrackTintList(tint(0xff367585)); toggle.setPadding(0, 0, 0, 0); toggle.setMinHeight(dp(48)); return toggle;
        }
        private LinearLayout rowSurface(int color, int rim) {
            LinearLayout row = new LinearLayout(owner); row.setOrientation(HORIZONTAL); row.setGravity(Gravity.CENTER_VERTICAL);
            row.setPadding(dp(12), dp(6), dp(8), dp(6)); row.setBackground(surface(color, rim, 10)); return row;
        }
        private void section(LinearLayout list, String title) {
            TextView label = text(title, 10, ACCENT); label.setTypeface(null, Typeface.BOLD); label.setLetterSpacing(.09f); label.setPadding(dp(3), dp(7), 0, dp(5)); list.addView(label);
        }
        private void addOption(LinearLayout list, int effect, String label, String detail) {
            LinearLayout.LayoutParams layout = new LinearLayout.LayoutParams(-1, -2); layout.bottomMargin = dp(5); list.addView(option(effect, label, detail, true), layout);
        }
        private LinearLayout option(int effect, String label, String detail, boolean card) {
            LinearLayout row = new LinearLayout(owner); row.setGravity(Gravity.CENTER_VERTICAL); row.setPadding(dp(card ? 12 : 6), dp(2), dp(6), dp(2)); row.setMinimumHeight(dp(52));
            if (card) row.setBackground(surface(0xff10283c, 0xff2c4c62, 10));
            LinearLayout copy = vertical(); TextView title = text(label, 13, WHITE); title.setTypeface(null, Typeface.BOLD); title.setMaxLines(2); copy.addView(title);
            TextView hint = text(detail, 10, MUTED); hint.setSingleLine(true); hint.setEllipsize(android.text.TextUtils.TruncateAt.END); copy.addView(hint);
            row.addView(copy, new LinearLayout.LayoutParams(0, -2, 1));
            TextView value = text("", 10, ACTIVE); value.setSingleLine(true); value.setPadding(dp(5), 0, dp(6), 0); row.addView(value);
            Switch toggle = toggle(label); row.addView(toggle, new LinearLayout.LayoutParams(dp(52), dp(48))); options.add(new Option(effect, label, toggle, value));
            toggle.setOnCheckedChangeListener((button, checked) -> { if (!updating) preferences.setEnabled(effect, checked); });
            row.setOnClickListener(v -> { if (toggle.isEnabled()) toggle.setChecked(!toggle.isChecked()); }); return row;
        }
        private void render(StationGraphicsPreferences.State state) {
            updating = true;
            try {
                master.setChecked(!state.masterDisabled); masterValue.setText(state.masterDisabled ? "Economia" : "Ativos"); masterValue.setTextColor(state.masterDisabled ? MUTED : ACTIVE);
                int active = Integer.bitCount(state.effectiveMask()); if (!state.backgroundAllowed() && state.isEnabled(StationGraphicsPreferences.CLOUDS)) active--;
                status.setText(state.masterDisabled ? "Animações interrompidas" : active + " de 6 efeitos em uso");
                for (Option option : options) {
                    boolean chosen = (state.individualMask & option.effect) != 0;
                    boolean running = chosen && !state.masterDisabled && (option.effect != StationGraphicsPreferences.CLOUDS || state.backgroundAllowed());
                    option.toggle.setChecked(chosen); option.toggle.setEnabled(!state.masterDisabled); option.toggle.setAlpha(state.masterDisabled ? .4f : 1f);
                    option.value.setText(state.masterDisabled ? "Economia" : option.effect == StationGraphicsPreferences.CLOUDS && state.backgroundMode == StationGraphicsPreferences.OFF ? "Sem fundo" : running ? "Ativo" : "Desativado");
                    option.value.setTextColor(running ? ACTIVE : MUTED); option.toggle.setContentDescription(option.label + ", " + option.value.getText());
                }
                backgrounds.check(MODE_ID + state.backgroundMode); backgrounds.setAlpha(state.masterDisabled ? .45f : 1f);
                for (int i = 0; i < backgrounds.getChildCount(); i++) {
                    RadioButton button = (RadioButton) backgrounds.getChildAt(i); boolean checked = button.isChecked(); button.setEnabled(!state.masterDisabled);
                    button.setTextColor(checked ? WHITE : MUTED); button.setTypeface(null, checked ? Typeface.BOLD : Typeface.NORMAL);
                    button.setBackground(surface(checked ? 0xff24536a : 0xff142b3e, checked ? 0xff5fb2c6 : 0xff263f54, 8));
                }
                backgroundHint.setText(state.masterDisabled ? "Fundo interrompido pelo modo de economia." : state.backgroundMode == StationGraphicsPreferences.OFF ? "Sem fundo animado; a escolha dos outros efeitos continua salva." : !state.backgroundAllowed() ? "O estilo está salvo. Ative Animar o fundo para mostrar seu movimento." : state.backgroundMode == StationGraphicsPreferences.WAVES ? "Ondas suaves no fundo dos menus." : "Céu com a cor escolhida nas configurações.");
            } finally { updating = false; }
        }
        @Override protected void onAttachedToWindow() { super.onAttachedToWindow(); if (!connected) { connected = true; preferences.addListener(this); } render(preferences.snapshot()); }
        @Override protected void onDetachedFromWindow() { disconnect(); super.onDetachedFromWindow(); }
        void disconnect() { if (connected) { preferences.removeListener(this); connected = false; } }
        @Override public void onGraphicsChanged(StationGraphicsPreferences.State state) { owner.runOnUiThread(() -> { if (connected && !owner.isFinishing() && !owner.isDestroyed()) render(preferences.snapshot()); }); }
    }
}
