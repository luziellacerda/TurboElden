package org.emulationstation.frontend.netplay;

import android.content.Context;
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

/**
 * Static PSP-style waves for the online menu.
 *
 * The complete image is rasterized only when the View receives a new size.
 * There is no clock, render thread, animation callback or periodic invalidation.
 */
final class StationHyperspaceView extends View {
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
    private final Rect source=new Rect(),target=new Rect();
    private Bitmap background;

    StationHyperspaceView(Context context){
        super(context);setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);setFocusable(false);setClickable(false);
    }

    /** Kept for StationRoomsActivity compatibility; the background is static. */
    void setResumed(boolean value){}

    @Override protected void onSizeChanged(int width,int height,int oldWidth,int oldHeight){
        super.onSizeChanged(width,height,oldWidth,oldHeight);
        if(width<=0||height<=0){background=null;return;}
        int renderWidth=StationHyperspaceState.renderWidth(width,height);
        int renderHeight=StationHyperspaceState.renderHeight(width,height);
        background=renderBackground(renderWidth,renderHeight);
    }

    private Bitmap renderBackground(int width,int height){
        Bitmap bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(bitmap);

        paint.setStyle(Paint.Style.FILL);paint.setAlpha(255);
        paint.setShader(new LinearGradient(0,0,width,height,0xff02040a,0xff071421,Shader.TileMode.CLAMP));
        canvas.drawRect(0,0,width,height,paint);

        paint.setShader(new RadialGradient(width*.72f,height*.52f,Math.max(width,height)*.62f,
                new int[]{0x281d73a3,0x120c405f,Color.TRANSPARENT},new float[]{0f,.46f,1f},Shader.TileMode.CLAMP));
        canvas.drawRect(0,0,width,height,paint);paint.setShader(null);

        drawWave(canvas,width,height,.48f,.055f,0x174e9bd4,14f);
        drawWave(canvas,width,height,.54f,.075f,0x224ba7dc,7f);
        drawWave(canvas,width,height,.60f,.095f,0x3a9edcf4,2.2f);
        drawWave(canvas,width,height,.66f,.070f,0x2492caeb,1.3f);
        return bitmap;
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
        if(background==null){canvas.drawColor(0xff02040a);return;}
        source.set(0,0,background.getWidth(),background.getHeight());target.set(0,0,getWidth(),getHeight());
        paint.setStyle(Paint.Style.FILL);paint.setShader(null);paint.setAlpha(255);canvas.drawBitmap(background,source,target,paint);
    }

    @Override protected void onDetachedFromWindow(){background=null;super.onDetachedFromWindow();}
}
