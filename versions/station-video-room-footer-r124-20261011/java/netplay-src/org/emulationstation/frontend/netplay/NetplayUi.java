package org.emulationstation.frontend.netplay;
import android.app.Activity;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

final class NetplayUi {
    final Activity activity;final LinearLayout content;
    NetplayUi(Activity activity,String title){
        this.activity=activity;activity.getWindow().setStatusBarColor(0xff08120c);activity.getWindow().setNavigationBarColor(0xff08120c);
        ScrollView scroll=new ScrollView(activity);scroll.setFillViewport(true);scroll.setBackgroundColor(0xff08120c);
        content=new LinearLayout(activity);content.setOrientation(LinearLayout.VERTICAL);content.setPadding(dp(24),dp(18),dp(24),dp(24));
        scroll.addView(content,new ScrollView.LayoutParams(-1,-2));activity.setContentView(scroll);
        text("LZ GAMES  /  TURBORAMA",12,0xff62ed8d).setTypeface(null,Typeface.BOLD);
        text(title,27,0xfff0fff4).setTypeface(null,Typeface.BOLD);
    }
    int dp(float value){return(int)(value*activity.getResources().getDisplayMetrics().density+.5f);}
    TextView text(String text,float size,int color){TextView view=new TextView(activity);view.setText(text);view.setTextSize(size);view.setTextColor(color);view.setPadding(0,dp(5),0,dp(7));content.addView(view,new LinearLayout.LayoutParams(-1,-2));return view;}
    Button action(String text,View.OnClickListener listener,boolean prominent){
        Button button=new Button(activity);button.setText(text);button.setAllCaps(false);button.setTextSize(17);button.setTextColor(prominent?0xff06160b:0xffeafff0);button.setMinHeight(dp(52));button.setGravity(Gravity.CENTER);
        GradientDrawable background=new GradientDrawable();background.setCornerRadius(dp(13));background.setColor(prominent?0xff4fde79:0xff142b1d);background.setStroke(dp(1),prominent?0xff8bffa9:0xff2d5d3d);
        button.setBackground(new android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(0x447cffad),background,null));button.setOnClickListener(listener);
        LinearLayout.LayoutParams layout=new LinearLayout.LayoutParams(-1,-2);layout.topMargin=dp(8);content.addView(button,layout);return button;
    }
}
