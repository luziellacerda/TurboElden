package org.emulationstation.frontend.netplay;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Presentation only. The caller retains the engine's original exit callback. */
final class StationExitPanel {
    static AlertDialog create(Activity activity,Runnable exit){
        return panel(activity,"Partida online","Continue jogando ou volte às salas.",
                "Continuar",StationActionButton.PRIMARY,StationSocialIcon.PLAY,
                "Voltar às salas",StationSocialIcon.EXIT,exit,
                "Ao sair, sua participação nesta partida termina.",false);
    }
    static AlertDialog confirm(Activity activity,Runnable exit){
        return panel(activity,"Sair da partida?","Você encerra sua participação e volta às salas.",
                "Continuar",StationActionButton.PRIMARY,StationSocialIcon.PLAY,
                "Sair da partida",StationSocialIcon.EXIT,exit,
                "Os demais jogadores serão informados da sua saída.",true);
    }
    private static AlertDialog panel(Activity activity,String heading,String description,
            String backLabel,int backTone,int backIcon,String exitLabel,int exitIcon,Runnable exit,String note,boolean confirming){
        float density=activity.getResources().getDisplayMetrics().density;
        int displayWidth=activity.getResources().getDisplayMetrics().widthPixels;
        int width=Math.min(Math.round(420*density),Math.max(1,displayWidth-Math.round(32*density)));
        boolean stacked=width<Math.round(360*density)||activity.getResources().getConfiguration().fontScale>1.25f;
        LinearLayout surface=new LinearLayout(activity);surface.setOrientation(LinearLayout.VERTICAL);
        int pad=Math.round(20*density);surface.setPadding(pad,pad,pad,Math.round(12*density));
        surface.setBackground(face(density,0xff101722,0xff304258,10));
        LinearLayout body=new LinearLayout(activity);body.setOrientation(LinearLayout.VERTICAL);
        LinearLayout headingRow=new LinearLayout(activity);headingRow.setOrientation(LinearLayout.HORIZONTAL);headingRow.setGravity(Gravity.CENTER_VERTICAL);
        TextView eyebrow=text(activity,confirming?"CONFIRMAR SAÍDA":"MENU DA PARTIDA",10,0xff46dbff);eyebrow.setLetterSpacing(.10f);
        headingRow.addView(eyebrow,new LinearLayout.LayoutParams(0,-2,1));
        ImageView symbol=new ImageView(activity);symbol.setImageDrawable(new StationSocialIcon(confirming?StationSocialIcon.EXIT:StationSocialIcon.PLAY,Math.round(24*density),confirming?0xffffc3cb:0xff46dbff));
        symbol.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        headingRow.addView(symbol,new LinearLayout.LayoutParams(Math.round(24*density),Math.round(24*density)));body.addView(headingRow);
        TextView title=text(activity,heading,22,0xffeff5ff);title.setPadding(0,Math.round(8*density),0,Math.round(9*density));body.addView(title);
        TextView hint=text(activity,description,14,0xffd9e7f3);hint.setLineSpacing(2*density,1);body.addView(hint);
        if(!note.isEmpty()){TextView footnote=text(activity,note,12,0xffa7b7cf);footnote.setLineSpacing(2*density,1);footnote.setPadding(0,Math.round(9*density),0,0);body.addView(footnote);}
        ScrollView scroll=new ScrollView(activity);scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(false);scroll.addView(body);
        surface.addView(scroll,new LinearLayout.LayoutParams(-1,-2,1));
        AlertDialog dialog=new AlertDialog.Builder(activity).setView(surface).create();
        View separator=new View(activity);separator.setBackgroundColor(0xff273448);
        LinearLayout.LayoutParams separatorSize=new LinearLayout.LayoutParams(-1,Math.max(1,Math.round(density)));separatorSize.topMargin=Math.round(16*density);surface.addView(separator,separatorSize);
        LinearLayout actions=new LinearLayout(activity);actions.setGravity(Gravity.CENTER_VERTICAL);actions.setOrientation(stacked?LinearLayout.VERTICAL:LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams actionSize=new LinearLayout.LayoutParams(-1,stacked?-2:Math.round(48*density));actionSize.topMargin=Math.round(8*density);surface.addView(actions,actionSize);
        StationActionButton back=action(activity,actions,backLabel,backTone,backIcon,0,stacked,()->dialog.dismiss());
        action(activity,actions,exitLabel,StationActionButton.DANGER,exitIcon,Math.round(8*density),stacked,()->{dialog.dismiss();exit.run();});
        dialog.setOnShowListener(d->{
            Window w=dialog.getWindow();if(w==null)return;w.setBackgroundDrawableResource(android.R.color.transparent);w.setDimAmount(.72f);
            w.setLayout(width,-2);w.getDecorView().setSystemUiVisibility(5894);back.requestFocus();
            w.getDecorView().post(()->{if(!dialog.isShowing())return;int maximum=Math.max(1,activity.getResources().getDisplayMetrics().heightPixels-Math.round(32*density));if(w.getDecorView().getHeight()>maximum)w.setLayout(width,maximum);});
        });
        return dialog;
    }
    private static TextView text(Activity a,String value,int size,int color){TextView t=new TextView(a);t.setText(value);t.setTextColor(color);t.setTextSize(size);t.setTypeface(Typeface.create(size>=20?"sans-serif-medium":"sans-serif",0));t.setIncludeFontPadding(false);return t;}
    private static GradientDrawable face(float d,int fill,int border,int radius){GradientDrawable g=new GradientDrawable();g.setColor(fill);g.setStroke(Math.max(1,(int)d),border);g.setCornerRadius(radius*d);return g;}
    private static StationActionButton action(Activity a,LinearLayout row,String title,int tone,int icon,int margin,boolean stacked,Runnable action){
        StationActionButton button=new StationActionButton(a,title,tone,icon);
        float density=a.getResources().getDisplayMetrics().density;
        LinearLayout.LayoutParams lp=stacked?new LinearLayout.LayoutParams(-1,Math.round(48*density)):new LinearLayout.LayoutParams(0,-1,1);
        if(stacked)lp.topMargin=margin;else lp.leftMargin=margin;row.addView(button,lp);
        button.setContentDescription(title);button.setOnClickListener(v->action.run());return button;
    }
}
