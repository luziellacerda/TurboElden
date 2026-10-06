package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Compact actions beside the existing cached cover; owns no bitmap, timer or decoder. */
final class StationCreateGameCard extends LinearLayout {
    final LinearLayout actions;
    private final FrameLayout art;
    private final ImageView cover;
    private final TextView placeholder;
    private String gameName = "Jogo não selecionado";

    StationCreateGameCard(Context context) {
        super(context);
        setGravity(Gravity.CENTER_VERTICAL);
        setPadding(0, dp(8), 0, dp(4));
        actions = new LinearLayout(context);
        actions.setOrientation(VERTICAL);
        addView(actions, new LayoutParams(0, LayoutParams.WRAP_CONTENT));
        art = new FrameLayout(context);
        art.setPadding(dp(12), dp(8), dp(12), dp(8));
        addView(art, new LayoutParams(0, dp(192), 1));
        placeholder = new TextView(context);
        placeholder.setText("Capa indisponível");
        placeholder.setTextColor(0xff9aaab2);
        placeholder.setTextSize(12);
        placeholder.setGravity(Gravity.CENTER);
        art.addView(placeholder, new FrameLayout.LayoutParams(-1, -1));
        cover = new ImageView(context);
        cover.setScaleType(ImageView.ScaleType.FIT_CENTER);
        cover.setBackgroundColor(Color.TRANSPARENT);
        cover.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        art.addView(cover, new FrameLayout.LayoutParams(-1, -1));
    }

    private int dp(float value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override protected void onMeasure(int widthSpec, int heightSpec) {
        int width = Math.max(0, MeasureSpec.getSize(widthSpec) - getPaddingLeft() - getPaddingRight());
        boolean stacked = width < dp(300);
        setOrientation(stacked ? VERTICAL : HORIZONTAL);
        LayoutParams buttons = (LayoutParams) actions.getLayoutParams();
        buttons.width = stacked ? width : Math.min(dp(280), Math.round(width * .56f));
        buttons.weight = 0;
        LayoutParams artwork = (LayoutParams) art.getLayoutParams();
        artwork.width = stacked ? width : 0;
        artwork.weight = stacked ? 0 : 1;
        artwork.height = stacked ? dp(144) : Math.min(dp(216), Math.max(dp(160), width / 3));
        artwork.leftMargin = stacked ? 0 : dp(16);
        super.onMeasure(widthSpec, heightSpec);
    }

    void setGameName(String name) {
        gameName = name == null || name.isEmpty() ? "Jogo não selecionado" : name;
        art.setContentDescription("Capa de " + gameName);
    }

    void setCover(Bitmap bitmap) {
        cover.setImageBitmap(bitmap);
        placeholder.setVisibility(bitmap == null ? View.VISIBLE : View.GONE);
    }
}
