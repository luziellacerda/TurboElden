package org.emulationstation.frontend;

import android.app.Activity;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.os.SystemClock;
import android.text.TextPaint;
import android.text.TextUtils;
import android.view.View;
import android.view.ViewGroup;

/** Turborama skin for the existing game-loading view. Progress is completed native preparation stages, not elapsed time. */
final class LoadingOverlay extends View {
    private static LoadingOverlay sView;
    private final Paint background=new Paint();
    private final Paint line=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final TextPaint brand=new TextPaint(Paint.ANTI_ALIAS_FLAG);
    private final TextPaint title=new TextPaint(Paint.ANTI_ALIAS_FLAG);
    private final TextPaint caption=new TextPaint(Paint.ANTI_ALIAS_FLAG);
    private final RectF ring=new RectF();
    private final long start=SystemClock.uptimeMillis();
    private String mName,drawnName="",lastName;
    private float unit;
    private int completed;
    private boolean failed;
    private final RectF progressRect=new RectF();
    private static final String[] STAGES={"ABRINDO EMULADOR","CARREGANDO O JOGO","INICIANDO VÍDEO","PRONTO PARA JOGAR"};

    private LoadingOverlay(Context context,String name) {
        super(context);mName=name;
        Typeface font=Typeface.DEFAULT;
        try { font=Typeface.createFromAsset(context.getAssets(),"resources/sst_medium_condensed.ttf"); }
        catch(Exception ignored) {}
        brand.setTypeface(Typeface.create(font,Typeface.BOLD));
        title.setTypeface(font);caption.setTypeface(font);
        for(TextPaint p:new TextPaint[]{brand,title,caption})p.setTextAlign(Paint.Align.CENTER);
        setClickable(true);
        setContentDescription("Turborama. Preparando jogo.");
    }
    @Override protected void onSizeChanged(int w,int h,int oldw,int oldh) {
        unit=Math.min(w,h);
        background.setShader(new RadialGradient(w*.5f,h*.43f,Math.max(w,h)*.62f,
            new int[]{0xff103524,0xff07110b,0xff030504},new float[]{0,.42f,1},Shader.TileMode.CLAMP));
        brand.setTextSize(unit*.066f);brand.setColor(0xfff2fff6);
        title.setTextSize(unit*.036f);title.setColor(0xffe4f3e8);
        caption.setTextSize(unit*.024f);caption.setColor(0xff77dca7);
        lastName=null;
    }
    @Override protected void onDraw(Canvas canvas) {
        float w=getWidth(),h=getHeight(),cx=w*.5f,cy=h*.48f,r=unit*.064f;
        canvas.drawRect(0,0,w,h,background);
        line.setStyle(Paint.Style.FILL);line.setColor(0xff34d399);
        canvas.drawRect(w*.06f,h*.065f,w*.12f,h*.065f+Math.max(2,unit*.003f),line);
        line.setColor(0xffdf3749);
        canvas.drawRect(w*.88f,h*.065f,w*.94f,h*.065f+Math.max(2,unit*.003f),line);
        canvas.drawText("TURBORAMA",cx,h*.28f,brand);
        canvas.drawText("SEU JOGO ESTÁ CHEGANDO",cx,h*.335f,caption);
        line.setStyle(Paint.Style.STROKE);line.setStrokeCap(Paint.Cap.ROUND);
        line.setStrokeWidth(unit*.0055f);line.setColor(0xff183c2a);
        canvas.drawCircle(cx,cy,r,line);
        ring.set(cx-r,cy-r,cx+r,cy+r);
        float angle=((SystemClock.uptimeMillis()-start)%1800)*.2f-90;
        line.setStrokeWidth(unit*.016f);line.setColor(0x2334d399);
        canvas.drawArc(ring,angle,100,false,line);
        line.setStrokeWidth(unit*.0055f);line.setColor(0xff65ee9d);
        canvas.drawArc(ring,angle,100,false,line);
        line.setColor(0xffe34754);
        canvas.drawArc(ring,angle+185,15,false,line);
        line.setStyle(Paint.Style.FILL);line.setColor(0xff34d399);
        float bar=unit*.005f;
        canvas.drawRoundRect(cx-r*.32f,cy-r*.30f,cx+r*.32f,cy-r*.30f+bar,bar*.5f,bar*.5f,line);
        canvas.drawRoundRect(cx-bar*.5f,cy-r*.30f,cx+bar*.5f,cy+r*.30f,bar*.5f,bar*.5f,line);
        if(lastName!=mName) {
            lastName=mName;
            drawnName=TextUtils.ellipsize(mName==null?"":mName,title,w*.82f,TextUtils.TruncateAt.END).toString();
        }
        canvas.drawText(drawnName,cx,h*.655f,title);
        canvas.drawText(failed?"CARREGAMENTO NÃO CONCLUÍDO":STAGES[completed],cx,h*.72f,caption);
        float barWidth=Math.min(w*.74f,unit*1.15f),barHeight=unit*.018f;
        float left=cx-barWidth*.5f,top=h*.765f;
        progressRect.set(left,top,left+barWidth,top+barHeight);
        line.setColor(0xff183828);canvas.drawRoundRect(progressRect,barHeight*.5f,barHeight*.5f,line);
        int percent=completed==3?100:completed*100/3;
        if(percent>0){
            progressRect.right=left+barWidth*percent/100f;
            line.setColor(failed?0xffe34754:0xff45ef87);
            canvas.drawRoundRect(progressRect,barHeight*.5f,barHeight*.5f,line);
        }
        canvas.drawText(percent+"%",cx,h*.84f,title);
        canvas.drawText(completed+" DE 3 ETAPAS CONCLUÍDAS",cx,h*.885f,caption);
        // Only this existing loading view animates; removal stops invalidation naturally.
        if(isShown()&&getWindowVisibility()==VISIBLE)postInvalidateDelayed(33);
    }
    static void show(final Activity activity,final String name) {
        if(activity==null)return;
        activity.runOnUiThread(new Runnable(){@Override public void run(){
            if(sView!=null) {
                sView.mName=name;sView.completed=0;sView.failed=false;sView.animate().cancel();sView.animate().setStartDelay(0);sView.setAlpha(1);sView.invalidate();return;
            }
            sView=new LoadingOverlay(activity,name);sView.setAlpha(0);
            activity.addContentView(sView,new ViewGroup.LayoutParams(-1,-1));
            sView.animate().alpha(1).setDuration(160).start();
        }});
    }
    static void updateProgress(final Activity activity,final int done) {
        if(activity==null)return;
        activity.runOnUiThread(new Runnable(){@Override public void run(){
            LoadingOverlay view=sView;if(view==null)return;
            if(done<0)view.failed=true;
            else if(!view.failed&&done<=3&&done>=view.completed)view.completed=done;
            int percent=view.completed==3?100:view.completed*100/3;
            view.setContentDescription("Turborama. "+percent+" por cento das etapas concluídas. "+(view.failed?"Carregamento não concluído.":STAGES[view.completed]));
            view.invalidate();
        }});
    }
    static void hide(Activity activity) {
        if(activity==null)return;
        activity.runOnUiThread(new Runnable(){@Override public void run(){
            final LoadingOverlay view=sView;if(view==null)return;sView=null;
            view.animate().alpha(0).setStartDelay(view.completed==3&&!view.failed?80:0).setDuration(view.completed==3&&!view.failed?160:240).withEndAction(new Runnable(){@Override public void run(){
                ViewGroup parent=(ViewGroup)view.getParent();if(parent!=null)parent.removeView(view);
            }}).start();
        }});
    }
}
