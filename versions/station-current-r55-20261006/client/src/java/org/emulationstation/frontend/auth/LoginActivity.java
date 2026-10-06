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
import android.widget.CheckBox;
import android.content.res.ColorStateList;
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
    private boolean storagePermissionPending;
    private static final int STORAGE_REQUEST = 8251;
    private EditText password;
    private CheckBox rememberAccess;
    private TextView status;
    private TextView welcome;

    private void openCommercial() {
        openFrontend();
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
        if (StationLogin.ready() && storageAllowed()) {
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
        if(StationLogin.ready())openFrontend();
        else if(StationLogin.hasLicense(this)&&StationLogin.rememberAccess(this))submit();
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
        FrameLayout root = new FrameLayout(this);
        root.setFitsSystemWindows(true);
        root.setBackgroundColor(BLACK);
        root.addView(new HangarBackdrop(this), new FrameLayout.LayoutParams(-1, -1));

        LinearLayout brand = column();
        brand.setGravity(android.view.Gravity.CENTER_VERTICAL);
        ImageView brandMark = mark();
        brand.addView(brandMark, new LinearLayout.LayoutParams(dp(72), dp(72)));
        LinearLayout brandCopy = column();
        TextView brandEyebrow = text("ACESSO STATION", 10, GREEN);
        brandEyebrow.setLetterSpacing(0.12f);
        brandCopy.addView(brandEyebrow);
        TextView brandTitle = text("TURBORAMA\nSTATION", 24, WHITE);
        brandTitle.setTypeface(Typeface.create("sans-serif-black", 0));
        brandTitle.setLetterSpacing(0.04f);
        add(brandCopy, brandTitle, 5);
        TextView brandTagline = text("Seu universo de jogos.", 13, MUTED);
        add(brandCopy, brandTagline, 8);
        brand.addView(brandCopy, new LinearLayout.LayoutParams(-1, -2));

        LinearLayout form = column();
        this.welcome = text("BEM-VINDO DE VOLTA", 10, GREEN);
        this.welcome.setLetterSpacing(0.12f);
        form.addView(this.welcome);
        this.greeting = text("Entre no seu hangar.", 22, WHITE);
        this.greeting.setTypeface(Typeface.create("sans-serif-medium", 0));
        add(form, this.greeting, 4);
        welcomeName(StationLogin.displayName());

        TextView accessLabel = text("SENHA DE ACESSO", 10, MUTED);
        accessLabel.setLetterSpacing(0.1f);
        add(form, accessLabel, 12);
        this.password = new EditText(this);
        this.password.setId(View.generateViewId());
        accessLabel.setLabelFor(this.password.getId());
        this.password.setHint(StationLogin.hasLicense(this)?"Acesso salvo. Toque em Entrar":"Digite sua senha");
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
        StateListDrawable passwordBackground = new StateListDrawable();
        passwordBackground.addState(new int[]{R.attr.state_focused}, shape(-16314870, GREEN, 12));
        passwordBackground.addState(new int[0], shape(-16314870, -13613257, 12));
        this.password.setBackground(passwordBackground);
        add(form, this.password, 6);

        this.rememberAccess = new CheckBox(this);
        this.rememberAccess.setId(View.generateViewId());
        this.rememberAccess.setText("Manter conectado");
        this.rememberAccess.setContentDescription("Salvar acesso neste aparelho e entrar automaticamente");
        this.rememberAccess.setTextColor(WHITE);
        this.rememberAccess.setTextSize(13);
        this.rememberAccess.setButtonTintList(ColorStateList.valueOf(GREEN));
        this.rememberAccess.setMinHeight(dp(48));
        this.rememberAccess.setChecked(StationLogin.rememberAccess(this));
        this.rememberAccess.setOnCheckedChangeListener((checkbox,checked)->StationLogin.rememberAccess(this,checked));
        add(form, this.rememberAccess, 0);

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
        StateListDrawable buttonBackground = new StateListDrawable();
        buttonBackground.addState(new int[]{R.attr.state_pressed}, shape(-12269524, WHITE, 12));
        buttonBackground.addState(new int[]{R.attr.state_focused}, shape(GREEN, WHITE, 12));
        GradientDrawable gradient = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{-6488253, -12984483});
        gradient.setCornerRadius(dp(12));
        buttonBackground.addState(new int[0], gradient);
        button.setBackground(buttonBackground);
        add(form, button, 6);
        this.password.setNextFocusDownId(this.rememberAccess.getId());
        this.rememberAccess.setNextFocusUpId(this.password.getId());
        this.rememberAccess.setNextFocusDownId(button.getId());
        button.setNextFocusUpId(this.rememberAccess.getId());

        this.status = text("", 12, -29293);
        this.status.setMinHeight(dp(18));
        this.status.setAccessibilityLiveRegion(1);
        add(form, this.status, 4);
        TextView purchaseNote = text("Use o acesso vinculado à sua compra", 11, MUTED);
        add(form, purchaseNote, 4);

        ScrollView formScroll = new ScrollView(this);
        formScroll.setFillViewport(false);
        formScroll.setClipToPadding(false);
        formScroll.setOverScrollMode(View.OVER_SCROLL_IF_CONTENT_SCROLLS);
        formScroll.setVerticalScrollBarEnabled(true);
        formScroll.addView(form, new FrameLayout.LayoutParams(-1, -2));
        root.addView(new LoginPanel(brand, brandMark, brandCopy, brandTitle, brandTagline, formScroll),
                new FrameLayout.LayoutParams(-1, -1));

        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                LoginActivity.this.submit();
            }
        });
        this.password.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView textView, int action, KeyEvent keyEvent) {
                if (action == 2 || action == 6 || (keyEvent != null && keyEvent.getKeyCode() == 66 && keyEvent.getAction() == 1)) {
                    LoginActivity.this.submit();
                    return true;
                }
                return false;
            }
        });
        setContentView(root);
        this.password.requestFocus();
    }

    /** Measures the same input views again when bars, the keyboard or the window change size. */
    private final class LoginPanel extends android.view.ViewGroup {
        private final LinearLayout brand;
        private final ImageView brandMark;
        private final LinearLayout brandCopy;
        private final TextView brandTitle;
        private final TextView brandTagline;
        private final ScrollView formScroll;
        private final GradientDrawable panelBackground = shape(-183757552, -14270930, 22);
        private int outer;
        private int inset;
        private int gap;
        private int contentHeight;
        private boolean sideBySide;
        private boolean brandVisible;
        private int presentation = -1;

        LoginPanel(LinearLayout brand, ImageView brandMark, LinearLayout brandCopy,
                TextView brandTitle, TextView brandTagline, ScrollView formScroll) {
            super(LoginActivity.this);
            this.brand = brand;
            this.brandMark = brandMark;
            this.brandCopy = brandCopy;
            this.brandTitle = brandTitle;
            this.brandTagline = brandTagline;
            this.formScroll = formScroll;
            setWillNotDraw(false);
            addView(brand, new android.view.ViewGroup.LayoutParams(-2, -2));
            addView(formScroll, new android.view.ViewGroup.LayoutParams(-1, -2));
        }

        @Override
        protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
            int width = MeasureSpec.getSize(widthMeasureSpec);
            int height = MeasureSpec.getSize(heightMeasureSpec);
            outer = Math.min(dp(height < dp(420) ? 10 : 20), Math.min(width, height) / 8);
            int padding = dp(height < dp(300) ? 12 : 20);
            inset = Math.min(outer + padding, Math.min(width, height) / 4);
            int availableWidth = Math.max(1, width - 2 * inset);
            int availableHeight = Math.max(1, height - 2 * inset);
            sideBySide = availableWidth >= dp(480) && width > height;
            brandVisible = availableHeight >= dp(150);
            boolean compactBrand = availableHeight < dp(260);
            int nextPresentation = (sideBySide ? 1 : 0) | (brandVisible ? 2 : 0)
                    | (compactBrand ? 4 : 0);
            if (nextPresentation != presentation) {
                presentation = nextPresentation;
                brand.setVisibility(brandVisible ? View.VISIBLE : View.GONE);
                brand.setOrientation(sideBySide ? LinearLayout.VERTICAL : LinearLayout.HORIZONTAL);
                brandMark.setVisibility(compactBrand && sideBySide ? View.GONE : View.VISIBLE);
                brandTagline.setVisibility(compactBrand || !sideBySide ? View.GONE : View.VISIBLE);
                brandTitle.setTextSize(sideBySide ? 24 : 18);
                int markSize = dp(sideBySide ? 72 : 48);
                brandMark.setLayoutParams(new LinearLayout.LayoutParams(markSize, markSize));
                LinearLayout.LayoutParams copyParams = new LinearLayout.LayoutParams(
                        sideBySide ? -1 : 0, -2, sideBySide ? 0.0f : 1.0f);
                copyParams.topMargin = dp(sideBySide && !compactBrand ? 12 : 0);
                copyParams.leftMargin = dp(sideBySide ? 0 : 12);
                brandCopy.setLayoutParams(copyParams);
            }
            gap = brandVisible ? dp(sideBySide ? 24 : 12) : 0;
            int formWidth = availableWidth;
            int formHeight = availableHeight;
            if (brandVisible) {
                int brandWidth = sideBySide
                        ? Math.min(dp(280), Math.max(dp(140), availableWidth * 30 / 100))
                        : availableWidth;
                int brandHeightLimit = sideBySide ? availableHeight
                        : Math.min(dp(84), Math.max(dp(48), availableHeight / 3));
                brand.measure(MeasureSpec.makeMeasureSpec(brandWidth, MeasureSpec.EXACTLY),
                        MeasureSpec.makeMeasureSpec(brandHeightLimit, MeasureSpec.AT_MOST));
                if (sideBySide) formWidth = Math.max(1, availableWidth - brandWidth - gap);
                else formHeight = Math.max(1, availableHeight - brand.getMeasuredHeight() - gap);
            }
            formScroll.measure(MeasureSpec.makeMeasureSpec(formWidth, MeasureSpec.EXACTLY),
                    MeasureSpec.makeMeasureSpec(formHeight, MeasureSpec.AT_MOST));
            contentHeight = formScroll.getMeasuredHeight();
            if (brandVisible && !sideBySide) contentHeight += brand.getMeasuredHeight() + gap;
            setMeasuredDimension(width, height);
        }

        @Override
        protected void onLayout(boolean changed, int left, int top, int right, int bottom) {
            int availableHeight = Math.max(1, getMeasuredHeight() - 2 * inset);
            int formLeft = inset;
            int formTop = inset + Math.max(0, (availableHeight - contentHeight) / 2);
            if (brandVisible) {
                int brandTop = sideBySide
                        ? inset + Math.max(0, (availableHeight - brand.getMeasuredHeight()) / 2)
                        : formTop;
                brand.layout(inset, brandTop, inset + brand.getMeasuredWidth(),
                        brandTop + brand.getMeasuredHeight());
                if (sideBySide) formLeft += brand.getMeasuredWidth() + gap;
                else formTop += brand.getMeasuredHeight() + gap;
            }
            formScroll.layout(formLeft, formTop, formLeft + formScroll.getMeasuredWidth(),
                    formTop + formScroll.getMeasuredHeight());
        }

        @Override
        protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            panelBackground.setBounds(outer, outer, getWidth() - outer, getHeight() - outer);
            panelBackground.draw(canvas);
        }
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void submit() {
        if (opening || authenticating) return;
        if(StationLogin.ready()){openFrontend();return;}
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
        if(!storageAllowed()){
            if(status!=null)status.setText("Permita o acesso aos arquivos para preparar suas pastas e abrir a biblioteca.");
            if(password!=null)password.setEnabled(true);
            if(storagePermissionPending)return;
            storagePermissionPending=true;
            try{
                if(android.os.Build.VERSION.SDK_INT>=30){
                    Intent settings=new Intent(android.provider.Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION,
                        android.net.Uri.parse("package:"+getPackageName()));
                    startActivityForResult(settings,STORAGE_REQUEST);
                }else requestPermissions(new String[]{android.Manifest.permission.WRITE_EXTERNAL_STORAGE},STORAGE_REQUEST);
            }catch(android.content.ActivityNotFoundException absent){
                storagePermissionPending=false;
                if(status!=null)status.setText("Abra as configurações do Android e permita o acesso aos arquivos deste aplicativo. Depois toque em Entrar.");
            }
            return;
        }
        this.opening = true;
        Intent intent = new Intent();
        intent.setClassName(this, "org.emulationstation.frontend.ESActivity");
        intent.addFlags(268566528);
        startActivity(intent);
        finish();
    }

    private boolean storageAllowed(){
        return android.os.Build.VERSION.SDK_INT>=30?android.os.Environment.isExternalStorageManager():
            checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)==android.content.pm.PackageManager.PERMISSION_GRANTED;
    }
    private void storageReturned(){
        storagePermissionPending=false;
        if(storageAllowed()){
            if(StationLogin.ready())openFrontend();
            else if(StationLogin.hasLicense(this))submit();
        }else if(status!=null)status.setText("O acesso aos arquivos ainda não foi permitido. Toque em Entrar para tentar novamente.");
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(request==STORAGE_REQUEST)storageReturned();
    }
    @Override public void onRequestPermissionsResult(int request,String[] permissions,int[] results){
        super.onRequestPermissionsResult(request,permissions,results);if(request==STORAGE_REQUEST)storageReturned();
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
