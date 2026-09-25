package org.emulationstation.frontend;

import android.app.Activity;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.os.SystemClock;
import android.view.View;
import android.view.ViewGroup;

final class LoadingOverlay extends View {
    private static LoadingOverlay sView;
    private final Paint mArc;
    private final Paint mCaption;
    private int mGradientHeight;
    private String mName;
    private final RectF mOval;
    private final Paint mScrim;
    private final long mStart;
    private final Paint mTitle;
    private final Paint mTrack;

    private LoadingOverlay(Context context, String name) {
        super(context);
        this.mScrim = new Paint();
        this.mTrack = new Paint(1);
        this.mArc = new Paint(1);
        this.mTitle = new Paint(1);
        this.mCaption = new Paint(1);
        this.mOval = new RectF();
        this.mStart = SystemClock.uptimeMillis();
        this.mName = name;
        this.mTrack.setStyle(Paint.Style.STROKE);
        this.mTrack.setColor(822083583);
        this.mArc.setStyle(Paint.Style.STROKE);
        this.mArc.setStrokeCap(Paint.Cap.ROUND);
        this.mArc.setColor(-419430401);
        Typeface typeface = Typeface.DEFAULT;
        try {
            typeface = Typeface.createFromAsset(context.getAssets(), "resources/sst_medium_condensed.ttf");
        } catch (Exception e) {
        }
        this.mTitle.setTypeface(typeface);
        this.mTitle.setColor(-1);
        this.mTitle.setTextAlign(Paint.Align.CENTER);
        this.mCaption.setTypeface(typeface);
        this.mCaption.setColor(-4668720);
        this.mCaption.setTextAlign(Paint.Align.CENTER);
        setClickable(true);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        int width = getWidth();
        int height = getHeight();
        if (this.mGradientHeight != height) {
            this.mGradientHeight = height;
            this.mScrim.setShader(new LinearGradient(0.0f, 0.0f, 0.0f, height, -266989755, -165005936, Shader.TileMode.CLAMP));
        }
        canvas.drawRect(0.0f, 0.0f, width, height, this.mScrim);
        float unit = Math.min(width, height);
        float radius = unit * 0.04f;
        float cx = width * 0.5f;
        float cy = height * 0.5f;
        float stroke = radius * 0.09f;
        this.mTrack.setStrokeWidth(stroke);
        this.mArc.setStrokeWidth(stroke);
        this.mOval.set(cx - radius, cy - radius, cx + radius, cy + radius);
        long elapsed = SystemClock.uptimeMillis() - this.mStart;
        float angle = (elapsed * 0.2865f) % 360.0f;
        canvas.drawCircle(cx, cy, radius, this.mTrack);
        canvas.drawArc(this.mOval, angle, 80.0f, false, this.mArc);
        this.mTitle.setTextSize(0.045f * unit);
        this.mCaption.setTextSize(0.032f * unit);
        float titleY = (2.2f * radius) + cy + this.mTitle.getTextSize();
        if (this.mName != null && !this.mName.isEmpty()) {
            canvas.drawText(this.mName, cx, titleY, this.mTitle);
        }
        canvas.drawText("CARREGANDO", cx, (this.mCaption.getTextSize() * 1.6f) + titleY, this.mCaption);
        postInvalidateOnAnimation();
    }

    static void show(final Activity activity, final String name) {
        if (activity == null) {
            return;
        }
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (LoadingOverlay.sView != null) {
                    LoadingOverlay.sView.mName = name;
                    LoadingOverlay.sView.animate().cancel();
                    LoadingOverlay.sView.setAlpha(1.0f);
                    return;
                }
                LoadingOverlay.sView = new LoadingOverlay(activity, name);
                LoadingOverlay.sView.setAlpha(0.0f);
                activity.addContentView(LoadingOverlay.sView, new ViewGroup.LayoutParams(-1, -1));
                LoadingOverlay.sView.animate().alpha(1.0f).setDuration(160L).start();
            }
        });
    }

    static void hide(Activity activity) {
        if (activity == null) {
            return;
        }
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                final LoadingOverlay view = LoadingOverlay.sView;
                if (view == null) {
                    return;
                }
                LoadingOverlay.sView = null;
                view.animate().alpha(0.0f).setDuration(240L).withEndAction(new Runnable(this) {
                    final RunnableC05142 this$0;

                    {
                        this.this$0 = this;
                    }

                    @Override
                    public void run() {
                        ViewGroup parent = (ViewGroup) view.getParent();
                        if (parent != null) {
                            parent.removeView(view);
                        }
                    }
                }).start();
            }
        });
    }
}
