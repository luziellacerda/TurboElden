package org.emulationstation.frontend.auth;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Bundle;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.InputStream;

/** Turborama branding. Authentication and frontend navigation remain the stable implementation. */
public final class LoginActivity extends Activity {
    private static final int BLACK = 0xff050907;
    private static final int GREEN = 0xff70fa45;
    private static final int WHITE = 0xfff2f7f3;
    private static final int MUTED = 0xff99ada1;
    private static final int RED = 0xfff04a55;
    private EditText password;
    private TextView status;
    private boolean opening;
    private Bitmap emblem;

    public static void ensureAuthorized(Activity activity) {
        AuthSession.attach(activity);
        if (!AuthSession.isAuthorized()) {
            Intent login = new Intent(activity, LoginActivity.class);
            login.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            activity.startActivity(login);
        }
    }

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        AuthSession.attach(this);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);
        getWindow().setStatusBarColor(BLACK);
        getWindow().setNavigationBarColor(BLACK);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
                | WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
        if (AuthSession.isAuthorized()) {
            openFrontend();
            return;
        }
        try (InputStream input = getAssets().open("turborama-brand/turborama-icon-master.png")) {
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inSampleSize = 2;
            emblem = BitmapFactory.decodeStream(input, null, options);
        } catch (java.io.IOException ignored) {
            // A text wordmark remains available even if an asset cannot be decoded.
        }
        buildScreen();
    }

    @Override public void onConfigurationChanged(Configuration configuration) {
        super.onConfigurationChanged(configuration);
        if (!opening && !AuthSession.isAuthorized()) {
            // Reflow on rotation or window-size changes without losing entered text.
            CharSequence entered = password == null ? "" : password.getText().toString();
            CharSequence message = status == null ? "" : status.getText();
            buildScreen();
            password.setText(entered);
            password.setSelection(password.length());
            status.setText(message);
        }
    }

    private void buildScreen() {
        final boolean wide = getResources().getConfiguration().screenWidthDp >= 650;
        final boolean compact = getResources().getConfiguration().screenHeightDp < 420;
        FrameLayout root = new FrameLayout(this);
        root.setFitsSystemWindows(true);
        root.setBackgroundColor(BLACK);
        root.addView(new HangarBackdrop(this), new FrameLayout.LayoutParams(-1, -1));

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);
        root.addView(scroll, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout page = column();
        page.setPadding(dp(wide ? 30 : 22), dp(compact ? 14 : 24), dp(wide ? 30 : 22), dp(16));
        scroll.addView(page, new ScrollView.LayoutParams(-1, -1));

        LinearLayout header = new LinearLayout(this);
        header.setGravity(Gravity.CENTER_VERTICAL);
        View accent = new View(this);
        accent.setBackgroundColor(RED);
        header.addView(accent, new LinearLayout.LayoutParams(dp(3), dp(22)));
        TextView brand = text("TURBORAMA", 16, WHITE);
        brand.setTypeface(Typeface.create("sans-serif-black", Typeface.NORMAL));
        brand.setLetterSpacing(0.13f);
        LinearLayout.LayoutParams wordmark = new LinearLayout.LayoutParams(0, -2, 1);
        wordmark.leftMargin = dp(12);
        header.addView(brand, wordmark);
        TextView tag = text("ACESSO LOCAL", 10, GREEN);
        tag.setLetterSpacing(0.14f);
        header.addView(tag);
        page.addView(header, new LinearLayout.LayoutParams(-1, dp(30)));

        LinearLayout main = new LinearLayout(this);
        main.setOrientation(wide ? LinearLayout.HORIZONTAL : LinearLayout.VERTICAL);
        main.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams mainParams = new LinearLayout.LayoutParams(-1, 0, 1);
        mainParams.topMargin = dp(compact ? 8 : 18);
        mainParams.bottomMargin = dp(12);
        page.addView(main, mainParams);

        LinearLayout identity = column();
        identity.setGravity(wide ? Gravity.CENTER_VERTICAL : Gravity.CENTER_HORIZONTAL);
        identity.setPadding(0, dp(8), dp(wide ? 28 : 0), dp(wide ? 8 : 20));
        if (wide) {
            ImageView mark = mark();
            identity.addView(mark, new LinearLayout.LayoutParams(dp(compact ? 56 : 140), dp(compact ? 56 : 140)));
            TextView eyebrow = text("SEU UNIVERSO DE JOGOS", 10, GREEN);
            eyebrow.setLetterSpacing(0.18f);
            add(identity, eyebrow, 9);
            TextView headline = text("O próximo jogo\ncomeça aqui.", compact ? 28 : 36, WHITE);
            headline.setTypeface(Typeface.create("sans-serif-black", Typeface.NORMAL));
            headline.setLineSpacing(dp(2), 1.0f);
            add(identity, headline, 8);
            add(identity, text("Clássicos, descobertas e novas aventuras.\nTudo na sua TurboramaStation.", 13, MUTED), 12);
            LinearLayout rails = new LinearLayout(this);
            View greenRail = new View(this);
            greenRail.setBackgroundColor(GREEN);
            rails.addView(greenRail, new LinearLayout.LayoutParams(dp(58), dp(3)));
            View redRail = new View(this);
            redRail.setBackgroundColor(RED);
            LinearLayout.LayoutParams smallRail = new LinearLayout.LayoutParams(dp(12), dp(3));
            smallRail.leftMargin = dp(5);
            rails.addView(redRail, smallRail);
            if (!compact) add(identity, rails, 20);
            main.addView(identity, new LinearLayout.LayoutParams(0, -2, 1));
        } else {
            identity.addView(mark(), new LinearLayout.LayoutParams(dp(84), dp(84)));
            TextView welcome = text("Seu universo de jogos.", 22, WHITE);
            welcome.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
            add(identity, welcome, 8);
            welcome.setGravity(Gravity.CENTER);
            main.addView(identity, new LinearLayout.LayoutParams(-1, -2));
        }

        LinearLayout card = column();
        card.setPadding(dp(24), dp(compact ? 20 : 28), dp(24), dp(compact ? 16 : 22));
        card.setBackground(shape(0xf50c1510, 0xff263e2e, 22));
        int cardWidth = wide ? dp(326) : Math.min(dp(420), getResources().getDisplayMetrics().widthPixels - dp(44));
        main.addView(card, new LinearLayout.LayoutParams(cardWidth, -2));

        TextView welcome = text("BEM-VINDO DE VOLTA", 10, GREEN);
        welcome.setLetterSpacing(0.15f);
        card.addView(welcome);
        TextView title = text("Entre no seu hangar.", 25, WHITE);
        title.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        add(card, title, 9);
        add(card, text("Sua biblioteca está esperando por você.", 12, MUTED), 6);
        TextView label = text("SENHA DE ACESSO", 10, MUTED);
        label.setLetterSpacing(0.1f);
        add(card, label, compact ? 18 : 24);

        password = new EditText(this);
        password.setId(View.generateViewId());
        label.setLabelFor(password.getId());
        password.setHint("Digite sua senha");
        password.setContentDescription("Senha de acesso");
        password.setTextColor(WHITE);
        password.setHintTextColor(0xff6f8577);
        password.setTextSize(16);
        password.setSingleLine(true);
        password.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        password.setImeOptions(EditorInfo.IME_ACTION_GO | EditorInfo.IME_FLAG_NO_EXTRACT_UI);
        password.setFilters(new InputFilter[] {new InputFilter.LengthFilter(128)});
        password.setSaveEnabled(false);
        password.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO_EXCLUDE_DESCENDANTS);
        password.setPadding(dp(16), dp(12), dp(16), dp(12));
        password.setMinHeight(dp(52));
        StateListDrawable field = new StateListDrawable();
        field.addState(new int[] {android.R.attr.state_focused}, shape(0xff070e0a, GREEN, 12));
        field.addState(new int[] {}, shape(0xff070e0a, 0xff304737, 12));
        password.setBackground(field);
        add(card, password, 8);

        Button enter = new Button(this);
        enter.setId(View.generateViewId());
        enter.setText("ENTRAR  →");
        enter.setAllCaps(false);
        enter.setContentDescription("Entrar na TurboramaStation");
        enter.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        enter.setLetterSpacing(0.06f);
        enter.setTextSize(14);
        enter.setTextColor(BLACK);
        enter.setMinHeight(dp(52));
        enter.setPadding(dp(12), dp(10), dp(12), dp(10));
        StateListDrawable button = new StateListDrawable();
        button.addState(new int[] {android.R.attr.state_pressed}, shape(0xff44c82c, WHITE, 12));
        button.addState(new int[] {android.R.attr.state_focused}, shape(GREEN, WHITE, 12));
        GradientDrawable normal = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,
                new int[] {0xff9cff43, 0xff39df5d});
        normal.setCornerRadius(dp(12));
        button.addState(new int[] {}, normal);
        enter.setBackground(button);
        add(card, enter, 14);
        password.setNextFocusDownId(enter.getId());
        enter.setNextFocusUpId(password.getId());
        status = text("", 12, 0xffff8d93);
        status.setMinHeight(dp(18));
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        add(card, status, 7);
        TextView local = text("Acesso local neste aparelho", 11, MUTED);
        local.setGravity(Gravity.CENTER);
        add(card, local, 3);
        TextView footer = text("TURBORAMA STATION     /     SUA BIBLIOTECA. SEU JOGO.", 9, 0xff617669);
        footer.setLetterSpacing(0.08f);
        page.addView(footer);

        enter.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { submit(); }
        });
        password.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override public boolean onEditorAction(TextView view, int action, KeyEvent event) {
                if (action == EditorInfo.IME_ACTION_GO || action == EditorInfo.IME_ACTION_DONE
                        || (event != null && event.getKeyCode() == KeyEvent.KEYCODE_ENTER
                        && event.getAction() == KeyEvent.ACTION_UP)) {
                    submit();
                    return true;
                }
                return false;
            }
        });
        setContentView(root);
        password.requestFocus();
    }

    private ImageView mark() {
        ImageView view = new ImageView(this);
        view.setImageBitmap(emblem);
        view.setScaleType(ImageView.ScaleType.FIT_CENTER);
        view.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        return view;
    }
    private LinearLayout column() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        return layout;
    }
    private TextView text(String value, int size, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        view.setIncludeFontPadding(false);
        return view;
    }
    private GradientDrawable shape(int fill, int stroke, int radius) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(fill);
        shape.setCornerRadius(dp(radius));
        shape.setStroke(dp(1), stroke);
        return shape;
    }
    private void add(LinearLayout parent, View view, int top) {
        LinearLayout.LayoutParams layout = new LinearLayout.LayoutParams(-1, -2);
        layout.topMargin = dp(top);
        parent.addView(view, layout);
    }
    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void submit() {
        if (opening) return;
        boolean accepted = AuthSession.authenticate(password.getText().toString());
        password.getText().clear();
        if (!accepted) {
            status.setText("Senha incorreta. Tente novamente.");
            password.requestFocus();
            return;
        }
        InputMethodManager keyboard = (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
        if (keyboard != null) keyboard.hideSoftInputFromWindow(password.getWindowToken(), 0);
        openFrontend();
    }
    private void openFrontend() {
        if (opening || !AuthSession.isAuthorized()) return;
        opening = true;
        Intent frontend = new Intent();
        frontend.setClassName(this, "org.emulationstation.frontend.ESActivity");
        frontend.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
        startActivity(frontend);
        finish();
    }
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        if (AuthSession.isAuthorized()) openFrontend();
    }
    @Override public void onBackPressed() {
        Intent home = new Intent(Intent.ACTION_MAIN);
        home.addCategory(Intent.CATEGORY_HOME);
        home.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(home);
    }

    /** Static artwork: no timers, rendering loop, 3D engine or work after leaving login. */
    private static final class HangarBackdrop extends View {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private Shader glow;
        HangarBackdrop(Context context) {
            super(context);
            setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        }
        @Override protected void onSizeChanged(int w, int h, int ow, int oh) {
            glow = new RadialGradient(w * 0.18f, h * 0.40f, Math.max(w, h) * 0.75f,
                    new int[] {0xff103c22, 0xff07110b, BLACK}, new float[] {0, 0.5f, 1}, Shader.TileMode.CLAMP);
        }
        @Override protected void onDraw(Canvas canvas) {
            paint.setShader(glow);
            canvas.drawRect(0, 0, getWidth(), getHeight(), paint);
            paint.setShader(null);
            paint.setStrokeWidth(getResources().getDisplayMetrics().density);
            paint.setColor(0x123eae5e);
            float horizon = getHeight() * 0.70f;
            for (int i = -4; i < 11; i++) {
                float end = getWidth() * i / 6.0f;
                canvas.drawLine(getWidth() * 0.25f, horizon, end, getHeight(), paint);
            }
            for (int i = 1; i <= 4; i++) {
                float y = horizon + (getHeight() - horizon) * i * i / 16.0f;
                canvas.drawLine(0, y, getWidth(), y, paint);
            }
        }
    }
}
