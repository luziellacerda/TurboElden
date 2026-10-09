package org.emulationstation.frontend.netplay;

import android.content.res.ColorStateList;
import android.graphics.*;
import android.graphics.drawable.Drawable;

/** Consistent 24-unit vectors; no bitmap, timer or per-frame allocations. */
final class StationSocialIcon extends Drawable {
    // Existing kinds 0..6 retain their meanings for legacy callers.
    static final int NONE=-1, ROOM=0, PEOPLE=1, CREATE=2, CHAT=3, CODE=4,
            RECONNECT=5, BACK=6, READY=7, PLAY=8, EXIT=9, SEARCH=10,
            SEND=11, CLOSE=12, COPY=13, NOT_READY=14;
    static final int ROOMS=ROOM, START=PLAY;
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path path=new Path();
    private final int kind,size;
    private final ColorStateList colors;
    private int alpha=255;

    StationSocialIcon(int kind,int size,int color){this(kind,size,ColorStateList.valueOf(color));}
    StationSocialIcon(int kind,int size,ColorStateList colors){
        this.kind=kind;this.size=size;this.colors=colors;
        paint.setColor(colors.getDefaultColor());paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(1.7f);paint.setStrokeCap(Paint.Cap.ROUND);paint.setStrokeJoin(Paint.Join.ROUND);
        setBounds(0,0,size,size);
    }
    @Override public int getIntrinsicWidth(){return size;}
    @Override public int getIntrinsicHeight(){return size;}
    @Override public boolean isStateful(){return colors.isStateful();}
    @Override protected boolean onStateChange(int[] state){
        int color=colors.getColorForState(state,colors.getDefaultColor());
        color=(color&0x00ffffff)|((Color.alpha(color)*alpha/255)<<24);
        if(paint.getColor()==color)return false;
        paint.setColor(color);invalidateSelf();return true;
    }
    @Override public void draw(Canvas canvas){
        if(kind==NONE)return;
        int saved=canvas.save();canvas.translate(getBounds().left,getBounds().top);
        canvas.scale(getBounds().width()/24f,getBounds().height()/24f);
        if(kind==ROOMS){
            canvas.drawRoundRect(3,4,21,20,2,2,paint);canvas.drawLine(8,4,8,20,paint);
            canvas.drawLine(12,9,17,9,paint);canvas.drawLine(12,14,17,14,paint);
        }else if(kind==PEOPLE){
            canvas.drawCircle(9,7,3,paint);canvas.drawArc(3,12,15,24,180,180,false,paint);
            canvas.drawArc(14,4,20,10,-80,160,false,paint);canvas.drawArc(14,12,22,24,180,180,false,paint);
        }else if(kind==CREATE){
            canvas.drawRoundRect(3,3,21,21,3,3,paint);
            canvas.drawLine(7,12,17,12,paint);canvas.drawLine(12,7,12,17,paint);
        }else if(kind==CODE){
            canvas.drawRoundRect(3,5,21,19,2,2,paint);
            canvas.drawLine(9,5,9,8,paint);canvas.drawLine(9,11,9,13,paint);canvas.drawLine(9,16,9,19,paint);
            canvas.drawLine(13,10,17,10,paint);canvas.drawLine(13,14,17,14,paint);
        }else if(kind==RECONNECT){
            canvas.drawArc(4,4,20,20,40,280,false,paint);
            canvas.drawLine(18,3,19,8,paint);canvas.drawLine(19,8,14,8,paint);
        }else if(kind==BACK){
            canvas.drawLine(4,12,20,12,paint);canvas.drawLine(4,12,10,6,paint);canvas.drawLine(4,12,10,18,paint);
        }else if(kind==READY){
            canvas.drawCircle(12,12,9,paint);canvas.drawLine(7,12,10.5f,15.5f,paint);canvas.drawLine(10.5f,15.5f,17,8.5f,paint);
        }else if(kind==NOT_READY){
            canvas.drawCircle(12,12,9,paint);canvas.drawLine(8,12,16,12,paint);
        }else if(kind==START){
            path.reset();path.moveTo(8,4);path.lineTo(20,12);path.lineTo(8,20);path.close();canvas.drawPath(path,paint);
        }else if(kind==EXIT){
            path.reset();path.moveTo(10,4);path.lineTo(4,4);path.lineTo(4,20);path.lineTo(10,20);canvas.drawPath(path,paint);
            canvas.drawLine(9,12,21,12,paint);canvas.drawLine(21,12,16,7,paint);canvas.drawLine(21,12,16,17,paint);
        }else if(kind==SEARCH){
            canvas.drawCircle(10,10,6.5f,paint);canvas.drawLine(15,15,21,21,paint);
        }else if(kind==SEND){
            path.reset();path.moveTo(3,3);path.lineTo(21,12);path.lineTo(3,21);path.lineTo(6,12);path.close();canvas.drawPath(path,paint);
            canvas.drawLine(6,12,21,12,paint);
        }else if(kind==CLOSE){
            canvas.drawLine(6,6,18,18,paint);canvas.drawLine(18,6,6,18,paint);
        }else if(kind==COPY){
            canvas.drawRoundRect(8,7,20,21,2,2,paint);
            path.reset();path.moveTo(15,3);path.lineTo(4,3);path.lineTo(4,16);canvas.drawPath(path,paint);
        }else{
            canvas.drawRoundRect(3,3,21,17,3,3,paint);
            canvas.drawLine(7,17,5,21,paint);canvas.drawLine(5,21,12,17,paint);
            canvas.drawLine(7,8,17,8,paint);canvas.drawLine(7,12,14,12,paint);
        }
        canvas.restoreToCount(saved);
    }
    @Override public void setAlpha(int alpha){this.alpha=alpha;onStateChange(getState());}
    @Override public void setColorFilter(ColorFilter filter){paint.setColorFilter(filter);invalidateSelf();}
    @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
}
