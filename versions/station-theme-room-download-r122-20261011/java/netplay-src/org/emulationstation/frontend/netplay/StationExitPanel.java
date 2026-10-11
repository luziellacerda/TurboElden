package org.emulationstation.frontend.netplay;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Presentation only. The caller retains the engine's original exit callback. */
final class StationExitPanel {
    static AlertDialog create(Activity activity,Runnable exit){
        return panel(activity,"Partida online","Continue jogando ou volte às salas.",
                "Continuar",StationActionButton.PRIMARY,StationSocialIcon.PLAY,
                "Voltar às salas",StationSocialIcon.EXIT,exit,
                "Ao sair, sua participação na partida termina.");
    }
    static AlertDialog confirm(Activity activity,Runnable exit){
        return panel(activity,"Sair da partida?","Sua saída será informada aos demais jogadores.",
                "Continuar",StationActionButton.SECONDARY,StationSocialIcon.PLAY,
                "Sair da partida",StationSocialIcon.EXIT,exit,"");
    }
    private static AlertDialog panel(Activity activity,String heading,String description,
            String backLabel,int backTone,int backIcon,String exitLabel,int exitIcon,Runnable exit,String note){
        float density=activity.getResources().getDisplayMetrics().density;
        int displayWidth=activity.getResources().getDisplayMetrics().widthPixels;
        int width=Math.min(Math.round(420*density),Math.max(1,displayWidth-Math.round(32*density)));
        boolean stacked=width<Math.round(360*density)||activity.getResources().getConfiguration().fontScale>1.25f;
        LinearLayout body=new LinearLayout(activity);body.setOrientation(1);int pad=Math.round(20*density);body.setPadding(pad,pad,pad,pad);
        body.setBackground(face(density,0xff101722,0xff304258,8));
        TextView eyebrow=text(activity,"MENU DA PARTIDA",10,0xff46dbff);eyebrow.setLetterSpacing(.10f);body.addView(eyebrow);
        TextView title=text(activity,heading,22,0xffeff5ff);title.setPadding(0,Math.round(8*density),0,Math.round(7*density));body.addView(title);
        TextView hint=text(activity,description,13,0xffa7b7cf);hint.setLineSpacing(2*density,1);body.addView(hint);
        ScrollView scroll=new ScrollView(activity);scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(false);scroll.addView(body);
        AlertDialog dialog=new AlertDialog.Builder(activity).setView(scroll).create();
        LinearLayout actions=new LinearLayout(activity);actions.setGravity(Gravity.CENTER_VERTICAL);actions.setOrientation(stacked?LinearLayout.VERTICAL:LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams actionSize=new LinearLayout.LayoutParams(-1,stacked?-2:Math.round(48*density));actionSize.topMargin=Math.round(16*density);body.addView(actions,actionSize);
        StationActionButton back=action(activity,actions,backLabel,backTone,backIcon,0,stacked,()->dialog.dismiss());
        action(activity,actions,exitLabel,StationActionButton.DANGER,exitIcon,Math.round(8*density),stacked,()->{dialog.dismiss();exit.run();});
        if(!note.isEmpty()){TextView footnote=text(activity,note,11,0xffa7b7cf);footnote.setPadding(0,Math.round(8*density),0,0);body.addView(footnote);}
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
