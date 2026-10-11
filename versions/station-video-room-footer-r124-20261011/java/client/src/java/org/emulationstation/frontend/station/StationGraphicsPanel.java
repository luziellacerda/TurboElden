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

    /** Static rounded surface; no timer, bitmap, shader or animation. */
    private static final class ConsoleSurface extends android.graphics.drawable.Drawable {
        private final android.graphics.Paint paint = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
        private final android.graphics.RectF rectangle = new android.graphics.RectF();
        private final int fill, rim, rail;
        private final float density;
        private int alpha=255;
        ConsoleSurface(int fill, int rim, int rail, float density) { this.fill=fill;this.rim=rim;this.rail=rail;this.density=density; }
        @Override protected void onBoundsChange(android.graphics.Rect bounds) {
            float inset=density*.5f;
            rectangle.set(bounds.left+inset,bounds.top+inset,bounds.right-inset,bounds.bottom-inset);
        }
        @Override public void draw(android.graphics.Canvas canvas) {
            int fillAlpha=android.graphics.Color.alpha(fill)*alpha/255;
            if(fillAlpha>0){paint.setStyle(android.graphics.Paint.Style.FILL);paint.setColor(fill);paint.setAlpha(fillAlpha);canvas.drawRoundRect(rectangle,density*6,density*6,paint);}
            int rimAlpha=android.graphics.Color.alpha(rim)*alpha/255;
            if(rimAlpha>0){paint.setStyle(android.graphics.Paint.Style.STROKE);paint.setStrokeWidth(density);paint.setColor(rim);paint.setAlpha(rimAlpha);canvas.drawRoundRect(rectangle,density*6,density*6,paint);}
            int railAlpha=android.graphics.Color.alpha(rail)*alpha/255;
            if(railAlpha>0){paint.setStyle(android.graphics.Paint.Style.FILL);paint.setColor(rail);paint.setAlpha(railAlpha);
                canvas.drawRoundRect(rectangle.left+density*8,rectangle.bottom-density*3,rectangle.right-density*8,rectangle.bottom-density, density,density,paint);}
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
        final int effect; final String label; final Switch toggle; final LinearLayout surface;
        Option(int effect,String label,Switch toggle,LinearLayout surface) { this.effect=effect;this.label=label;this.toggle=toggle;this.surface=surface; }
    }
    private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener, StationCarouselStylePreferences.Listener {
        private static final int WHITE=0xffeff5ff, MUTED=0xff9eaabc, ACCENT=0xff46dbff;
        private static final int BASE=0xff06080d, SURFACE=0xff101a27, LINE=0xff263545, PRIMARY=0xff244eb3;
        private static final int MODE_ID=0x118100, STYLE_ID=0x123100;
        private final Activity owner;
        private final StationGraphicsPreferences preferences;
        private final StationCarouselStylePreferences carouselPreferences;
        private final ArrayList<Option> options=new ArrayList<>();
        private final Switch master;
        private final TextView status,backgroundHint,carouselHint;
        private final LinearLayout masterSurface;
        private final RadioGroup backgrounds,carouselStyles;
        private final boolean wide;
        private boolean connected,updating;

        Content(Activity owner,Runnable close) {
            super(owner);this.owner=owner;preferences=StationGraphicsPreferences.get(owner);carouselPreferences=StationCarouselStylePreferences.get(owner);
            android.util.DisplayMetrics display=getResources().getDisplayMetrics();
            wide=display.widthPixels>display.heightPixels&&display.widthPixels/display.density>=620;
            setOrientation(VERTICAL);setDescendantFocusability(FOCUS_AFTER_DESCENDANTS);
            setPadding(dp(wide?22:14),dp(8),dp(wide?22:14),dp(6));setBackgroundColor(BASE);
            LinearLayout header=row();LinearLayout titles=vertical();
            TextView eyebrow=text("Configurações",10,MUTED);titles.addView(eyebrow);
            TextView title=text("Efeitos gráficos",18,WHITE);title.setTypeface(null,Typeface.BOLD);titles.addView(title);
            header.addView(titles,new LinearLayout.LayoutParams(0,dp(48),1));
            TextView back=text("‹  Voltar",12,WHITE);back.setTypeface(null,Typeface.BOLD);back.setGravity(Gravity.CENTER);back.setMinWidth(dp(76));
            back.setBackground(segmentStates());back.setPadding(dp(12),0,dp(12),0);back.setFocusable(true);back.setContentDescription("Voltar às configurações");
            back.setOnClickListener(v->{if(close!=null)close.run();});header.addView(back,new LinearLayout.LayoutParams(-2,dp(48)));addView(header);
            separator(this,dp(4));

            ScrollView scroll=new ScrollView(owner);scroll.setFillViewport(false);scroll.setFocusable(false);scroll.setOverScrollMode(View.OVER_SCROLL_NEVER);scroll.setClipToPadding(false);
            LinearLayout body=vertical();body.setPadding(0,dp(8),0,dp(6));scroll.addView(body,new ScrollView.LayoutParams(-1,-2));addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
            masterSurface=row();masterSurface.setPadding(dp(12),0,dp(8),0);masterSurface.setMinimumHeight(dp(48));masterSurface.setBackground(rowStates(true));masterSurface.setFocusable(false);
            LinearLayout masterCopy=vertical();TextView masterTitle=text("Efeitos dos menus",14,WHITE);masterTitle.setTypeface(null,Typeface.BOLD);masterCopy.addView(masterTitle);
            status=text("",11,MUTED);status.setMaxLines(2);masterCopy.addView(status);masterSurface.addView(masterCopy,new LinearLayout.LayoutParams(0,-2,1));
            master=toggle("Efeitos gerais");masterSurface.addView(master,new LinearLayout.LayoutParams(dp(52),dp(48)));focusSurface(master,masterSurface);
            body.addView(masterSurface,new LinearLayout.LayoutParams(-1,-2));
            master.setOnCheckedChangeListener((button,checked)->{if(!updating)preferences.setMasterDisabled(!checked);});
            masterSurface.setOnClickListener(v->master.setChecked(!master.isChecked()));

            LinearLayout columns=new LinearLayout(owner);columns.setOrientation(wide?HORIZONTAL:VERTICAL);LinearLayout.LayoutParams columnsSize=new LinearLayout.LayoutParams(-1,-2);columnsSize.topMargin=dp(8);body.addView(columns,columnsSize);
            LinearLayout left=vertical(),right=vertical();
            if(wide){LinearLayout.LayoutParams side=new LinearLayout.LayoutParams(0,-2,.40f);side.rightMargin=dp(18);columns.addView(left,side);columns.addView(right,new LinearLayout.LayoutParams(0,-2,.60f));}
            else{columns.addView(left,new LinearLayout.LayoutParams(-1,-2));columns.addView(right,new LinearLayout.LayoutParams(-1,-2));}
            section(left,"Ambiente");
            backgrounds=new RadioGroup(owner);backgrounds.setOrientation(HORIZONTAL);
            int[] modes={StationGraphicsPreferences.WAVES,StationGraphicsPreferences.SKY,StationGraphicsPreferences.OFF};String[] names={"Ondas","Céu","Desligado"};
            for(int i=0;i<modes.length;i++)backgrounds.addView(choice(MODE_ID+modes[i],names[i],"Fundo "+names[i]),choiceSize(i));
            backgrounds.setOnCheckedChangeListener((group,id)->{if(!updating&&id>=MODE_ID&&id<=MODE_ID+2)preferences.setBackgroundMode(id-MODE_ID);});
            left.addView(backgrounds,new LinearLayout.LayoutParams(-1,-2));
            left.addView(option(StationGraphicsPreferences.CLOUDS,"Movimento do fundo","Anima ondas ou nuvens"),new LinearLayout.LayoutParams(-1,-2));
            backgroundHint=text("",11,MUTED);backgroundHint.setPadding(dp(2),dp(2),dp(2),0);backgroundHint.setMaxLines(3);left.addView(backgroundHint);

            section(left,"Carrossel");
            carouselStyles=new RadioGroup(owner);carouselStyles.setOrientation(HORIZONTAL);
            String[] styleNames={"Reta","Diagonal","De lado"};
            for(int i=0;i<styleNames.length;i++)carouselStyles.addView(choice(STYLE_ID+i,styleNames[i],"Carrossel "+styleNames[i]),choiceSize(i));
            carouselStyles.setOnCheckedChangeListener((group,id)->{if(!updating&&id>=STYLE_ID&&id<=STYLE_ID+2)carouselPreferences.setStyle(id-STYLE_ID);});
            left.addView(carouselStyles,new LinearLayout.LayoutParams(-1,-2));
            carouselHint=text("",11,MUTED);carouselHint.setPadding(dp(2),dp(2),dp(2),0);carouselHint.setMaxLines(3);left.addView(carouselHint);

            section(right,"Personalizar");
            LinearLayout effectsList=vertical();effectsList.setBackground(new ConsoleSurface(SURFACE,LINE,0,display.density));effectsList.setPadding(dp(8),0,dp(8),0);right.addView(effectsList,new LinearLayout.LayoutParams(-1,-2));
            int[] effects={StationGraphicsPreferences.LED,StationGraphicsPreferences.VIDEO,StationGraphicsPreferences.ICONS,StationGraphicsPreferences.CELL_EFFECTS,StationGraphicsPreferences.UI_TRANSITIONS};
            String[] labels={"LEDs das capas","Vídeos do carrossel","Ícones e Lotties","Efeitos das células","Transições"};
            String[] hints={"Luzes e rastros","Sistemas e coleções","Robô e estrelas","Brilhos dos menus","Entrada e troca de itens"};
            for(int i=0;i<effects.length;i++){
                if(i>0)separator(effectsList,0);
                effectsList.addView(option(effects[i],labels[i],hints[i]),new LinearLayout.LayoutParams(-1,-2));
            }
            TextView foot=text("Salvo automaticamente",10,MUTED);foot.setGravity(Gravity.RIGHT);foot.setPadding(0,dp(2),0,0);addView(foot);
            render(preferences.snapshot());
        }

        private int dp(float value){return Math.round(value*getResources().getDisplayMetrics().density);}
        private LinearLayout vertical(){LinearLayout view=new LinearLayout(owner);view.setOrientation(VERTICAL);return view;}
        private LinearLayout row(){LinearLayout view=new LinearLayout(owner);view.setOrientation(HORIZONTAL);view.setGravity(Gravity.CENTER_VERTICAL);return view;}
        private TextView text(String value,int size,int color){TextView view=new TextView(owner);view.setText(value);view.setTextSize(size);view.setTextColor(color);view.setGravity(Gravity.CENTER_VERTICAL);return view;}
        private void separator(LinearLayout list,int margin){View line=new View(owner);line.setBackgroundColor(LINE);LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(-1,dp(1));size.topMargin=margin;list.addView(line,size);}
        private android.graphics.drawable.StateListDrawable rowStates(boolean primary){
            float density=getResources().getDisplayMetrics().density;android.graphics.drawable.StateListDrawable states=new android.graphics.drawable.StateListDrawable();
            states.addState(new int[]{android.R.attr.state_pressed},new ConsoleSurface(0xff1c354b,0,0,density));
            states.addState(new int[]{android.R.attr.state_activated},new ConsoleSurface(0xff132a3d,ACCENT,0,density));
            states.addState(new int[]{},new ConsoleSurface(primary?SURFACE:android.graphics.Color.TRANSPARENT,primary?LINE:0,0,density));return states;
        }
        private android.graphics.drawable.Drawable segmentStates(){
            float density=getResources().getDisplayMetrics().density;android.graphics.drawable.StateListDrawable states=new android.graphics.drawable.StateListDrawable();
            states.addState(new int[]{-android.R.attr.state_enabled,android.R.attr.state_checked},new ConsoleSurface(0xff101a27,0xff263545,0xff315766,density));
            states.addState(new int[]{-android.R.attr.state_enabled},new ConsoleSurface(0xff10151d,0xff1e2834,0,density));
            states.addState(new int[]{android.R.attr.state_pressed},new ConsoleSurface(0xff1f3c56,WHITE,ACCENT,density));
            states.addState(new int[]{android.R.attr.state_focused},new ConsoleSurface(0xff183148,WHITE,ACCENT,density));
            states.addState(new int[]{android.R.attr.state_checked},new ConsoleSurface(0xff142d40,0xff315b70,ACCENT,density));
            states.addState(new int[]{},new ConsoleSurface(SURFACE,LINE,0,density));
            return new android.graphics.drawable.InsetDrawable(states,0,dp(8),0,dp(8));
        }
        private RadioButton choice(int id,String label,String description){
            RadioButton button=new RadioButton(owner);button.setId(id);button.setText(label);button.setTextSize(12);button.setTextColor(WHITE);button.setGravity(Gravity.CENTER);
            button.setButtonDrawable(new ColorDrawable(android.graphics.Color.TRANSPARENT));button.setBackground(segmentStates());button.setPadding(dp(6),0,dp(6),0);
            button.setFocusable(true);button.setSingleLine(true);button.setEllipsize(android.text.TextUtils.TruncateAt.END);button.setContentDescription(description);return button;
        }
        private RadioGroup.LayoutParams choiceSize(int index){RadioGroup.LayoutParams size=new RadioGroup.LayoutParams(0,dp(48),1);size.leftMargin=index==0?0:dp(4);return size;}
        private ColorStateList tint(int active,int idle){return new ColorStateList(new int[][]{{-android.R.attr.state_enabled},{android.R.attr.state_checked},{}},new int[]{0xff475262,active,idle});}
        private Switch toggle(String description){
            Switch view=new Switch(owner);view.setShowText(false);view.setContentDescription(description);view.setFocusable(true);
            view.setThumbTintList(tint(WHITE,0xffa9b4c4));view.setTrackTintList(tint(0xff287c99,0xff414c5a));view.setBackground(new ColorDrawable(android.graphics.Color.TRANSPARENT));
            view.setPadding(0,0,0,0);view.setMinHeight(dp(48));return view;
        }
        private void focusSurface(View target,View surface){target.setOnFocusChangeListener((view,focus)->surface.setActivated(focus));}
        private void section(LinearLayout list,String title){TextView label=text(title,12,ACCENT);label.setTypeface(null,Typeface.BOLD);label.setPadding(dp(2),dp(7),0,dp(3));list.addView(label);}
        private LinearLayout option(int effect,String label,String detail){
            LinearLayout card=row();card.setPadding(dp(4),0,dp(2),0);card.setMinimumHeight(dp(48));card.setBackground(rowStates(false));card.setFocusable(false);
            LinearLayout copy=vertical();TextView title=text(label,13,WHITE);title.setTypeface(null,Typeface.BOLD);title.setMaxLines(2);title.setEllipsize(android.text.TextUtils.TruncateAt.END);
            title.setCompoundDrawablesWithIntrinsicBounds(new ConsoleMark(effect,ACCENT,dp(14)),null,null,null);title.setCompoundDrawablePadding(dp(6));copy.addView(title);
            TextView hint=text(detail,11,MUTED);hint.setMaxLines(2);hint.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(hint);
            card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));Switch toggle=toggle(label);LinearLayout.LayoutParams switchSize=new LinearLayout.LayoutParams(dp(52),dp(48));switchSize.leftMargin=dp(8);card.addView(toggle,switchSize);
            Option option=new Option(effect,label,toggle,card);options.add(option);focusSurface(toggle,card);
            toggle.setOnCheckedChangeListener((button,checked)->{if(!updating)preferences.setEnabled(effect,checked);});
            card.setOnClickListener(v->{if(toggle.isEnabled())toggle.setChecked(!toggle.isChecked());});return card;
        }
        private void render(StationGraphicsPreferences.State state){
            updating=true;
            try{
                master.setChecked(!state.masterDisabled);masterSurface.setSelected(!state.masterDisabled);
                int active=Integer.bitCount(state.effectiveMask());if(!state.backgroundAllowed()&&state.isEnabled(StationGraphicsPreferences.CLOUDS))active--;
                status.setText(state.masterDisabled?"Tudo parado · escolhas preservadas":active+" de 6 opções ativadas");
                master.setContentDescription("Efeitos gerais, "+(state.masterDisabled?"economia":"ativos"));
                for(Option option:options){
                    boolean chosen=(state.individualMask&option.effect)!=0;
                    boolean enabled=chosen&&!state.masterDisabled&&(option.effect!=StationGraphicsPreferences.CLOUDS||state.backgroundAllowed());
                    option.toggle.setChecked(chosen);option.toggle.setEnabled(!state.masterDisabled);option.surface.setEnabled(!state.masterDisabled);option.surface.setSelected(chosen);
                    String value=state.masterDisabled?"pausado":option.effect==StationGraphicsPreferences.CLOUDS&&state.backgroundMode==StationGraphicsPreferences.OFF?"sem fundo":enabled?"ativo":"desativado";
                    option.toggle.setContentDescription(option.label+", "+value);
                }
                backgrounds.check(MODE_ID+state.backgroundMode);
                for(int i=0;i<backgrounds.getChildCount();i++){
                    RadioButton button=(RadioButton)backgrounds.getChildAt(i);button.setEnabled(!state.masterDisabled);
                    button.setTextColor(button.isChecked()?WHITE:MUTED);button.setTypeface(null,button.isChecked()?Typeface.BOLD:Typeface.NORMAL);
                    int mode=button.getId()-MODE_ID;String name=mode==StationGraphicsPreferences.WAVES?"Ondas":mode==StationGraphicsPreferences.SKY?"Céu":"Desligado";
                    button.setContentDescription("Fundo "+name+(button.isChecked()?", selecionado":"")+(state.masterDisabled?", pausado pela economia":""));
                }
                backgroundHint.setText(state.masterDisabled?"Fundo pausado pela economia.":state.backgroundMode==StationGraphicsPreferences.OFF?"Sem fundo animado.":!state.backgroundAllowed()?"Estilo salvo; movimento desligado.":state.backgroundMode==StationGraphicsPreferences.WAVES?"Ondas suaves nos menus.":"Céu com a cor das configurações.");
                renderCarouselStyle(state);
                View focused=findFocus();if(focused!=null&&!focused.isEnabled())master.requestFocus();
            }finally{updating=false;}
        }
        private void renderCarouselStyle(StationGraphicsPreferences.State state){
            boolean previous=updating;updating=true;
            try{
                int style=carouselPreferences.style();boolean enabled=state.isEnabled(StationGraphicsPreferences.CELL_EFFECTS);
                carouselStyles.check(STYLE_ID+style);
                for(int i=0;i<carouselStyles.getChildCount();i++){
                    RadioButton button=(RadioButton)carouselStyles.getChildAt(i);button.setEnabled(enabled);
                    button.setTextColor(button.isChecked()?WHITE:MUTED);button.setTypeface(null,button.isChecked()?Typeface.BOLD:Typeface.NORMAL);
                    button.setContentDescription("Carrossel "+button.getText()+(button.isChecked()?", selecionado":"")+(!enabled?", pausado pelos efeitos":""));
                }
                carouselHint.setText(!enabled?"Estilo salvo; inclinação desativada.":style==StationCarouselStylePreferences.DIAGONAL?"Inclina as células sem destaque.":style==StationCarouselStylePreferences.LATERAL?"Perspectiva nas células sem destaque.":"Mantém o alinhamento atual.");
            }finally{updating=previous;}
        }
        @Override protected void onAttachedToWindow(){super.onAttachedToWindow();if(!connected){connected=true;preferences.addListener(this);carouselPreferences.addListener(this);}render(preferences.snapshot());if(findFocus()==null)master.requestFocus();}
        @Override protected void onDetachedFromWindow(){disconnect();super.onDetachedFromWindow();}
        void disconnect(){if(connected){preferences.removeListener(this);carouselPreferences.removeListener(this);connected=false;}}
        @Override public void onGraphicsChanged(StationGraphicsPreferences.State state){owner.runOnUiThread(()->{if(connected&&!owner.isFinishing()&&!owner.isDestroyed())render(preferences.snapshot());});}
        @Override public void onCarouselStyleChanged(int style){owner.runOnUiThread(()->{if(connected&&!owner.isFinishing()&&!owner.isDestroyed())renderCarouselStyle(preferences.snapshot());});}
    }
}
