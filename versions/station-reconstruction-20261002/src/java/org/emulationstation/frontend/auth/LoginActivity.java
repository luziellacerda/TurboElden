package org.emulationstation.frontend.auth;

import android.R;
import org.emulationstation.frontend.station.StationApi;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Bundle;
import android.text.InputFilter;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.IOException;
import java.io.InputStream;

/* JADX INFO: loaded from: E:\ESTUDO APK\work\turbostations-reconstruction-20261002\input\classes8.dex */
public final class LoginActivity extends Activity {
    private static final int BLACK = -16447225;
    private static final int GREEN = -9373115;
    private static final int MUTED = -6705759;
    private static final int RED = -1029547;
    private static final int WHITE = -854029;
    private Bitmap emblem;
    private StationApi.Cancellation loginAttempt;
    private boolean authenticating;
    private TextView greeting;
    private boolean opening;
    private EditText password;
    private TextView status;
    private TextView welcome;

    private void openCommercial() {
        if (this.opening) {
            return;
        }
        this.opening = true;
        Intent intent = new Intent();
        intent.setClassName(this, "org.emulationstation.frontend.ESActivity");
        intent.addFlags(268566528);
        startActivity(intent);
        finish();
    }

    void commercialFail(String str) {
        authenticating=false;
        this.status.setText(str);
        this.password.setEnabled(true);
        this.password.requestFocus();
    }

    void commercialOk(String str) {
        String str2;
        if (this.opening) {
            return;
        }
        authenticating=false;
        welcomeName(str);
        if (str == null || str.isEmpty()) {
            str2 = "Bem-vindo";
        } else {
            str2 = "Bem-vindo, " + str;
        }
        this.status.setText(str2);
        openCommercial();
    }

    void welcomeName(String str) {
        TextView textView;
        if (str == null || str.isEmpty() || (textView = this.welcome) == null) {
            return;
        }
        String str2 = "Bem-vindo, " + str;
        textView.setLetterSpacing(0.0f);
        textView.setText(str2);
        TextView textView2 = this.greeting;
        if (textView2 != null) {
            textView2.setText(str2);
        }
    }

    public static void ensureAuthorized(Activity activity) {
        StationLogin.ensureAuthorized(activity);
    }

    @Override // android.app.Activity
    protected void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        requestWindowFeature(1);
        getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_SECURE);
        getWindow().setStatusBarColor(BLACK);
        getWindow().setNavigationBarColor(BLACK);
        getWindow().setSoftInputMode(19);
        if (StationLogin.ready()) {
            openFrontend();
            return;
        }
        try {
            InputStream inputStreamOpen = getAssets().open("turborama-brand/turborama-icon-master.png");
            try {
                BitmapFactory.Options options = new BitmapFactory.Options();
                options.inSampleSize = 2;
                this.emblem = BitmapFactory.decodeStream(inputStreamOpen, null, options);
                if (inputStreamOpen != null) {
                    inputStreamOpen.close();
                }
            } catch (Throwable th) {
                if (inputStreamOpen != null) {
                    try {
                        inputStreamOpen.close();
                    } catch (Throwable th2) {
                        th.addSuppressed(th2);
                    }
                }
                throw th;
            }
        } catch (IOException e) {
        }
        buildScreen();
        if(StationLogin.hasLicense(this))submit();
    }

    @Override // android.app.Activity, android.content.ComponentCallbacks
    public void onConfigurationChanged(Configuration configuration) {
        super.onConfigurationChanged(configuration);
        if (!this.opening && !StationLogin.ready()) {
            String string = this.password == null ? "" : this.password.getText().toString();
            CharSequence text = this.status != null ? this.status.getText() : "";
            buildScreen();
            this.password.setText(string);
            this.password.setSelection(this.password.length());
            this.status.setText(text);
            this.password.setEnabled(!authenticating);
        }
    }

    private void buildScreen() {
        int i;
        int i2 = getResources().getConfiguration().screenWidthDp >= 650 ? 1 : 0;
        boolean z = getResources().getConfiguration().screenHeightDp < 420;
        FrameLayout frameLayout = new FrameLayout(this);
        frameLayout.setFitsSystemWindows(true);
        frameLayout.setBackgroundColor(BLACK);
        frameLayout.addView(new HangarBackdrop(this), new FrameLayout.LayoutParams(-1, -1));
        ScrollView scrollView = new ScrollView(this);
        scrollView.setFillViewport(true);
        scrollView.setClipToPadding(false);
        frameLayout.addView(scrollView, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout linearLayoutColumn = column();
        linearLayoutColumn.setPadding(dp(i2 != 0 ? 30 : 22), dp(z ? 14 : 24), dp(i2 != 0 ? 30 : 22), dp(16));
        scrollView.addView(linearLayoutColumn, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout linearLayout = new LinearLayout(this);
        linearLayout.setGravity(16);
        View view = new View(this);
        view.setBackgroundColor(RED);
        linearLayout.addView(view, new LinearLayout.LayoutParams(dp(3), dp(22)));
        TextView textViewText = text("TURBORAMA", 16, WHITE);
        textViewText.setTypeface(Typeface.create("sans-serif-black", 0));
        textViewText.setLetterSpacing(0.13f);
        LinearLayout.LayoutParams layoutParams = new LinearLayout.LayoutParams(0, -2, 1.0f);
        layoutParams.leftMargin = dp(12);
        linearLayout.addView(textViewText, layoutParams);
        TextView textViewText2 = text("ACESSO STATION", 10, GREEN);
        textViewText2.setLetterSpacing(0.14f);
        linearLayout.addView(textViewText2);
        linearLayoutColumn.addView(linearLayout, new LinearLayout.LayoutParams(-1, dp(30)));
        LinearLayout linearLayout2 = new LinearLayout(this);
        linearLayout2.setOrientation(i2 ^ 1);
        linearLayout2.setGravity(17);
        LinearLayout.LayoutParams layoutParams2 = new LinearLayout.LayoutParams(-1, 0, 1.0f);
        layoutParams2.topMargin = dp(z ? 8 : 18);
        layoutParams2.bottomMargin = dp(12);
        linearLayoutColumn.addView(linearLayout2, layoutParams2);
        LinearLayout linearLayoutColumn2 = column();
        linearLayoutColumn2.setGravity(i2 != 0 ? 16 : 1);
        linearLayoutColumn2.setPadding(0, dp(8), dp(i2 != 0 ? 28 : 0), dp(i2 != 0 ? 8 : 20));
        if (i2 != 0) {
            linearLayoutColumn2.addView(mark(), new LinearLayout.LayoutParams(dp(z ? 56 : 140), dp(z ? 56 : 140)));
            TextView textViewText3 = text("SEU UNIVERSO DE JOGOS", 10, GREEN);
            textViewText3.setLetterSpacing(0.18f);
            add(linearLayoutColumn2, textViewText3, 9);
            TextView textViewText4 = text("O próximo jogo\ncomeça aqui.", z ? 28 : 36, WHITE);
            textViewText4.setTypeface(Typeface.create("sans-serif-black", 0));
            textViewText4.setLineSpacing(dp(2), 1.0f);
            add(linearLayoutColumn2, textViewText4, 8);
            add(linearLayoutColumn2, text("Clássicos, descobertas e novas aventuras.\nTudo na sua TurboramaStation.", 13, MUTED), 12);
            LinearLayout linearLayout3 = new LinearLayout(this);
            View view2 = new View(this);
            view2.setBackgroundColor(GREEN);
            linearLayout3.addView(view2, new LinearLayout.LayoutParams(dp(58), dp(3)));
            View view3 = new View(this);
            view3.setBackgroundColor(RED);
            LinearLayout.LayoutParams layoutParams3 = new LinearLayout.LayoutParams(dp(12), dp(3));
            layoutParams3.leftMargin = dp(5);
            linearLayout3.addView(view3, layoutParams3);
            if (z) {
                i = 20;
            } else {
                i = 20;
                add(linearLayoutColumn2, linearLayout3, 20);
            }
            linearLayout2.addView(linearLayoutColumn2, new LinearLayout.LayoutParams(0, -2, 1.0f));
        } else {
            i = 20;
            linearLayoutColumn2.addView(mark(), new LinearLayout.LayoutParams(dp(84), dp(84)));
            TextView textViewText5 = text("Seu universo de jogos.", 22, WHITE);
            textViewText5.setTypeface(Typeface.create("sans-serif-medium", 0));
            add(linearLayoutColumn2, textViewText5, 8);
            textViewText5.setGravity(17);
            linearLayout2.addView(linearLayoutColumn2, new LinearLayout.LayoutParams(-1, -2));
        }
        LinearLayout linearLayoutColumn3 = column();
        int iDp = dp(24);
        if (!z) {
            i = 28;
        }
        linearLayoutColumn3.setPadding(iDp, dp(i), dp(24), dp(z ? 16 : 22));
        linearLayoutColumn3.setBackground(shape(-183757552, -14270930, 22));
        linearLayout2.addView(linearLayoutColumn3, new LinearLayout.LayoutParams(i2 != 0 ? dp(326) : Math.min(dp(420), getResources().getDisplayMetrics().widthPixels - dp(44)), -2));
        TextView textViewText6 = text("BEM-VINDO DE VOLTA", 10, GREEN);
        textViewText6.setLetterSpacing(0.15f);
        linearLayoutColumn3.addView(textViewText6);
        this.welcome = textViewText6;
        welcomeName(StationLogin.displayName());
        TextView textViewText7 = text("Entre no seu hangar.", 25, WHITE);
        textViewText7.setTypeface(Typeface.create("sans-serif-medium", 0));
        this.greeting = textViewText7;
        welcomeName(StationLogin.displayName());
        add(linearLayoutColumn3, textViewText7, 9);
        add(linearLayoutColumn3, text("Sua biblioteca está esperando por você.", 12, MUTED), 6);
        TextView textViewText8 = text("SENHA DE ACESSO", 10, MUTED);
        textViewText8.setLetterSpacing(0.1f);
        add(linearLayoutColumn3, textViewText8, z ? 18 : 24);
        this.password = new EditText(this);
        this.password.setId(View.generateViewId());
        textViewText8.setLabelFor(this.password.getId());
        this.password.setHint("Digite sua senha");
        this.password.setContentDescription("Senha de acesso");
        this.password.setTextColor(WHITE);
        this.password.setHintTextColor(-9468553);
        this.password.setTextSize(16.0f);
        this.password.setSingleLine(true);
        this.password.setInputType(129);
        this.password.setImeOptions(268435458);
        this.password.setFilters(new InputFilter[]{new InputFilter.LengthFilter(128)});
        this.password.setSaveEnabled(false);
        this.password.setImportantForAutofill(8);
        this.password.setPadding(dp(16), dp(12), dp(16), dp(12));
        this.password.setMinHeight(dp(52));
        StateListDrawable stateListDrawable = new StateListDrawable();
        stateListDrawable.addState(new int[]{R.attr.state_focused}, shape(-16314870, GREEN, 12));
        stateListDrawable.addState(new int[0], shape(-16314870, -13613257, 12));
        this.password.setBackground(stateListDrawable);
        add(linearLayoutColumn3, this.password, 8);
        Button button = new Button(this);
        button.setId(View.generateViewId());
        button.setText("ENTRAR  →");
        button.setAllCaps(false);
        button.setContentDescription("Entrar na TurboramaStation");
        button.setTypeface(Typeface.create("sans-serif-medium", 0));
        button.setLetterSpacing(0.06f);
        button.setTextSize(14.0f);
        button.setTextColor(BLACK);
        button.setMinHeight(dp(52));
        button.setPadding(dp(12), dp(10), dp(12), dp(10));
        StateListDrawable stateListDrawable2 = new StateListDrawable();
        stateListDrawable2.addState(new int[]{R.attr.state_pressed}, shape(-12269524, WHITE, 12));
        stateListDrawable2.addState(new int[]{R.attr.state_focused}, shape(GREEN, WHITE, 12));
        GradientDrawable gradientDrawable = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{-6488253, -12984483});
        gradientDrawable.setCornerRadius(dp(12));
        stateListDrawable2.addState(new int[0], gradientDrawable);
        button.setBackground(stateListDrawable2);
        add(linearLayoutColumn3, button, 14);
        this.password.setNextFocusDownId(button.getId());
        button.setNextFocusUpId(this.password.getId());
        this.status = text("", 12, -29293);
        this.status.setMinHeight(dp(18));
        this.status.setAccessibilityLiveRegion(1);
        add(linearLayoutColumn3, this.status, 7);
        TextView textViewText9 = text("Use o acesso vinculado à sua compra", 11, MUTED);
        textViewText9.setGravity(17);
        add(linearLayoutColumn3, textViewText9, 3);
        TextView textViewText10 = text("TURBORAMA STATION     /     SUA BIBLIOTECA. SEU JOGO.", 9, -10389911);
        textViewText10.setLetterSpacing(0.08f);
        linearLayoutColumn.addView(textViewText10);
        button.setOnClickListener(new View.OnClickListener() { // from class: org.emulationstation.frontend.auth.LoginActivity.1
            @Override // android.view.View.OnClickListener
            public void onClick(View view4) {
                LoginActivity.this.submit();
            }
        });
        this.password.setOnEditorActionListener(new TextView.OnEditorActionListener() { // from class: org.emulationstation.frontend.auth.LoginActivity.2
            @Override // android.widget.TextView.OnEditorActionListener
            public boolean onEditorAction(TextView textView, int i3, KeyEvent keyEvent) {
                if (i3 == 2 || i3 == 6 || (keyEvent != null && keyEvent.getKeyCode() == 66 && keyEvent.getAction() == 1)) {
                    LoginActivity.this.submit();
                    return true;
                }
                return false;
            }
        });
        setContentView(frameLayout);
        this.password.requestFocus();
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void submit() {
        if (opening || authenticating) return;
        String code=password.getText().toString().trim();
        if(code.isEmpty() && !StationLogin.hasLicense(this)) {
            status.setText("Informe o código recebido após a compra.");return;
        }
        password.getText().clear();password.setEnabled(false);authenticating=true;
        status.setText("Conferindo acesso...");
        loginAttempt=StationLogin.begin(this,code,new StationLogin.Callback(){
            public void ok(String name){commercialOk(name);}
            public void fail(String message){commercialFail(message);}
        });
    }

    private void openFrontend() {
        if (this.opening || !StationLogin.ready()) {
            return;
        }
        this.opening = true;
        Intent intent = new Intent();
        intent.setClassName(this, "org.emulationstation.frontend.ESActivity");
        intent.addFlags(268566528);
        startActivity(intent);
        finish();
    }

    @Override // android.app.Activity
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        if (intent.getBooleanExtra("stationLogin", false) || !StationLogin.ready()) {
            return;
        }
        openFrontend();
    }

    @Override // android.app.Activity
    public void onBackPressed() {
        Intent intent = new Intent("android.intent.action.MAIN");
        intent.addCategory("android.intent.category.HOME");
        intent.addFlags(268435456);
        startActivity(intent);
    }

    private ImageView mark() {
        ImageView imageView = new ImageView(this);
        imageView.setImageBitmap(this.emblem);
        imageView.setScaleType(ImageView.ScaleType.FIT_CENTER);
        imageView.setImportantForAccessibility(2);
        return imageView;
    }

    private LinearLayout column() {
        LinearLayout linearLayout = new LinearLayout(this);
        linearLayout.setOrientation(1);
        return linearLayout;
    }

    private TextView text(String str, int i, int i2) {
        TextView textView = new TextView(this);
        textView.setText(str);
        textView.setTextSize(i);
        textView.setTextColor(i2);
        textView.setIncludeFontPadding(false);
        return textView;
    }

    private GradientDrawable shape(int i, int i2, int i3) {
        GradientDrawable gradientDrawable = new GradientDrawable();
        gradientDrawable.setColor(i);
        gradientDrawable.setCornerRadius(dp(i3));
        gradientDrawable.setStroke(dp(1), i2);
        return gradientDrawable;
    }

    private void add(LinearLayout linearLayout, View view, int i) {
        LinearLayout.LayoutParams layoutParams = new LinearLayout.LayoutParams(-1, -2);
        layoutParams.topMargin = dp(i);
        linearLayout.addView(view, layoutParams);
    }

    private int dp(int i) {
        return Math.round(i * getResources().getDisplayMetrics().density);
    }

    private static final class HangarBackdrop extends View {
        private Shader glow;
        private final Paint paint;

        HangarBackdrop(Context context) {
            super(context);
            this.paint = new Paint(1);
            setImportantForAccessibility(2);
        }

        @Override // android.view.View
        protected void onSizeChanged(int i, int i2, int i3, int i4) {
            this.glow = new RadialGradient(i * 0.18f, i2 * 0.4f, Math.max(i, i2) * 0.75f, new int[]{-15713246, -16314101, LoginActivity.BLACK}, new float[]{0.0f, 0.5f, 1.0f}, Shader.TileMode.CLAMP);
        }

        @Override // android.view.View
        protected void onDraw(Canvas canvas) {
            this.paint.setShader(this.glow);
            canvas.drawRect(0.0f, 0.0f, getWidth(), getHeight(), this.paint);
            this.paint.setShader(null);
            this.paint.setStrokeWidth(getResources().getDisplayMetrics().density);
            this.paint.setColor(306097758);
            float height = getHeight() * 0.7f;
            for (int i = -4; i < 11; i++) {
                canvas.drawLine(0.25f * getWidth(), height, (getWidth() * i) / 6.0f, getHeight(), this.paint);
            }
            for (int i2 = 1; i2 <= 4; i2++) {
                float f = i2;
                float height2 = height + ((((getHeight() - height) * f) * f) / 16.0f);
                canvas.drawLine(0.0f, height2, getWidth(), height2, this.paint);
            }
        }
    }
    @Override protected void onStop() {
        if(!opening && loginAttempt!=null && authenticating) {
            loginAttempt.cancel();authenticating=false;
            if(password!=null)password.setEnabled(true);
            if(status!=null)status.setText("Consulta pausada. Toque em Entrar para continuar.");
        }
        super.onStop();
    }
    @Override protected void onDestroy() {
        if(loginAttempt!=null)loginAttempt.cancel();
        if(emblem!=null){emblem.recycle();emblem=null;}
        super.onDestroy();
    }

}
