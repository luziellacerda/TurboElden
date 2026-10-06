package org.emulationstation.frontend.netplay;
import android.graphics.*;import android.graphics.drawable.Drawable;
/** Lightweight vector icons. No idle animator or bitmap allocations. */
final class StationSocialIcon extends Drawable {
 private final Paint p=new Paint(3);private final int kind,size;StationSocialIcon(int k,int s,int color){kind=k;size=s;p.setColor(color);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.7f);p.setStrokeCap(Paint.Cap.ROUND);setBounds(0,0,s,s);}
 public int getIntrinsicWidth(){return size;}public int getIntrinsicHeight(){return size;}
 public void draw(Canvas c){c.save();c.translate(getBounds().left,getBounds().top);c.scale(getBounds().width()/24f,getBounds().height()/24f);
 if(kind==0){c.drawRoundRect(3,4,21,20,3,3,p);c.drawLine(8,4,8,20,p);c.drawLine(12,9,17,9,p);c.drawLine(12,14,17,14,p);}
 else if(kind==1){c.drawCircle(9,8,3,p);c.drawArc(3,12,15,25,185,170,false,p);c.drawArc(13,5,20,12,-85,170,false,p);c.drawArc(13,12,22,24,190,145,false,p);}
 else if(kind==2){c.drawRoundRect(3,3,21,21,5,5,p);c.drawLine(7,12,17,12,p);c.drawLine(12,7,12,17,p);}
 else{c.drawRoundRect(3,3,21,18,4,4,p);c.drawLine(7,18,5,22,p);c.drawLine(5,22,12,18,p);c.drawLine(7,8,17,8,p);c.drawLine(7,12,14,12,p);}c.restore();}
 public void setAlpha(int a){p.setAlpha(a);}public void setColorFilter(ColorFilter f){p.setColorFilter(f);}public int getOpacity(){return PixelFormat.TRANSLUCENT;}
}
