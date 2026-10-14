package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RadialGradient;
import android.graphics.Rect;
import android.graphics.Shader;
import android.view.View;
import org.emulationstation.frontend.station.StationGraphicsPreferences;

/** The room keeps its cached sky and draws the selected online ribbons only while visible. */
final class StationHyperspaceView extends View implements StationGraphicsPreferences.Listener,Runnable,SharedPreferences.OnSharedPreferenceChangeListener {
    private static final long FRAME_MILLIS=34L;
    private static final int SAMPLES=24;
    private static final int[] BLUE_TOP={0x60184477,0x58327dbd,0x5089d2f2};
    private static final int[] BLUE_BOTTOM={0x28102c53,0x24205884,0x205b98b5};
    private static final int[] DARK_TOP={0x602b65ae,0x584a9cd9,0x50a1dcf5};
    private static final int[] DARK_BOTTOM={0x281b416f,0x24316b98,0x206f9fb5};
    private static final double[] PHASE_SPEED={.68d,.84d,.76d};
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
    private final Rect source=new Rect(),target=new Rect();
    private final Paint[] ribbonPaints={new Paint(Paint.ANTI_ALIAS_FLAG),new Paint(Paint.ANTI_ALIAS_FLAG),new Paint(Paint.ANTI_ALIAS_FLAG)};
    private final Path[] ribbonPaths={new Path(),new Path(),new Path()};
    private final SharedPreferences appearance;
    private Bitmap background;
    private StationGraphicsPreferences graphics;
    private boolean attached,resumed,framePending,blueTheme;
    private long lastFrameNanos;
    private double motionSeconds;

    @Override public void run(){
        framePending=false;
        if(!mayAnimate()){lastFrameNanos=0L;return;}
        long now=System.nanoTime();
        if(lastFrameNanos!=0L)motionSeconds+=Math.min(.1d,(now-lastFrameNanos)/1_000_000_000d);
        lastFrameNanos=now;
        invalidate();
        schedule();
    }

    StationHyperspaceView(Context context){
        super(context);graphics=StationGraphicsPreferences.get(context);appearance=context.getSharedPreferences("station_appearance",Context.MODE_PRIVATE);
        blueTheme=appearance.getInt("theme",0)==1;
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);setFocusable(false);setClickable(false);
    }

    void setResumed(boolean value){resumed=value;if(value)readTheme();reconcile();}

    @Override protected void onSizeChanged(int width,int height,int oldWidth,int oldHeight){
        super.onSizeChanged(width,height,oldWidth,oldHeight);
        if(width<=0||height<=0||!allowed()){background=null;return;}
        int renderWidth=StationHyperspaceState.renderWidth(width,height);
        int renderHeight=StationHyperspaceState.renderHeight(width,height);
        background=renderBackground(renderWidth,renderHeight);
        updateRibbonShaders(height);
    }

    private Bitmap renderBackground(int width,int height){
        Bitmap bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(bitmap);

        paint.setStyle(Paint.Style.FILL);paint.setAlpha(255);
        paint.setShader(new LinearGradient(0,0,width,height,0xff226fa7,0xff509acc,Shader.TileMode.CLAMP));
        canvas.drawRect(0,0,width,height,paint);

        paint.setShader(new RadialGradient(width*.72f,height*.52f,Math.max(width,height)*.62f,
                new int[]{0x281d73a3,0x120c405f,Color.TRANSPARENT},new float[]{0f,.46f,1f},Shader.TileMode.CLAMP));
        canvas.drawRect(0,0,width,height,paint);paint.setShader(null);

        if(!onlineMode()){
            drawWave(canvas,width,height,.48f,.055f,0x174e9bd4,14f);
            drawWave(canvas,width,height,.54f,.075f,0x224ba7dc,7f);
            drawWave(canvas,width,height,.60f,.095f,0x3a9edcf4,2.2f);
            drawWave(canvas,width,height,.66f,.070f,0x2492caeb,1.3f);
        }
        return bitmap;
    }

    private void readTheme(){
        boolean next=appearance.getInt("theme",0)==1;
        if(next!=blueTheme){blueTheme=next;updateRibbonShaders(getHeight());invalidate();}
    }
    @Override public void onSharedPreferenceChanged(SharedPreferences saved,String key){if(attached&&"theme".equals(key))readTheme();}

    private void updateRibbonShaders(int height){
        if(height<=0)return;
        int[] tops=blueTheme?BLUE_TOP:DARK_TOP,bottoms=blueTheme?BLUE_BOTTOM:DARK_BOTTOM;
        for(int layer=0;layer<ribbonPaints.length;layer++){
            Paint ribbon=ribbonPaints[layer];ribbon.setStyle(Paint.Style.FILL);
            ribbon.setShader(new LinearGradient(0,height*.40f,0,height*.90f,tops[layer],bottoms[layer],Shader.TileMode.CLAMP));
        }
    }

    private void drawOnlineRibbons(Canvas canvas){
        float width=getWidth(),height=getHeight();
        double t=motionSeconds;
        for(int layer=0;layer<ribbonPaths.length;layer++){
            double drift=.25d*Math.sin(t*(.067d+.013d*layer)+layer*1.73d);
            double primary=t*PHASE_SPEED[layer]+drift+layer*1.15d;
            double secondary=t*PHASE_SPEED[layer]*.73d+drift*.55d+layer*.6d;
            double envelope=1d+.20d*Math.sin(t*(.11d+.023d*layer)+layer*2.07d);
            double bob=.014d*Math.sin(t*(.19d+.027d*layer)+layer*1.41d);
            Path path=ribbonPaths[layer];path.reset();
            for(int point=0;point<=SAMPLES;point++){
                double u=point/(double)SAMPLES;
                double curve=envelope*(Math.sin(u*Math.PI*2d+primary)*.055d+Math.sin(u*Math.PI+secondary)*.035d);
                float x=(float)(width*u),y=(float)(height*(.59d+layer*.055d+bob+curve));
                if(point==0)path.moveTo(x,y);else path.lineTo(x,y);
            }
            path.lineTo(width,height);path.lineTo(0,height);path.close();
            canvas.drawPath(path,ribbonPaints[layer]);
        }
    }

    private void drawWave(Canvas canvas,int width,int height,float center,float amplitude,int color,float stroke){
        float y=center*height,a=amplitude*height;
        Path path=new Path();path.moveTo(-width*.05f,y+a*.45f);
        path.cubicTo(width*.16f,y-a,width*.34f,y-a,width*.52f,y);
        path.cubicTo(width*.70f,y+a,width*.86f,y+a*.72f,width*1.05f,y-a*.28f);
        paint.setStyle(Paint.Style.STROKE);paint.setStrokeCap(Paint.Cap.ROUND);paint.setStrokeWidth(stroke);paint.setColor(color);paint.setAlpha(Color.alpha(color));
        canvas.drawPath(path,paint);
    }

    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);
        if(background==null)canvas.drawColor(0xff226fa7);
        else{
            source.set(0,0,background.getWidth(),background.getHeight());target.set(0,0,getWidth(),getHeight());
            paint.setStyle(Paint.Style.FILL);paint.setShader(null);paint.setAlpha(255);canvas.drawBitmap(background,source,target,paint);
        }
        if(onlineMode()&&getWidth()>0&&getHeight()>0)drawOnlineRibbons(canvas);
    }

    private boolean onlineMode(){return graphics!=null&&graphics.effectiveBackgroundMode()==StationGraphicsPreferences.ONLINE_WAVES;}
    private boolean allowed(){return graphics!=null&&(graphics.effectiveBackgroundMode()==StationGraphicsPreferences.SKY||graphics.effectiveBackgroundMode()==StationGraphicsPreferences.ONLINE_WAVES);}
    private void ensureBackground(){if(background==null&&allowed()&&getWidth()>0&&getHeight()>0)background=renderBackground(StationHyperspaceState.renderWidth(getWidth(),getHeight()),StationHyperspaceState.renderHeight(getWidth(),getHeight()));}
    private boolean mayAnimate(){return attached&&resumed&&onlineMode()&&isShown()&&getWindowVisibility()==VISIBLE&&hasWindowFocus()&&getWidth()>0&&getHeight()>0;}
    private void schedule(){if(!framePending&&mayAnimate()){framePending=true;postDelayed(this,FRAME_MILLIS);}}
    private void reconcile(){if(mayAnimate())schedule();else{removeCallbacks(this);framePending=false;lastFrameNanos=0L;}}
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();attached=true;graphics.addListener(this);appearance.registerOnSharedPreferenceChangeListener(this);readTheme();ensureBackground();reconcile();}
    @Override protected void onDetachedFromWindow(){attached=false;removeCallbacks(this);framePending=false;lastFrameNanos=0L;appearance.unregisterOnSharedPreferenceChangeListener(this);graphics.removeListener(this);background=null;super.onDetachedFromWindow();}
    @Override protected void onVisibilityChanged(View changed,int visibility){super.onVisibilityChanged(changed,visibility);if(graphics!=null)reconcile();}
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);if(graphics!=null)reconcile();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);reconcile();}
    @Override public void onGraphicsChanged(StationGraphicsPreferences.State state){background=null;ensureBackground();updateRibbonShaders(getHeight());reconcile();invalidate();}
}
