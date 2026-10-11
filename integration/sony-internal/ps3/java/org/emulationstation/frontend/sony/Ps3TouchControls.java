package org.emulationstation.frontend.sony;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.SparseIntArray;
import android.view.MotionEvent;
import android.view.View;

/** Event-driven static controls; no timer, animation or foreign UI resource dependency. */
final class Ps3TouchControls extends View {
    private final Ps3Input input;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final SparseIntArray pointers = new SparseIntArray();
    private final RectF bounds = new RectF();
    private final int[] ids = {1,2,3,4,5,6,7,8,17,18,19,20,21,22,23,24,25};
    private final String[] labels = {"◀","▲","▶","▼","□","×","○","△","L1","L2","L3","R1","R2","R3","START","SELECT","PS"};
    // Normalized positions keep the central game unobscured.
    private final float[] xs = {.07f,.13f,.19f,.13f,.81f,.87f,.93f,.87f,.055f,.14f,.29f,.945f,.86f,.71f,.56f,.44f,.5f};
    private final float[] ys = {.69f,.58f,.69f,.8f,.69f,.8f,.69f,.58f,.12f,.12f,.83f,.12f,.12f,.83f,.9f,.9f,.12f};
    Ps3TouchControls(Context context, Ps3Input input) { super(context); this.input = input; setFocusable(false); }
    private float radius() { return Math.min(getHeight() * .055f, getWidth() * .037f); }
    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas); float radius = radius();
        paint.setTextSize(radius * .72f); paint.setTextAlign(Paint.Align.CENTER);
        for (int i = 0; i < ids.length; i++) {
            float x = xs[i] * getWidth(), y = ys[i] * getHeight();
            paint.setColor(0x66405065); canvas.drawCircle(x, y, radius, paint);
            paint.setColor(0xccffffff); canvas.drawText(labels[i], x, y - (paint.ascent() + paint.descent()) / 2, paint);
        }
        paint.setColor(0x5535465d); canvas.drawCircle(getWidth()*.29f, getHeight()*.62f, radius*1.3f, paint);
        canvas.drawCircle(getWidth()*.71f, getHeight()*.62f, radius*1.3f, paint);
    }
    private int hit(float x, float y) {
        float radius = radius() * 1.3f;
        for (int i = 0; i < ids.length; i++) if (Math.hypot(x - xs[i]*getWidth(), y - ys[i]*getHeight()) < radius) return ids[i];
        if (Math.hypot(x-getWidth()*.29f,y-getHeight()*.62f)<radius*1.5f) return 100;
        if (Math.hypot(x-getWidth()*.71f,y-getHeight()*.62f)<radius*1.5f) return 101;
        return 0;
    }
    @Override public boolean onTouchEvent(MotionEvent event) {
        int action = event.getActionMasked(), index = event.getActionIndex();
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            int control = hit(event.getX(index), event.getY(index));
            pointers.put(event.getPointerId(index), control);
            if (control < 100) input.control(control, 255);
        }
        if (action == MotionEvent.ACTION_MOVE || action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            for (int i = 0; i < event.getPointerCount(); i++) {
                int control = pointers.get(event.getPointerId(i), 0);
                if (control == 100 || control == 101) {
                    int base = control == 100 ? 9 : 13;
                    float center = control == 100 ? .29f : .71f;
                    float x = Math.max(-1,Math.min(1,(event.getX(i)-getWidth()*center)/(radius()*1.3f)));
                    float y = Math.max(-1,Math.min(1,(event.getY(i)-getHeight()*.62f)/(radius()*1.3f)));
                    input.control(base, x < -.1f ? Math.round(-x*255) : 0);
                    input.control(base+2, x > .1f ? Math.round(x*255) : 0);
                    input.control(base+1, y < -.1f ? Math.round(-y*255) : 0);
                    input.control(base+3, y > .1f ? Math.round(y*255) : 0);
                }
            }
        }
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP) {
            int pointer = event.getPointerId(index), control = pointers.get(pointer, 0); pointers.delete(pointer);
            if (control < 100) { if (pointers.indexOfValue(control) < 0) input.control(control, 0); }
            else { int base = control == 100 ? 9 : 13; for (int i = 0; i < 4; i++) input.control(base+i, 0); }
        }
        if (action == MotionEvent.ACTION_CANCEL) release();
        return true;
    }
    void release() { pointers.clear(); input.releaseTouch(); }
}
