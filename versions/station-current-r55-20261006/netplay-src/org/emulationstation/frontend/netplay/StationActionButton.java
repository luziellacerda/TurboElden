package org.emulationstation.frontend.netplay;

import android.animation.ValueAnimator;
import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.*;
import android.graphics.drawable.*;
import android.view.View;
import android.view.animation.LinearInterpolator;
import android.widget.Button;

/** One lightweight sheen on the primary CTA, only while visible and enabled. */
final class StationActionButton extends Button {
    private final boolean primary;
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path clip=new Path();
    private final Matrix sweep=new Matrix();
    private LinearGradient light;
    private ValueAnimator animator;
    private boolean motion;
    private float phase;
    private final float density;
    StationActionButton(Context context,String label,boolean primary){
        super(context);this.primary=primary;density=getResources().getDisplayMetrics().density;
        setText(label);setAllCaps(false);setTextSize(13);setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        setTextColor(new ColorStateList(new int[][]{new int[]{-android.R.attr.state_enabled},new int[]{}},new int[]{0xff789883,0xffeffff3}));
        setMinHeight(0);setMinimumHeight(0);setMinWidth(0);setMinimumWidth(0);setPadding(dp(12),0,dp(12),0);setStateListAnimator(null);
        GradientDrawable enabled=face(primary?0xff16633d:0xff173024,primary?0xff0a3322:0xff102219,primary?0xff4dd985:0xff31543e);
        GradientDrawable disabled=face(0xff17281f,0xff111d17,0xff26392d);
        StateListDrawable states=new StateListDrawable();states.addState(new int[]{-android.R.attr.state_enabled},disabled);states.addState(new int[]{},enabled);
        setBackground(new RippleDrawable(ColorStateList.valueOf(0x407fffb3),states,null));
        setElevation(primary?dp(2):0);
    }
    private int dp(float n){return (int)(n*density+.5f);}
    private GradientDrawable face(int top,int bottom,int border){GradientDrawable d=new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,new int[]{top,bottom});d.setCornerRadius(dp(10));d.setStroke(dp(1),border);return d;}
    @Override protected void onSizeChanged(int w,int h,int ow,int oh){super.onSizeChanged(w,h,ow,oh);clip.reset();clip.addRoundRect(0,0,w,h,dp(10),dp(10),Path.Direction.CW);light=new LinearGradient(-dp(38),0,dp(38),0,new int[]{0x0078ffab,0x3378ffab,0x0078ffab},null,Shader.TileMode.CLAMP);}
    @Override protected void onDraw(Canvas canvas){
        if(allowsMotion()&&motion&&isEnabled()&&light!=null){int save=canvas.save();canvas.clipPath(clip);sweep.reset();sweep.setRotate(-18);sweep.postTranslate(-dp(70)+(getWidth()+dp(140))*phase,0);light.setLocalMatrix(sweep);paint.setShader(light);canvas.drawRect(0,0,getWidth(),getHeight(),paint);paint.setShader(null);canvas.restoreToCount(save);}
        super.onDraw(canvas);
    }
    private boolean allowsMotion(){
        String label=String.valueOf(getText()).trim().toUpperCase(java.util.Locale.ROOT);
        return label.equals("ABRIR")||label.startsWith("ABRIR ")||label.equals("VOLTAR")||label.startsWith("VOLTAR ");
    }
    private void animateIfVisible(){
        boolean run=allowsMotion()&&motion&&isEnabled()&&isAttachedToWindow()&&getWindowVisibility()==View.VISIBLE&&isShown()&&hasWindowFocus();
        if(run&&animator==null){animator=ValueAnimator.ofFloat(0,1);animator.setDuration(3400);animator.setRepeatCount(ValueAnimator.INFINITE);animator.setInterpolator(new LinearInterpolator());animator.addUpdateListener(a->{phase=(Float)a.getAnimatedValue();invalidate();});animator.start();}
        else if(!run&&animator!=null){animator.cancel();animator=null;}
    }
    void setMotion(boolean enabled){motion=enabled;animateIfVisible();invalidate();}
    @Override public void setEnabled(boolean enabled){super.setEnabled(enabled);animateIfVisible();}
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();animateIfVisible();}
    @Override protected void onDetachedFromWindow(){if(animator!=null){animator.cancel();animator=null;}super.onDetachedFromWindow();}
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);animateIfVisible();}
    @Override protected void onVisibilityChanged(View changed,int visibility){super.onVisibilityChanged(changed,visibility);animateIfVisible();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);animateIfVisible();}
}
