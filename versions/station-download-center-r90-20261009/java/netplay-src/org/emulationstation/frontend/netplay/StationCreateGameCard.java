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

/** Compact actions beside the existing cached cover; borrows cached artwork; lighting stops with visibility/lifecycle. */
final class StationCreateGameCard extends LinearLayout {
    final LinearLayout actions;
    private final FrameLayout art;
    private final StationOnlineCoverView cover;
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
        cover = new StationOnlineCoverView(context);
        cover.setBackgroundColor(Color.TRANSPARENT);
        cover.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        art.addView(cover, new FrameLayout.LayoutParams(-1, -1));
    }

    private int dp(float value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override protected void onMeasure(int widthSpec, int heightSpec) {
        int width = Math.max(0, MeasureSpec.getSize(widthSpec) - getPaddingLeft() - getPaddingRight());
        boolean stacked = width < dp(430);
        setOrientation(stacked ? VERTICAL : HORIZONTAL);
        int screenHeight=getResources().getDisplayMetrics().heightPixels;
        int artWidth=stacked?Math.min(width,StationCoverLayout.preferredWidth(screenHeight)):
                StationCoverLayout.width(screenHeight,width,dp(220),dp(12));
        LayoutParams buttons=(LayoutParams)actions.getLayoutParams();
        buttons.width=stacked?width:width-artWidth-dp(12);buttons.weight=0;
        actions.measure(MeasureSpec.makeMeasureSpec(buttons.width,MeasureSpec.EXACTLY),
                MeasureSpec.makeMeasureSpec(0,MeasureSpec.UNSPECIFIED));
        LayoutParams artwork=(LayoutParams)art.getLayoutParams();
        artwork.width=artWidth;artwork.weight=0;
        artwork.height=StationCoverLayout.height(artWidth,cover.aspect());
        artwork.leftMargin=stacked?0:dp(12);artwork.topMargin=stacked?dp(12):0;
        artwork.gravity=Gravity.CENTER;
        super.onMeasure(widthSpec, heightSpec);
    }

    void setGameName(String name) {
        gameName = name == null || name.isEmpty() ? "Jogo não selecionado" : name;
        art.setContentDescription("Capa de " + gameName);
    }

    void setPlatform(String platform){cover.setPlatform(platform);}

    void setCover(Bitmap bitmap) {
        cover.setImageBitmap(bitmap);
        placeholder.setVisibility(bitmap == null ? View.VISIBLE : View.GONE);
    }
}
