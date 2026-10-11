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
    private boolean viewportBounded;
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

    void setViewportBounded(boolean value){if(viewportBounded!=value){viewportBounded=value;requestLayout();}}

    @Override protected void onMeasure(int widthSpec, int heightSpec) {
        int width = Math.max(0, MeasureSpec.getSize(widthSpec) - getPaddingLeft() - getPaddingRight());
        int gap=Math.min(dp(12),width);
        if(viewportBounded&&MeasureSpec.getMode(heightSpec)!=MeasureSpec.UNSPECIFIED){
            int height=Math.max(0,MeasureSpec.getSize(heightSpec)-getPaddingTop()-getPaddingBottom());
            setOrientation(HORIZONTAL);setGravity(Gravity.TOP);
            StationCoverLayout.Size size=StationCoverLayout.hero(width,height,cover.aspect(),dp(280),gap,dp(224));
            LayoutParams buttons=(LayoutParams)actions.getLayoutParams();
            buttons.width=Math.max(0,width-size.width-gap);buttons.height=height;buttons.weight=0;
            LayoutParams artwork=(LayoutParams)art.getLayoutParams();
            artwork.width=size.width;artwork.height=size.height;
            artwork.weight=0;artwork.leftMargin=gap;artwork.topMargin=0;artwork.gravity=Gravity.TOP;
            super.onMeasure(widthSpec,heightSpec);return;
        }
        // A room in a list is a thumbnail, not another full-screen hero. Own-room
        // setup calls setViewportBounded(true) and keeps the hero branch above.
        setOrientation(HORIZONTAL);setGravity(Gravity.CENTER_VERTICAL);
        int maximumHeight=MeasureSpec.getMode(heightSpec)==MeasureSpec.UNSPECIFIED?dp(240):
                Math.max(0,MeasureSpec.getSize(heightSpec)-getPaddingTop()-getPaddingBottom());
        StationCoverLayout.Size size=room?
                StationCoverLayout.thumbnail(width,cover.aspect(),dp(76),dp(112),gap):
                StationCoverLayout.hero(width,maximumHeight,cover.aspect(),dp(280),gap,dp(224));
        LayoutParams buttons=(LayoutParams)actions.getLayoutParams();
        buttons.width=Math.max(0,width-size.width-gap);buttons.height=LayoutParams.WRAP_CONTENT;buttons.weight=0;
        LayoutParams artwork=(LayoutParams)art.getLayoutParams();
        artwork.width=size.width;artwork.height=size.height;artwork.weight=0;
        artwork.leftMargin=gap;artwork.topMargin=0;artwork.gravity=Gravity.CENTER_VERTICAL;
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
