package org.emulationstation.frontend.netplay;

import android.animation.ValueAnimator;
import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.*;
import android.graphics.drawable.*;
import android.view.Gravity;
import android.view.View;
import android.os.SystemClock;
import android.widget.Button;

/** Shared room actions. Compact faces retain a 48dp touch target. */
final class StationActionButton extends Button {
    static final int SECONDARY=0, PRIMARY=1, DANGER=2;
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path clip=new Path();
    private final Matrix sweep=new Matrix();
    private LinearGradient light;
    private boolean running,compact,navigation;
    private long started;
    private final Runnable frame=new Runnable(){public void run(){
        if(!running)return;
        if(!mayAnimate()){animateIfVisible();return;}
        phase=((SystemClock.uptimeMillis()-started)%3400)/3400f;
        invalidate();postDelayed(this,34);
    }};
    private boolean motion;
    private float phase;
    private final float density;
    private final int tone;
    private ColorStateList foreground;
    private int actionIcon=StationSocialIcon.NONE;

    // Compatibility: existing sheets already inset this constructor's face by 6dp.
    StationActionButton(Context context,String label,boolean primary){
        this(context,label,primary?PRIMARY:SECONDARY);
        setActionIcon(iconForLabel(label));
    }
    // Only controlled UI labels choose an illustration; callbacks and tone never
    // depend on text. Explicit semantic constructors can always supply an icon.
    static int iconForLabel(String label){
        String value=label==null?"":label.trim().toUpperCase(java.util.Locale.ROOT);
        switch(value){
            case "VER SALAS":case "SALAS":case "MAIS SALAS":case "MAIS SALAS →":
                return StationSocialIcon.ROOM;
            case "PESSOAS ONLINE":case "CONVIDAR":case "CONVIDAR JOGADOR":
            case "CONVIDAR PARA SALA":case "CONVIDAR PARA A SALA":case "ENVIAR CONVITE":
            case "PERFIL / CONVITE":case "PERFIL":case "VER PERFIL":
                return StationSocialIcon.PEOPLE;
            case "CRIAR SALA":case "CRIAR SALA E CONVIDAR":return StationSocialIcon.CREATE;
            case "SUAS CONVERSAS":case "CONVERSA":case "CONVERSAR":
            case "CONVERSAR NA SALA":case "NOVA MENSAGEM":return StationSocialIcon.CHAT;
            case "CÓDIGO DA SALA":case "CÓDIGO DA MINHA SALA":case "CÓDIGO DE CONVITE":
                return StationSocialIcon.CODE;
            case "COPIAR":case "COPIAR CÓDIGO":return StationSocialIcon.COPY;
            case "RECONECTAR":case "TENTAR NOVAMENTE":case "TENTAR ABRIR NOVAMENTE":
            case "ATUALIZAR":return StationSocialIcon.RECONNECT;
            case "VOLTAR":case "VOLTAR AO CATÁLOGO":case "ANTERIOR":
            case "PÁGINA ANTERIOR":case "← PÁGINA ANTERIOR":return StationSocialIcon.BACK;
            case "ESTOU PRONTO":case "CONFIRMAR":case "ACEITAR E ENTRAR":
            case "ACEITAR PEDIDO":case "PEDIDO ENVIADO":case "CONVITE ENVIADO":
                return StationSocialIcon.READY;
            case "CANCELAR CONFIRMAÇÃO":case "DESMARCAR PRONTO":case "BLOQUEAR JOGADOR":
                return StationSocialIcon.NOT_READY;
            case "INICIAR":case "INICIAR PARTIDA":case "ENTRAR":case "ENTRAR NA SALA":
            case "PEDIR PARA JOGAR":case "JOGAR ONLINE":case "ABRIR":
            case "PRÓXIMA PÁGINA":case "PRÓXIMA PÁGINA →":return StationSocialIcon.PLAY;
            case "SAIR":case "SAIR DA SALA":return StationSocialIcon.EXIT;
            case "ESCOLHER JOGO":case "SELECIONAR JOGO":case "TROCAR JOGO":
            case "BUSCAR":case "BUSCAR JOGO":return StationSocialIcon.SEARCH;
            case "ENVIAR":case "ENVIAR MENSAGEM":return StationSocialIcon.SEND;
            case "FECHAR":case "CANCELAR":case "AGORA NÃO":case "RECUSAR":
                return StationSocialIcon.CLOSE;
            default:return StationSocialIcon.NONE;
        }
    }
    private StationActionButton(Context context,String label,int tone){
        super(context);this.tone=tone;density=getResources().getDisplayMetrics().density;
        setText(label);setAllCaps(false);setTextSize(13);
        setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        setIncludeFontPadding(false);setSingleLine(true);
        setEllipsize(android.text.TextUtils.TruncateAt.END);
        setMinHeight(0);setMinimumHeight(0);setMinWidth(0);setMinimumWidth(0);
        setPadding(dp(12),0,dp(12),0);setCompoundDrawablePadding(dp(8));
        setStateListAnimator(null);setElevation(0);
        int enabled=tone==DANGER?0xffefb3b8:tone==PRIMARY?0xffeffbf4:0xffd8e3e7;
        foreground=new ColorStateList(new int[][]{new int[]{-android.R.attr.state_enabled},new int[]{}},
                new int[]{0xff94a2a9,enabled});
        setTextColor(foreground);applyFace();
    }
    // New room layout API: no extra InsetDrawable is needed around this button.
    StationActionButton(Context context,String label,int tone,int icon){
        this(context,label,tone);compactAppearance();setActionIcon(icon);
    }
    void compactAppearance(){
        compact=true;setMinHeight(dp(48));setMinimumHeight(dp(48));
        setGravity(Gravity.CENTER_VERTICAL|Gravity.START);
        setTextAlignment(View.TEXT_ALIGNMENT_GRAVITY);
        applyFace();updateClip();
    }
    void setActionIcon(int icon){
        actionIcon=icon;
        setCompoundDrawablesWithIntrinsicBounds(icon<0?null:new StationSocialIcon(icon,dp(18),foreground),null,null,null);
        setCompoundDrawablePadding(dp(8));
    }
    void setNavigationSelected(boolean selected){
        navigation=true;setSelected(selected);
        foreground=new ColorStateList(new int[][]{new int[]{-android.R.attr.state_enabled},new int[]{}},
                new int[]{0xff94a2a9,selected?0xffeffbf4:0xffafc0c7});
        setTextColor(foreground);setActionIcon(actionIcon);applyFace();
    }
    private int dp(float n){return (int)(n*density+.5f);}
    private GradientDrawable face(int color,int border){
        GradientDrawable d=new GradientDrawable();d.setColor(color);
        d.setCornerRadius(dp(8));d.setStroke(dp(1),border);return d;
    }
    private void applyFace(){
        int fill=tone==PRIMARY?0xff194d38:tone==DANGER?0xff281b20:0xff111e23;
        int rim=tone==PRIMARY?0xff428463:tone==DANGER?0xff67434b:0xff31434a;
        if(navigation){fill=isSelected()?0xff19352b:0x00000000;rim=isSelected()?0xff365e4d:0x00000000;}
        int focus=tone==DANGER?0xffd2919b:0xff79cba6;
        StateListDrawable states=new StateListDrawable();
        states.addState(new int[]{-android.R.attr.state_enabled},face(0xff151f23,0xff2c393f));
        states.addState(new int[]{android.R.attr.state_focused},face(fill,focus));
        states.addState(new int[]{},face(fill,rim));
        Drawable background=new RippleDrawable(ColorStateList.valueOf(tone==DANGER?0x32f2a5ad:0x305fcca0),states,null);
        setBackground(compact?new InsetDrawable(background,0,dp(6),0,dp(6)):background);
        setPadding(dp(12),0,dp(12),0);
    }
    private void updateClip(){
        clip.reset();float inset=compact?dp(6):0;
        if(getWidth()>0&&getHeight()>2*inset)
            clip.addRoundRect(0,inset,getWidth(),getHeight()-inset,dp(8),dp(8),Path.Direction.CW);
    }
    @Override protected void onSizeChanged(int w,int h,int ow,int oh){
        super.onSizeChanged(w,h,ow,oh);updateClip();
        light=new LinearGradient(-dp(38),0,dp(38),0,new int[]{0x0078ffab,0x3378ffab,0x0078ffab},null,Shader.TileMode.CLAMP);
    }
    @Override protected void onDraw(Canvas canvas){
        if(allowsMotion()&&motion&&isEnabled()&&light!=null){int save=canvas.save();canvas.clipPath(clip);sweep.reset();sweep.setRotate(-18);sweep.postTranslate(-dp(70)+(getWidth()+dp(140))*phase,0);light.setLocalMatrix(sweep);paint.setShader(light);canvas.drawRect(0,0,getWidth(),getHeight(),paint);paint.setShader(null);canvas.restoreToCount(save);}
        super.onDraw(canvas);
    }
    private boolean allowsMotion(){
        String label=String.valueOf(getText()).trim().toUpperCase(java.util.Locale.ROOT);
        return label.equals("ABRIR")||label.startsWith("ABRIR ")||label.equals("VOLTAR")||label.startsWith("VOLTAR ");
    }
    private boolean mayAnimate(){return allowsMotion()&&motion&&isEnabled()&&isAttachedToWindow()&&getWindowVisibility()==View.VISIBLE&&isShown()&&hasWindowFocus()&&ValueAnimator.areAnimatorsEnabled();}
    private void animateIfVisible(){
        if(frame==null)return; // View's constructor may dispatch setEnabled before our fields initialize.
        boolean run=mayAnimate();if(run==running)return;
        running=run;removeCallbacks(frame);
        if(run){started=SystemClock.uptimeMillis();post(frame);}
    }
    void setMotion(boolean enabled){motion=enabled;animateIfVisible();invalidate();}
    @Override public void setEnabled(boolean enabled){super.setEnabled(enabled);animateIfVisible();}
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();animateIfVisible();}
    @Override protected void onDetachedFromWindow(){running=false;removeCallbacks(frame);super.onDetachedFromWindow();}
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);animateIfVisible();}
    @Override protected void onVisibilityChanged(View changed,int visibility){super.onVisibilityChanged(changed,visibility);animateIfVisible();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);animateIfVisible();}
}
