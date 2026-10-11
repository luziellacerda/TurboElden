package org.emulationstation.frontend.sony;

import android.content.Context;
import android.graphics.*;
import android.view.MotionEvent;
import android.view.View;
import android.util.SparseArray;
import java.util.ArrayList;

/** Static, input-driven pad. No animation timer; physical controllers hide this entire view. */
final class Ps4Touch extends View {
    interface Target {void snapshot(long buttons,int lx,int ly,int rx,int ry);void clear();}
    private final Target target;
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final ArrayList<Button> buttons=new ArrayList<>();
    private final SparseArray<PointF> pointers=new SparseArray<>();
    private final SparseArray<Integer> sticks=new SparseArray<>();
    private final RectF left=new RectF(),right=new RectF();
    private final float unit;
    private static final class Button {final RectF bounds;final String name;final int mask;Button(RectF bounds,String name,int mask){this.bounds=bounds;this.name=name;this.mask=mask;}}
    Ps4Touch(Context context,Target target) {super(context);this.target=target;unit=context.getResources().getDisplayMetrics().density;setFocusable(false);}
    @Override protected void onSizeChanged(int width,int height,int oldWidth,int oldHeight) {
        buttons.clear();float size=48*unit,gap=7*unit,pad=20*unit,bottom=height-20*unit;
        float dx=pad+size,dy=bottom-size*2.5f;
        button(dx,dy-size-gap,size,"▲",0x10);button(dx-size-gap,dy,size,"◀",0x80);
        button(dx+size+gap,dy,size,"▶",0x20);button(dx,dy+size+gap,size,"▼",0x40);
        float fx=width-pad-size*2,fy=dy;
        button(fx,fy-size-gap,size,"△",0x1000);button(fx-size-gap,fy,size,"□",0x8000);
        button(fx+size+gap,fy,size,"○",0x2000);button(fx,fy+size+gap,size,"×",0x4000);
        button(pad,24*unit,size,"L2",0x100);button(pad+size+gap,24*unit,size,"L1",0x400);
        button(width-pad-size*2-gap,24*unit,size,"R1",0x800);button(width-pad-size,24*unit,size,"R2",0x200);
        float center=width/2f;
        button(center-size*1.2f,24*unit,size,"Touch",0x100000);button(center+size*.2f,24*unit,size,"Opções",8);
        float stick=62*unit,centerY=bottom-stick;
        left.set(center-160*unit-stick,centerY-stick,center-160*unit+stick,centerY+stick);
        right.set(center+160*unit-stick,centerY-stick,center+160*unit+stick,centerY+stick);
        button(left.centerX()-size/2,left.top-40*unit,32*unit,"L3",2);
        button(right.centerX()-size/2,right.top-40*unit,32*unit,"R3",4);
    }
    private void button(float x,float y,float size,String name,int mask) {buttons.add(new Button(new RectF(x,y,x+size,y+size),name,mask));}
    @Override protected void onDraw(Canvas canvas) {
        paint.setTypeface(Typeface.create(Typeface.SANS_SERIF,Typeface.BOLD));paint.setTextAlign(Paint.Align.CENTER);
        for(Button button:buttons) {
            boolean pressed=false;for(int i=0;i<pointers.size();i++)if(button.bounds.contains(pointers.valueAt(i).x,pointers.valueAt(i).y)){pressed=true;break;}
            paint.setStyle(Paint.Style.FILL);paint.setColor(pressed?0xb066aaff:0x65202a38);canvas.drawRoundRect(button.bounds,12*unit,12*unit,paint);
            paint.setStyle(Paint.Style.STROKE);paint.setStrokeWidth(unit);paint.setColor(0x99bad2ec);canvas.drawRoundRect(button.bounds,12*unit,12*unit,paint);
            paint.setStyle(Paint.Style.FILL);paint.setTextSize((button.name.length()>2?10:23)*unit);paint.setColor(Color.WHITE);
            canvas.drawText(button.name,button.bounds.centerX(),button.bounds.centerY()-(paint.ascent()+paint.descent())/2,paint);
        }
        drawStick(canvas,left,0);drawStick(canvas,right,1);
    }
    private void drawStick(Canvas canvas,RectF area,int index) {
        paint.setStyle(Paint.Style.STROKE);paint.setStrokeWidth(unit);paint.setColor(0x8890adc9);canvas.drawOval(area,paint);
        float x=area.centerX(),y=area.centerY();for(int i=0;i<sticks.size();i++)if(sticks.valueAt(i)==index){PointF p=pointers.get(sticks.keyAt(i));if(p!=null){x=p.x;y=p.y;}}
        paint.setStyle(Paint.Style.FILL);paint.setColor(0x88709cc8);canvas.drawCircle(x,y,18*unit,paint);
    }
    @Override public boolean onTouchEvent(MotionEvent event) {
        int action=event.getActionMasked(),index=event.getActionIndex(),id=event.getPointerId(index);
        if(action==MotionEvent.ACTION_CANCEL){clear();return true;}
        if(action==MotionEvent.ACTION_DOWN||action==MotionEvent.ACTION_POINTER_DOWN) {
            PointF point=new PointF(event.getX(index),event.getY(index));pointers.put(id,point);
            if(left.contains(point.x,point.y))sticks.put(id,0);else if(right.contains(point.x,point.y))sticks.put(id,1);
        } else if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_POINTER_UP){pointers.remove(id);sticks.remove(id);}
        else if(action==MotionEvent.ACTION_MOVE)for(int i=0;i<event.getPointerCount();i++) {
            PointF point=pointers.get(event.getPointerId(i));if(point!=null)point.set(event.getX(i),event.getY(i));
        }
        submit();invalidate();return true;
    }
    private void submit() {
        long mask=0;int lx=128,ly=128,rx=128,ry=128;
        for(int i=0;i<pointers.size();i++) {
            int id=pointers.keyAt(i);PointF point=pointers.valueAt(i);Integer stick=sticks.get(id);
            if(stick==null) {for(Button button:buttons)if(button.bounds.contains(point.x,point.y))mask|=button.mask;}
            else {RectF area=stick==0?left:right;int x=axis(point.x,area.centerX(),area.width()/2),y=axis(point.y,area.centerY(),area.height()/2);
                if(stick==0){lx=x;ly=y;}else{rx=x;ry=y;}}
        }target.snapshot(mask,lx,ly,rx,ry);
    }
    private static int axis(float value,float center,float radius) {return Math.max(0,Math.min(255,Math.round(128+127*(value-center)/radius)));}
    void clear() {pointers.clear();sticks.clear();target.clear();invalidate();}
}
