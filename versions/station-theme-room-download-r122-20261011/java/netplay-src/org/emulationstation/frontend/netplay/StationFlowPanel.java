package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.graphics.Bitmap;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

/** Compact, proportional artwork accompanies each step without consuming the dialog. */
final class StationFlowPanel extends LinearLayout {
    final LinearLayout content;
    private final ScrollView scroll;
    private final FrameLayout art;
    private final StationOnlineCoverView image;
    private final TextView placeholder;
    private float aspect=.66f;
    StationFlowPanel(Context c){
        super(c);setPadding(dp(16),dp(12),dp(16),dp(12));setGravity(Gravity.TOP);
        scroll=new ScrollView(c);scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(true);
        content=new LinearLayout(c);content.setOrientation(VERTICAL);content.setPadding(0,0,0,0);
        scroll.addView(content,new ScrollView.LayoutParams(-1,-2));addView(scroll,new LayoutParams(0,-1,1));
        art=new FrameLayout(c);addView(art,new LayoutParams(dp(180),-1));
        placeholder=new TextView(c);placeholder.setText("Capa indisponível");placeholder.setTextColor(0xff9aaab2);placeholder.setTextSize(12);placeholder.setGravity(Gravity.CENTER);art.addView(placeholder,new FrameLayout.LayoutParams(-1,-1));
        image=new StationOnlineCoverView(c);art.addView(image,new FrameLayout.LayoutParams(-1,-1));
    }
    private int dp(float n){return Math.round(n*getResources().getDisplayMetrics().density);}
    void setPlatform(String platform){image.setPlatform(platform);}
    void setCover(Bitmap bitmap,String name){image.setImageBitmap(bitmap);image.setContentDescription("Capa de "+name);placeholder.setVisibility(bitmap==null?View.VISIBLE:View.GONE);aspect=bitmap==null?2f/3f:(float)bitmap.getWidth()/bitmap.getHeight();requestLayout();}
    @Override protected void onMeasure(int ws,int hs){
        int width=Math.max(0,MeasureSpec.getSize(ws)-getPaddingLeft()-getPaddingRight());
        int height=Math.max(0,MeasureSpec.getSize(hs)-getPaddingTop()-getPaddingBottom());
        boolean stacked=width<dp(430);setOrientation(stacked?VERTICAL:HORIZONTAL);
        LayoutParams left=(LayoutParams)scroll.getLayoutParams(),right=(LayoutParams)art.getLayoutParams();
        int gap=Math.min(dp(12),stacked?height:width);
        StationCoverLayout.Size size=stacked?
                StationCoverLayout.fit(Math.min((int)(width*.38f),dp(120)),Math.min(dp(130),height/3),aspect):
                StationCoverLayout.hero(width,height,aspect,dp(280),gap,dp(184));
        if(stacked)gap=StationCoverLayout.gap(dp(12),height,size.height);
        left.width=stacked?width:Math.max(0,width-size.width-gap);
        left.height=stacked?Math.max(0,height-size.height-gap):height;left.weight=0;
        right.width=size.width;right.height=size.height;right.weight=0;
        right.leftMargin=stacked?0:gap;right.topMargin=stacked?gap:0;
        right.gravity=stacked?Gravity.CENTER_HORIZONTAL:Gravity.TOP;
        super.onMeasure(ws,hs);
    }
}
