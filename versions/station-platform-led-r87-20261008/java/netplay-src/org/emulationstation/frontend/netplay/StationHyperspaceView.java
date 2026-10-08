package org.emulationstation.frontend.netplay;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.*;
import android.os.SystemClock;
import android.util.Log;
import android.view.View;
import java.io.InputStream;

/** Static local nebula plus three sparse star layers. No streaks or frame allocations. */
final class StationHyperspaceView extends View {
    private static final int STARS=144,FRAME_MS=40;
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
    private final float[] seedsX=new float[STARS],seedsY=new float[STARS],points=new float[STARS*2];
    private final StationHyperspaceState clock=new StationHyperspaceState();
    private final RectF background=new RectF();
    private final float density;
    private boolean resumed,attached,running;
    private Bitmap nebula;
    private long frames;
    private final Runnable frame=new Runnable(){public void run(){
        if(!eligible()){sync();return;}
        if(!running)return;
        clock.advance(SystemClock.uptimeMillis());frames++;invalidate();postDelayed(this,FRAME_MS);
    }};
    StationHyperspaceView(Context context){
        super(context);density=getResources().getDisplayMetrics().density;
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);setFocusable(false);setClickable(false);
        paint.setStrokeCap(Paint.Cap.ROUND);
        java.util.Random random=new java.util.Random(452026L);
        for(int i=0;i<STARS;i++){seedsX[i]=random.nextFloat();seedsY[i]=random.nextFloat();}
        // Bounded local asset, decoded once per screen. No render-time generation.
        try(InputStream in=context.getAssets().open("station-ui-r45/space-nebula.png")){
            BitmapFactory.Options options=new BitmapFactory.Options();options.inPreferredConfig=Bitmap.Config.RGB_565;
            nebula=BitmapFactory.decodeStream(in,null,options);
        }catch(Exception e){Log.w("StationHyperspace","Local space background unavailable");}
    }
    void setResumed(boolean value){resumed=value;sync();}
    private boolean eligible(){return StationHyperspaceState.mayRun(resumed,attached,isShown(),getWindowVisibility()==VISIBLE,hasWindowFocus(),ValueAnimator.areAnimatorsEnabled());}
    private void sync(){
        boolean next=eligible();if(next==running)return;
        running=next;clock.setActive(next);removeCallbacks(frame);
        Log.i("StationHyperspace",(next?"started":"stopped")+" frames="+frames);
        if(next)post(frame);
    }
    @Override protected void onSizeChanged(int w,int h,int oldW,int oldH){
        super.onSizeChanged(w,h,oldW,oldH);
        if(w<=0||h<=0)return;
        float aspect=nebula==null?2f:nebula.getWidth()/(float)nebula.getHeight();
        float bw=Math.max(w,h*aspect),bh=bw/aspect;
        background.set((w-bw)/2,(h-bh)/2,(w+bw)/2,(h+bh)/2);
    }
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);canvas.drawColor(0xff03050c);
        paint.setAlpha(255);paint.setShader(null);
        if(nebula!=null)canvas.drawBitmap(nebula,null,background,paint);
        // Slow parallax gives depth without a radial pattern of lines.
        float time=clock.seconds(),w=getWidth(),h=getHeight();
        for(int layer=0;layer<3;layer++){
            float drift=time*(layer+1)/120f;
            for(int j=0;j<48;j++){
                int i=layer*48+j;float x=seedsX[i]+drift,y=seedsY[i];x-=Math.floor(x);
                points[i*2]=x*w;points[i*2+1]=y*h;
            }
            int pulse=(int)(10*Math.sin(time*.75+layer*2));
            paint.setColor(layer==0?0xff8ca7ce:layer==1?0xffc3d5ef:0xfff0f5ff);
            paint.setAlpha(76+layer*46+pulse);paint.setStrokeWidth(density*(.4f+layer*.35f));
            canvas.drawPoints(points,layer*96,96,paint);
        }
    }
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();attached=true;sync();}
    @Override protected void onDetachedFromWindow(){attached=false;sync();removeCallbacks(frame);super.onDetachedFromWindow();}
    @Override protected void onVisibilityChanged(View changed,int visibility){super.onVisibilityChanged(changed,visibility);if(frame!=null)sync();}
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);if(frame!=null)sync();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);if(frame!=null)sync();}
}
