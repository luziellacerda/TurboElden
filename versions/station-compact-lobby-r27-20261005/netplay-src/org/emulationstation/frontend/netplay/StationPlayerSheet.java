package org.emulationstation.frontend.netplay;

import android.app.*;
import android.content.*;
import android.graphics.Typeface;
import android.graphics.Color;
import android.graphics.drawable.*;
import android.view.*;
import android.widget.*;

/** Compact, scrollable player profile. Actions remain owned by the signed room controller. */
final class StationPlayerSheet extends Dialog {
    interface Actions {void invite();void code();void block();}
    private final Activity activity;
    private final Actions actions;
    private final LinearLayout content;
    private final ScrollView scroll;
    private final TextView name,status,notice;
    private final int white=0xffeffff3,muted=0xff9eb7aa,green=0xff65ed99;
    StationPlayerSheet(Activity activity,Actions actions){
        super(activity);this.activity=activity;this.actions=actions;
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        LinearLayout root=vertical();root.setPadding(dp(24),dp(16),dp(24),dp(20));root.setBackground(face(0xff0b1410,0xff315441,20));
        LinearLayout heading=new LinearLayout(activity);heading.setGravity(Gravity.CENTER_VERTICAL);root.addView(heading,new LinearLayout.LayoutParams(-1,dp(44)));
        TextView mark=label("LZ GAMES  /  JOGADOR",10,green);mark.setLetterSpacing(.12f);heading.addView(mark,new LinearLayout.LayoutParams(0,-2,1));
        TextView close=label("×",26,muted);close.setGravity(Gravity.CENTER);close.setContentDescription("Fechar perfil do jogador");close.setBackground(new RippleDrawable(android.content.res.ColorStateList.valueOf(0x337fffff),face(0x00101813,0x00283f32,10),null));heading.addView(close,new LinearLayout.LayoutParams(dp(44),dp(44)));close.setOnClickListener(v->dismiss());
        name=label("Jogador",25,white);name.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));name.setMaxLines(2);name.setEllipsize(android.text.TextUtils.TruncateAt.END);root.addView(name,new LinearLayout.LayoutParams(-1,-2));
        status=label("",12,green);status.setPadding(0,dp(7),0,dp(17));root.addView(status);
        View divider=new View(activity);divider.setBackgroundColor(0xff233a2d);root.addView(divider,new LinearLayout.LayoutParams(-1,dp(1)));
        scroll=new ScrollView(activity);scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(true);content=vertical();scroll.addView(content,new ScrollView.LayoutParams(-1,-2));root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        notice=label("",12,green);notice.setPadding(0,dp(10),0,0);notice.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);notice.setVisibility(View.GONE);root.addView(notice,new LinearLayout.LayoutParams(-1,-2));
        setContentView(root);
    }
    private int dp(float n){return(int)(activity.getResources().getDisplayMetrics().density*n+.5f);}
    private LinearLayout vertical(){LinearLayout l=new LinearLayout(activity);l.setOrientation(1);return l;}
    private TextView label(String s,int size,int color){TextView t=new TextView(activity);t.setText(s);t.setTextSize(size);t.setTextColor(color);t.setIncludeFontPadding(false);return t;}
    private GradientDrawable face(int color,int rim,int radius){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));d.setStroke(dp(1),rim);return d;}
    private void field(String label,String value){TextView h=label(label,10,muted);h.setLetterSpacing(.1f);h.setPadding(0,dp(18),0,dp(6));content.addView(h);TextView t=label(value,14,white);t.setLineSpacing(dp(3),1);content.addView(t,new LinearLayout.LayoutParams(-1,-2));}
    private void button(String label,boolean primary,boolean enabled,Runnable action){StationActionButton b=new StationActionButton(activity,label,primary);b.setEnabled(enabled);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(48));p.setMargins(0,dp(10),0,0);content.addView(b,p);b.setOnClickListener(v->action.run());}
    void render(StationPlayerModel model,String gameName,String selectedGame,boolean busy,String feedback){
        int y=scroll.getScrollY();name.setText(model.name);status.setText((model.available?"●  ":"○  ")+model.status);status.setTextColor(model.available?green:muted);
        content.removeAllViews();
        if(!model.roomItemId.isEmpty())field("JOGO NA SALA",gameName);
        else if(!model.self&&model.canInvite)field("SEU CONVITE",selectedGame);
        field("PARTIDA",model.reason);
        if(!model.self)button(busy?"Aguarde…":model.inviteLabel,true,!busy&&model.canInvite,actions::invite);
        if(model.canShare)button("Código da minha sala",false,!busy,actions::code);
        if(!model.self&&model.present){TextView safety=label("Bloquear jogador",12,0xffe89a9a);safety.setGravity(Gravity.CENTER);safety.setContentDescription("Bloquear jogador "+model.name);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(44));p.topMargin=dp(10);content.addView(safety,p);safety.setEnabled(!busy);safety.setAlpha(busy?.45f:1);safety.setOnClickListener(v->actions.block());}
        notice.setText(feedback==null?"":feedback);notice.setVisibility(feedback==null||feedback.isEmpty()?View.GONE:View.VISIBLE);scroll.post(()->scroll.scrollTo(0,y));
    }
    @Override public void show(){super.show();Window w=getWindow();if(w==null)return;w.setBackgroundDrawableResource(android.R.color.transparent);w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);WindowManager.LayoutParams lp=w.getAttributes();lp.width=Math.min(dp(520),activity.getResources().getDisplayMetrics().widthPixels-dp(32));lp.height=Math.min(dp(490),activity.getResources().getDisplayMetrics().heightPixels-dp(32));lp.dimAmount=.7f;lp.gravity=Gravity.CENTER;w.setAttributes(lp);w.getDecorView().setSystemUiVisibility(activity.getWindow().getDecorView().getSystemUiVisibility());}
}
