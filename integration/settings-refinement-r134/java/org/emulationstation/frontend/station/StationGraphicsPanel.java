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
    private static final class Content extends LinearLayout implements StationGraphicsPreferences.Listener, StationCarouselStylePreferences.Listener, RadioGroup.OnCheckedChangeListener, View.OnClickListener {
        private static final int WHITE=0xffeff5ff, MUTED=0xff9eaabc, ACCENT=0xff46dbff;
        private static final int BASE=0xff06080d, SURFACE=0xff101a27, LINE=0xff263545, PRIMARY=0xff244eb3;
        private static final int MODE_ID=0x118100, STYLE_ID=0x123100, LOOP_ID=0x130100;
        private final Activity owner;
        private final StationGraphicsPreferences preferences;
        private final StationCarouselStylePreferences carouselPreferences;
        private final ArrayList<Option> options=new ArrayList<>();
        private final Switch master;
        private final TextView status,backgroundHint,carouselHint,videoLoopHint;
        private final LinearLayout masterSurface;
        private final RadioGroup backgrounds,carouselStyles,videoLoopModes;
        private final boolean wide;
        private final ArrayList<LinearLayout> pages=new ArrayList<>();
        private final ArrayList<TextView> navigation=new ArrayList<>();
        private final TextView pageTitle;
        private int selectedPage;
        private boolean connected,updating;

        Content(Activity owner,Runnable close) {
            super(owner);this.owner=owner;preferences=StationGraphicsPreferences.get(owner);carouselPreferences=StationCarouselStylePreferences.get(owner);
            android.util.DisplayMetrics display=getResources().getDisplayMetrics();
            wide=display.widthPixels>display.heightPixels&&display.widthPixels/display.density>=620;
            setOrientation(VERTICAL);setDescendantFocusability(FOCUS_AFTER_DESCENDANTS);
            setPadding(dp(wide?22:14),dp(8),dp(wide?22:14),dp(6));setBackgroundColor(BASE);
            LinearLayout header=row(),titles=vertical();
            TextView eyebrow=text("CONFIGURAÇÕES",10,MUTED);eyebrow.setLetterSpacing(.12f);titles.addView(eyebrow);
            TextView title=text("Efeitos gráficos",18,WHITE);title.setTypeface(null,Typeface.BOLD);titles.addView(title);
            header.addView(titles,new LinearLayout.LayoutParams(0,dp(52),1));
            masterSurface=row();masterSurface.setPadding(dp(12),0,dp(6),0);masterSurface.setMinimumHeight(dp(48));masterSurface.setBackground(rowStates(true));masterSurface.setFocusable(false);
            LinearLayout masterCopy=vertical();TextView masterTitle=text("Efeitos gerais",12,WHITE);masterTitle.setTypeface(null,Typeface.BOLD);masterCopy.addView(masterTitle);
            status=text("",10,MUTED);status.setMaxLines(2);masterCopy.addView(status);masterSurface.addView(masterCopy,new LinearLayout.LayoutParams(0,-2,1));
            master=toggle("Efeitos gerais");masterSurface.addView(master,new LinearLayout.LayoutParams(dp(52),dp(48)));focusSurface(master,masterSurface);
            master.setOnCheckedChangeListener((button,checked)->{if(!updating)preferences.setMasterDisabled(!checked);});
            masterSurface.setOnClickListener(v->master.setChecked(!master.isChecked()));
            if(wide){LinearLayout.LayoutParams control=new LinearLayout.LayoutParams(dp(220),dp(48));control.rightMargin=dp(16);header.addView(masterSurface,control);}
            TextView back=text("‹  Voltar",12,WHITE);back.setTypeface(null,Typeface.BOLD);back.setGravity(Gravity.CENTER);back.setMinWidth(dp(80));
            back.setBackground(segmentStates());back.setPadding(dp(12),0,dp(12),0);back.setFocusable(true);back.setContentDescription("Voltar às configurações");
            back.setOnClickListener(v->{if(close!=null)close.run();});header.addView(back,new LinearLayout.LayoutParams(-2,dp(48)));addView(header);
            if(!wide){LinearLayout.LayoutParams controls=new LinearLayout.LayoutParams(-1,dp(48));controls.topMargin=dp(4);addView(masterSurface,controls);}
            separator(this,dp(6));
            LinearLayout workspace=new LinearLayout(owner);workspace.setOrientation(wide?HORIZONTAL:VERTICAL);workspace.setPadding(0,dp(12),0,0);addView(workspace,new LinearLayout.LayoutParams(-1,0,1));
            LinearLayout nav=new LinearLayout(owner);nav.setOrientation(wide?VERTICAL:HORIZONTAL);
            String[] names={"Fundo","Carrossel","Luzes","Ícones"};
            for(int i=0;i<names.length;i++){
                TextView button=text(names[i],12,WHITE);button.setTypeface(null,Typeface.BOLD);button.setTag(Integer.valueOf(i));button.setOnClickListener(this);
                button.setBackground(rowStates(true));button.setPadding(dp(12),0,dp(12),0);button.setFocusable(true);button.setContentDescription("Opções de "+names[i]);
                button.setGravity(wide?Gravity.CENTER_VERTICAL:Gravity.CENTER);button.setSingleLine(true);navigation.add(button);
                LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(wide?-1:0,dp(48),wide?0:1);if(i>0){if(wide)size.topMargin=dp(6);else size.leftMargin=dp(4);}nav.addView(button,size);
            }
            if(wide){LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(dp(142),-1);size.rightMargin=dp(18);workspace.addView(nav,size);}
            else{LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(-1,dp(48));size.bottomMargin=dp(10);workspace.addView(nav,size);}
            LinearLayout detail=vertical();if(wide)workspace.addView(detail,new LinearLayout.LayoutParams(0,-1,1));else workspace.addView(detail,new LinearLayout.LayoutParams(-1,0,1));
            pageTitle=text("",16,WHITE);pageTitle.setTypeface(null,Typeface.BOLD);pageTitle.setPadding(dp(2),0,0,dp(6));detail.addView(pageTitle);
            ScrollView scroll=new ScrollView(owner);scroll.setFillViewport(false);scroll.setFocusable(false);scroll.setOverScrollMode(View.OVER_SCROLL_NEVER);scroll.setClipToPadding(false);
            LinearLayout body=vertical();body.setPadding(0,0,0,dp(4));scroll.addView(body,new ScrollView.LayoutParams(-1,-2));detail.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
            for(int i=0;i<4;i++){LinearLayout page=vertical();page.setPadding(dp(12),dp(4),dp(12),dp(8));page.setBackground(new ConsoleSurface(SURFACE,LINE,0,display.density));pages.add(page);body.addView(page,new LinearLayout.LayoutParams(-1,-2));}
            LinearLayout environment=pages.get(0),carousel=pages.get(1),lights=pages.get(2),icons=pages.get(3);
            section(environment,"Estilo do fundo");backgrounds=new RadioGroup(owner);backgrounds.setOrientation(HORIZONTAL);
            int[] modes={StationGraphicsPreferences.WAVES,StationGraphicsPreferences.SKY,StationGraphicsPreferences.OFF};String[] backgroundsNames={"Ondas","Céu","Sem fundo"};
            for(int i=0;i<modes.length;i++)backgrounds.addView(choice(MODE_ID+modes[i],backgroundsNames[i],"Fundo "+backgroundsNames[i]),choiceSize(i));
            backgrounds.setOnCheckedChangeListener((group,id)->{if(!updating&&id>=MODE_ID&&id<=MODE_ID+2)preferences.setBackgroundMode(id-MODE_ID);});environment.addView(backgrounds,new LinearLayout.LayoutParams(-1,-2));
            separator(environment,dp(4));environment.addView(option(StationGraphicsPreferences.CLOUDS,"Movimento do fundo","Anima somente o estilo escolhido"),new LinearLayout.LayoutParams(-1,-2));
            backgroundHint=text("",11,MUTED);backgroundHint.setPadding(dp(4),dp(2),dp(4),0);backgroundHint.setMaxLines(2);environment.addView(backgroundHint);
            section(carousel,"Posição das capas");carouselStyles=new RadioGroup(owner);carouselStyles.setOrientation(HORIZONTAL);String[] styleNames={"Reta","Diagonal","De lado"};
            for(int i=0;i<styleNames.length;i++)carouselStyles.addView(choice(STYLE_ID+i,styleNames[i],"Carrossel "+styleNames[i]),choiceSize(i));
            carouselStyles.setOnCheckedChangeListener((group,id)->{if(!updating&&id>=STYLE_ID&&id<=STYLE_ID+2)carouselPreferences.setStyle(id-STYLE_ID);});carousel.addView(carouselStyles,new LinearLayout.LayoutParams(-1,-2));
            carouselHint=text("",10,MUTED);carouselHint.setPadding(dp(4),0,dp(4),dp(2));carouselHint.setMaxLines(2);carousel.addView(carouselHint);separator(carousel,dp(4));
            carousel.addView(option(StationGraphicsPreferences.VIDEO,"Vídeos do carrossel","Vídeos de sistemas e coleções"),new LinearLayout.LayoutParams(-1,-2));
            videoLoopModes=new RadioGroup(owner);videoLoopModes.setOrientation(HORIZONTAL);videoLoopModes.addView(choice(LOOP_ID+1,"Com loop","Vídeo principal com loop"),choiceSize(0));videoLoopModes.addView(choice(LOOP_ID,"Sem loop","Vídeo principal sem loop"),choiceSize(1));videoLoopModes.setOnCheckedChangeListener(this);carousel.addView(videoLoopModes,new LinearLayout.LayoutParams(-1,-2));
            videoLoopHint=text("",10,MUTED);videoLoopHint.setMaxLines(2);videoLoopHint.setPadding(dp(4),0,dp(4),dp(4));carousel.addView(videoLoopHint,new LinearLayout.LayoutParams(-1,-2));
            lights.addView(option(StationGraphicsPreferences.LED,"LEDs das capas","Luzes e rastros ao redor das capas"),new LinearLayout.LayoutParams(-1,-2));separator(lights,0);
            lights.addView(option(StationGraphicsPreferences.CELL_EFFECTS,"Efeitos das células","Brilhos e perspectiva dos menus"),new LinearLayout.LayoutParams(-1,-2));
            icons.addView(option(StationGraphicsPreferences.ICONS,"Ícones e Lotties","Animações do robô e das estrelas"),new LinearLayout.LayoutParams(-1,-2));separator(icons,0);
            icons.addView(option(StationGraphicsPreferences.UI_TRANSITIONS,"Transições","Entrada e troca de itens"),new LinearLayout.LayoutParams(-1,-2));
            TextView foot=text("Alterações salvas automaticamente",10,MUTED);foot.setGravity(Gravity.RIGHT);foot.setPadding(0,dp(4),0,0);addView(foot);
            selectPage(0);render(preferences.snapshot());
        }

        private void selectPage(int index){
            if(index<0||index>=pages.size())return;selectedPage=index;
            String[] headings={"Fundo dos menus","Carrossel e vídeos","Iluminação das capas","Ícones e transições"};pageTitle.setText(headings[index]);
            for(int i=0;i<pages.size();i++){
                boolean active=i==index;pages.get(i).setVisibility(active?View.VISIBLE:View.GONE);TextView button=navigation.get(i);button.setActivated(active);button.setTextColor(active?ACCENT:MUTED);button.setSelected(active);
            }
        }
        @Override public void onClick(View view){Object index=view.getTag();if(index instanceof Integer)selectPage(((Integer)index).intValue());}

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
            LinearLayout copy=vertical();TextView title=text(label,13,WHITE);title.setTypeface(null,Typeface.BOLD);title.setMaxLines(1);title.setEllipsize(android.text.TextUtils.TruncateAt.END);
            title.setCompoundDrawablesWithIntrinsicBounds(new ConsoleMark(effect,ACCENT,dp(14)),null,null,null);title.setCompoundDrawablePadding(dp(6));copy.addView(title);
            TextView hint=text(detail,10,MUTED);hint.setMaxLines(2);hint.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(hint);
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
                renderVideoLoop(state);
                View focused=findFocus();if(focused!=null&&!focused.isEnabled())master.requestFocus();
            }finally{updating=false;}
        }
        private void renderVideoLoop(StationGraphicsPreferences.State state){
            boolean enabled=state.isEnabled(StationGraphicsPreferences.VIDEO);
            videoLoopModes.check(LOOP_ID+(preferences.platformVideoLoop()?1:0));
            for(int i=0;i<videoLoopModes.getChildCount();i++){
                RadioButton button=(RadioButton)videoLoopModes.getChildAt(i);button.setEnabled(enabled);
                button.setTextColor(button.isChecked()?WHITE:MUTED);button.setTypeface(null,button.isChecked()?Typeface.BOLD:Typeface.NORMAL);
                button.setContentDescription("Vídeo principal "+button.getText()+(button.isChecked()?", selecionado":"")+(!enabled?", vídeos desligados":""));
            }
            videoLoopHint.setText(!enabled?"Escolha salva; vídeos desligados.":"Só o vídeo em destaque nas plataformas. Coleções sempre sem loop.");
        }
        @Override public void onCheckedChanged(RadioGroup group,int id){
            if(group==videoLoopModes&&!updating&&id>=LOOP_ID&&id<=LOOP_ID+1)
                preferences.setPlatformVideoLoop(id==LOOP_ID+1);
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
