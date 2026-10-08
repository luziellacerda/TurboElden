package org.emulationstation.frontend.netplay;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.*;
import android.os.SystemClock;
import android.view.View;
import java.io.InputStream;

/** Original 80 Favourite Lottie frames, one decoder and one visible-only display clock. */
final class StationGameRatingView extends View {
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
    private final Path outline=new Path();
    private final Rect source=new Rect();private final RectF destination=new RectF();
    private Bitmap atlas;
    private boolean loading,resumed,running;private int rating=-1;
    private long previous=-1;private long elapsed;
    private final Runnable frame=new Runnable(){public void run(){
        if(!visible()){motion();return;}
        if(!running)return;
        long now=SystemClock.uptimeMillis();if(previous>=0)elapsed=(elapsed+(int)Math.max(0,Math.min(100,now-previous)));
        // Sample the original 60 fps atlas at a menu cadence below 30 fps.
        // Keep elapsed time so the animation duration does not double.
        previous=now;invalidate();postDelayed(this,34);
    }};
    StationGameRatingView(Context c){super(c);}
    void setRating(int thousandths){rating=thousandths>=0&&thousandths<=1000?thousandths:-1;setContentDescription(rating<0?"Avaliação não informada":String.format(java.util.Locale.forLanguageTag("pt-BR"),"Avaliação %.2f de 5 estrelas",rating/200f));motion();invalidate();}
    void setResumed(boolean value){resumed=value;motion();}
    private boolean visible(){return resumed&&rating>=0&&atlas!=null&&isAttachedToWindow()&&isShown()&&getWindowVisibility()==VISIBLE&&hasWindowFocus()&&ValueAnimator.areAnimatorsEnabled();}
    private void motion(){
        boolean next=visible();if(next==running)return;
        running=next;previous=-1;removeCallbacks(frame);if(next)post(frame);
    }
    private void load(){
        if(loading||atlas!=null)return;loading=true;Context c=getContext().getApplicationContext();
        Thread worker=new Thread(()->{
            Bitmap loaded=null;
            try(InputStream in=c.getAssets().open("station-ui-r46b/rating-atlas.png")){loaded=BitmapFactory.decodeStream(in);}
            catch(Exception e){android.util.Log.w("StationRating","Local rating frames unavailable");}
            final Bitmap ready=loaded;
            post(()->{loading=false;if(!isAttachedToWindow()){if(ready!=null)ready.recycle();return;}atlas=ready;motion();invalidate();});
        },"StationRatingDecode");worker.setDaemon(true);worker.start();
    }
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);float size=Math.min(getHeight(),getWidth()/5.6f),step=size*1.15f,y=(getHeight()-size)/2;
        if(rating<0){paint.setColor(0xff9aaab2);paint.setTextSize(size*.7f);canvas.drawText("—",0,y+size*.8f,paint);return;}
        int index=(int)((elapsed*60/1000)%80);source.set(index%8*128,index/8*128,index%8*128+128,index/8*128+128);
        for(int i=0;i<5;i++){
            float x=i*step;outline.reset();
            for(int v=0;v<10;v++){double a=v*Math.PI/5-Math.PI/2;float r=size*(v%2==0?.46f:.21f);float xx=x+size*.5f+(float)Math.cos(a)*r,yy=y+size*.5f+(float)Math.sin(a)*r;if(v==0)outline.moveTo(xx,yy);else outline.lineTo(xx,yy);}outline.close();
            paint.setColor(0xff40555a);canvas.drawPath(outline,paint);
            float fill=Math.max(0,Math.min(1,rating/200f-i));if(fill<=0)continue;
            int save=canvas.save();canvas.clipRect(x,y,x+size*fill,y+size);
            paint.setColor(0xffffbe32);canvas.drawPath(outline,paint);
            if(atlas!=null){destination.set(x-size*.5f,y-size*.5f,x+size*1.5f,y+size*1.5f);paint.setColor(0xffffffff);canvas.drawBitmap(atlas,source,destination,paint);}
            else{paint.setColor(0xffffda56);canvas.drawPath(outline,paint);}
            canvas.restoreToCount(save);
        }
    }
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();load();motion();}
    @Override protected void onDetachedFromWindow(){resumed=false;motion();removeCallbacks(frame);super.onDetachedFromWindow();}
    @Override protected void onVisibilityChanged(View v,int visibility){super.onVisibilityChanged(v,visibility);if(frame!=null)motion();}
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);if(frame!=null)motion();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);motion();}
}
