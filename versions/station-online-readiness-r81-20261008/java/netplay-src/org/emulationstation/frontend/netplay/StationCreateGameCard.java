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
    private final boolean room;
    private String gameName = "Jogo não selecionado";

    StationCreateGameCard(Context context) {
        this(context, false);
    }

    StationCreateGameCard(Context context, boolean room) {
        super(context);
        this.room = room;
        setGravity(Gravity.CENTER_VERTICAL);
        setPadding(0, 0, 0, 0);
        actions = new LinearLayout(context);
        actions.setOrientation(VERTICAL);
        addView(actions, new LayoutParams(0, LayoutParams.WRAP_CONTENT));
        art = new FrameLayout(context);
        art.setPadding(0, 0, 0, 0);
        addView(art, new LayoutParams(0, LayoutParams.MATCH_PARENT, 1));
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
        boolean stacked = width < dp(340);
        setOrientation(stacked ? VERTICAL : HORIZONTAL);
        LayoutParams buttons = (LayoutParams) actions.getLayoutParams();
        buttons.width = stacked ? width : Math.min(dp(room ? 380 : 300), Math.round(width * (room ? .57f : .48f)));
        buttons.weight = 0;
        // Natural text/button height first; a filled ScrollView supplies the remaining
        // viewport in its second pass. Artwork uses that height instead of a 216dp cap.
        actions.measure(MeasureSpec.makeMeasureSpec(buttons.width, MeasureSpec.EXACTLY),
                MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED));
        int available = MeasureSpec.getMode(heightSpec) == MeasureSpec.UNSPECIFIED ? 0 :
                Math.max(0, MeasureSpec.getSize(heightSpec) - getPaddingTop() - getPaddingBottom());
        LayoutParams artwork = (LayoutParams) art.getLayoutParams();
        artwork.width = stacked ? width : 0;
        artwork.weight = stacked ? 0 : 1;
        artwork.height = stacked ? Math.min(dp(420), Math.round(width * 1.45f)) :
                Math.max(actions.getMeasuredHeight(), available);
        artwork.leftMargin = stacked ? 0 : dp(6);
        artwork.topMargin = stacked ? dp(12) : 0;
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
