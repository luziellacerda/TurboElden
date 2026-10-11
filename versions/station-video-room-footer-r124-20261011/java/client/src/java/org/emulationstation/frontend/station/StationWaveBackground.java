package org.emulationstation.frontend.station;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Shader;
import android.view.View;

/** Three simple filled ribbons: no per-frame bitmap, blur, texture or shader build. */
public final class StationWaveBackground extends View implements StationGraphicsPreferences.Listener {
    private static final long FRAME_MILLIS = 34L;
    private static final int SAMPLES = 24;
    private final StationGraphicsPreferences preferences;
    private final SharedPreferences appearance;
    private final Paint[] paints = { new Paint(Paint.ANTI_ALIAS_FLAG), new Paint(Paint.ANTI_ALIAS_FLAG), new Paint(Paint.ANTI_ALIAS_FLAG) };
    private final Path[] paths = { new Path(), new Path(), new Path() };
    private boolean attached, connected, framePending, allowed;
    private boolean blue;
    private final SharedPreferences.OnSharedPreferenceChangeListener themeListener = (saved, key) -> {
        if ("theme".equals(key) && attached) { readTheme(); invalidate(); }
    };
    private double phase;
    private long lastFrameNanos;
    private final Runnable frame = new Runnable() {
        @Override public void run() {
            framePending = false;
            if (!mayAnimate()) { lastFrameNanos = 0L; return; }
            long now = System.nanoTime();
            if (lastFrameNanos != 0L) phase = (phase + Math.min(.1d, (now - lastFrameNanos) / 1_000_000_000d) * .35d) % (Math.PI * 2d);
            lastFrameNanos = now;
            invalidate();
            schedule();
        }
    };

    public StationWaveBackground(Context context) {
        super(context);
        preferences = StationGraphicsPreferences.get(context);
        appearance = context.getSharedPreferences("station_appearance", Context.MODE_PRIVATE);
        setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        readPreferences();
        readTheme();
    }

    @Override protected void onSizeChanged(int width, int height, int oldWidth, int oldHeight) {
        super.onSizeChanged(width, height, oldWidth, oldHeight);
        updatePalette(height);
    }

    private void readTheme() {
        boolean nextBlue = appearance.getInt("theme", 0) == 1;
        if (blue == nextBlue) return;
        blue = nextBlue;
        updatePalette(getHeight());
    }
    private void updatePalette(int height) {
        if (height <= 0) return;
        int[] tops = blue ? new int[] { 0x2029acff, 0x185782ff, 0x1838d9e8 }
                : new int[] { 0x203b4b59, 0x18384550, 0x18616b74 };
        int[] bottoms = blue ? new int[] { 0x0833509b, 0x06233573, 0x052087a7 }
                : new int[] { 0x081a2128, 0x061a2027, 0x05303840 };
        for (int i = 0; i < paints.length; i++) {
            paints[i].setShader(new LinearGradient(0, height * .40f, 0, height * .90f, tops[i], bottoms[i], Shader.TileMode.CLAMP));
        }
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawColor(blue ? 0xff050a15 : 0xff000000);
        if (!allowed || getWidth() <= 0 || getHeight() <= 0) return;
        float width = getWidth(), height = getHeight();
        for (int layer = 0; layer < paths.length; layer++) {
            Path path = paths[layer]; path.reset();
            for (int point = 0; point <= SAMPLES; point++) {
                double x = point / (double) SAMPLES;
                double curve = Math.sin(x * Math.PI * 2d + phase + layer * 1.15d) * .055d
                        + Math.sin(x * Math.PI + phase * .7d + layer * .6d) * .035d;
                float y = (float) ((.59d + layer * .055d + curve) * height);
                if (point == 0) path.moveTo(0, y); else path.lineTo((float) (x * width), y);
            }
            path.lineTo(width, height); path.lineTo(0, height); path.close();
            canvas.drawPath(path, paints[layer]);
        }
    }

    private void readPreferences() {
        allowed = preferences.effectiveBackgroundMode() == StationGraphicsPreferences.WAVES;
    }
    private boolean mayAnimate() { return attached && allowed && isShown() && getWindowVisibility() == View.VISIBLE && hasWindowFocus(); }
    private void schedule() {
        if (!framePending && mayAnimate()) { framePending = true; postDelayed(frame, FRAME_MILLIS); }
    }
    private void reconcile() {
        if (mayAnimate()) { lastFrameNanos = 0L; schedule(); }
        else { removeCallbacks(frame); framePending = false; lastFrameNanos = 0L; }
    }
    @Override protected void onAttachedToWindow() {
        super.onAttachedToWindow(); attached = true;
        if (!connected) { preferences.addListener(this); appearance.registerOnSharedPreferenceChangeListener(themeListener); connected = true; }
        readPreferences(); readTheme(); reconcile();
    }
    @Override protected void onDetachedFromWindow() {
        attached = false; removeCallbacks(frame); framePending = false; lastFrameNanos = 0L;
        if (connected) { preferences.removeListener(this); appearance.unregisterOnSharedPreferenceChangeListener(themeListener); connected = false; }
        super.onDetachedFromWindow();
    }
    @Override protected void onVisibilityChanged(View view, int visibility) { super.onVisibilityChanged(view, visibility); if (preferences != null) reconcile(); }
    @Override protected void onWindowVisibilityChanged(int visibility) { super.onWindowVisibilityChanged(visibility); if (preferences != null) reconcile(); }
    @Override public void onWindowFocusChanged(boolean focus) { super.onWindowFocusChanged(focus); reconcile(); }
    @Override public void onGraphicsChanged(StationGraphicsPreferences.State state) {
        post(() -> { if (!attached) return; readPreferences(); reconcile(); invalidate(); });
    }
}
