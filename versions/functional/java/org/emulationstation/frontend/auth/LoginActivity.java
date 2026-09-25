package org.emulationstation.frontend.auth;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
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
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Native Android entry screen, independent of SDL, themes and network connectivity. */
public final class LoginActivity extends Activity {
    private EditText password;
    private TextView status;
    private boolean opening;

    /** Called on every ESActivity resume, including Android restoring an old task. */
    public static void ensureAuthorized(Activity activity) {
        if (!AuthSession.isAuthorized()) {
            Intent login = new Intent(activity, LoginActivity.class);
            login.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            activity.startActivity(login);
        }
    }

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);
        getWindow().setStatusBarColor(Color.rgb(11, 16, 31));
        getWindow().setNavigationBarColor(Color.rgb(11, 16, 31));
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
                | WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
        if (AuthSession.isAuthorized()) {
            openFrontend();
            return;
        }

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackground(new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[] {Color.rgb(11, 16, 31), Color.rgb(27, 22, 53)}));
        LinearLayout outer = new LinearLayout(this);
        outer.setGravity(Gravity.CENTER);
        outer.setPadding(dp(24), dp(20), dp(24), dp(20));
        scroll.addView(outer, new ScrollView.LayoutParams(-1, -1));

        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(26), dp(22), dp(26), dp(22));
        card.setBackground(shape(Color.rgb(22, 29, 47), Color.rgb(56, 65, 89)));
        int width = Math.min(dp(480), getResources().getDisplayMetrics().widthPixels - dp(48));
        outer.addView(card, new LinearLayout.LayoutParams(width, -2));

        TextView tag = text("TURBORETRO  /  ACESSO LOCAL", 12, Color.rgb(105, 224, 222));
        tag.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        card.addView(tag);
        TextView title = text("Sua biblioteca. Seu jogo.", 26, Color.WHITE);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        add(card, title, 8);
        add(card, text("Digite a senha para entrar.", 15, Color.rgb(183, 192, 212)), 6);

        password = new EditText(this);
        password.setId(View.generateViewId());
        password.setHint("Senha de acesso");
        password.setContentDescription("Senha de acesso");
        password.setTextColor(Color.WHITE);
        password.setHintTextColor(Color.rgb(160, 172, 196));
        password.setTextSize(17);
        password.setSingleLine(true);
        password.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        password.setImeOptions(EditorInfo.IME_ACTION_GO | EditorInfo.IME_FLAG_NO_EXTRACT_UI);
        password.setFilters(new InputFilter[] {new InputFilter.LengthFilter(128)});
        password.setSaveEnabled(false);
        password.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO_EXCLUDE_DESCENDANTS);
        password.setPadding(dp(16), dp(12), dp(16), dp(12));
        password.setMinHeight(dp(52));
        StateListDrawable field = new StateListDrawable();
        field.addState(new int[] {android.R.attr.state_focused},
                shape(Color.rgb(12, 20, 36), Color.rgb(105, 224, 222)));
        field.addState(new int[] {}, shape(Color.rgb(12, 20, 36), Color.rgb(68, 78, 102)));
        password.setBackground(field);
        add(card, password, 18);

        Button enter = new Button(this);
        enter.setId(View.generateViewId());
        enter.setText("Entrar");
        enter.setAllCaps(false);
        enter.setTextSize(17);
        enter.setTextColor(Color.WHITE);
        enter.setMinHeight(dp(50));
        StateListDrawable button = new StateListDrawable();
        button.addState(new int[] {android.R.attr.state_pressed},
                shape(Color.rgb(95, 66, 185), Color.rgb(164, 141, 242)));
        button.addState(new int[] {android.R.attr.state_focused},
                shape(Color.rgb(119, 87, 222), Color.rgb(105, 224, 222)));
        button.addState(new int[] {}, shape(Color.rgb(112, 77, 213), Color.rgb(139, 110, 231)));
        enter.setBackground(button);
        add(card, enter, 12);
        password.setNextFocusDownId(enter.getId());
        enter.setNextFocusUpId(password.getId());

        status = text("", 13, Color.rgb(255, 157, 168));
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        add(card, status, 8);
        add(card, text("Acesso provisório neste aparelho. Servidor de login ainda não conectado.",
                12, Color.rgb(145, 159, 183)), 4);
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
        setContentView(scroll);
        password.requestFocus();
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
        // ESActivity is singleInstance in another task. Merely moving this task to the
        // back could expose restored ES, which would immediately reopen Login.
        // Go Home without finishing ES (its original onDestroy can kill this process).
        Intent home = new Intent(Intent.ACTION_MAIN);
        home.addCategory(Intent.CATEGORY_HOME);
        home.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(home);
    }

    private TextView text(String value, int size, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        return view;
    }

    private GradientDrawable shape(int fill, int stroke) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(fill);
        shape.setCornerRadius(dp(12));
        shape.setStroke(dp(2), stroke);
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
}
