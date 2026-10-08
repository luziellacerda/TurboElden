package org.emulationstation.frontend.netplay;

import android.content.Context;
import android.graphics.Bitmap;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

/** Dialog content and full-height artwork remain side by side throughout room setup. */
final class StationFlowPanel extends LinearLayout {
    final LinearLayout content;
    private final ScrollView scroll;
    private final FrameLayout art;
    private final StationOnlineCoverView image;
    private final TextView placeholder;
    private float aspect=.66f;
    StationFlowPanel(Context c){
        super(c);setPadding(dp(16),dp(12),dp(16),dp(12));setGravity(Gravity.CENTER_VERTICAL);
        scroll=new ScrollView(c);scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(true);
        content=new LinearLayout(c);content.setOrientation(VERTICAL);content.setPadding(0,0,dp(12),0);
        scroll.addView(content,new ScrollView.LayoutParams(-1,-2));addView(scroll,new LayoutParams(0,-1,1));
        art=new FrameLayout(c);addView(art,new LayoutParams(dp(180),-1));
        placeholder=new TextView(c);placeholder.setText("Capa indisponível");placeholder.setTextColor(0xff9aaab2);placeholder.setTextSize(12);placeholder.setGravity(Gravity.CENTER);art.addView(placeholder,new FrameLayout.LayoutParams(-1,-1));
        image=new StationOnlineCoverView(c);art.addView(image,new FrameLayout.LayoutParams(-1,-1));
    }
    private int dp(float n){return Math.round(n*getResources().getDisplayMetrics().density);}
    void setPlatform(String platform){image.setPlatform(platform);}
    void setCover(Bitmap bitmap,String name){image.setImageBitmap(bitmap);image.setContentDescription("Capa de "+name);placeholder.setVisibility(bitmap==null?View.VISIBLE:View.GONE);if(bitmap!=null){aspect=(float)bitmap.getWidth()/bitmap.getHeight();requestLayout();}}
    @Override protected void onMeasure(int ws,int hs){
        int width=Math.max(0,MeasureSpec.getSize(ws)-getPaddingLeft()-getPaddingRight());
        int height=Math.max(0,MeasureSpec.getSize(hs)-getPaddingTop()-getPaddingBottom());
        boolean stacked=width<dp(430);setOrientation(stacked?VERTICAL:HORIZONTAL);
        LayoutParams left=(LayoutParams)scroll.getLayoutParams(),right=(LayoutParams)art.getLayoutParams();
        left.width=stacked?-1:0;left.height=stacked?0:-1;left.weight=1;
        right.width=stacked?-1:Math.min(StationCoverLayout.width(getResources().getDisplayMetrics().heightPixels,width,dp(240),dp(12)),Math.round(height*aspect));right.height=stacked?Math.min(dp(170),height/3):-1;right.weight=0;
        super.onMeasure(ws,hs);
    }
}
