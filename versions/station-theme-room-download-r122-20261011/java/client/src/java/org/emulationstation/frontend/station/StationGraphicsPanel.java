package org.emulationstation.frontend.station;

import android.app.Activity;
import android.app.Application;
import android.app.Dialog;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
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
        getWindow().setBackgroundDrawable(new ColorDrawable(0xff06080d));
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

    /** A single flat console surface. Geometry is rebuilt only when its bounds change. */
    private static final class ConsoleSurface extends android.graphics.drawable.Drawable {
        private final android.graphics.Paint paint = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
        private final android.graphics.Path outline = new android.graphics.Path();
        private final int fill, rim, rail;
        private final float density;
        private int alpha=255;
        ConsoleSurface(int fill, int rim, int rail, float density) { this.fill = fill; this.rim = rim; this.rail = rail; this.density = density; }
        @Override protected void onBoundsChange(android.graphics.Rect bounds) {
            float inset = density, cut = Math.min(5 * density, bounds.height() * .15f);
            float l = bounds.left + inset, t = bounds.top + inset, r = bounds.right - inset, b = bounds.bottom - inset;
            outline.reset(); outline.moveTo(l, t); outline.lineTo(r - cut, t); outline.lineTo(r, t + cut);
            outline.lineTo(r, b); outline.lineTo(l + cut, b); outline.lineTo(l, b - cut); outline.close();
        }
        @Override public void draw(android.graphics.Canvas canvas) {
            paint.setStyle(android.graphics.Paint.Style.FILL); paint.setColor(fill); paint.setAlpha(alpha); canvas.drawPath(outline, paint);
            paint.setStyle(android.graphics.Paint.Style.STROKE); paint.setStrokeWidth(density * 1.5f); paint.setColor(rim); paint.setAlpha(alpha); canvas.drawPath(outline, paint);
            if (rail != 0) { android.graphics.Rect b = getBounds(); paint.setStyle(android.graphics.Paint.Style.FILL); paint.setColor(rail);
                paint.setAlpha(alpha); canvas.drawRect(b.left + density * 2, b.top + density * 8, b.left + density * 5, b.bottom - density * 8, paint); }
        }
        @Override public void setAlpha(int alpha) { if(this.alpha!=alpha){this.alpha=alpha;invalidateSelf();} }
        @Override public void setColorFilter(android.graphics.ColorFilter filter) { paint.setColorFilter(filter); }
        @Override public int getOpacity() { return android.graphics.PixelFormat.TRANSLUCENT; }
    }
    /** Small code-drawn marks; they have no animator, bitmap or refresh callback. */
    private static final class ConsoleMark extends android.graphics.drawable.Drawable {
        private final android.graphics.Paint paint = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
        private final android.graphics.Path shape = new android.graphics.Path();
        private final int kind, color, size;
        private int alpha=255;
        ConsoleMark(int kind, int color, int size) { this.kind = kind; this.color = color; this.size = size; setBounds(0, 0, size, size); }
        @Override protected void onBoundsChange(android.graphics.Rect b) {
            shape.reset(); float x = b.left, y = b.top, s = Math.min(b.width(), b.height()) / 24f;
            if (kind == StationGraphicsPreferences.VIDEO) {
                shape.moveTo(x + 7*s, y + 4*s); shape.lineTo(x + 20*s, y + 12*s); shape.lineTo(x + 7*s, y + 20*s); shape.close();
            } else if (kind == StationGraphicsPreferences.LED) {
                for (int side = 0; side < 2; side++) { float px = x + (side == 0 ? 5 : 19)*s; shape.moveTo(px,y+3*s); shape.lineTo(px,y+21*s); }
                shape.moveTo(x+9*s,y+5*s); shape.lineTo(x+15*s,y+5*s); shape.moveTo(x+9*s,y+19*s); shape.lineTo(x+15*s,y+19*s);
            } else if (kind == StationGraphicsPreferences.ICONS) {
                shape.addRect(x+4*s,y+6*s,x+20*s,y+20*s,android.graphics.Path.Direction.CW);
                shape.moveTo(x+12*s,y+2*s); shape.lineTo(x+12*s,y+6*s); shape.moveTo(x+8*s,y+11*s); shape.lineTo(x+8*s,y+14*s);
                shape.moveTo(x+16*s,y+11*s); shape.lineTo(x+16*s,y+14*s); shape.moveTo(x+9*s,y+17*s); shape.lineTo(x+15*s,y+17*s);
            } else if (kind == StationGraphicsPreferences.CELL_EFFECTS) {
                shape.addRect(x+4*s,y+4*s,x+20*s,y+20*s,android.graphics.Path.Direction.CW);
                shape.moveTo(x+9*s,y+12*s); shape.lineTo(x+15*s,y+12*s); shape.moveTo(x+12*s,y+9*s); shape.lineTo(x+12*s,y+15*s);
            } else if (kind == 101 || kind == StationGraphicsPreferences.CLOUDS) {
                shape.moveTo(x+2*s,y+10*s); shape.cubicTo(x+6*s,y+3*s,x+11*s,y+17*s,x+16*s,y+10*s); shape.lineTo(x+22*s,y+10*s);
                shape.moveTo(x+2*s,y+16*s); shape.cubicTo(x+6*s,y+9*s,x+11*s,y+23*s,x+16*s,y+16*s); shape.lineTo(x+22*s,y+16*s);
            } else if (kind == 100) {
                shape.moveTo(x+5*s,y+18*s); shape.cubicTo(x-1*s,y+13*s,x+5*s,y+7*s,x+9*s,y+10*s);
                shape.cubicTo(x+10*s,y+2*s,x+21*s,y+4*s,x+20*s,y+12*s); shape.cubicTo(x+25*s,y+12*s,x+24*s,y+18*s,x+20*s,y+18*s); shape.close();
            } else if (kind == 102) {
                shape.addRect(x+4*s,y+4*s,x+20*s,y+20*s,android.graphics.Path.Direction.CW); shape.moveTo(x+5*s,y+19*s); shape.lineTo(x+19*s,y+5*s);
            } else {
                shape.moveTo(x+3*s,y+7*s); shape.lineTo(x+20*s,y+7*s); shape.lineTo(x+16*s,y+3*s);
                shape.moveTo(x+21*s,y+17*s); shape.lineTo(x+4*s,y+17*s); shape.lineTo(x+8*s,y+21*s);
            }
        }
        @Override public void draw(android.graphics.Canvas canvas) {
            paint.setColor(color); paint.setAlpha(alpha); paint.setStrokeWidth(Math.max(1, size/14f)); paint.setStrokeJoin(android.graphics.Paint.Join.ROUND);
            paint.setStyle(kind == StationGraphicsPreferences.VIDEO ? android.graphics.Paint.Style.FILL : android.graphics.Paint.Style.STROKE); canvas.drawPath(shape,paint);
        }
        @Override public void setAlpha(int alpha) { if(this.alpha!=alpha){this.alpha=alpha;invalidateSelf();} }
        @Override public void setColorFilter(android.graphics.ColorFilter filter) { paint.setColorFilter(filter); }
        @Override public int getOpacity() { return android.graphics.PixelFormat.TRANSLUCENT; }
        @Override public int getIntrinsicWidth() { return size; }
        @Override public int getIntrinsicHeight() { return size; }
    }
    private static final class Option {
        final int effect; final String label; final Switch toggle; final TextView value; final LinearLayout surface;
        Option(int effect,String label,Switch toggle,TextView value,LinearLayout surface) { this.effect=effect;this.label=label;this.toggle=toggle;this.value=value;this.surface=surface; }
    }
    private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener {
        private static final int WHITE=0xffeff5ff, MUTED=0xff9eaabc, ACCENT=0xff46dbff, ACTIVE=0xff78deaf;
        private static final int BASE=0xff06080d, SURFACE=0xff151f2e, LINE=0xff334153, PRIMARY=0xff244eb3;
        private static final int MODE_ID=0x118100;
        private final Activity owner;
        private final StationGraphicsPreferences preferences;
        private final ArrayList<Option> options=new ArrayList<>();
        private final Switch master;
        private final TextView status,masterValue,backgroundHint;
        private final LinearLayout masterSurface;
        private final RadioGroup backgrounds;
        private final boolean wide;
        private boolean connected,updating;

        Content(Activity owner,Runnable close) {
            super(owner);this.owner=owner;preferences=StationGraphicsPreferences.get(owner);
            android.util.DisplayMetrics display=getResources().getDisplayMetrics();
            wide=display.widthPixels>display.heightPixels&&display.widthPixels/display.density>=620;
            setOrientation(VERTICAL);setDescendantFocusability(FOCUS_AFTER_DESCENDANTS);
            setPadding(dp(wide?22:14),dp(10),dp(wide?22:14),dp(8));setBackgroundColor(BASE);
            LinearLayout header=row();LinearLayout titles=vertical();
            TextView eyebrow=text("TURBOSTATIONS  /  CONFIGURAÇÕES",9,ACCENT);eyebrow.setLetterSpacing(.08f);titles.addView(eyebrow);
            TextView title=text("EFEITOS GRÁFICOS",22,WHITE);title.setTypeface(null,Typeface.BOLD);titles.addView(title);
            header.addView(titles,new LinearLayout.LayoutParams(0,dp(48),1));
            TextView back=text("‹  VOLTAR",12,WHITE);back.setTypeface(null,Typeface.BOLD);back.setGravity(Gravity.CENTER);back.setMinWidth(dp(96));
            back.setPadding(dp(14),0,dp(14),0);back.setBackground(states(false));back.setFocusable(true);back.setContentDescription("Voltar às configurações");
            back.setOnClickListener(v->{if(close!=null)close.run();});header.addView(back,new LinearLayout.LayoutParams(-2,dp(48)));addView(header);
            View line=new View(owner);line.setBackgroundColor(LINE);LinearLayout.LayoutParams lineSize=new LinearLayout.LayoutParams(-1,dp(1));lineSize.topMargin=dp(6);addView(line,lineSize);

            ScrollView scroll=new ScrollView(owner);scroll.setFillViewport(true);scroll.setFocusable(false);scroll.setOverScrollMode(View.OVER_SCROLL_NEVER);scroll.setClipToPadding(false);
            LinearLayout body=vertical();body.setPadding(0,dp(8),0,dp(6));scroll.addView(body,new ScrollView.LayoutParams(-1,-2));addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
            masterSurface=row();masterSurface.setPadding(dp(12),dp(3),dp(8),dp(3));masterSurface.setMinimumHeight(dp(52));masterSurface.setBackground(states(true));masterSurface.setFocusable(false);
            LinearLayout masterCopy=vertical();TextView masterTitle=text("VISUAL DOS MENUS",13,WHITE);masterTitle.setTypeface(null,Typeface.BOLD);masterCopy.addView(masterTitle);
            status=text("",10,MUTED);status.setMaxLines(2);masterCopy.addView(status);masterSurface.addView(masterCopy,new LinearLayout.LayoutParams(0,-2,1));
            masterValue=text("",11,ACCENT);masterValue.setSingleLine(true);masterValue.setTypeface(null,Typeface.BOLD);masterValue.setPadding(dp(6),0,dp(10),0);masterSurface.addView(masterValue);
            master=toggle("Efeitos gerais");masterSurface.addView(master,new LinearLayout.LayoutParams(dp(52),dp(48)));focusSurface(master,masterSurface);
            body.addView(masterSurface,new LinearLayout.LayoutParams(-1,-2));
            master.setOnCheckedChangeListener((button,checked)->{if(!updating)preferences.setMasterDisabled(!checked);});
            masterSurface.setOnClickListener(v->master.setChecked(!master.isChecked()));

            LinearLayout columns=new LinearLayout(owner);columns.setOrientation(wide?HORIZONTAL:VERTICAL);LinearLayout.LayoutParams columnsSize=new LinearLayout.LayoutParams(-1,-2);columnsSize.topMargin=dp(6);body.addView(columns,columnsSize);
            LinearLayout left=vertical(),right=vertical();
            if(wide){LinearLayout.LayoutParams side=new LinearLayout.LayoutParams(0,-2,.36f);side.rightMargin=dp(16);columns.addView(left,side);columns.addView(right,new LinearLayout.LayoutParams(0,-2,.64f));}
            else{columns.addView(left,new LinearLayout.LayoutParams(-1,-2));columns.addView(right,new LinearLayout.LayoutParams(-1,-2));}
            section(left,"AMBIENTE");
            backgrounds=new RadioGroup(owner);backgrounds.setOrientation(HORIZONTAL);
            int[] modes={StationGraphicsPreferences.WAVES,StationGraphicsPreferences.SKY,StationGraphicsPreferences.OFF};String[] names={"Ondas","Céu","Desligado"};
            for(int i=0;i<modes.length;i++){
                RadioButton button=new RadioButton(owner);button.setId(MODE_ID+modes[i]);button.setText(names[i]);button.setTextSize(11);button.setTextColor(WHITE);button.setGravity(Gravity.CENTER);
                button.setButtonDrawable(new ColorDrawable(android.graphics.Color.TRANSPARENT));button.setBackground(states(false));button.setFocusable(true);
                button.setCompoundDrawablesWithIntrinsicBounds(null,new ConsoleMark(100+modes[i],ACCENT,dp(21)),null,null);button.setCompoundDrawablePadding(dp(2));
                button.setPadding(dp(4),dp(5),dp(4),dp(3));button.setSingleLine(true);button.setContentDescription("Fundo "+names[i]);
                RadioGroup.LayoutParams slot=new RadioGroup.LayoutParams(0,dp(64),1);slot.setMargins(i==0?0:dp(5),0,0,0);backgrounds.addView(button,slot);
            }
            backgrounds.setOnCheckedChangeListener((group,id)->{if(!updating&&id>=MODE_ID&&id<=MODE_ID+2)preferences.setBackgroundMode(id-MODE_ID);});
            left.addView(backgrounds,new LinearLayout.LayoutParams(-1,-2));
            LinearLayout.LayoutParams motionSize=new LinearLayout.LayoutParams(-1,-2);motionSize.topMargin=dp(6);
            left.addView(option(StationGraphicsPreferences.CLOUDS,"Movimento do fundo","Ondas ou nuvens"),motionSize);
            backgroundHint=text("",10,MUTED);backgroundHint.setPadding(dp(2),dp(6),dp(2),0);backgroundHint.setMaxLines(3);left.addView(backgroundHint);

            section(right,"PERSONALIZAR O VISUAL");
            int[] effects={StationGraphicsPreferences.LED,StationGraphicsPreferences.VIDEO,StationGraphicsPreferences.ICONS,StationGraphicsPreferences.CELL_EFFECTS,StationGraphicsPreferences.UI_TRANSITIONS};
            String[] labels={"LEDs das capas","Vídeos do carrossel","Ícones e Lotties","Efeitos das células","Transições"};
            String[] hints={"Luzes e rastros","Sistemas e coleções","Robô e estrelas","Brilhos dos menus","Entrada e troca de itens"};
            LinearLayout gridRow=null;
            for(int i=0;i<effects.length;i++){
                if(!wide||i%2==0){gridRow=row();gridRow.setGravity(Gravity.TOP);LinearLayout.LayoutParams groupSize=new LinearLayout.LayoutParams(-1,-2);groupSize.bottomMargin=dp(6);right.addView(gridRow,groupSize);}
                LinearLayout card=option(effects[i],labels[i],hints[i]);
                LinearLayout.LayoutParams cardSize=wide?new LinearLayout.LayoutParams(0,-2,1):new LinearLayout.LayoutParams(-1,-2);if(wide&&i%2==1)cardSize.leftMargin=dp(8);gridRow.addView(card,cardSize);
                if(wide&&i==effects.length-1){View spacer=new View(owner);LinearLayout.LayoutParams spare=new LinearLayout.LayoutParams(0,1,1);spare.leftMargin=dp(8);gridRow.addView(spacer,spare);}
            }
            TextView economy=text("ECONOMIA pausa as animações e mantém suas escolhas salvas.",10,MUTED);economy.setPadding(0,dp(4),0,0);body.addView(economy);
            TextView foot=text("Salvo automaticamente",9,MUTED);foot.setGravity(Gravity.RIGHT);foot.setPadding(0,dp(2),0,0);addView(foot);
            render(preferences.snapshot());
        }

        private int dp(float value){return Math.round(value*getResources().getDisplayMetrics().density);}
        private LinearLayout vertical(){LinearLayout view=new LinearLayout(owner);view.setOrientation(VERTICAL);return view;}
        private LinearLayout row(){LinearLayout view=new LinearLayout(owner);view.setOrientation(HORIZONTAL);view.setGravity(Gravity.CENTER_VERTICAL);return view;}
        private TextView text(String value,int size,int color){TextView view=new TextView(owner);view.setText(value);view.setTextSize(size);view.setTextColor(color);view.setGravity(Gravity.CENTER_VERTICAL);return view;}
        private android.graphics.drawable.StateListDrawable states(boolean primary){
            float density=getResources().getDisplayMetrics().density;android.graphics.drawable.StateListDrawable states=new android.graphics.drawable.StateListDrawable();
            states.addState(new int[]{-android.R.attr.state_enabled,android.R.attr.state_checked},new ConsoleSurface(0xff101620,LINE,0xff315766,density));
            states.addState(new int[]{-android.R.attr.state_enabled,android.R.attr.state_selected},new ConsoleSurface(0xff101620,LINE,0xff315766,density));
            states.addState(new int[]{-android.R.attr.state_enabled},new ConsoleSurface(0xff101620,0xff25303e,0,density));
            states.addState(new int[]{android.R.attr.state_pressed},new ConsoleSurface(0xff3262c8,WHITE,ACCENT,density));
            states.addState(new int[]{android.R.attr.state_focused},new ConsoleSurface(PRIMARY,WHITE,ACCENT,density));
            states.addState(new int[]{android.R.attr.state_activated},new ConsoleSurface(PRIMARY,WHITE,ACCENT,density));
            states.addState(new int[]{android.R.attr.state_checked},new ConsoleSurface(0xff14283f,0xff3c728e,ACCENT,density));
            states.addState(new int[]{android.R.attr.state_selected},new ConsoleSurface(0xff14283f,0xff3c728e,ACCENT,density));
            states.addState(new int[]{},new ConsoleSurface(primary?0xff142038:SURFACE,LINE,primary?ACCENT:0,density));return states;
        }
        private ColorStateList tint(int active,int idle){return new ColorStateList(new int[][]{{-android.R.attr.state_enabled},{android.R.attr.state_checked},{}},new int[]{0xff475262,active,idle});}
        private Switch toggle(String description){
            Switch view=new Switch(owner);view.setShowText(false);view.setContentDescription(description);view.setFocusable(true);
            view.setThumbTintList(tint(WHITE,0xffa9b4c4));view.setTrackTintList(tint(0xff287c99,0xff414c5a));view.setBackground(new ColorDrawable(android.graphics.Color.TRANSPARENT));
            view.setPadding(0,0,0,0);view.setMinHeight(dp(48));return view;
        }
        private void focusSurface(View target,View surface){target.setOnFocusChangeListener((view,focus)->surface.setActivated(focus));}
        private void section(LinearLayout list,String title){
            TextView label=text(title,10,ACCENT);label.setTypeface(null,Typeface.BOLD);label.setLetterSpacing(.08f);label.setPadding(dp(2),dp(6),0,dp(5));list.addView(label);
        }
        private LinearLayout option(int effect,String label,String detail){
            LinearLayout card=row();card.setPadding(dp(10),dp(6),dp(7),dp(6));card.setMinimumHeight(dp(68));card.setBackground(states(false));card.setFocusable(false);
            LinearLayout copy=vertical();TextView title=text(label,13,WHITE);title.setTypeface(null,Typeface.BOLD);title.setMaxLines(2);title.setEllipsize(android.text.TextUtils.TruncateAt.END);
            title.setCompoundDrawablesWithIntrinsicBounds(new ConsoleMark(effect,ACCENT,dp(16)),null,null,null);title.setCompoundDrawablePadding(dp(6));copy.addView(title);
            TextView hint=text(detail,9,MUTED);hint.setSingleLine(true);hint.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(hint);
            TextView value=text("",10,ACTIVE);value.setSingleLine(true);value.setTypeface(null,Typeface.BOLD);copy.addView(value);
            card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));Switch toggle=toggle(label);LinearLayout.LayoutParams switchSize=new LinearLayout.LayoutParams(dp(52),dp(48));switchSize.leftMargin=dp(5);card.addView(toggle,switchSize);
            Option option=new Option(effect,label,toggle,value,card);options.add(option);focusSurface(toggle,card);
            toggle.setOnCheckedChangeListener((button,checked)->{if(!updating)preferences.setEnabled(effect,checked);});
            card.setOnClickListener(v->{if(toggle.isEnabled())toggle.setChecked(!toggle.isChecked());});return card;
        }
        private void render(StationGraphicsPreferences.State state){
            updating=true;
            try{
                master.setChecked(!state.masterDisabled);masterSurface.setSelected(!state.masterDisabled);masterValue.setText(state.masterDisabled?"ECONOMIA":"ATIVO");masterValue.setTextColor(state.masterDisabled?MUTED:ACCENT);
                int active=Integer.bitCount(state.effectiveMask());if(!state.backgroundAllowed()&&state.isEnabled(StationGraphicsPreferences.CLOUDS))active--;
                status.setText(state.masterDisabled?"Tudo parado · escolhas preservadas":active+" de 6 opções ativadas");
                master.setContentDescription("Efeitos gerais, "+(state.masterDisabled?"economia":"ativos"));
                for(Option option:options){
                    boolean chosen=(state.individualMask&option.effect)!=0;
                    boolean enabled=chosen&&!state.masterDisabled&&(option.effect!=StationGraphicsPreferences.CLOUDS||state.backgroundAllowed());
                    option.toggle.setChecked(chosen);option.toggle.setEnabled(!state.masterDisabled);option.surface.setEnabled(!state.masterDisabled);option.surface.setSelected(chosen);
                    option.value.setText(state.masterDisabled?"PAUSADO":option.effect==StationGraphicsPreferences.CLOUDS&&state.backgroundMode==StationGraphicsPreferences.OFF?"SEM FUNDO":enabled?"ATIVO":"DESATIVADO");
                    option.value.setTextColor(enabled?ACTIVE:MUTED);option.toggle.setContentDescription(option.label+", "+option.value.getText());
                }
                backgrounds.check(MODE_ID+state.backgroundMode);
                for(int i=0;i<backgrounds.getChildCount();i++){
                    RadioButton button=(RadioButton)backgrounds.getChildAt(i);button.setEnabled(!state.masterDisabled);
                    button.setTextColor(button.isChecked()?WHITE:MUTED);button.setTypeface(null,button.isChecked()?Typeface.BOLD:Typeface.NORMAL);
                    int mode=button.getId()-MODE_ID;String name=mode==StationGraphicsPreferences.WAVES?"Ondas":mode==StationGraphicsPreferences.SKY?"Céu":"Desligado";
                    button.setContentDescription("Fundo "+name+(button.isChecked()?", selecionado":"")+(state.masterDisabled?", pausado pela economia":""));
                }
                backgroundHint.setText(state.masterDisabled?"Fundo pausado pela economia.":state.backgroundMode==StationGraphicsPreferences.OFF?"Sem fundo animado.":!state.backgroundAllowed()?"Estilo salvo; movimento desligado.":state.backgroundMode==StationGraphicsPreferences.WAVES?"Ondas suaves nos menus.":"Céu com a cor das configurações.");
                View focused=findFocus();if(focused!=null&&!focused.isEnabled())master.requestFocus();
            }finally{updating=false;}
        }
        @Override protected void onAttachedToWindow(){super.onAttachedToWindow();if(!connected){connected=true;preferences.addListener(this);}render(preferences.snapshot());if(findFocus()==null)master.requestFocus();}
        @Override protected void onDetachedFromWindow(){disconnect();super.onDetachedFromWindow();}
        void disconnect(){if(connected){preferences.removeListener(this);connected=false;}}
        @Override public void onGraphicsChanged(StationGraphicsPreferences.State state){owner.runOnUiThread(()->{if(connected&&!owner.isFinishing()&&!owner.isDestroyed())render(preferences.snapshot());});}
    }
}
