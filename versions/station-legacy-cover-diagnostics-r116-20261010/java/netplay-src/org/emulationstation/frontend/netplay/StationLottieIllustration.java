package org.emulationstation.frontend.netplay;

import android.animation.ValueAnimator;
import android.content.Context;
import android.database.ContentObserver;
import android.graphics.Canvas;
import android.graphics.Movie;
import android.graphics.drawable.Animatable;
import android.graphics.drawable.AnimatedImageDrawable;
import android.graphics.drawable.Drawable;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.provider.Settings;
import android.view.View;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

/** Local online illustration: efficient native loop with a terminal decode-failure gate. */
final class StationLottieIllustration extends View {
    /* Local APK assets cannot appear later in the same process. This also prevents rebuilt
       empty-state views from decoding the same unavailable asset again. */
    private static final Set<String> UNAVAILABLE=Collections.newSetFromMap(new ConcurrentHashMap<String,Boolean>());
    private static final ThreadPoolExecutor DECODE=new ThreadPoolExecutor(
            0,1,1L,TimeUnit.SECONDS,new LinkedBlockingQueue<Runnable>(),r->{
                Thread t=new Thread(r,"StationIllustrationDecode");t.setDaemon(true);return t;
            });
    private final String asset;
    private final Handler main=new Handler(Looper.getMainLooper());
    private final StationSinglePassAnimationState fallbackPlayback=new StationSinglePassAnimationState();
    private final ContentObserver animatorScaleObserver;
    private Drawable drawable;
    private Movie fallback;
    private boolean observerRegistered;

    StationLottieIllustration(Context context,String asset){
        super(context);this.asset=asset;setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
        if(Build.VERSION.SDK_INT<28)setLayerType(View.LAYER_TYPE_SOFTWARE,null);
        animatorScaleObserver=new ContentObserver(main){@Override public void onChange(boolean selfChange){motion();}};
    }
    private boolean visible(){return isAttachedToWindow()&&isShown()&&getWindowVisibility()==VISIBLE&&hasWindowFocus();}
    private boolean mayAnimate(){return visible()&&ValueAnimator.areAnimatorsEnabled();}
    private int decodeWidth(){return Math.max(1,getWidth()>0?getWidth():(int)(112*getResources().getDisplayMetrics().density+.5f));}
    private int decodeHeight(){return Math.max(1,getHeight()>0?getHeight():(int)(112*getResources().getDisplayMetrics().density+.5f));}
    private void load(){
        if(!visible()||drawable!=null||fallback!=null||UNAVAILABLE.contains(asset)||!fallbackPlayback.beginLoad())return;
        final Context context=getContext().getApplicationContext();final int targetWidth=decodeWidth(),targetHeight=decodeHeight();
        DECODE.execute(()->{
            Drawable next=null;Movie movie=null;Throwable failure=null;
            if(Build.VERSION.SDK_INT>=28){
                try{next=Api28.decode(context,asset,targetWidth,targetHeight);}
                catch(Throwable webpFailure){failure=webpFailure;}
            }
            if(next==null){
                try(InputStream stream=context.getAssets().open("station-ui-r42/"+asset+".gif")){
                    movie=Movie.decodeStream(stream);if(movie==null)throw new IOException("GIF decoder returned no frames");
                }catch(Throwable gifFailure){if(failure==null)failure=gifFailure;else failure.addSuppressed(gifFailure);}
            }
            final Drawable result=next;final Movie old=movie;final Throwable problem=failure;
            post(()->{
                boolean available=result!=null||old!=null;fallbackPlayback.finishLoad(available);
                if(!available){
                    if(UNAVAILABLE.add(asset))android.util.Log.w("StationIllustration","Local animation unavailable: "+asset,problem);
                    invalidate();return;
                }
                drawable=result;fallback=old;fallbackPlayback.resetPlayback();
                if(fallback!=null)setLayerType(View.LAYER_TYPE_SOFTWARE,null);
                if(drawable!=null&&isAttachedToWindow())drawable.setCallback(this);motion();invalidate();
            });
        });
    }
    private static final class Api28 {
        static Drawable decode(Context context,String asset,int targetWidth,int targetHeight)throws IOException{
            Drawable drawable=android.graphics.ImageDecoder.decodeDrawable(
                    android.graphics.ImageDecoder.createSource(context.getAssets(),"station-ui-r42/"+asset+".webp"),
                    (decoder,info,source)->{
                        int width=info.getSize().getWidth(),height=info.getSize().getHeight();
                        float scale=Math.min(1f,Math.min(targetWidth/(float)width,targetHeight/(float)height));
                        if(scale<1f)decoder.setTargetSize(Math.max(1,Math.round(width*scale)),Math.max(1,Math.round(height*scale)));
                    });
            if(drawable instanceof AnimatedImageDrawable)((AnimatedImageDrawable)drawable).setRepeatCount(AnimatedImageDrawable.REPEAT_INFINITE);
            return drawable;
        }
    }
    private void motion(){
        boolean visibleNow=visible(),play=mayAnimate();
        if(visibleNow)load();
        if(drawable instanceof Animatable){
            Animatable animation=(Animatable)drawable;
            if(play&&!animation.isRunning())animation.start();else if(!play&&animation.isRunning())animation.stop();
        }
        fallbackPlayback.setRunning(play&&fallback!=null,SystemClock.uptimeMillis());
        if(fallbackPlayback.shouldContinue())invalidate();
    }
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);int width=drawable!=null?drawable.getIntrinsicWidth():fallback!=null?fallback.width():0;
        int height=drawable!=null?drawable.getIntrinsicHeight():fallback!=null?fallback.height():0;
        if(width<=0||height<=0)return;
        float scale=Math.min((float)getWidth()/width,(float)getHeight()/height);
        int x=(int)((getWidth()-width*scale)*.5f),y=(int)((getHeight()-height*scale)*.5f);
        if(drawable!=null){drawable.setBounds(x,y,x+(int)(width*scale),y+(int)(height*scale));drawable.draw(canvas);}
        else{
            fallback.setTime(fallbackPlayback.frameTime(SystemClock.uptimeMillis(),fallback.duration()));
            int save=canvas.save();canvas.translate(x,y);canvas.scale(scale,scale);fallback.draw(canvas,0,0);canvas.restoreToCount(save);
            if(fallbackPlayback.shouldContinue())postInvalidateDelayed(34);
        }
    }
    @Override protected boolean verifyDrawable(Drawable d){return d==drawable||super.verifyDrawable(d);}
    @Override protected void onAttachedToWindow(){
        super.onAttachedToWindow();
        if(drawable!=null)drawable.setCallback(this);
        try{getContext().getContentResolver().registerContentObserver(Settings.Global.getUriFor(Settings.Global.ANIMATOR_DURATION_SCALE),false,animatorScaleObserver);observerRegistered=true;}
        catch(RuntimeException e){observerRegistered=false;}
        motion();
    }
    @Override protected void onDetachedFromWindow(){
        fallbackPlayback.setRunning(false,SystemClock.uptimeMillis());
        if(observerRegistered){try{getContext().getContentResolver().unregisterContentObserver(animatorScaleObserver);}catch(RuntimeException ignored){}observerRegistered=false;}
        if(drawable instanceof Animatable)((Animatable)drawable).stop();
        if(drawable!=null){unscheduleDrawable(drawable);drawable.setCallback(null);}super.onDetachedFromWindow();
    }
    @Override protected void onVisibilityChanged(View v,int visibility){super.onVisibilityChanged(v,visibility);motion();}
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);motion();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);motion();}
}
