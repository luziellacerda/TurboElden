package org.emulationstation.frontend.netplay;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Presentation only. The caller retains the engine's original exit callback. */
final class StationExitPanel {
    static AlertDialog create(Activity activity,Runnable exit){
        float density=activity.getResources().getDisplayMetrics().density;
        LinearLayout body=new LinearLayout(activity);body.setOrientation(1);int pad=(int)(22*density);body.setPadding(pad,pad,pad,pad);
        body.setBackground(face(density,0xff0c151b,0xff2c4742,18));
        TextView brand=text(activity,"LZ GAMES  /  TURBOSTATIONS",10,0xff65dda9);brand.setLetterSpacing(.12f);body.addView(brand);
        TextView title=text(activity,"Partida online",24,0xfff1f7f5);title.setPadding(0,(int)(12*density),0,(int)(8*density));body.addView(title);
        TextView description=text(activity,"Voltar às salas encerra sua participação. Seus jogos e configurações locais serão mantidos.",13,0xffaabbbd);description.setLineSpacing(3*density,1);body.addView(description);
        ScrollView scroll=new ScrollView(activity);scroll.setFillViewport(true);scroll.addView(body);
        AlertDialog dialog=new AlertDialog.Builder(activity).setView(scroll).create();
        addAction(activity,body,"▶","Continuar jogando","Fechar este menu e retornar à partida.",0xff65dda9,()->dialog.dismiss());
        addAction(activity,body,"↶","Voltar às salas","Encerrar sua participação nesta partida.",0xffff828b,()->{dialog.dismiss();exit.run();});
        dialog.setOnShowListener(d->{Window w=dialog.getWindow();if(w==null)return;w.setBackgroundDrawableResource(android.R.color.transparent);w.setDimAmount(.72f);int width=Math.min((int)(500*density),(int)(activity.getResources().getDisplayMetrics().widthPixels*.86f));w.setLayout(width,-2);w.getDecorView().setSystemUiVisibility(5894);});
        return dialog;
    }
    private static TextView text(Activity a,String value,int size,int color){TextView t=new TextView(a);t.setText(value);t.setTextColor(color);t.setTextSize(size);t.setTypeface(Typeface.create(size>=20?"sans-serif-medium":"sans-serif",0));t.setIncludeFontPadding(false);return t;}
    private static GradientDrawable face(float d,int fill,int border,int radius){GradientDrawable g=new GradientDrawable();g.setColor(fill);g.setStroke(Math.max(1,(int)d),border);g.setCornerRadius(radius*d);return g;}
    private static void addAction(Activity a,LinearLayout body,String symbol,String title,String detail,int accent,Runnable action){
        float d=a.getResources().getDisplayMetrics().density;LinearLayout row=new LinearLayout(a);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding((int)(14*d),(int)(12*d),(int)(14*d),(int)(12*d));row.setBackground(new RippleDrawable(ColorStateList.valueOf(0x3065dda9),face(d,0xff17252c,0xff30454b,12),null));
        TextView icon=text(a,symbol,24,accent);icon.setGravity(Gravity.CENTER);row.addView(icon,new LinearLayout.LayoutParams((int)(36*d),(int)(40*d)));
        LinearLayout labels=new LinearLayout(a);labels.setOrientation(1);labels.setPadding((int)(12*d),0,0,0);row.addView(labels,new LinearLayout.LayoutParams(0,-2,1));TextView heading=text(a,title,16,accent);labels.addView(heading);TextView hint=text(a,detail,12,0xffaabbbd);hint.setPadding(0,(int)(5*d),0,0);labels.addView(hint);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.topMargin=(int)(12*d);body.addView(row,lp);row.setMinimumHeight((int)(64*d));row.setClickable(true);row.setFocusable(true);row.setContentDescription(title+". "+detail);row.setOnClickListener(v->action.run());
    }
}
