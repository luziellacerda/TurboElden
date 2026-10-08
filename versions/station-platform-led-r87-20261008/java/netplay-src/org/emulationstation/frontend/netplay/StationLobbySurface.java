package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.graphics.*;
import android.os.SystemClock;
import android.view.View;
import android.widget.LinearLayout;

/** Low-cost header lighting. One 16 fps invalidation only while its window is visible. */
final class StationLobbySurface extends LinearLayout {
    private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path clip=new Path();
    private final RectF rect=new RectF();
    private LinearGradient base,edge;
    private final float d;
    private boolean attached,running;
    private final Runnable frame=new Runnable(){public void run(){if(running){invalidate();postDelayed(this,64);}}};
    StationLobbySurface(Context c){super(c);d=getResources().getDisplayMetrics().density;setWillNotDraw(false);setLayerType(View.LAYER_TYPE_NONE,null);}
    @Override protected void onSizeChanged(int w,int h,int ow,int oh){super.onSizeChanged(w,h,ow,oh);rect.set(d,d,w-d,h-d);clip.reset();clip.addRoundRect(rect,14*d,14*d,Path.Direction.CW);base=new LinearGradient(0,h,w,0,new int[]{0xff12271b,0xff092316,0xff12251a},null,Shader.TileMode.CLAMP);edge=new LinearGradient(0,0,w,0,new int[]{0xff4bdf88,0xff204c32,0xff246541},null,Shader.TileMode.CLAMP);}
    @Override protected void onDraw(Canvas c){
        if(base==null)return;int save=c.save();c.clipPath(clip);p.setShader(base);p.setStyle(Paint.Style.FILL);c.drawRect(rect,p);p.setShader(null);
        p.setStrokeWidth(d);p.setColor(0x124fdf85);
        for(int i=0;i<9;i++){float x=getWidth()*.60f+i*28*d;c.drawLine(x,-10*d,x-42*d,getHeight()+10*d,p);}
        float phase=(SystemClock.uptimeMillis()%6000)/6000f,x=getWidth()*(.38f+phase*.55f);
        p.setColor(0x114cf48d);p.setStrokeWidth(22*d);c.drawLine(x,0,x-42*d,getHeight(),p);
        p.setColor(0x174cf48d);p.setStrokeWidth(6*d);c.drawLine(x,0,x-42*d,getHeight(),p);
        c.restoreToCount(save);p.setShader(edge);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(d);c.drawRoundRect(rect,14*d,14*d,p);p.setShader(null);p.setStyle(Paint.Style.FILL);
        p.setColor(0xff79fda4);c.drawRoundRect(18*d,0,62*d,2*d,d,d,p);
        super.onDraw(c);
    }
    private void sync(){boolean should=attached&&isShown()&&getWindowVisibility()==VISIBLE&&hasWindowFocus();if(should==running)return;running=should;removeCallbacks(frame);if(running)post(frame);}
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();attached=true;sync();}
    @Override protected void onDetachedFromWindow(){attached=false;running=false;removeCallbacks(frame);super.onDetachedFromWindow();}
    @Override protected void onWindowVisibilityChanged(int v){super.onWindowVisibilityChanged(v);if(frame!=null)sync();}
    @Override protected void onVisibilityChanged(View changed,int v){super.onVisibilityChanged(changed,v);if(frame!=null)sync();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);sync();}
}

/** Original vector lobby symbols; no images, fonts or external icon downloads. */
final class StationLobbyIcon extends View {
    private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);private final Path shape=new Path();
    private final int kind;
    StationLobbyIcon(Context c,int kind){super(c);this.kind=kind;setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);}
    @Override protected void onDraw(Canvas c){
        float s=Math.min(getWidth(),getHeight())/80f;c.save();c.translate((getWidth()-80*s)/2,(getHeight()-80*s)/2);c.scale(s,s);
        p.setStyle(Paint.Style.FILL);p.setColor(0xff112f20);c.drawCircle(40,40,36,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1);p.setColor(0xff2a6643);c.drawCircle(40,40,35,p);p.setColor(0xff65ed99);p.setStrokeWidth(2);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
        if(kind==1){c.drawCircle(34,30,8,p);c.drawArc(20,40,49,66,190,160,false,p);p.setColor(0xff398256);c.drawCircle(53,34,6,p);c.drawArc(45,43,67,64,185,140,false,p);}
        else if(kind==3){shape.reset();shape.moveTo(23,25);shape.lineTo(56,25);shape.quadTo(61,25,61,31);shape.lineTo(61,46);shape.quadTo(61,51,55,51);shape.lineTo(38,51);shape.lineTo(27,59);shape.lineTo(27,51);shape.quadTo(20,51,20,45);shape.lineTo(20,32);shape.quadTo(20,25,23,25);c.drawPath(shape,p);for(int i=0;i<3;i++)c.drawCircle(30+i*10,38,1,p);}
        else {shape.reset();shape.moveTo(27,29);shape.cubicTo(20,29,17,40,15,50);shape.cubicTo(12,61,21,61,29,48);shape.lineTo(50,48);shape.cubicTo(60,62,69,60,65,48);shape.cubicTo(62,35,59,29,53,29);shape.close();c.drawPath(shape,p);c.drawLine(27,34,27,44,p);c.drawLine(22,39,32,39,p);c.drawCircle(53,35,1.8f,p);c.drawCircle(58,41,1.8f,p);c.drawLine(35,40,40,40,p);}
        p.setStyle(Paint.Style.FILL);p.setColor(0xff8bffb5);c.drawCircle(64,15,3,p);p.setColor(0x2261ee8a);c.drawCircle(64,15,6,p);c.restore();
    }
}
