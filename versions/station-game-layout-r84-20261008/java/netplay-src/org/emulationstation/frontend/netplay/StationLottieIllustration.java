package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Movie;
import android.graphics.Rect;
import android.graphics.drawable.Animatable;
import android.graphics.drawable.Drawable;
import android.os.Build;
import android.os.SystemClock;
import android.view.View;
import java.io.InputStream;

/** Original Lottie frames packaged locally; no WebView or network at runtime. */
final class StationLottieIllustration extends View {
    private final String asset;
    private Drawable drawable;
    private Movie fallback;
    private boolean loading;
    private long started;
    StationLottieIllustration(Context context,String asset){
        super(context);this.asset=asset;setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
        if(Build.VERSION.SDK_INT<28)setLayerType(View.LAYER_TYPE_SOFTWARE,null);
    }
    private boolean visible(){return isAttachedToWindow()&&isShown()&&getWindowVisibility()==VISIBLE&&hasWindowFocus();}
    private void load(){
        if(loading||drawable!=null||fallback!=null)return;loading=true;
        final Context context=getContext().getApplicationContext();
        Thread worker=new Thread(()->{
            Drawable next=null;Movie movie=null;
            try{
                if(Build.VERSION.SDK_INT>=28)next=Api28.decode(context,asset);
                else try(InputStream stream=context.getAssets().open("station-ui-r42/"+asset+".gif")){movie=Movie.decodeStream(stream);}
            }catch(Exception e){android.util.Log.w("StationIllustration","Local animation unavailable: "+asset);}
            final Drawable result=next;final Movie old=movie;
            post(()->{loading=false;if(!isAttachedToWindow())return;drawable=result;fallback=old;started=SystemClock.uptimeMillis();if(drawable!=null)drawable.setCallback(this);motion();invalidate();});
        },"StationIllustrationDecode");worker.setDaemon(true);worker.start();
    }
    private static final class Api28 {
        static Drawable decode(Context context,String asset)throws java.io.IOException{
            Drawable d=android.graphics.ImageDecoder.decodeDrawable(android.graphics.ImageDecoder.createSource(context.getAssets(),"station-ui-r42/"+asset+".webp"));
            if(d instanceof android.graphics.drawable.AnimatedImageDrawable)((android.graphics.drawable.AnimatedImageDrawable)d).setRepeatCount(android.graphics.drawable.AnimatedImageDrawable.REPEAT_INFINITE);
            return d;
        }
    }
    private void motion(){
        if(drawable instanceof Animatable){Animatable a=(Animatable)drawable;if(visible())a.start();else a.stop();}
        if(visible()&&fallback!=null)invalidate();
    }
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);int width=drawable!=null?drawable.getIntrinsicWidth():fallback!=null?fallback.width():0;
        int height=drawable!=null?drawable.getIntrinsicHeight():fallback!=null?fallback.height():0;
        if(width<=0||height<=0)return;
        float scale=Math.min((float)getWidth()/width,(float)getHeight()/height);
        int x=(int)((getWidth()-width*scale)*.5f),y=(int)((getHeight()-height*scale)*.5f);
        if(drawable!=null){drawable.setBounds(x,y,x+(int)(width*scale),y+(int)(height*scale));drawable.draw(canvas);}
        else{fallback.setTime((int)((SystemClock.uptimeMillis()-started)%Math.max(1,fallback.duration())));int save=canvas.save();canvas.translate(x,y);canvas.scale(scale,scale);fallback.draw(canvas,0,0);canvas.restoreToCount(save);if(visible())postInvalidateDelayed(34);}
    }
    @Override protected boolean verifyDrawable(Drawable d){return d==drawable||super.verifyDrawable(d);}
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();if(drawable!=null)drawable.setCallback(this);load();motion();}
    @Override protected void onDetachedFromWindow(){if(drawable instanceof Animatable)((Animatable)drawable).stop();if(drawable!=null){unscheduleDrawable(drawable);drawable.setCallback(null);}super.onDetachedFromWindow();}
    @Override protected void onVisibilityChanged(View v,int visibility){super.onVisibilityChanged(v,visibility);motion();}
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);motion();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);motion();}
}
